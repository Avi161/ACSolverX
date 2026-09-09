"""Run greedy and s20_mk2 over the WHOLE AC19 Aut-min screen at 10,000 nodes.

WHY THIS RUNNER EXISTS
----------------------
The 1k/10k wave over the 72,779 orbits ran in Colab on 2026-07-31 and only its
FAILURE lists came back into the repo (``unsolved_10k_baseline.csv``, 831 rows;
``unsolved_10k_s20_mk2.csv``, 259). The ~72k per-row costs of the rows that
SOLVED were never committed and exist nowhere reachable. Everything above that
rung is a funnel -- each rung ran only the rung below's failures -- so the
100k/1M/5M/10M jsonls add depth on those same 831 and 259 and not one extra
presentation. The consequence is visible in the week-9 deck: its three-arm
comparison rests on 225 rows because that is all the overlap the archive can
support.

This reverses an earlier instruction ("do not run greedy or s20_mk2 again on
those ~72k") on the operator's explicit later direction, and the runner is the
durable half of that: the jsonl is regenerable from this file, the file is not
regenerable from the jsonl.

WHY ONE RUN AT 10,000 REBUILDS BOTH LOST WAVES
----------------------------------------------
A search at budget B is exactly the first B pops of a longer one -- same
explored set, same discovery order, same pop order -- so a row that solves at
340 nodes records 340 whether the ceiling was 1,000 or 10,000. One pass at
10,000 therefore reports the 1,000-node rung for free by filtering on
``nodes_explored <= 1000``. Cap 48 is not a free choice either: it is what the
surviving 100k/1M/5M rungs ran at, and a different cap would be a different
search that cannot be spliced onto them.

WHY NOT ONE OF THE RUNNERS THAT ALREADY EXIST
---------------------------------------------
``run_leftovers_1m`` owns the arms, the cap and the record schema -- and this
runner reuses all three, calling its ``_job`` verbatim so the records are
byte-comparable with the 100k rung. What it cannot lend is its POOL:
``maxtasksperchild=1`` gives every row a fresh interpreter, which is right at
25-80 minutes a row and ruinous at 72,779 rows of 20-30 ms. ``run_leftovers_5m``
isolates per row for the same reason. ``run_ac19_cascade_screen`` has the pool
but its record is cascade-shaped (winner/attempts/certificate) and its cap is
255. So: their arms, their schema, the screen's pool.

WHAT IT COSTS
-------------
Measured here on a 300-row uniform sample of the screen, budget 10,000, cap 48,
hcompact: greedy 29.1 ms/row (0.59 core-hours over 72,779), s20_mk2 18.5 ms/row
(0.37 core-hours). Both arms together are about one core-hour. The tail is
represented in that sample -- 3 of the 300 ran the full 10,000 -- because 831 of
72,779 is 1.1% and a 300-row sample expects 3.4 of them.

    PYTHONPATH=. python3 -m experiments.search.run_ac19_autmin_10k plan
    PYTHONPATH=. python3 -m experiments.search.run_ac19_autmin_10k smoke --arm greedy
    PYTHONPATH=. python3 -m experiments.search.run_ac19_autmin_10k run --arm greedy
    PYTHONPATH=. python3 -m experiments.search.run_ac19_autmin_10k verify --arm greedy
    PYTHONPATH=. python3 -m experiments.search.run_ac19_autmin_10k report --arm greedy
    PYTHONPATH=. python3 -m experiments.search.run_ac19_autmin_10k costs
"""
from __future__ import annotations

import argparse
import csv
import json
import multiprocessing as mp
import os
import resource
import sys
import time

# Must precede any numba-backed import: BLAS/OpenMP pools spin one thread per
# vCPU at import and each reserves a ~64 MiB malloc arena, which blows a
# worker's RLIMIT_AS before a row runs.
for _var in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
             "NUMBA_NUM_THREADS"):
    os.environ.setdefault(_var, "1")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from experiments.search.run_leftovers_1m import (  # noqa: E402
    ARMS, HAVE_HCOMPACT, _ensure_trailing_newline, _job, read_rows,
    resolve_arm,
)
from experiments.search.run_leftovers_5m import stride_chunk  # noqa: E402

CAMPAIGN = "ac19_autmin_10k"
BUDGET = 10_000
MRL = 48                     # what the 100k/1M/5M rungs ran at; not negotiable
N_ROWS = 72_779

SCREEN_DIR = os.path.join(ROOT, "results", "heuristic_search",
                          "ac19_autmin_screen")
ROWS_CSV = os.path.join(SCREEN_DIR, "ac19_autmin_orbits.csv")
DEFAULT_OUT = os.path.join(ROOT, "results", "heuristic_search", CAMPAIGN)

# The archived failure lists, which are this run's ORACLE. See `verify`.
ORACLE_CSV = {"greedy": "unsolved_10k_baseline.csv",
              "s20_mk2": "unsolved_10k_s20_mk2.csv"}

# How many of the 72,779 orbits the ORIGINAL 10k wave actually judged, per arm
# (hsearch_ac19_hard100k/RESULTS.md, "Residual set sizes"). This run judges all
# 72,779, so it may legitimately fail on rows the archive never saw -- but only
# on those. More extra failures than the gap means the extras are not gap rows
# and something else has changed.
ARCHIVED_COVERAGE = {"greedy": 71_556, "s20_mk2": 71_582}

# Measured on this machine over a 300-row uniform sample, not assumed.
SECONDS_PER_ROW = {"greedy": 0.0291, "s20_mk2": 0.0185}

# Address space per worker. The search itself is small at this budget (the
# widest row seen in the sample grew to ~339k states), but RLIMIT_AS caps
# ADDRESS SPACE, not RAM: it is nearly free to hand out on 64-bit and exists
# only to stop a runaway. The cascade screen uses 4.0 at this same budget.
WORKER_RLIMIT_GB = 4.0
EST_GB_PER_WORKER = 1.0      # run_leftovers_1m.est_gb(10_000, 48) floors at 1.0

ARM_CHOICES = ("greedy", "s20_mk2")


def out_path(arm, out_dir=DEFAULT_OUT, chunks=1, chunk_index=1,
             budget=BUDGET, mrl=MRL):
    key, _ = resolve_arm(arm)
    stem = f"{CAMPAIGN}_{key}_b{budget}_mrl{mrl}"
    if chunks and chunks > 1:
        stem += f"_part{chunk_index}of{chunks}"
    return os.path.join(out_dir, stem + ".jsonl")


def load_rows(path=None, expect=N_ROWS):
    """The screen list. The row count is asserted, never assumed.

    A shallow or stale clone handing this runner a shorter list would otherwise
    run a different experiment to completion and report it under this name.
    """
    path = path or ROWS_CSV
    if not os.path.exists(path):
        raise SystemExit(
            f"{path} is missing. Build it first:\n"
            "  PYTHONPATH=. python3 -m experiments.search."
            "make_ac19_autmin_screen --write")
    with open(path, newline="") as fh:
        rows = [{"name": r["name"], "r1": r["r1"], "r2": r["r2"]}
                for r in csv.DictReader(fh)]
    names = [r["name"] for r in rows]
    if len(names) != len(set(names)):
        raise SystemExit(f"duplicate names in {path}")
    if expect and len(rows) != expect:
        raise SystemExit(f"{path} has {len(rows)} rows, expected {expect} -- "
                         "stale clone; pull the branch before running.")
    return rows


def done_names(path):
    """Finished row names only. Resume never needs more than this."""
    return {r["name"] for r in read_rows(path)
            if "name" in r and not r.get("error")}


def _init_worker(rlimit_bytes):
    try:
        resource.setrlimit(resource.RLIMIT_AS, (rlimit_bytes, rlimit_bytes))
    except (ValueError, OSError) as exc:
        # Fail closed, as every other runner in this campaign does: an
        # unguarded worker on a shared box is how a run takes the box with it.
        raise SystemExit(f"cannot enforce worker address-space limit: {exc}")
    try:
        os.nice(5)
    except OSError:
        pass


def resolve_workers(workers="auto", ram_gb=None):
    cores = os.cpu_count() or 1
    if workers not in (None, "auto"):
        return max(1, int(workers))
    if ram_gb is None:
        try:
            ram_gb = (os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
                      / 2 ** 30)
        except (ValueError, OSError):
            ram_gb = 4.0
    by_ram = max(1, int((ram_gb - 2.0) // EST_GB_PER_WORKER))
    return max(1, min(cores - 1 if cores > 1 else 1, by_ram))


def plan(workers="auto", log=print):
    cores = os.cpu_count() or 1
    n_workers = resolve_workers(workers)
    info = {"campaign": CAMPAIGN, "rows": N_ROWS, "rows_csv": ROWS_CSV,
            "budget": BUDGET, "cap": MRL,
            "engine": "hcompact" if HAVE_HCOMPACT else "PYTHON FALLBACK",
            "cores_here": cores, "workers": n_workers,
            "worker_rlimit_gb_address_space": WORKER_RLIMIT_GB,
            "seconds_per_row_measured": SECONDS_PER_ROW,
            "core_hours": {a: round(N_ROWS * s / 3600, 2)
                           for a, s in SECONDS_PER_ROW.items()},
            "wall_minutes_at_this_worker_count": {
                a: round(N_ROWS * s / 60 / n_workers, 1)
                for a, s in SECONDS_PER_ROW.items()}}
    log(json.dumps(info, indent=2))
    return info


def run(arm, out_dir=DEFAULT_OUT, *, budget=BUDGET, mrl=MRL, rows_csv=None,
        workers="auto", chunks=1, chunk_index=1, limit=None, resume=True,
        rlimit_gb=WORKER_RLIMIT_GB, expect=N_ROWS, log=print):
    key, spec = resolve_arm(arm)
    if key not in ARM_CHOICES:
        raise SystemExit(f"arm {key!r} is not one of {ARM_CHOICES}")
    if not HAVE_HCOMPACT:
        # No silent Python fallback. A 72,779-row sweep on the reference
        # implementation is a different cost and a different provenance, and
        # it must be a decision someone made rather than one a failed import
        # made for them.
        raise SystemExit(
            "hcompact is not importable, and this runner will not fall back to "
            "the Python reference. Build the engine first (see perf_lab/RUNBOOK.md).")
    rows = stride_chunk(load_rows(rows_csv, expect=expect), chunks, chunk_index)
    if limit:
        rows = rows[:int(limit)]
    os.makedirs(out_dir, exist_ok=True)
    path = out_path(key, out_dir, chunks, chunk_index, budget, mrl)
    seen = done_names(path) if resume else set()
    todo = [r for r in rows if r["name"] not in seen]
    n_workers = resolve_workers(workers)

    log(f"  campaign : {CAMPAIGN} / {key} -- {spec['label']}")
    log(f"  input    : {rows_csv or ROWS_CSV}")
    log(f"  budget   : {budget:,} nodes, cap {mrl}")
    log(f"  engine   : hcompact (packed arena, numba)")
    log(f"  rows     : {len(rows):,} in this chunk "
        f"({chunk_index} of {chunks}), {len(seen):,} done, {len(todo):,} to run")
    log(f"  workers  : {n_workers} (rlimit {rlimit_gb} GB address space each)")
    log(f"  out      : {path}")
    if not todo:
        log("  nothing to do")
        return path

    rlimit = int(rlimit_gb * 2 ** 30)
    # `_job` is run_leftovers_1m's, called verbatim: same arm dispatch, same
    # cache hygiene, same record. That is what makes this file spliceable onto
    # the 100k rung rather than merely similar to it. heartbeat_secs is large
    # because at 20-30 ms a row the in-search heartbeat can only be noise.
    jobs = [(key, r, budget, mrl, 3600.0) for r in todo]
    started = time.time()
    written = 0
    _ensure_trailing_newline(path)
    ctx = mp.get_context("fork")
    with open(path, "a") as fh:
        if n_workers == 1:
            _init_worker(rlimit)
            stream = (_job(j) for j in jobs)
            pool = None
        else:
            pool = ctx.Pool(n_workers, initializer=_init_worker,
                            initargs=(rlimit,))
            # Every worker must get several chunks: a flat chunksize hands all
            # of a short list to one worker and starves the rest.
            chunksize = max(1, min(64, len(jobs) // (n_workers * 8)))
            stream = pool.imap_unordered(_job, jobs, chunksize=chunksize)
        try:
            for record in stream:
                fh.write(json.dumps(record) + "\n")
                written += 1
                if written % 2000 == 0:
                    fh.flush()
                    rate = written / max(1e-9, time.time() - started)
                    left = (len(jobs) - written) / max(1e-9, rate) / 60
                    log(f"  {written:,}/{len(jobs):,}  {rate:.1f} rows/s  "
                        f"~{left:.1f} min left")
        finally:
            if pool is not None:
                pool.close()
                pool.join()
        fh.flush()
    log(f"  wrote {written:,} rows in {(time.time() - started) / 60:.2f} min")
    return path


def _all_records(arm, out_dir=DEFAULT_OUT, chunks=1, budget=BUDGET, mrl=MRL):
    """Every record for this arm, over every chunk file, newest-wins by name."""
    key, _ = resolve_arm(arm)
    by_name = {}
    paths = [out_path(key, out_dir, 1, 1, budget, mrl)]
    if chunks and chunks > 1:
        paths = [out_path(key, out_dir, chunks, i, budget, mrl)
                 for i in range(1, chunks + 1)]
    for p in paths:
        for r in read_rows(p):
            if "name" in r and not r.get("error"):
                by_name[r["name"]] = r
    return by_name


def verify(arm, out_dir=DEFAULT_OUT, chunks=1, budget=BUDGET, mrl=MRL,
           log=print):
    """The archived 10k failure list is the correctness oracle for this re-run.

    Every row in ``unsolved_10k_<arm>.csv`` was searched at exactly this budget
    and this cap by the original wave and did NOT solve, running the full
    10,000 pops. A faithful re-run must reproduce that on every one of them --
    same verdict AND the same node count -- because the search is deterministic
    and every engine change since has been gated bit-identical.

    A row on that list that now SOLVES is not a happy surprise. It means the
    search being run is not the search that built the archive, and splicing
    this file onto the 100k/1M/5M rungs would then compare two different
    experiments. That is a stop, not a warning.

    The converse is allowed and expected in one direction only: the original
    wave judged 71,556 of the 72,779 orbits on the greedy arm and 71,582 on
    s20_mk2, so this run may fail on rows the archive never saw. That licence
    is bounded, not open: at most 1,223 (greedy) / 1,197 (s20_mk2) rows sit in
    the gap, so more extra failures than that is not a coverage difference.
    """
    key, _ = resolve_arm(arm)
    recs = _all_records(key, out_dir, chunks, budget, mrl)
    if not recs:
        raise SystemExit(f"no records for arm {key} under {out_dir}")
    oracle_path = os.path.join(SCREEN_DIR, ORACLE_CSV[key])
    with open(oracle_path, newline="") as fh:
        oracle = {r["name"]: int(r["nodes_explored"]) for r in csv.DictReader(fh)}

    missing, now_solved, wrong_nodes = [], [], []
    for name, nodes in oracle.items():
        rec = recs.get(name)
        if rec is None:
            missing.append(name)
            continue
        if rec.get("solved"):
            now_solved.append((name, rec["nodes_explored"]))
        elif int(rec["nodes_explored"]) != nodes:
            wrong_nodes.append((name, nodes, int(rec["nodes_explored"])))

    new_fail = {n for n, r in recs.items() if not r.get("solved")}
    gap = N_ROWS - ARCHIVED_COVERAGE[key]
    extra = new_fail - set(oracle)
    log(f"  arm            : {key}")
    log(f"  records        : {len(recs):,}")
    log(f"  oracle         : {oracle_path} ({len(oracle):,} archived failures)")
    log(f"  reproduced     : {len(oracle) - len(now_solved) - len(missing):,}")
    log(f"  not yet run    : {len(missing):,}")
    log(f"  failures now   : {len(new_fail):,} "
        f"({len(extra):,} outside the archived list; the wave never judged "
        f"{gap:,} of the {N_ROWS:,} orbits)")
    ok = True
    if now_solved:
        ok = False
        log(f"  !! {len(now_solved)} archived failure(s) now SOLVE, e.g. "
            f"{now_solved[:5]} -- the engine or the arm has diverged from the "
            "run that built the archive. STOP: do not splice this file onto "
            "the 100k/1M/5M rungs.")
    if len(extra) > gap:
        ok = False
        log(f"  !! {len(extra):,} failures outside the archived list, but only "
            f"{gap:,} orbits were ever outside it. The surplus cannot be "
            "explained by coverage.")
    if wrong_nodes:
        ok = False
        log(f"  !! {len(wrong_nodes)} archived failure(s) ran a different node "
            f"count, e.g. {wrong_nodes[:5]} -- same verdict, different search.")
    if ok and not missing:
        log("  OK: every archived failure reproduced, verdict and node count.")
    elif ok:
        log("  OK so far: no divergence in the rows run to date.")
    return {"ok": ok, "n_records": len(recs), "n_oracle": len(oracle),
            "missing": len(missing), "now_solved": now_solved,
            "wrong_nodes": wrong_nodes,
            "new_failures": len(new_fail),
            "failures_outside_archive": len(extra),
            "coverage_gap": gap}


def report(arm, out_dir=DEFAULT_OUT, chunks=1, budget=BUDGET, mrl=MRL,
           rungs=(1_000, 10_000), log=print):
    """Solved counts, and the smaller rungs read off the same run for free."""
    key, _ = resolve_arm(arm)
    recs = _all_records(key, out_dir, chunks, budget, mrl)
    solved = [r for r in recs.values() if r.get("solved")]
    costs = sorted(int(r["nodes_explored"]) for r in solved)
    info = {"arm": key, "records": len(recs), "solved": len(solved),
            "unsolved": len(recs) - len(solved),
            "anytime": {c: sum(1 for x in costs if x <= c) for c in rungs},
            "mean_nodes_solved": round(sum(costs) / len(costs), 1) if costs else None,
            "median_nodes_solved": costs[len(costs) // 2] if costs else None,
            "p90_nodes_solved": costs[int(0.9 * len(costs))] if costs else None,
            "max_nodes_solved": costs[-1] if costs else None}
    log(json.dumps(info, indent=2))
    return info


def costs(out_dir=DEFAULT_OUT, chunks=1, budget=BUDGET, mrl=MRL, log=print):
    """Derive the small per-row CSV the deck actually reads.

    The jsonls carry the provenance; this is the join key. One row per
    (arm, presentation), with the two fields every figure in the deck asks for.
    """
    path = os.path.join(out_dir, f"{CAMPAIGN}_costs.csv")
    n = 0
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["name", "arm", "solved", "nodes_explored", "path_length",
                    "budget", "max_relator_length"])
        for arm in ARM_CHOICES:
            for name, r in sorted(_all_records(arm, out_dir, chunks, budget,
                                               mrl).items()):
                w.writerow([name, arm, int(bool(r["solved"])),
                            r["nodes_explored"], r["path_length"],
                            r["budget"], r["max_relator_length"]])
                n += 1
    log(f"  wrote {n:,} rows -> {path}")
    return path


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("command",
                    choices=("plan", "smoke", "run", "verify", "report", "costs"))
    ap.add_argument("--arm", choices=ARM_CHOICES)
    ap.add_argument("--out-dir", default=DEFAULT_OUT)
    ap.add_argument("--rows-csv", default=None)
    ap.add_argument("--workers", default="auto")
    ap.add_argument("--chunks", type=int, default=1)
    ap.add_argument("--chunk-index", type=int, default=1)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--budget", type=int, default=BUDGET)
    ap.add_argument("--mrl", type=int, default=MRL)
    a = ap.parse_args(argv)

    if a.command == "plan":
        plan(a.workers)
        return 0
    if a.command == "costs":
        costs(a.out_dir, a.chunks, a.budget, a.mrl)
        return 0
    if not a.arm:
        raise SystemExit(f"--arm is required for `{a.command}`")
    if a.command == "smoke":
        # 200 rows into a *_smoke directory: proves the pipeline end to end
        # without writing a row into the campaign's own file.
        run(a.arm, a.out_dir + "_smoke", budget=a.budget, mrl=a.mrl,
            rows_csv=a.rows_csv, workers=a.workers, limit=200, expect=None)
        return 0
    if a.command == "run":
        run(a.arm, a.out_dir, budget=a.budget, mrl=a.mrl, rows_csv=a.rows_csv,
            workers=a.workers, chunks=a.chunks, chunk_index=a.chunk_index,
            limit=a.limit)
        return 0
    if a.command == "verify":
        got = verify(a.arm, a.out_dir, a.chunks, a.budget, a.mrl)
        return 0 if got["ok"] else 1
    report(a.arm, a.out_dir, a.chunks, a.budget, a.mrl)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
