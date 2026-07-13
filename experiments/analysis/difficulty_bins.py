"""Label all 640 ms640 presentations with a difficulty bin.

The bin is an **equal-width slice of log10(nodes_explored)**, not a decile.
Difficulty here is multiplicative -- 10 -> 20 nodes doubles the work, 500,000 ->
500,010 is nothing -- so equal *ratios*, not equal differences, are what "one
step harder" means. Ten equal log slices over [min, max] make every bin exactly
``10**((log10(max) - log10(min)) / 10)`` times more expensive than the one below
it. Deciles would instead put five of the ten levels inside nodes <= 11, because
half of ms640 solves that fast.

Truth comes from the 1M-budget run: every one of the 640 solves there, so no row
is censored, and (nodes_explored, path_length) are the *true* costs -- a search
at budget B is exactly the first B pops of any longer search, so a solved row
never moves when the budget is raised.

The 50k columns ride along because 50k is the planned comparison budget for the
stable-AC experiments: a presentation the baseline cannot solve at 50k has no
speedup ratio, only a newly-solved/not verdict. For those, ``progress_at_50k`` --
``min_relator_length`` minus the starting total length -- is the metric that still
says something (< 0 = the search got below where it started). It is the same key
the reach tier scores on, so the two tiers are read the same way. On a *solved* row
it is just ``2 - start`` and carries no information: the search reached trivial.

``aut_class`` is the Aut(F2) / change-of-variables class -- the exact orbit
invariant from ``whitehead.canonical_form``. The 640 collapse to **113** classes,
so ms640 holds far fewer *distinct problems* than presentations.

It is a column, **not** a dedup key. Search cost is not an orbit invariant: 623
and 636 are provably Aut-equivalent yet cost 59,710 vs 213,882 nodes (and 708 vs
678 path). Two coordinate systems on one problem are two genuinely different test
instances for a *search*, and the gap between them is exactly what Branch B (change
of variables) sets out to exploit -- if cost were an orbit invariant, CoV could
never gain anything. What the column is for: (a) a technique that canonicalises
first maps a whole class to one representative, so its runs on 623 and 636 return
identical numbers -- duplicated compute, and a summary statistic that double-counts
that orbit; (b) it makes the sampling weight visible (subset_20's four hardest
picks cover only three classes).

AC-equivalence, by contrast, is vacuous here: every ms640 presentation is
AC-trivialisable by construction, so all 640 lie in one AC class.

Writes ``results/benchmark/difficulty_bins.csv``. Read-only over ``results/``::

    .venv/bin/python3 -m experiments.analysis.difficulty_bins
"""

import argparse
import csv
import json
import math
import os
from collections import Counter

from experiments.analysis.whitehead import canon_pair, canonical_form

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASELINE_DIR = os.path.join(REPO, "results", "greedy_baseline")
OUT_DIR = os.path.join(REPO, "results", "benchmark")

TRUTH_BUDGET = 1_000_000      # every presentation solves here -- nothing censored
COMPARE_BUDGET = 50_000       # the budget Steps 3-5 actually run at
N_BINS = 10


def _load(budget):
    """The one jsonl for this budget, keyed by pres_id."""
    hits = [f for f in os.listdir(BASELINE_DIR)
            if f.startswith(f"greedy_{budget}_640_") and f.endswith(".jsonl")]
    if len(hits) != 1:
        raise SystemExit(f"expected exactly one budget-{budget} file, found {hits}")
    with open(os.path.join(BASELINE_DIR, hits[0])) as f:
        rows = [json.loads(ln) for ln in f if ln.strip()]
    if len(rows) != 640:
        raise SystemExit(f"{hits[0]}: expected 640 rows, found {len(rows)}")
    return hits[0], {r["pres_id"]: r for r in rows}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bins", type=int, default=N_BINS)
    args = ap.parse_args()

    truth_file, truth = _load(TRUTH_BUDGET)
    cmp_file, cmp_ = _load(COMPARE_BUDGET)

    unsolved = [i for i, r in truth.items() if not r["solved"]]
    if unsolved:
        raise SystemExit(f"budget {TRUTH_BUDGET} left {len(unsolved)} unsolved; "
                         "the ranking would be censored")

    lo = math.log10(min(r["nodes_explored"] for r in truth.values()))
    hi = math.log10(max(r["nodes_explored"] for r in truth.values()))
    width = (hi - lo) / args.bins
    edges = [lo + i * width for i in range(args.bins + 1)]

    def bin_of(nodes):
        # clamp: the max lands exactly on the top edge, which would index past the end
        return min(int((math.log10(nodes) - lo) / width), args.bins - 1)

    # Aut(F2) orbit invariant. Class ids are assigned by sorted canonical form, so
    # they are stable across runs and do not depend on iteration order.
    forms = {r["pres_id"]: canonical_form(canon_pair(r["r1"], r["r2"]))
             for r in truth.values()}
    if any(capped for _, _, capped in forms.values()):
        raise SystemExit("an Aut orbit hit the enumeration cap; the class id is unsound")
    class_id = {cf: i for i, cf in
                enumerate(sorted({cf for cf, _, _ in forms.values()}))}

    # difficulty_rank ties break the same way as results/graphs/difficulty_ranking.csv
    order = sorted(truth.values(),
                   key=lambda r: (r["nodes_explored"], r["path_length"], r["pres_id"]))

    out = []
    for rank, r in enumerate(order):
        pid, n = r["pres_id"], r["nodes_explored"]
        b = bin_of(n)
        c = cmp_[pid]
        cf, orbit, _ = forms[pid]
        out.append({
            "pres_id": pid,
            "difficulty_rank": rank,
            "bin": b,
            "bin_lo_nodes": round(10 ** edges[b]),
            "bin_hi_nodes": round(10 ** edges[b + 1]),
            "nodes_explored": n,
            "path_length": r["path_length"],
            "log10_nodes": round(math.log10(n), 4),
            "aut_class": class_id[cf],
            "aut_min_total": cf[0],
            "aut_rep_r1": cf[1][0],
            "aut_rep_r2": cf[1][1],
            "aut_orbit_size": orbit,
            "start_length": len(r["r1"]) + len(r["r2"]),
            "solved_at_50k": c["solved"],
            "nodes_at_50k": c["nodes_explored"],
            "path_at_50k": c["path_length"],
            "min_relator_length_at_50k": c["min_relator_length"],
            # < 0 = the search got below its own starting length. Only meaningful on an
            # unsolved row; on a solved one it is just 2 - start.
            "progress_at_50k": c["min_relator_length"] - (len(r["r1"]) + len(r["r2"])),
            "r1": r["r1"],
            "r2": r["r2"],
        })

    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, "difficulty_bins.csv")
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)

    counts = Counter(r["bin"] for r in out)
    print(f"truth   : {truth_file}")
    print(f"compare : {cmp_file}")
    print(f"log10(nodes): {lo:.3f} -> {hi:.3f} | {args.bins} bins of {width:.4f} "
          f"decades -> each bin x{10 ** width:.2f} the one below")
    print(f"Aut(F2)     : the 640 presentations are {len(class_id)} distinct classes "
          f"(orbits fully enumerated)\n")
    print(f"{'bin':>3} {'node edges':>19} {'members':>15} {'n':>4} {'path range':>12} "
          f"{'solved@50k':>11} {'aut cls':>8}")
    for b in range(args.bins):
        m = [r for r in out if r["bin"] == b]
        n_solved = sum(r["solved_at_50k"] for r in m)
        ns = [r["nodes_explored"] for r in m]
        ps = [r["path_length"] for r in m]
        n_cls = len({r["aut_class"] for r in m})
        print(f"{b:>3} {round(10**edges[b]):>8}-{round(10**edges[b+1]):<10} "
              f"{min(ns):>6}-{max(ns):<8} {counts[b]:>4} "
              f"{min(ps):>4}-{max(ps):<7} {n_solved:>4}/{counts[b]} "
              f"{n_cls:>5}/{counts[b]}")
    un = [r for r in out if not r["solved_at_50k"]]
    if un:
        print(f"\nunsolved at 50k: {len(un)} (bins 8-9). progress_at_50k = "
              f"min_relator_length - start, < 0 means it got below where it began:")
        for r in sorted(un, key=lambda r: r["pres_id"]):
            print(f"  pres {r['pres_id']:>3}  start={r['start_length']:>2}  "
                  f"min_relator_length={r['min_relator_length_at_50k']:>2}  "
                  f"progress={r['progress_at_50k']:>+3}")
    print(f"\n-> {os.path.relpath(path, REPO)}  ({len(out)} rows)")


if __name__ == "__main__":
    main()
