"""Dataset and benchmark loaders; each returns a list of ``Row(id, pres, meta)``.

``rows(name)`` reads any dataset, benchmark or split by name (``DATASETS``, ``BENCHMARKS``, ``SPLITS``) or path.
``MS`` and ``AK`` build the Miller-Schupp and Akbulut-Kirby presentations.
"""
import csv
import gzip
import json
import os
from collections import namedtuple

from .core.words import Presentation

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

Row = namedtuple("Row", "id pres meta")

DATASETS = {
    "ms640": "data/ms640_solved.txt",
    "ms_unsolved": "data/ms_unsolved_reps/ms_reps_unsolved.txt",
    "1190ms": "data/1190MS.txt",
    "ac19": "data/AC19.txt",
    "ac19_extended": "data/AC19_extended.txt",
    "ac1m": "data/AC1M.txt.gz",
}

BENCHMARKS = {
    **{f"bench{n}": f"benchmark/subsets/benchmark_subset_{n}.csv" for n in (10, 20, 40, 60)},
    **{f"ladder{n}": f"benchmark/ladder/ladder_{n}.csv" for n in (20, 40, 60, 100, 200, 300, 500)},
    **{f"ladder{n}_s20hard": f"benchmark/ladder/ladder_{n}_s20hard.csv" for n in (20, 40, 60, 100, 200, 300)},
    "ac19_autmin": "data/AC19_extended_aut_min.csv",
    "ac1m_autmin": "data/AC1M_aut_min.csv.gz",
    "u124": "data/ms_unsolved_reps/aca_124_initial.csv",
}

SPLITS = {"ac1m_hard_holdout60": ("benchmark/splits/splits_ac1m_hard_aut.json", "holdout")}


def path_of(name_or_path, table=DATASETS):
    """The file of a dataset name in ``table``, or of a path (relative paths are relative to the repository root)."""
    p = table.get(name_or_path, name_or_path)
    return p if os.path.isabs(p) else os.path.join(ROOT, p)


def _open(p):
    """Text file handle of ``p``, gunzipped if it ends in ``.gz``."""
    return gzip.open(p, "rt", newline="") if p.endswith(".gz") else open(p, newline="")


def parse_line(line):
    """One dataset line, a zero-padded flat list or tuple of ints ``[r1 | r2]``, as a ``Presentation``."""
    ints = [int(t) for t in line.strip().strip("[]()").split(",") if t.strip()]
    return Presentation.from_flat(ints)


def load(name_or_path, ids=None):
    """A flat-int ``.txt`` dataset (``.gz`` read transparently), one presentation per line. A row's ``id`` is its
    0-based line index as a string; ``ids`` selects lines, in the order given."""
    with _open(path_of(name_or_path)) as f:
        lines = [ln for ln in f if ln.strip()]
    pick = range(len(lines)) if ids is None else [int(i) for i in ids]
    return [Row(str(i), parse_line(lines[i]), {}) for i in pick]


def load_csv(name_or_path):
    """A benchmark CSV with ``r1``/``r2`` string columns. A row's ``id`` is its ``name`` column if present, else
    ``pres_id``, else the row index; ``meta`` holds every other column as a raw string."""
    with _open(path_of(name_or_path, BENCHMARKS)) as f:
        rows = list(csv.DictReader(f))
    out = []
    for k, r in enumerate(rows):
        rid = r.get("name") or r.get("pres_id") or str(k)
        meta = {c: v for c, v in r.items() if c not in ("r1", "r2")}
        out.append(Row(rid, Presentation.parse(r["r1"], r["r2"]), meta))
    return out


def load_split(path, part="holdout"):
    """The ``<part>_rows`` of a split JSON (entries with ``idx``, ``r1``, ``r2``, ...); ``id`` is ``idx``."""
    with open(path_of(path)) as f:
        rows = json.load(f)[f"{part}_rows"]
    return [Row(str(r["idx"]), Presentation.parse(r["r1"], r["r2"]),
                {k: v for k, v in r.items() if k not in ("idx", "r1", "r2")}) for r in rows]


def rows(name_or_path):
    """Rows of a dataset, benchmark CSV or split, by name or by path (``.txt``/``.csv``, optionally ``.gz``)."""
    if name_or_path in SPLITS:
        return load_split(*SPLITS[name_or_path])
    if name_or_path in DATASETS:
        return load(name_or_path)
    if name_or_path in BENCHMARKS or ".csv" in name_or_path:
        return load_csv(name_or_path)
    if name_or_path.endswith((".txt", ".txt.gz")):
        return load(name_or_path)
    names = sorted(DATASETS) + sorted(BENCHMARKS) + sorted(SPLITS)
    raise KeyError(f"unknown benchmark {name_or_path!r}; names: {names}")


def MS(n, w):
    """Miller-Schupp ``<x, y | x^-1 y^n x = y^(n+1), x = w>`` with ``w`` a word in x, y."""
    return Presentation.parse("X" + "y" * n + "x" + "Y" * (n + 1), "X" + w)


def AK(n):
    """Akbulut-Kirby ``<x, y | xyx = yxy, x^n = y^(n+1)>``."""
    return Presentation.parse("xyxYXY", "x" * n + "Y" * (n + 1))
