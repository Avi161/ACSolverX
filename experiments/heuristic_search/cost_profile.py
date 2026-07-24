"""What the tuned ordering costs: nodes explored and path length, against the baseline.

Solve rate alone cannot say whether an ordering is *better* -- one that reaches more solutions by
wandering into longer, more expensive derivations has traded solution quality for coverage. This
reports both remaining axes.

Every comparison is on the presentations **both arms solve**. That restriction is the whole point:
the tuned arm solves 13-14 presentations the baseline does not, and those are the hard ones with
the longest derivations, so pooling them would make the tuned arm look worse on path length purely
because it got further. The tuned arm's unrestricted mean is reported separately, and must never
be read against the baseline's.

Neither arm claims a shortest path -- best-first by length is not optimal for AC derivations -- so
path length here is solution quality relative to the baseline, not distance from optimal.

    python3 -m experiments.heuristic_search.cost_profile
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.heuristic_search.hsearch import ROOT, hsearch                 # noqa: E402
from experiments.heuristic_search.run_sweep import MRL, OUT, load, subset_ids  # noqa: E402
from experiments.heuristic_search.tune_multi import BASELINE, make_priority    # noqa: E402

BUDGETS = (100, 200, 500, 1_000)          # 1,000 is the hard local ceiling
TUNED = (8.0, 6.23, 0.84, 8.33)


def main():
    assert max(BUDGETS) <= 1_000, "1,000 nodes is the hard local cap"
    pres = load(subset_ids(60))
    out = []
    for b in BUDGETS:
        B = {p: hsearch(r1, r2, b, make_priority(BASELINE), max_relator_length=MRL)
             for p, r1, r2 in pres}
        T = {p: hsearch(r1, r2, b, make_priority(TUNED), max_relator_length=MRL)
             for p, r1, r2 in pres}
        both = [p for p in B if B[p]["solved"] and T[p]["solved"]]
        m = lambda d, ps, k: float(np.mean([d[p][k] for p in ps]))
        out.append({
            "budget": b, "n": len(pres),
            "solved_baseline": sum(B[p]["solved"] for p in B),
            "solved_tuned": sum(T[p]["solved"] for p in T),
            "n_both": len(both),
            "nodes_baseline": m(B, both, "nodes_explored"),
            "nodes_tuned": m(T, both, "nodes_explored"),
            "path_baseline": m(B, both, "path_length"),
            "path_tuned": m(T, both, "path_length"),
            "path_tuned_all_solves": m(T, [p for p in T if T[p]["solved"]], "path_length"),
        })

    print(f"\n{'=' * 100}\nCOST PROFILE  ·  benchmark subset 60  ·  tuned ordering vs baseline"
          f"\n  nodes and path are measured on the presentations BOTH arms solve\n{'=' * 100}")
    print(f"  {'budget':>6} {'solved':>15} {'nodes (both-solved)':>27} {'path (both-solved)':>24}"
          f" {'tuned, all solves':>18}")
    for r in out:
        print(f"  {r['budget']:>6} {r['solved_tuned']:>3d} vs {r['solved_baseline']:>2d} base "
              f"  {r['nodes_tuned']:>7.1f} vs {r['nodes_baseline']:>6.1f} "
              f" x{r['nodes_tuned'] / r['nodes_baseline']:.2f}"
              f"   {r['path_tuned']:>6.2f} vs {r['path_baseline']:>5.2f} "
              f"{r['path_tuned'] - r['path_baseline']:+5.2f}"
              f"   {r['path_tuned_all_solves']:>10.2f} (n={r['solved_tuned']})")

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "cost_profile.json"), "w") as f:
        json.dump({"subset": "benchmark_subset_60", "tuned_params": list(TUNED),
                   "max_relator_length": MRL, "rows": out}, f, indent=1)
    print(f"\nwrote -> {os.path.relpath(OUT, ROOT)}/cost_profile.json")


if __name__ == "__main__":
    main()
