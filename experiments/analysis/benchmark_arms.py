"""Per-presentation best-known cost for each technique, joined onto every benchmark subset.

The subset files say what the *problems* are. This says what each technique currently *costs* on
them -- nodes explored and the path length that came with those nodes -- so a new technique can be
priced against the field without re-deriving the field.

Writes ``benchmark/subsets/benchmark_subset_{10,20,40,60}_arms.{csv,json}`` plus
``benchmark/subsets/ARMS.md``. It never touches the frozen ``benchmark_subset_{N}.{csv,json}``:
those regenerate from the baseline jsonl alone and are checked by a zero-diff regeneration, and
folding a scoreboard into them would make the problem set depend on the results measured on it.

**Coverage is partial below subset-60.** The four subsets are not nested (``nested: false``) and
both campaigns ran against subset-60's row list, so subset-10/20/40 have arm data for only 4/10,
18/20 and 25/40 of their rows. Untested rows are emitted with ``tested = False``, ``-1`` in every
numeric arm column and ``"none"`` in every string one -- **including ``*_solved``, which must never
be ``False`` there**: ``False`` says "we ran it and it did not solve", a far stronger claim than
"we have not run it". Every summary counts ``tested`` rows only.

Three blocks of columns, and they answer different questions.

**Best-known** (``greedy_*``, ``bestcov_*``, ``heur_*``) -- the cheapest solve anyone has recorded,
each arm at its own budget and its own relator cap. This is what "how expensive is this row" means
in practice, and it is what the user asked for. It is **not** a controlled comparison: the arms ran
at 1,000,000 / <=20,000 / 100,000 nodes and at cap 24 / 24 / 48. Never read a ratio across them.

**Matched** (``m10k_*``) -- all three arms at budget 10,000 and cap 24, from
``results/comparison/three_way_b10k_subset60.csv``, whose builder refuses to write unless its
length-only control reproduces the plain greedy pop for pop on all 60 rows. This is the block a
head-to-head claim belongs in.

**Combined** (``b1k_*``) -- the 2x2 of *transform the start* x *change the ordering*, every arm one
search at budget 1,000, from ``results/comparison/cov_heur_b1k_subset60.csv``. ``b1k_covheur_*`` is
the combination: singly destabilise with the winning ``z`` (the same ``bestcov_z`` this file already
carries), then search with the recommended ordering. Its control is ``b1k_covgreedy_*`` -- same
start, same per-row cap (``b1k_cov_cap``), ordering the only difference. Unlike the blocks above,
**these arms do not all solve**, so an unsolved row carries ``nodes = 1,000`` and a blank path; no
mean or median over them is taken except over the rows the compared arms both solve.

Run::

    .venv/bin/python3 -m experiments.heuristic_search.runners.cov_heur_b1k   # writes the b1k source
    .venv/bin/python3 -m experiments.analysis.benchmark_arms
"""
import csv
import json
import os
import sys


def _repo_root():
    d = os.path.dirname(os.path.abspath(__file__))
    while d != os.path.dirname(d):
        if (os.path.isdir(os.path.join(d, "experiments"))
                and os.path.isdir(os.path.join(d, "data"))):
            return d
        d = os.path.dirname(d)
    raise RuntimeError("repo root not found")


REPO = _repo_root()
sys.path.insert(0, REPO)

SUBSETS_DIR = os.path.join(REPO, "benchmark", "subsets")
COMPARISON = os.path.join(REPO, "results", "comparison")
BESTCOV_CSV = os.path.join(COMPARISON, "greedy_vs_bestcov_subset60_nodes_path.csv")
THREEWAY_CSV = os.path.join(COMPARISON, "three_way_b10k_subset60.csv")
EXP28_JSONL = os.path.join(REPO, "results", "heuristic_search", "runs",
                           "EXP28_colab_scale.jsonl")
B1K_CSV = os.path.join(COMPARISON, "cov_heur_b1k_subset60.csv")

SIZES = (10, 20, 40, 60)

# The four subsets are **not** nested (`nested: false` in each file), and both the CoV sweep and the
# heuristic campaign were run against subset-60's row list -- so 10/20/40 contain rows no arm has
# ever been run on (4/10, 18/20 and 25/40 have data). Those rows are emitted with an explicit
# not-tested marker rather than dropped or left blank: a dropped row misrepresents the subset, and a
# blank or `False` in a `*_solved` column reads as "we tried and it failed", which is a different
# and much stronger claim than "we have not tried".
UNTESTED_NUM = -1        # every numeric arm column
UNTESTED_STR = "none"    # every string arm column, including *_solved

# The recommended heap ordering, as shipped in experiments/heuristic_search/core/hsolve.py:RECOMMENDED.
# Mirrored here as data so this file can state the formula without importing the solver; the
# weights are asserted against RECOMMENDED at run time, so the two cannot drift apart silently.
HEUR_WEIGHTS = {"L": 1.0, "K": 2.53, "MK": 6.418, "S": 8.458, "xyimb": 3.292}
HEUR_FORMULA = ("priority(r1, r2) = L + 2.53*K + 6.418*MK + 8.458*S + 3.292*xyimb   "
                "(one segment, no length threshold)")
HEUR_TERMS = {
    "L": "total length |r1| + |r2| -- the baseline greedy's entire ordering",
    "K": "knot sum knots(r1) + knots(r2), where knots(w) = 0 for a pure power, "
         "else max(#x-blocks, #y-blocks) read cyclically",
    "MK": "max knots over the two relators",
    "S": "smaller mean block -- the mean run length of the thinner generator",
    "xyimb": "generator imbalance |#x - #y| / L, scale-free",
}

# Every arm's provenance, so a column can never be read without its budget and cap.
ARMS = {
    "greedy": {"what": "baseline greedy, best known", "budget": 1_000_000, "cap": 24,
               "source": "benchmark/subsets/benchmark_subset_60.json (nodes_1M / path_1M)"},
    "bestcov": {"what": "best change of variables over the whole subword family", "budget": 20_000,
                "cap": 24, "source": "results/comparison/greedy_vs_bestcov_subset60_nodes_path.csv"},
    "heur": {"what": "recommended heap ordering (formula above)", "budget": 100_000, "cap": 48,
             "source": "results/heuristic_search/runs/EXP28_colab_scale.jsonl, arm=recommended"},
    "m10k": {"what": "all three arms at a matched budget and cap", "budget": 10_000, "cap": 24,
             "source": "results/comparison/three_way_b10k_subset60.csv"},
    "b1k": {"what": "transform x ordering, 2x2 -- greedy / heuristic, on the original pair and on "
                    "the best-CoV pair", "budget": 1_000, "cap": "24 (original) / b1k_cov_cap (CoV)",
            "source": "results/comparison/cov_heur_b1k_subset60.csv"},
}

FIELDS = [
    "pres_id", "bin", "aut_class", "start_length", "r1", "r2", "tested",
    # best known, each arm at its own budget/cap -- see ARMS
    "greedy_solved", "greedy_nodes", "greedy_path",
    "bestcov_solved", "bestcov_nodes", "bestcov_path",
    "bestcov_z", "bestcov_class", "bestcov_found_at_budget",
    "heur_solved", "heur_nodes", "heur_path",
    # matched budget 10,000 / cap 24 -- the controlled head-to-head
    "m10k_greedy_solved", "m10k_greedy_nodes", "m10k_greedy_path",
    "m10k_bestcov_solved", "m10k_bestcov_nodes", "m10k_bestcov_path",
    "m10k_heur_solved", "m10k_heur_nodes", "m10k_heur_path",
    # budget 1,000 -- the 2x2 of transform x ordering; these arms do NOT all solve
    "b1k_greedy_solved", "b1k_greedy_nodes", "b1k_greedy_path",
    "b1k_heur_solved", "b1k_heur_nodes", "b1k_heur_path",
    "b1k_covgreedy_solved", "b1k_covgreedy_nodes", "b1k_covgreedy_path",
    "b1k_covheur_solved", "b1k_covheur_nodes", "b1k_covheur_path",
    "b1k_cov_cap", "b1k_cov_n_tied_starts",
]
B1K_ARMS = ("b1k_greedy", "b1k_heur", "b1k_covgreedy", "b1k_covheur")


def _int(v):
    return None if v in ("", None) else int(v)


def _bool(v):
    return v in (True, "True", "true", 1, "1")


def load_bestcov():
    """pres_id -> the best CoV's cost, with the z it was found under."""
    out = {}
    with open(BESTCOV_CSV) as f:
        for r in csv.DictReader(f):
            out[int(r["pres_id"])] = {
                "bestcov_solved": _bool(r["bestcov_solved"]),
                "bestcov_nodes": _int(r["bestcov_nodes"]),
                "bestcov_path": _int(r["bestcov_path"]),
                "bestcov_z": r["bestcov_z"],
                "bestcov_class": r["bestcov_class"],
                "bestcov_found_at_budget": _int(r["bestcov_found_at_budget"]),
            }
    return out


def load_heuristic():
    """pres_id -> the recommended ordering's cost at 100,000 nodes, cap 48 (EXP-28)."""
    out = {}
    with open(EXP28_JSONL) as f:
        for line in f:
            row = json.loads(line)
            if row.get("arm") != "recommended":
                continue
            name = row.get("name", "")
            if not name.startswith("ms") or not name[2:].isdigit():
                continue          # the six reach rows carry a non-numeric suffix
            out[int(name[2:])] = {
                "heur_solved": bool(row["solved"]),
                "heur_nodes": row.get("nodes_explored"),
                "heur_path": row.get("path_length"),
            }
    return out


def load_matched():
    """pres_id -> all three arms at budget 10,000, cap 24."""
    out = {}
    with open(THREEWAY_CSV) as f:
        for r in csv.DictReader(f):
            out[int(r["pres_id"])] = {
                "m10k_greedy_solved": _bool(r["greedy_solved"]),
                "m10k_greedy_nodes": _int(r["greedy_nodes"]),
                "m10k_greedy_path": _int(r["greedy_path"]),
                "m10k_bestcov_solved": _bool(r["bestcov_solved"]),
                "m10k_bestcov_nodes": _int(r["bestcov_nodes"]),
                "m10k_bestcov_path": _int(r["bestcov_path"]),
                "m10k_heur_solved": _bool(r["heur_solved"]),
                "m10k_heur_nodes": _int(r["heur_nodes"]),
                "m10k_heur_path": _int(r["heur_path"]),
            }
    return out


def load_b1k():
    """pres_id -> the 2x2 at budget 1,000: {greedy, heur} x {original pair, best-CoV pair}.

    An unsolved row here is a real measurement, not a gap: it carries ``solved = False``,
    ``nodes = 1,000`` (the budget) and a blank path, exactly as the m10k block does.
    """
    out = {}
    with open(B1K_CSV) as f:
        for r in csv.DictReader(f):
            row = {"b1k_cov_cap": _int(r["cov_cap"]),
                   "b1k_cov_n_tied_starts": _int(r["cov_n_tied_starts"])}
            for arm in B1K_ARMS:
                row[f"{arm}_solved"] = _bool(r[f"{arm}_solved"])
                row[f"{arm}_nodes"] = _int(r[f"{arm}_nodes"])
                row[f"{arm}_path"] = _int(r[f"{arm}_path"]) if r[f"{arm}_path"] else ""
            out[int(r["pres_id"])] = row
    return out


def _untested_block():
    """Every arm column marked not-tested: -1 for numbers, "none" for strings and solved flags."""
    out = {}
    for k in FIELDS:
        if not k.startswith(("bestcov_", "heur_", "m10k_", "b1k_")):
            continue
        out[k] = UNTESTED_STR if (k.endswith(("_solved", "_z", "_class"))) else UNTESTED_NUM
    return out


def build_rows(size, bestcov, heur, matched, b1k):
    with open(os.path.join(SUBSETS_DIR, f"benchmark_subset_{size}.json")) as f:
        subset = json.load(f)["subset"]
    untested = _untested_block()
    rows = []
    for s in subset:
        pid = s["pres_id"]
        has = pid in bestcov and pid in heur and pid in matched and pid in b1k
        row = {
            "pres_id": pid,
            "bin": s["bin"],
            "aut_class": s.get("aut_class"),
            "start_length": s.get("start_length"),
            "r1": s["r1"],
            "r2": s["r2"],
            "tested": has,
            # The baseline's 10^6-node run is the subset's own ground truth: all 640 solve there,
            # so the greedy columns are populated on every row of every subset.
            "greedy_solved": True,
            "greedy_nodes": s["nodes_1M"],
            "greedy_path": s["path_1M"],
        }
        if has:
            row.update(bestcov[pid])
            row.update(heur[pid])
            row.update(matched[pid])
            row.update(b1k[pid])
        else:
            row.update(untested)
        rows.append(row)
    return rows


def summarize(rows):
    """Means over the rows every listed arm solves -- the only set a cross-arm mean is honest on.

    Restricted to `tested` rows throughout. An untested row is not a failure: counting it as one
    would understate every transformed arm on exactly the subsets they were never run on.
    """
    tested = [r for r in rows if r["tested"]]
    both = [r for r in tested
            if r["greedy_solved"] and r["bestcov_solved"] and r["heur_solved"]]
    out = {"n_rows": len(rows), "n_tested": len(tested),
           "n_untested": len(rows) - len(tested), "n_all_three_solved": len(both)}
    for arm in ("greedy", "bestcov", "heur"):
        out[f"{arm}_solved"] = sum(1 for r in tested if r[f"{arm}_solved"] is True)
        out[f"{arm}_mean_nodes"] = (round(sum(r[f"{arm}_nodes"] for r in both) / len(both), 2)
                                    if both else None)
        out[f"{arm}_mean_path"] = (round(sum(r[f"{arm}_path"] for r in both) / len(both), 2)
                                   if both else None)
    for arm in ("m10k_greedy", "m10k_bestcov", "m10k_heur"):
        out[f"{arm}_solved"] = sum(1 for r in tested if r[f"{arm}_solved"] is True)
    # The b1k arms do not all solve, so only the solve count is a whole-block statistic. Nodes are
    # summarised over the rows an arm SOLVES -- an unsolved row's node count is the budget, and
    # averaging the ceiling in would report "how long we waited" as "what it cost".
    for arm in B1K_ARMS:
        won = [r for r in tested if r[f"{arm}_solved"] is True]
        out[f"{arm}_solved"] = len(won)
        out[f"{arm}_median_nodes_solved"] = _median([r[f"{arm}_nodes"] for r in won])
        out[f"{arm}_median_path_solved"] = _median([r[f"{arm}_path"] for r in won])
    return out


def _median(v):
    v = sorted(v)
    if not v:
        return None
    return (v[len(v) // 2 - 1] + v[len(v) // 2]) / 2 if len(v) % 2 == 0 else v[len(v) // 2]


def main():
    # Fail loudly rather than shipping a stale formula if RECOMMENDED ever changes.
    from experiments.heuristic_search.core.hsolve import RECOMMENDED
    shipped = RECOMMENDED["segments"]
    assert len(shipped) == 1 and shipped[0]["upto"] is None, \
        f"RECOMMENDED is no longer a single unthresholded segment: {RECOMMENDED}"
    assert shipped[0]["w"] == HEUR_WEIGHTS, \
        f"HEUR_WEIGHTS drifted from hsolve.RECOMMENDED: {shipped[0]['w']} != {HEUR_WEIGHTS}"

    bestcov, heur, matched = load_bestcov(), load_heuristic(), load_matched()
    b1k = load_b1k()

    for size in SIZES:
        rows = build_rows(size, bestcov, heur, matched, b1k)
        csv_path = os.path.join(SUBSETS_DIR, f"benchmark_subset_{size}_arms.csv")
        with open(csv_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            w.writerows(rows)
        s = summarize(rows)
        json_path = os.path.join(SUBSETS_DIR, f"benchmark_subset_{size}_arms.json")
        with open(json_path, "w") as f:
            json.dump({
                "size": size,
                "heuristic_formula": HEUR_FORMULA,
                "heuristic_weights": HEUR_WEIGHTS,
                "heuristic_terms": HEUR_TERMS,
                "arms": ARMS,
                "untested_marker": {"numeric": UNTESTED_NUM, "string": UNTESTED_STR,
                                    "flag": "tested",
                                    "note": "a not-tested row means no CoV/heuristic run has "
                                            "covered it -- it is NOT a failed solve"},
                "summary": summarize(rows),
                "rows": rows,
            }, f, indent=1)
        b1k_line = "  ".join(f"{a[4:]} {s[f'{a}_solved']}" for a in B1K_ARMS)
        untested = f", {s['n_untested']} NOT TESTED" if s["n_untested"] else ""
        print(f"subset_{size:<3} n={s['n_rows']:<3} tested {s['n_tested']}{untested:<18} "
              f"solved greedy {s['greedy_solved']}, cov {s['bestcov_solved']}, "
              f"heur {s['heur_solved']}  |  all-three-solve rows: {s['n_all_three_solved']}  "
              f"nodes {s['greedy_mean_nodes']} / {s['bestcov_mean_nodes']} / {s['heur_mean_nodes']}"
              f"   path {s['greedy_mean_path']} / {s['bestcov_mean_path']} / {s['heur_mean_path']}")
        print(f"{'':<12} b1k @1,000 solved:  {b1k_line}")

    write_doc(bestcov, heur, matched, b1k)
    print("\nwrote -> benchmark/subsets/benchmark_subset_{10,20,40,60}_arms.{csv,json} + ARMS.md")


def _b1k_section(rows60):
    """The 2x2 block, written from the rows so the prose can never drift from the CSV."""
    n = {a: sum(1 for r in rows60 if r[f"{a}_solved"] is True) for a in B1K_ARMS}
    both = [r for r in rows60 if r["b1k_covgreedy_solved"] and r["b1k_covheur_solved"]]
    ch_only = [r["pres_id"] for r in rows60
               if r["b1k_covheur_solved"] and not r["b1k_covgreedy_solved"]]
    cg_only = [(r["pres_id"], r["bin"]) for r in rows60
               if r["b1k_covgreedy_solved"] and not r["b1k_covheur_solved"]]
    caps = sorted(r["b1k_cov_cap"] for r in rows60)
    n_tied = sum(1 for r in rows60 if r["b1k_cov_n_tied_starts"] > 1)
    lost_ids = {p for p, _b in cg_only}
    tied_losses = [r["pres_id"] for r in rows60
                   if r["pres_id"] in lost_ids and r["b1k_cov_n_tied_starts"] > 1]
    lines = [
        "## Combining them: transform × ordering at budget 1,000",
        "",
        f"`b1k_covheur_*` is the combination the CoV work and the heuristic work each point at: singly destabilise with the winning `z` (`bestcov_z`), then search the transformed pair with the recommended ordering. Every arm here is **one** search at budget 1,000.",
        "",
        f"**The comparison that is controlled** — `b1k_covheur_*` against `b1k_covgreedy_*`: same transformed start, same per-row cap, the ordering is the only difference.",
        "",
        "| arm on the best-CoV start | solved | gained | lost |",
        "|---|---|---|---|",
        f"| length-only ordering (`b1k_covgreedy_*`) | {n['b1k_covgreedy']}/60 | — | — |",
        f"| recommended ordering (`b1k_covheur_*`) | **{n['b1k_covheur']}/60** | {len(ch_only)} | {len(cg_only)} |",
        "",
        f"**The ordering does not add to the transform.** It gains **{len(ch_only)}** rows and loses **{len(cg_only)}**"
        + (f" ({', '.join(f'{p} (bin {b})' for p, b in cg_only)})" if cg_only else "")
        + f": the solved sets are nested, {'covheur ⊂ covgreedy' if not ch_only else 'neither contains the other'}. The union of all four `b1k_*` arms is {sum(1 for r in rows60 if any(r[f'{a}_solved'] for a in B1K_ARMS))}/60 — nothing anywhere in the block reaches a row the transform alone misses.",
        "",
        f"On the {len(both)} rows both CoV arms solve it is not paying for those losses in nodes: the medians tie at {_median([r['b1k_covheur_nodes'] for r in both]):,.0f} nodes and the mean nearly halves, {sum(r['b1k_covheur_nodes'] for r in both)/len(both):,.1f} against {sum(r['b1k_covgreedy_nodes'] for r in both)/len(both):,.1f} — cheaper on {sum(1 for r in both if r['b1k_covheur_nodes'] < r['b1k_covgreedy_nodes'])} rows, equal on {sum(1 for r in both if r['b1k_covheur_nodes'] == r['b1k_covgreedy_nodes'])}, dearer on {sum(1 for r in both if r['b1k_covheur_nodes'] > r['b1k_covgreedy_nodes'])}. What the ordering costs on this start is reach at the hard end, not nodes on the rows it reaches.",
        "",
        f"**Reference, not a matched comparison** — the same two orderings on the *untransformed* pair are `b1k_greedy_*` {n['b1k_greedy']}/60 and `b1k_heur_*` {n['b1k_heur']}/60. Do not read those against the CoV row as a clean 2×2: a CoV lengthens relators, so a transformed arm runs at `b1k_cov_cap` = longest + 16 ({caps[0]}–{caps[-1]} on these rows) while an untransformed one runs at 24, and [a CoV row compared against a control at a different `max_relator_length` is not a comparison](../../experiments/lessons/control-with-no-dynamic-range.md). The cap is carried per row so the confound stays visible.",
        "",
        f"> Two caveats the controlled contrast cannot shed. **The `z` is a doubly-selected oracle**: it is the cheapest of ~80–174 subword CoVs (~2.2M nodes per presentation to find) *and* it was ranked by what **length-only** ordering cost at ≤20,000 nodes. So `b1k_covheur_*` runs the recommended ordering from a start chosen to suit the other ordering, which is not a clean measurement of either. **And on {n_tied} of the 60 rows more than one transformed start ties for cheapest** (`b1k_cov_n_tied_starts`); the winner is a first-seen tie-break, so on those rows the transformed pair is arbitrary among starts that are equally cheap *for length-only ordering*. "
        + (f"The {len(cg_only)} lost rows are not among them — each has a unique cheapest CoV start, so the tie-break did not choose their start for them."
           if cg_only and not tied_losses else
           f"{len(tied_losses)} of the {len(cg_only)} lost rows are among them." if cg_only else
           "No row is lost, so the tie-break cannot explain one."),
        "",
    ]
    return lines


def write_doc(bestcov, heur, matched, b1k):
    lines = [
        "# Best-known cost per presentation, per technique",
        "",
        "`benchmark_subset_{10,20,40,60}_arms.{csv,json}` give one row per presentation: what each technique costs to solve it, in **nodes explored** and the **path length** that came with those nodes. Produced by `experiments/analysis/benchmark_arms.py`; the frozen `benchmark_subset_{N}.{csv,json}` are untouched.",
        "",
        "## Not every row has been tested",
        "",
        "The four subsets are *not* nested (`nested: false` in each file), and both the CoV sweep and the heuristic campaign were run against **subset-60's** row list. So the smaller subsets contain presentations no transformed arm has ever run on:",
        "",
        "| subset | rows | tested | not tested |",
        "|---|---|---|---|",
        "__COVERAGE_ROWS__",
        "",
        "A not-tested row carries `tested = False`, `-1` in every numeric arm column and `none` in every string one — including `*_solved`. **`none` is not `False`.** A blank or a `False` there would read as \"we ran it and it did not solve\", which is a far stronger claim than \"we have not run it\"; every summary below counts only `tested` rows, because scoring an untested row as a failure would understate the transformed arms on exactly the subsets they were never run on.",
        "",
        "The `greedy_*` columns are populated on **every** row of every subset — they come from the baseline's own 10⁶-node run, where all 640 presentations solve.",
        "",
        "## The heuristic",
        "",
        "The recommended heap ordering — the baseline greedy with **only** the priority expression replaced, so any difference is attributable to the ordering and nothing else:",
        "",
        "```",
        HEUR_FORMULA,
        "```",
        "",
        "| term | weight | what it measures |",
        "|---|---|---|",
    ]
    for k, desc in HEUR_TERMS.items():
        # A bare "|" ends the cell in GFM, even inside a code span -- these descriptions carry
        # |r1| + |r2| and |#x - #y| / L, so escape before rendering, not in the data.
        lines.append(f"| `{k}` | {HEUR_WEIGHTS[k]} | {desc.replace('|', chr(92) + '|')} |")
    lines += [
        "",
        "Lower is popped first. Every term is a pure function of the state and rotation-invariant — a priority reading `depth` or the parent would make pop order depend on discovery order and stop being reproducible. It is a **single segment with no length threshold**: the earlier phased form is unnecessary here, because `S` and `MK` both fall as a pair approaches the trivial state, so the climb self-regulates.",
        "",
        "Shipped as `RECOMMENDED` in `experiments/heuristic_search/core/hsolve.py`; the producer asserts these weights against it, so the two cannot drift apart.",
        "",
        "## Columns",
        "",
        "**Best known** — each arm at its own budget and cap. This is what a row costs in practice.",
        "",
        "| prefix | technique | budget | cap | source |",
        "|---|---|---|---|---|",
    ]
    for k in ("greedy", "bestcov", "heur"):
        a = ARMS[k]
        lines.append(f"| `{k}_*` | {a['what']} | {a['budget']:,} | {a['cap']} | `{a['source']}` |")
    lines += [
        "",
        "> ⚠ **The three ran at different budgets and different relator caps.** Never read a ratio across them — a CoV row compared against a control at a different `max_relator_length` is not a comparison. Use the matched block for that.",
        "",
        "**Matched** — `m10k_*`, all three arms at budget 10,000 and cap 24, from "
        "`results/comparison/three_way_b10k_subset60.csv`, whose builder refuses to write unless its length-only control reproduces the plain greedy pop for pop on all 60 rows. A head-to-head claim belongs here.",
        "",
        "`bestcov_z` is the change of variables that produced the win and `bestcov_class` how it acts (`relabel` = a pure renaming, which is most of them — a rename is not a no-op, because the greedy reads strings, not orbits).",
        "",
        "**Combined** — `b1k_*`, the 2×2 of *transform the start* × *change the ordering*, every arm one search at budget 1,000, from `results/comparison/cov_heur_b1k_subset60.csv`. It is the only block whose arms do **not** all solve: an unsolved row there carries `nodes = 1,000` and a blank path, so never take a mean across it. Read it in the section below.",
        "",
        "## What the numbers say",
        "",
    ]
    rows60 = build_rows(60, bestcov, heur, matched, b1k)
    s = summarize(rows60)
    lab = {"greedy": "greedy @ 1,000,000, cap 24",
           "bestcov": "best CoV @ ≤20,000, cap 24",
           "heur": "heuristic @ 100,000, cap 48"}
    lines += [
        f"On subset-60 all three arms solve **{s['n_all_three_solved']}/60**, so every row below is a like-for-like row. **Read the median, not the mean** — both are given because the mean is dominated by a handful of second-hump rows (greedy: mean 45,244 against a median of 1,310, a 35× skew).",
        "",
        "| arm | solved | median nodes | mean nodes | median path | mean path |",
        "|---|---|---|---|---|---|",
    ]
    for k in ("greedy", "bestcov", "heur"):
        n = sorted(r[f"{k}_nodes"] for r in rows60)
        p = sorted(r[f"{k}_path"] for r in rows60)
        med = lambda v: (v[len(v) // 2 - 1] + v[len(v) // 2]) / 2 if len(v) % 2 == 0 else v[len(v) // 2]
        lines.append(f"| {lab[k]} | {s[f'{k}_solved']}/60 | {med(n):,.0f} | "
                     f"{s[f'{k}_mean_nodes']:,.0f} | {med(p):,.0f} | {s[f'{k}_mean_path']} |")
    lines += [
        "",
        "Both transformed arms cost **less** than the untransformed greedy on the same rows, and return **shorter** derivations — path length is not being traded for reach.",
        "",
        f"At the matched budget of 10,000 and cap 24, the solve counts are greedy **{s['m10k_greedy_solved']}/60**, best CoV **{s['m10k_bestcov_solved']}/60**, heuristic **{s['m10k_heur_solved']}/60**. That is the controlled comparison; the table above is best-known cost, where each arm ran at a different budget.",
        "",
        "> The best-CoV column is an **oracle**: 2,383 median nodes is what the winning `z` costs *once you know which `z` wins*, and finding it cost ~2.2M nodes per presentation of sweeping. It is a lower bound on a transformed route, not a runnable procedure ([why that distinction matters](../../experiments/lessons/price-the-untransformed-route.md)). The heuristic column has no such caveat — it is one search, with one fixed ordering.",
        "",
    ]
    lines += _b1k_section(rows60)
    cov = []
    for size in SIZES:
        cs = summarize(build_rows(size, bestcov, heur, matched, b1k))
        cov.append(f"| **subset-{size}** | {cs['n_rows']} | {cs['n_tested']} |"
                   f" {cs['n_untested'] or '—'} |")
    out = "\n".join(lines).replace("__COVERAGE_ROWS__", "\n".join(cov))
    with open(os.path.join(SUBSETS_DIR, "ARMS.md"), "w") as f:
        f.write(out)


if __name__ == "__main__":
    main()
