"""The generator channel on subset-60: ignore inverses entirely, x/X -> +1, y/Y -> -1.

**The argument.** `r -> r^-1` is a symmetry of the AC problem, so whether a letter is inverted
carries no invariant information, while which generator it is does. A spectral feature ought to
read the generator ring and nothing else. That also kills the relabel wart for free: a channel
that never reads the exponent cannot be moved by an exponent relabel.

**Why this is not already settled.** The generator channel was set aside earlier as redundant with
the heap's existing features, via two Parseval identities:

    A_gen[1] = L - 4K            (k=1 content is the knot count)
    P_gen[0] = (L * xyimb)^2     (DC content is generator imbalance)

Those pin the **DC and k=1** terms only. The peak, the flatness, the centroid and the high band
are untouched by them, so most of this channel's spectrum was never actually screened. This run
screens all of it, and reports the redundancy against `{L, K, xyimb}` alone so the identities can
be checked rather than cited.

**Pool.** subset-60 (`benchmark/subsets/benchmark_subset_60.json`), MRL **24**, budget 1,000 —
a different pool and a different cap from the ac1m work, so the control gate is re-run here:
`wF = 0` must reproduce `greedy_search` pop for pop, and the `length` arm must land on the
documented 29/60.

**Selection caveat.** subset-60 is the benchmark; there is no holdout behind it. The full weight
curve is reported rather than only its maximum, because picking the best weight on the same 60
presentations that score it is selection, and a single best-of-grid number hides that.

    PYTHONPATH=. .venv/bin/python3 -m experiments.heuristic_search.runners.scout_genchannel_bench60
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone

import numpy as np

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

from experiments.heuristic_search.core.search_fftvar import search_fftvar  # noqa: E402
from experiments.heuristic_search.core.fftvar_feats import fvar_pair_words  # noqa: E402
from experiments.heuristic_search.core.hlab import FEATURES, phi  # noqa: E402
from experiments.search.greedy_baseline import greedy_search  # noqa: E402

ROOT = _d
SUBSET = os.path.join(ROOT, "benchmark", "subsets", "benchmark_subset_60.json")
OUT_DIR = os.path.join(ROOT, "results", "heuristic_search", "genchannel_bench60")
JSONL = os.path.join(OUT_DIR, "runs.jsonl")
RESULTS = os.path.join(OUT_DIR, "RESULTS.md")

BUDGET = 1000
MRL = 24                    # subset-60's cap -- NOT the 48 used by the ac1m work
BASELINE_SOLVED = 29        # documented `length` score on subset-60 at budget 1,000

#: generator channel -- the thing being tested
GEN = ("genlo", "genhi", "genpeak", "gencent", "genflat", "genlag345")
#: the incumbents, same weights, for a like-for-like three-channel read
OTHER = ("lag345", "cplxlo", "dftlo")
#: The first pass ran (2, 4, 8, 16) and every arm peaked at **2**, the smallest cell — a maximum
#: on the boundary of a grid is not a maximum, it is a grid that stopped too early. Extended
#: downward; the jsonl is keyed (arm, pres_id) so the original cells resume rather than re-run.
WF_GRID = (0.5, 1.0, 2.0, 4.0, 8.0, 16.0)


def _cfg_L():
    return {"segments": [{"upto": None, "w": {"L": 1.0}}]}


def _arms():
    out = [("length", "lag345", 0.0)]
    for v in GEN + OTHER:
        for w in WF_GRID:
            out.append((f"{v}_w{w:g}", v, w))
    return out


def control_gate(sub):
    """`wF = 0` must BE the baseline search, and land on the documented 29/60.

    Re-run here rather than inherited: this pool and cap (MRL 24) are not the ones the ac1m
    scouts gated on, and a cap mismatch would not raise -- it would just quietly change every
    number below.
    """
    solved = 0
    for r in sub:
        a = greedy_search(r["r1"], r["r2"], BUDGET, max_relator_length=MRL)
        b = search_fftvar(r["r1"], r["r2"], BUDGET, _cfg_L(), MRL, wF=0.0)
        if bool(a["solved"]) != bool(b["solved"]) or \
                a["nodes_explored"] != b["nodes_explored"]:
            raise RuntimeError(
                f"control diverges on pres {r['pres_id']}: baseline "
                f"{a['solved']}/{a['nodes_explored']} vs wF=0 "
                f"{b['solved']}/{b['nodes_explored']}")
        solved += bool(b["solved"])
    if solved != BASELINE_SOLVED:
        raise RuntimeError(f"length scored {solved}/60, expected {BASELINE_SOLVED}/60")
    return solved


def redundancy(sub):
    """R^2 of each variant against (a) the full 17 heap features and (b) just {L, K, xyimb}.

    Column (b) is the direct test of the Parseval argument: if `A_gen[1] = L - 4K` and
    `P_gen[0] = (L*xyimb)^2` really account for a variant, three columns should already explain
    it. A variant that (b) cannot explain was never covered by that argument.
    """
    X = np.asarray([list(phi(r["r1"], r["r2"])) for r in sub], dtype=float)
    idx = [FEATURES.index(f) for f in ("L", "K", "xyimb")]
    X_small = X[:, idx]

    def r2(y, M):
        M1 = np.concatenate([M, np.ones((len(M), 1))], axis=1)
        ss_tot = float(np.sum((y - y.mean()) ** 2))
        if ss_tot <= 0:
            return 1.0
        coef, _, _, _ = np.linalg.lstsq(M1, y, rcond=None)
        return 1.0 - float(np.sum((y - M1 @ coef) ** 2)) / ss_tot

    out = []
    for v in GEN + OTHER:
        y = np.asarray([fvar_pair_words(r["r1"], r["r2"], v) for r in sub], float)
        out.append({"variant": v, "R2_vs_17": r2(y, X), "R2_vs_LKxyimb": r2(y, X_small),
                    "mean": float(y.mean()), "std": float(y.std())})
    return out


def _append(row):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(JSONL, "a") as f:
        f.write(json.dumps(row) + "\n")
        f.flush()
        os.fsync(f.fileno())


def _done():
    s = set()
    if not os.path.exists(JSONL):
        return s
    for line in open(JSONL):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        s.add((r.get("arm"), r.get("pres_id")))
    return s


def run(sub, arms):
    done = _done()
    t0 = time.perf_counter()
    for arm, variant, wF in arms:
        for r in sub:
            if (arm, r["pres_id"]) in done:
                continue
            res = search_fftvar(r["r1"], r["r2"], BUDGET, _cfg_L(), MRL,
                                wF=wF, variant=variant)
            _append({
                "arm": arm, "variant": variant, "wF": wF,
                "pres_id": r["pres_id"], "bin": r["bin"],
                "aut_class": r["aut_class"], "start_length": r["start_length"],
                "budget": BUDGET, "mrl": MRL,
                "solved": bool(res["solved"]),
                "nodes": int(res["nodes_explored"]),
                "path_length": res["path_length"],
                "ts": datetime.now(timezone.utc).isoformat(),
            })
        print(f"  {arm:16s} ({(time.perf_counter()-t0)/60:.1f} min)", flush=True)


def tally():
    by = {}
    for line in open(JSONL):
        r = json.loads(line)
        by.setdefault(r["arm"], []).append(r)
    out = {}
    for arm, rs in by.items():
        solved = [r for r in rs if r["solved"]]
        nodes = [r["nodes"] for r in solved]
        out[arm] = {
            "n": len(rs), "solved": len(solved),
            # 60 rows are only 45 Aut(F2) orbits -- an orbit solved twice is one result
            "orbits": len({r["aut_class"] for r in solved}),
            "mean_nodes": (sum(nodes) / len(nodes)) if nodes else None,
            "variant": rs[0]["variant"], "wF": rs[0]["wF"],
            "by_bin": {b: sum(1 for r in rs if r["bin"] == b and r["solved"])
                       for b in sorted({r["bin"] for r in rs})},
            "solved_ids": {r["pres_id"] for r in solved},
        }
    return out


def write_report(t, red, n_orbits, wall_min):
    ctrl = t["length"]
    L = []
    L.append("# Generator channel on subset-60 — `L + wF*F`, budget 1,000")
    L.append("")
    L.append(f"Updated `{datetime.now(timezone.utc).isoformat()}`")
    L.append("")
    L.append("Generator ring: **x, X -> +1 ; y, Y -> -1**, exponent never read. Motivated by "
             "`r -> r^-1` being an AC symmetry, so inversion carries no invariant information.")
    L.append("")
    L.append(f"**Pool** subset-60, MRL **{MRL}**, budget {BUDGET}. **Control gate passed**: "
             f"`wF=0` reproduces `greedy_search` pop for pop on all 60, and `length` scores "
             f"{ctrl['solved']}/60 — the documented baseline. Wall {wall_min:.1f} min.")
    L.append("")
    L.append(f"> **No holdout.** subset-60 is the benchmark. The whole weight curve is below "
             f"rather than only its best cell, because choosing a weight on the same 60 that "
             f"score it is selection. Also, 60 rows are only **{n_orbits} Aut(F2) orbits**, so "
             f"an orbit column is reported alongside the row count.")
    L.append("")
    L.append("## Does the Parseval argument actually cover this channel?")
    L.append("")
    L.append("| variant | R² vs 17 feats | R² vs {L, K, xyimb} | mean | std |")
    L.append("|---|---:|---:|---:|---:|")
    for r in red:
        tag = "**" if r["variant"] in GEN else ""
        L.append(f"| {tag}`{r['variant']}`{tag} | {r['R2_vs_17']:.3f} | "
                 f"{r['R2_vs_LKxyimb']:.3f} | {r['mean']:.3f} | {r['std']:.3f} |")
    L.append("")
    L.append("The identities `A_gen[1] = L - 4K` and `P_gen[0] = (L*xyimb)²` predict that the "
             "**{L, K, xyimb}** column alone should explain a generator-channel variant. Where "
             "it does not, that variant was never covered by the argument that set the channel "
             "aside.")
    L.append("")
    L.append("## Weight curve — solved / 60")
    L.append("")
    L.append("| variant | channel | " + " | ".join(f"wF={w:g}" for w in WF_GRID)
             + " | best | @ wF | orbits |")
    L.append("|---|---|" + "---:|" * (len(WF_GRID) + 3))
    chan = {**{v: "generator" for v in GEN}, "lag345": "sign", "dftlo": "sign",
            "cplxlo": "complex"}
    rows = []
    for v in GEN + OTHER:
        cells, best, best_arm = [], -1, None
        for w in WF_GRID:
            a = t.get(f"{v}_w{w:g}")
            cells.append(a["solved"] if a else None)
            if a and a["solved"] > best:
                best, best_arm = a["solved"], a
        rows.append((best, v, cells, best_arm))
    for best, v, cells, best_arm in sorted(rows, reverse=True):
        tag = "**" if v in GEN else ""
        cs = " | ".join(str(c) if c is not None else "—" for c in cells)
        edge = " ⚠" if best_arm["wF"] == min(WF_GRID) else ""
        L.append(f"| {tag}`{v}`{tag} | {chan[v]} | {cs} | **{best}** | "
                 f"{best_arm['wF']:g}{edge} | {best_arm['orbits']} |")
    L.append(f"| `length` (control) | — | "
             + " | ".join([str(ctrl['solved'])] * len(WF_GRID))
             + f" | **{ctrl['solved']}** | — | {ctrl['orbits']} |")
    L.append("")
    L.append("⚠ marks a best cell sitting on the **low edge** of the grid — the optimum may be "
             "outside it, so that arm's score is a lower bound, not a peak.")
    L.append("")
    L.append("## Best generator arm vs the incumbents, per difficulty bin")
    L.append("")
    best_gen = max((t[f"{v}_w{w:g}"] for v in GEN for w in WF_GRID
                    if f"{v}_w{w:g}" in t), key=lambda a: a["solved"])
    best_oth = max((t[f"{v}_w{w:g}"] for v in OTHER for w in WF_GRID
                    if f"{v}_w{w:g}" in t), key=lambda a: a["solved"])
    show = [("length", ctrl),
            (f"{best_gen['variant']} @ wF={best_gen['wF']:g}", best_gen),
            (f"{best_oth['variant']} @ wF={best_oth['wF']:g}", best_oth)]
    bins = sorted(ctrl["by_bin"])
    L.append("| arm | " + " | ".join(f"bin {b}" for b in bins) + " | total | mean nodes |")
    L.append("|---|" + "---:|" * (len(bins) + 2))
    for name, a in show:
        mn = f"{a['mean_nodes']:.0f}" if a["mean_nodes"] is not None else "—"
        L.append(f"| `{name}` | " + " | ".join(str(a["by_bin"].get(b, 0)) for b in bins)
                 + f" | **{a['solved']}/60** | {mn} |")
    L.append("")
    L.append("Each bin holds 6 presentations, bin 0 easiest, and each bin is 3.37x the "
             "nodes of the one below.")
    L.append("")
    L.append("## Paired against the control")
    L.append("")
    L.append("| arm | solves control misses | control solves it misses |")
    L.append("|---|---:|---:|")
    for name, a in show[1:]:
        L.append(f"| `{name}` | {len(a['solved_ids'] - ctrl['solved_ids'])} | "
                 f"{len(ctrl['solved_ids'] - a['solved_ids'])} |")
    L.append("")
    L.append("## Notes")
    L.append("")
    L.append("- Every generator-channel variant is exactly invariant under the x<->X relabel "
             "by construction — it cannot read the exponent — so the shipped `lag345`'s "
             "documented relabel wart cannot arise here at all.")
    L.append("- `length` is flat across the weight columns by definition (`wF` multiplies "
             "nothing); it is repeated so the row reads against the others.")
    L.append("- Unsolved = unsolved within budget 1,000.")
    L.append("")
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(RESULTS, "w") as f:
        f.write("\n".join(L))
    return "\n".join(L)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    t0 = time.perf_counter()
    sub = json.load(open(SUBSET))["subset"]
    n_orbits = len({r["aut_class"] for r in sub})
    print(f"subset-60: {len(sub)} rows, {n_orbits} Aut orbits, MRL {MRL}", flush=True)

    search_fftvar("X", "Y", 20, _cfg_L(), MRL, wF=0.0)
    print("control gate…", flush=True)
    print(f"  passed: length = {control_gate(sub)}/60", flush=True)

    print("redundancy…", flush=True)
    red = redundancy(sub)
    for r in red:
        print(f"   {r['variant']:10s} R2_17={r['R2_vs_17']:.3f} "
              f"R2_LKxy={r['R2_vs_LKxyimb']:.3f}", flush=True)
    with open(os.path.join(OUT_DIR, "redundancy.json"), "w") as f:
        json.dump(red, f, indent=2)
        f.write("\n")

    arms = _arms()
    print(f"search: {len(arms)} arms x {len(sub)} pres @ budget {BUDGET}", flush=True)
    run(sub, arms)
    print(write_report(tally(), red, n_orbits, (time.perf_counter() - t0) / 60.0))
    print(f"\nwrote {RESULTS}")


if __name__ == "__main__":
    main()
