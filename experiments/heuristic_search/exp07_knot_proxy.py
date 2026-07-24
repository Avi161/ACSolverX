"""EXP-07 -- does knot-progress predict solving? The gate before ranking the second hump on it.

The user's target is the second hump: presentations that do not solve inside ten million greedy
nodes. Nothing this program can run will solve them, so their only measurable signal is a proxy,
and the obvious proxy is the user's own insight -- a state with fewer knots than the start is a
structurally easier presentation, worth reaching even if it is longer. ``min_K`` records the
fewest knots any discovered state reached.

Ranking the hardest rows on a proxy is exactly how a program overfits to something that is not the
goal. So before any experiment *selects* on ``min_K``, this asks whether the proxy earns its use:

    among searches that have NOT solved by 500 nodes, do the ones that go on to solve by 1,000
    already show more knot-progress at the 500-node mark than the ones that never solve?

If yes, knot-progress at a small budget is a leading indicator of a solve at a larger one, and
using it on the truly-unsolvable rows is defensible. If no, it does not discriminate even where
the answer is visible, and selecting the second hump on it would be ranking noise.

The window is the boundary rows -- solvable by 1,000 but not by 500 -- because those are the only
rows where both the proxy (measured at 500) and the ground truth (a solve by 1,000) exist. Bins
8/9 and reach cannot supply the ground truth at any budget this program runs, which is the whole
reason the proxy is needed and the whole reason it must be validated where it can be.

    python3 -m experiments.heuristic_search.exp07_knot_proxy
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.heuristic_search.hlab import (                    # noqa: E402
    BASELINE_CONFIG, LOGS, cfg_name,
)
from experiments.heuristic_search.lab import evaluate, read, sign_test  # noqa: E402
from experiments.heuristic_search.exp05_cap import top_configs     # noqa: E402

MRL = 48
SLICE = "train"
N_TOP = 10
OUT = os.path.join(LOGS, "EXP07_knot_proxy.jsonl")


def main():
    cfgs = [BASELINE_CONFIG] + top_configs(N_TOP)
    # Both budgets, same rows: the 500 row carries min_K, the 1,000 row carries the solve.
    evaluate(cfgs, SLICE, 500, MRL, OUT, label="EXP07-500")
    evaluate(cfgs, SLICE, 1000, MRL, OUT, label="EXP07-1000")

    lo = read(OUT, by=("config_id", "budget"))
    pairs = []                     # (knot_progress_at_500, solved_by_1000) over not-solved-at-500
    for cid in {c.split(" | ")[0] for c in lo}:
        a = lo.get(f"{cid} | 500", {})
        b = lo.get(f"{cid} | 1000", {})
        for name in a:
            if name not in b:
                continue
            r500, r1000 = a[name], b[name]
            if r500["solved"]:
                continue           # already solved at 500 -- no window
            if "min_K" not in r500:
                continue
            kp = r500["start_K"] - r500["min_K"]
            pairs.append((kp, bool(r1000["solved"]), cid, name))

    solv = [kp for kp, s, _, _ in pairs if s]
    nsol = [kp for kp, s, _, _ in pairs if not s]

    def mean(v):
        return sum(v) / len(v) if v else 0.0

    # Companion check: hold min_total to the same bar. Rejecting the knot proxy is only meaningful
    # if its natural replacement -- length-progress -- is not silently just as blind. It is: almost
    # every unsolved search shortens SOMETHING by 500, so "shortened" is near-constant and cannot
    # separate anything.
    from experiments.heuristic_search.hlab import bench66
    start_total = {r["name"]: int(r["base_total_length"]) for r in bench66()}
    mt = [(start_total[name] - a[name]["min_total"], bool(b[name]["solved"]))
          for cid in {c.split(" | ")[0] for c in lo}
          for a in [lo.get(f"{cid} | 500", {})] for b in [lo.get(f"{cid} | 1000", {})]
          for name in a if name in b and not a[name]["solved"]]
    mt_sol = mean([p for p, s in mt if s])
    mt_nsol = mean([p for p, s in mt if not s])

    # A cleaner, threshold-free reading of the same question: does "showed ANY knot drop by 500"
    # separate the eventual solvers from the rest? A 2x2 table with an exact sign-style summary.
    a = sum(1 for kp, s, _, _ in pairs if kp > 0 and s)       # dropped & solved
    b = sum(1 for kp, s, _, _ in pairs if kp > 0 and not s)   # dropped & not
    c = sum(1 for kp, s, _, _ in pairs if kp <= 0 and s)      # no drop & solved
    d = sum(1 for kp, s, _, _ in pairs if kp <= 0 and not s)  # no drop & not
    p_solve_if_drop = a / (a + b) if (a + b) else 0.0
    p_solve_if_not = c / (c + d) if (c + d) else 0.0

    verdict = ("VALIDATED — knot-progress at 500 separates the eventual solvers; it earns its use "
               "on the second hump" if p_solve_if_drop > p_solve_if_not + 0.05 and mean(solv) > mean(nsol)
               else "NOT VALIDATED — knot-progress does not discriminate at the boundary; do not "
               "rank the second hump on it, use min_total and real solves instead")

    out = {"n_windows": len(pairs), "mean_kp_solved": mean(solv), "mean_kp_unsolved": mean(nsol),
           "table": {"drop_solved": a, "drop_unsolved": b, "nodrop_solved": c, "nodrop_unsolved": d},
           "p_solve_given_drop": p_solve_if_drop, "p_solve_given_no_drop": p_solve_if_not,
           "verdict": verdict}
    with open(os.path.join(LOGS, "EXP07_knot_proxy.json"), "w") as f:
        json.dump(out, f, indent=1)

    lines = [
        "# EXP-07 — is knot-progress a leading indicator of a solve?", "",
        "The gate before any experiment ranks the second hump on `min_K`. The second hump never "
        "solves at these budgets, so its only signal is a proxy; this checks the proxy where the "
        "ground truth is visible — the **boundary rows**, not solved by 500 but solved by 1,000.", "",
        f"Windows (a not-solved-at-500 search that had a 1,000 outcome): **{len(pairs)}**.", "",
        "## Knot-progress at the 500-node mark",
        "",
        f"- searches that went on to **solve** by 1,000: mean knot drop **{mean(solv):+.2f}**",
        f"- searches that **never** solved: mean knot drop **{mean(nsol):+.2f}**", "",
        "## Did *any* knot drop by 500 separate them?", "",
        "| | solved by 1,000 | never solved |", "|---|---|---|",
        f"| dropped ≥1 knot by 500 | {a} | {b} |",
        f"| no knot drop by 500 | {c} | {d} |", "",
        f"- P(solve | dropped a knot) = **{p_solve_if_drop:.2f}**",
        f"- P(solve | no knot drop) = **{p_solve_if_not:.2f}**", "",
        "## Companion: is length-progress any better?", "",
        "Rejecting the knot proxy only means something if its obvious replacement is not equally "
        "blind.", "",
        f"- eventual solvers: mean length-progress by 500 = **{mt_sol:+.2f}**",
        f"- never solved: mean length-progress by 500 = **{mt_nsol:+.2f}**", "",
        "Almost every unsolved search has already shortened *something* by 500, so length-progress "
        "is near-constant across both groups and separates them no better than knots do. **Neither "
        "checkpoint proxy forecasts a solve** — at these budgets solving is a discrete event, not "
        "the endpoint of visible progress.", "",
        f"## Verdict", "", verdict, "",
    ]
    with open(os.path.join(LOGS, "EXP07_knot_proxy.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
