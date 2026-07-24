"""EXP-03 -- the dynamic part: should the ordering change as the presentation gets shorter?

A single weight vector has to serve two different jobs. While the presentation is long the search
is trying to cross the two-hump barrier, which means tolerating states that are *worse* by length
in exchange for better structure. Once it is short the remaining work is cancellation, and
structure stops mattering -- the trivial state has zero knots and length two, so near the end the
only thing worth optimising is length.

A **segment** switches the whole weight vector at a total-length threshold. The key carries the
segment index first, so every state in the short segment outranks every state in the long one; the
threshold is not a soft preference but a strict ordering of phases.

Two directions are swept, and the second is the reason this experiment is not just a threshold
scan. ``endgame`` is length-only below the threshold and structural above it -- the natural
reading. ``inverted`` is the opposite. If inverted did as well, the threshold would be doing
something other than what the story says (partitioning the queue rather than phasing the search),
and the interpretation would be wrong even though the number went up.

Feeds on EXP-02: the per-feature best weights are read from its jsonl rather than retyped, so the
two experiments cannot drift apart.

    python3 -m experiments.heuristic_search.exp03_segments
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.heuristic_search.hlab import (                    # noqa: E402
    BASELINE_CONFIG, LOGS, cfg_name,
)
from experiments.heuristic_search.lab import evaluate, rank, read  # noqa: E402
from experiments.heuristic_search.exp02_single import (            # noqa: E402
    OUT as EXP02_OUT, configs as exp02_configs,
)

BUDGET = 500
MRL = 48
SLICE = "train"
THRESHOLDS = (6, 8, 10, 12, 14, 16, 20, 24, 28)
N_FEATURES = 4          # how many of EXP-02's features to carry forward
OUT = os.path.join(LOGS, "EXP03_segments.jsonl")


def top_single_arms(n=N_FEATURES):
    """The best (feature, weight) per feature, from EXP-02, best features first.

    Read from the raw jsonl, not retyped from the report: a hand-copied weight that drifts from
    the experiment that chose it turns every downstream comparison into a comparison with
    something else.
    """
    _, meta = exp02_configs()
    res = read(EXP02_OUT)
    ctrl = cfg_name(BASELINE_CONFIG)
    if ctrl not in res:
        raise SystemExit("EXP-02 has not produced a control row yet -- run it first")
    rows = {r["config_id"]: r for r in rank(res, ctrl)}

    per = {}
    for cid, (feat, w) in meta.items():
        if cid not in rows:
            continue
        r = rows[cid]
        cur = per.get(feat)
        cand = (-r["solved"], r["nodes_mean"] if r["nodes_mean"] is not None else 1e9, feat, w)
        if cur is None or cand < cur[0]:
            per[feat] = (cand, feat, w, r["solved"])
    best = sorted(per.values(), key=lambda t: t[0])
    return [(f, w, s) for _, f, w, s in best[:n]]


def configs():
    arms = top_single_arms()
    out, meta = [BASELINE_CONFIG], {}
    for feat, w, _ in arms:
        struct = {"L": 1.0, feat: w}
        for T in THRESHOLDS:
            # endgame: length alone once short, structure while long -- the phased reading.
            c = {"segments": [{"upto": T, "w": {"L": 1.0}}, {"upto": None, "w": struct}]}
            out.append(c)
            meta[cfg_name(c)] = {"feature": feat, "weight": w, "T": T, "dir": "endgame"}
            # inverted: structure once short, length while long -- the control on the direction.
            c = {"segments": [{"upto": T, "w": struct}, {"upto": None, "w": {"L": 1.0}}]}
            out.append(c)
            meta[cfg_name(c)] = {"feature": feat, "weight": w, "T": T, "dir": "inverted"}
        # the un-segmented arm, so the threshold's contribution is separable from the feature's
        c = {"segments": [{"upto": None, "w": struct}]}
        out.append(c)
        meta[cfg_name(c)] = {"feature": feat, "weight": w, "T": None, "dir": "flat"}
    return out, meta, arms


def main():
    cfgs, meta, arms = configs()
    print(f"  carrying forward from EXP-02: "
          + ", ".join(f"{f} w={w:g} ({s}/40)" for f, w, s in arms), flush=True)
    evaluate(cfgs, SLICE, BUDGET, MRL, OUT, label="EXP03")

    res = read(OUT)
    ctrl = cfg_name(BASELINE_CONFIG)
    rows = rank(res, ctrl)
    base = next(r for r in rows if r["config_id"] == ctrl)
    by_id = {r["config_id"]: r for r in rows}

    lines = [f"# EXP-03 — length-keyed segments: does the ordering want to change phase?", "",
             f"Slice: `{SLICE}` (40). Budget {BUDGET}, cap {MRL}. Control = baseline, "
             f"**{base['solved']}/{base['n']}**.", "",
             "`endgame` = length-only below the threshold, structural above it. `inverted` = the "
             "same two vectors swapped. `flat` = no threshold at all. Inverted is the control on "
             "the *direction*: if it scored as well, the threshold would be partitioning the queue "
             "rather than phasing the search, and the phased reading would be wrong.", ""]

    for feat, w, _ in arms:
        lines += [f"## `L + {w:g}·{feat}`", "",
                  "| T | endgame | inverted |", "|---|---|---|"]
        flat = [c for c, m in meta.items() if m["feature"] == feat and m["dir"] == "flat"]
        fl = by_id.get(flat[0]) if flat else None
        for T in THRESHOLDS:
            cells = []
            for d in ("endgame", "inverted"):
                cid = next((c for c, m in meta.items()
                            if m["feature"] == feat and m["T"] == T and m["dir"] == d), None)
                r = by_id.get(cid)
                cells.append(f"{r['solved']}/{r['n']} ({r['net']:+d})" if r else "—")
            lines.append(f"| {T} | {cells[0]} | {cells[1]} |")
        if fl:
            lines.append(f"| _none (flat)_ | {fl['solved']}/{fl['n']} ({fl['net']:+d}) | — |")
        lines.append("")

    lines += ["## Top 15 overall", "",
              "| config | solved | net | p | mean nodes | mean path | Δmin |", "|---|---|---|---|---|---|---|"]
    for r in rows[:15]:
        nm = f"{r['nodes_mean']:.0f}" if r["nodes_mean"] is not None else "—"
        pm = f"{r['path_mean']:.1f}" if r["path_mean"] is not None else "—"
        tag = " ← control" if r["config_id"] == ctrl else ""
        lines.append(f"| `{r['config_id']}`{tag} | {r['solved']}/{r['n']} | {r['net']:+d} | "
                     f"{r['sign_p']:.3f} | {nm} | {pm} | {r['min_total_gain']:+.2f} |")

    with open(os.path.join(LOGS, "EXP03_segments.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines[:50]))


if __name__ == "__main__":
    main()
