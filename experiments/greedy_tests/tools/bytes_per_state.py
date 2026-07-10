"""Bytes per discovered state, for the heavy and compact solvers.

    .venv/bin/python3 -m experiments.greedy_tests.tools.bytes_per_state

This is what ``_BYTES_PER_STATE`` and ``_BYTES_PER_STATE_COMPACT`` in
``run_baseline`` are derived from, and it never runs a search above the repo's
1,000-node ceiling.

Two rules govern how the numbers below are obtained, both learned the hard way:

* **Never calibrate on macOS ``ru_maxrss``.** The memory compressor evicts cold
  heap pages, so measured bytes/state *falls* as states grow -- physically
  impossible, and it once made a 14 GB working set read as 0.59 GB resident.
  ``tracemalloc`` counts CPython allocations and is platform-independent.
  See ``lessons/gb-per-pres-sized-from-measured-memory.md``.
* **Calibrate at the key lengths the deep search actually holds.** The heavy
  solver's cost is dominated by a ``bytes`` object whose payload is the relator
  pair, so a shallow search reads ~185 B/state and a 1M-node one ~214. The
  compact solver has no such dependence: its row is fixed at ``2*((cap+1)//2)``
  bytes whatever the relators do. That difference is the entire result.

So the heavy solver is measured twice -- once from a real (shallow) search, once
by constructing its exact structures at deep key lengths -- and the compact
solver is not measured at all. With numpy arrays its footprint is *arithmetic*:
``arena + len1 + len2 + depth + heap + table``, exact at any state count.
"""

import heapq
import sys
import tracemalloc

from experiments.search.greedy_baseline import GreedyHeavySolver
from experiments.search.greedy_compact import (
    GreedyCompactSolver, _next_pow2, est_states, row_width,
)
from experiments.run_baseline import load_dataset

MAX_BUDGET = 1_000          # repo hard rule; never raise it here
_RESERVE_SLACK = 1.5        # must match greedy_compact._RESERVE_SLACK


def _warm(r1, r2, cap):
    """Compile every njit kernel BEFORE tracemalloc starts.

    numba's first-call compilation allocates tens of MB through CPython's
    allocator. Measured inside the window it reads as ~850 B/state on a 37k-state
    search -- four times the truth, and it looks like a real result.
    """
    GreedyHeavySolver(r1, r2, max_nodes=2, max_relator_length=cap).solve()
    GreedyCompactSolver(r1, r2, max_nodes=2, max_relator_length=cap).solve()


def _heavy_live_bytes(r1, r2, budget, cap):
    """visited + heap of a REAL search, via tracemalloc. Shallow keys."""
    tracemalloc.start()
    base = tracemalloc.get_traced_memory()[0]
    s = GreedyHeavySolver(r1, r2, max_nodes=budget, max_relator_length=cap)
    s.solve()
    used = tracemalloc.get_traced_memory()[0] - base
    n = s.n_discovered
    tracemalloc.stop()
    del s
    return used, n


def _heavy_bytes_at_key_length(n, keylen, depth_span):
    """Build the heavy solver's exact structures at a chosen key length.

    A 1M-node search holds ~92-byte keys (two ~45-symbol relators plus the 0x00
    separator). No search is run: the set and heap are populated directly, which
    is the only honest way to reach 1M-depth key lengths under a 1,000-node cap.
    """
    tracemalloc.start()
    base = tracemalloc.get_traced_memory()[0]
    visited, pq = set(), []
    for i in range(n):
        key = i.to_bytes(6, 'big') + bytes([(i % 4) + 1]) * (keylen - 6)
        visited.add(key)
        heapq.heappush(pq, (keylen - 1, i % depth_span, key))
    used = tracemalloc.get_traced_memory()[0] - base
    tracemalloc.stop()
    del visited, pq
    return used


def _compact_bytes(n, cap):
    """Exact. Touched bytes at ``n`` discovered states, plus the whole table."""
    rw = row_width(cap)
    states_cap = max(1024, int(est_states(1_000_000) * _RESERVE_SLACK)) \
        + 4 * (cap + 1) ** 2
    tcap = _next_pow2(2 * states_cap)
    # arena + len1 + len2 + depth + heap are indexed densely 0..n-1;
    # the table is hashed into, so effectively every page is touched.
    return n * (rw + 1 + 1 + 4 + 4) + tcap * 4, tcap


def main():
    pres = [(a, b) for _, a, b in
            load_dataset("data/ms_unsolved_reps/ms_reps_unsolved.txt", None)][:1]
    r1, r2 = pres[0]
    cap = 48

    print(f"python {sys.version.split()[0]} | cap={cap} | "
          f"budget={MAX_BUDGET} (repo ceiling)\n")

    # --- 1. a real, shallow search: both solvers, same state count -----------
    _warm(r1, r2, cap)
    used, n = _heavy_live_bytes(r1, r2, MAX_BUDGET, cap)
    c = GreedyCompactSolver(r1, r2, max_nodes=MAX_BUDGET, max_relator_length=cap)
    c.solve()
    assert c.n_discovered == n, (c.n_discovered, n)   # parity, incidentally
    ctouched = n * (c.rw + 10) + c.tcap * 4

    print(f"REAL SEARCH  n_discovered = {n:,}  (identical for both -- dedup parity)")
    print(f"  heavy    visited+heap   {used / n:7.1f} B/state   ({used / 1e6:.2f} MB)")
    print(f"  compact  touched        {ctouched / n:7.1f} B/state   "
          f"({ctouched / 1e6:.2f} MB, exact)")
    print(f"  compact  grew {c.grew} time(s); reserved "
          f"{c.bytes_reserved() / 1e6:.1f} MB of virtual address space")
    print(f"  ratio    {used / ctouched:.2f}x at equal state count\n")
    print("  NB shallow keys FLATTER the heavy solver: its key payload is short")
    print("     here, while the compact row is already full width. The gap widens")
    print("     with depth, which is the whole point.\n")

    # --- 2. heavy at the key lengths a 1M search really holds ---------------
    print("HEAVY, at 1M-search key lengths (structures built, no search run)")
    for keylen in (40, 68, 92):
        for n_keys in (200_000, 400_000):
            b = _heavy_bytes_at_key_length(n_keys, keylen, 300)
            print(f"  keylen={keylen:3d} B  n={n_keys:,}   {b / n_keys:7.1f} B/state")
    print("  -> flat in n, and rises ~1.3 B per byte of key. The shipped")
    print("     _BYTES_PER_STATE = 220 sits at keylen ~60. This construction is")
    print("     NOT identical to the one in the lesson (tuple/int-caching details")
    print("     differ), so treat it as corroborating the slope, not the constant.\n")

    # --- 3. compact, projected to the production budget --------------------
    print("COMPACT, exact arithmetic at the projected 1M-node state count")
    n1m = est_states(1_000_000)
    for cp in (24, 48):
        total, tcap = _compact_bytes(n1m, cp)
        print(f"  cap={cp}  n={n1m:,}  {total / n1m:6.1f} B/state  "
              f"= {total / 1e9:5.2f} GB   (table {tcap * 4 / 1e9:.2f} GB)")
    total48, _ = _compact_bytes(n1m, 48)
    print(f"\n  headline: {total48 / n1m:.0f} B/state at cap=48 vs 220 for heavy "
          f"-> {220 / (total48 / n1m):.2f}x")
    print(f"  a 1M search: {total48 / 1e9:.2f} GB + 0.35 GB base, x1.3 spread "
          f"= {(total48 / 1e9 * 1.3 + 0.35):.2f} GB worst case")
    print(f"  _BYTES_PER_STATE_COMPACT should be >= {total48 / n1m:.0f} "
          f"(peak-inclusive, not the {row_width(48) + 10} B floor)")


if __name__ == "__main__":
    main()
