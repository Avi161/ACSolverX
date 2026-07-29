"""Timed serial vs parallel mini sweep @ budget ≤ 1000 (HIGH_SPEEDUP path).

Uses unsolved124 head (burns the full budget) so wall time is measurable.
Run as a module so spawn workers re-import safely:

    PYTHONPATH=. python3 -m experiments.heuristic_search.runners.mini_hspeed_bench
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

from experiments.heuristic_search.runners import run_s24_scale as rs  # noqa: E402
from experiments.heuristic_search.runners import run_ab as ra  # noqa: E402
from experiments.heuristic_search.core.hcompact import greedy_search_hcompact  # noqa: E402

ARMS = ["baseline", "s12", "s28", "s20_mk2", "s24_k1_mk2"]
SUBSET = 8
BUDGET = 1000
MRL = 48


def _load(path):
    d = {}
    for line in open(path):
        r = json.loads(line)
        d[(r["arm"], r["name"])] = (
            r["solved"], r["nodes_explored"], r.get("path_length"))
    return d


def _run(label, n_workers, out):
    cfg = dict(
        DATASET="unsolved124", SUBSET=SUBSET, ARMS=ARMS,
        NODE_BUDGET=BUDGET, CHECKPOINTS=[BUDGET],
        MAX_RELATOR_LENGTH=MRL, ENGINE="hcompact", KEEP_PATH=True,
        RESUME=False, OUT_STEM=f"mini_{label}", N_WORKERS=n_workers,
        STAGE_DIR=str(out / "stage"),
    )
    t0 = time.perf_counter()
    ra.run_ab(cfg, out_dir=str(out), heartbeat_secs=10**6, progress_secs=10**6)
    dt = time.perf_counter() - t0
    files = list(out.glob("*.jsonl"))
    assert len(files) == 1, files
    n = sum(1 for line in open(files[0]) if line.strip())
    nw, per = ra._resolve_workers(
        {"N_WORKERS": n_workers}, BUDGET, MRL, "hcompact", True)
    return dict(wall_s=dt, rows=n, nw=nw, gb=per, path=str(files[0]))


def main():
    missing = [a for a in ARMS if a not in ra.ARMS]
    assert not missing, missing

    print("warming kernels...", flush=True)
    greedy_search_hcompact(
        "xyx", "yx", 50, max_relator_length=32, config=ra.ARMS["s12"])

    n_jobs = SUBSET * len(ARMS)
    print(f"host cores={os.cpu_count()} MemAvailable≈{ra._avail_gb():.1f} GB",
          flush=True)
    print(f"jobs={n_jobs} (= {SUBSET} rows × {len(ARMS)} arms) "
          f"budget={BUDGET} engine=hcompact dataset=unsolved124", flush=True)

    tmpdir = Path(tempfile.mkdtemp(prefix="hsearch_mini_"))
    try:
        print("--- SERIAL N_WORKERS=1 ---", flush=True)
        r1 = _run("serial", 1, tmpdir / "ser")
        print(f"SERIAL:  wall={r1['wall_s']:.2f}s  rows={r1['rows']}  "
              f"workers={r1['nw']}", flush=True)

        print("--- PARALLEL N_WORKERS=auto ---", flush=True)
        r2 = _run("parallel", "auto", tmpdir / "par")
        print(f"PARALLEL: wall={r2['wall_s']:.2f}s  rows={r2['rows']}  "
              f"workers={r2['nw']}  est={r2['gb']:.2f}GB/search", flush=True)

        speedup = r1["wall_s"] / r2["wall_s"]
        print(f"\n=== SPEEDUP {speedup:.2f}x  "
              f"(serial_wall / parallel_wall) ===", flush=True)
        print(f"per-job: serial={r1['wall_s']/n_jobs:.3f}s  "
              f"parallel={r2['wall_s']/n_jobs:.3f}s", flush=True)

        a, b = _load(r1["path"]), _load(r2["path"])
        mism = [k for k in a if a[k] != b[k]]
        print(f"result-neutral mismatches: {len(mism)}/{len(a)}", flush=True)
        assert not mism

        _ag, _cc = ra._avail_gb, os.cpu_count
        ra._avail_gb = lambda: 50.0
        os.cpu_count = lambda: 8
        nw_c, per_c = ra._resolve_workers(
            {"N_WORKERS": "auto"}, 1_000_000, 48, "hcompact", True)
        ra._avail_gb, os.cpu_count = _ag, _cc
        print(f"\nColab @1M / 8 cores / 50GB / hcompact: "
              f"workers={nw_c} ({per_c:.1f} GB/search)", flush=True)
        print(f"Ideal bound ~{nw_c}x; measured here with {r2['nw']} "
              f"workers = {speedup:.2f}x "
              f"(efficiency {100 * speedup / max(r2['nw'], 1):.0f}% "
              f"of {r2['nw']}x)", flush=True)
        return speedup, r1, r2, nw_c
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    main()
