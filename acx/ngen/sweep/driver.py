"""Run a sweep config over its rows, in worker processes, into a result directory."""
import json
import os
import shutil
import time
from contextlib import nullcontext
from multiprocessing import Pool

from ... import data
from .config import SweepConfig, words_of
from .rows import row_path, sweep_row_file
from .summary import summarize
from .words import combos


def open_result_dir(result_dir, key, fresh):
    """Create ``result_dir`` and write its ``config.json``; refuse a directory that holds another config."""
    if fresh:
        shutil.rmtree(result_dir, ignore_errors=True)
    os.makedirs(os.path.join(result_dir, "rows"), exist_ok=True)
    config_file = os.path.join(result_dir, "config.json")
    if os.path.exists(config_file):
        with open(config_file) as f:
            if json.load(f) != key:
                raise SystemExit(f"{result_dir} holds a run with another config: pass --fresh or another name")
    with open(config_file, "w") as f:
        json.dump(key, f, indent=1)


def run(cfg, out="results", fresh=False, log=print):
    """Sweep the selected rows of ``cfg`` into ``<out>/<name>/``; write and return the summary."""
    from ...runner import select
    sc = SweepConfig.from_cfg(cfg)
    rows = select(data.rows(cfg["benchmark"]), cfg.get("rows"))
    result_dir = os.path.join(out, cfg["name"])
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
