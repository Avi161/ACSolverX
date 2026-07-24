"""EXP-10 -- round two: a finer joint search at budget 1,000, near the winners, honestly.

The first joint search (EXP-04) was at budget 500 over the whole feature space. This one zooms:
budget 1,000 (where the user runs), thresholds around the 16 that kept winning, and weights drawn
near the coefficients the earlier winners used, over the handful of features that carried signal
(knots, max-knots, smaller-block, generator-imbalance, the block extremes). The question is narrow
-- can a nearby config beat the 43/66 the finalists reached -- so the search is narrow too.

Two rules keep this from becoming a way to overfit:

1. **The test slice is already spent.** ``synthesize`` read ``aut_test`` once, for the finalists.
   Reading it again for new configs would turn it into a second selection surface, so this
   experiment never touches it. Everything happens on ``aut_train``.
2. **Selection optimism is measured on aut_train, not hoped away.** ``aut_train`` is split in half
   many times; the best config is chosen on one half and scored on the other. A config that only
   wins on the half it was picked on is fitting the 45 rows, and the gap says by how much.

So the deliverable is not a new headline -- it is either "a nearby config is robustly better,
worth the user validating at a larger budget on Colab" or "nothing near the winners beats them,
the recommendation stands". Both are results.

    python3 -m experiments.heuristic_search.exp10_refine
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.heuristic_search.hlab import (                    # noqa: E402
    BASELINE_CONFIG, LOGS, cfg_name, load_split,
)
from experiments.heuristic_search.lab import evaluate, rank, read, score  # noqa: E402
from experiments.heuristic_search.perbin import decidable          # noqa: E402

BUDGET = 1_000
MRL = 48
SLICE = "aut_train"
SEED = 71
N_RANDOM = 400
N_INNER = 40
OUT = os.path.join(LOGS, "EXP10_refine.jsonl")

# The features that carried signal, with the sign the winners used. Magnitudes are drawn near the
# winning coefficients rather than across three decades -- this is a local search, not a fresh one.
FEATS = {
    "K": (1.5, 10.0), "MK": (0.5, 8.0), "S": (2.0, 10.0), "xyimb": (-8.0, 4.0),
    "Bmax": (-4.0, 0.5), "Bmin": (-1.0, 0.5), "imbal": (0.0, 1.2), "Lmax": (0.0, 6.0),
}
THRESHOLDS = (12, 14, 16, 18, 20)


def configs(seed=SEED, n=N_RANDOM):
    rng = np.random.default_rng(seed)
    out, meta = [BASELINE_CONFIG], {}
    seen = {cfg_name(BASELINE_CONFIG)}
    names = list(FEATS)
    while len(out) < n:
        k = int(rng.integers(2, 5))                       # 2-4 climb features
        picks = list(rng.choice(names, size=k, replace=False))
        w = {"L": 1.0}
        for f in picks:
            lo, hi = FEATS[f]
            w[f] = float(np.round(rng.uniform(lo, hi), 3))
        T = int(rng.choice(THRESHOLDS))
        cfg = {"segments": [{"upto": T, "w": {"L": 1.0}}, {"upto": None, "w": w}]}
        cid = cfg_name(cfg)
        if cid in seen:
            continue
        seen.add(cid)
        out.append(cfg)
        meta[cid] = {"w": w, "T": T}
    return out, meta


def half_split_optimism(res, ctrl, names, rng, n_inner=N_INNER):
    arms = [c for c in res if c != ctrl]
    picked, scored, winners = [], [], []
    for _ in range(n_inner):
        idx = list(names)
        rng.shuffle(idx)
        a, b = set(idx[:len(idx) // 2]), set(idx[len(idx) // 2:])

        def sv(cid, sub):
            return sum(1 for nm in sub if res[cid].get(nm, {}).get("solved"))
        best = max(arms, key=lambda c: (sv(c, a), -sum(res[c].get(nm, {}).get("nodes", 0)
                                                        for nm in a)))
        picked.append(sv(best, a) - sv(ctrl, a))
        scored.append(sv(best, b) - sv(ctrl, b))
        winners.append(best)
    return {"gain_selection_half": float(np.mean(picked)),
            "gain_held_half": float(np.mean(scored)),
            "optimism": float(np.mean(picked) - np.mean(scored)),
            "distinct_winners": len(set(winners)),
            "modal_winner": max(set(winners), key=winners.count)}


def main():
    cfgs, meta = configs()
    evaluate(cfgs, SLICE, BUDGET, MRL, OUT, label="EXP10")

    res = read(OUT)
    ctrl = cfg_name(BASELINE_CONFIG)
    dec = set(decidable(res))
    rows = rank(res, ctrl)
    names = [r["name"] for r in load_split(SLICE)]

    rng = np.random.default_rng(SEED + 1)
    opt = half_split_optimism(res, ctrl, names, rng)

    def dsolved(cid):
        return sum(1 for nm in dec if res[cid].get(nm, {}).get("solved"))

    ranked = sorted((c for c in res if c != ctrl),
                    key=lambda c: (-dsolved(c), score(res[c], res[ctrl])["nodes_mean"] or 1e9))
    best = ranked[0]
    base_dec = dsolved(ctrl)

    # The prior best on this exact slice/budget, for the "did we beat it" line.
    #
    # Scored on THIS experiment's decidable set (``dec``), not on one recomputed from the prior
    # run's own configs. Those are different row sets -- the finalists' was 11 rows, this one is
    # 24 -- and scoring the prior on its set while printing the result against this denominator
    # makes any new config look like a breakthrough. That mistake reported "10/24 -> 20/24" here
    # when the true comparison is a dead tie.
    prior = None
    aut = read(os.path.join(LOGS, "AUT_final.jsonl"), by=("config_id", "budget"))
    tr = {r["name"] for r in load_split(SLICE)}
    prior_res = {c.rsplit(" | ", 1)[0]: {n: r for n, r in v.items() if n in tr}
                 for c, v in aut.items() if c.endswith("| 1000")}
    if prior_res:
        prior = max(((sum(1 for nm in dec if prior_res[c].get(nm, {}).get("solved")), c)
                     for c in prior_res if c != ctrl), default=(0, None))

    lines = [
        "# EXP-10 — round two: a finer search near the winners, at budget 1,000", "",
        f"Slice: `{SLICE}` (45), budget {BUDGET}, cap {MRL}, {len(cfgs)} configs drawn near the "
        "earlier winners. **The test slice is untouched** — it was already spent on the finalists, "
        "so this reports `aut_train` only.", "",
        "## Best-of-N optimism on aut_train", "",
        f"- gain on the half it was **chosen** on: **{opt['gain_selection_half']:+.2f}**",
        f"- gain on the half it was **not**: **{opt['gain_held_half']:+.2f}**",
        f"- optimism of a best-of-{len(cfgs)} pick: **{opt['optimism']:.2f}** presentations",
        f"- {opt['distinct_winners']} distinct half-split winners", "",
        "## Did anything beat the standing best?", "",
        f"- standing best on `aut_train` @1000 (from the finalists): "
        f"**{prior[0] if prior else '—'}/{len(dec)}** decidable",
        f"- round-two best: `{best}` — **{dsolved(best)}/{len(dec)}** decidable "
        f"(baseline {base_dec}/{len(dec)})", "",
    ]
    # A raw "beats it" is not enough: best-of-400 on 24 rows hits the ceiling by chance, which is
    # exactly what the optimism figure prices. Only an edge LARGER than that optimism is a signal
    # worth the user's Colab time.
    margin = dsolved(best) - prior[0] if prior else 0
    if prior and margin > opt["optimism"]:
        lines += [f"Round two beat the standing best by **{margin}** on `aut_train`, which exceeds "
                  f"the {opt['optimism']:.2f}-presentation optimism of a best-of-{len(cfgs)} pick. "
                  "It is a candidate for the user to validate at a larger budget on Colab — this "
                  "run cannot score it on the spent test slice.", ""]
    elif prior and margin > 0:
        lines += [f"Round two is **{margin}** ahead on `aut_train`, but a best-of-{len(cfgs)} pick "
                  f"buys **{opt['optimism']:.2f}** presentations of optimism for free, so that edge "
                  "is inside the noise. **The recommendation stands.**", ""]
    else:
        lines += ["Nothing near the winners beats them on `aut_train` — the finalists and the "
                  "round-two best reach the same count on the same rows. **The recommendation "
                  "stands**; the earlier winners are at the local ceiling for this family.", ""]

    lines += ["## Top 12 on aut_train (decidable)", "",
              "| config | decidable | net | p | mean nodes | mean path |", "|---|---|---|---|---|---|"]
    for r in rows[:12]:
        nm = f"{r['nodes_mean']:.0f}" if r["nodes_mean"] is not None else "—"
        pm = f"{r['path_mean']:.1f}" if r["path_mean"] is not None else "—"
        tag = " ← control" if r["config_id"] == ctrl else ""
        lines.append(f"| `{r['config_id'][:48]}`{tag} | {dsolved(r['config_id'])}/{len(dec)} | "
                     f"{r['net']:+d} | {r['sign_p']:.3f} | {nm} | {pm} |")

    with open(os.path.join(LOGS, "EXP10_refine.json"), "w") as f:
        json.dump({"best": best, "best_decidable": dsolved(best), "baseline_decidable": base_dec,
                   "decidable_n": len(dec), "optimism": opt,
                   "prior_best": prior[0] if prior else None}, f, indent=1)
    with open(os.path.join(LOGS, "EXP10_refine.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
