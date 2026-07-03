"""Phase 0.5 — one (cap, budget) n=2 greedy sweep over MS(1190), resumable.

The heavy lifting is here (importable/testable); ``run_greedy.ipynb`` is a thin Colab
wrapper that sets params and calls ``run_sweep``. One run == one of the 4 streams:

    cap='sum'         -> greedy_reprogate_{tier}.jsonl   (notebook sum-cap; reproduce 634/640)
    cap='per_relator' -> greedy_baseline_{tier}.jsonl    (env L=24 cap; the arms' baseline)

Each run is independent and resumable (skips idx already in its stream). Use --workers>1
for multi-core boxes; the MAIN process is the single JSONL writer (safe appends).

    python run_greedy.py --cap sum         --budget 100000  --workers 4
    python run_greedy.py --cap per_relator --budget 1000000 --workers 4
    python run_greedy.py --cap sum --budget 1000000 --shard 0/3   # idx chunk 0 of 3
"""
import argparse
import ast
import os
import time
from multiprocessing import Pool

import greedy_ac as g
from jsonl_io import jsonl_append, jsonl_done_ids

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
DEFAULT_DATA = os.path.join(ROOT, "data", "1190MS.txt")
DEFAULT_OUT_DIR = os.path.join(ROOT, "results")

ARM = {"sum": "reprogate", "per_relator": "baseline"}
DEFAULT_MAX_LEN = {"sum": 100, "per_relator": 24}
CONTROL_IDX = 700  # a known-unsolved idx (>=640) for the base-case control


def stream_name(cap, budget):
    tier = {100_000: "100k", 1_000_000: "1m"}.get(budget, str(budget))
    return f"greedy_{ARM[cap]}_{tier}.jsonl"


def load_lines(data_path):
    with open(data_path) as f:
        return [ast.literal_eval(ln) for ln in f if ln.strip()]


def _worker(task):
    idx, flat, cap, max_len, budget = task
    r = g.solve_one(flat, cap_mode=cap, max_len=max_len, max_nodes=budget)
    r["idx"] = idx
    r["budget_nodes"] = budget
    r["cap"] = cap
    return r


def base_case(lines, cap, max_len):
    """Must pass before the sweep. (1) solver matches the notebook, (2) known-easy idx
    solve + verify, (3) a known-hard idx stays unsolved."""
    r1, r2 = g.MS(3, "YXyxy")
    s = g.ACRelatorSolver(r1, r2, max_nodes=10_000, max_len=20, verbose=False, stop_early=False)
    path, nodes, _ = s.solve()
    assert path is None and nodes == 10_000, f"notebook-match failed: nodes={nodes} solved={path is not None}"
    for idx in range(5):
        r = g.solve_one(lines[idx], cap_mode=cap, max_len=max_len, max_nodes=100_000)
        assert r["solved"] and r["path_verified"], f"base solve idx {idx} failed: {r}"
    r = g.solve_one(lines[CONTROL_IDX], cap_mode=cap, max_len=max_len, max_nodes=10_000)
    assert not r["solved"], f"control idx {CONTROL_IDX} unexpectedly solved: {r}"
    print(f"[base-case] PASS (cap={cap}, max_len={max_len}): notebook-match + idx0-4 solved&verified "
          f"+ idx{CONTROL_IDX} unsolved")


def run_sweep(cap, budget, max_len, data_path=DEFAULT_DATA, out_dir=DEFAULT_OUT_DIR,
              workers=1, shard=None, run_base=True, progress_every=25):
    lines = load_lines(data_path)
    n = len(lines)
    if run_base:
        base_case(lines, cap, max_len)

    lo, hi = 0, n
    if shard is not None:
        i, k = shard
        chunk = (n + k - 1) // k
        lo, hi = i * chunk, min((i + 1) * chunk, n)

    out_path = os.path.join(out_dir, stream_name(cap, budget))
    done = jsonl_done_ids(out_path)
    todo = [idx for idx in range(lo, hi) if idx not in done]
    print(f"[sweep] {stream_name(cap, budget)} cap={cap} budget={budget} max_len={max_len} "
          f"range=[{lo},{hi}) done={len(done)} todo={len(todo)} workers={workers}")

    tasks = ((idx, lines[idx], cap, max_len, budget) for idx in todo)
    t0 = time.time()
    n_done = n_solved = 0

    def record(r):
        nonlocal n_done, n_solved
        jsonl_append(out_path, r)
        n_done += 1
        n_solved += int(r["solved"] and r["path_verified"])
        if n_done % progress_every == 0:
            print(f"  {n_done}/{len(todo)} done, {n_solved} solved (this run), {time.time() - t0:.0f}s")

    if workers == 1:
        for task in tasks:
            record(_worker(task))
    else:
        with Pool(workers) as pool:
            for r in pool.imap_unordered(_worker, tasks, chunksize=1):
                record(r)

    print(f"[sweep] DONE: {n_done} new ({n_solved} solved) in {time.time() - t0:.0f}s -> {out_path}")
    return out_path


def _parse_shard(s):
    if not s:
        return None
    i, k = s.split("/")
    return int(i), int(k)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap", choices=["sum", "per_relator"], required=True)
    ap.add_argument("--budget", type=int, required=True)
    ap.add_argument("--max_len", type=int, default=None, help="default: 100 (sum) / 24 (per_relator)")
    ap.add_argument("--data", default=DEFAULT_DATA)
    ap.add_argument("--out_dir", default=DEFAULT_OUT_DIR)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--shard", default=None, help="i/k contiguous idx chunk (e.g. 0/3)")
    ap.add_argument("--no_base_case", action="store_true")
    args = ap.parse_args()

    max_len = args.max_len if args.max_len is not None else DEFAULT_MAX_LEN[args.cap]
    run_sweep(args.cap, args.budget, max_len, data_path=args.data, out_dir=args.out_dir,
              workers=args.workers, shard=_parse_shard(args.shard), run_base=not args.no_base_case)


if __name__ == "__main__":
    main()
