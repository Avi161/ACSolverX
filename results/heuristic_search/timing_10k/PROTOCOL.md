# Matched four-method comparison at 10,000 pops

The user explicitly requested 10,000 pops per presentation and clarified
that there is **no timeout**. The primary time comparison is the arithmetic
mean search time on the exact presentations both methods solve.

## Fixed methods and inputs

All 60 rows of `benchmark/subsets/benchmark_subset_60.json`, in file order:

| Record name | Priority | Generator-change neighbors |
|---|---|---|
| greedy | L | off |
| s20_mk2 | L+20S+2MK | off |
| s40_gen | L+40S | four fixed Nielsen moves |
| s20_w1p5_gen | L+20S+1.5W | the same four moves |

Every method uses relator cap 48, path capture, and the same compiled packed
expansion, Python heap and parent map in `heuristic_1k.mixed_search`.
Each heap pop, including a terminal pop, consumes one unit of the common
10,000-pop budget. Generator moves add neighbors to the same heap and use
that same counter. Roots and states are canonically cyclically reduced,
inverted and ordered; they are not forced to be Aut-minimal.

No scoring or expansion code is changed for this benchmark. The existing
`heuristic_1k.run` CLI/API retains its 1,000-pop ceiling. The dedicated
timing driver validates a maximum budget of 10,000 and invokes the same
underlying search function. Mixed generator/substitution certificates are
reported as such, not as ordinary substitution-only certificates.

## Clocks and local load

One serial worker, numerical-library thread limits 1, no overlapping
presentation searches. Method order rotates by row, so each method occupies
each position 15 times. After every search there is a cooldown of at least
max(0.5 seconds, the preceding search wall time). macOS chooses the physical
core; the manifest records whether the scheduling-priority request succeeds.

`perf_counter` wall time and `process_time` CPU time surround the entire
search function call. This includes initialization, path reconstruction and
local search-object cleanup. Compilation/warm-up, explicit pre-search
garbage collection, certificate verification, historical comparisons,
file output and cooldown are excluded.

There is one measured pass per method and presentation. Timing ratios are
descriptive measurements on this machine; repeated-run noise is not estimated.

## Verification and comparison

A synthetic-record test checks that pairwise means use actual intersections
rather than the smaller solve count, including empty intersections and
duplicate/missing row rejection. A four-method, one-presentation preflight
uses the previous 1k budget before the full benchmark.

Every solve is independently replayed. For rows already solved by the same
method at 1k, the 10k result must have identical pop count, state path, move
path and generator-evaluation count. A former1k failure can only become a
solve after pop 1,000. Inputs, implementation and previous-result hashes are
pinned in the manifest and checked again at the end of the run.

For methods A and B, let I be the intersection of their solved presentation
IDs. Report |I| and, separately for each method, sum(search_time over I)/|I|.
Compute all six pairs and the intersection of all four methods. Unsolved
rows are excluded from shared-solve means; all 60 searches are included in
total workload times and budgeted pop totals. Per-row JSON records preserve
the IDs and measurements needed to reproduce every mean.

This is a budget extension on the same subset previously used for selecting
the two new methods, not independent validation or a change to production.

## Reproduction

From the repository root, use a fresh output directory:

```sh
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 NUMBA_NUM_THREADS=1 .venv/bin/python -m experiments.search.time_heuristic_10k --out results/heuristic_search/timing_10k_repeat
```
