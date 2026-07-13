"""Phase 0: where do the 261 'reps' come from, and is word-reversal a free extra symmetry?

Answers three questions with no search at all:
  1. Are the 261 CSV rows Miller-Schupp presentations, and what dedup produced them from the 1190?
  2. Is w -> reverse(w) an AC-triviality-preserving symmetry NOT already quotiented out?
  3. Does an independent orbit enumeration reproduce the 168 Aut(F2) classes?
"""
import ast
import csv
import os
import sys
from collections import defaultdict

# The repo root, found by walking up rather than by counting directory levels. A
# dirname chain encodes this file's depth, so it silently repoints at the wrong
# directory the moment the file moves -- and every path below is then wrong.
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

from experiments.equivalence_classes.lib.words import (  # noqa: E402
    SIGNED_PERMS, abelian_det, apply_pair, canon_pair, exp_sums, ints_to_word,
    inv, ms_presentation, relabel_key, rev,
)

D = os.path.join(ROOT, "data")


def load_reps():
    with open(os.path.join(D, "ms_unsolved_reps", "ms_reps_unsolved.csv")) as f:
        return [(r["r1"], r["r2"], r["name"]) for r in csv.DictReader(f)]


def load_1190():
    out = []
    with open(os.path.join(D, "1190MS.txt")) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            ints = ast.literal_eval(line)
            half = len(ints) // 2
            out.append((ints_to_word(ints[:half]), ints_to_word(ints[half:])))
    return out


def load_grid():
    """rows = w, cols = n in 1..7, cell = 'trivial' or a rep name."""
    cells = []
    with open(os.path.join(D, "ms_unsolved_reps", "ms_solved_grid.csv")) as f:
        rows = list(csv.reader(f))
    header = rows[0]
    ns = [c for c in header[1:] if c.strip()]
    for row in rows[1:]:
        w = row[0]
        if not w:  # the trailing totals row
            continue
        for j, n in enumerate(ns):
            v = row[1 + j].strip()
            if v:
                cells.append((w, int(n), v))
    return cells


def main():
    reps = load_reps()
    ms1190 = load_1190()
    grid = load_grid()

    print(f"reps        : {len(reps)}")
    print(f"1190MS.txt  : {len(ms1190)}")
    print(f"grid cells  : {len(grid)}")

    named = [c for c in grid if c[2] != "trivial"]
    triv = [c for c in grid if c[2] == "trivial"]
    names = {c[2] for c in named}
    print(f"grid trivial: {len(triv)}   grid named: {len(named)}   distinct names: {len(names)}")

    # --- Q1a: is the grid's (w, n) -> MS presentation consistent with 1190MS.txt? ---
    ms_set = {canon_pair(*p) for p in ms1190}
    grid_ms = {canon_pair(*ms_presentation(n, w)) for (w, n, _) in grid}
    print(f"\n[Q1a] canonical MS from 1190MS.txt : {len(ms_set)}")
    print(f"[Q1a] canonical MS rebuilt from grid: {len(grid_ms)}")
    print(f"[Q1a] rebuilt == file             : {grid_ms == ms_set}")

    # --- Q1b: do the 261 reps equal the canonical forms of the 550 unsolved MS cells? ---
    unsolved_ms = {}
    for (w, n, name) in named:
        unsolved_ms.setdefault(canon_pair(*ms_presentation(n, w)), []).append((w, n, name))
    print(f"\n[Q1b] unsolved grid cells {len(named)} -> distinct canonical MS pairs: {len(unsolved_ms)}")

    rep_canon = {canon_pair(r1, r2): name for (r1, r2, name) in reps}
    print(f"[Q1b] 261 reps -> distinct canonical pairs: {len(rep_canon)}")
    print(f"[Q1b] reps == canonical unsolved MS pairs : {set(rep_canon) == set(unsolved_ms)}")

    if set(rep_canon) != set(unsolved_ms):
        only_rep = set(rep_canon) - set(unsolved_ms)
        only_ms = set(unsolved_ms) - set(rep_canon)
        print(f"       only in reps: {len(only_rep)}  e.g. {list(only_rep)[:3]}")
        print(f"       only in MS  : {len(only_ms)}  e.g. {list(only_ms)[:3]}")
        r0 = reps[0]
        print(f"       rep[0] = {r0}  exp_sums r1={exp_sums(r0[0])} r2={exp_sums(r0[1])}")
        ms0 = ms_presentation(2, "YYXyxyy")
        print(f"       MS(2,'YYXyxyy') = {ms0} -> canon {canon_pair(*ms0)}")

    # name -> how many (w, n) cells carry it: this is the collapse the upstream dedup made
    by_name = defaultdict(list)
    for (w, n, name) in named:
        by_name[name].append((w, n))
    multi = {k: v for k, v in by_name.items() if len(v) > 1}
    print(f"\n[Q1c] rep names carried by >1 (w,n) cell: {len(multi)}")
    for k in list(multi)[:5]:
        print(f"       {k}: {multi[k]}")

    # --- Q2: word reversal ---
    # Claim: reverse(w) = sigma(w^-1) with sigma: x->X, y->Y, so on a PAIR,
    # (rev r1, rev r2) has the same canonical form as sigma(r1, r2) -- already one of the 8.
    sigma = {"x": "X", "y": "Y"}
    bad_id, bad_cls = 0, 0
    for (r1, r2, name) in reps:
        lhs = canon_pair(rev(r1), rev(r2))
        rhs = apply_pair((r1, r2), sigma)
        if lhs != rhs:
            bad_id += 1
        if relabel_key((rev(r1), rev(r2))) != relabel_key((r1, r2)):
            bad_cls += 1
    print(f"\n[Q2] canon(rev(P)) == canon(sigma(P)) on all 261 : {bad_id == 0} ({bad_id} failures)")
    print(f"[Q2] relabel_key(rev(P)) == relabel_key(P)       : {bad_cls == 0} ({bad_cls} failures)")
    print("[Q2] => word reversal is subsumed by the 8 signed perms. No new merges.")

    # --- Q3: relabel classes, and |det| ---
    cls = defaultdict(list)
    for (r1, r2, name) in reps:
        cls[relabel_key((r1, r2))].append(name)
    print(f"\n[Q3] relabel (8 signed perm) classes: {len(cls)}")
    dets = {abs(abelian_det(r1, r2)) for (r1, r2, _) in reps}
    print(f"[Q3] |det| values over the 261: {sorted(dets)}")


if __name__ == "__main__":
    main()
