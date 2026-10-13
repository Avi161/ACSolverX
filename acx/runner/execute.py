"""Solving the rows of a config and writing ``results/<name>/``: row selection, workers, resume, summary."""
import json
import os
import time
from contextlib import nullcontext
from multiprocessing import Pool

from .. import data
from ..verify.replay import ReplayError, abs_det
from .config import run_config
from .methods import SOLVERS, record
from .output import shape
from .summary import summarize


def select(rows, spec):
    """``rows`` sliced by ``"a:b[:c]"`` or picked by comma-separated ids (a repeated id once, first place)."""
    if spec in (None, ""):
        return rows
    spec = str(spec)
    if ":" in spec:
        try:
            return rows[slice(*(int(t) if t else None for t in spec.split(":")))]
        except (ValueError, TypeError):
            raise ValueError(f"bad rows slice {spec!r}: write integers as a:b or a:b:c, the step not 0") from None
    ids = list(dict.fromkeys(spec.split(",")))
    by_id = {r.id: r for r in rows}
    missing = [i for i in ids if i not in by_id]
    if missing:
        raise KeyError(f"rows not in the benchmark: {missing}")
    return [by_id[i] for i in ids]


def check_method(cfg):
    """Fail early with a clear message when an optional dependency is missing."""
    if cfg["method"] == "rl":
        try:
            import torch  # noqa: F401
        except ModuleNotFoundError:
            raise SystemExit("method 'rl' needs PyTorch: pip install -e .[rl]") from None


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
    return shape({"id": row.id, **rec, "seconds": round(time.perf_counter() - wall, 4),
                  "cpu_seconds": round(time.process_time() - cpu, 6)}, cfg)


def _load_done(paths_file):
    """The records in ``paths_file`` by id. A last line that is cut off (an interrupted write) is dropped."""
    done, good_bytes = {}, 0
    with open(paths_file, "rb") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except ValueError:
                break
            if not line.endswith(b"\n"):
                break
            done[rec["id"]] = rec
            good_bytes += len(line)
    with open(paths_file, "r+b") as f:
        f.truncate(good_bytes)
    return done


def _prepare_run_dir(run_dir, cfg, fresh):
    """Create ``run_dir`` and write its ``config.json``; return the ``paths.jsonl`` path.

    ``fresh`` clears the earlier results. Otherwise a folder holding a run under another config is refused.
    """
    os.makedirs(run_dir, exist_ok=True)
    paths_file = os.path.join(run_dir, "paths.jsonl")
    config_file = os.path.join(run_dir, "config.json")
    if fresh:
        for name in (paths_file, config_file, os.path.join(run_dir, "summary.json")):
            if os.path.exists(name):
                os.remove(name)
    config = run_config(cfg)
    if os.path.exists(config_file):
        with open(config_file) as f:
            if json.load(f) != config:
                raise SystemExit(f"{run_dir} holds a run with another config: pass --fresh or another name")
    with open(config_file, "w") as f:
        json.dump(config, f, indent=1)
    return paths_file


def _solve_rows(cfg, todo, done, paths_file, log):
    """Solve ``todo`` (in ``cfg["workers"]`` processes), appending each record to ``paths_file`` and ``done``."""
    workers = cfg.get("workers", 1)
    jobs = [(cfg, row) for row in todo]
    solved = 0
    with open(paths_file, "a") as f, (Pool(workers) if workers > 1 else nullcontext()) as pool:
        for n, rec in enumerate(pool.imap(_solve_row, jobs) if pool else map(_solve_row, jobs), 1):
            done[rec["id"]] = rec
            f.write(json.dumps(rec) + "\n")
            f.flush()
            solved += rec["solved"]
            if n % 50 == 0 or n == len(todo):
                log(f"  {n}/{len(todo)} rows, {solved} solved")


def run(cfg, out="results", fresh=False, log=print):
    """Run ``cfg`` over its rows and return the summary.

    Writes ``<out>/<name>/``: ``config.json``, ``paths.jsonl`` (one record per row, flushed as it is solved) and
    ``summary.json``. Rows already in ``paths.jsonl`` are skipped, so an interrupted run resumes and a run under
    another config (``path`` and ``fields`` included) needs ``fresh`` or another name; the summary covers every
    record in ``paths.jsonl``, error rows included (a row that raised is recorded, not retried on resume).
    The record fields are in ``acx.runner.methods.record`` and ``acx.runner.output``.
    """
    check_method(cfg)
    if cfg["method"] == "rankn":
        from ..ngen.sweep import run as run_rankn
        return run_rankn(cfg, out, fresh, log)
    rows = select(data.rows(cfg["benchmark"]), cfg.get("rows"))
    run_dir = os.path.join(out, cfg["name"])
    paths_file = _prepare_run_dir(run_dir, cfg, fresh)
    done = _load_done(paths_file) if os.path.exists(paths_file) else {}
    todo = [r for r in rows if r.id not in done]
    log(f"{cfg['name']}: {cfg['method']} on {cfg['benchmark']}, {len(rows)} rows ({len(rows) - len(todo)} done)")
    start = time.perf_counter()
    _solve_rows(cfg, todo, done, paths_file, log)
    summary = summarize(cfg, list(done.values()), time.perf_counter() - start)
    with open(os.path.join(run_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1)
    return summary
