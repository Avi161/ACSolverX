"""EXP-13 -- more than two phases, and a climb that gets stronger as the pair gets longer.

Every winning config so far has exactly two phases: pure length below a threshold, one fixed
structural climb above it. That was never argued for -- it was just the first thing tried, and it
won. Two questions it leaves open, and the second is the user's:

1. **Does a third tier help at all?** A two-phase ordering treats a 20-letter pair and a 60-letter
   pair identically. If the right amount of climb differs between "somewhat long" and "very long",
   only a third tier can express it.

2. **Should the knot weight RISE with length?** The user's intuition is that reducing a knot is
   worth more on a hard presentation than an easy one. Difficulty is not a state property and
   cannot enter the priority (EXP-11 covers the one path-dependent term there is), but length is
   the observable that tracks it: harder presentations are longer, and a state deep in the climb
   is longer than one near the endgame. So "value knots more when it is harder" becomes **a knot
   coefficient that increases across the tiers** -- and its control is the same ladder inverted, a
   coefficient that *decreases*. If rising and falling do equally well, the ladder is not encoding
   the user's idea, it is just adding parameters.

Nothing here needs a new feature or a solver change: the segment machinery already accepts any
number of tiers, and this is the first experiment to use more than two.

    python3 -m experiments.heuristic_search.exp13_tiers
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.heuristic_search.hlab import (                    # noqa: E402
    BASELINE_CONFIG, LOGS, cfg_name,
)
from experiments.heuristic_search.lab import evaluate, rank, read  # noqa: E402
from experiments.heuristic_search.perbin import decidable          # noqa: E402

MRL = 48
SLICE = "train"
OUT = os.path.join(LOGS, "EXP13_tiers.jsonl")

ENDGAME = 16          # the boundary every two-tier winner agreed on; held fixed here
MIDS = (24, 28, 32, 40)     # where the second boundary goes
# (low, high) knot coefficients for the mid and long tiers.
LADDERS = {
    "rising": ((4.0, 12.0), (2.5, 9.0), (6.0, 16.0)),
    "falling": ((12.0, 4.0), (9.0, 2.5), (16.0, 6.0)),
}


def configs():
    """Two-tier incumbents + three-tier rising/falling ladders at several mid boundaries."""
    out, meta = [BASELINE_CONFIG], {}

    # The two-tier incumbents, re-run here so the comparison is inside one file.
    for k in (8.0, 12.0):
        c = {"segments": [{"upto": ENDGAME, "w": {"L": 1.0}},
                          {"upto": None, "w": {"L": 1.0, "K": k}}]}
        out.append(c)
        meta[cfg_name(c)] = {"tiers": 2, "mid": None, "dir": "flat", "k": (k, k)}

    for mid in MIDS:
        for direction, pairs in LADDERS.items():
            for lo, hi in pairs:
                c = {"segments": [
                    {"upto": ENDGAME, "w": {"L": 1.0}},
                    {"upto": mid, "w": {"L": 1.0, "K": lo}},
                    {"upto": None, "w": {"L": 1.0, "K": hi}}]}
                cid = cfg_name(c)
                if cid in meta:
                    continue
                out.append(c)
                meta[cid] = {"tiers": 3, "mid": mid, "dir": direction, "k": (lo, hi)}
    return out, meta


def main():
    cfgs, meta = configs()
    for budget in (500, 1000):
        evaluate(cfgs, SLICE, budget, MRL, OUT, label=f"EXP13-{budget}")

    ctrl = cfg_name(BASELINE_CONFIG)
    lines = ["# EXP-13 — three tiers, and a knot weight that rises with length", "",
             f"Endgame boundary fixed at {ENDGAME} (every two-tier winner agreed on it); the "
             "second boundary and the two knot coefficients vary. **rising** = a larger knot "
             "coefficient on the longer tier, the user's \"knots matter more when it is harder\" "
             "made state-pure through length. **falling** = the same ladder inverted, which is the "
             "control: if it does as well, the ladder is adding parameters rather than encoding "
             "the idea.", ""]

    for budget in (500, 1000):
        res = read(OUT, by=("config_id", "budget"))
        arm = {c.rsplit(" | ", 1)[0]: v for c, v in res.items()
               if int(c.rsplit(" | ", 1)[1]) == budget}
        if ctrl not in arm:
            continue
        dec = set(decidable(arm))

        def ds(cid):
            return sum(1 for nm in dec if arm.get(cid, {}).get(nm, {}).get("solved"))

        two = [(ds(c), c) for c in arm if c in meta and meta[c]["tiers"] == 2]
        best_two = max(two, default=(0, None))
        lines += [f"## Budget {budget} — decidable subset ({len(dec)} rows)", "",
                  f"Baseline **{ds(ctrl)}/{len(dec)}**. Best two-tier incumbent "
                  f"**{best_two[0]}/{len(dec)}**.", "",
                  "| mid boundary | rising (k_mid → k_long) | falling |", "|---|---|---|"]
        for mid in MIDS:
            cells = []
            for direction in ("rising", "falling"):
                got = []
                for c, m in meta.items():
                    if m["tiers"] == 3 and m["mid"] == mid and m["dir"] == direction and c in arm:
                        got.append((ds(c), m["k"]))
                got.sort(reverse=True)
                cells.append(", ".join(f"**{s}** ({a:g}→{b:g})" for s, (a, b) in got[:3])
                             or "—")
            lines.append(f"| {mid} | {cells[0]} | {cells[1]} |")
        lines.append("")

        best_three = max(((ds(c), c) for c in arm if c in meta and meta[c]["tiers"] == 3),
                         default=(0, None))
        rise = max((ds(c) for c in arm if c in meta and meta[c]["dir"] == "rising"), default=0)
        fall = max((ds(c) for c in arm if c in meta and meta[c]["dir"] == "falling"), default=0)
        if best_three[0] > best_two[0]:
            verdict = (f"A third tier **helps** at this budget ({best_three[0]} vs "
                       f"{best_two[0]}): `{best_three[1]}`.")
        elif best_three[0] == best_two[0]:
            verdict = (f"A third tier **matches** the two-tier incumbent ({best_three[0]}) and "
                       "costs two more parameters — prefer two tiers.")
        else:
            verdict = (f"A third tier is **worse** ({best_three[0]} vs {best_two[0]}); the extra "
                       "boundary splits the queue without helping.")
        if rise > fall:
            verdict += (f" Rising beats falling ({rise} vs {fall}), which is the direction the "
                        "user's intuition predicts.")
        elif rise == fall:
            verdict += (f" Rising and falling tie ({rise}), so the ladder is not encoding "
                        "\"knots matter more when harder\" — it is just more parameters.")
        else:
            verdict += (f" Falling beats rising ({fall} vs {rise}) — the opposite of the "
                        "intuition, and worth not over-reading at this sample size.")
        lines += [verdict, ""]

    with open(os.path.join(LOGS, "EXP13_tiers.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
