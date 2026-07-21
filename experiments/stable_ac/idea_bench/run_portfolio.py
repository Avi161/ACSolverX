"""Production portfolio runner: top idea_bench strategies on the 124 (idea 12).

Wraps the idea_bench machinery for Colab-scale budgets with the discipline the
local sweep runner deliberately lacks:

- **Budget gate**: budgets > 1000 refuse to run unless ``ACSOLVERX_ALLOW_BIG=1``
  (the Colab notebook sets it; local runs must not).
- **One jsonl per budget** (standing feedback rule: multi-budget runs write
  per-budget files), filename = resume identity — every result-changing knob in
  (bench, strategy group, budget, cap), no dates, no result-neutral knobs.
- **flock ownership claim** on each output file before append (a live holder is
  an orphaned worker from a superseded run — it gets killed; see
  ``lessons/orphaned-workers-double-compute.md``), via ``run_cov._claim_out_path``.
- **Torn-line repair before any append** (``run_baseline._repair_jsonl``).
- **Drive mirroring**: appends go to the local file; a whole-file fsynced mirror
  copy lands in ``mirror_dir`` every ``MIRROR_EVERY_S`` (never append to a FUSE
  mount), and a fresh VM seeds the local file back from the mirror.
- **Same-budget control**: the ``baseline`` strategy is force-included — every
  comparison in the analysis is against plain greedy at the same budget.
- ``jobs=1`` runs cells inline (deterministic, monkeypatchable — the test seam).

Row schema = ``run_sweep``'s plus ``cap`` and ``bench``. Resume key =
``(strategy, pres_id, budget)`` within each per-budget file. A solved row here is
a LEAD until its start pair is re-searched and the path replayed through
``experiments/stable_ac/verify_results.py`` conventions — see RUN_ME.

CLI (Colab sets ACSOLVERX_ALLOW_BIG=1; locally keep budgets <= 1000):
    .venv/bin/python3 -m experiments.stable_ac.idea_bench.run_portfolio \
        --bench aca_124 --group top5 --budgets 500 --cap 24 --row-limit 15
"""

import argparse
import json
import os
import re
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

from experiments.run_baseline import _copy_file, _repair_jsonl, _seed_stage
from experiments.stable_ac.cov.run_cov import _claim_out_path
from experiments.stable_ac.idea_bench import harness
from experiments.stable_ac.idea_bench.run_sweep import _run_cell

MIRROR_EVERY_S = 60

# the ladder-validated top rankers (idea_bench RESULTS.md) + the un-harvested
# same-orbit re-seed generator (idea 11) + the mu-descent ranker (orbit-floor
# refutation, STABLE_AC_NEW.tex) + the mandatory same-budget control
DEFAULT_STRATEGIES = ("baseline", "cov_abel_len_lex", "cov_nsubs_escape",
                      "cov_deep_z", "cov_defining_iso", "reseed_orbit",
                      "cov_mu_lex")


def _require_budget_allowed(budgets):
    big = [b for b in budgets if b > 1000]
    if big and os.environ.get("ACSOLVERX_ALLOW_BIG") != "1":
        raise SystemExit(
            f"budgets {big} exceed the 1000-node local cap; production budgets "
            f"run on Colab with ACSOLVERX_ALLOW_BIG=1 (refusing)")


def _out_name(bench, group, budget, cap):
    """Resume identity: every result-changing knob, no dates."""
    return f"portfolio_{bench}_{group}_{budget}_mrl{cap}.jsonl"


def _wandb_start(bench, group, budget, cap, strategies, out_path):
    """Minimal W&B mirror (jsonl stays source of truth). Run id = the dateless
    filename stem, resume='allow' — a Colab disconnect reattaches. run/* keys
    ride a monotone n_cells step; nothing passes step= (monotonic-step lesson).
    Entity/project come from env (WANDB_ENTITY/WANDB_PROJECT, defaulting to
    the repo's team entity); the API key is NEVER hardcoded."""
    import wandb

    run_id = re.sub(r"[^A-Za-z0-9_-]", "-",
                    os.path.splitext(os.path.basename(out_path))[0])
    run = wandb.init(
        entity=os.environ.get("WANDB_ENTITY", "avigyapaudel045-aisc"),
        project=os.environ.get("WANDB_PROJECT", "acsolver"),
        id=run_id, name=f"{group} · {budget} · {bench}",
        group=f"portfolio-{bench}", job_type="stable_ac_portfolio",
        resume="allow",
        config={"bench": bench, "group": group, "budget": budget, "cap": cap,
                "strategies": list(strategies)})
    run.define_metric("n_cells")
    run.define_metric("run/*", step_metric="n_cells")
    return run, run_id


def _wandb_finish(run, run_id, out_path):
    import wandb

    rows = [json.loads(ln) for ln in open(out_path) if ln.strip()]
    n_solved = sum(bool(r.get("solved")) for r in rows)
    run.summary.update({"n_rows": len(rows), "n_solved": n_solved,
                        "cum_nodes": sum(r.get("total_nodes") or 0
                                         for r in rows)})
    art = wandb.Artifact(run_id, type="stable_ac_portfolio_results")
    art.add_file(out_path)
    run.log_artifact(art)
    run.finish()


def _read_done(path):
    done = set()
    if os.path.exists(path):
        for ln in open(path):
            ln = ln.strip()
            if not ln:
                continue
            try:
                r = json.loads(ln)
            except ValueError:
                continue
            done.add((r["strategy"], r["pres_id"], r["budget"]))
    return done


def run_portfolio(bench="aca_124", strategies=DEFAULT_STRATEGIES, group="top5",
                  budgets=(500,), cap=harness.DEFAULT_CAP, jobs=None,
                  row_limit=None, names=None, mirror_dir=None,
                  out_dir="results/stable_ac/portfolio", high_speedup=False,
                  use_wandb=False):
    _require_budget_allowed(budgets)
    if high_speedup:      # env var so spawned workers inherit it; result-neutral
        os.environ["ACSOLVERX_HIGH_SPEEDUP"] = "1"
    root = harness.find_repo_root(harness.HERE)
    bench_rows = harness.load_bench(bench)
    if names:
        keep = set(names)
        bench_rows = [p for p in bench_rows if p["pres_id"] in keep]
    if row_limit:
        bench_rows = bench_rows[:row_limit]
    strategies = list(dict.fromkeys(["baseline", *strategies]))  # control first
    known = harness.load_strategies()
    missing = [s for s in strategies if s not in known]
    if missing:
        raise SystemExit(f"unknown strategies: {missing}")
    if jobs is None:
        jobs = max(1, (os.cpu_count() or 4) - 2)
    od = out_dir if os.path.isabs(out_dir) else os.path.join(root, out_dir)
    os.makedirs(od, exist_ok=True)

    written = []
    for budget in budgets:                       # one file per budget
        out_path = os.path.join(od, _out_name(bench, group, budget, cap))
        mirror_path = (os.path.join(mirror_dir, os.path.basename(out_path))
                       if mirror_dir else None)
        if mirror_path:
            _seed_stage(out_path, mirror_path)
        _claim_out_path(out_path)
        _repair_jsonl(out_path)
        wb_run = None
        if use_wandb:
            wb_run, wb_id = _wandb_start(bench, group, budget, cap,
                                         strategies, out_path)
        done = _read_done(out_path)
        cells = [(s, p, [budget], cap) for s in strategies for p in bench_rows
                 if (s, p["pres_id"], budget) not in done]
        print(f"[{budget}] {len(bench_rows)} pres x {len(strategies)} strat; "
              f"{len(cells)} cells to run ({len(done)} rows done) on {jobs} "
              f"workers -> {os.path.basename(out_path)}", flush=True)
        n_done, n_solved, last_mirror = 0, 0, time.monotonic()
        with open(out_path, "a") as f:
            def _write(rows):
                nonlocal n_done, n_solved, last_mirror
                for r in rows:
                    r.update({"cap": cap, "bench": bench})
                    if r.get("solved"):
                        n_solved += 1
                        print(f"  SOLVED {r['pres_id']} by {r['strategy']} "
                              f"(idx {r['solve_idx']}, {r['winning_nodes']} "
                              f"nodes)", flush=True)
                    f.write(json.dumps(r) + "\n")
                f.flush()
                os.fsync(f.fileno())
                n_done += 1
                if n_done % 5 == 0 or n_done == len(cells):
                    print(f"  [{budget}] {n_done}/{len(cells)} cells, "
                          f"{n_solved} solved rows", flush=True)
                if wb_run is not None:   # len(done)+n_done is monotone across resumes
                    wb_run.log({"n_cells": len(done) + n_done,
                                "run/n_solved": n_solved})
                if mirror_path and time.monotonic() - last_mirror > MIRROR_EVERY_S:
                    _copy_file(out_path, mirror_path)
                    last_mirror = time.monotonic()

            if jobs == 1:
                for c in cells:
                    _write(_run_cell(c))
            else:
                with ProcessPoolExecutor(max_workers=jobs) as ex:
                    futs = {ex.submit(_run_cell, c): c for c in cells}
                    for fut in as_completed(futs):
                        _write(fut.result())
        if mirror_path:
            _copy_file(out_path, mirror_path)
        if wb_run is not None:
            _wandb_finish(wb_run, wb_id, out_path)
        written.append(out_path)
        print(f"[{budget}] written: {out_path}", flush=True)
    return written


def main():
    ap = argparse.ArgumentParser(description="Portfolio runner on the 124.")
    ap.add_argument("--bench", default="aca_124")
    ap.add_argument("--strategies", nargs="*", default=list(DEFAULT_STRATEGIES))
    ap.add_argument("--group", default="top5",
                    help="short tag naming this strategy group (file identity)")
    ap.add_argument("--budgets", type=int, nargs="+", default=[500])
    ap.add_argument("--cap", type=int, default=harness.DEFAULT_CAP)
    ap.add_argument("--jobs", type=int, default=None)
    ap.add_argument("--row-limit", type=int, default=None)
    ap.add_argument("--names", nargs="*", default=None)
    ap.add_argument("--mirror-dir", default=None)
    ap.add_argument("--high-speedup", action="store_true")
    ap.add_argument("--wandb", action="store_true")
    args = ap.parse_args()
    run_portfolio(bench=args.bench, strategies=args.strategies, group=args.group,
                  budgets=args.budgets, cap=args.cap, jobs=args.jobs,
                  row_limit=args.row_limit, names=args.names,
                  mirror_dir=args.mirror_dir, high_speedup=args.high_speedup,
                  use_wandb=args.wandb)


if __name__ == "__main__":
    main()
