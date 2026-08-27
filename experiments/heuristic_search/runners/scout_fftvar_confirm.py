"""Confirm pass for ``scout_fftvar``: is the transform ranking a weight artifact, and does it
replicate off the slice it was picked on?

``scout_fftvar`` ranks 13 transforms at one weight on 20 presentations. Two ways that ranking
could be an illusion, and this file tests both:

1. **Weight artifact.** The variants are normalised to per-relator [0,1], but their *spreads*
   still differ (``dftlo`` std 0.49 vs ``lag345`` std 0.36 on start states), so at a single
   weight a wider feature gets a larger effective push. Sweeping ``wF`` over {2, 4, 8} for the
   finalists separates "better transform" from "more of a transform".

2. **Slice artifact.** Slice A (train rows 0-19) is where the winner was chosen; a 15-arm sweep
   on 20 presentations has room to pick a lucky one. Slice B (train rows 20-39) is disjoint and
   is read once, at the fixed weight, with the arms frozen. Both slices are inside the *train*
   split, so neither holdout is spent.

Still budget 1,000 and 20 presentations per slice (repo local-run cap). This decides which
transform earns a Colab run, not whether it works.

    PYTHONPATH=. .venv/bin/python3 -m experiments.heuristic_search.runners.scout_fftvar_confirm
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

from experiments.heuristic_search.core.search_fftvar import search_fftvar  # noqa: E402

ROOT = _d
SPLIT = os.path.join(ROOT, "results", "heuristic_search", "splits",
                     "splits_ac1m_hard_aut.json")
OUT_DIR = os.path.join(ROOT, "results", "heuristic_search", "fftvar_scout")
JSONL = os.path.join(OUT_DIR, "confirm.jsonl")
RESULTS = os.path.join(OUT_DIR, "CONFIRM.md")

BUDGET = 1000
CAP = 48
N_PRES = 20

#: finalists from scout_fftvar, plus the shipped transform as the control
FINALISTS = ("lag345", "dftlo", "cplxlo", "dfthi")
WF_GRID = (2.0, 4.0, 8.0)
WF_FIXED = 4.0


def _cfg_L():
    return {"segments": [{"upto": None, "w": {"L": 1.0}}]}


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
        s.add((r.get("slice"), r.get("arm"), r.get("idx")))
    return s


def _run(slice_name, pres, arms, done):
    t0 = time.perf_counter()
    for arm, variant, wF in arms:
        for rec in pres:
            if (slice_name, arm, rec["idx"]) in done:
                continue
            res = search_fftvar(rec["r1"], rec["r2"], BUDGET, _cfg_L(), CAP,
                                wF=wF, variant=variant)
            _append({
                "slice": slice_name, "arm": arm, "variant": variant, "wF": wF,
                "idx": rec["idx"], "budget": BUDGET, "cap": CAP,
                "solved": bool(res["solved"]),
                "nodes": int(res["nodes_explored"]),
                "min_relator_length": int(res["min_relator_length"]),
                "ts": datetime.now(timezone.utc).isoformat(),
            })
        print(f"  [{slice_name}] {arm:16s} ({(time.perf_counter()-t0)/60:.1f} min)",
              flush=True)


def _tally(slice_name):
    by = {}
    for line in open(JSONL):
        r = json.loads(line)
        if r["slice"] != slice_name:
            continue
        by.setdefault(r["arm"], []).append(r)
    out = {}
    for arm, rs in by.items():
        solved = sorted(r["idx"] for r in rs if r["solved"])
        nodes = [r["nodes"] for r in rs if r["solved"]]
        out[arm] = {
            "n": len(rs), "solved": len(solved), "solved_idxs": solved,
            "mean_nodes": (sum(nodes) / len(nodes)) if nodes else None,
            "mean_min_relator": sum(r["min_relator_length"] for r in rs) / len(rs),
            "variant": rs[0]["variant"], "wF": rs[0]["wF"],
        }
    return out


def write_report(a, b, wall_min):
    L = []
    L.append("# Spectral-transform confirm — weight sweep + disjoint replication")
    L.append("")
    L.append(f"Updated `{datetime.now(timezone.utc).isoformat()}`")
    L.append("")
    L.append("Tests the two ways [`RESULTS.md`](RESULTS.md)'s ranking could be an illusion: a "
             "weight artifact (the variants have different spreads) and a slice artifact (the "
             "winner was chosen on slice A).")
    L.append("")
    L.append(f"Budget {BUDGET}, cap {CAP}. **Slice A** = ac1m_hard_aut train rows 0-{N_PRES-1} "
             f"(selection). **Slice B** = train rows {N_PRES}-{2*N_PRES-1}, disjoint, arms "
             f"frozen at wF={WF_FIXED:g}. Holdouts untouched. Wall {wall_min:.1f} min.")
    L.append("")
    L.append("## 1. Weight sweep — slice A (selection)")
    L.append("")
    L.append("| variant | wF=2 | wF=4 | wF=8 | best |")
    L.append("|---|---:|---:|---:|---:|")
    for v in FINALISTS:
        cells = []
        for w in WF_GRID:
            r = a.get(f"{v}_w{w:g}")
            cells.append(f"{r['solved']}/{r['n']}" if r else "—")
        best = max((a[f"{v}_w{w:g}"]["solved"] for w in WF_GRID
                    if f"{v}_w{w:g}" in a), default=0)
        mark = "**" if v == "lag345" else ""
        L.append(f"| {mark}`{v}`{mark} | " + " | ".join(cells) + f" | {best} |")
    ctrl = a.get("length_w0")
    if ctrl:
        L.append(f"| `length` (control) | {ctrl['solved']}/{ctrl['n']} | — | — | "
                 f"{ctrl['solved']} |")
    L.append("")
    L.append("## 2. Disjoint replication — slice B, wF=4, frozen")
    L.append("")
    L.append("| variant | slice A | slice B | mean nodes (B) | mean min-relator (B) |")
    L.append("|---|---:|---:|---:|---:|")
    order = sorted(FINALISTS,
                   key=lambda v: -(b.get(f"{v}_w{WF_FIXED:g}", {}).get("solved", 0)))
    for v in order:
        ra = a.get(f"{v}_w{WF_FIXED:g}")
        rb = b.get(f"{v}_w{WF_FIXED:g}")
        if not rb:
            continue
        mn = f"{rb['mean_nodes']:.0f}" if rb["mean_nodes"] is not None else "—"
        mark = "**" if v == "lag345" else ""
        L.append(f"| {mark}`{v}`{mark} | {ra['solved']}/{ra['n']} | "
                 f"**{rb['solved']}/{rb['n']}** | {mn} | {rb['mean_min_relator']:.1f} |")
    cb = b.get("length_w0")
    ca = a.get("length_w0")
    if cb and ca:
        L.append(f"| `length` (control) | {ca['solved']}/{ca['n']} | "
                 f"**{cb['solved']}/{cb['n']}** | — | {cb['mean_min_relator']:.1f} |")
    L.append("")
    L.append("## 3. Which presentations each arm solves (slice A, wF=4)")
    L.append("")
    L.append("Pairing matters more than the counts at n=20: an arm that solves a strict "
             "superset is a different claim from one that trades solves.")
    L.append("")
    L.append("| variant | solved idxs |")
    L.append("|---|---|")
    for v in FINALISTS:
        r = a.get(f"{v}_w{WF_FIXED:g}")
        if r:
            L.append(f"| `{v}` | {', '.join(str(i) for i in r['solved_idxs']) or '—'} |")
    L.append("")
    L.append("## Notes")
    L.append("")
    L.append("- Slice B is read **once**, with arms frozen from slice A — no re-tuning.")
    L.append("- Both slices are train. Neither the spent nor the fresh holdout is touched, so "
             "the eventual Colab read is still clean.")
    L.append("- Unsolved = unsolved within budget 1,000.")
    L.append("")
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(RESULTS, "w") as f:
        f.write("\n".join(L))
    return "\n".join(L)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    t0 = time.perf_counter()
    sp = json.load(open(SPLIT))
    train = sorted(sp["train_rows"], key=lambda r: r["idx"])
    slice_a = train[:N_PRES]
    slice_b = train[N_PRES:2 * N_PRES]
    assert not ({r["idx"] for r in slice_a} & {r["idx"] for r in slice_b})

    arms_a = [("length_w0", "lag345", 0.0)]
    for v in FINALISTS:
        for w in WF_GRID:
            arms_a.append((f"{v}_w{w:g}", v, w))
    arms_b = [("length_w0", "lag345", 0.0)] + [
        (f"{v}_w{WF_FIXED:g}", v, WF_FIXED) for v in FINALISTS]

    search_fftvar("X", "Y", 20, _cfg_L(), 32, wF=0.0)
    done = _done()
    print(f"slice A: {len(arms_a)} arms x {len(slice_a)} pres", flush=True)
    _run("A", slice_a, arms_a, done)
    done = _done()
    print(f"slice B: {len(arms_b)} arms x {len(slice_b)} pres", flush=True)
    _run("B", slice_b, arms_b, done)

    wall = (time.perf_counter() - t0) / 60.0
    print(write_report(_tally("A"), _tally("B"), wall))
    print(f"\nwrote {RESULTS}")


if __name__ == "__main__":
    main()
