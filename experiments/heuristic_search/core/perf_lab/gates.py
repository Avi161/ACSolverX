"""Equivalence gates a candidate ``hcompact`` engine must pass before promotion.

Three independent checks, each stricter than the last:

  --oracle   The candidate agrees with the pure-Python oracle (``hsolve.greedy_search_h``)
             field for field on many short searches, AND agrees with the frozen baseline
             engine on the full returned dict. Cheap, broad coverage (default 60 rows).

  --twin     The candidate agrees with the frozen baseline BIT-FOR-BIT on a few longer,
             real searches: every scalar the solver tracks, the discovered-state arrays
             (as numpy arrays, compared with ``array_equal``), every decoded relator string
             below the discovered count, and the exact "rows widen ..." lines the engine
             prints as it runs (captured by redirecting OS file descriptor 1 -- the numba
             kernels and the plain ``print()`` calls in ``_grow``/``_grow_width`` both write
             through that fd, and ``contextlib.redirect_stdout`` only patches
             ``sys.stdout``, which is not the same thing).

  --suite    The existing test suite (``tests/test_leftovers_5m.py``) still passes.

--all runs a, b, c in that order and stops at the first failure -- there is no reason to
spend the (slower) twin or suite gate's time once the oracle gate has already found a
divergence.

Exit code is 0 iff every requested gate passed; nonzero otherwise. Every mismatch is
printed with the concrete values on both sides, not just "differs".

    PYTHONPATH=. python3 experiments/heuristic_search/core/perf_lab/gates.py --all
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile

# ---------------------------------------------------------------------------
# Same repo-root discovery as bench.py / hcompact.py: walk up from this file.
# ---------------------------------------------------------------------------
_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
ROOT = _d
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from experiments.heuristic_search.core.perf_lab.bench import load_rows  # noqa: E402


# ---------------------------------------------------------------------------
# fd-level stdout capture. contextlib.redirect_stdout only swaps sys.stdout,
# which misses anything written straight to file descriptor 1 (numba-compiled
# code that prints, C extensions, etc); dup2 on the real fd catches all of it.
# We additionally cross-check the captured line count against ``solver.widened``
# below, which is what actually proves the capture worked rather than merely
# running without error.
# ---------------------------------------------------------------------------
def _solve_capturing_fd1(solver):
    sys.stdout.flush()
    saved_fd = os.dup(1)
    tmp = tempfile.TemporaryFile(mode="w+b")
    os.dup2(tmp.fileno(), 1)
    try:
        solved, nodes = solver.solve()
    finally:
        sys.stdout.flush()
        os.dup2(saved_fd, 1)
        os.close(saved_fd)
    tmp.seek(0)
    text = tmp.read().decode(errors="replace")
    tmp.close()
    return solved, nodes, text


def _widen_lines(text):
    return [ln for ln in text.splitlines() if "rows widen" in ln]


_WIDEN_AT = re.compile(r"rows widen .* at ([\d,]+) states")


def _widen_states(lines):
    """The 'at N states' figure of each widen line -- the part of the line that
    fingerprints the SEARCH (which pop widened the rows). The 'aB -> bB' widths
    are a property of the row layout: a candidate that stores symbols in fewer
    bits legitimately prints different widths at the very same pops."""
    out = []
    for ln in lines:
        m = _WIDEN_AT.search(ln)
        out.append(m.group(1) if m else ln)
    return out


# ---------------------------------------------------------------------------
# Gate (a): oracle
# ---------------------------------------------------------------------------
_ORACLE_FIELDS = (
    "solved", "nodes_explored", "path_length", "min_relator_length",
    "max_relator_length", "max_relator_length_expanded", "path", "path_moves",
)


def gate_oracle(args):
    from experiments.heuristic_search.core.hcompact import (
        greedy_search_hcompact as cand_solve)
    from experiments.heuristic_search.core.perf_lab.hcompact_baseline import (
        greedy_search_hcompact as base_solve)
    from experiments.heuristic_search.core.hsolve import greedy_search_h
    from experiments.search.run_leftovers_1m import S20_MK2

    row_names = [f"aca_{i}" for i in range(args.oracle_rows)]
    rows = load_rows(row_names)

    failures = []
    for name, r1, r2 in rows:
        # keep_path=False on the oracle, track_path=False on both engines: the
        # spec for this gate names the oracle call explicitly as keep_path=False,
        # and pairing that with track_path=False on the engines is what makes
        # "path"/"path_moves" a meaningful (rather than trivially-empty-either-way)
        # part of the field-for-field comparison.
        fast = cand_solve(r1, r2, args.oracle_budget, max_relator_length=args.mrl,
                          config=S20_MK2, track_path=False)
        ref = greedy_search_h(r1, r2, args.oracle_budget, args.mrl,
                              config=S20_MK2, keep_path=False)
        row_fail = []
        for k in _ORACLE_FIELDS:
            if fast[k] != ref[k]:
                row_fail.append(
                    f"field {k!r} vs oracle differs: candidate={fast[k]!r} oracle={ref[k]!r}")

        base = base_solve(r1, r2, args.oracle_budget, max_relator_length=args.mrl,
                          config=S20_MK2, track_path=False)
        if fast != base:
            diff_keys = sorted(set(fast) | set(base),
                               key=lambda k: fast.get(k) == base.get(k))
            diff_keys = [k for k in diff_keys if fast.get(k) != base.get(k)]
            for k in diff_keys:
                row_fail.append(
                    f"field {k!r} vs baseline differs: candidate={fast.get(k)!r} "
                    f"baseline={base.get(k)!r}")

        if row_fail:
            failures.append((name, row_fail))

    ok = not failures
    print(f"[oracle] {len(rows)} rows, budget={args.oracle_budget}, mrl={args.mrl}, "
         f"config=S20_MK2: {'PASS' if ok else 'FAIL'}")
    if not ok:
        print(f"  {len(failures)} of {len(rows)} rows mismatched:")
        for name, fs in failures:
            print(f"  - {name}:")
            for f in fs:
                print(f"      {f}")
    return ok


# ---------------------------------------------------------------------------
# Gate (b): twin
# ---------------------------------------------------------------------------
_TWIN_SCALAR_FIELDS = (
    "n_discovered", "min_id", "min_total", "max_id", "max_total",
    "max_expanded_id", "max_expanded_total", "solved_depth", "solved_id",
    "widened",
)
_TWIN_ARRAY_FIELDS = ("len1", "len2", "depth", "seg", "score", "parent", "pmove")


def gate_twin(args):
    import numpy as np
    from experiments.heuristic_search.core.hcompact import HCompactSolver as CandSolver
    from experiments.heuristic_search.core.perf_lab.hcompact_baseline import (
        HCompactSolver as BaseSolver)
    from experiments.search.run_leftovers_1m import S20_MK2

    row_names = [f"aca_{i}" for i in range(args.twin_rows)]
    rows = load_rows(row_names)

    failures = []
    for name, r1, r2 in rows:
        cand = CandSolver(r1, r2, max_nodes=args.twin_budget,
                          max_relator_length=args.mrl, config=S20_MK2,
                          track_path=True)
        base = BaseSolver(r1, r2, max_nodes=args.twin_budget,
                          max_relator_length=args.mrl, config=S20_MK2,
                          track_path=True)

        c_solved, c_nodes, c_text = _solve_capturing_fd1(cand)
        b_solved, b_nodes, b_text = _solve_capturing_fd1(base)
        c_widen, b_widen = _widen_lines(c_text), _widen_lines(b_text)

        row_fail = []

        if (c_solved, c_nodes) != (b_solved, b_nodes):
            row_fail.append(
                f"(solved, nodes) differs: candidate={(c_solved, c_nodes)!r} "
                f"baseline={(b_solved, b_nodes)!r}")

        for f in _TWIN_SCALAR_FIELDS:
            cv, bv = getattr(cand, f), getattr(base, f)
            if cv != bv:
                row_fail.append(f"{f} differs: candidate={cv!r} baseline={bv!r}")

        # The capture must actually be catching what the engine prints, not
        # merely running without error -- cross-check the line count against
        # the solver's own widen counter before trusting the line comparison.
        if len(c_widen) != cand.widened:
            row_fail.append(
                f"stdout capture is unreliable: candidate printed "
                f"{len(c_widen)} 'rows widen' line(s) but solver.widened={cand.widened}")
        if len(b_widen) != base.widened:
            row_fail.append(
                f"stdout capture is unreliable: baseline printed "
                f"{len(b_widen)} 'rows widen' line(s) but solver.widened={base.widened}")
        if args.widen_lines == "states":
            # layout-change mode: the state counts (and the number of widen
            # events) must match exactly; the byte widths may differ
            if _widen_states(c_widen) != _widen_states(b_widen):
                row_fail.append(
                    "'rows widen' state counts differ (--widen-lines states):\n"
                    f"      candidate: {c_widen}\n"
                    f"      baseline:  {b_widen}")
        elif c_widen != b_widen:
            row_fail.append(
                "'rows widen' stdout differs:\n"
                f"      candidate: {c_widen}\n"
                f"      baseline:  {b_widen}")

        n = min(cand.n_discovered, base.n_discovered)
        if cand.n_discovered != base.n_discovered:
            row_fail.append(
                f"n_discovered differs: candidate={cand.n_discovered} "
                f"baseline={base.n_discovered} (arrays below compared only "
                f"over the shared prefix [:{n}])")

        for arr_name in _TWIN_ARRAY_FIELDS:
            ca = getattr(cand, arr_name)[:n]
            ba = getattr(base, arr_name)[:n]
            if not np.array_equal(ca, ba):
                bad = (np.nonzero(ca != ba)[0] if ca.ndim == 1
                      else np.nonzero(np.any(ca != ba, axis=1))[0])
                msg = f"array {arr_name!r} differs over [:{n}] at {len(bad)} position(s)"
                if len(bad):
                    i = int(bad[0])
                    msg += f"; first at index {i}: candidate={ca[i]!r} baseline={ba[i]!r}"
                row_fail.append(msg)

        decode_n = min(n, args.decode_max)
        mismatch_sid = None
        for sid in range(decode_n):
            if cand.relators(sid) != base.relators(sid):
                mismatch_sid = sid
                break
        if mismatch_sid is not None:
            row_fail.append(
                f"decoded relators differ at sid={mismatch_sid} (checked "
                f"sid 0..{decode_n - 1}): candidate={cand.relators(mismatch_sid)!r} "
                f"baseline={base.relators(mismatch_sid)!r}")

        if row_fail:
            failures.append((name, row_fail))

    ok = not failures
    print(f"[twin] {len(rows)} rows, budget={args.twin_budget}, mrl={args.mrl}, "
         f"config=S20_MK2, decode-max={args.decode_max}, "
         f"widen-lines={args.widen_lines}: {'PASS' if ok else 'FAIL'}")
    if not ok:
        print(f"  {len(failures)} of {len(rows)} rows mismatched:")
        for name, fs in failures:
            print(f"  - {name}:")
            for f in fs:
                print(f"      {f}")
    return ok


# ---------------------------------------------------------------------------
# Gate (c): suite
# ---------------------------------------------------------------------------
def gate_suite(args):
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_leftovers_5m.py", "-q"],
        cwd=ROOT, capture_output=True, text=True)
    sys.stdout.write(proc.stdout)
    if proc.stderr:
        sys.stderr.write(proc.stderr)
    ok = proc.returncode == 0
    print(f"[suite] python -m pytest tests/test_leftovers_5m.py -q: "
         f"{'PASS' if ok else 'FAIL'} (returncode={proc.returncode})")
    return ok


# ---------------------------------------------------------------------------
GATES = {"oracle": gate_oracle, "twin": gate_twin, "suite": gate_suite}


def main(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--oracle", action="store_true", help="run the oracle gate")
    ap.add_argument("--oracle-rows", type=int, default=60,
                    help="check aca_0..aca_{N-1} (default 60)")
    ap.add_argument("--oracle-budget", type=int, default=1000)
    ap.add_argument("--twin", action="store_true", help="run the twin gate")
    ap.add_argument("--twin-rows", type=int, default=12,
                    help="check aca_0..aca_{N-1} (default 12)")
    ap.add_argument("--twin-budget", type=int, default=100_000)
    ap.add_argument("--decode-max", type=int, default=2_000_000,
                    help="compare at most this many decoded relators per row")
    ap.add_argument("--widen-lines", choices=("exact", "states"), default="exact",
                    help="twin: compare the 'rows widen' lines verbatim (exact, "
                         "the default) or by their 'at N states' figures only "
                         "(states) -- for a candidate whose ROW LAYOUT differs "
                         "from the baseline's, so the byte widths it prints "
                         "differ while the pops at which it widens must not")
    ap.add_argument("--mrl", type=int, default=64,
                    help="max_relator_length for both --oracle and --twin")
    ap.add_argument("--suite", action="store_true", help="run the pytest suite gate")
    ap.add_argument("--all", action="store_true",
                    help="run oracle, then twin, then suite; stop at first failure")
    args = ap.parse_args(argv)

    if args.all:
        order = ["oracle", "twin", "suite"]
    else:
        order = [g for g in ("oracle", "twin", "suite") if getattr(args, g)]
    if not order:
        ap.error("nothing to do: pass --oracle, --twin, --suite, and/or --all")

    for gate in order:
        ok = GATES[gate](args)
        print()
        if not ok:
            print(f"STOPPING at gate {gate!r}: it failed. Later gates were not run.")
            return 1

    print(f"ALL GATES PASSED: {', '.join(order)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
