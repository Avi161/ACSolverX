"""Parallel runner for the idea benchmark (harness.py).

Spreads (strategy, presentation) cells across processes so the full 17-strategy ×
22-presentation × 2-budget sweep finishes in minutes, not hours. Candidate
generation is budget-independent, so each cell generates the candidate list ONCE
and searches it at every budget. Uses the default start method (spawn on macOS —
re-imports per worker, sharing numba's on-disk cache; this sidesteps the
fork+numba deadlock recorded in experiments/lessons). Writes the SAME jsonl schema
as harness.run_bench, so harness.summarize reads it unchanged.

CLI (from the repo root):
    .venv/bin/python3 -m experiments.stable_ac.idea_bench.run_sweep \
        --bench combined_22 --budgets 500 1000 --jobs 8
"""

import argparse
import json
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime

from experiments.stable_ac.idea_bench import harness

_STRAT = None


def _strategies():
    global _STRAT
    if _STRAT is None:
        _STRAT = harness.load_strategies()
    return _STRAT


def _run_cell(payload):
    """One (strategy, presentation) cell: generate candidates once, search at each
    budget. Returns a list of result rows (one per budget)."""
    sname, pres, budgets, cap = payload
    fn = _strategies()[sname]
    err = None
    try:
        cands = list(fn(pres["r1"], pres["r2"], cap))
    except Exception as e:
        cands, err = None, repr(e)
    rows = []
    for budget in budgets:
        if err is not None:
            res = {"solved": False, "error": err, "n_candidates": 0,
                   "search_calls": 0, "total_nodes": 0, "winning_nodes": None,
                   "path_length": None, "solve_idx": None, "changed_coords": False}
        else:
            t0 = time.perf_counter()
            res = harness.evaluate_cands(cands, pres["r1"], pres["r2"], budget, cap)
            res["elapsed"] = round(time.perf_counter() - t0, 3)
        res.update({"pres_id": pres["pres_id"], "tier": pres["tier"],
                    "strategy": sname, "budget": budget,
                    "nodes_1M": pres["nodes_1M"], "path_1M": pres["path_1M"]})
        rows.append(res)
    return rows


def run(bench="combined_22", budgets=(500, 1000), cap=harness.DEFAULT_CAP,
        jobs=None, out_path=None, only=None, out_dir="results/stable_ac/idea_bench"):
    """Run the sweep in parallel with RESUME: any (strategy, pres_id, budget) row
    already present in ``out_path`` is skipped, so a run killed by a background-job
    wall is simply relaunched (foreground, bounded) until it reports nothing left.
    A fixed ``out_path`` accumulates across relaunches; summarize keeps the last row
    per (strategy, pres_id, budget), so a redone interrupted cell is harmless."""
    root = harness.find_repo_root(harness.HERE)
    bench_rows = harness.load_bench(bench)
    strat = harness.load_strategies()
    if only:
        strat = {k: v for k, v in strat.items() if k in set(only)}
    if jobs is None:
        jobs = max(1, (os.cpu_count() or 4) - 2)
    od = out_dir if os.path.isabs(out_dir) else os.path.join(root, out_dir)
    os.makedirs(od, exist_ok=True)
    if out_path is None:
        stamp = datetime.now().strftime("%m_%d_%y_%H%M%S")
        out_path = os.path.join(
            od, f"idea_bench_{bench}_{'_'.join(map(str, budgets))}_{stamp}.jsonl")
    elif not os.path.isabs(out_path):
        out_path = os.path.join(od, out_path)

    done = set()
    if os.path.exists(out_path):
        for ln in open(out_path):
            ln = ln.strip()
            if not ln:
                continue
            try:
                r = json.loads(ln)
            except ValueError:
                continue
            done.add((r["strategy"], r["pres_id"], r["budget"]))
    cells = [(sname, p, list(budgets), cap) for sname in strat for p in bench_rows
             if not all((sname, p["pres_id"], b) in done for b in budgets)]
    print(f"{len(bench_rows)} pres ({bench}) × {len(strat)} strat × {len(budgets)} "
          f"budg; {len(cells)} cells to run ({len(done)} rows already done) on "
          f"{jobs} workers -> {os.path.basename(out_path)}", flush=True)
    if not cells:
        print("nothing to do — all cells done", flush=True)
        return out_path

    n = 0
    with open(out_path, "a") as f, ProcessPoolExecutor(max_workers=jobs) as ex:
        futs = {ex.submit(_run_cell, c): c for c in cells}
        for fut in as_completed(futs):
            for r in fut.result():
                f.write(json.dumps(r) + "\n")
            f.flush()
            n += 1
            if n % 20 == 0 or n == len(cells):
                print(f"  {n}/{len(cells)} cells done", flush=True)
    print(f"written: {out_path}", flush=True)
    return out_path


def main():
    ap = argparse.ArgumentParser(description="Parallel idea benchmark runner.")
    ap.add_argument("--bench", default="combined_22")
    ap.add_argument("--budgets", type=int, nargs="+", default=[500, 1000])
    ap.add_argument("--cap", type=int, default=harness.DEFAULT_CAP)
    ap.add_argument("--jobs", type=int, default=None)
    ap.add_argument("--out", default=None,
                    help="fixed output jsonl (relative to results dir) to resume/append")
    ap.add_argument("--only", nargs="*", default=None,
                    help="restrict to these strategy names")
    ap.add_argument("--no-summary", action="store_true",
                    help="skip the summary (for intermediate resume chunks)")
    args = ap.parse_args()
    path = run(bench=args.bench, budgets=args.budgets, cap=args.cap, jobs=args.jobs,
               out_path=args.out, only=args.only)
    if not args.no_summary:
        harness.summarize(path)


if __name__ == "__main__":
    main()
