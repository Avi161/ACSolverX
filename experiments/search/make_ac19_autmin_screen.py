"""Rebuild the AC19 Aut(F2)-minimal screen list that every leftover CSV names.

The campaign lists shipped in ``results/heuristic_search/ac19_autmin_screen/``
are residues: each one holds only the rows some arm failed at some budget. The
list they are cut from -- one row per ``Aut(F2)`` orbit of
``data/AC19_extended.txt``, keyed ``ac19_<orbit index>`` -- was built off-repo
and never committed, so a screen-wide campaign had nothing to iterate over.

This regenerates it, and then proves the regeneration is the same list rather
than merely a similar one: every row of every shipped residue CSV must come
back byte-identical in name, representative, member count and member indices.
The orbit index is the position of the orbit's FIRST dataset member in file
order, zero-based; that convention is not documented anywhere else, it is
recovered here and then checked against 1,000+ known rows.

    PYTHONPATH=. python3 -m experiments.search.make_ac19_autmin_screen --verify
    PYTHONPATH=. python3 -m experiments.search.make_ac19_autmin_screen --write

Roughly 8 core-minutes for the canonicalization; ``--jobs`` splits it.
"""
from __future__ import annotations

import argparse
import csv
import json
import multiprocessing as mp
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATASET = os.path.join(ROOT, "data", "AC19_extended.txt")
SCREEN_DIR = os.path.join(ROOT, "results", "heuristic_search", "ac19_autmin_screen")
OUT = os.path.join(SCREEN_DIR, "ac19_autmin_orbits.csv")
FIELDS = ("name", "r1", "r2", "n_members", "members")

# The dataset stores zero-padded signed integer arrays, two 24-slot relators to
# a line. Zero is padding, never a generator.
SYM = {1: "x", -1: "X", 2: "y", -2: "Y"}


def decode(line):
    values = json.loads(line)
    half = len(values) // 2
    return ("".join(SYM[v] for v in values[:half] if v),
            "".join(SYM[v] for v in values[half:] if v))


def load_dataset(path=DATASET):
    with open(path) as fh:
        return [decode(line) for line in fh if line.strip()]


def _canon_chunk(pairs):
    from experiments.equivalence_classes.lib.autcanon import aut_canon
    return [aut_canon(p)[1] for p in pairs]


def canonicalize(pairs, jobs=1, log=print):
    """Aut(F2)-canonical representative of every dataset row, in file order."""
    t = time.time()
    if jobs <= 1:
        reps = _canon_chunk(pairs)
    else:
        size = (len(pairs) + jobs - 1) // jobs
        chunks = [pairs[i:i + size] for i in range(0, len(pairs), size)]
        with mp.get_context("fork").Pool(jobs) as pool:
            reps = [r for part in pool.map(_canon_chunk, chunks) for r in part]
    log(f"  canonicalized {len(pairs):,} rows in {time.time() - t:.0f}s "
        f"on {jobs} core(s)")
    return reps


def group(reps):
    """Orbits in first-appearance order. Index is the row's own position."""
    orbits, order = {}, []
    for index, rep in enumerate(reps):
        if rep not in orbits:
            orbits[rep] = []
            order.append(rep)
        orbits[rep].append(index)
    return [{"rep": rep, "members": orbits[rep]} for rep in order]


def build(jobs=1, log=print):
    pairs = load_dataset()
    log(f"  dataset       : {len(pairs):,} presentations")
    rows = group(canonicalize(pairs, jobs, log))
    for index, row in enumerate(rows):
        row["name"] = f"ac19_{index}"
    log(f"  orbits        : {len(rows):,}")
    return rows


def as_csv_rows(rows):
    for row in rows:
        r1, r2 = row["rep"]
        yield {"name": row["name"], "r1": r1, "r2": r2,
               "n_members": len(row["members"]),
               "members": " ".join(str(m) for m in row["members"])}


def shipped_residues():
    """The committed RESIDUE lists that name orbits, as {name: row}.

    Explicitly not the rebuilt list itself: once ``--write`` has run, the
    output lands in this same directory, and a cross-check that includes it
    is a cross-check against itself -- it would pass on any list whatsoever.
    """
    known = {}
    for entry in sorted(os.listdir(SCREEN_DIR)):
        if not entry.endswith(".csv") or entry == os.path.basename(OUT):
            continue
        with open(os.path.join(SCREEN_DIR, entry)) as fh:
            for row in csv.DictReader(fh):
                known.setdefault(row["name"], (entry, row))
    return known


def verify(rows, log=print):
    """Fail loudly unless every shipped residue row is reproduced exactly."""
    built = {row["name"]: row for row in as_csv_rows(rows)}
    known = shipped_residues()
    bad = []
    for name, (source, want) in sorted(known.items()):
        got = built.get(name)
        if got is None:
            bad.append(f"{name} ({source}): absent from the rebuilt list")
            continue
        for field in ("r1", "r2", "n_members", "members"):
            if str(got[field]) != str(want[field]):
                bad.append(f"{name} ({source}) {field}: "
                           f"rebuilt {got[field]!r} != shipped {want[field]!r}")
    log(f"  cross-checked : {len(known):,} shipped rows over "
        f"{len(set(s for s, _ in known.values()))} residue files")
    if bad:
        for line in bad[:20]:
            log(f"    MISMATCH {line}")
        raise SystemExit(
            f"rebuild does not reproduce the shipped lists ({len(bad)} mismatches)")
    log("  agreement     : exact on every shipped row")
    return True


def write(rows, path=OUT, log=print):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(as_csv_rows(rows))
    log(f"  wrote         : {path} ({os.path.getsize(path):,} B)")
    return path


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 1) - 1))
    ap.add_argument("--write", action="store_true",
                    help="write the list once it has been cross-checked")
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args(argv)
    rows = build(args.jobs)
    verify(rows)
    if args.write:
        write(rows, args.out)
    else:
        print("  (dry run; pass --write to commit the list to disk)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
