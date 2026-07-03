#!/usr/bin/env python3
"""Multi-arm greedy sweep over the 640 solved MS(1190) presentations — baseline + z=w arms.

Generalizes ``run_baseline_greedy.py`` (whose small helpers it reuses) to run several arms in one
resumable pass and emit records in the identical ``calibrate_probe.probe`` schema, so the website
merges/compares them on ``dataset|idx|arm|budget_nodes``:

  * ``arm == "baseline"``  -> n_gen=2, no stabilization, no null-revert block (the 2-gen control).
  * any other arm (``r1,r2,x,y,...``) -> n_gen=3, ``z=w`` stabilization + null-revert block.

**Memory-aware two-phase scheduling (the reason this is not just ``--workers N``).** On a 16 GB box a
single n=3 case that runs toward a 500k budget peaks at ~5-8 GB RSS (visited set), so only ~2 fit at
once; but the vast majority of idx solve in <=12k nodes (<~170 MB). So we split idx per arm into
*light* (cheap, high parallelism) and *heavy* (may exhaust, low parallelism) and run light first:

  * n=3 arm: heavy = idx that were UNSOLVED at the 12k-budget pass in the ms640 label file
    (``website/sample-data/calibration_ms640.jsonl``); light = the rest.
  * baseline (n=2, memory-light): heavy = the 6 known budget-exhausting boundary idx 634-639.

Light idx run at ``--light_workers`` (default 8), then heavy idx at ``--heavy_workers`` (default 2).
Running light-first lands the bulk of the comparison data in minutes; the heavy tail (hours) can be
gathered incrementally (append+flush+fsync, resumable per (arm,budget)).

Output (one file pair per arm under ``--out_dir``):
    <out_dir>/solved/calibration_<arm>.jsonl
    <out_dir>/paths/paths_<arm>.jsonl

Usage (the matched-budget 640 comparison set: baseline + r1 + r2 at 500k):
    python run_greedy_sweep.py --arms baseline,r1,r2 --budget 500000 --out_dir <repo>/results/solved640
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

import greedy_nrel as gn
from calibrate_probe import probe
from run_baseline_greedy import read_flats, done_idx, append_jsonl, persist  # reuse (DRY)

L = 24
BASELINE_HEAVY = set(range(634, 640))   # n=2 boundary cases that exhaust (from the 1M baseline run)


def arm_n_gen(arm):
    return 2 if arm == "baseline" else 3


def load_ms640_unsolved(ms640_path):
    """arm -> set(idx unsolved at the 12k pass) — the heavy set for n=3 arms."""
    unsolved = {}
    if not os.path.exists(ms640_path):
        return unsolved
    for line in open(ms640_path):
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        if not r.get("solved", True):
            unsolved.setdefault(r["arm"], set()).add(r["idx"])
    return unsolved


def run_phase(tasks, n_workers, calib_of, paths_of, run_tag, label, t0):
    """Run one phase (list of probe tasks) at n_workers, persisting each result to its arm's files."""
    if not tasks:
        return 0
    n_solved = 0
    if n_workers <= 1:
        it = (probe(t) for t in tasks)
    else:
        import multiprocessing as mp
        ctx = mp.get_context("fork" if "fork" in mp.get_all_start_methods() else "spawn")
        pool = ctx.Pool(n_workers, maxtasksperchild=1)
        it = pool.imap_unordered(probe, tasks)
    for k, rec in enumerate(it, 1):
        n_solved += int(rec["solved"])
        persist(rec, calib_of(rec["arm"]), paths_of(rec["arm"]), run_tag, n_workers)
        if k % 20 == 0 or k == len(tasks):
            print(f"  [{label}] {k}/{len(tasks)}  solved={n_solved}  ({time.time() - t0:.0f}s)", flush=True)
    if n_workers > 1:
        pool.close(); pool.join()
    return n_solved


def main():
    ap = argparse.ArgumentParser(description="Multi-arm greedy sweep over the 640 solved MS(1190).")
    ap.add_argument("--arms", default="baseline,r1,r2", help="comma list; 'baseline'=n2, others=n3 z=w")
    ap.add_argument("--dataset", default="1190MS")
    ap.add_argument("--dataset_path", default=None)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--end", type=int, default=640, help="exclusive; 640 = the AC-trivial solved set")
    ap.add_argument("--budget", type=int, default=500_000)
    ap.add_argument("--max_len", type=int, default=L)
    ap.add_argument("--out_dir", default=os.path.join(ROOT, "results", "solved640"))
    ap.add_argument("--light_workers", type=int, default=8)
    ap.add_argument("--heavy_workers", type=int, default=2, help="keep low: n=3 @500k ~5-8GB/worker")
    ap.add_argument("--ms640", default=os.path.join(ROOT, "website", "sample-data", "calibration_ms640.jsonl"),
                    help="12k label file used to classify light vs heavy idx for n=3 arms")
    ap.add_argument("--run_tag", default=None)
    args = ap.parse_args()

    arms = [a.strip() for a in args.arms.split(",") if a.strip()]
    ds_path = args.dataset_path or os.path.join(ROOT, "data", f"{args.dataset}.txt")
    flats = read_flats(ds_path)
    end = min(args.end, len(flats))
    idx_all = list(range(args.start, end))
    ms640_unsolved = load_ms640_unsolved(args.ms640)
    run_tag = args.run_tag or f"solved640_b{args.budget // 1000}k"

    def calib_of(arm):
        return os.path.join(args.out_dir, "solved", f"calibration_{arm}.jsonl")

    def paths_of(arm):
        return os.path.join(args.out_dir, "paths", f"paths_{arm}.jsonl")

    light, heavy = [], []
    for arm in arms:
        ng = arm_n_gen(arm)
        use_block = (arm != "baseline")
        heavy_set = BASELINE_HEAVY if arm == "baseline" else ms640_unsolved.get(arm, set())
        done = done_idx(calib_of(arm), args.dataset, arm, args.budget)
        for i in idx_all:
            if i in done:
                continue
            task = ("solved640", args.dataset, i, arm, args.budget, flats[i], ng, args.max_len, use_block)
            (heavy if i in heavy_set else light).append(task)
        print(f"[sweep] arm {arm:8} n_gen={ng}  heavy={len(heavy_set)}  already_done={len(done)}")

    print(f"[sweep] dataset={args.dataset} idx[{args.start},{end}) budget={args.budget:,} "
          f"max_len={args.max_len}  -> {args.out_dir}")
    print(f"[sweep] LIGHT phase: {len(light)} tasks @ {args.light_workers}w ; "
          f"HEAVY phase: {len(heavy)} tasks @ {args.heavy_workers}w")
    if not light and not heavy:
        print("[sweep] nothing to do (resumed complete).")
        return

    warm = light[0] if light else heavy[0]
    gn.solve_one(warm[5], n_gen=warm[6], max_len=args.max_len, max_nodes=8)  # warm numba in parent

    t0 = time.time()
    s1 = run_phase(light, args.light_workers, calib_of, paths_of, run_tag, "light", t0)
    s2 = run_phase(heavy, args.heavy_workers, calib_of, paths_of, run_tag, "heavy", t0)
    print(f"[sweep] done: light {s1}/{len(light)} + heavy {s2}/{len(heavy)} solved "
          f"in {time.time() - t0:.0f}s  ->  {args.out_dir}")


if __name__ == "__main__":
    main()
