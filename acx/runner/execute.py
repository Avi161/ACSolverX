"""Solving the rows of a config: workers, resume and ``summary.json`` (the run folder itself: ``rundir``)."""
import json
import os
import time
from contextlib import nullcontext, suppress
from multiprocessing import Pool

from .. import data
from ..verify.replay import ReplayError, abs_det
from .methods import SOLVERS, record
from .output import shape
from .rundir import drop_changed, prepare, pres_text, read_records
from .summary import summarize

WARM_UP = data.parse_presentation("xxYYY, xyxYXY")     # AK(2): a short solve that every method can take


def _unsolvable(pres):
    """Why no AC path starts from ``pres`` (``|det| != 1``, or not balanced), None when one may exist."""
    try:
        det = abs_det(pres)
    except ReplayError as e:
        return str(e)
    return None if det == 1 else f"|det| = {det}, not AC-trivial"


def _solve_row(args):
    """``(cfg, row)`` -> the row's record, shaped by the config's ``path`` and ``fields``.

    A row no AC path can start from, and a row whose method raises, are unsolved records with an ``error``
    (``Type: message``): one bad row does not end the run. ``cpu_seconds`` is this process's CPU time for the row.
    """
    cfg, row = args
    wall, cpu = time.perf_counter(), time.process_time()
    try:
        why = _unsolvable(row.pres)
        rec = record(False, error=why) if why else SOLVERS[cfg["method"]](row.pres, cfg)
    except Exception as e:
        rec = record(False, error=f"{type(e).__name__}: {e}")
    return shape({"id": row.id, "pres": pres_text(row.pres), **rec, "seconds": round(time.perf_counter() - wall, 4),
                  "cpu_seconds": round(time.process_time() - cpu, 6)}, cfg)


def warm_up(cfg):
    """Solve ``WARM_UP`` once, unrecorded, so that compiling the numba kernels (or loading the rl policy) is not
    timed in the first row. A warm-up that raises is skipped: the rows record their own errors."""
    with suppress(Exception):
        SOLVERS[cfg["method"]](WARM_UP, cfg)


def _solve_rows(cfg, todo, done, paths_file, log):
    """Solve ``todo`` (in ``cfg["workers"]`` processes, each warmed up first), appending each record to
    ``paths_file`` and ``done``."""
    workers = cfg.get("workers", 1)
    jobs = [(cfg, row) for row in todo]
    if workers == 1:
        warm_up(cfg)
    solved = 0
    pool = Pool(workers, initializer=warm_up, initargs=(cfg,)) if workers > 1 else nullcontext()
    with open(paths_file, "a") as f, pool:
        for n, rec in enumerate(pool.imap(_solve_row, jobs) if workers > 1 else map(_solve_row, jobs), 1):
            done[rec["id"]] = rec
            f.write(json.dumps(rec) + "\n")
            f.flush()
            solved += rec["solved"]
            if n % 50 == 0 or n == len(todo):
                log(f"  {n}/{len(todo)} rows, {solved} solved")


def run(cfg, out="results", fresh=False, log=print):
    """Run ``cfg`` over its rows and return the summary.

    Writes ``<out>/<name>/``: ``config.json``, ``paths.jsonl`` (one record per row, flushed as it is solved) and
    ``summary.json``. Rows already in ``paths.jsonl`` with the same presentation are skipped, so an interrupted run
    resumes and a run under another config (``path`` and ``fields`` included) needs ``fresh`` or another name; the
    summary covers every record in ``paths.jsonl``, error rows included (a row that raised is recorded, not retried
    on resume). The record fields are in ``acx.runner.methods.record`` and ``acx.runner.output``.
    """
    if cfg["method"] == "rl":
        try:
            import torch  # noqa: F401
        except ModuleNotFoundError:
            raise SystemExit("method 'rl' needs PyTorch: pip install -e .[rl]") from None
    if cfg["method"] == "rankn":
        from ..ngen.sweep import run as run_rankn
        return run_rankn(cfg, out, fresh, log)
    every_row = data.rows(cfg["benchmark"])
    rows = data.select(every_row, cfg.get("rows"))
    run_dir = os.path.join(out, cfg["name"])
    paths_file = prepare(run_dir, cfg, fresh, len(rows))
    done = {}
    if os.path.exists(paths_file):
        done = {rec["id"]: rec for rec in read_records(paths_file, repair=True)}
    drop_changed(done, every_row, paths_file)
    todo = [r for r in rows if r.id not in done]
    log(f"{cfg['name']}: {cfg['method']} on {cfg['benchmark']}, {len(rows)} rows ({len(rows) - len(todo)} done)")
    start = time.perf_counter()
    if todo:
        _solve_rows(cfg, todo, done, paths_file, log)
    summary = summarize(cfg, list(done.values()), time.perf_counter() - start)
    with open(os.path.join(run_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1)
    return summary
