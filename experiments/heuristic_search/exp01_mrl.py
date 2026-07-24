"""EXP-01 -- does letting the relators expand past 24 buy anything, and what does it cost?

Every later experiment has to pick a cap, and picking it by taste would be picking the search
space by taste. ``max_relator_length`` is the one knob that changes which states *exist*: lowering
it strictly shrinks the reachable set, so it can only reduce the solve rate, while raising it
admits longer intermediates -- the climb over the two-hump barrier -- at a branching cost that
grows like the product of the two relator lengths.

So this measures both sides on the same slice: solves and progress (what a bigger cap buys) and
seconds (what it costs). The baseline ordering is used throughout, because the question here is
about the space, not the ordering; whichever cap wins becomes the default every arm is compared
at, control included.

    python3 -m experiments.heuristic_search.exp01_mrl
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.heuristic_search.hlab import BASELINE_CONFIG, LOGS   # noqa: E402
from experiments.heuristic_search.lab import evaluate, read           # noqa: E402

CAPS = (24, 32, 48, 64)
BUDGETS = (500, 1000)
SLICE = "train"
OUT = os.path.join(LOGS, "EXP01_mrl.jsonl")


def main():
    t0 = time.perf_counter()
    for budget in BUDGETS:
        for mrl in CAPS:
            evaluate([BASELINE_CONFIG], SLICE, budget, mrl, OUT,
                     label=f"EXP01 b{budget} mrl{mrl}")
    wall = time.perf_counter() - t0

    res = read(OUT, by=("budget", "mrl"))
    lines = ["# EXP-01 — the relator cap: what expansion buys and what it costs", "",
             f"Slice: `{SLICE}` (40 presentations). Ordering: the baseline (`L`) throughout — this "
             "experiment is about the reachable space, not about the heap order. `min_total` is "
             "the shortest total length reached; `Δmin` averages it over the presentations that "
             "did **not** solve, against the cap-24 arm.", ""]
    lines.append("| budget | cap | solved | mean nodes (solved) | mean path | mean min_total "
                 "(unsolved) |")
    lines.append("|---|---|---|---|---|---|")
    for budget in BUDGETS:
        for mrl in CAPS:
            arm = res.get(f"{budget} | {mrl}")
            if not arm:
                continue
            sol = [r for r in arm.values() if r["solved"]]
            uns = [r for r in arm.values() if not r["solved"]]
            mn = sum(r["nodes"] for r in sol) / len(sol) if sol else float("nan")
            mp = sum(r["path_length"] for r in sol) / len(sol) if sol else float("nan")
            mt = sum(r["min_total"] for r in uns) / len(uns) if uns else float("nan")
            lines.append(f"| {budget} | {mrl} | {len(sol)}/{len(arm)} | {mn:.0f} | {mp:.1f} | "
                         f"{mt:.2f} |")
    lines += ["", f"Wall clock for the whole sweep: {wall/60:.1f} min on 9 workers.", ""]

    with open(os.path.join(LOGS, "EXP01_mrl.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
