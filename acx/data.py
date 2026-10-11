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
    "bench10": "benchmark/subsets/benchmark_subset_10.csv",
    "bench20": "benchmark/subsets/benchmark_subset_20.csv",
    "bench40": "benchmark/subsets/benchmark_subset_40.csv",
    "bench60": "benchmark/subsets/benchmark_subset_60.csv",
    "ladder60": "benchmark/ladder/ladder_60.csv",
    "ladder100": "benchmark/ladder/ladder_100.csv",
    "ladder200": "benchmark/ladder/ladder_200.csv",
}


def path_of(name_or_path, table=DATASETS):
    p = table.get(name_or_path, name_or_path)
    return p if os.path.isabs(p) else os.path.join(ROOT, p)


def parse_line(line, n_rel=2):
    ints = [int(t) for t in line.strip().strip("[]()").split(",") if t.strip()]
    return Presentation.from_flat(ints, n_rel=n_rel)


def load(name_or_path, ids=None, n_rel=2):
    p = path_of(name_or_path)
    with (gzip.open(p, "rt") if p.endswith(".gz") else open(p)) as f:
        lines = [ln for ln in f if ln.strip()]
    pick = range(len(lines)) if ids is None else [int(i) for i in ids]
    return [Row(str(i), parse_line(lines[i], n_rel), {}) for i in pick]


def load_csv(name_or_path):
    with open(path_of(name_or_path, BENCHMARKS), newline="") as f:
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
