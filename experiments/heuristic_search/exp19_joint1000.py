"""EXP-19 -- the joint search, redone where it matters: budget 1,000, all 17 features.

EXP-04 searched the joint weight space at budget 500 over 13 features, with a length threshold on
every candidate. Three things have changed since, and each one moves the space this should be
searching in:

- **The budget that matters is 1,000, not 500.** EXP-06 and EXP-16 both showed the ranking moves
  with budget -- the lean winner plateaus while the richer climb keeps converting -- so a space
  searched at 500 is being searched in the wrong place.
- **There are 17 features now**, not 13. The second family (longest block, block spread, length
  ratio, block density) has never been in a joint search; EXP-14 only screened it one feature at a
  time and against a winner that had no headroom left.
- **The threshold is optional**, not mandatory (EXP-18). Roughly half the candidates here are
  threshold-free single-vector configs, which is the shape the current recommendation takes.

Selection happens on ``aut_train`` and the optimism of a best-of-N pick is measured on it by
repeated half-splits, exactly as EXP-04 did. The held-out ``aut_test`` slice is **not** read: it
was spent on the finalists, and re-reading it for new candidates would turn it into a second
selection surface. So the deliverable is either "a better config, worth validating on Colab" or
"nothing beats the incumbent", and the second is as useful as the first.

    python3 -m experiments.heuristic_search.exp19_joint1000
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
SEED = 1907
N_RANDOM = 320
N_INNER = 40
OUT = os.path.join(LOGS, "EXP19_joint1000.jsonl")

# ``nb`` stays out: it is 2K plus the pure-power count (balance theorem), so it would spend the
# sweep on a duplicate coordinate. ``density`` is nb/L and so is *close* to a rescaled knot count,
# but not identical, and it has never been in a joint search -- so it is in, and if it shows up in
# a winner that is a result to be suspicious of rather than to celebrate.
POOL = ("K", "MK", "mK", "S", "Bmax", "B1", "Bmin", "Lmin", "Lmax", "imbal", "xyimb",
        "Bmaxrun", "Bspread", "ratio", "density")
THRESHOLDS = (0, 0, 0, 12, 16, 20)      # 0 = no threshold; weighted to half the draws

INCUMBENTS = {
    "richer (recommended)": {"segments": [
        {"upto": None, "w": {"L": 1.0, "K": 2.53, "MK": 6.418, "S": 8.458, "xyimb": 3.292}}]},
    "richer phased": {"segments": [
        {"upto": 16, "w": {"L": 1.0}},
        {"upto": None, "w": {"L": 1.0, "K": 2.53, "MK": 6.418, "S": 8.458, "xyimb": 3.292}}]},
    "blocks": {"segments": [{"upto": None, "w": {"L": 1.0, "Bmax": -2.185, "S": 5.668}}]},
}


def configs(seed=SEED, n=N_RANDOM):
    rng = np.random.default_rng(seed)
    out, meta = [BASELINE_CONFIG], {}
    seen = {cfg_name(BASELINE_CONFIG)}
    for label, cfg in INCUMBENTS.items():
        cid = cfg_name(cfg)
        if cid not in seen:
            seen.add(cid)
            out.append(cfg)
            meta[cid] = {"kind": "incumbent", "label": label}
    while len(out) < n:
        k = int(rng.integers(2, 6))                    # 2-5 climb features
        feats = list(rng.choice(POOL, size=k, replace=False))
        w = {"L": 1.0}
        for f in feats:
            mag = float(10 ** rng.uniform(-0.7, 1.1))  # ~0.2 to ~12
            w[f] = float(np.round(mag * (1 if rng.random() < 0.75 else -1), 3))
        T = int(rng.choice(THRESHOLDS))
        cfg = ({"segments": [{"upto": None, "w": w}]} if T == 0 else
               {"segments": [{"upto": T, "w": {"L": 1.0}}, {"upto": None, "w": w}]})
        cid = cfg_name(cfg)
        if cid in seen:
            continue
        seen.add(cid)
        out.append(cfg)
        meta[cid] = {"kind": "random", "w": w, "T": T or None}
    return out, meta


def half_split_optimism(res, ctrl, names, rng, n_inner=N_INNER):
    arms = [c for c in res if c != ctrl]
    picked, held, winners = [], [], []
    for _ in range(n_inner):
        idx = list(names)
        rng.shuffle(idx)
        a, b = set(idx[:len(idx) // 2]), set(idx[len(idx) // 2:])

        def sv(cid, sub):
            return sum(1 for nm in sub if res[cid].get(nm, {}).get("solved"))
        best = max(arms, key=lambda c: (sv(c, a), -sum(res[c].get(nm, {}).get("nodes", 0)
                                                        for nm in a)))
        picked.append(sv(best, a) - sv(ctrl, a))
        held.append(sv(best, b) - sv(ctrl, b))
        winners.append(best)
    return {"gain_selection_half": float(np.mean(picked)),
            "gain_held_half": float(np.mean(held)),
            "optimism": float(np.mean(picked) - np.mean(held)),
            "distinct_winners": len(set(winners))}


def main():
    cfgs, meta = configs()
    evaluate(cfgs, SLICE, BUDGET, MRL, OUT, label="EXP19")

    res = read(OUT)
    ctrl = cfg_name(BASELINE_CONFIG)
    dec = set(decidable(res))
    names = [r["name"] for r in load_split(SLICE)]
    rng = np.random.default_rng(SEED + 1)
    opt = half_split_optimism(res, ctrl, names, rng)

    def ds(cid):
        return sum(1 for nm in dec if res.get(cid, {}).get(nm, {}).get("solved"))

    inc = {label: ds(cfg_name(cfg)) for label, cfg in INCUMBENTS.items()
           if cfg_name(cfg) in res}
    best_inc = max(inc.values()) if inc else 0
    ranked = sorted((c for c in res if c != ctrl),
                    key=lambda c: (-ds(c), score(res[c], res[ctrl])["nodes_mean"] or 1e9))
    best = ranked[0]
    margin = ds(best) - best_inc

    lines = [f"# EXP-19 — the joint search at budget {BUDGET}, over all 17 features", "",
             f"Slice `{SLICE}` ({len(names)}), budget {BUDGET}, cap {MRL}, {len(cfgs)} configs. "
             "Half the random draws are **threshold-free** single weight vectors, which is the "
             "shape the current recommendation takes (EXP-18). The held-out slice is not read — "
             "it was spent on the finalists.", "",
             f"Decidable subset **{len(dec)}** rows. Baseline **{ds(ctrl)}**.", "",
             "## The incumbents", "",
             "| ordering | decidable |", "|---|---|"]
    for label, v in sorted(inc.items(), key=lambda kv: -kv[1]):
        lines.append(f"| {label} | {v}/{len(dec)} |")

    lines += ["", "## Best-of-N optimism, measured on aut_train", "",
              f"- gain on the half it was **chosen** on: **{opt['gain_selection_half']:+.2f}**",
              f"- gain on the half it was **not**: **{opt['gain_held_half']:+.2f}**",
              f"- optimism of a best-of-{len(cfgs)} pick: **{opt['optimism']:.2f}** presentations",
              f"- {opt['distinct_winners']} distinct half-split winners", "",
              "## Did the search find anything better?", "",
              f"- best incumbent: **{best_inc}/{len(dec)}**",
              f"- best of {len(cfgs)}: `{best}` — **{ds(best)}/{len(dec)}** "
              f"(**{margin:+d}**)", ""]

    if margin > opt["optimism"]:
        lines += [f"The margin ({margin:+d}) exceeds the measured optimism "
                  f"({opt['optimism']:.2f}), so this is a genuine candidate — worth validating at "
                  "a larger budget on Colab, which this program cannot do.", ""]
    elif margin > 0:
        lines += [f"The margin ({margin:+d}) is **inside** the {opt['optimism']:.2f}-presentation "
                  f"optimism a best-of-{len(cfgs)} pick buys for free, so it is not evidence of a "
                  "better ordering. **The recommendation stands.**", ""]
    else:
        lines += ["**Nothing in the enlarged space beats the incumbent.** Searching 17 features at "
                  "the budget that matters, with the threshold free to vanish, does not improve on "
                  "the ordering already recommended — which is the strongest statement this "
                  "program can make that the recommendation is at its local ceiling.", ""]

    # Do the new features appear in the top arms at all?
    from experiments.heuristic_search.hlab import FEATURES
    new = set(FEATURES[13:])
    top = ranked[:15]
    appear = {f: sum(1 for c in top if meta.get(c, {}).get("w", {}).get(f)) for f in sorted(new)}
    lines += ["## Do the second-family features show up in the top arms?", "",
              "| feature | appearances in the top 15 |", "|---|---|"]
    for f, c in appear.items():
        lines.append(f"| `{f}` | {c} |")
    lines += ["", "## Top 15", "",
              "| config | decidable | net | p | mean nodes |", "|---|---|---|---|---|"]
    rows = {r["config_id"]: r for r in rank(res, ctrl)}
    for c in top:
        r = rows[c]
        nm = f"{r['nodes_mean']:.0f}" if r["nodes_mean"] is not None else "—"
        tag = " ← incumbent" if meta.get(c, {}).get("kind") == "incumbent" else ""
        lines.append(f"| `{c[:52]}`{tag} | {ds(c)}/{len(dec)} | {r['net']:+d} | "
                     f"{r['sign_p']:.3f} | {nm} |")

    with open(os.path.join(LOGS, "EXP19_joint1000.json"), "w") as f:
        json.dump({"best": best, "best_decidable": ds(best), "incumbents": inc,
                   "optimism": opt, "margin": margin, "decidable_n": len(dec)}, f, indent=1)
    with open(os.path.join(LOGS, "EXP19_joint1000.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines[:50]))


if __name__ == "__main__":
    main()
