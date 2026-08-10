"""Holdout read: S×MK×F family winners + shipped recommended portfolio.

Family winners (train-selected from smk_f_grid) and the Aut-tune Colab portfolio
(baseline/length, s12, s28, s20_mk2, s24_k1_mk2) on:
  - spent Aut holdout 60
  - virgin fft fresh holdout 60
Budget 1000. No re-selection on holdout.

    PYTHONPATH=. .venv/bin/python3 -m experiments.heuristic_search.runners.scout_smk_f_families_holdout
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
JSONL = os.path.join(OUT_DIR, "families_holdout_runs.jsonl")
# also resume-skip any overlapping cells already in the earlier holdout jsonl
PRIOR = os.path.join(OUT_DIR, "holdout_runs.jsonl")
RESULTS = os.path.join(OUT_DIR, "FAMILIES_HOLDOUT.md")
BUDGET = 1000
CAP = 48


def _cfg(**w):
    ww = {"L": 1.0}
    ww.update({k: float(v) for k, v in w.items() if v})
    return {"segments": [{"upto": None, "w": ww}]}


# (arm, cfg, S, K, MK, F, family_label, train_solved)
# family_label empty ⇒ recommended-portfolio arm only
ARMS = [
    ("length", _cfg(), 0.0, 0.0, 0.0, 0.0, "length", 0),
    ("S20", _cfg(S=20), 20.0, 0.0, 0.0, 0.0, "pure S", 49),
    ("MK6_418", _cfg(MK=6.418), 0.0, 0.0, 6.418, 0.0, "pure MK", 16),
    ("F4", _cfg(), 0.0, 0.0, 0.0, 4.0, "pure F", 30),
    ("S20_MK2", _cfg(S=20, MK=2), 20.0, 0.0, 2.0, 0.0, "S+MK", 54),
    ("S16_F4", _cfg(S=16), 16.0, 0.0, 0.0, 4.0, "S+F", 48),
    ("MK6_418_F8", _cfg(MK=6.418), 0.0, 0.0, 6.418, 8.0, "MK+F", 31),
    ("S28_MK2_F8", _cfg(S=28, MK=2), 28.0, 0.0, 2.0, 8.0, "S+MK+F", 57),
    # shipped recommended portfolio extras (beyond length / S20 / S20_MK2)
    ("S12", _cfg(S=12), 12.0, 0.0, 0.0, 0.0, "recommended", None),
    ("S28", _cfg(S=28), 28.0, 0.0, 0.0, 0.0, "recommended", None),
    ("S24_K1_MK2", _cfg(S=24, K=1, MK=2), 24.0, 1.0, 2.0, 0.0,
     "recommended", None),
]


def _append(row):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(JSONL, "a") as f:
        f.write(json.dumps(row) + "\n")
        f.flush()
        os.fsync(f.fileno())


def _done_from(path):
    s = set()
    if not os.path.exists(path):
        return s
    for line in open(path):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        s.add((r.get("half"), r.get("arm"), r.get("idx")))
    return s


def _load_rows(path, half_key="holdout_rows"):
    d = json.load(open(path))
    return d[half_key]


def _worker(job):
    half, arm, cfg, s, k, mk, wF, fam, train_n, rec = job
    res = search_signlag(rec["r1"], rec["r2"], BUDGET, cfg, CAP, wF=wF)
    return {
        "half": half, "arm": arm, "family": fam,
        "S": s, "K": k, "MK": mk, "F": wF,
        "train_solved": train_n,
        "idx": rec["idx"], "L": rec.get("L"),
        "budget": BUDGET, "cap": CAP,
        "solved": bool(res["solved"]),
        "nodes": int(res["nodes_explored"]),
        "solved_at": (int(res["nodes_explored"]) if res["solved"] else None),
        "ts": datetime.now(timezone.utc).isoformat(),
    }


def _summarize(half):
    # merge PRIOR + JSONL for this half
    by = defaultdict(list)
    for path in (PRIOR, JSONL):
        if not os.path.exists(path):
            continue
        for line in open(path):
            r = json.loads(line)
            if r.get("half") != half:
                continue
            by[r["arm"]].append(r)
    # de-dupe by idx (prefer JSONL via later overwrite — rebuild carefully)
    by2 = {}
    for path in (PRIOR, JSONL):
        if not os.path.exists(path):
            continue
        for line in open(path):
            r = json.loads(line)
            if r.get("half") != half:
                continue
            by2[(r["arm"], r["idx"])] = r
    by = defaultdict(list)
    for (arm, _idx), r in by2.items():
        by[arm].append(r)

    out = []
    for arm, _, s, k, mk, wF, fam, train_n in ARMS:
        rs = by.get(arm, [])
        sol = [r for r in rs if r["solved"]]
        mean_n = (sum(r["nodes"] for r in sol) / len(sol)) if sol else None
        out.append({
            "arm": arm, "family": fam,
            "S": s, "K": k, "MK": mk, "F": wF,
            "train_solved": train_n,
            "n": len(rs), "solved": len(sol), "mean_nodes": mean_n,
        })
    return out


def write_results(spent, fresh):
    lines = [
        "# Family winners + recommended portfolio — holdout @ budget 1,000",
        "",
        f"Updated `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "**selected_on** = ac1m_hard_aut train 120 (family winners from "
        "`smk_f_grid`; recommended = Aut-tune Colab portfolio)",
        "**evaluated_on** = spent Aut holdout 60 + virgin fft fresh holdout 60",
        "",
        "## Family winners",
        "",
        "| family | arm | train | spent 60 | fresh 60 | mean nodes (spent) |",
        "|---|---|---:|---:|---:|---:|",
    ]
    spent_m = {r["arm"]: r for r in spent}
    fresh_m = {r["arm"]: r for r in fresh}
    for arm, *_rest, fam, train_n in ARMS:
        if fam == "recommended":
            continue
        sp, fr = spent_m[arm], fresh_m[arm]
        mn = (f"{sp['mean_nodes']:.0f}" if sp["mean_nodes"] is not None
              else "—")
        tr = f"{train_n}/120" if train_n is not None else "—"
        lines.append(
            f"| **{fam}** | `{arm}` | {tr} | "
            f"**{sp['solved']}/{sp['n']}** | "
            f"**{fr['solved']}/{fr['n']}** | {mn} |")

    lines += [
        "",
        "## Recommended portfolio (shipped Colab arms)",
        "",
        "| arm | spent 60 | fresh 60 | mean nodes (spent) |",
        "|---|---:|---:|---:|",
    ]
    for arm, *_rest, fam, _tn in ARMS:
        if fam != "recommended" and arm not in (
                "length", "S20", "S20_MK2"):
            # still show length/S20/S20_MK2 in recommended table as they are
            # part of the portfolio — include them explicitly below
            continue
    # explicit portfolio order matching SHIP.md
    for arm in ("length", "S12", "S28", "S20_MK2", "S24_K1_MK2"):
        sp, fr = spent_m[arm], fresh_m[arm]
        mn = (f"{sp['mean_nodes']:.0f}" if sp["mean_nodes"] is not None
              else "—")
        lines.append(
            f"| `{arm}` | **{sp['solved']}/{sp['n']}** | "
            f"**{fr['solved']}/{fr['n']}** | {mn} |")

    lines += [
        "",
        "## Full arm table",
        "",
        "| arm | S | K | MK | F | train | spent | fresh |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for arm, _, s, k, mk, wF, fam, train_n in ARMS:
        sp, fr = spent_m[arm], fresh_m[arm]
        tr = f"{train_n}/120" if train_n is not None else "—"
        lines.append(
            f"| `{arm}` | {s:g} | {k:g} | {mk:g} | {wF:g} | {tr} | "
            f"**{sp['solved']}/{sp['n']}** | "
            f"**{fr['solved']}/{fr['n']}** |")

    lines += [
        "",
        "## Notes",
        "",
        "- Fixed arms — no re-tuning on either holdout.",
        "- Spent holdout was used in prior S+K+MK selection (confirmatory).",
        "- Fresh holdout is Aut-disjoint from train + spent.",
        "- `S24_K1_MK2` is the only K>0 arm (shipped portfolio).",
        "",
    ]
    with open(RESULTS, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines), flush=True)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    spent_rows = _load_rows(SPLIT)
    fresh_rows = _load_rows(FRESH)
    done = _done_from(JSONL) | _done_from(PRIOR)
    jobs = []
    for half, rows in (("holdout", spent_rows), ("fresh", fresh_rows)):
        for rec in rows:
            for arm, cfg, s, k, mk, wF, fam, train_n in ARMS:
                if (half, arm, rec["idx"]) in done:
                    continue
                jobs.append((half, arm, cfg, s, k, mk, wF, fam, train_n, rec))
    nw = max(1, os.cpu_count() or 1)
    print(f"[fam-ho] arms={len(ARMS)} spent={len(spent_rows)} "
          f"fresh={len(fresh_rows)} todo={len(jobs)} workers={nw}", flush=True)

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
                    if n_new % 50 == 0 or n_new == len(jobs):
                        rate = n_new / max(time.time() - t0, 1e-9)
                        eta = (len(jobs) - n_new) / max(rate, 1e-9)
                        print(f"  +{n_new}/{len(jobs)} {rate:.2f}/s "
                              f"ETA {eta/60:.1f} min last={row['arm']} "
                              f"{row['half']} sol={row['solved']}", flush=True)
        print(f"[fam-ho] new={n_new}", flush=True)

    write_results(_summarize("holdout"), _summarize("fresh"))


if __name__ == "__main__":
    main()
