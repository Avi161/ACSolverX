"""Run the numba CoV-gate search on MS640 and ladder100 (bench60 is read off MS640), all six gates, in parallel.

One JSONL per (benchmark, gate) in --out, one record per row (resumable: finished rows are skipped). Rows are
scheduled hardest first (MS640 by its GS-SUB node count, ladder100 by level) so long searches start early.

  python benchmark/ryan/run_all.py --out results/ryan_1e5 --max-nodes 100000 --workers 64
  python benchmark/ryan/run_all.py --out results/ryan_1e6 --max-nodes 1000000 --only-unsolved-from results/ryan_1e5

No length cap by default (--max-length / --max-total set one; Ryan's are 24 / 48).
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

os.environ.setdefault("NUMBA_NUM_THREADS", "1")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import cov_gates_cpu as C  # noqa: E402

CODE = {"x": 1, "X": -1, "y": 2, "Y": -2}


def rows(bench):
    """[(row_id, key, difficulty)] for ms640 or ladder100."""
    out = []
    if bench == "ms640":
        g = {}
        with (ROOT / "benchmark/difficulty_bins.csv").open() as f:
            for r in csv.DictReader(f):
                g[int(r["pres_id"])] = int(r["nodes_explored"])
        lines = [l for l in (ROOT / "data/ms640_solved.txt").read_text().splitlines() if l.strip()]
        for i, line in enumerate(lines):
            out.append((str(i), C.start_key_from_row(json.loads(line)), g.get(i, 0)))
    elif bench == "ladder100":
        with (ROOT / "benchmark/ladder/ladder_default.csv").open() as f:
            for r in csv.DictReader(f):
                r1 = tuple(CODE[c] for c in r["r1"])
                r2 = tuple(CODE[c] for c in r["r2"])
                out.append((r["name"], C.canonical_key(r1, r2), int(r["level"]) * 10**7))
    else:
        raise ValueError(bench)
    return out


def work(bench, gate, rid, key, max_nodes, max_len, max_total):
    import cov_gates_numba as K
    rec = K.search(key, gate, max_nodes, max_len, max_total)
    rec.update(bench=bench, id=rid, gate=gate, max_nodes=max_nodes, max_length=max_len, max_total=max_total)
    rec["start"] = C._payload(key)
    return rec


def _warm():
    import cov_gates_numba as K
    K.search(C.canonical_key((-2, -2, -1, 2, 1), (-2, 1)), "periodic10", 20)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--benches", default="ms640,ladder100")
    ap.add_argument("--gates", default=",".join(C.GATES))
    ap.add_argument("--max-nodes", type=int, default=100_000)
    ap.add_argument("--max-length", type=int, default=None)
    ap.add_argument("--max-total", type=int, default=None)
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--only-unsolved-from", default=None)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    jobs = []
    for bench in a.benches.split(","):
        rs = rows(bench)
        for gate in a.gates.split(","):
            f = out / f"{bench}__{gate}.jsonl"
            done = {json.loads(l)["id"] for l in f.read_text().splitlines()} if f.exists() else set()
            prev = {}
            if a.only_unsolved_from:
                pf = Path(a.only_unsolved_from) / f"{bench}__{gate}.jsonl"
                prev = {r["id"]: r for r in map(json.loads, pf.read_text().splitlines())}
            for rid, key, diff in rs:
                if rid in done:
                    continue
                if prev and prev[rid]["solved"]:
                    continue
                jobs.append((diff, bench, gate, rid, key))
    jobs.sort(key=lambda j: -j[0])
    print(f"{len(jobs)} searches, {a.workers} workers", flush=True)
    handles = {}
    with ProcessPoolExecutor(a.workers, initializer=_warm) as ex:
        futs = {ex.submit(work, b, g, rid, key, a.max_nodes, a.max_length, a.max_total): (b, g)
                for _, b, g, rid, key in jobs}
        for n, fut in enumerate(as_completed(futs), 1):
            b, g = futs[fut]
            rec = fut.result()
            if (b, g) not in handles:
                handles[b, g] = (out / f"{b}__{g}.jsonl").open("a", buffering=1)
            handles[b, g].write(json.dumps(rec, separators=(",", ":")) + "\n")
            if n % 100 == 0 or n == len(jobs):
                print(f"{n}/{len(jobs)} done", flush=True)
    for h in handles.values():
        h.close()


if __name__ == "__main__":
    main()
