"""Run Elliot Steffen's Dual / Triple GS (ACSolverES) on our benchmarks.

Uses the compact C++ engines of https://github.com/ElliotSteffen/ACSolverES
(package `ac_final_paper`, installed separately). Parameters are the ones of that
repo's results/ms640_final_paper_v1/config.json, except:

* max_len = 65, the largest total length the compact engine stores (it is a strict
  bound on |r1|+|r2|, so states up to total 64 are kept);
* max_live_frontier_states = None: no frontier pruning, so no state is dropped
  for being long;
* total_node_budget from --budget.

Usage:
  python benchmark/elliot/run_elliot.py --budget 10000 --out results/elliot_10k \
      [--benches ms640,bench60,ladder100] [--algos ...] [--workers 4]

Writes <out>/<bench>__<algo>.jsonl, one record a row (resumes on rerun).
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

os.environ.setdefault("NUMBA_NUM_THREADS", "1")
csv.field_size_limit(sys.maxsize)

ROOT = Path(__file__).resolve().parents[2]
ALGOS = ("single_auto_cov_dual", "auto_dual", "auto_nonauto_cov_triple")

PAPER_PARAMS = {
    "single_auto_cov_dual": {
        "cov_min_subword_len": 2,
        "cov_preference_threshold": 2,
        "depth_tie_strategy": "deepest",
        "min_standard_moves_between_cov": 0,
        "seed_initial_cov_neighbors": True,
    },
    "auto_dual": {
        "auto_cov_preference_threshold": 2,
        "depth_tie_strategy": "deepest",
        "min_standard_moves_between_auto_cov": 0,
        "seed_initial_auto_cov_neighbors": True,
    },
    "auto_nonauto_cov_triple": {
        "auto_cov_preference_threshold": 2,
        "complete_cov_preference_threshold": 2,
        "depth_tie_strategy": "deepest",
        "min_standard_moves_between_auto_cov": 0,
        "seed_initial_auto_cov_neighbors": True,
        "seed_initial_complete_cov_neighbors": True,
    },
}
MAX_LEN = 65


def load_bench(name: str):
    """Rows (id, r1, r2) of a benchmark; ladder100 is the paper's ladder_default."""
    if name == "ms640":
        rows = []
        letters = {1: "x", -1: "X", 2: "y", -2: "Y"}
        for i, line in enumerate((ROOT / "data/ms640_solved.txt").read_text().split("\n")):
            if not line.strip():
                continue
            ints = [int(t) for t in line.replace("[", " ").replace("]", " ").replace(",", " ").split()]
            half = len(ints) // 2
            r1 = "".join(letters[a] for a in ints[:half] if a)
            r2 = "".join(letters[a] for a in ints[half:] if a)
            rows.append((str(i), r1, r2))
        return rows
    path = {
        "bench60": ROOT / "benchmark/subsets/benchmark_subset_60.csv",
        "ladder100": ROOT / "benchmark/ladder/ladder_default.csv",
    }[name]
    out = []
    with path.open() as fh:
        for r in csv.DictReader(fh):
            out.append((r.get("pres_id") or r["name"], r["r1"], r["r2"]))
    return out


def _move_kind(move):
    t = move.get("move_type")
    if t == "complete_cov":
        return "single_cov" if move.get("cov_variant") == "single_cov" else "complete_cov"
    return t


def run_one(algo: str, budget: int, pid: str, r1: str, r2: str):
    from ac_final_paper import algorithm_adapters as aa

    params = dict(PAPER_PARAMS[algo])
    params.update(total_node_budget=budget, max_len=MAX_LEN, max_live_frontier_states=None)
    rec = {"algo": algo, "id": pid, "r1": r1, "r2": r2, "budget": budget, "max_len": MAX_LEN}
    try:
        t0 = time.perf_counter()
        res = aa.run_algorithm(algo, (r1, r2), params)
        rec["seconds"] = time.perf_counter() - t0
        solved = bool(res.get("solved"))
        moves = res.get("moves") or []
        path = res.get("path") or []
        kinds = {}
        for m in moves:
            k = _move_kind(m)
            kinds[k] = kinds.get(k, 0) + 1
        sub = kinds.get("standard_substitution", 0)
        cov = sum(v for k, v in kinds.items() if k != "standard_substitution")
        rec.update(
            solved=solved,
            nodes=int(res["total_nodes_used"]),
            termination=res.get("termination_reason"),
            path_length=int(res.get("path_length", 0)) if solved else None,
            sub_moves=sub if solved else None,
            cov_moves=cov if solved else None,
            move_kinds=kinds if solved else None,
            # stable_cert: a complete (non-automorphic) CoV step is on the path
            kind=(("stable_cert" if kinds.get("complete_cov") else "ac_path") if solved else None),
            max_relator_len=max(max(len(a), len(b)) for a, b in path) if solved else None,
            max_total_len=max(len(a) + len(b) for a, b in path) if solved else None,
            start_total_len=len(r1) + len(r2),
            frontier_prune_count=res.get("frontier_prune_count"),
            frontier_peak=res.get("frontier_peak", res.get("frontier_peak_live_state_count")),
            path=[list(s) for s in path] if solved else None,
            moves=[{k: v for k, v in m.items() if k in (
                "move_type", "cov_variant", "automorphism", "subword", "target",
                "replacement", "source_queue")} for m in moves] if solved else None,
        )
    except Exception:
        rec["error"] = traceback.format_exc()
    return rec


def _warm(_=None):
    from ac_final_paper import algorithm_adapters as aa
    aa.warm_up(max_len=MAX_LEN)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=10_000)
    ap.add_argument("--out", default="results/elliot_10k")
    ap.add_argument("--benches", default="ms640,bench60,ladder100")
    ap.add_argument("--algos", default=",".join(ALGOS))
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--from", dest="base", default=None,
                    help="earlier run folder at a smaller budget: its solved rows are carried over "
                         "(same result at any larger budget), only its unsolved rows are searched")
    a = ap.parse_args()

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    carried = []          # (bench, algo, record) copied from --from
    jobs = []             # (bench, algo, pid, r1, r2) to search
    for bench in a.benches.split(","):
        rows = load_bench(bench)
        for algo in a.algos.split(","):
            f = out / f"{bench}__{algo}.jsonl"
            done = set()
            if f.exists():
                done = {json.loads(l)["id"] for l in f.read_text().splitlines() if l.strip()}
            base = {}
            if a.base:
                bf = Path(a.base) / f"{bench}__{algo}.jsonl"
                base = {r["id"]: r for r in map(json.loads, bf.read_text().splitlines()) if "error" not in r}
            for pid, r1, r2 in rows:
                if pid in done:
                    continue
                prev = base.get(pid)
                if prev is not None and prev["solved"] and prev["budget"] <= a.budget:
                    rec = dict(prev, budget=a.budget, carried_from=str(a.base))
                    carried.append((bench, algo, rec))
                else:
                    jobs.append((bench, algo, pid, r1, r2))

    handles = {}

    def write(bench, algo, rec):
        rec["bench"] = bench
        key = (bench, algo)
        if key not in handles:
            handles[key] = (out / f"{bench}__{algo}.jsonl").open("a")
        handles[key].write(json.dumps(rec) + "\n")
        handles[key].flush()

    for bench, algo, rec in carried:
        write(bench, algo, rec)
    # one search per (algo, presentation): bench60 and the ladder's ms_* rows are MS640 rows
    unique = {}
    for bench, algo, pid, r1, r2 in jobs:
        unique.setdefault((algo, r1, r2), []).append((bench, pid))
    print(f"{len(carried)} rows carried, {len(jobs)} rows to search, {len(unique)} distinct searches", flush=True)
    with ProcessPoolExecutor(a.workers, initializer=_warm) as ex:
        futs = {ex.submit(run_one, algo, a.budget, uses[0][1], r1, r2): (algo, uses)
                for (algo, r1, r2), uses in unique.items()}
        for n, fut in enumerate(as_completed(futs), 1):
            algo, uses = futs[fut]
            rec = fut.result()
            for bench, pid in uses:
                write(bench, algo, dict(rec, id=pid))
            print(n, algo, [u[1] for u in uses], rec.get("solved"), rec.get("nodes"),
                  round(rec.get("seconds", 0)), rec.get("error", "")[:200], flush=True)
    for h in handles.values():
        h.close()


if __name__ == "__main__":
    main()
