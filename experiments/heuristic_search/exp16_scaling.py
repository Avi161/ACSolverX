"""EXP-16 -- how does the advantage scale with budget? The only honest bridge to Colab.

Everything measured so far lives at 500 and 1,000 nodes because that is the local ceiling. The
user runs at 10^5-10^6. Recommending an ordering on the strength of a 1,000-node result and hoping
it holds three orders of magnitude away is exactly the kind of extrapolation that turns out to be
wrong, so this measures the *shape* of the advantage instead of asserting it: solve count against
budget, for the baseline and each finalist, at every budget the local rule allows.

Three shapes are distinguishable and they imply very different things:

- **Widening** -- the gap grows with budget. The ordering is not just finding the easy solutions
  first, it keeps converting budget into solves the baseline cannot. Best case for Colab.
- **Constant** -- a fixed offset. The ordering is worth a fixed number of presentations and the
  baseline never catches up within this range, but nothing suggests the gap keeps growing.
- **Closing** -- the baseline catches up as budget grows. The ordering would be buying *earliness*,
  not reach, and at 10^6 it would be worth little. This is the outcome that would most change the
  recommendation, which is why it is worth the run.

A search at budget B is exactly the first B pops of any longer search, so the whole curve for one
(config, presentation) comes from a single 1,000-node run: record the node count at which it
solved, and it is solved at every budget at or above that. No extra searching, no cap violation.

    python3 -m experiments.heuristic_search.exp16_scaling
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.heuristic_search.hlab import LOGS, bench66        # noqa: E402
from experiments.heuristic_search.hfast import search_fast         # noqa: E402
from experiments.heuristic_search.perbin import bin_of             # noqa: E402

BUDGET = 1_000               # the local ceiling; every smaller budget is read off this run
MRL = 48
GRID = (50, 100, 200, 300, 500, 700, 1000)
OUT = os.path.join(LOGS, "EXP16_scaling.jsonl")

ORDERINGS = {
    "baseline (length)": {"segments": [{"upto": None, "w": {"L": 1.0}}]},
    "phased K8": {"segments": [{"upto": 16, "w": {"L": 1.0}},
                               {"upto": None, "w": {"L": 1.0, "K": 8.0}}]},
    "phased K+xyimb": {"segments": [
        {"upto": 16, "w": {"L": 1.0}},
        {"upto": None, "w": {"L": 1.0, "K": 8.936, "xyimb": -5.978}}]},
    "richer knot climb": {"segments": [
        {"upto": 16, "w": {"L": 1.0}},
        {"upto": None, "w": {"L": 1.0, "K": 2.53, "MK": 6.418, "S": 8.458, "xyimb": 3.292}}]},
}


def main():
    rows = [r for r in bench66() if r["source"] == "ladder"]
    done = set()
    if os.path.exists(OUT):
        for line in open(OUT):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            done.add((r["ordering"], r["name"]))

    with open(OUT, "a") as f:
        for label, cfg in ORDERINGS.items():
            for row in rows:
                if (label, row["name"]) in done:
                    continue
                res = search_fast(row["r1"], row["r2"], BUDGET, cfg, MRL)
                f.write(json.dumps({
                    "ordering": label, "name": row["name"], "bin": bin_of(row["name"]),
                    "mrl": MRL, "solved": res["solved"],
                    # The node count at which it solved IS the whole curve: solved at every
                    # budget >= this, unsolved below it.
                    "solved_at": res["nodes"] if res["solved"] else None,
                    "path_length": res["path_length"]}) + "\n")
                f.flush()
                os.fsync(f.fileno())

    data = [json.loads(l) for l in open(OUT)]
    hard = [r for r in data if r["bin"] in (4, 5, 6, 7)]     # the decidable band

    def curve(label, subset):
        d = [r for r in subset if r["ordering"] == label]
        return [sum(1 for r in d if r["solved_at"] is not None and r["solved_at"] <= b)
                for b in GRID]

    lines = ["# EXP-16 — how the advantage scales with budget", "",
             "A search at budget B is exactly the first B pops of any longer search, so each "
             f"curve below comes from one {BUDGET}-node run per (ordering, presentation): the node "
             "count at which it solved is the budget from which it is solved. No extra searching.",
             "", "## The decidable band (bins 4–7, 24 rows)", "",
             "| ordering | " + " | ".join(f"{b}" for b in GRID) + " |",
             "|---" * (len(GRID) + 1) + "|"]

    base = curve("baseline (length)", hard)
    for label in ORDERINGS:
        c = curve(label, hard)
        lines.append(f"| {label} | " + " | ".join(str(v) for v in c) + " |")
    lines += ["", "### The gap against the baseline", "",
              "| ordering | " + " | ".join(f"{b}" for b in GRID) + " | shape |",
              "|---" * (len(GRID) + 2) + "|"]
    shapes = {}
    for label in ORDERINGS:
        if label.startswith("baseline"):
            continue
        c = curve(label, hard)
        gap = [a - b for a, b in zip(c, base)]
        # Two different questions, and only the second bears on extrapolation. Over the WHOLE
        # range every good ordering widens -- it has to, since the baseline starts at zero. What
        # matters for a 10^6 run is whether the gap is still growing at the TOP of the range or
        # has already turned over.
        overall = "widening" if gap[-1] > gap[1] else "closing" if gap[-1] < gap[1] else "flat"
        i500 = GRID.index(500)
        d = gap[-1] - gap[i500]
        # +/-1 solve on 24 rows is one presentation and the curves visibly jitter by that much
        # (phased K8 runs +11, +10, +12, +11 over the last four budgets). Anything inside that
        # is called flat rather than dressed up as a trend.
        tail = ("**still growing**" if d >= 2 else
                "**turning over**" if d <= -2 else "flat (±1)")
        shapes[label] = {"gap": gap, "overall": overall, "tail": tail, "tail_delta": d}
        lines.append(f"| {label} | " + " | ".join(f"{g:+d}" for g in gap)
                     + f" | {overall} / tail {tail} |")

    growing = [k for k, v in shapes.items() if "growing" in v["tail"]]
    lines += ["", "## What this implies for a Colab-scale run", "",
              "Over the whole range every finalist widens its gap — which it must, since the "
              "baseline solves nothing below 500. The question that bears on a 10^5–10^6 run is "
              "the **tail**: is the gap still growing where the budget runs out, or has it already "
              "turned over?", ""]
    lines += ["Change in the gap from budget 500 to 1,000, which is the only part of these curves "
              "that speaks to a larger run. One solve on 24 rows is inside the jitter, so a tail "
              "is only called a trend at ±2 or more.", "",
              "| ordering | gap @500 | gap @1000 | change | reading |", "|---|---|---|---|---|"]
    i500 = GRID.index(500)
    for label, v in shapes.items():
        lines.append(f"| {label} | {v['gap'][i500]:+d} | {v['gap'][-1]:+d} | "
                     f"{v['tail_delta']:+d} | {v['tail']} |")
    lines.append("")
    if len(growing) == 1:
        g = growing[0]
        lines += [f"Only **`{g}`** is still converting budget into new solves where the local "
                  "ceiling cuts the curve off. The leaner orderings peak in the middle of the "
                  "range and hold or give ground back: they find their solutions early and then "
                  "stop finding new ones. That is the same crossover EXP-06 found by a completely "
                  "different route — the richer climb gained 25→29 with budget while the lean "
                  "winner plateaued 27→27. **Two independent measurements agreeing on which "
                  "ordering keeps scaling is the strongest evidence in this program for what to "
                  "run at 10^5–10^6 nodes.**", ""]
    elif growing:
        lines += ["Still growing at the ceiling: " + ", ".join(f"`{k}`" for k in growing)
                  + ". These are the ones whose advantage has not yet turned over where the local "
                  "budget runs out, so they are the candidates for a larger run.", ""]
    else:
        lines += ["**No finalist is still growing at the ceiling** — every gap is flat or turning "
                  "over by 1,000 nodes. The orderings buy *earliness* within this range, and their "
                  "value at 10^6 nodes cannot be read off these curves.", ""]

    lines += ["## Where each ordering's solves land in time", "",
              "Median solving budget on the rows each one solves — a low median with a high final "
              "count means it finds its solutions early and keeps finding more.", "",
              "| ordering | rows solved by 1000 | median solving budget | max |",
              "|---|---|---|---|"]
    import statistics
    for label in ORDERINGS:
        d = [r["solved_at"] for r in hard if r["ordering"] == label and r["solved_at"]]
        if d:
            lines.append(f"| {label} | {len(d)}/24 | {statistics.median(d):.0f} | {max(d)} |")

    with open(os.path.join(LOGS, "EXP16_scaling.json"), "w") as f:
        json.dump({"grid": list(GRID), "baseline": base,
                   "curves": {k: curve(k, hard) for k in ORDERINGS},
                   "shapes": shapes}, f, indent=1)
    with open(os.path.join(LOGS, "EXP16_scaling.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
