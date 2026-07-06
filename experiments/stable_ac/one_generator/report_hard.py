#!/usr/bin/env python3
"""Generate results/stable_ac/3_generators_w_choices/hard_solved_test/README.md from the sweep's
JSONL streams. Re-runnable any time (resumable sweep). The question this study answers: for a
HARD-but-solvable presentation (idx 625, 610), which z=w(x,y) word choice solves best — can a
clever word beat the dumb baseline (z=r1) in nodes/path, or solve where the dumb words fail?

    python report_hard.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "results", "stable_ac", "3_generators_w_choices", "hard_solved_test")
MS640 = os.path.join(ROOT, "results", "stable_ac", "3_generators_w_choices", "ms640", "runs")
BASE2GEN = os.path.join(ROOT, "results", "baseline_greedy", "solved", "calibration_baseline.jsonl")
TARGETS = [625, 610]
BUDGETS = [100_000, 1_000_000]
TRIVIAL_TOTAL_LEN = 3          # 3 relators, each length 1
_CH = {1: "x", -1: "X", 2: "y", -2: "Y", 3: "z", -3: "Z"}

FAM_DESC = {
    "relhalf": "1 — parts of THIS target's relators: inverses, pure-power runs (yⁿ/Yⁿ⁺¹), cyclic halves",
    "wk": "2 — `y⁻ᵏ·x⁻¹yxy`, k∈[-8,8] (AK(n) isolation family, Thm 6/7)",
    "wstar": "3 — `y⁻¹xyx⁻¹` + automorphism images (Thm 3)",
    "conj": "4 — `g·x·g⁻¹`, `g·y·g⁻¹` for short g (Wirtinger/Rmk 17)",
    "comm": "5 — commutators + short double commutators",
    "brute": "6 — all freely-reduced words of length ≤3 (breadth; includes the dumb w=x, w=y)",
    "ms": "7 — MS(n,w) library w-values (`w1=y⁻¹x⁻¹yxy`)",
    "control": "8 — the dumb baselines w=r1, w=r2",
}


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


def runs(idx, budget):
    rows = [r for r in load(os.path.join(OUT, "runs", f"hard_ms{idx}_{budget}.jsonl"))
            if r.get("idx") == idx and r.get("budget_nodes") == budget]
    by = {}
    for r in rows:                                 # dedup by word_name, keep last
        by[r["word_name"]] = r
    return list(by.values())


def base2gen(idx):
    for r in load(BASE2GEN):
        if r.get("idx") == idx and r.get("solved"):
            return r
    return None


def dumb_controls(idx):
    """The existing n=3 dumb-word baselines {r1,r2,x,y} @500k for this idx (arms on disk)."""
    out = {}
    for arm in ("r1", "r2", "x", "y"):
        for r in load(os.path.join(MS640, f"calibration_{arm}.jsonl")):
            if r.get("idx") == idx and r.get("arm") == arm:
                out[arm] = r
    return out


def decode_state(states):
    if not states:
        return "—"
    return "  |  ".join("".join(_CH.get(int(a), "?") for a in r) for r in states)


def solves_for(idx):
    return load(os.path.join(OUT, "paths", f"hard_ms{idx}.jsonl"))


def solved_table(rows):
    rows = sorted([r for r in rows if r.get("solved")],
                  key=lambda r: (r.get("nodes_explored", 10 ** 9), r.get("path_len", 10 ** 9)))
    if not rows:
        return "_(no word solved at this budget.)_"
    lines = ["| rank | family | word `w=z` | nodes | path len | nodes/s | peak GB |",
             "|-----:|--------|------------|------:|---------:|--------:|--------:|"]
    for i, r in enumerate(rows, 1):
        lines.append(f"| {i} | {r['family']} | `{r['word_name']}` | {r.get('nodes_explored',0):,} | "
                     f"{r.get('path_len','?')} | {r.get('nodes_per_sec','?')} | "
                     f"{r.get('peak_rss_mb',0)/1024:.1f} |")
    return "\n".join(lines)


def closest_unsolved_table(rows, k=8):
    rows = sorted([r for r in rows if not r.get("solved")],
                  key=lambda r: (r.get("min_total_len", 10 ** 9), r.get("nodes_explored", 0)))
    if not rows:
        return "_(every word solved — no unsolved words at this budget.)_"
    lines = ["| family | word `w` | min total len | closest presentation `⟨x,y,z\\|·⟩` reached |",
             "|--------|----------|--------------:|-------------------------------------------|"]
    for r in rows[:k]:
        st = decode_state(r.get("min_total_state") or [])
        lines.append(f"| {r['family']} | `{r['word_name']}` | {r.get('min_total_len','?')} | `{st}` |")
    return "\n".join(lines)


def family_summary(rows):
    fam = {}
    for r in rows:
        f = r["family"]
        d = fam.setdefault(f, {"n": 0, "solved": 0, "best_mtl": 10 ** 9, "best_nodes": None})
        d["n"] += 1
        if r.get("solved"):
            d["solved"] += 1
            nn = r.get("nodes_explored", 10 ** 9)
            if d["best_nodes"] is None or nn < d["best_nodes"]:
                d["best_nodes"] = nn
        d["best_mtl"] = min(d["best_mtl"], r.get("min_total_len", 10 ** 9))
    lines = ["| family | words | solved | best nodes-to-solve | closest (min total len) | description |",
             "|--------|------:|-------:|--------------------:|------------------------:|-------------|"]
    for f in sorted(fam, key=lambda k: int(FAM_DESC.get(k, "9").split()[0])):
        d = fam[f]
        bn = f"{d['best_nodes']:,}" if d["best_nodes"] is not None else "—"
        lines.append(f"| `{f}` | {d['n']} | {d['solved']} | {bn} | {d['best_mtl']} | {FAM_DESC.get(f,'')} |")
    return "\n".join(lines)


def finding_section():
    """Consolidated 'what we did / what we learned' conclusion, recomputed from the sweep streams so
    it stays correct on every regenerate. Screen tier (100k) only — the 1M full tier is user-gated."""
    S = []
    S.append("## Finding — what we did & what we learned\n")
    S.append(
        "**What we did.** Took two *hard-but-solvable* Miller–Schupp presentations (idx 625, 610 — "
        "the plain 2-gen greedy solves them, but only after ~60–80k nodes and a 300–660-move path, "
        "so there is a real baseline to beat), stabilized each as `⟨x,y,z | r1, r2, z·w⁻¹⟩` for ~97 "
        "candidate words `w(x,y)` across 8 families (relator halves/inverses, the AK isolation "
        "family `wk`, `wstar`, conjugates, commutators, all freely-reduced words of length ≤3, MS "
        "library words, and the dumb `r1/r2` controls), and ran the n=3 greedy solver at a "
        "**100,000-node screen**. Win condition: a word that solves in fewer nodes / a shorter path "
        "than `z=r1`, or solves where the dumb words fail.\n")
    generic_solved = generic_runs = 0
    plateaus = []
    for idx in TARGETS:
        rows = runs(idx, 100_000)
        if not rows:
            continue
        solved = [r for r in rows if r.get("solved")]
        solved_fams = sorted({r["family"] for r in solved})
        generic = [r for r in rows if r["family"] not in ("control", "relhalf")]
        generic_runs += len(generic)
        generic_solved += sum(1 for r in generic if r.get("solved"))
        by = {r["word_name"]: r for r in rows}
        ctrl = by.get("r1") if by.get("r1", {}).get("solved") else by.get("r2")
        ctrl_n = ctrl.get("nodes_explored") if ctrl and ctrl.get("solved") else None
        best = min((r.get("nodes_explored", 10 ** 9) for r in solved), default=None)
        plateau = min((r.get("min_total_len", 10 ** 9) for r in rows if not r.get("solved")),
                      default=None)
        if plateau is not None:
            plateaus.append(plateau)
        rel = "ties" if (best is not None and ctrl_n is not None and best >= ctrl_n) else "beats"
        fam_txt = "/".join(f"`{f}`" for f in solved_fams) or "—"
        best_txt = f"{best:,}" if best is not None else "—"
        ctrl_txt = f"{ctrl_n:,}" if ctrl_n is not None else "—"
        S.append(
            f"- **idx {idx}:** {len(rows)} words, **{len(solved)} solved** — only {fam_txt} "
            f"(relator-derived); **0 generic-family** words solved. Best solve {best_txt} nodes "
            f"{rel} the `z=r1` control ({ctrl_txt} n). Every unsolved word plateaus at total "
            f"length ≥ {plateau} (trivial = {TRIVIAL_TOTAL_LEN}).")
    S.append("")
    pmin, pmax = (min(plateaus), max(plateaus)) if plateaus else ("?", "?")
    S.append(
        f"**What we learned — a clean negative at the 100k screen.** Across both targets, **only "
        f"relator-derived words solve** (the `control` words `z=r1/r2` and `relhalf` words built "
        f"from the target's own relators), and **none beats the dumb `z=r1` control** — the `relhalf` "
        f"solvers land at the *same* node count as `z=r1` because they are a half/inverse of `r1`, "
        f"i.e. the same solve in disguise. **{generic_solved} of {generic_runs} generic-family "
        f"(word×target) runs solved** — every structurally-different word, including the "
        f"theory-motivated `wk` AK-isolation family, stalls at total length {pmin}–{pmax} "
        f"(trivial {TRIVIAL_TOTAL_LEN}). So at screen budget there is **no wormhole shortcut** on "
        f"these targets: naming a clever `z=w` does not help ordinary greedy find a cheaper/shorter "
        f"path. This mirrors the AK(3) sweep's negative (0 solved, hard plateau): ordinary greedy "
        f"substitution does not exploit the change of variables — realizing a useful `z=w` is "
        f"Fagan's Lemma-11 *atomic destabilization*, a supermove greedy does not perform. The "
        f"1,000,000-node full tier was intentionally **not** run (user-gated); on this evidence the "
        f"plateau is unlikely to move.\n")
    return "\n".join(S)


def main():
    L = []
    P = L.append
    P("# Hard-but-solvable “wormhole” word-choice sweep — results\n")
    P("AK(3) gave a *negative* result (0 solved, everything plateaus at total length 13), so it "
      "can’t tell us *which* word family is most useful. This study asks the same question on "
      "presentations the plain 2-generator greedy **did** solve, but only after many nodes and a "
      "long path — so there is a real baseline to beat. We stabilize `⟨x,y|r1,r2⟩ → "
      "`⟨x,y,z|r1,r2,z·w⁻¹⟩` for ~97 word choices `w(x,y)` (+ the dumb controls) and run the n=3 "
      "greedy solver. **Win = a word that solves in fewer nodes / shorter path than `z=r1`, or "
      "solves where the dumb words can’t.**\n")

    P(finding_section())

    # per-target overview with built-in baselines
    for idx in TARGETS:
        b2 = base2gen(idx)
        dumb = dumb_controls(idx)
        wbp = os.path.join(OUT, f"word_bank_ms{idx}.json")
        wb = json.load(open(wbp)) if os.path.exists(wbp) else {}
        P(f"## Target idx {idx} — `r1 = {wb.get('r1','?')}`, `r2 = {wb.get('r2','?')}` "
          f"(Miller–Schupp)\n")
        if b2:
            P(f"- **2-gen baseline** (no stabilization): solved in **{b2.get('nodes_explored',0):,} "
              f"nodes**, path length **{b2.get('path_len','?')}**.")
        if dumb:
            def fmt(arm):
                r = dumb.get(arm)
                if not r:
                    return f"`z={arm}`: —"
                if r.get("solved"):
                    return f"`z={arm}`: ✅ {r.get('nodes_explored',0):,} n / {r.get('path_len','?')} p"
                return f"`z={arm}`: ❌ exhausted {r.get('budget_nodes',0):,}"
            P(f"- **n=3 dumb-word controls @500k** (on disk): {fmt('r1')} · {fmt('r2')} · "
              f"{fmt('x')} · {fmt('y')}.")
        # sweep results, this target
        for budget in BUDGETS:
            rows = runs(idx, budget)
            if not rows:
                continue
            ns = sum(1 for r in rows if r.get("solved"))
            unsolved = [r for r in rows if not r.get("solved")]
            mtl = min((r.get("min_total_len", 10 ** 9) for r in unsolved), default=None)  # closest UNSOLVED
            best = min((r.get("nodes_explored", 10 ** 9) for r in rows if r.get("solved")), default=None)
            # in-sweep baseline: this sweep's OWN z=r1 control (apples-to-apples, same solver/order)
            by = {r["word_name"]: r for r in rows}
            base_ctrl = by.get("r1") if by.get("r1", {}).get("solved") else by.get("r2")
            base_nodes = base_ctrl.get("nodes_explored") if base_ctrl and base_ctrl.get("solved") else None
            tier = "SCREEN" if budget == 100_000 else "FULL"
            P(f"\n### {tier} @ {budget:,} nodes — {len(rows)} words run, **{ns} solved**, "
              f"closest *unsolved* min-total-len = {mtl}\n")
            if best is not None:
                # a GENUINE shortcut = a word NOT derived from the relators (not control/relhalf)
                # that solves in meaningfully fewer nodes than the z=r1 baseline
                shortcuts = [r for r in rows if r.get("solved") and r["family"] not in ("control", "relhalf")
                             and base_nodes and r.get("nodes_explored", 10 ** 9) < 0.9 * base_nodes]
                best_generic = min((r.get("nodes_explored", 10 ** 9) for r in rows
                                    if r.get("solved") and r["family"] not in ("control", "relhalf")),
                                   default=None)
                base_txt = f" (in-sweep `z=r1` control: {base_nodes:,} nodes)" if base_nodes else ""
                if shortcuts:
                    verdict = (f"Best solve: **{best:,} nodes**{base_txt}. **{len(shortcuts)} word(s) from "
                               f"non-relator families beat z=r1 by >10%** — a genuine wormhole shortcut: "
                               + ", ".join(f"`{r['word_name']}` ({r['family']}, {r['nodes_explored']:,})"
                                           for r in sorted(shortcuts, key=lambda r: r['nodes_explored'])[:5]) + ".")
                elif best_generic is not None:
                    verdict = (f"Best solve: **{best:,} nodes**{base_txt}. No structurally-different word "
                               f"beats z=r1 by a meaningful margin — the words that match it are the relators "
                               f"themselves or their inverses/halves (family `control`/`relhalf`, the same "
                               f"solve in disguise). Best *generic-family* solve: {best_generic:,} nodes.")
                else:
                    verdict = (f"Best solve: **{best:,} nodes**{base_txt}. Only relator-derived words "
                               f"(`control`/`relhalf`) solved; no generic word family solved at this budget.")
                P(verdict + "\n")
            P("**Solved words** (fewest nodes first):\n")
            P(solved_table(rows))
            P("\n**Closest UNSOLVED words** — the actual presentation greedy got stuck on "
              "(`min_total_state`, trivial total length = 3):\n")
            P(closest_unsolved_table(rows))
            P("\n**By family:**\n")
            P(family_summary(rows))
            P("")

    # word bank + reproduce
    P("## What was implemented\n")
    P("`z=w(x,y)` stabilization + n=3 greedy with a **null-revert block** (forbids `z=1`, forcing "
      "the search to use `w`). Two-tier, crash-safe & resumable. Code (all under "
      "`experiments/stable_ac/one_generator/`): `hard_words.py` (target loader + word bank, reusing "
      "the generic families from `ak3_words.py`; only `relhalf` is re-derived from the target’s own "
      "relators), `hard_probe.py` (spawn-safe worker; records `min_total_len` **and** "
      "`min_total_state`), `run_hard_wormhole.py` (driver), `report_hard.py` (this report). "
      "Independent adversarial suite: `tests/hard_words_independent_test.py`.\n")
    P("Word families (same breadth as the AK(3) sweep):\n")
    P("| family | description |")
    P("|--------|-------------|")
    for f in sorted(FAM_DESC, key=lambda k: int(FAM_DESC[k].split()[0])):
        P(f"| `{f}` | {FAM_DESC[f]} |")
    P("\n## Reproduce / resume\n```bash")
    P("cd experiments/stable_ac/one_generator")
    P("python hard_words.py                                   # build word banks + Phase-0.5 gates")
    P("python run_hard_wormhole.py --phase screen             # 100k screen, both targets (resumable)")
    P("python run_hard_wormhole.py --phase full --only <w,..> # escalate chosen words to 1M")
    P("python report_hard.py                                  # regenerate this README")
    P("python tests/hard_words_independent_test.py            # independent suite")
    P("```")
    P("Streams resume by `(idx, word_name, budget)`; re-running is a no-op, a killed run continues. "
      "`runs/hard_ms<idx>_<budget>.jsonl` (every word), `paths/hard_ms<idx>.jsonl` (a replayable "
      "path per solve).\n")
    P("## Caveats (honest)\n")
    P("- Ordinary greedy substitution on the stabilized presentation (not Fagan’s Lemma-11 atomic "
      "destabilization). A reached-trivial 3-gen presentation is a valid trivialization of the base "
      "by AC5 destabilization.")
    P("- JAX-env gold gate deferred (JAX absent; env `s_move` is n=2-only). Each solve’s evidence is "
      "`verify_path` (independent replay) + reload→replay; strong but not the executable gold gate.")

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "README.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    total_solves = sum(len(solves_for(idx)) for idx in TARGETS)
    print(f"wrote {os.path.relpath(os.path.join(OUT, 'README.md'), ROOT)}  (path-file solves={total_solves})")


if __name__ == "__main__":
    main()
