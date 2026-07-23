"""Certificate verifier for stable-AC results: replay every solved row's path.

A ``solved: true`` row is a *claim*; the move path is its *certificate*. This
tool replays each certificate and checks, step by step, that

  * every move is one the search could have enumerated (indices in range,
    ``i != j``, ``s ∈ {±1}``, rotations within the relator lengths) and its
    seam cancels (Definition 2.1's validity condition),
  * no intermediate relator ever exceeds the row's per-relator cap,
  * the final state is the mathematically trivial presentation
    (``Presentation.is_trivial``, not merely all-lengths-1),
  * ``abs_det`` is 1 at the start (a solved claim is impossible otherwise)
    and preserved to the end,
  * the row's ``path_length`` equals the number of moves.

Across files it also checks **budget invariance**: a budget-``B`` search is
exactly the first ``B`` pops of any longer search, so for the same
``(presentation, cap, cyclic)`` job, solved-at-``B1`` implies solved-at-``B2``
with identical ``nodes_explored`` and ``path_length`` for every ``B2 > B1``.

INDEPENDENCE RULE: replays go through ``experiments/greedy_tests/spec`` ONLY —
never through ``solvern`` or the numba solvers — so a solver bug (or a gamed
test suite) cannot self-certify. This file's job never changes when a solver
does; treat any edit to it with the same suspicion as an edit to ``spec/``.

Handles both pipelines' formats:
  * nocov results jsonl + ``*_paths.jsonl`` sibling (5-field ``i_j_s_k1_k2``
    moves, 0-based, n_gen=3),
  * cov/covbase jsonl with inline ``path_moves`` (legacy 4-field
    ``target_jsign_k1_k2`` moves, target 1-based, n_gen=2).

CLI (from the repo root; verifies everything under results/stable_ac by
default, runs no searches, needs no budget):

    .venv/bin/python3 -m experiments.stable_ac.verify_results
    .venv/bin/python3 -m experiments.stable_ac.verify_results results/stable_ac/nocov/nocov_*_A1_100_*.jsonl
"""

import argparse
import glob
import json
import os
import sys

from experiments.greedy_tests.spec.invariants import abs_det
from experiments.greedy_tests.spec.moves import (
    Move, apply_move, legacy_to_move, seam_cancels, source_word,
)
from experiments.greedy_tests.spec.presentation import Presentation
from experiments.greedy_tests.spec.words import reduce_word


class CertificateError(Exception):
    """One row's certificate failed; the message says exactly where."""


def parse_move(s):
    """``"i_j_s_k1_k2"`` (general, 0-based) or ``"t_s_k1_k2"`` (legacy 2-rel)."""
    parts = [int(p) for p in s.split("_")]
    if len(parts) == 5:
        return Move(*parts)
    if len(parts) == 4:
        return legacy_to_move(*parts)
    raise CertificateError(f"unparseable move string {s!r}")


def replay_verified(pres, moves, cap, cyclic):
    """spec replay with legality and the cap enforced at every step."""
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


def start_presentation(row, path_row=None):
    """The exact presentation the search ran on, rebuilt from the row."""
    if row.get("mode") == "nocov":
        z_relator = (path_row or row)["z_relator"]
        return Presentation.from_strs(row["r1"], row["r2"], z_relator, n_gen=3)
    # cov / covbase: the row's r1/r2 ARE the (possibly transformed) search input
    return Presentation.from_strs(row["r1"], row["r2"], n_gen=row.get("n_gen", 2))


def verify_solved_row(row, path_moves, path_row=None):
    """Raise CertificateError unless this solved row's certificate is valid."""
    if not path_moves:
        raise CertificateError("solved row has no path_moves certificate")
    if row.get("path_length") != len(path_moves):
        raise CertificateError(
            f"path_length {row.get('path_length')} != {len(path_moves)} moves")
    if row.get("mode") == "nocov":
        # bind the certificate to the row's IDENTITY: rows are keyed by
        # (name, z_word), so a valid certificate relabeled under a different
        # z_word must not verify (verifier-audit finding, 2026-07-13)
        if row.get("z_relator") != "Z" + str(row.get("z_word") or ""):
            raise CertificateError(
                f"z_relator {row.get('z_relator')!r} does not encode "
                f"z_word {row.get('z_word')!r}")
    if path_row is not None:
        for k in ("r1", "r2", "z_relator"):
            if path_row.get(k) != row.get(k):
                raise CertificateError(f"paths row {k} disagrees with results row")
    pres = start_presentation(row, path_row)
    d0 = abs_det(pres)
    if d0 != 1:
        raise CertificateError(f"solved claim with abs_det {d0} != 1 is impossible")
    moves = [parse_move(s) for s in path_moves]
    final = replay_verified(pres, moves, row["max_relator_length_cap"],
                            row.get("cyclic_reduce", True))
    if not final.is_trivial():
        raise CertificateError(
            f"replay ends at {final.to_strs()}, not the trivial presentation")
    if abs_det(final) != d0:
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


def _job_key(row, path_row=None):
    """Full search identity: (relators, cap, cyclic). Everything nodes/path
    depend on besides the budget."""
    z = (path_row or row).get("z_relator") if row.get("mode") == "nocov" else None
    return (row.get("mode"), row["r1"], row["r2"], z,
            row["max_relator_length_cap"], row.get("cyclic_reduce", True))


def verify_file(path, invariance_pool=None):
    """Verify one results jsonl. Returns (n_rows, n_solved, failures)."""
    rows, notes = load_jsonl(path)
    failures = []
    for note in notes:
        print(f"  note: {note}")

    paths_index = {}
    is_nocov = any(r.get("mode") == "nocov" for r in rows)
    if is_nocov:
        ppath = path[:-len(".jsonl")] + "_paths.jsonl"
        if os.path.exists(ppath):
            prows, pnotes = load_jsonl(ppath)
            for note in pnotes:
                print(f"  note: {note}")
            paths_index = {(p["name"], p["z_word"]): p for p in prows}
        elif any(r.get("solved") for r in rows):
            failures.append((path, "(file)", "solved rows but no _paths.jsonl sibling"))

    n_solved, solved_keys = 0, set()
    for r in rows:
        rid = (r.get("name"), r.get("z_word")) if is_nocov else (r.get("pres_id"),)
        if invariance_pool is not None:
            path_row = paths_index.get(rid) if is_nocov else None
            invariance_pool.setdefault(_job_key(r, path_row), {})[
                r["node_budget"]] = (bool(r.get("solved")),
                                     r.get("nodes_explored"),
                                     r.get("path_length"), path)
        if not r.get("solved"):
            continue
        n_solved += 1
        solved_keys.add(rid)
        try:
            if is_nocov:
                prow = paths_index.get(rid)
                if prow is None:
                    raise CertificateError("no paths row for this solved job")
                verify_solved_row(r, prow.get("path_moves"), prow)
            else:
                verify_solved_row(r, r.get("path_moves"))
        except CertificateError as e:
            failures.append((path, rid, str(e)))
        except (KeyError, ValueError, TypeError) as e:
            # a malformed row must FAIL cleanly, never crash the whole run
            failures.append((path, rid, f"malformed row: {type(e).__name__}: {e}"))

    if is_nocov and paths_index:
        orphans = set(paths_index) - solved_keys
        if orphans:
            failures.append((path, "(file)",
                             f"{len(orphans)} paths rows without a solved results "
                             f"row, e.g. {sorted(orphans)[0]}"))
    return len(rows), n_solved, failures


def check_budget_invariance(pool):
    """Cross-file check: same job at budgets B1 < B2 must agree."""
    violations = 0
    for key, by_budget in pool.items():
        budgets = sorted(by_budget)
        for a in range(len(budgets)):
            for b in range(a + 1, len(budgets)):
                b1, b2 = budgets[a], budgets[b]
                s1, n1, p1, f1 = by_budget[b1]
                s2, n2, p2, f2 = by_budget[b2]
                bad = None
                if s1 and not (s2 and n1 == n2 and p1 == p2):
                    bad = (f"solved at {b1} (nodes {n1}, path {p1}) but budget "
                           f"{b2} says solved={s2}, nodes {n2}, path {p2}")
                elif not s1 and s2 and n2 is not None and n2 <= b1:
                    bad = (f"solved at {b2} in {n2} <= {b1} nodes but the "
                           f"budget-{b1} run reports unsolved")
                elif not s1 and not s2 and n1 is not None and n1 < b1 and n1 != n2:
                    bad = (f"frontier exhausted at {n1} < {b1} nodes but budget "
                           f"{b2} explored {n2}")
                if bad:
                    violations += 1
                    print(f"INVARIANCE VIOLATION: r1={key[1]!r} r2={key[2]!r} "
                          f"z={key[3]!r}: {bad}\n  files: {f1} vs {f2}")
    return violations


def collect_files(args_paths):
    files = []
    for p in args_paths:
        if os.path.isdir(p):
            files.extend(sorted(glob.glob(os.path.join(p, "**", "*.jsonl"),
                                          recursive=True)))
        else:
            files.extend(sorted(glob.glob(p)) or [p])
    return [f for f in files if not f.endswith("_paths.jsonl")]


def _is_search_results(path):
    """True if `path` is a search-results jsonl (has the `_job_key` fields).

    `results/stable_ac/` also holds analysis jsonl — mu-ladder rungs, MITM
    merges — that carry no `node_budget`/`max_relator_length_cap` and no
    certificate to verify. Pooling one into the invariance check raises
    KeyError, so they are skipped *loudly*: a silent skip in a verifier reads
    as "everything verified" when it did not."""
    try:
        with open(path) as f:
            for ln in f:
                if ln.strip():
                    row = json.loads(ln)
                    return ("max_relator_length_cap" in row
                            and "node_budget" in row)
    except (OSError, json.JSONDecodeError):
        return True          # let verify_file report it properly
    return False             # empty file


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("paths", nargs="*", default=["results/stable_ac"],
                    help="results jsonl files or directories "
                         "(default: results/stable_ac)")
    args = ap.parse_args(argv)

    files = collect_files(args.paths)
    if not files:
        print("no results files found")
        return 1

    skipped = [f for f in files if not _is_search_results(f)]
    files = [f for f in files if f not in set(skipped)]
    for f in skipped:
        print(f"{f}: not a search-results jsonl — SKIPPED (no certificates)")
    if not files:
        print("no search-results files among the paths given")
        return 1

    pool, all_failures, total_rows, total_solved = {}, [], 0, 0
    for f in files:
        try:
            n_rows, n_solved, failures = verify_file(f, invariance_pool=pool)
        except CertificateError as e:
            all_failures.append((f, "(file)", str(e)))
            print(f"{f}: UNREADABLE — {e}")
            continue
        total_rows += n_rows
        total_solved += n_solved
        all_failures.extend(failures)
        bad = sum(1 for ff in failures if ff[0] == f)
        print(f"{f}: {n_rows} rows, {n_solved} solved, "
              f"{n_solved - bad} certificates verify" + (f", {bad} FAIL" if bad else ""))

    violations = check_budget_invariance(pool)
    n_multi = sum(1 for v in pool.values() if len(v) > 1)
    print(f"budget-invariance: {n_multi} jobs seen at >1 budget, "
          f"{violations} violations")

    if all_failures or violations:
        print(f"\n{len(all_failures)} CERTIFICATE FAILURES, "
              f"{violations} INVARIANCE VIOLATIONS")
        for f, rid, msg in all_failures:
            print(f"  {f} {rid}: {msg}")
        return 1
    print(f"\nALL {total_solved} SOLVED-ROW CERTIFICATES VERIFY "
          f"({total_rows} rows across {len(files)} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
