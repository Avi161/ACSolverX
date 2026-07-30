"""Holdout read for S×MK×F grid winner on AC1M-hard Aut holdout 60.

Train-selected winner `S28_MK2_F8` (57/120) + controls. Budget 1000.
Also optionally reads the virgin fft fresh holdout 60.

    PYTHONPATH=. .venv/bin/python3 -m experiments.heuristic_search.runners.scout_smk_f_holdout
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
SPLIT = os.path.join(ROOT, "results", "heuristic_search", "splits",
                     "splits_ac1m_hard_aut.json")
FRESH = os.path.join(ROOT, "results", "heuristic_search", "splits",
                     "splits_fft_fresh_holdout60.json")
OUT_DIR = os.path.join(ROOT, "results", "heuristic_search", "smk_f_grid")
JSONL = os.path.join(OUT_DIR, "holdout_runs.jsonl")
RESULTS = os.path.join(OUT_DIR, "HOLDOUT.md")
BUDGET = 1000
CAP = 48


def _cfg(s=0.0, mk=0.0):
    w = {"L": 1.0}
    if s:
        w["S"] = float(s)
    if mk:
        w["MK"] = float(mk)
    return {"segments": [{"upto": None, "w": w}]}


# Train-selected winner + nearest controls (fixed; no re-selection on holdout).
ARMS = [
    ("length", _cfg(0, 0), 0.0, 0.0, 0.0),
    ("S20", _cfg(20, 0), 20.0, 0.0, 0.0),
    ("S20_MK2", _cfg(20, 2), 20.0, 2.0, 0.0),
    ("S20_MK2_F4", _cfg(20, 2), 20.0, 2.0, 4.0),
    ("S28_MK2_F8", _cfg(28, 2), 28.0, 2.0, 8.0),
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
        s.add((r.get("half"), r.get("arm"), r.get("idx")))
    return s


def _worker(job):
    half, arm, cfg, s, mk, wF, rec = job
    res = search_signlag(rec["r1"], rec["r2"], BUDGET, cfg, CAP, wF=wF)
    return {
        "half": half, "arm": arm,
        "S": s, "MK": mk, "F": wF,
        "idx": rec["idx"], "L": rec.get("L"),
        "budget": BUDGET, "cap": CAP,
        "solved": bool(res["solved"]),
        "nodes": int(res["nodes_explored"]),
        "solved_at": (int(res["nodes_explored"]) if res["solved"] else None),
        "ts": datetime.now(timezone.utc).isoformat(),
    }


def _summarize(half):
    by = defaultdict(list)
    for line in open(JSONL):
        r = json.loads(line)
        if r.get("half") != half:
            continue
        by[r["arm"]].append(r)
    out = []
    for arm, _, s, mk, wF in ARMS:
        rs = by.get(arm, [])
        sol = [r for r in rs if r["solved"]]
        mean_n = (sum(r["nodes"] for r in sol) / len(sol)) if sol else None
        out.append({
            "arm": arm, "S": s, "MK": mk, "F": wF,
            "n": len(rs), "solved": len(sol), "mean_nodes": mean_n,
        })
    return out


def write_results(spent, fresh):
    lines = [
        "# S×MK×F holdout read — budget 1,000",
        "",
        f"Updated `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "**selected_on** = ac1m_hard_aut train 120 (grid winner `S28_MK2_F8`)",
        "**evaluated_on (primary)** = ac1m_hard_aut holdout 60 (spent — used in prior S/K/MK tune)",
        "**evaluated_on (virgin)** = fft fresh holdout 60",
        "",
        "## Spent Aut holdout 60",
        "",
        "| arm | S | MK | F | solved | mean nodes |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for r in spent:
        mn = f"{r['mean_nodes']:.0f}" if r["mean_nodes"] is not None else "—"
        lines.append(
            f"| `{r['arm']}` | {r['S']:g} | {r['MK']:g} | {r['F']:g} | "
            f"**{r['solved']}/{r['n']}** | {mn} |")
    lines += [
        "",
        "## Fresh holdout 60",
        "",
        "| arm | S | MK | F | solved | mean nodes |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for r in fresh:
        mn = f"{r['mean_nodes']:.0f}" if r["mean_nodes"] is not None else "—"
        lines.append(
            f"| `{r['arm']}` | {r['S']:g} | {r['MK']:g} | {r['F']:g} | "
            f"**{r['solved']}/{r['n']}** | {mn} |")
    lines += [
        "",
        "## Notes",
        "",
        "- Fixed arms from train selection — no re-tuning on holdout.",
        "- Spent holdout was already used for earlier S+K+MK selection; treat as confirmatory.",
        "- Fresh holdout is Aut-disjoint from train + spent (see split note).",
        "",
    ]
    with open(RESULTS, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines), flush=True)


def _load_fresh():
    d = json.load(open(FRESH))
    if "holdout_rows" in d:
        return d["holdout_rows"]
    if "rows" in d:
        return d["rows"]
    # fallback shapes
    for k, v in d.items():
        if isinstance(v, list) and v and isinstance(v[0], dict) and "r1" in v[0]:
            return v
    raise SystemExit(f"unrecognized fresh split keys: {sorted(d)}")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    spent_rows = json.load(open(SPLIT))["holdout_rows"]
    fresh_rows = _load_fresh()
    done = _done()
    jobs = []
    for half, rows in (("holdout", spent_rows), ("fresh", fresh_rows)):
        for rec in rows:
            for arm, cfg, s, mk, wF in ARMS:
                if (half, arm, rec["idx"]) in done:
                    continue
                jobs.append((half, arm, cfg, s, mk, wF, rec))
    nw = max(1, os.cpu_count() or 1)
    print(f"[smk-f-ho] arms={len(ARMS)} spent={len(spent_rows)} "
          f"fresh={len(fresh_rows)} todo={len(jobs)} workers={nw}", flush=True)

    search_signlag("X", "Y", 30, _cfg(20, 2), 32, wF=4.0)

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
                    if n_new % 50 == 0 or n_new == len(jobs):
                        rate = n_new / max(time.time() - t0, 1e-9)
                        eta = (len(jobs) - n_new) / max(rate, 1e-9)
                        print(f"  +{n_new}/{len(jobs)} {rate:.2f}/s "
                              f"ETA {eta/60:.1f} min last={row['arm']} "
                              f"{row['half']} sol={row['solved']}", flush=True)
        print(f"[smk-f-ho] new={n_new}", flush=True)

    write_results(_summarize("holdout"), _summarize("fresh"))


if __name__ == "__main__":
    main()
