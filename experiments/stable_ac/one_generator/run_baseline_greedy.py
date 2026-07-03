#!/usr/bin/env python3
"""2-gen GS-Sub baseline greedy over the 640 solved MS(1190) presentations.

Runs the n-relator greedy solver at ``n_gen=2`` (no z-stabilization, no null-revert block) on the
first 640 lines of ``data/1190MS.txt`` — the AC-trivial "solved" set (idx 0-639; the first 634 are
byte-identical to ``data/AC19_extended.txt[0:634]``, the 6 at idx 634-639 trivialize only at >=1M
nodes) — to a fixed node budget (default 1,000,000). This is the classical 2-generator control for
the ``z=w`` (n=3) stabilization arms: it emits solved-metric + retraced-path records in the SAME
schema as the z=w calibration streams (via ``calibrate_probe.probe``), so the website viewer can
merge/compare baseline vs z=w directly on the merge key ``dataset|idx|arm|budget_nodes`` (arm = "baseline").

Per-relator length cap (``max_len=24``) — the SAME cap the z=w arms use, so node-usage / path-length
deltas reflect stabilization, not a cap artifact. Best-first on total relator length (GS default).

Output (append-only, crash-safe: append + flush + fsync; resumable — skips idx already recorded):
    <out_dir>/solved/calibration_baseline.jsonl
    <out_dir>/paths/paths_baseline.jsonl

Local:
    python run_baseline_greedy.py                         # -> results/baseline_greedy/{solved,paths}/
    python run_baseline_greedy.py --start 0 --end 640 --budget 1000000 --workers 6

Colab (clone/pull test/stable-ac-moves, mount Drive, then):
    !python experiments/stable_ac/one_generator/run_baseline_greedy.py \
        --out_dir /content/drive/MyDrive/baseline_greedy --workers 6
    # then copy /content/drive/MyDrive/baseline_greedy -> repo results/baseline_greedy/
"""
import argparse
import ast
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)                     # importable calibrate_probe/greedy_nrel/stabilize (fork + spawn)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

import greedy_nrel as gn
from calibrate_probe import probe

L = 24
ARM = "baseline"
N_GEN = 2


def read_flats(path):
    with open(path) as f:
        return [ast.literal_eval(line) for line in f if line.strip()]


def done_idx(path, dataset, arm, budget):
    """idx already recorded for this (dataset, arm, budget) in the solved-metric stream. Tolerates a
    trailing truncated/corrupt line (that idx is simply recomputed)."""
    done = set()
    if not os.path.exists(path):
        return done
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("dataset") == dataset and r.get("arm") == arm and r.get("budget_nodes") == budget:
                done.add(r["idx"])
    return done


def append_jsonl(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(obj) + "\n")
        f.flush()
        os.fsync(f.fileno())


def persist(rec, calib_path, paths_path, run_tag, n_workers):
    """Write the path record FIRST (so a crash never orphans a metric line whose path is missing),
    then the solved-metric row. Stamps run_tag/_source_file for provenance parity with the z=w streams."""
    prec = rec.pop("path_record", None)
    if prec is not None:
        prec["run_tag"] = run_tag
        prec["_source_file"] = os.path.basename(paths_path)
        append_jsonl(paths_path, prec)
    rec["run_tag"] = run_tag
    rec["n_workers"] = n_workers
    rec["_source_file"] = os.path.basename(calib_path)
    append_jsonl(calib_path, rec)


def main():
    ap = argparse.ArgumentParser(description="2-gen GS-Sub baseline greedy over the 640 solved MS(1190).")
    ap.add_argument("--dataset", default="1190MS",
                    help="dataset label stamped on records (also resolves data/<dataset>.txt unless --dataset_path)")
    ap.add_argument("--dataset_path", default=None, help="override path to the presentations file")
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--end", type=int, default=640, help="exclusive; default 640 = the AC-trivial solved set")
    ap.add_argument("--budget", type=int, default=1_000_000, help="node budget per presentation")
    ap.add_argument("--max_len", type=int, default=L, help="per-relator length cap (match the z=w arms)")
    ap.add_argument("--out_dir", default=os.path.join(ROOT, "results", "baseline_greedy"),
                    help="on Colab point this at the mounted Drive dir")
    ap.add_argument("--workers", type=int, default=0, help="0 = auto (cpu_count-1); 1 = serial")
    ap.add_argument("--run_tag", default=None)
    args = ap.parse_args()

    ds_path = args.dataset_path or os.path.join(ROOT, "data", f"{args.dataset}.txt")
    flats = read_flats(ds_path)
    end = min(args.end, len(flats))
    calib_path = os.path.join(args.out_dir, "solved", f"calibration_{ARM}.jsonl")
    paths_path = os.path.join(args.out_dir, "paths", f"paths_{ARM}.jsonl")

    already = done_idx(calib_path, args.dataset, ARM, args.budget)
    todo = [i for i in range(args.start, end) if i not in already]
    tasks = [("baseline", args.dataset, i, ARM, args.budget, flats[i], N_GEN, args.max_len, False)
             for i in todo]

    n_workers = args.workers if args.workers > 0 else max(1, (os.cpu_count() or 2) - 1)
    run_tag = args.run_tag or f"{ARM}_b{args.budget // 1000}k_w{n_workers}"

    print(f"[baseline] {ds_path}")
    print(f"[baseline] idx [{args.start},{end})  budget={args.budget:,}  max_len={args.max_len}  "
          f"arm={ARM}  n_gen={N_GEN}")
    print(f"[baseline] {len(already)} already done, {len(tasks)} to run  ->  {calib_path}")
    if not tasks:
        print("[baseline] nothing to do (resumed complete).")
        return

    gn.solve_one(flats[todo[0]], n_gen=N_GEN, max_len=args.max_len, max_nodes=8)  # warm numba in parent

    t0 = time.time()
    n_solved = 0

    def report(k):
        if k % 25 == 0 or k == len(tasks):
            print(f"  {k}/{len(tasks)}  solved={n_solved}  ({time.time() - t0:.0f}s)")

    if n_workers <= 1:
        for k, task in enumerate(tasks, 1):
            rec = probe(task)
            n_solved += int(rec["solved"])
            persist(rec, calib_path, paths_path, run_tag, n_workers)
            report(k)
    else:
        import multiprocessing as mp
        ctx = mp.get_context("fork" if "fork" in mp.get_all_start_methods() else "spawn")
        with ctx.Pool(n_workers, maxtasksperchild=1) as pool:
            for k, rec in enumerate(pool.imap_unordered(probe, tasks), 1):
                n_solved += int(rec["solved"])
                persist(rec, calib_path, paths_path, run_tag, n_workers)
                report(k)

    print(f"[baseline] done: {n_solved}/{len(tasks)} solved this run in {time.time() - t0:.0f}s "
          f"({len(already) + len(tasks)} total recorded in {os.path.basename(calib_path)}).")


if __name__ == "__main__":
    main()
