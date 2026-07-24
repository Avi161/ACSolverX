"""EXP-02 -- one feature at a time: which of the twelve carries any signal at all, and at what sign?

Before searching a thirteen-dimensional weight space it is worth knowing which coordinates do
anything, because a random sweep over dead coordinates spends its budget proving they are dead.
So every config here is ``L + w*f`` for a single feature ``f`` -- the baseline ordering with one
term added -- swept over weights spanning three orders of magnitude in **both signs**, plus the
lexicographic limit in both directions.

Both signs is the part that is easy to skip and expensive to skip. The clustering work found that
unsolved presentations have *more* knots, which makes "minimise knots" the obvious reading; but a
search is not a classifier, and the ordering that finds a solution may well be the one that
tolerates a temporarily worse state in order to cross the two-hump barrier. The sign is a
measurement, not a deduction.

The lexicographic arms (``w = +/-1e6``) are the "keep knots at the top of the queue" idea at full
strength: the feature dominates and length only breaks ties. The pilot already suggests that is
too aggressive -- pure knots-first solved 15/40 against the control's 17/40 -- but it is swept
here for every feature so that the *shape* of each feature's weight response is visible rather
than assumed.

    python3 -m experiments.heuristic_search.exp02_single
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.heuristic_search.hlab import (                    # noqa: E402
    BASELINE_CONFIG, FEATURES, LOGS, cfg_name,
)
from experiments.heuristic_search.lab import evaluate, rank, read  # noqa: E402

BUDGET = 500
MRL = 48            # expansion allowed; EXP-01 showed the cap is inert for the control at 24-64
SLICE = "train"
WEIGHTS = (-1e6, -16, -8, -4, -2, -1, -0.5, -0.25, 0.25, 0.5, 1, 2, 4, 8, 16, 1e6)
OUT = os.path.join(LOGS, "EXP02_single.jsonl")


def configs():
    """Returns (configs, {config_id: (feature, weight)}).

    The map is carried explicitly rather than parsed back out of the config id. Recovering a
    feature name from a rendered id is unsound the moment two feature names nest -- ``K`` is a
    substring of ``MK`` and ``mK``, ``Bmin`` of nothing but ``B1`` looks like a prefix -- so a
    string match would silently file several features' rows under one heading.
    """
    out, meta = [BASELINE_CONFIG], {}
    for f in FEATURES:
        if f == "L":
            continue
        for w in WEIGHTS:
            # At the lexicographic limit the feature IS the order and L only breaks ties; a finite
            # weight blends the two. Both are expressed the same way, which is the point of the
            # linear form -- there is no separate "lexicographic" code path to get wrong.
            cfg = {"segments": [{"upto": None, "w": {"L": 1.0, f: w}}]}
            out.append(cfg)
            meta[cfg_name(cfg)] = (f, w)
    return out, meta


def main():
    cfgs, meta = configs()
    evaluate(cfgs, SLICE, BUDGET, MRL, OUT, label="EXP02")

    res = read(OUT)
    ctrl = cfg_name(BASELINE_CONFIG)
    rows = rank(res, ctrl)
    base = next(r for r in rows if r["config_id"] == ctrl)

    # Per-feature best, so the report reads as "which features matter", not "which 180 configs ran".
    per = {}
    for r in rows:
        if r["config_id"] == ctrl or r["config_id"] not in meta:
            continue
        per.setdefault(meta[r["config_id"]][0], []).append(r)

    lines = [f"# EXP-02 — single-feature screen (`L + w·f`), budget {BUDGET}, cap {MRL}", "",
             f"Slice: `{SLICE}` (40 presentations). Control = the baseline ordering, "
             f"**{base['solved']}/{base['n']}** solved. `net` counts presentations won minus lost "
             "against the control; `p` is a two-sided exact sign test on those discordant pairs. "
             "`Δmin` is the mean improvement in shortest total length reached, over the "
             "presentations this arm did **not** solve — progress where there is no solve.", "",
             "## Best weight per feature", "",
             "| feature | best weight | solved | net | p | mean nodes | mean path | Δmin |",
             "|---|---|---|---|---|---|---|---|"]
    best_per = []
    for feat in sorted(per, key=lambda k: -max(r["solved"] for r in per[k])):
        rs = sorted(per[feat], key=lambda r: (-r["solved"], r["nodes_mean"] or 1e9))
        b = rs[0]
        best_per.append((feat, b))
        w = f"{meta[b['config_id']][1]:g}"
        nm = f"{b['nodes_mean']:.0f}" if b["nodes_mean"] is not None else "—"
        pm = f"{b['path_mean']:.1f}" if b["path_mean"] is not None else "—"
        lines.append(f"| `{feat}` | `{w}` | {b['solved']}/{b['n']} | {b['net']:+d} | "
                     f"{b['sign_p']:.3f} | {nm} | {pm} | {b['min_total_gain']:+.2f} |")

    lines += ["", "## Top 20 configs overall", "",
              "| config | solved | net | p | mean nodes | mean path | Δmin | max relator popped |",
              "|---|---|---|---|---|---|---|---|"]
    raw = read(OUT)
    for r in rows[:20]:
        mp = max(x["max_pop"] for x in raw[r["config_id"]].values())
        nm = f"{r['nodes_mean']:.0f}" if r["nodes_mean"] is not None else "—"
        pmm = f"{r['path_mean']:.1f}" if r["path_mean"] is not None else "—"
        tag = " ← control" if r["config_id"] == ctrl else ""
        lines.append(f"| `{r['config_id']}`{tag} | {r['solved']}/{r['n']} | {r['net']:+d} | "
                     f"{r['sign_p']:.3f} | {nm} | {pmm} | {r['min_total_gain']:+.2f} | {mp} |")

    caps = [max(x["max_pop"] for x in raw[c].values()) for c in raw]
    lines += ["", f"Longest single relator popped by **any** of the {len(raw)} configs: "
                  f"**{max(caps)}** (cap was {MRL}). Configs that ever popped a relator longer "
                  f"than 24: {sum(1 for c in caps if c > 24)}/{len(caps)}.", ""]

    with open(os.path.join(LOGS, "EXP02_single.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines[:60]))


if __name__ == "__main__":
    main()
