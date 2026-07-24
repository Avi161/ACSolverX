"""The two best orderings against the baseline at the 1,000-node ceiling, on benchmark subset 20.

Budget 1,000 is the hard local maximum (``experiments/lessons/local-run-budget-cap.md``) and this
script must never be edited to exceed it -- ``_BUDGET_CEILING`` is asserted, not commented.

Why run it at all, when 500 already ranked the arms: a search at budget B is exactly the first B
pops of any longer search, so 1,000 is the 500-node run plus 500 more pops. That does not re-test
the ordering, it tests whether the ordering's advantage **survives** as the baseline is given
enough budget to catch up. An opening heuristic that only wins by reaching the goal sooner will
converge back to the control here; one that wins by reaching states the control never orders
highly will not. Those two look identical at 500 and have opposite consequences for a production
run at 50k.

    python3 -m experiments.heuristic_search.run_top2_1000
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.heuristic_search.hsearch import PRIORITIES, ROOT   # noqa: E402
from experiments.heuristic_search.run_sweep import (                # noqa: E402
    MRL, OUT, compare, control_gate, load, run, subset_ids,
)

_BUDGET_CEILING = 1_000
BUDGETS = (500, 1_000)
ARMS = ("length+4.0*knots", "knots_first@endgame16")   # the top two on the tuning set at 500


def main():
    assert max(BUDGETS) <= _BUDGET_CEILING, "1,000 nodes is the hard local cap -- never raise it"
    pres = load(subset_ids(20))
    n = len(pres)
    out = {}

    for budget in BUDGETS:
        control_gate(pres, budget)
        ctrl = run(pres, budget, "length")
        out[budget] = {"length": compare(ctrl, ctrl)}
        for a in ARMS:
            out[budget][a] = compare(run(pres, budget, a), ctrl)

    print(f"\n{'=' * 96}\nBENCHMARK SUBSET 20  ·  the two best orderings vs the baseline"
          f"\n  control gate passed at every budget (length priority == greedy_search, pop for pop)"
          f"\n{'=' * 96}")
    print(f"  {'priority':26s}" + "".join(f"{'@' + str(b):>26}" for b in BUDGETS))
    for name in ["length"] + list(ARMS):
        cells = ""
        for b in BUDGETS:
            r = out[b][name]
            if name == "length":
                cells += f"{r['solved']:>3d}/{n}".rjust(26)
            else:
                cells += (f"{r['solved']:>3d}/{n}  {r['net']:+d}  "
                          f"(w{len(r['won'])} l{len(r['lost'])}) p={r['sign_p']:.2f}").rjust(26)
        print(f"  {name:26s}{cells}")

    print(f"\n  nodes per commonly-solved search (lower is better):")
    for b in BUDGETS:
        for a in ARMS:
            r = out[b][a]
            if r["nodes_both_mean"] is not None:
                d = r["nodes_both_mean"] / r["nodes_both_ctrl_mean"]
                print(f"    @{b:<5d} {a:26s} {r['nodes_both_mean']:7.1f} vs "
                      f"{r['nodes_both_ctrl_mean']:7.1f} ctrl   x{d:.2f}  (n={r['n_both']})")

    print(f"\n  did the baseline catch up between 500 and 1,000?")
    for a in ARMS:
        print(f"    {a:26s} net {out[500][a]['net']:+d} @500  ->  {out[1000][a]['net']:+d} @1000")

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "top2_1000.json"), "w") as f:
        json.dump({"subset": "benchmark_subset_20", "n": n, "budgets": list(BUDGETS),
                   "arms": list(ARMS), "max_relator_length": MRL,
                   "results": {str(k): v for k, v in out.items()}}, f, indent=1)
    print(f"\nwrote -> {os.path.relpath(OUT, ROOT)}/top2_1000.json")


if __name__ == "__main__":
    main()
