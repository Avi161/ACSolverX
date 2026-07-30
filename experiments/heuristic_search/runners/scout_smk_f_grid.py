"""Full S × MK × Fsign grid on AC1M-hard Aut train 120 @ budget 1000.

No K (this sweep is S/MK/F only). Fsign = mean |sign-lag autocorr| at lags 3–5
(FFT band-energy equivalent on the exponent-sign channel).

Grids match prior scouts:
  S  ∈ {0,4,8,12,16,20,24,28}
  MK ∈ {0,2,4,6.418,8,10}
  F  ∈ {0,2,4,8,16}
→ 8×6×5 = 240 arms × 120 = 28,800 searches.

    PYTHONPATH=. .venv/bin/python3 -m experiments.heuristic_search.runners.scout_smk_f_grid
"""
from __future__ import annotations

import concurrent.futures
import csv
import itertools
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
OUT_DIR = os.path.join(ROOT, "results", "heuristic_search", "smk_f_grid")
JSONL = os.path.join(OUT_DIR, "runs.jsonl")
RESULTS = os.path.join(OUT_DIR, "RESULTS.md")
CSV_OUT = os.path.join(OUT_DIR, "ranking_train.csv")
BUDGET = 1000
CAP = 48

S_GRID = (0.0, 4.0, 8.0, 12.0, 16.0, 20.0, 24.0, 28.0)
MK_GRID = (0.0, 2.0, 4.0, 6.418, 8.0, 10.0)
F_GRID = (0.0, 2.0, 4.0, 8.0, 16.0)


def _f(x):
    return f"{x:g}".replace(".", "_")


def _tag(s, mk, wF):
    if s == 0 and mk == 0 and wF == 0:
        return "length"
    parts = []
    if s:
        parts.append(f"S{_f(s)}")
    if mk:
        parts.append(f"MK{_f(mk)}")
    if wF:
        parts.append(f"F{_f(wF)}")
    return "_".join(parts) if parts else "length"


def _cfg(s, mk):
    w = {"L": 1.0}
    if s:
        w["S"] = float(s)
    if mk:
        w["MK"] = float(mk)
    return {"segments": [{"upto": None, "w": w}]}


def all_arms():
    arms = []
    for s, mk, wF in itertools.product(S_GRID, MK_GRID, F_GRID):
        arms.append((_tag(s, mk, wF), _cfg(s, mk), float(s), float(mk),
                     float(wF)))
    return arms


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


def _worker(job):
    arm, cfg, s, mk, wF, rec = job
    res = search_signlag(rec["r1"], rec["r2"], BUDGET, cfg, CAP, wF=wF)
    return {
        "half": "train", "arm": arm,
        "S": s, "MK": mk, "F": wF,
        "idx": rec["idx"], "L": rec.get("L"),
        "budget": BUDGET, "cap": CAP,
        "solved": bool(res["solved"]),
        "nodes": int(res["nodes_explored"]),
        "solved_at": (int(res["nodes_explored"]) if res["solved"] else None),
        "ts": datetime.now(timezone.utc).isoformat(),
    }


def _rank():
    by = defaultdict(list)
    for line in open(JSONL):
        r = json.loads(line)
        if r.get("half") != "train":
            continue
        by[r["arm"]].append(r)
    ranked = []
    for arm, rs in by.items():
        sol = [r for r in rs if r["solved"]]
        mean_n = (sum(r["nodes"] for r in sol) / len(sol)) if sol else None
        ranked.append({
            "arm": arm,
            "S": rs[0]["S"], "MK": rs[0]["MK"], "F": rs[0]["F"],
            "n": len(rs), "solved": len(sol),
            "mean_nodes": mean_n,
        })
    ranked.sort(key=lambda r: (-r["solved"],
                               r["mean_nodes"] if r["mean_nodes"] is not None
                               else 1e18))
    return ranked


def write_results(ranked):
    length = next((r for r in ranked if r["arm"] == "length"), None)
    best = ranked[0]
    # best by family
    def fam(pred, name):
        cands = [r for r in ranked if pred(r)]
        return (name, cands[0] if cands else None)

    families = [
        fam(lambda r: r["S"] == 0 and r["MK"] == 0 and r["F"] == 0, "length"),
        fam(lambda r: r["S"] > 0 and r["MK"] == 0 and r["F"] == 0, "pure S"),
        fam(lambda r: r["S"] == 0 and r["MK"] > 0 and r["F"] == 0, "pure MK"),
        fam(lambda r: r["S"] == 0 and r["MK"] == 0 and r["F"] > 0, "pure F"),
        fam(lambda r: r["S"] > 0 and r["MK"] > 0 and r["F"] == 0, "S+MK"),
        fam(lambda r: r["S"] > 0 and r["MK"] == 0 and r["F"] > 0, "S+F"),
        fam(lambda r: r["S"] == 0 and r["MK"] > 0 and r["F"] > 0, "MK+F"),
        fam(lambda r: r["S"] > 0 and r["MK"] > 0 and r["F"] > 0, "S+MK+F"),
    ]
    lines = [
        "# S × MK × Fsign grid — AC1M-hard Aut train 120 @ budget 1,000",
        "",
        f"Updated `{datetime.now(timezone.utc).isoformat()}`",
        "",
        f"Grid: |S|={len(S_GRID)} × |MK|={len(MK_GRID)} × |F|={len(F_GRID)} "
        f"= {len(S_GRID)*len(MK_GRID)*len(F_GRID)} arms. No K.",
        "Fsign = mean_|A_sign[d]| for d=3..5 (FFT-equivalent sign-channel lags).",
        "",
        "**selected_on / evaluated_on** = ac1m_hard_aut train 120 "
        "(this run is the selection sweep; holdout not read).",
        "",
        f"## Winner: `{best['arm']}`",
        "",
        f"S={best['S']:g}, MK={best['MK']:g}, F={best['F']:g} → "
        f"**{best['solved']}/{best['n']}**"
        + (f" (mean nodes {best['mean_nodes']:.0f})"
           if best["mean_nodes"] is not None else ""),
        "",
        f"Length control: "
        f"**{length['solved']}/{length['n']}**" if length else "",
        "",
        "### Best by family",
        "",
    ]
    for name, r in families:
        if r is None:
            lines.append(f"- **{name}:** —")
        else:
            mn = (f", mean nodes {r['mean_nodes']:.0f}"
                  if r["mean_nodes"] is not None else "")
            lines.append(
                f"- **{name}:** `{r['arm']}` → {r['solved']}/{r['n']} "
                f"(S={r['S']:g}, MK={r['MK']:g}, F={r['F']:g}{mn})")
    lines += [
        "",
        "### Top 40",
        "",
        "| rank | arm | S | MK | F | solved | Δ vs length | mean nodes |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    base = length["solved"] if length else 0
    for i, r in enumerate(ranked[:40], 1):
        mn = f"{r['mean_nodes']:.0f}" if r["mean_nodes"] is not None else "—"
        lines.append(
            f"| {i} | `{r['arm']}` | {r['S']:g} | {r['MK']:g} | {r['F']:g} | "
            f"**{r['solved']}/{r['n']}** | {r['solved']-base:+d} | {mn} |")
    lines += [
        "",
        "## Notes",
        "",
        "- Headline Δ is vs length on the same 120 (length is 0 here).",
        "- Do not promote from train alone — need a virgin holdout read next.",
        "- Unsolved = unsolved within budget 1000.",
        "",
    ]
    with open(RESULTS, "w") as f:
        f.write("\n".join(lines) + "\n")
    with open(CSV_OUT, "w", newline="") as f:
        w = csv.DictWriter(
            f, fieldnames=["rank", "arm", "S", "MK", "F", "solved", "n",
                           "mean_nodes"])
        w.writeheader()
        for i, r in enumerate(ranked, 1):
            w.writerow({"rank": i, **r})
    print("\n".join(lines[:80]), flush=True)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    train = json.load(open(SPLIT))["train_rows"]
    arms = all_arms()
    done = _done()
    jobs = []
    for rec in train:
        for arm, cfg, s, mk, wF in arms:
            if (arm, rec["idx"]) in done:
                continue
            jobs.append((arm, cfg, s, mk, wF, rec))
    nw = max(1, os.cpu_count() or 1)
    print(f"[smk-f] train={len(train)} arms={len(arms)} "
          f"todo={len(jobs)} workers={nw}", flush=True)

    # warm kernels in parent (fork inherits)
    search_signlag("X", "Y", 30, _cfg(20, 2), 32, wF=4.0)

    if jobs:
        t0 = time.time()
        n_new = 0
        ctx = mp.get_context("fork")
        with concurrent.futures.ProcessPoolExecutor(
                max_workers=nw, mp_context=ctx) as ex:
            CHUNK = 256
            for i0 in range(0, len(jobs), CHUNK):
                batch = jobs[i0:i0 + CHUNK]
                futs = [ex.submit(_worker, j) for j in batch]
                for fut in concurrent.futures.as_completed(futs):
                    row = fut.result()
                    _append(row)
                    n_new += 1
                    if n_new % 200 == 0 or n_new == len(jobs):
                        rate = n_new / max(time.time() - t0, 1e-9)
                        eta = (len(jobs) - n_new) / max(rate, 1e-9)
                        print(f"  +{n_new}/{len(jobs)} {rate:.2f}/s "
                              f"ETA {eta/60:.1f} min last={row['arm']} "
                              f"sol={row['solved']}", flush=True)
        print(f"[smk-f] new={n_new}", flush=True)

    ranked = _rank()
    # require complete arms
    incomplete = [r for r in ranked if r["n"] < len(train)]
    if incomplete:
        print(f"[warn] {len(incomplete)} incomplete arms", flush=True)
    write_results(ranked)


if __name__ == "__main__":
    main()
