"""Run a sweep config over its rows, in worker processes, into a result directory."""
import json
import os
import shutil
import time
from contextlib import nullcontext
from multiprocessing import Pool

from ... import data
from ...runner.rundir import write_config
from .config import SweepConfig, words_of
from .rows import check_two_relators, finished_rows, row_path, sweep_row_file
from .summary import summarize
from .words import combos


def open_result_dir(result_dir, key, fresh):
    """Create ``result_dir`` and write its ``config.json``; refuse a directory that holds another config."""
    if fresh:
        shutil.rmtree(result_dir, ignore_errors=True)
    os.makedirs(os.path.join(result_dir, "rows"), exist_ok=True)
    write_config(result_dir, key)


def refuse_to_shrink(result_dir, row_ids):
    """Refuse a run whose summary would cover fewer rows than the summary published in ``result_dir`` (a shipped
    folder holds ``config.json`` and ``summary.*`` but not the row files)."""
    summary_file = os.path.join(result_dir, "summary.json")
    if not os.path.exists(summary_file):
        return
    try:
        with open(summary_file) as f:
            published = json.load(f).get("rows", 0)
    except ValueError:                  # cut off while it was written; the run rewrites it from rows/
        return
    rows_dir = os.path.join(result_dir, "rows")
    held = set(finished_rows(result_dir)) if os.path.isdir(rows_dir) else set()
    if len(held | set(row_ids)) < published:
        raise SystemExit(f"{result_dir} holds a published summary of {published} rows: a run of {len(row_ids)} would "
                         "replace it; pass --fresh or another name")


def run(cfg, out="results", fresh=False, log=print):
    """Sweep the selected rows of ``cfg`` into ``<out>/<name>/``; write and return the summary.

    Refused before anything is written: a row that is not two-generator, two-relator, and (unless ``fresh``) a run
    that would replace a published summary with one of fewer rows.
    """
    sc = SweepConfig.from_cfg(cfg)
    rows = data.select(data.rows(cfg["benchmark"]), cfg.get("rows"))
    check_two_relators(rows)
    result_dir = os.path.join(out, cfg["name"])
    if not fresh:
        refuse_to_shrink(result_dir, [row.id for row in rows])
    open_result_dir(result_dir, {"benchmark": cfg["benchmark"], "method": "rankn", "sweep": sc.key()}, fresh)

    n_words = len(words_of(sc))
    done = sum(os.path.exists(row_path(result_dir, r.id)) for r in rows)
    log(f"{cfg['name']}: rankn (extra {sc.extra}, lengths {sc.min_len}-{sc.max_len}, {n_words} words, "
        f"{len(combos(n_words, sc.extra))} starts per row) on {cfg['benchmark']}, {len(rows)} rows ({done} done)")

    began = time.perf_counter()
    workers = cfg.get("workers", 1)
    tasks = [(result_dir, r.id, r.pres, sc) for r in rows]
    with (Pool(workers) if workers > 1 else nullcontext()) as pool:
        run_tasks = map if pool is None else pool.imap_unordered
        for n, _ in enumerate(run_tasks(sweep_row_file, tasks), 1):
            if n % 50 == 0 or n == len(tasks):
                log(f"  {n}/{len(tasks)} rows")
    return summarize(result_dir, wall=time.perf_counter() - began)
