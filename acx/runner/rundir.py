"""A run folder, ``<out>/<name>/``: the ``config.json`` guard, the records of ``paths.jsonl``, and what a resume keeps.

The runner, the rank-n sweep (``write_config``) and ``run.py`` (``--solved-from`` and the report of ``--pres``) read
and guard a folder through these functions, so a cut-off or damaged ``paths.jsonl`` reads the same way everywhere.
"""
import json
import os

from .config import run_config


def pres_text(pres):
    """A record's ``pres``: the presentation as a LETTERS line, ``"xxYYY, xyxYXY"``."""
    return ", ".join(pres.strs)


def write_config(run_dir, config):
    """Write ``config`` to ``<run_dir>/config.json``; refuse a folder that holds a run under another config."""
    config_file = os.path.join(run_dir, "config.json")
    if os.path.exists(config_file):
        with open(config_file) as f:
            if json.load(f) != config:
                raise SystemExit(f"{run_dir} holds a run with another config: pass --fresh or another name")
    with open(config_file, "w") as f:
        json.dump(config, f, indent=1)


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


def read_records(path, repair=False):
    """The records of a ``paths.jsonl``, in file order.

    A cut-off last line (a run stopped mid-write) is skipped; ``repair`` also cuts it from the file, so that the
    records a resume appends start on a line of their own. A bad line with lines after it raises ``ValueError``.
    """
    with open(path, "rb") as f:
        lines = f.readlines()
    records = []
    for number, line in enumerate(lines, 1):
        rec = _parse(line)
        if rec is None and number < len(lines):
            raise ValueError(f"{path}:{number}: not a record; fix or delete the line, then run again")
        if rec is not None:
            records.append(rec)
    if repair and len(records) < len(lines):
        with open(path, "r+b") as f:
            f.truncate(sum(map(len, lines[:-1])))
    return records


def drop_changed(done, rows, paths_file):
    """Forget, in ``done`` (records by id) and in ``paths_file``, the records whose row left ``rows`` (every row,
    selected or not) or now holds another presentation. A record without ``pres`` is kept while its row is there."""
    pres_of = {r.id: r.pres for r in rows}

    def is_stale(row_id, rec):
        if row_id not in pres_of:
            return True                                     # the row left the input
        return "pres" in rec and rec["pres"] != pres_text(pres_of[row_id])

    stale = [row_id for row_id, rec in done.items() if is_stale(row_id, rec)]
    if stale:
        for row_id in stale:
            del done[row_id]
        with open(paths_file, "w") as f:
            f.writelines(json.dumps(rec) + "\n" for rec in done.values())
