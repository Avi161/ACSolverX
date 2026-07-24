"""EXP-14 -- do the four new features carry anything the first thirteen did not?

The second family was added because the original thirteen are all means, counts and differences,
and three shapes were missing: an extreme (the longest single block -- ``Bmax`` is the larger
*mean*, which averages a spike away), a dispersion (longest minus shortest), and two scale-free
forms (imbalance as a ratio rather than a difference, and blocks per letter).

Whether that reasoning is worth anything is a measurement. This is EXP-02's design re-run on the
new coordinates alone -- ``L + w*f`` for one feature at a time, both signs, three orders of
magnitude -- so the two screens are read on the same axis and a new feature can be compared
directly against ``K``'s 23/40.

Then the part that decides whether they are actually *new*: each new feature is also added on top
of the standing phased winner. A feature that scores well alone but adds nothing to the winner is
re-expressing something the winner already captures, which is the likely outcome for at least one
of these -- ``density`` is ``nb / L`` and ``nb`` is ``2K`` by the balance theorem, so it is close
to a knot count already divided by length.

    python3 -m experiments.heuristic_search.exp14_newfeats
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.heuristic_search.hlab import (                    # noqa: E402
    BASELINE_CONFIG, LOGS, cfg_name,
)
from experiments.heuristic_search.lab import evaluate, rank, read  # noqa: E402
from experiments.heuristic_search.perbin import decidable          # noqa: E402

BUDGET = 500
MRL = 48
SLICE = "train"
NEW = ("Bmaxrun", "Bspread", "ratio", "density")
WEIGHTS = (-1e6, -16, -8, -4, -2, -1, -0.5, -0.25, 0.25, 0.5, 1, 2, 4, 8, 16, 1e6)
OUT = os.path.join(LOGS, "EXP14_newfeats.jsonl")

# The standing phased winner, for the "does it ADD anything" half.
WINNER = [{"upto": 16, "w": {"L": 1.0}},
          {"upto": None, "w": {"L": 1.0, "K": 8.936, "xyimb": -5.978}}]
ADD_WEIGHTS = (-8, -4, -2, -1, 1, 2, 4, 8)


def configs():
    out, meta = [BASELINE_CONFIG], {}
    win = {"segments": [dict(s, w=dict(s["w"])) for s in WINNER]}
    out.append(win)
    meta[cfg_name(win)] = {"kind": "winner", "feature": None, "weight": None}

    for f in NEW:
        for w in WEIGHTS:                       # alone, exactly EXP-02's shape
            c = {"segments": [{"upto": None, "w": {"L": 1.0, f: w}}]}
            cid = cfg_name(c)
            if cid not in meta:
                out.append(c)
                meta[cid] = {"kind": "alone", "feature": f, "weight": w}
        for w in ADD_WEIGHTS:                   # on top of the standing winner
            segs = [dict(s, w=dict(s["w"])) for s in WINNER]
            segs[-1]["w"][f] = w
            c = {"segments": segs}
            cid = cfg_name(c)
            if cid not in meta:
                out.append(c)
                meta[cid] = {"kind": "added", "feature": f, "weight": w}
    return out, meta


def main():
    cfgs, meta = configs()
    evaluate(cfgs, SLICE, BUDGET, MRL, OUT, label="EXP14")

    res = read(OUT)
    ctrl = cfg_name(BASELINE_CONFIG)
    win_id = cfg_name({"segments": [dict(s, w=dict(s["w"])) for s in WINNER]})
    dec = set(decidable(res))
    rows = {r["config_id"]: r for r in rank(res, ctrl)}

    def ds(cid):
        return sum(1 for nm in dec if res.get(cid, {}).get(nm, {}).get("solved"))

    base, win = ds(ctrl), ds(win_id)
    lines = [f"# EXP-14 — the second feature family, screened like the first", "",
             f"Slice `{SLICE}` (40), budget {BUDGET}, cap {MRL}. Decidable subset "
             f"**{len(dec)}** rows: baseline **{base}**, standing phased winner **{win}**.", "",
             "`alone` repeats EXP-02's design (`L + w·f`, both signs) so a new coordinate can be "
             "read against `K`'s result on the same axis. `added` puts the feature on top of the "
             "standing winner — a feature that scores well alone but adds nothing there is "
             "re-expressing something already captured, not a new coordinate.", "",
             "| feature | best alone | best added to winner | verdict |", "|---|---|---|---|"]

    for f in NEW:
        al = [(ds(c), meta[c]["weight"]) for c in meta if meta[c]["kind"] == "alone"
              and meta[c]["feature"] == f and c in res]
        ad = [(ds(c), meta[c]["weight"]) for c in meta if meta[c]["kind"] == "added"
              and meta[c]["feature"] == f and c in res]
        if not al:
            continue
        ba, wa = max(al)
        bd, wd = max(ad) if ad else (0, None)
        if bd > win:
            v = f"**adds {bd - win}** to the winner"
        elif ba > base:
            v = "beats the baseline alone, but adds nothing to the winner"
        else:
            v = "no signal"
        lines.append(f"| `{f}` | {ba}/{len(dec)} (w={wa:g}) | {bd}/{len(dec)} (w={wd:g}) | {v} |"
                     if wd is not None else
                     f"| `{f}` | {ba}/{len(dec)} (w={wa:g}) | — | {v} |")

    best_add = max(((ds(c), c) for c in meta if meta[c]["kind"] == "added" and c in res),
                   default=(0, None))
    lines += ["", "## Verdict", ""]
    if best_add[0] > win:
        lines += [f"The second family **does** add: `{best_add[1]}` reaches "
                  f"**{best_add[0]}/{len(dec)}** against the standing winner's {win}. Worth "
                  "carrying into the joint search.", ""]
    else:
        lines += [f"**Nothing in the second family improves on the standing winner** "
                  f"({win}/{len(dec)}). The four new shapes are either redundant with the block and "
                  "knot features already present or simply uninformative — the first thirteen "
                  "already span what this state representation offers for this search.", ""]

    lines += ["", "## Every arm, best-first", "",
              "| config | kind | feature | decidable | net | p |", "|---|---|---|---|---|---|"]
    for cid, r in sorted(rows.items(), key=lambda kv: -ds(kv[0]))[:20]:
        m = meta.get(cid, {"kind": "control", "feature": None})
        tag = " ← ctrl" if cid == ctrl else (" ← winner" if cid == win_id else "")
        lines.append(f"| `{cid[:44]}`{tag} | {m['kind']} | {m['feature'] or '—'} | "
                     f"{ds(cid)}/{len(dec)} | {r['net']:+d} | {r['sign_p']:.3f} |")

    with open(os.path.join(LOGS, "EXP14_newfeats.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines[:40]))


if __name__ == "__main__":
    main()
