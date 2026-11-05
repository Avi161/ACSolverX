"""Run cov_full.search (Ryan's CoV-gate search with the full CoV image family) on MS640 and ladder100, in parallel.

bench60 is read off MS640. One JSONL per benchmark in --out, one record per row; finished rows are skipped, so a
rerun resumes. A ladder100 row with the same start state as an MS640 row reuses that search. Rows run hardest first.
Each search runs in its own process, so ``max_rss_mb`` is that search's peak memory.

  python benchmark/ryan/run_full.py --out results/ryan_cov_full_1e5 --budget 100000 --workers 190
  python benchmark/ryan/run_full.py --out results/ryan_cov_full_1e6 --budget 1000000 \\
      --only-unsolved-from results/ryan_cov_full_1e5 --workers 24
"""
from __future__ import annotations

import argparse
import json
import os
import resource
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

os.environ.setdefault("NUMBA_NUM_THREADS", "1")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cov_gates_cpu as C  # noqa: E402
from run_all import rows  # noqa: E402


def work(key, gate, budget, mode, charge):
    import cov_full as F
    rec = F.search(key, gate, budget, mode, charge)
    rec["max_rss_mb"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--benches", default="ms640,ladder100")
    ap.add_argument("--gate", default="no_short_sub", choices=C.GATES)
    ap.add_argument("--mode", default="full", choices=("ryan", "union", "full"))
    ap.add_argument("--budget", type=int, default=100_000, help="units per row")
    ap.add_argument("--no-charge", action="store_true", help="count pops only, as Ryan's code does")
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--only-unsolved-from", default=None)
    ap.add_argument("--limit", type=int, default=None, help="first N rows of each benchmark (tests)")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    meta = {"gate": a.gate, "mode": a.mode, "budget": a.budget, "charge_openings": not a.no_charge,
            "family": "suballpxyb8", "max_length": None}
    targets = {}                        # start key -> [(bench, id)]
    order = {}                          # start key -> difficulty
    for bench in a.benches.split(","):
        f = out / f"{bench}__{a.gate}.jsonl"
        done = {json.loads(l)["id"] for l in f.read_text().splitlines()} if f.exists() else set()
        prev = {}
        if a.only_unsolved_from:
            prev = {r["id"]: r for r in map(json.loads,
                                             (Path(a.only_unsolved_from) / f.name).read_text().splitlines())}
        for rid, key, diff in rows(bench)[:a.limit]:
            if rid in done or (prev and prev[rid]["solved"]):
                continue
            targets.setdefault(key, []).append((bench, rid))
            order[key] = max(order.get(key, 0), diff)
    keys = sorted(targets, key=lambda k: -order[k])
    print(f"{len(keys)} searches for {sum(map(len, targets.values()))} rows, {a.workers} workers", flush=True)
    handles = {}
    with ProcessPoolExecutor(a.workers, max_tasks_per_child=1) as ex:
        futs = {ex.submit(work, k, a.gate, a.budget, a.mode, not a.no_charge): k for k in keys}
        for n, fut in enumerate(as_completed(futs), 1):
            key = futs[fut]
            rec = fut.result()
            for bench, rid in targets[key]:
                if bench not in handles:
                    handles[bench] = (out / f"{bench}__{a.gate}.jsonl").open("a", buffering=1)
                handles[bench].write(json.dumps({**rec, "bench": bench, "id": rid, **meta,
                                                 "start": C._payload(key)}, separators=(",", ":")) + "\n")
            print(f"{n}/{len(keys)} solved={rec['solved']} units={rec['units']} rss={rec['max_rss_mb']}MB "
                  f"sec={rec['elapsed_sec']} {targets[key][0]}", flush=True)
    for h in handles.values():
        h.close()


if __name__ == "__main__":
    main()
