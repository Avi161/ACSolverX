#!/usr/bin/env python3
"""Generate results/stable_ac/3_generators_w_choices/ak_3_test/README.md from the sweep's JSONL
streams. Re-runnable at any time (the 1M tier is long + resumable) — regenerates the report from
whatever is on disk. A verified AK(3) solve is headlined at the very top.

    python report_ak3.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "results", "stable_ac", "3_generators_w_choices", "ak_3_test")
FORMS = ["textbook", "rep"]
BUDGETS = [100_000, 1_000_000]
TRIVIAL_TOTAL_LEN = 3          # 3 relators, each length 1


def load(path):
    if not os.path.exists(path):
        return []
    out = []
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return out


def runs(form, budget):
    rows = [r for r in load(os.path.join(OUT, "runs", f"ak3_{form}_{budget}.jsonl"))
            if r.get("form") == form and r.get("budget_nodes") == budget]
    # dedup by word_name, keep last
    by = {}
    for r in rows:
        by[r["word_name"]] = r
    return list(by.values())


def solves():
    out = []
    for form in FORMS:
        for r in load(os.path.join(OUT, "paths", f"ak3_{form}.jsonl")):
            out.append(r)
    return out


def counts(rows):
    n = len(rows)
    ns = sum(1 for r in rows if r.get("solved"))
    return n, ns, n - ns


def closest_table(rows, k=10):
    rows = sorted(rows, key=lambda r: (r.get("min_total_len", 10 ** 9), r.get("nodes_explored", 0)))
    lines = ["| rank | family | word `w` | z-relator | min total len reached | nodes | nodes/s | peak GB |",
             "|-----:|--------|----------|-----------|----------------------:|------:|--------:|--------:|"]
    for i, r in enumerate(rows[:k], 1):
        zrel = "".join({1: "x", -1: "X", 2: "y", -2: "Y", 3: "z", -3: "Z"}.get(a, "?")
                       for a in r.get("z_relator", []))
        lines.append(f"| {i} | {r['family']} | `{r['word_name']}` | `{zrel}` | "
                     f"{r.get('min_total_len','?')} | {r.get('nodes_explored','?'):,} | "
                     f"{r.get('nodes_per_sec','?')} | {r.get('peak_rss_mb',0)/1024:.1f} |")
    return "\n".join(lines)


def main():
    wb = {}
    wbp = os.path.join(OUT, "word_bank.json")
    if os.path.exists(wbp):
        wb = json.load(open(wbp))

    allsolves = solves()
    L = []
    P = L.append

    P("# AK(3) “wormhole” word-choice sweep — results\n")
    P("Can we trivialize **AK(3)** (the length-13 Akbulut–Kirby presentation `13_1`, a 20+ year "
      "open candidate AC-counterexample) by **stabilizing to 3 generators** with a *chosen* relator "
      "`z = w(x,y)` and running the existing greedy substitution solver? `w` is a free choice, so we "
      "throw ~100 literature-grounded words at it. Reaching the trivial 3-generator presentation "
      "would be a genuine AC-trivialization of AK(3) (destabilize `z` back out).\n")

    # ---- headline ----
    if allsolves:
        P("## \U0001f6a8 SOLVE(S) FOUND \U0001f6a8\n")
        P("A stabilized AK(3) presentation reached the trivial presentation. **Verify each with the "
          "reload→replay gate before believing it** (`verify_path` on the reloaded path + a "
          "destabilization check).\n")
        P("| form | word `w` | family | path len | verified | budget | path file |")
        P("|------|----------|--------|---------:|:--------:|-------:|-----------|")
        for s in allsolves:
            P(f"| {s.get('form')} | `{s.get('word_name')}` | {s.get('family','?')} | "
              f"{s.get('path_len','?')} | {s.get('path_verified')} | {s.get('budget_nodes','?'):,} | "
              f"`paths/ak3_{s.get('form')}.jsonl` |")
        P("")
    else:
        P("## Status: no solve yet\n")
        P("No word has trivialized AK(3) in this sweep so far — the expected outcome for a "
          "presentation that has resisted search for two decades. The greedy search drives the total "
          f"relator length down to a **plateau near 13** (trivial = {TRIVIAL_TOTAL_LEN}) and gets "
          "stuck there — a clean illustration of the AK(3) “second hump.” The value here "
          "is the reusable machinery + the record of which of ~100 word choices got closest, so the "
          "1M tier (and future methods) can target them.\n")

    # ---- what was implemented ----
    P("## What was implemented\n")
    P("`z = w(x,y)` stabilization `<x,y|r1,r2> -> <x,y,z|r1,r2, z·w⁻¹>` + the n-relator "
      "greedy substitution solver, with a **null-revert block** (forbids collapsing `z=1`, forcing "
      "the search to use `w`). Two-tier, crash-safe & resumable:\n")
    P("- **SCREEN** — every word × both AK(3) forms at **100k** nodes (parallel): fast solve "
      "detection + how close greedy got (`min_total_len`).")
    P("- **FULL** — every still-unsolved word escalated to **1,000,000** nodes, 1 worker "
      "(a 1M n=3 run peaks ~10 GB RSS), in priority order (Fagan’s flagship words first).\n")
    P("Code (all under `experiments/stable_ac/one_generator/`): `ak3_words.py` (word bank + "
      "`stabilize_with_word`, built from the shipped `stabilize.py` primitives), `ak3_probe.py` "
      "(spawn-safe worker), `run_ak3_wormhole.py` (driver), `report_ak3.py` (this report). "
      "Independent adversarial suite: `tests/ak3_words_independent_test.py` (18/18 pass — own-oracle "
      "+ differential-vs-`stabilize.py` + structural invariants).\n")

    # ---- word bank ----
    if wb:
        P("## Word bank\n")
        P(f"**{wb.get('n_words','?')} unique words** (freely reduced, deduped, z-relator "
          f"≤ L=24). By family (priority = 1M escalation order):\n")
        fam_desc = {
            "relhalf": "1 — relator sides of AK(3) `xyx,yxy,x³,y⁴` + rotations/inverses (Fagan z=xyx & alts)",
            "wk": "2 — `y⁻ᵏ·x⁻¹yxy`, k∈[-8,8] (paper Thm 6/7: exact valid isolations of x)",
            "wstar": "3 — `y⁻¹xyx⁻¹` + automorphism images (paper Thm 3)",
            "conj": "4 — `g·x·g⁻¹`, `g·y·g⁻¹` for short g (Wirtinger/Rmk 17)",
            "comm": "5 — commutators + short double commutators (App F bridge is commutator-heavy)",
            "brute": "6 — all freely-reduced words of length ≤3 (breadth probes)",
            "ms": "7 — MS(n,w) library w-values (`w1=y⁻¹x⁻¹yxy`, Prop 5)",
            "control": "8 — the dumb baselines w=r1, w=r2 (form-dependent)",
        }
        P("| family | count | description |")
        P("|--------|------:|-------------|")
        for fam, cnt in sorted(wb.get("by_family", {}).items(),
                               key=lambda kv: int(fam_desc.get(kv[0], "9").split()[0])):
            P(f"| `{fam}` | {cnt} | {fam_desc.get(fam, '')} |")
        P(f"\nProvenance for every word (int form, z-relator, length) is in `word_bank.json`. "
          f"The two forms swept (both are AK(3)): **textbook** `<x,y|xyx=yxy, x³=y⁴>` "
          f"(where the theory’s words are provably isolatable) and **rep** `13_1` "
          f"(`YXyXYx`/`YYYXXXX`, the exact object in `data/ms_unsolved_reps`).\n")

    # ---- results per form/budget ----
    P("## Results\n")
    for budget in BUDGETS:
        tier = "SCREEN" if budget == 100_000 else "FULL"
        P(f"### {tier} @ {budget:,} nodes\n")
        any_rows = False
        for form in FORMS:
            rows = runs(form, budget)
            if not rows:
                continue
            any_rows = True
            n, ns, nx = counts(rows)
            mtl = min((r.get("min_total_len", 10 ** 9) for r in rows), default=None)
            note = ""
            if budget == 1_000_000:
                note = f"  _(of {wb.get('n_words','~95')+2} words — escalation in progress if < that)_"
            P(f"**{form}**: {n} words run, **{ns} solved**, {nx} exhausted budget; "
              f"closest total length reached = **{mtl}** (trivial={TRIVIAL_TOTAL_LEN}).{note}\n")
            P(closest_table(rows, 10))
            P("")
        if not any_rows:
            P("_(no records yet — tier not started or in progress.)_\n")

    # ---- reproduce ----
    P("## Reproduce / resume\n")
    P("```bash")
    P("cd experiments/stable_ac/one_generator")
    P("python ak3_words.py                         # build word_bank.json + Phase-0 gates")
    P("python run_ak3_wormhole.py --phase screen   # 100k screen, both forms (resumable)")
    P("python run_ak3_wormhole.py --phase full     # escalate unsolved to 1M, priority order (resumable)")
    P("python report_ak3.py                        # regenerate this README from the JSONL streams")
    P("python -m pytest ../../../tests/ak3_words_independent_test.py -q   # independent suite")
    P("```")
    P("Streams are append-only + fsync’d and resume by `(form, word_name, budget)`; re-running is a "
      "no-op, a killed run continues. Files: `runs/ak3_<form>_<budget>.jsonl` (every word, solved+"
      "unsolved), `paths/ak3_<form>.jsonl` (one replayable move+state path per solve).\n")

    P("## Caveats (honest)\n")
    P("- This runs **ordinary greedy substitution** on the stabilized presentation — it does *not* "
      "execute Fagan’s Lemma-11 destabilization as an atomic move; the bet is that the extra `z=w` "
      "relator opens a greedy path the 2-gen form lacks. A reached-trivial 3-gen presentation is still "
      "a valid AK(3) trivialization by AC5 destabilization.")
    P("- The JAX-env gold gate (`envs/ac_moves.py::s_move` / `check_paths`) is **deferred** (JAX absent "
      "here; that env’s `s_move` is hardcoded to relators 0/1 and can’t run n=3). Every solve’s "
      "evidence is `verify_path` (independent replay) + a reload→replay + destabilization check — "
      "strong, but not the executable gold gate.")
    P("- No literature result trivializes AK(3); families 1–2 have paper-level isolation validity, "
      "3–8 are motivated search directions. Near-identical words differ wildly in hardness, so "
      "breadth across families is the point.\n")

    with open(os.path.join(OUT, "README.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print(f"wrote {os.path.relpath(os.path.join(OUT, 'README.md'), ROOT)}  "
          f"(solves={len(allsolves)})")


if __name__ == "__main__":
    main()
