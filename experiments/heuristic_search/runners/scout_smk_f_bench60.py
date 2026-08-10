"""Family winners on benchmark_subset_60 @ budget 1,000.

Arms = length + pure S/MK/F + S+MK / S+F / MK+F / S+MK+F (train-selected
from smk_f_grid). Fixed; no selection on this set.

    PYTHONPATH=. .venv/bin/python3 -m experiments.heuristic_search.runners.scout_smk_f_bench60
"""
from __future__ import annotations

import concurrent.futures
import json
import multiprocessing as mp
import os
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

from experiments.heuristic_search.core.search_signlag import search_signlag  # noqa: E402

ROOT = _d
SUBSET = os.path.join(ROOT, "benchmark", "subsets", "benchmark_subset_60.json")
OUT_DIR = os.path.join(ROOT, "results", "heuristic_search", "smk_f_grid")
JSONL = os.path.join(OUT_DIR, "bench60_1k_runs.jsonl")
RESULTS = os.path.join(OUT_DIR, "BENCH60_1K.md")
BUDGET = 1000
CAP = 48

# prior Aut-split scores for the report table (train / spent / fresh)
PRIOR = {
    "length": (0, 0, 0),
    "S20": (49, 30, 27),
    "MK6_418": (16, 5, 9),
    "F4": (30, 10, 15),
    "S20_MK2": (54, 33, 27),
    "S16_F4": (48, 29, 23),
    "MK6_418_F8": (31, 11, 11),
    "S28_MK2_F8": (57, 28, 22),
}


def _cfg(**w):
    ww = {"L": 1.0}
    ww.update({k: float(v) for k, v in w.items() if v})
    return {"segments": [{"upto": None, "w": ww}]}


ARMS = [
    ("length", _cfg(), 0.0, 0.0, 0.0, "length"),
    ("S20", _cfg(S=20), 20.0, 0.0, 0.0, "pure S"),
    ("MK6_418", _cfg(MK=6.418), 0.0, 6.418, 0.0, "pure MK"),
    ("F4", _cfg(), 0.0, 0.0, 4.0, "pure F"),
    ("S20_MK2", _cfg(S=20, MK=2), 20.0, 2.0, 0.0, "S+MK"),
    ("S16_F4", _cfg(S=16), 16.0, 0.0, 4.0, "S+F"),
    ("MK6_418_F8", _cfg(MK=6.418), 0.0, 6.418, 8.0, "MK+F"),
    ("S28_MK2_F8", _cfg(S=28, MK=2), 28.0, 2.0, 8.0, "S+MK+F"),
]


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


def _worker(job):
    arm, cfg, s, mk, wF, fam, rec = job
    res = search_signlag(rec["r1"], rec["r2"], BUDGET, cfg, CAP, wF=wF)
    return {
        "half": "bench60", "arm": arm, "family": fam,
        "S": s, "MK": mk, "F": wF,
        "pres_id": rec["pres_id"], "bin": rec.get("bin"),
        "r1": rec["r1"], "r2": rec["r2"],
        "nodes_1M_greedy": rec.get("nodes_1M"),
        "budget": BUDGET, "cap": CAP,
        "solved": bool(res["solved"]),
        "nodes": int(res["nodes_explored"]),
        "solved_at": (int(res["nodes_explored"]) if res["solved"] else None),
        "ts": datetime.now(timezone.utc).isoformat(),
    }


def _summarize():
    by = defaultdict(list)
    for line in open(JSONL):
        r = json.loads(line)
        by[r["arm"]].append(r)
    out = []
    for arm, _, s, mk, wF, fam in ARMS:
        rs = by.get(arm, [])
        # de-dupe by pres_id (last wins)
        uniq = {}
        for r in rs:
            uniq[r["pres_id"]] = r
        rs = list(uniq.values())
        sol = [r for r in rs if r["solved"]]
        mean_n = (sum(r["nodes"] for r in sol) / len(sol)) if sol else None
        # by bin
        bins = defaultdict(lambda: [0, 0])
        for r in rs:
            bins[r.get("bin")][1] += 1
            if r["solved"]:
                bins[r.get("bin")][0] += 1
        out.append({
            "arm": arm, "family": fam, "S": s, "MK": mk, "F": wF,
            "n": len(rs), "solved": len(sol), "mean_nodes": mean_n,
            "bins": dict(bins),
        })
    return out


def write_results(ranked):
    lines = [
        "# Family winners on benchmark_subset_60 @ budget 1,000",
        "",
        f"Updated `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "**evaluated_on** = `benchmark/subsets/benchmark_subset_60.json` "
        "(difficulty-binned ladder; not the Aut hard holdout)",
        "**selected_on** = ac1m_hard_aut train 120 (arms fixed from smk_f_grid)",
        "",
        "| family | arm | train | spent 60 | fresh 60 | **bench60 @1k** | mean nodes |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for r in ranked:
        tr, sp, fr = PRIOR[r["arm"]]
        mn = (f"{r['mean_nodes']:.0f}" if r["mean_nodes"] is not None else "—")
        lines.append(
            f"| **{r['family']}** | `{r['arm']}` | {tr}/120 | "
            f"{sp}/60 | {fr}/60 | **{r['solved']}/{r['n']}** | {mn} |")

    lines += [
        "",
        "### Per-bin solves (bench60)",
        "",
    ]
    # collect bin ids
    all_bins = sorted({b for r in ranked for b in r["bins"]},
                      key=lambda x: (x is None, x))
    header = "| arm | " + " | ".join(f"b{b}" for b in all_bins) + " |"
    sep = "|---|" + "|".join(["---:"] * len(all_bins)) + "|"
    lines += [header, sep]
    for r in ranked:
        cells = []
        for b in all_bins:
            sol, n = r["bins"].get(b, [0, 0])
            cells.append(f"{sol}/{n}" if n else "—")
        lines.append(f"| `{r['arm']}` | " + " | ".join(cells) + " |")

    lines += [
        "",
        "## Notes",
        "",
        "- Bench60 is an easy→hard ladder (many bin-0/1 presentations). "
          "Length solves a large fraction here; it scored 0 on the Aut-hard 60s.",
        "- Do not re-rank from this set alone — selection stayed on Aut train.",
        "- Unsolved = unsolved within budget 1000.",
        "",
    ]
    with open(RESULTS, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines), flush=True)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    rows = json.load(open(SUBSET))["subset"]
    assert len(rows) == 60, len(rows)
    done = _done()
    jobs = []
    for rec in rows:
        for arm, cfg, s, mk, wF, fam in ARMS:
            if (arm, rec["pres_id"]) in done:
                continue
            jobs.append((arm, cfg, s, mk, wF, fam, rec))
    nw = max(1, os.cpu_count() or 1)
    print(f"[bench60-1k] n={len(rows)} arms={len(ARMS)} "
          f"todo={len(jobs)} workers={nw}", flush=True)

    search_signlag("X", "Y", 30, _cfg(S=20, MK=2), 32, wF=4.0)

    if jobs:
        t0 = time.time()
        n_new = 0
        ctx = mp.get_context("fork")
        with concurrent.futures.ProcessPoolExecutor(
                max_workers=nw, mp_context=ctx) as ex:
            CHUNK = 128
            for i0 in range(0, len(jobs), CHUNK):
                batch = jobs[i0:i0 + CHUNK]
                futs = [ex.submit(_worker, j) for j in batch]
                for fut in concurrent.futures.as_completed(futs):
                    row = fut.result()
                    _append(row)
                    n_new += 1
                    if n_new % 40 == 0 or n_new == len(jobs):
                        rate = n_new / max(time.time() - t0, 1e-9)
                        eta = (len(jobs) - n_new) / max(rate, 1e-9)
                        print(f"  +{n_new}/{len(jobs)} {rate:.2f}/s "
                              f"ETA {eta/60:.1f} min last={row['arm']} "
                              f"id={row['pres_id']} sol={row['solved']}",
                              flush=True)
        print(f"[bench60-1k] new={n_new}", flush=True)

    write_results(_summarize())


if __name__ == "__main__":
    main()
