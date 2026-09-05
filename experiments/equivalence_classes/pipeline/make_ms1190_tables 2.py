"""The full Miller-Schupp benchmark as two tables: what is settled, and what is left.

The 1190 of ``data/1190MS.txt`` are ``MS(n, w)`` over the 170 zero-x-exponent words of
``ms_solved_grid.csv`` and ``n in 1..7``. The grid splits them 640 trivial / 550 unsolved,
and the 550 carry only 261 distinct rep names, which collapse to 124 ACA classes
(``data/ms_unsolved_reps/aca_124.csv``; see ``results/equivalence_classes/EQUIVALENCE_FINDING.md``).

Table A (solved) is the 640 trivial cells keyed by their **Aut(F2)-minimal state** -- Whitehead's
complete invariant, via ``lib/autcanon.aut_canon`` -- keeping exactly one representative per
distinct orbit. Table B (unsolved) is the 124 ACA classes, carrying the same Aut column so the
two sides are read on one ruler.

Two things this deliberately does NOT do:

  * It does not dedupe the two sides against **each other's** relation. Table A is quotiented by
    Aut(F2) only; Table B by ACA, which is strictly coarser (AC moves *and* change of variables).
    An Aut-orbit count on the left is therefore not comparable to a class count on the right --
    only the per-row Aut rep is.
  * It does not claim the Aut rep of a solved row is AC-equivalent to its members. Aut(F2) does
    not act by AC moves; it preserves AC-*triviality* (EQUIVALENCE_FINDING.md Sec 0), which is
    all a solved/unsolved split needs, and is why the orbit is the right dedup key here.

The disjointness check at the end is the one that carries information: an Aut rep appearing on
both sides would mean an "unsolved" class is Aut-equivalent to a trivialized one, hence solved.

    python3 -m experiments.equivalence_classes.pipeline.make_ms1190_tables
"""
import csv
import os
import sys
from collections import defaultdict


def _repo_root():
    d = os.path.dirname(os.path.abspath(__file__))
    while d != os.path.dirname(d):
        if (os.path.isdir(os.path.join(d, "experiments"))
                and os.path.isdir(os.path.join(d, "data"))):
            return d
        d = os.path.dirname(d)
    raise RuntimeError("repo root (holding experiments/ and data/) not found")


ROOT = _repo_root()
sys.path.insert(0, ROOT)

from experiments.equivalence_classes.lib.autcanon import aut_canon, check  # noqa: E402
from experiments.equivalence_classes.lib.words import canon_pair, ms_presentation  # noqa: E402
from experiments.equivalence_classes.phases.phase0_provenance import load_grid  # noqa: E402

D = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "results", "equivalence_classes", "ms1190_tables")

SOLVED_COLS = ["aut_id", "rep_r1", "rep_r2", "rep_len", "n_cells", "ms_r1", "ms_r2", "cells"]
UNSOLVED_COLS = ["aca_id", "r1", "r2", "rep_r1", "rep_r2", "rep_len", "n_reps", "n_cells", "reps"]


def load_aca_124():
    with open(os.path.join(D, "ms_unsolved_reps", "aca_124.csv")) as f:
        return list(csv.DictReader(f))


def build_solved(grid):
    """The 640 trivial cells, one row per distinct Aut(F2) orbit."""
    orbits = defaultdict(list)
    for (w, n, v) in grid:
        if v != "trivial":
            continue
        pair = canon_pair(*ms_presentation(n, w))
        total, rep, phi = aut_canon(pair)
        if not check(pair, rep, phi):
            raise RuntimeError(f"aut_canon certificate failed on MS({n}, {w!r})")
        orbits[rep].append((f"{w}@{n}", pair))

    rows = []
    # Order by orbit size then by the rep itself: the heaviest redundancy reads first, and the
    # ordering is a pure function of the data (no dict-insertion or hash dependence).
    for rep in sorted(orbits, key=lambda r: (-len(orbits[r]), r)):
        members = sorted(orbits[rep])
        # The concrete MS pair shown is the shortest member, ties broken lexicographically, so
        # the row's witness is deterministic rather than "whichever cell came first".
        ms = min((len(p[0]) + len(p[1]), p) for _, p in members)[1]
        rows.append({
            "rep_r1": rep[0], "rep_r2": rep[1], "rep_len": len(rep[0]) + len(rep[1]),
            "n_cells": len(members), "ms_r1": ms[0], "ms_r2": ms[1],
            "cells": " ".join(c for c, _ in members),
        })
    for i, r in enumerate(rows):
        r["aut_id"] = f"sol_{i:03d}"
    return [{k: r[k] for k in SOLVED_COLS} for r in rows]


def build_unsolved(grid):
    """The 124 ACA classes, with the Aut(F2) rep of each class representative."""
    cells_per_name = defaultdict(int)
    for (w, n, v) in grid:
        if v != "trivial":
            cells_per_name[v] += 1

    rows = []
    for r in load_aca_124():
        pair = canon_pair(r["r1"], r["r2"])
        total, rep, phi = aut_canon(pair)
        if not check(pair, rep, phi):
            raise RuntimeError(f"aut_canon certificate failed on {r['name']}")
        names = r["members"].split()
        rows.append({
            "aca_id": r["name"], "r1": r["r1"], "r2": r["r2"],
            "rep_r1": rep[0], "rep_r2": rep[1], "rep_len": len(rep[0]) + len(rep[1]),
            "n_reps": len(names), "n_cells": sum(cells_per_name[n] for n in names),
            "reps": " ".join(names),
        })
    return rows


def write_csv(path, cols, rows):
    with open(path, "w", newline="") as f:
        wtr = csv.DictWriter(f, fieldnames=cols)
        wtr.writeheader()
        wtr.writerows(rows)


def write_side_by_side(path, solved, unsolved):
    """Both tables in one sheet, left block | gutter | right block."""
    with open(path, "w", newline="") as f:
        wtr = csv.writer(f)
        wtr.writerow(
            [f"TABLE A - SOLVED: {len(solved)} distinct Aut(F2) orbits over the 640 trivial cells"]
            + [""] * (len(SOLVED_COLS) - 1) + [""]
            + [f"TABLE B - UNSOLVED: {len(unsolved)} ACA classes over the 550 unsolved cells"]
        )
        wtr.writerow(SOLVED_COLS + [""] + UNSOLVED_COLS)
        for i in range(max(len(solved), len(unsolved))):
            left = ([solved[i][c] for c in SOLVED_COLS] if i < len(solved)
                    else [""] * len(SOLVED_COLS))
            right = ([unsolved[i][c] for c in UNSOLVED_COLS] if i < len(unsolved)
                     else [""] * len(UNSOLVED_COLS))
            wtr.writerow(left + [""] + right)


def main():
    grid = load_grid()
    n_triv = sum(1 for c in grid if c[2] == "trivial")
    n_unsolved = len(grid) - n_triv
    if (len(grid), n_triv, n_unsolved) != (1190, 640, 550):
        raise RuntimeError(f"grid is {len(grid)} cells / {n_triv} trivial -- expected 1190 / 640")

    solved = build_solved(grid)
    unsolved = build_unsolved(grid)

    if sum(int(r["n_cells"]) for r in solved) != 640:
        raise RuntimeError("solved rows do not account for exactly 640 cells")
    if sum(int(r["n_reps"]) for r in unsolved) != 261:
        raise RuntimeError("ACA classes do not account for exactly 261 rep names")
    if sum(int(r["n_cells"]) for r in unsolved) != 550:
        raise RuntimeError("ACA classes do not account for exactly 550 unsolved cells")

    os.makedirs(OUT, exist_ok=True)
    write_csv(os.path.join(OUT, "solved_640_aut_orbits.csv"), SOLVED_COLS, solved)
    write_csv(os.path.join(OUT, "unsolved_124_aca_classes.csv"), UNSOLVED_COLS, unsolved)
    write_side_by_side(os.path.join(OUT, "ms1190_two_tables.csv"), solved, unsolved)

    print(f"1190 cells = {n_triv} trivial + {n_unsolved} unsolved")
    print(f"TABLE A: 640 solved cells -> {len(solved)} distinct Aut(F2) orbits "
          f"({640 - len(solved)} redundant, {640 / len(solved):.1f}x)")
    print(f"TABLE B: 550 unsolved cells -> 261 rep names -> {len(unsolved)} ACA classes")

    left = {(r["rep_r1"], r["rep_r2"]) for r in solved}
    right = {(r["rep_r1"], r["rep_r2"]) for r in unsolved}
    shared = left & right
    print(f"\nAut reps shared between the two tables: {len(shared)} "
          f"(expected 0 -- a shared orbit would mean an 'unsolved' class is already solved)")
    if shared:
        for s in sorted(shared):
            print(f"  !! {s}")
    print(f"\nwrote -> {os.path.relpath(OUT, ROOT)}/")


if __name__ == "__main__":
    main()
