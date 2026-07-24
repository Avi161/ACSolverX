"""Prove ``hcompact`` pops exactly like ``greedy_search_h`` — then measure what it saves.

The claim under test is total: not "same solve rate" but the SAME SEARCH. Since every state is
pushed exactly once, pop order follows from the comparison relation alone; if the two solvers
agree on every scalar field *and* on the first-seen min / max / max-expanded relator strings
(which update on strict inequality only, so they are deterministic and pin discovery order),
across solved and unsolved rows, three configs and two budgets, then the comparator, the score
computation and the enumeration order all agree. A single flipped tie-break anywhere would move
one of these strings on some row.

Sweep: all 66 benchmark rows + the first 12 unsolved-124 rows (full-budget burns, the worst case
for tie-break traffic), configs None / RECOMMENDED / LEAN_SMALL_BUDGET, budgets 500 and 1,000
(the repo's local ceiling). ~470 paired searches.

    .venv/bin/python3 -m experiments.heuristic_search.verify_hcompact
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.heuristic_search.hlab import bench66                # noqa: E402
from experiments.heuristic_search.hsolve import (                    # noqa: E402
    LEAN_SMALL_BUDGET, RECOMMENDED, greedy_search_h,
)
from experiments.heuristic_search.hcompact import (                  # noqa: E402
    HCompactSolver, greedy_search_hcompact,
)
from experiments.heuristic_search.run_ab import load_rows            # noqa: E402

MRL = 48
FIELDS = ("solved", "nodes_explored", "path_length", "min_relator_length",
          "min_relator", "max_relator_length", "max_relator",
          "max_relator_length_expanded", "max_relator_expanded")
# The three shipped configs, plus two that exist ONLY to exercise branches the shipped ones
# never reach (advisor review): "depth" takes hsolve's sc += seg_depth*nd post-processing on
# every push, and "fallback" has no terminal INF segment so states longer than its bound take
# the seg = n_seg / score = L fallback in both solvers. Verified branches, not dead code.
CONFIGS = (("baseline", None), ("recommended", RECOMMENDED), ("lean", LEAN_SMALL_BUDGET),
           ("depth", {"segments": [{"upto": None,
                                    "w": {"L": 1.0, "K": 2.53, "MK": 6.418,
                                          "S": 8.458, "xyimb": 3.292},
                                    "depth": 0.125}]}),
           ("fallback", {"segments": [{"upto": 14, "w": {"L": 1.0, "K": 3.0}}]}))
# Configs whose solve count must be nonzero at budget 1000, so the solved branch -- the only
# place a post-string-lock tie-break divergence is visible -- is pinned per ordering, not in
# aggregate.
MUST_SOLVE = {"recommended", "lean"}


def run_matrix(rows, budgets, label=""):
    n_pairs = bad = 0
    per_cfg_solved = {c: 0 for c, _ in CONFIGS}
    for budget in budgets:
        for cfg_name, cfg in CONFIGS:
            for r in rows:
                a = greedy_search_h(r["r1"], r["r2"], budget, max_relator_length=MRL,
                                    config=cfg, keep_path=False)
                b = greedy_search_hcompact(r["r1"], r["r2"], budget,
                                           max_relator_length=MRL, config=cfg)
                n_pairs += 1
                per_cfg_solved[cfg_name] += a["solved"]
                for f in FIELDS:
                    if a[f] != b[f]:
                        bad += 1
                        print(f"  MISMATCH{label} {cfg_name} b={budget} {r['name']} {f}: "
                              f"hsolve={a[f]!r} hcompact={b[f]!r}")
        print(f"  budget {budget}{label}: cumulative {n_pairs} pairs, {bad} mismatches",
              flush=True)
    return n_pairs, bad, per_cfg_solved


def main():
    rows = ([{"name": r["name"], "r1": r["r1"], "r2": r["r2"]} for r in bench66()]
            + load_rows("unsolved124", subset=12))
    n_pairs, bad, per_cfg = run_matrix(rows, (500, 1000))

    for c in MUST_SOLVE:
        assert per_cfg[c] > 0, f"{c} solved nothing -- its solved branch went unexercised"
    assert bad == 0, f"{bad} field mismatches"
    print(f"\nmain matrix PASS — {n_pairs} paired searches, per-config solves: "
          + ", ".join(f"{c}={n}" for c, n in per_cfg.items()))

    # The chunk-boundary pass: at the production _HB_CHECK_EVERY = 1024 every budget <= 1000
    # search is a SINGLE chunk, so the return-to-Python re-entry (stats round-tripping through
    # st[], score/seg surviving the boundary) never runs above. Shrink the chunk so a 1,000-node
    # burn crosses it four times, and require the same total agreement.
    import experiments.heuristic_search.hcompact as hc
    saved = hc._HB_CHECK_EVERY
    hc._HB_CHECK_EVERY = 200
    try:
        n2, bad2, _ = run_matrix(rows[:20], (1000,), label=" [chunk=200]")
    finally:
        hc._HB_CHECK_EVERY = saved
    assert bad2 == 0, f"{bad2} mismatches with the chunk boundary crossed"
    print(f"chunk-boundary pass PASS — {n2} pairs at _HB_CHECK_EVERY=200")

    print(f"\nALL PASS — {n_pairs + n2} paired searches total, every field identical "
          f"including first-seen min/max/expanded strings")

    s = HCompactSolver("xyx", "yx", max_nodes=10**6, max_relator_length=48,
                       config=RECOMMENDED)
    print(f"reservation for a 10^6-node search at cap 48: "
          f"{s.bytes_reserved()/2**30:.2f} GiB reserved, "
          f"{s.bytes_per_state():.1f} B/state over {s.states_cap:,} slots "
          f"(vs hsolve keep_path=False ~24 GB at the same budget)")


if __name__ == "__main__":
    main()
