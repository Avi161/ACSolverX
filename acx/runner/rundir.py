"""A run folder, ``<out>/<name>/``: the ``config.json`` guard, the records of ``paths.jsonl``, and what a resume keeps.

The runner, the rank-n sweep (``write_config``) and ``run.py`` (``--solved-from`` and the report of ``--pres``) read
and guard a folder through these functions, so a cut-off or damaged ``paths.jsonl`` reads the same way everywhere.
"""
import json
import os

from .config import run_config
from .storage import atomic_write, write_json


def pres_text(pres):
    """A record's ``pres``: the presentation as a LETTERS line, ``"xxYYY, xyxYXY"``."""
    return ", ".join(pres.strs)


def check_config(run_dir, config):
    """Refuse a folder holding a different config, without changing it."""
    config_file = os.path.join(run_dir, "config.json")
    if os.path.exists(config_file):
        with open(config_file) as f:
            if json.load(f) != config:
                raise SystemExit(f"{run_dir} holds a run with another config: pass --fresh or another name")


def write_config(run_dir, config):
    """Write ``config`` to ``<run_dir>/config.json``; refuse a folder that holds a run under another config."""
    check_config(run_dir, config)
    write_json(os.path.join(run_dir, "config.json"), config)


def prepare(run_dir, cfg, fresh, n_rows):
    """Create ``run_dir`` and write its ``config.json``; return the ``paths.jsonl`` path.

    ``fresh`` clears the earlier results. Otherwise these are refused: a folder holding a run under another config, a
    ``paths.jsonl`` without its ``config.json`` (its config is unknown), and a run of fewer rows into a published
    folder (``summary.json`` without ``paths.jsonl``), which it would replace.
    """
    os.makedirs(run_dir, exist_ok=True)
    paths_file = os.path.join(run_dir, "paths.jsonl")
    config_file = os.path.join(run_dir, "config.json")
    summary_file = os.path.join(run_dir, "summary.json")
    for path in (paths_file, config_file, summary_file):
        if os.path.islink(path):
            raise ValueError(f"run output must not be a symlink: {path}")
    if fresh:
        for name in (paths_file, config_file, summary_file):
            if os.path.exists(name):
                os.remove(name)
    if os.path.exists(summary_file) and not os.path.exists(paths_file):
        with open(summary_file) as f:
            published = json.load(f).get("rows", 0)
        if n_rows < published:
            raise SystemExit(f"{run_dir} holds a published summary of {published} rows: a run of {n_rows} would "
                             "replace it; pass --fresh or another name")
    if os.path.exists(paths_file) and not os.path.exists(config_file):
        raise SystemExit(f"{run_dir} holds paths.jsonl without its config.json, so its records may be of another "
                         "config: pass --fresh or another name")
    write_config(run_dir, run_config(cfg))
    return paths_file


def _parse(line):
    """The record on a whole line (one that ends in a newline), else None."""
    if not line.endswith(b"\n"):
        return None
    try:
        return json.loads(line)
    except ValueError:
        return None


def iter_records(path, repair=False):
    """Stream records of a ``paths.jsonl``, in file order, ignoring blank lines.

    A cut-off last line (a run stopped mid-write) is skipped; ``repair`` also cuts it from the file, so that the
    records a resume appends start on a line of their own. A bad line with lines after it raises ``ValueError``.
    """
    cut = None
    first_line = {}
    with open(path, "rb") as f:
        line, number, offset = f.readline(), 1, 0
        while line:
            following = f.readline()
            if line.strip():
                rec = _parse(line)
                if rec is None:
                    if following:
                        raise ValueError(f"{path}:{number}: not a record; fix or delete the line, then run again")
                    cut = offset
                else:
                    if (not isinstance(rec, dict) or not isinstance(rec.get("id"), str)
                            or type(rec.get("solved")) is not bool
                            or ("pres" in rec and not isinstance(rec["pres"], str))):
                        raise ValueError(f"{path}:{number}: a record needs string id, boolean solved and optional string pres")
                    rid = rec["id"]
                    if rid in first_line:
                        raise ValueError(f"{path}:{number}: duplicate id {rid!r} (first on line {first_line[rid]})")
                    first_line[rid] = number
                    yield rec
            offset += len(line)
            line, number = following, number + 1
    if repair and cut is not None:
        with open(path, "r+b") as f:
            f.truncate(cut)


def read_records(path, repair=False):
    """Read all records using the same interrupted-write rules as the report and resume."""
    return list(iter_records(path, repair))


def drop_changed(done, rows, paths_file):
    """Forget, in ``done`` (records by id) and in ``paths_file``, the records whose row left ``rows`` (every row,
    selected or not) or now holds another presentation. A record without ``pres`` is kept while its row is there.
    The file keeps the other records as they are: ``done`` may hold them without their certificates."""
    pres_of = {r.id: r.pres for r in rows}

    def is_stale(row_id, rec):
        if row_id not in pres_of:
            return True                                     # the row left the input
        return "pres" in rec and rec["pres"] != pres_text(pres_of[row_id])

    stale = {row_id for row_id, rec in done.items() if is_stale(row_id, rec)}
    if stale:
        for row_id in stale:
            del done[row_id]
        kept = (json.dumps(rec) + "\n" for rec in iter_records(paths_file) if rec["id"] not in stale)
        atomic_write(paths_file, "".join(kept))
