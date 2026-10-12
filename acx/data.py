"""Dataset and benchmark loaders; each returns a list of ``Row(id, pres, meta)``.

``rows(spec)`` reads a dataset, benchmark or split by name (``DATASETS``, ``BENCHMARKS``, ``SPLITS``), or your own
presentations from a file, optionally gzipped. Generators are ``x y z a b ...`` and upper case is the inverse; any
number of relators and generators is read (what a method can solve is up to the method)::

    mine.txt     xxYYY, xyxYXY             one presentation per line, relators split by commas or spaces;
                 xyxYXY xxxYYYY  # AK(3)   "#" starts a comment, blank lines are skipped (the flat-int lines
                                           of the shipped data/*.txt load too)
    mine.csv     id,r1,r2,note             relator columns r1..rN, empty cells skipped; the id is the "id", else
                 AK2,xxYYY,xyxYXY,easy     "name", else "pres_id" column; the other columns are the row's meta
    mine.jsonl   {"id": "AK2", "relators": ["xxYYY", "xyxYXY"], "note": "easy"}     other keys are the meta

A row's id is the one given, else its 0-based position among the file's presentations. A bad line raises
``ValueError("<file>:<line>: <what is wrong>")``, and a file that is not UTF-8 text ``ValueError("<file>: ...")``.
``MS`` and ``AK`` build the Miller-Schupp and Akbulut-Kirby families.
"""
import csv
import gzip
import json
import os
import re
from collections import namedtuple
from contextlib import contextmanager

from .core.words import GEN_CHARS, Presentation

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

_GENERATOR_LETTERS = set(GEN_CHARS + GEN_CHARS.upper())
_RELATOR_COLUMN = re.compile(r"r\d+")


def path_of(name_or_path, table=DATASETS):
    """The file of a name in ``table``, or of a path: as given if it exists, else relative to the repository root."""
    if name_or_path in table:
        return os.path.join(ROOT, table[name_or_path])
    return name_or_path if os.path.exists(name_or_path) else os.path.join(ROOT, name_or_path)


@contextmanager
def _open(p):
    """Text file handle of ``p``, gunzipped if it ends in ``.gz``; a leading byte-order mark is dropped. A file that
    is not UTF-8 text raises ``ValueError`` naming it, wherever in the file the bad byte is."""
    opener = gzip.open if p.lower().endswith(".gz") else open
    try:
        with opener(p, "rt", encoding="utf-8-sig", newline="") as f:
            yield f
    except UnicodeDecodeError:
        raise ValueError(f"{p}: not UTF-8 text (save the file as UTF-8)") from None


def _presentation(relators):
    """The ``Presentation`` of relator strings (empty ones are skipped); ``ValueError`` for a character that is not
    a generator letter, or when no relator is left."""
    if not all(isinstance(r, str) for r in relators):
        raise ValueError(f"relators must be strings, got {relators}")
    relators = [text for r in relators if (text := r.strip())]
    if not relators:
        raise ValueError("no relators")
    unknown = sorted(set("".join(relators)) - _GENERATOR_LETTERS)
    if unknown:
        raise ValueError(f"unknown letters {''.join(unknown)!r}: generators are x y z a b ... w, upper case inverts")
    return Presentation.parse(*relators)


def parse_presentation(text):
    """One LETTERS line such as ``"xxYYY, xyxYXY"``: relators split by commas or spaces, as a ``Presentation``."""
    return _presentation(text.replace(",", " ").split())


def parse_line(line):
    """One ``.txt`` line as a ``Presentation``: letters (``xxYYY, xyxYXY``) if it starts with a letter, else the flat
    layout of the shipped datasets, a zero-padded list or tuple of ints ``[r1 | r2]``."""
    if line.lstrip()[:1].isalpha():
        return parse_presentation(line)
    ints = [int(t) for t in line.strip().strip("[]()").split(",") if t.strip()]
    return Presentation.from_flat(ints)


@contextmanager
def _at(path, number):
    """Make a ``ValueError`` raised for line ``number`` of ``path`` say so: ``<path>:<number>: <message>``."""
    try:
        yield
    except ValueError as e:
        raise ValueError(f"{path}:{number}: {e}") from None


def load(name_or_path, ids=None):
    """A ``.txt`` file, one presentation per line (``parse_line``); blank lines are skipped and ``#`` starts a comment.
    A row's ``id`` is the 0-based position of its presentation as a string; ``ids`` selects them, in the order given."""
    path = path_of(name_or_path)
    with _open(path) as f:
        lines = [(n, text) for n, line in enumerate(f, 1) if (text := line.partition("#")[0].strip())]
    pick = range(len(lines)) if ids is None else [int(i) for i in ids]
    out = []
    for i in pick:
        number, text = lines[i]
        with _at(path, number):
            out.append(Row(str(i), parse_line(text), {}))
    return out


def _read(path, items, make):
    """The rows of ``(line number, raw)`` items, where ``make(raw)`` gives a line's ``(id, relators, meta)``. An id
    of ``None`` or ``""`` is the position; an id used before is an error."""
    rows, first_line = [], {}
    for number, raw in items:
        with _at(path, number):
            rid, relators, meta = make(raw)
            rid = str(rid) if rid not in (None, "") else str(len(rows))
            if rid in first_line:
                raise ValueError(f"duplicate id {rid!r} (first on line {first_line[rid]})")
            first_line[rid] = number
            rows.append(Row(rid, _presentation(relators), meta))
    return rows


def _csv_record(row, columns):
    """The ``(id, relators, meta)`` of a CSV row."""
    rid = row.get("id") or row.get("name") or row.get("pres_id")
    return rid, [row[c] or "" for c in columns], {c: v for c, v in row.items() if c not in columns}


def load_csv(name_or_path):
    """A CSV with relator columns ``r1..rN`` (empty cells are skipped). A row's ``id`` is its ``id``, ``name`` or
    ``pres_id`` column if present, else its position; ``meta`` holds every other column as a raw string."""
    path = path_of(name_or_path, BENCHMARKS)
    with _open(path) as f:
        reader = csv.DictReader(f, skipinitialspace=True)
        columns = sorted(filter(_RELATOR_COLUMN.fullmatch, reader.fieldnames or []), key=lambda c: int(c[1:]))
        if not columns:
            raise ValueError(f"{path}: no relator columns r1, r2, ... in the header {reader.fieldnames}")
        return _read(path, ((reader.line_num, row) for row in reader), lambda row: _csv_record(row, columns))


def _jsonl_record(line):
    """The ``(id, relators, meta)`` of a JSON line; the meta is the object's other keys."""
    obj = json.loads(line)
    if not (isinstance(obj, dict) and isinstance(obj.get("relators"), list)):
        raise ValueError('expected an object like {"id": "AK2", "relators": ["xxYYY", "xyxYXY"]}')
    return obj.pop("id", None), obj.pop("relators"), obj


def load_jsonl(name_or_path):
    """A JSON Lines file, one ``{"id": "AK2", "relators": ["xxYYY", "xyxYXY"], ...}`` per line (blank lines are
    skipped). A row's ``id`` is its ``id`` value if present, else its position; ``meta`` holds the other keys."""
    path = path_of(name_or_path)
    with _open(path) as f:
        return _read(path, ((n, line) for n, line in enumerate(f, 1) if line.strip()), _jsonl_record)


def load_split(path, part="holdout"):
    """The ``<part>_rows`` of a split JSON (entries with ``idx``, ``r1``, ``r2``, ...); ``id`` is ``idx``."""
    with open(path_of(path)) as f:
        rows = json.load(f)[f"{part}_rows"]
    return [Row(str(r["idx"]), Presentation.parse(r["r1"], r["r2"]),
                {k: v for k, v in r.items() if k not in ("idx", "r1", "r2")}) for r in rows]


_READERS = {".txt": load, ".csv": load_csv, ".jsonl": load_jsonl}


def rows(spec):
    """Rows of a dataset, benchmark or split by name, or of your own ``.txt``, ``.csv`` or ``.jsonl`` file (optionally
    ``.gz``) by path (a string or a ``Path``); the formats are in the module docstring."""
    spec = os.fspath(spec)
    if spec in SPLITS:
        return load_split(*SPLITS[spec])
    if spec in DATASETS:
        return load(spec)
    if spec in BENCHMARKS:
        return load_csv(spec)
    reader = _READERS.get(os.path.splitext(spec.lower().removesuffix(".gz"))[1])
    if reader is None:
        names = sorted(DATASETS) + sorted(BENCHMARKS) + sorted(SPLITS)
        raise KeyError(f"unknown benchmark {spec!r}; names: {names}; or a .txt, .csv or .jsonl file, optionally .gz")
    return reader(spec)


def MS(n, w):
    """Miller-Schupp ``<x, y | x^-1 y^n x = y^(n+1), x = w>`` with ``w`` a word in x, y."""
    return Presentation.parse("X" + "y" * n + "x" + "Y" * (n + 1), "X" + w)


def AK(n):
    """Akbulut-Kirby ``<x, y | xyx = yxy, x^n = y^(n+1)>``."""
    return Presentation.parse("xyxYXY", "x" * n + "Y" * (n + 1))
