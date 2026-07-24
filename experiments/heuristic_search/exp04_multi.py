"""EXP-04 -- many features at once, with the selection bias measured instead of hoped away.

Single-feature screening finds which coordinates matter; it cannot find that two of them are only
useful together, or that the best weight for one shifts once another is present. So this searches
the joint space. The danger is equally specific: with a dozen free weights and forty presentations,
picking the best of a thousand random configs will produce a number that does not survive contact
with new presentations, and it will look like a result.

Three defences, in order of how much they cost to skip:

1. **The baseline is in the candidate pool.** A search space that cannot express "change nothing"
   will always appear to beat it.
2. **The selection bias is measured, not assumed.** After the sweep, the training slice is
   repeatedly split in half: the best config is chosen on one half and scored on the other, several
   times. The gap between those two numbers is what best-of-N selection buys you for free, and it
   is reported next to the headline rather than left for the reader to guess at. This uses only
   ``train`` -- the real test slice stays untouched.
3. **A robustness pick alongside the greedy pick.** The config with the best *worst-half* score is
   reported beside the config with the best overall score. When they differ, the greedy pick was
   fitting the slice.

    python3 -m experiments.heuristic_search.exp04_multi
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.heuristic_search.hlab import (                    # noqa: E402
    BASELINE_CONFIG, LOGS, cfg_name, load_split,
)
from experiments.heuristic_search.lab import evaluate, rank, read  # noqa: E402

BUDGET = 500
MRL = 48
SLICE = "train"
SEED = 41
N_RANDOM = 700
N_INNER = 40            # inner half-splits used to size the selection bias
OUT = os.path.join(LOGS, "EXP04_multi.jsonl")

# The pool the random search draws from. ``nb`` is deliberately excluded: it equals 2K plus the
# number of pure-power relators (0 violations in 4,089 reachable states, r = +0.9997 with K), a
# consequence of the balance theorem -- #x-blocks == #y-blocks for a cyclically reduced word in
# two generators with both present. Including it would spend the sweep on a duplicate coordinate
# and make any "two features agree" reading circular.
POOL = ("K", "MK", "mK", "S", "Bmax", "B1", "Bmin", "Lmin", "Lmax", "imbal", "xyimb")
THRESHOLDS = (0, 6, 8, 10, 12, 14, 16, 20)


def configs(seed=SEED, n=N_RANDOM):
    rng = np.random.default_rng(seed)
    out, meta = [BASELINE_CONFIG], {}
    seen = {cfg_name(BASELINE_CONFIG)}
    while len(out) < n:
        k = int(rng.integers(1, 5))                       # 1-4 features besides length
        feats = list(rng.choice(POOL, size=k, replace=False))
        w = {"L": 1.0}
        for f in feats:
            # Log-uniform magnitude with a random sign: the useful weights in EXP-02 spanned three
            # orders of magnitude, so a uniform draw would put almost all its mass on the large end.
            mag = float(10 ** rng.uniform(-1.0, 1.2))
            w[f] = float(np.round(mag * (1 if rng.random() < 0.75 else -1), 3))
        T = int(rng.choice(THRESHOLDS))
        cfg = ({"segments": [{"upto": None, "w": w}]} if T == 0 else
               {"segments": [{"upto": T, "w": {"L": 1.0}}, {"upto": None, "w": w}]})
        cid = cfg_name(cfg)
        if cid in seen:
            continue
        seen.add(cid)
        out.append(cfg)
        meta[cid] = {"w": w, "T": T or None}
    return out, meta


def half_split_bias(res, ctrl_id, names, rng, n_inner=N_INNER):
    """How much of the winner's margin is selection, measured on ``train`` alone.

    Choose the best config on one random half, score it on the other, repeat. The mean of the
    scored halves against the mean of the chosen halves is the optimism that best-of-N buys.
    """
    picked_on, scored_on, picks = [], [], []
    arms = [c for c in res if c != ctrl_id]
    for _ in range(n_inner):
        idx = list(names)
        rng.shuffle(idx)
        a, b = set(idx[:len(idx) // 2]), set(idx[len(idx) // 2:])

        def solved(cid, sub):
            return sum(1 for nm in sub if nm in res[cid] and res[cid][nm]["solved"])

        best = max(arms, key=lambda c: (solved(c, a), -sum(
            res[c][nm]["nodes"] for nm in a if nm in res[c])))
        picked_on.append(solved(best, a) - solved(ctrl_id, a))
        scored_on.append(solved(best, b) - solved(ctrl_id, b))
        picks.append(best)
    return {
        "gain_on_selection_half": float(np.mean(picked_on)),
        "gain_on_held_half": float(np.mean(scored_on)),
        "optimism": float(np.mean(picked_on) - np.mean(scored_on)),
        "distinct_winners": len(set(picks)),
        "modal_winner": max(set(picks), key=picks.count),
        "modal_winner_frequency": picks.count(max(set(picks), key=picks.count)) / len(picks),
    }


def main():
    cfgs, meta = configs()
    evaluate(cfgs, SLICE, BUDGET, MRL, OUT, label="EXP04")

    res = read(OUT)
    ctrl = cfg_name(BASELINE_CONFIG)
    rows = rank(res, ctrl)
    base = next(r for r in rows if r["config_id"] == ctrl)
    names = [r["name"] for r in load_split(SLICE)]

    rng = np.random.default_rng(SEED + 1)
    bias = half_split_bias(res, ctrl, names, rng)

    # The robustness pick: best worst-half, over the same inner splits.
    worst = {}
    for _ in range(N_INNER):
        idx = list(names)
        rng.shuffle(idx)
        halves = (set(idx[:len(idx) // 2]), set(idx[len(idx) // 2:]))
        for cid in res:
            s = min(sum(1 for nm in h if nm in res[cid] and res[cid][nm]["solved"])
                    for h in halves)
            worst[cid] = min(worst.get(cid, 99), s)
    robust = max(worst, key=lambda c: (worst[c], -(next(
        r["nodes_mean"] for r in rows if r["config_id"] == c) or 1e9)))

    lines = [f"# EXP-04 — joint weight search, with the selection bias measured", "",
             f"Slice: `{SLICE}` (40). Budget {BUDGET}, cap {MRL}, {len(cfgs)} configs "
             f"(random weights over {len(POOL)} features + a length-keyed threshold). "
             f"Control = baseline, **{base['solved']}/{base['n']}**.", "",
             "## What best-of-N selection is worth on its own", "",
             f"Choosing the best config on a random half of `train` and scoring it on the other "
             f"half, {N_INNER} times:", "",
             f"- gain on the half it was **chosen** on: **{bias['gain_on_selection_half']:+.2f}** "
             f"presentations",
             f"- gain on the half it was **not** chosen on: **{bias['gain_on_held_half']:+.2f}**",
             f"- so the optimism of a best-of-{len(cfgs)} pick is "
             f"**{bias['optimism']:.2f}** presentations",
             f"- {bias['distinct_winners']} distinct configs won across the {N_INNER} splits; the "
             f"most frequent won {bias['modal_winner_frequency']:.0%} of them", "",
             "Any headline below smaller than that optimism figure is selection, not signal.", "",
             "## Top 20 by training solves", "",
             "| config | solved | net | p | mean nodes | mean path | Δmin |",
             "|---|---|---|---|---|---|---|"]
    for r in rows[:20]:
        nm = f"{r['nodes_mean']:.0f}" if r["nodes_mean"] is not None else "—"
        pm = f"{r['path_mean']:.1f}" if r["path_mean"] is not None else "—"
        tag = " ← control" if r["config_id"] == ctrl else ""
        lines.append(f"| `{r['config_id'][:60]}`{tag} | {r['solved']}/{r['n']} | {r['net']:+d} | "
                     f"{r['sign_p']:.3f} | {nm} | {pm} | {r['min_total_gain']:+.2f} |")

    rr = next(r for r in rows if r["config_id"] == robust)
    lines += ["", "## The robustness pick", "",
              f"Best *worst-half* score over the inner splits: `{robust}` — "
              f"{rr['solved']}/{rr['n']} overall, net {rr['net']:+d}. "
              + ("Same as the greedy pick." if robust == rows[0]["config_id"] else
                 f"**Different** from the greedy pick (`{rows[0]['config_id'][:60]}`), which is "
                 "what fitting the slice looks like."), ""]

    with open(os.path.join(LOGS, "EXP04_multi.json"), "w") as f:
        json.dump({"bias": bias, "robust": robust, "top": rows[:30], "meta": meta}, f, indent=1)
    with open(os.path.join(LOGS, "EXP04_multi.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines[:45]))


if __name__ == "__main__":
    main()
