"""Load finished runs: a ``results/<run>/`` folder becomes a ``Run``, read from its ``paths.jsonl`` or, for a
shipped folder, from its ``summary.json``."""
import json
from pathlib import Path
from typing import NamedTuple

from ..runner.summary import COST_UNIT

# The record fields the report reads, besides the ``*_would_pop`` cap flags; a record's other fields are dropped.
KEEP = {"id", "solved", "cost", "sub_moves", "elem_moves", "seconds", "cpu_seconds", "error"}


class Run(NamedTuple):
    """One results folder: its name, method, benchmark, the unit its ``cost`` counts, and its records; a folder
    without ``paths.jsonl`` (the shipped ``results/``) has ``records`` None and its ``summary.json`` as ``summary``."""
    name: str
    method: str
    benchmark: str
    unit: str
    records: list | None
    summary: dict | None = None


def read_json(path):
    """The object in a JSON file, ``{}`` when the file is missing."""
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        return {}


def read_records(path):
    """The records of a ``paths.jsonl``, cut down to the fields the report reads: the move lists are most of a big
    file. A last line cut off by a run still writing is skipped; any other line that is not JSON stops the report."""
    records, bad = [], None
    with open(path, encoding="utf-8") as lines:
        for number, line in enumerate(lines, 1):
            if not line.strip():
                continue
            if bad:                                      # a bad line with more lines after it is not a cut-off
                raise SystemExit(f"{path}: line {bad} is not JSON")
            try:
                record = json.loads(line)
            except ValueError:
                bad = number
            else:
                records.append({k: v for k, v in record.items() if k in KEEP or k.endswith("_would_pop")})
    return records


def load_run(folder):
    """The ``Run`` in a results folder; ``summary.json``, else ``config.json``, names its method and benchmark. A
    folder without ``paths.jsonl`` is read from its ``summary.json``, which must be one that run.py wrote."""
    folder = Path(folder).absolute()
    if not folder.is_dir():
        raise SystemExit(f"{folder}: not a folder")
    summary = read_json(folder / "summary.json")
    info = {**read_json(folder / "config.json"), **summary}
    method = info.get("method", "?")
    unit = info.get("cost_unit") or COST_UNIT.get(method, "pops")
    if (folder / "paths.jsonl").exists():
        return Run(folder.name, method, info.get("benchmark", "?"), unit, read_records(folder / "paths.jsonl"))
    if "solved" not in summary:
        raise SystemExit(f"{folder.name} has no paths.jsonl and no summary.json of run.py to compare")
    return Run(folder.name, method, info.get("benchmark", "?"), unit, None, summary)
