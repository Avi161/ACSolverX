"""Certificate verifier for Track T2 (static rank-4/5) results — spec-only.

A ``solved: true`` row is a *claim*; its move path is the *certificate*. For each
solved row this tool checks, independently of any solver:

  (a) STRUCTURAL — the start presentation is a legal iterated stabilization of
      ``<x,y | r1, r2>``: relators ``(r1, r2, Z.w1, ..., G_k.w_k)`` with
      ``n_gen == n_rel == rank``, each ``r1, r2`` in ``F(x,y)``, and each adjoined
      generator introduced by exactly one coupled relator ``G^-1.w`` whose leading
      letter is that generator's inverse. Each ``w_i`` may use only generators
      ``1..2`` (default) or ``1..(2+i-1)`` when the row was produced with
      ``allow_chained``; an adjoined generator never occurs before its own coupled
      relator nor inside its own defining word.

  (b) REPLAY — the ``i_j_s_k1_k2`` move path is replayed through
      ``experiments/greedy_tests/spec`` (the pure-Python general-``n`` move
      machinery), each move checked legal (indices in range, ``i != j``,
      ``s in {±1}``, rotations within the relator lengths, seam cancels) and
      cap-respecting, and the final state asserted to have every relator of
      length 1 AND to be the mathematical trivial presentation (spec
      ``Presentation.is_trivial``).

  (c) INVARIANT — ``abs_det`` (the exponent-sum determinant) is 1 at the start (a
      solved claim is impossible otherwise) and preserved to the end.

INDEPENDENCE: replays go through ``spec`` ONLY — this module NEVER imports
``solvern`` or any numba solver, so a solver bug (or a gamed test suite) cannot
self-certify. The only shared thing is the on-disk rendering alphabet, which is
re-implemented here as pure I/O (``_CHARS``) because spec's own string codec only
renders ``x/y/z`` (n_gen <= 3) whereas rank 4/5 presentations use ``a, b``.

CLI (from the repo root; verifies everything under
results/stable_ac/static_rank by default, runs no searches, needs no budget):

    .venv/bin/python3 -m experiments.stable_ac.verify_static_rank
    .venv/bin/python3 -m experiments.stable_ac.verify_static_rank results/stable_ac/static_rank/staticrank_*_r4_*.jsonl
"""

import argparse
import glob
import json
import os
import sys

from experiments.greedy_tests.spec.invariants import abs_det
from experiments.greedy_tests.spec.moves import (
    Move, apply_move, seam_cancels, source_word,
)
from experiments.greedy_tests.spec.presentation import Presentation
from experiments.greedy_tests.spec.words import reduce_word

#: The runner's rendering alphabet (solvern.GEN_CHARS). Re-declared here as pure
#: I/O so the verifier shares NO code with the solver; spec's own codec stops at
#: "xyz", but rank 4/5 relators use a, b, ...
_CHARS = "xyz" + "abcdefghijklmnopqrstuvw"
_BASE_N_GEN = 2                       # <x, y | ...> is the un-stabilized rank


class CertificateError(Exception):
    """One row's certificate failed; the message says exactly where."""


def _char_to_int(c):
    g = _CHARS.index(c.lower()) + 1
    return g if c.islower() else -g


def _str_to_word(s):
    return tuple(_char_to_int(c) for c in s)


def _z_key(z_words):
    """Order-independent word-set key (must match run_static_rank._z_key)."""
    return "+".join(sorted(z_words))


def parse_move(s):
    """``"i_j_s_k1_k2"`` (general, 0-based) -> Move."""
    parts = [int(p) for p in s.split("_")]
    if len(parts) != 5:
        raise CertificateError(f"unparseable move string {s!r}")
    return Move(*parts)


# -- (a) structural stabilization check --------------------------------------


def structural_start(row, path_row=None):
    """Rebuild + structurally validate the start presentation of a solved row.

    Returns the ``Presentation`` (int relators). Raises ``CertificateError`` if
    the row is not a legal iterated static stabilization of ``<x,y | r1, r2>``.
    """
    src = path_row or row
    r1, r2 = row["r1"], row["r2"]
    z_words = list(src["z_words"])
    z_relators = list(src["z_relators"])
    rank = row["rank"]
    allow_chained = bool(row.get("allow_chained", False))
    k = rank - _BASE_N_GEN

    if len(z_words) != k or len(z_relators) != k:
        raise CertificateError(
            f"rank {rank} needs {k} adjoined word(s), got "
            f"{len(z_words)} z_words / {len(z_relators)} z_relators")
    if row.get("n_gen") not in (None, rank) or row.get("n_rel") not in (None, rank):
        raise CertificateError(
            f"rank {rank} but row reports n_gen={row.get('n_gen')}, "
            f"n_rel={row.get('n_rel')} (a balanced stabilization needs both == rank)")

    base = [_str_to_word(r1), _str_to_word(r2)]
    for idx, w in enumerate(base):
        if any(abs(g) > _BASE_N_GEN for g in w):
            raise CertificateError(
                f"base relator r{idx + 1}={ (r1, r2)[idx]!r} leaves F(x,y)")

    relators = list(base)
    for j, (zw, zrel) in enumerate(zip(z_words, z_relators)):
        g = _BASE_N_GEN + j + 1                    # z=3, a=4, b=5, ...
        w = _str_to_word(zw)
        expected = (-g,) + w
        if _str_to_word(zrel) != expected:
            raise CertificateError(
                f"adjoined relator {j} {zrel!r} != G^-1.w for "
                f"generator {g} and w={zw!r}")
        # each w_i's alphabet: 1..2 (default) or 1..(g-1) when chained
        max_gen = (g - 1) if allow_chained else _BASE_N_GEN
        if any(not (1 <= abs(s) <= max_gen) for s in w):
            raise CertificateError(
                f"adjoined word w{j + 1}={zw!r} uses a generator outside "
                f"1..{max_gen}" + ("" if allow_chained else " (F(x,y))"))
        # the adjoined generator g is introduced HERE and nowhere earlier, and
        # does not occur inside its own defining word w
        for earlier in relators:
            if any(abs(s) == g for s in earlier):
                raise CertificateError(
                    f"adjoined generator {g} occurs before its own coupled "
                    f"relator (relator {relators.index(earlier)})")
        if any(abs(s) == g for s in w):
            raise CertificateError(
                f"adjoined generator {g} occurs inside its own defining word "
                f"w{j + 1}={zw!r}")
        relators.append(expected)

    return Presentation(rank, tuple(relators))


# -- (b) legal + cap-respecting replay through spec --------------------------


def replay_verified(pres, moves, cap, cyclic):
    """spec replay with legality and the per-relator cap enforced at every step."""
    cur = pres.reduced(cyclic).canonical()
    if any(len(r) > cap for r in cur.relators):
        raise CertificateError(f"start state exceeds cap {cap}")
    for n, mv in enumerate(moves):
        if not (0 <= mv.i < cur.n_rel and 0 <= mv.j < cur.n_rel
                and mv.i != mv.j and mv.s in (1, -1)):
            raise CertificateError(f"move {n} {mv}: invalid indices")
        oj = source_word(cur.relators, mv)
        if not cur.relators[mv.i] or not oj:
            raise CertificateError(f"move {n} {mv}: empty relator")
        if not (0 <= mv.k1 < len(cur.relators[mv.i]) and 0 <= mv.k2 < len(oj)):
            raise CertificateError(f"move {n} {mv}: rotation out of range")
        if not seam_cancels(cur.relators, mv):
            raise CertificateError(f"move {n} {mv}: seam does not cancel")
        raw = apply_move(cur.relators, mv)
        red = tuple(reduce_word(r, cyclic) for r in raw)
        if any(len(r) > cap for r in red):
            raise CertificateError(f"move {n} {mv}: relator exceeds cap {cap}")
        cur = Presentation(cur.n_gen, red).canonical()
    return cur


def verify_solved_row(row, path_moves, path_row=None):
    """Raise ``CertificateError`` unless this solved row's certificate is valid."""
    if not path_moves:
        raise CertificateError("solved row has no path_moves certificate")
    if row.get("path_length") != len(path_moves):
        raise CertificateError(
            f"path_length {row.get('path_length')} != {len(path_moves)} moves")
    if path_row is not None:
        for k in ("r1", "r2"):
            if path_row.get(k) != row.get(k):
                raise CertificateError(f"paths row {k} disagrees with results row")
        if _z_key(path_row.get("z_words", [])) != _z_key(row.get("z_words", [])):
            raise CertificateError("paths row z_words disagree with results row")

    pres = structural_start(row, path_row)              # (a)
    d0 = abs_det(pres)                                   # (c) start
    if d0 != 1:
        raise CertificateError(f"solved claim with abs_det {d0} != 1 is impossible")
    moves = [parse_move(s) for s in path_moves]
    final = replay_verified(pres, moves, row["max_relator_length_cap"],
                            row.get("cyclic_reduce", True))                # (b)
    if not all(len(r) == 1 for r in final.relators):
        raise CertificateError("replay ends with a relator longer than one letter")
    if not final.is_trivial():
        raise CertificateError("replay ends at a non-trivial presentation")
    if abs_det(final) != d0:                             # (c) preserved
        raise CertificateError("abs_det not preserved by replay")


# -- file handling ------------------------------------------------------------


def load_jsonl(path):
    """(rows, notes). A torn FINAL line is tolerated (crash mid-append is the
    normal failure mode this pipeline recovers from); a torn interior line is
    corruption and fails the file."""
    rows, notes = [], []
    with open(path) as f:
        lines = f.read().splitlines()
    for n, ln in enumerate(lines):
        if not ln.strip():
            continue
        try:
            rows.append(json.loads(ln))
        except json.JSONDecodeError:
            if n == len(lines) - 1:
                notes.append(f"torn trailing line {n + 1} skipped")
            else:
                raise CertificateError(f"{path}:{n + 1}: malformed interior line")
    return rows, notes


def verify_file(path):
    """Verify one static_rank results jsonl. Returns (n_rows, n_solved, failures)."""
    rows, notes = load_jsonl(path)
    failures = []
    for note in notes:
        print(f"  note: {note}")

    ppath = path[:-len(".jsonl")] + "_paths.jsonl"
    paths_index = {}
    if os.path.exists(ppath):
        prows, pnotes = load_jsonl(ppath)
        for note in pnotes:
            print(f"  note: {note}")
        paths_index = {(p["name"], _z_key(p["z_words"])): p for p in prows}
    elif any(r.get("solved") for r in rows):
        failures.append((path, "(file)", "solved rows but no _paths.jsonl sibling"))

    n_solved, solved_keys = 0, set()
    for r in rows:
        rid = (r.get("name"), _z_key(r.get("z_words", [])))
        if not r.get("solved"):
            continue
        n_solved += 1
        solved_keys.add(rid)
        try:
            prow = paths_index.get(rid)
            if prow is None:
                raise CertificateError("no paths row for this solved job")
            verify_solved_row(r, prow.get("path_moves"), prow)
        except CertificateError as e:
            failures.append((path, rid, str(e)))
        except (KeyError, ValueError, TypeError) as e:
            failures.append((path, rid, f"malformed row: {type(e).__name__}: {e}"))

    if paths_index:
        orphans = set(paths_index) - solved_keys
        if orphans:
            failures.append((path, "(file)",
                             f"{len(orphans)} paths rows without a solved results "
                             f"row, e.g. {sorted(orphans)[0]}"))
    return len(rows), n_solved, failures


def collect_files(args_paths):
    files = []
    for p in args_paths:
        if os.path.isdir(p):
            files.extend(sorted(glob.glob(os.path.join(p, "**", "*.jsonl"),
                                          recursive=True)))
        else:
            files.extend(sorted(glob.glob(p)) or [p])
    return [f for f in files if not f.endswith("_paths.jsonl")]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("paths", nargs="*", default=["results/stable_ac/static_rank"],
                    help="results jsonl files or directories "
                         "(default: results/stable_ac/static_rank)")
    args = ap.parse_args(argv)

    files = collect_files(args.paths)
    if not files:
        print("no results files found")
        return 1

    all_failures, total_rows, total_solved = [], 0, 0
    for f in files:
        try:
            n_rows, n_solved, failures = verify_file(f)
        except CertificateError as e:
            all_failures.append((f, "(file)", str(e)))
            print(f"{f}: UNREADABLE — {e}")
            continue
        total_rows += n_rows
        total_solved += n_solved
        all_failures.extend(failures)
        bad = sum(1 for ff in failures if ff[0] == f)
        print(f"{f}: {n_rows} rows, {n_solved} solved, "
              f"{n_solved - bad} certificates verify"
              + (f", {bad} FAIL" if bad else ""))

    if all_failures:
        print(f"\n{len(all_failures)} CERTIFICATE FAILURES")
        for f, rid, msg in all_failures:
            print(f"  {f} {rid}: {msg}")
        return 1
    print(f"\nALL {total_solved} SOLVED-ROW CERTIFICATES VERIFY "
          f"({total_rows} rows across {len(files)} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
