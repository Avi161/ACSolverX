"""EXP-22 -- is "pick a complement from a different family" a real strategy, or hindsight?

EXP-21 reported that pairing the recommended climb with a knot-free ordering lifts 19/24 to 23/24,
and admitted the weakness in the same breath: those complements were chosen *because* they solved
rows the finalists miss. Selecting an arm on the rows you then score it on inflates the number by
an unknown amount, and "unknown" is not good enough for a recommendation.

This settles it without spending a fresh slice, and without running a single new search. EXP-19
already scored **320 configs on 45 presentations at budget 1,000**, so the marginal-coverage
question can be asked entirely inside that matrix, under cross-validation:

    repeat: split the rows in half; on half A, pick the config that adds the most rows to the
    recommended climb's coverage; measure how much that same config adds on half B.

The gap between the two is exactly the hindsight premium. Three things get measured against it:

- **the complement strategy** -- pick the best complement on A, score its marginal gain on B;
- **a same-family control** -- the best *stand-alone* config on A, which is what someone would
  reach for who had not noticed that redundancy is the problem;
- **a random control** -- a config drawn at random, which is what "any second ordering" is worth.

If the complement strategy's held-out gain is no better than picking the best stand-alone arm,
then EXP-21's finding is hindsight and the two-ordering advice should be withdrawn. If it holds up,
the advice is real and the honest effect size is the held-out number, not EXP-21's 23/24.

    python3 -m experiments.heuristic_search.exp22_complement_cv
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.heuristic_search.hlab import LOGS, cfg_name       # noqa: E402
from experiments.heuristic_search.lab import read                  # noqa: E402

SEED = 5150
N_SPLITS = 200
SRC = os.path.join(LOGS, "EXP19_joint1000.jsonl")

RECOMMENDED = {"segments": [
    {"upto": None, "w": {"L": 1.0, "K": 2.53, "MK": 6.418, "S": 8.458, "xyimb": 3.292}}]}


def main():
    res = read(SRC)
    rec_id = cfg_name(RECOMMENDED)
    if rec_id not in res:
        raise SystemExit(f"{rec_id} not in {SRC} -- run EXP-19 first")

    names = sorted({n for v in res.values() for n in v})
    solved = {cid: {n for n, r in v.items() if r["solved"]} for cid, v in res.items()}
    base = solved[rec_id]
    arms = [c for c in solved if c != rec_id]

    # Only rows where the pairing question is live: the recommended climb misses them, and at
    # least one other config gets them. Rows nothing solves cannot distinguish any strategy.
    gettable = {n for c in arms for n in solved[c]}
    live = sorted((gettable - base) & set(names))

    rng = np.random.default_rng(SEED)
    comp_pick, comp_held = [], []
    solo_pick, solo_held = [], []
    rand_held = []
    winners = []

    for _ in range(N_SPLITS):
        idx = list(names)
        rng.shuffle(idx)
        A, B = set(idx[:len(idx) // 2]), set(idx[len(idx) // 2:])

        def marginal(cid, sub):
            """Rows in ``sub`` this config adds to the recommended climb's coverage."""
            return len((solved[cid] & sub) - base)

        # 1. the complement strategy: chosen for marginal gain
        best_c = max(arms, key=lambda c: marginal(c, A))
        comp_pick.append(marginal(best_c, A))
        comp_held.append(marginal(best_c, B))
        winners.append(best_c)

        # 2. same-family control: chosen for stand-alone strength, scored on marginal gain
        best_s = max(arms, key=lambda c: len(solved[c] & A))
        solo_pick.append(marginal(best_s, A))
        solo_held.append(marginal(best_s, B))

        # 3. random control
        rand_held.append(marginal(arms[int(rng.integers(len(arms)))], B))

    def m(v):
        return float(np.mean(v))

    premium = m(comp_pick) - m(comp_held)
    lines = [
        "# EXP-22 — is the complement strategy real, or hindsight?", "",
        "EXP-21 paired the recommended climb with a knot-free ordering and reached 23/24, having "
        "chosen that ordering *because* it solved the rows the climb misses. This measures the "
        "hindsight premium directly, inside EXP-19's existing matrix of "
        f"**{len(res)} configs × {len(names)} presentations at budget 1,000** — no new searches, "
        "no fresh slice spent.", "",
        f"Method: {N_SPLITS} random half-splits. On half A pick a second ordering; on half B "
        "measure how many rows it adds to the recommended climb's coverage. Three picking rules "
        "are compared, so the question is not 'does a second ordering help' but 'does picking it "
        "**for complementarity** beat picking it for raw strength'.", "",
        f"The recommended climb alone solves **{len(base)}/{len(names)}**; "
        f"**{len(live)}** rows are live (it misses them, something else gets them).", "",
        "| picking rule | marginal gain on the half it was chosen on | on the held-out half |",
        "|---|---|---|",
        f"| **complementarity** (adds most rows) | {m(comp_pick):.2f} | **{m(comp_held):.2f}** |",
        f"| stand-alone strength (solves most) | {m(solo_pick):.2f} | {m(solo_held):.2f} |",
        f"| random config | — | {m(rand_held):.2f} |", "",
        f"Hindsight premium of picking for complementarity: **{premium:.2f}** rows "
        f"({m(comp_pick):.2f} on the chosen half against {m(comp_held):.2f} held out).", "",
        f"{len(set(winners))} distinct configs won across the {N_SPLITS} splits.", "",
        "## Verdict", "",
    ]

    if m(comp_held) > m(solo_held) + 0.25:
        lines += [f"**The strategy is real.** Choosing a second ordering for *complementarity* "
                  f"adds **{m(comp_held):.2f}** rows out of sample, against **{m(solo_held):.2f}** "
                  "for choosing the strongest stand-alone arm — the thing a reasonable person "
                  "would do by default. The gap is the whole point of EXP-21's finding, and it "
                  "survives cross-validation.", "",
                  f"But the honest effect size is **{m(comp_held):.2f} rows**, not the 23/24 "
                  f"EXP-21 showed: that figure carried a {premium:.2f}-row hindsight premium. "
                  "Use the strategy; quote this number.", ""]
    elif m(comp_held) > m(rand_held) + 0.25:
        lines += [f"**Partly.** A complement-picked ordering adds {m(comp_held):.2f} rows out of "
                  f"sample, better than a random one ({m(rand_held):.2f}) but not clearly better "
                  f"than simply taking the strongest stand-alone arm ({m(solo_held):.2f}). A "
                  "second ordering is worth running; picking it specifically for complementarity "
                  "is not clearly worth the extra care.", ""]
    else:
        lines += [f"**Hindsight.** Out of sample, picking for complementarity adds "
                  f"{m(comp_held):.2f} rows against {m(rand_held):.2f} for a random config — no "
                  "real advantage. EXP-21's 23/24 was selection on the scored rows, and the "
                  "two-ordering advice should be withdrawn or restated as 'run a second ordering, "
                  "any reasonable one'.", ""]

    top = sorted(set(winners), key=winners.count, reverse=True)[:5]
    lines += ["## The configs that most often won the complement slot", "",
              "| config | times chosen | solves alone | adds to the climb (all rows) |",
              "|---|---|---|---|"]
    for c in top:
        lines.append(f"| `{c[:50]}` | {winners.count(c)}/{N_SPLITS} | {len(solved[c])}/{len(names)} "
                     f"| {len(solved[c] - base)} |")

    with open(os.path.join(LOGS, "EXP22_complement_cv.json"), "w") as f:
        json.dump({"n_configs": len(res), "n_rows": len(names), "base": len(base),
                   "live": len(live), "complement_held": m(comp_held),
                   "solo_held": m(solo_held), "random_held": m(rand_held),
                   "premium": premium, "distinct_winners": len(set(winners))}, f, indent=1)
    with open(os.path.join(LOGS, "EXP22_complement_cv.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
