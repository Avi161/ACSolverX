"""Solving the rows of a config and writing ``results/<name>/``: row selection, workers, resume, summary."""
import json
import os
import re
import time
from contextlib import nullcontext, suppress
from multiprocessing import Pool

from .. import data
from ..verify.replay import ReplayError, abs_det
from .config import run_config
from .methods import SOLVERS, record
from .output import shape
from .summary import summarize

SLICE = re.compile(r"-?\d*:-?\d*(:-?\d*)?")     # integers around colons; anything else (``ms:1``) is an id
WARM_UP = data.parse_presentation("xxYYY, xyxYXY")     # AK(2): a short solve that every method can take


def select(rows, spec):
    """``rows`` sliced by ``"a:b[:c]"`` or picked by comma-separated ids (a repeated id once, first place)."""
    if spec in (None, ""):
        return rows
    spec = str(spec).strip()
    if SLICE.fullmatch(spec):
        try:
            return rows[slice(*(int(t) if t else None for t in spec.split(":")))]
        except ValueError:                                       # a step of 0
            raise ValueError(f"bad rows slice {spec!r}: write integers as a:b or a:b:c, the step not 0") from None
    ids = list(dict.fromkeys(i.strip() for i in spec.split(",")))
    by_id = {r.id: r for r in rows}
    missing = [i for i in ids if i not in by_id]
    if missing:
        raise KeyError(f"rows not in the benchmark: {missing}")
    return [by_id[i] for i in ids]


def pres_text(pres):
    """A record's ``pres``: the presentation as a LETTERS line, ``"xxYYY, xyxYXY"``."""
    return ", ".join(pres.strs)


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


def _load_done(paths_file):
    """The records in ``paths_file`` by id. A cut-off last line (an interrupted write) is dropped from the file; a
    bad line with more lines after it raises ``ValueError``."""
    with open(paths_file, "rb") as f:
        lines = f.readlines()
    done, good_bytes = {}, 0
    for number, line in enumerate(lines, 1):
        try:
            rec = json.loads(line) if line.endswith(b"\n") else None
        except ValueError:
            rec = None
        if rec is None:
            if number < len(lines):
                raise ValueError(f"{paths_file}:{number}: not a record; fix or delete the line, then run again")
            break
        done[rec["id"]] = rec
        good_bytes += len(line)
    with open(paths_file, "r+b") as f:
        f.truncate(good_bytes)
    return done


def _drop_changed(done, rows, paths_file):
    """Forget the records of rows that left the benchmark or now hold another presentation (the input file changed),
    in ``done`` and in ``paths_file``; ``rows`` is every row, selected or not. A record without ``pres`` is kept."""
    by_id = {r.id: r.pres for r in rows}
    changed = [i for i, rec in done.items()
               if i not in by_id or rec.get("pres", pres_text(by_id[i])) != pres_text(by_id[i])]
    if changed:
        for row_id in changed:
            del done[row_id]
        with open(paths_file, "w") as f:
            f.writelines(json.dumps(rec) + "\n" for rec in done.values())


def _prepare_run_dir(run_dir, cfg, fresh, n_rows):
    """Create ``run_dir`` and write its ``config.json``; return the ``paths.jsonl`` path.

    ``fresh`` clears the earlier results. Otherwise these are refused: a folder holding a run under another config, a
    ``paths.jsonl`` without its ``config.json`` (its config is unknown), and a run of fewer rows into a published
    folder (``summary.json`` without ``paths.jsonl``), which it would replace.
    """
    os.makedirs(run_dir, exist_ok=True)
    paths_file = os.path.join(run_dir, "paths.jsonl")
    config_file = os.path.join(run_dir, "config.json")
    summary_file = os.path.join(run_dir, "summary.json")
    if fresh:
        for name in (paths_file, config_file, summary_file):
            if os.path.exists(name):
                os.remove(name)
    if os.path.exists(summary_file) and not os.path.exists(paths_file):
        with open(summary_file) as f:
            published = json.load(f).get("rows", 0)
        if n_rows < published:
            raise SystemExit(f"{run_dir} holds published results of {published} rows: a run of {n_rows} would replace "
                             "them; pass --fresh or another name")
    if os.path.exists(paths_file) and not os.path.exists(config_file):
        raise SystemExit(f"{run_dir} holds paths.jsonl without its config.json, so its records may be of another "
                         "config: pass --fresh or another name")
    config = run_config(cfg)
    if os.path.exists(config_file):
        with open(config_file) as f:
            if json.load(f) != config:
                raise SystemExit(f"{run_dir} holds a run with another config: pass --fresh or another name")
    with open(config_file, "w") as f:
        json.dump(config, f, indent=1)
    return paths_file


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
    rows = select(every_row, cfg.get("rows"))
    run_dir = os.path.join(out, cfg["name"])
    paths_file = _prepare_run_dir(run_dir, cfg, fresh, len(rows))
    done = _load_done(paths_file) if os.path.exists(paths_file) else {}
    _drop_changed(done, every_row, paths_file)
    todo = [r for r in rows if r.id not in done]
    log(f"{cfg['name']}: {cfg['method']} on {cfg['benchmark']}, {len(rows)} rows ({len(rows) - len(todo)} done)")
    start = time.perf_counter()
    if todo:
        _solve_rows(cfg, todo, done, paths_file, log)
    summary = summarize(cfg, list(done.values()), time.perf_counter() - start)
    with open(os.path.join(run_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1)
    return summary
