"""Phase 1 gate B': calibrate (max_total, budget) against a merge we KNOW exists.

`19_52 = 18_9` and `19_46 = 18_11` were found by the 1M-node sweep. A two-source search that
cannot rediscover them at budget B tells us B is too small -- and the *smallest* (max_total,
budget) that does rediscover them is the operating point for the 169-source run.

AC paths must climb before they descend (the "hump"), so `max_total` is the knob that matters:
too tight and the ball is exhausted in tens of pops.
"""
import csv
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.equivalence_classes.aca_search import multi_source_search  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPS = {r["name"]: (r["r1"], r["r2"]) for r in csv.DictReader(
    open(os.path.join(ROOT, "data", "ms_unsolved_reps", "ms_reps_unsolved.csv")))}


def try_pair(a, b, max_total, budget, seam_only):
    pa, pb = REPS[a], REPS[b]
    t0 = time.time()
    dsu, merges, _, stats = multi_source_search(
        [(a, pa[0], pa[1]), (b, pb[0], pb[1])],
        nodes_per_source=budget, max_total=max_total, seam_only=seam_only,
        max_states=4_000_000, stop_when_merged=True)
    return (dsu.find(0) == dsu.find(1)), stats, time.time() - t0, merges


def main():
    pair = (sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else ("19_52", "18_9")
    print(f"target: {pair[0]} = {pair[1]}   "
          f"(totals {sum(map(len, REPS[pair[0]]))} and {sum(map(len, REPS[pair[1]]))})\n")
    print(f"{'moves':<5} {'max_total':>9} {'budget':>7} {'merged':>7} {'pops':>7} "
          f"{'states':>9} {'sec':>6}")
    for seam_only in (True, False):
        lbl = "seam" if seam_only else "full"
        for max_total in (24, 26, 28, 30, 32):
            merged, stats, dt, merges = try_pair(*pair, max_total, 20_000, seam_only)
            print(f"{lbl:<5} {max_total:>9} {20000:>7} {str(merged):>7} {stats['popped']:>7} "
                  f"{stats['states']:>9} {dt:>6.1f}"
                  f"{'  <-- ' + merges[0]['kind'] if merged else ''}"
                  f"{'  [state cap]' if stats['capped'] else ''}")
            if merged:
                break


if __name__ == "__main__":
    main()
