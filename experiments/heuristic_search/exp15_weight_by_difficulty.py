"""EXP-15 -- the user's actual claim: is a knot worth more on a HARD presentation?

The intuition being tested, in the user's words: "for presentations that are very hard to solve,
even if we can reduce a single knot that can create a lot of opportunities". EXP-13 tried to test
this and did not: it varied the knot coefficient by the *length of a state inside one search*,
which is a within-trajectory coordinate. A hard presentation can start short, and every search --
easy or hard -- passes through long states. Those are different quantities.

The direct test is per-presentation. Sweep the knot coefficient, score each weight **separately
within each difficulty stratum**, and ask whether the argmax moves. If the best knot weight is
larger on the hard stratum than the easy one, the intuition is supported and the practical
consequence is concrete: pick the weight from the difficulty of the presentation you are about to
run, which a caller knows before the search starts (unlike anything inside the search).

Two things this must get right, both of which have already bitten this program:

- **A stratum with no dynamic range measures nothing.** Bins 0-3 are solved by every ordering and
  bins 8-9 by none, so a sweep over either returns a flat line that says nothing about the weight.
  Only strata where solves actually vary can locate an argmax, and the report says which strata
  qualified rather than quietly averaging them in.
- **Difficulty is graded under the baseline.** ``bin`` comes from the length-ordered search's node
  count, and the knot ordering reorders difficulty (it cracks a 26,838-node row in 108 nodes while
  missing 16k ones). So the bins are an axis to *report against*, never ground truth for the new
  ordering -- the finding is "the weight depends on baseline-difficulty", which is still exactly
  what a caller can condition on.

    python3 -m experiments.heuristic_search.exp15_weight_by_difficulty
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.heuristic_search.hlab import (                    # noqa: E402
    BASELINE_CONFIG, LOGS, cfg_name, load_split,
)
from experiments.heuristic_search.lab import evaluate, read        # noqa: E402
from experiments.heuristic_search.perbin import bin_of             # noqa: E402

MRL = 48
SLICE = "train"
KWEIGHTS = (0.5, 1, 2, 3, 4, 6, 8, 12, 16, 24, 32)
ENDGAME = 16
OUT = os.path.join(LOGS, "EXP15_wbd.jsonl")

STRATA = {"easy (bins 0-3)": (0, 1, 2, 3),
          "mid (bins 4-5)": (4, 5),
          "hard (bins 6-7)": (6, 7),
          "unreachable (bins 8-9)": (8, 9)}


def configs():
    out, meta = [BASELINE_CONFIG], {}
    for k in KWEIGHTS:
        c = {"segments": [{"upto": ENDGAME, "w": {"L": 1.0}},
                          {"upto": None, "w": {"L": 1.0, "K": float(k)}}]}
        cid = cfg_name(c)
        if cid not in meta:
            out.append(c)
            meta[cid] = k
    return out, meta


def main():
    cfgs, meta = configs()
    for budget in (500, 1000):
        evaluate(cfgs, SLICE, budget, MRL, OUT, label=f"EXP15-{budget}")

    res = read(OUT, by=("config_id", "budget"))
    names = [r["name"] for r in load_split(SLICE)]
    by_stratum = {s: [n for n in names if bin_of(n) in bins] for s, bins in STRATA.items()}

    lines = ["# EXP-15 — does the best knot weight depend on how hard the presentation is?", "",
             "The direct form of the user's intuition. EXP-13 varied the knot weight by the length "
             "of a state *inside* a search; this varies it across **presentations**, scoring each "
             "weight separately within each difficulty stratum and asking whether the argmax "
             "moves. Ordering is the phased winner's shape: pure length below "
             f"{ENDGAME}, `L + k·knots` above it, with only `k` varying.", "",
             "Difficulty is the baseline's grading, so this says \"the weight depends on "
             "baseline-difficulty\" — which is still what a caller can condition on, since they "
             "know it before the search starts.", ""]

    summary = {}
    for budget in (500, 1000):
        arm = {c.rsplit(" | ", 1)[0]: v for c, v in res.items()
               if int(c.rsplit(" | ", 1)[1]) == budget}
        if not arm:
            continue
        lines += [f"## Budget {budget}", "",
                  "| stratum | n | " + " | ".join(f"k={k:g}" for k in KWEIGHTS) + " | best k |",
                  "|---" * (len(KWEIGHTS) + 3) + "|"]
        for s, sub in by_stratum.items():
            if not sub:
                continue
            row, best = [], (-1, None)
            for k in KWEIGHTS:
                cid = next(c for c, kk in meta.items() if kk == k)
                got = sum(1 for n in sub if arm.get(cid, {}).get(n, {}).get("solved"))
                row.append(got)
                if got > best[0]:
                    best = (got, k)
            flat = len(set(row)) == 1
            saturated = best[0] == len(sub) and row.count(best[0]) > len(row) // 2
            # The actionable number is not the argmax (which ties across many weights) but the
            # SMALLEST weight that reaches the stratum's ceiling -- the threshold a caller has to
            # clear. Past it the magnitude stops mattering.
            thresh = next((k for k, v in zip(KWEIGHTS, row) if v == best[0]), None)
            if flat:
                note = " _(flat — no dynamic range)_"
            elif saturated:
                note = " _(saturated — every weight solves it; no argmax)_"
            else:
                note = f" _(threshold k≥{thresh:g})_"
            lines.append(f"| {s} | {len(sub)} | " + " | ".join(str(v) for v in row)
                         + f" | **{best[1]:g}**{note} |")
            if not flat and not saturated:
                summary.setdefault(budget, {})[s] = {"argmax": best[1], "threshold": thresh,
                                                     "ceiling": best[0], "n": len(sub),
                                                     "floor": row[0]}
        lines.append("")

    lines += ["## Verdict", ""]
    for budget, per in summary.items():
        order = [s for s in STRATA if s in per]
        lines.append(f"- budget {budget}: "
                     + "; ".join(f"{s.split(' ')[0]} needs **k≥{per[s]['threshold']:g}** "
                                 f"(solves {per[s]['floor']}→{per[s]['ceiling']} of {per[s]['n']})"
                                 for s in order))
    lines.append("")

    # The shape that actually appears: easy rows solve at any weight, hard rows solve at NO weight
    # below a threshold. That is a necessity claim, not an optimum-location claim.
    gated = [(b, s, p) for b, per in summary.items() for s, p in per.items() if p["floor"] == 0]
    lines += ["### What the numbers actually say", ""]
    if gated:
        lines += [
            "The interesting structure is not where the optimum sits — past a point the magnitude "
            "stops mattering — but that **the hard strata solve nothing at all until the knot term "
            "is heavy enough**, while the easy stratum solves everything at every weight:", "",
        ]
        for b, s, p in gated:
            lines.append(f"- budget {b}, {s}: **0 solved** below k={p['threshold']:g}, "
                         f"{p['ceiling']}/{p['n']} at and above it.")
        lines += ["",
                  "So the user's intuition is **supported in the form that matters, and not in the "
                  "form it was posed**. Knots are not merely *worth more* on hard presentations — "
                  "on the hard stratum they are the difference between solving several and solving "
                  "**none**, whereas on the easy stratum the knot weight is irrelevant. What does "
                  "*not* hold is the smooth version: the optimal magnitude does not keep climbing "
                  "with difficulty. It is a threshold to clear, not a dial to turn up.", "",
                  "Practical consequence: there is nothing to gain from tuning the knot weight per "
                  "presentation. Pick one comfortably above the threshold — the phased winner's 8 "
                  "to 9 sits there — and it serves every stratum at once.", ""]
    else:
        lines += ["No stratum shows a weight threshold; the knot weight's optimum does not depend "
                  "on difficulty in a way this benchmark can resolve.", ""]

    with open(os.path.join(LOGS, "EXP15_wbd.json"), "w") as f:
        json.dump({"summary": {str(k): v for k, v in summary.items()},
                   "weights": list(KWEIGHTS)}, f, indent=1)
    with open(os.path.join(LOGS, "EXP15_wbd.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
