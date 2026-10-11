"""Dataset and benchmark loaders. Every loader returns a list of ``Row(id, pres, meta)``.

* ``load(name_or_path, ids=None)``: the flat-int ``.txt`` datasets in ``data/``
  (one zero-padded ``[r1 | r2]`` list or tuple per line; ``.gz`` read
  transparently). ``id`` is the 0-based line index as a string; ``ids``
  selects lines (in the order given).
* ``load_csv(path)``: benchmark CSVs with ``r1``/``r2`` string columns
  (``benchmark/subsets/benchmark_subset_*.csv``: ``pres_id`` = MS640 line;
  ``benchmark/ladder/ladder_*.csv``: ``name``, ``level`` 1..10, ...). ``id`` is
  ``name`` if present, else ``pres_id``, else the row index; ``meta`` holds
  every other column as the raw string.
* ``load_split(path, part)``: a split JSON holding ``<part>_rows`` with ``idx``,
  ``r1``, ``r2`` (``splits_ac1m_hard_aut.json``: ``part = "holdout"`` is the
  60-row Aut-disjoint holdout).
* ``rows(name)``: any of the above by name (``DATASETS``, ``BENCHMARKS``,
  ``SPLITS``) or by path; what ``run.py`` uses.
* ``MS(n, w)`` and ``AK(n)``: the Miller-Schupp and Akbulut-Kirby families
  (``origin/main:greedy_search.ipynb``).
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
    p = table.get(name_or_path, name_or_path)
    return p if os.path.isabs(p) else os.path.join(ROOT, p)


def parse_line(line, n_rel=2):
    ints = [int(t) for t in line.strip().strip("[]()").split(",") if t.strip()]
    return Presentation.from_flat(ints, n_rel=n_rel)


def load(name_or_path, ids=None, n_rel=2):
    p = path_of(name_or_path)
    with _open(p) as f:
        lines = [ln for ln in f if ln.strip()]
    pick = range(len(lines)) if ids is None else [int(i) for i in ids]
    return [Row(str(i), parse_line(lines[i], n_rel), {}) for i in pick]


def _open(p):
    return gzip.open(p, "rt", newline="") if p.endswith(".gz") else open(p, newline="")


def load_csv(name_or_path):
    with _open(path_of(name_or_path, BENCHMARKS)) as f:
        rows = list(csv.DictReader(f))
    out = []
    for k, r in enumerate(rows):
        rid = r.get("name") or r.get("pres_id") or str(k)
        meta = {c: v for c, v in r.items() if c not in ("r1", "r2")}
        out.append(Row(rid, Presentation.parse(r["r1"], r["r2"]), meta))
    return out


def load_split(path, part="holdout"):
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
    raise KeyError(f"unknown benchmark {name_or_path!r}; names: {sorted(DATASETS) + sorted(BENCHMARKS) + sorted(SPLITS)}")


def MS(n, w):
    """Miller-Schupp ``<x, y | x^-1 y^n x = y^(n+1), x = w>`` with ``w`` a word in x, y."""
    return Presentation.parse("X" + "y" * n + "x" + "Y" * (n + 1), "X" + w)


def AK(n):
    """Akbulut-Kirby ``<x, y | xyx = yxy, x^n = y^(n+1)>``."""
    return Presentation.parse("xyxYXY", "x" * n + "Y" * (n + 1))
