"""Pre-registered slice-C read for the complex-ring transform.

Provenance, in order, so the claim is auditable:

* [`RESULTS.md`](../../../results/heuristic_search/fftvar_scout/RESULTS.md) — slice A,
  13 transforms at wF=4. Picked `dftlo` (7/20) and `cplxlo` (6/20) over the shipped
  `lag345` (1/20).
* [`CONFIRM.md`](../../../results/heuristic_search/fftvar_scout/CONFIRM.md) — weight sweep on
  slice A and a frozen read on slice B. `dftlo` collapsed 7/20 -> 2/20 (selection artifact);
  `cplxlo` held 6/20 -> 6/20 and rose monotonically with weight, 4 / 6 / 9 at wF = 2 / 4 / 8.

Slice A therefore selects **`cplxlo` at wF=8**, and slice B is now spent for weight selection
(it was read at wF=4 only). This file reads that configuration **once**, on a third disjoint
train slice, against the two controls that matter — `length` (the baseline ordering) and
`lag345` (the shipped Fourier term). Nothing here is tuned; the arms are fixed before the run.

Slices A, B and C are all inside the *train* split, so both holdouts stay virgin for the
eventual Colab read on the full 120.

    PYTHONPATH=. .venv/bin/python3 -m experiments.heuristic_search.runners.scout_fftvar_slicec
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
JSONL = os.path.join(OUT_DIR, "slice_c.jsonl")
RESULTS = os.path.join(OUT_DIR, "SLICE_C.md")

BUDGET = 1000
CAP = 48
N_PRES = 20
SLICE_C_LO, SLICE_C_HI = 40, 60      # train rows 40-59, disjoint from A (0-19) and B (20-39)

#: Frozen before the run. (arm, variant, wF)
ARMS = (
    ("length", "lag345", 0.0),           # baseline ordering
    ("lag345_w4", "lag345", 4.0),        # shipped Fourier term
    ("cplxlo_w8", "cplxlo", 8.0),        # slice-A selection
)


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
        s.add((r.get("arm"), r.get("idx")))
    return s


def _tally(path, slice_filter=None):
    by = {}
    if not os.path.exists(path):
        return by
    for line in open(path):
        r = json.loads(line)
        if slice_filter is not None and r.get("slice") != slice_filter:
            continue
        by.setdefault(r["arm"], []).append(r)
    out = {}
    for arm, rs in by.items():
        solved = [r for r in rs if r["solved"]]
        nodes = [r["nodes"] for r in solved]
        out[arm] = {
            "n": len(rs), "solved": len(solved),
            "mean_nodes": (sum(nodes) / len(nodes)) if nodes else None,
            "mean_min_relator": sum(r["min_relator_length"] for r in rs) / len(rs),
        }
    return out


def write_report(c, wall_min):
    conf = os.path.join(OUT_DIR, "confirm.jsonl")
    a = _tally(conf, "A")
    b = _tally(conf, "B")

    # pooled across the three disjoint train slices, for the arms present in all three
    pooled = {}
    for label, key_a, key_b, key_c in (
            ("length", "length_w0", "length_w0", "length"),
            ("lag345 @ wF=4", "lag345_w4", "lag345_w4", "lag345_w4")):
        if key_a in a and key_b in b and key_c in c:
            pooled[label] = (a[key_a]["solved"] + b[key_b]["solved"] + c[key_c]["solved"],
                             a[key_a]["n"] + b[key_b]["n"] + c[key_c]["n"])

    L = []
    L.append("# Slice C — pre-registered read of the complex-ring transform")
    L.append("")
    L.append(f"Updated `{datetime.now(timezone.utc).isoformat()}`")
    L.append("")
    L.append("Arms frozen before the run; slice C read once. Selection provenance is in "
             "[`RESULTS.md`](RESULTS.md) (transform) and [`CONFIRM.md`](CONFIRM.md) "
             "(weight + replication).")
    L.append("")
    L.append(f"Budget {BUDGET}, cap {CAP}. **Slice C** = ac1m_hard_aut train rows "
             f"{SLICE_C_LO}-{SLICE_C_HI-1}, disjoint from A (0-19) and B (20-39). "
             f"Wall {wall_min:.1f} min.")
    L.append("")
    L.append("## Slice C")
    L.append("")
    L.append("| arm | score | solved | mean nodes | mean min-relator |")
    L.append("|---|---|---:|---:|---:|")
    label = {"length": "`L`", "lag345_w4": "`L + 4*F_lag345`",
             "cplxlo_w8": "`L + 8*F_cplxlo`"}
    for arm, _, _ in ARMS:
        r = c.get(arm)
        if not r:
            continue
        mn = f"{r['mean_nodes']:.0f}" if r["mean_nodes"] is not None else "—"
        L.append(f"| `{arm}` | {label[arm]} | **{r['solved']}/{r['n']}** | {mn} | "
                 f"{r['mean_min_relator']:.1f} |")
    L.append("")
    L.append("## All three train slices, arms common to all")
    L.append("")
    L.append("| arm | A (0-19) | B (20-39) | C (40-59) | pooled |")
    L.append("|---|---:|---:|---:|---:|")
    for lab, (ks, kn) in pooled.items():
        keys = {"length": ("length_w0", "length_w0", "length"),
                "lag345 @ wF=4": ("lag345_w4", "lag345_w4", "lag345_w4")}[lab]
        L.append(f"| `{lab}` | {a[keys[0]]['solved']}/{a[keys[0]]['n']} | "
                 f"{b[keys[1]]['solved']}/{b[keys[1]]['n']} | "
                 f"{c[keys[2]]['solved']}/{c[keys[2]]['n']} | **{ks}/{kn}** |")
    if "cplxlo_w4" in a and "cplxlo_w4" in b:
        L.append(f"| `cplxlo @ wF=4` | {a['cplxlo_w4']['solved']}/{a['cplxlo_w4']['n']} | "
                 f"{b['cplxlo_w4']['solved']}/{b['cplxlo_w4']['n']} | not run | "
                 f"**{a['cplxlo_w4']['solved'] + b['cplxlo_w4']['solved']}/"
                 f"{a['cplxlo_w4']['n'] + b['cplxlo_w4']['n']}** |")
    if "cplxlo_w8" in a and "cplxlo_w8" in c:
        L.append(f"| `cplxlo @ wF=8` | {a['cplxlo_w8']['solved']}/{a['cplxlo_w8']['n']} | "
                 f"not run | {c['cplxlo_w8']['solved']}/{c['cplxlo_w8']['n']} | "
                 f"**{a['cplxlo_w8']['solved'] + c['cplxlo_w8']['solved']}/"
                 f"{a['cplxlo_w8']['n'] + c['cplxlo_w8']['n']}** |")
    L.append("")
    L.append("Pooling is honest only for `length` and `lag345 @ wF=4`, which were fixed before "
             "any slice was read. `cplxlo` rows mix a selection slice with a confirmation "
             "slice and are shown for size, not as an unbiased estimate.")
    L.append("")
    L.append("## Notes")
    L.append("")
    L.append("- 60 presentations at budget 1,000 is still a scout. The decision read is the "
             "full train 120 plus a holdout, on Colab.")
    L.append("- Both holdouts (`splits_ac1m_hard_aut` holdout 60, `splits_fft_fresh_holdout60`) "
             "remain unspent by this work.")
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
    slice_c = train[SLICE_C_LO:SLICE_C_HI]
    assert len(slice_c) == N_PRES

    search_fftvar("X", "Y", 20, _cfg_L(), 32, wF=0.0)
    done = _done()
    for arm, variant, wF in ARMS:
        for rec in slice_c:
            if (arm, rec["idx"]) in done:
                continue
            res = search_fftvar(rec["r1"], rec["r2"], BUDGET, _cfg_L(), CAP,
                                wF=wF, variant=variant)
            _append({
                "slice": "C", "arm": arm, "variant": variant, "wF": wF,
                "idx": rec["idx"], "budget": BUDGET, "cap": CAP,
                "solved": bool(res["solved"]),
                "nodes": int(res["nodes_explored"]),
                "min_relator_length": int(res["min_relator_length"]),
                "ts": datetime.now(timezone.utc).isoformat(),
            })
        print(f"  [C] {arm:12s} ({(time.perf_counter()-t0)/60:.1f} min)", flush=True)

    wall = (time.perf_counter() - t0) / 60.0
    print(write_report(_tally(JSONL), wall))
    print(f"\nwrote {RESULTS}")


if __name__ == "__main__":
    main()
