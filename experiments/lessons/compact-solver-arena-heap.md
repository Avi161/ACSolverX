# [2026-07-09] Unique keys make the heap implementation free to change [WORKS]

## What happened

A 1M-node / `mrl=48` heavy search discovers ~63.7M states at a measured **220 B
each** → ~14 GB, peaking at 20.4 GB. On a 53 GB Colab runtime `_auto_workers`
returned 3, each worker's `1/n` share was 15.9 GB, and `_MemGuard` tripped on the
heavy tail. Throughput was capped by memory, not by cores.

Almost none of the 220 B was data. Per discovered state, CPython held:

| structure | B/state | what it is |
|---|---|---|
| `bytes` key object | ~125 | 33 B object header + ~92 B payload |
| its `set` entry | ~32 | hash + pointer, amortised |
| heap tuple `(total, depth, key)` | 48 | pure `PyTupleObject` overhead |
| heap list slot | ~9 | pointer + list overallocation |

**~70% is object overhead.** `expand_node_nj` — the actual mathematics — was
already `@njit` and was never the problem. Only the containers needed to change.

`experiments/search/greedy_compact.py` holds a state in numpy: a nibble-packed
fixed-width `arena` row, `len1`/`len2`/`depth` side arrays, an `int32` heap of
state ids, and an open-addressing `int32` visited table. **74.8 B/state at
1M/mrl48** — and that number is *arithmetic*, not a measurement.

## The load-bearing argument

A rewrite of the frontier looks like it must change the pop order. It does not,
and the reason is worth stating precisely:

> Every state is pushed **exactly once** — it is checked against `visited` before
> being pushed — so no two heap entries carry the same row. `(total, depth, row)`
> is therefore a **strict** total order with **no true ties**. The pop sequence is
> determined by the ordering relation alone, not by the heap implementation.

`heapq` is not a stable heap, and it never needs to be: no two entries compare
equal, so there is nothing for stability to decide. Any correct binary heap with
the same comparison pops in the same sequence. That single observation is what
made a numpy heap safe, and it is the first thing to check before touching a
priority queue anywhere.

Three things then had to be preserved, and each is preserved *by construction*:

1. **The row sorts like the old key.** The old key is `c1 + b'\x00' + c2` over
   order-preserving codes `X=1 < Y=2 < x=3 < y=4`. Nibbles are stored
   most-significant-first, so within a byte `16*hi + lo` is dominated by `hi` and
   nibble order *is* byte order. `0` pads below every code, reproducing `str`'s
   shorter-prefix-is-smaller rule at the first past-the-end slot. Each relator
   gets its own byte-aligned `(cap+1)//2`-byte region, so a short r1 cannot shift
   r2. Both a naive back-to-back packer and an LSB-nibble-first packer **fail**
   the sort test — it is not a formality.
2. **Children are enumerated in the same order**, because `depth` is fixed by
   first-visit order. `expand_node_nj` is reused verbatim.
3. **min/max update at the same moments**: `max_expanded` on POP, `min`/`max` on
   DISCOVERY with an `elif` (a first state that is both a new min and a new max
   updates only the min). The `elif` is load-bearing.

Because heavy and compact both take the *first-seen* extreme, their `min_relator`
and `max_relator` **strings** must match exactly — unlike normal, which
tie-breaks over a `set` and follows `PYTHONHASHSEED`. Asserting those strings is
a direct assertion that discovery order is identical, and it is worth more than
any other single check.

## Reserve; never copy

`np.empty` returns lazily-faulted pages. The arrays are allocated once at
`1.5 x est_states(budget)` and **never grown in practice**, so a presentation
that solves after 200 nodes touches ~200 rows and its RSS reflects that, not the
reservation. Preallocating is therefore not wasteful on Linux, and it dodges the
real hazard: a grow-by-copy on a 3 GB arena holds old **and** new simultaneously,
and four workers resizing near-simultaneously is a 30 GB spike — precisely the
failure being removed. Growth exists as a backstop, logs loudly, and never fired.

## Two numba traps, both silent

- **A ternary unifies `uint8` with `int64` to `float64`.** `return (b >> 4) if
  (t & 1) == 0 else (b & 15)` typed as `float64`, and the error surfaced twenty
  frames later as `set_intersection ... got (float64, int64)`. Cast **both**
  branches to `int64` explicitly.
- **A `uint64` cannot cross the Python boundary and come back.** `_fnv` returns
  `uint64`; calling it from Python unboxes to a Python int larger than `int64`,
  and passing it back into an `@njit` function raises `OverflowError: int too big
  to convert`. Pack the initial state inside njit rather than in `__init__`.

Also: numba refuses to unify `uint64` with `int64` in a bitwise op, so
`h & tmask` needs `np.uint64(tmask)`.

## Measuring honestly under a 1,000-node cap

`tools/bytes_per_state.py` reports both solvers and never runs a search above the
ceiling. Two rules it obeys:

- **Warm numba before starting `tracemalloc`.** First-call compilation allocates
  tens of MB through CPython's allocator; measured inside the window a 37k-state
  search read **850 B/state** — four times the truth, and it looks like a result.
- **Calibrate at the key lengths the deep search actually holds.** Heavy costs
  199 B/state at 40-byte keys and 251 at 92-byte keys; the compact row is fixed
  by the cap and does not move. The shipped `_BYTES_PER_STATE = 220` sits at
  keylen ~60. My construction is *not* identical to the one that produced 214 in
  [gb-per-pres-sized-from-measured-memory](gb-per-pres-sized-from-measured-memory.md),
  so it corroborates the slope, not the constant. Say so rather than claiming a
  reproduction.
- Size the constant at **peak, not floor**: `_BYTES_PER_STATE_COMPACT = 80`
  covers the 74.8 B arithmetic with room for a doubling transient. The 58 B floor
  (row + side arrays, table excluded) would under-provision and re-create the
  guard trip in a new solver.

## Results, all at the 1,000-node ceiling

- **parity**: 0 mismatches over 48 searches × 8 fields (cap 24/48 × cyclic T/F),
  including the first-seen extreme strings; `n_discovered` identical (37,576)
- **fork + pool**: 3 forked workers × 12 presentations → 12 rows, 0 dupes, 0
  mismatches (macOS defaults to `spawn`, so fork must be forced to test it)
- **speed**: 1.48× (109 vs 162 µs/node) on presentations that never solve. Speed
  was never the goal; measure it on inputs that *spend* the budget — ms640 solves
  in ~5 nodes and reports pure noise.
- **memory**: 190.4 → 85.9 B/state at equal state count (2.22× at shallow keys);
  2.94× projected at 1M, where heavy's key payload grows and the row does not
- **workers**: `_auto_workers` at 1M on 53 GB / 8 cores goes **3 → 8**. RAM stops
  binding; cores become the limit.

## Rules

- **Before rewriting a priority queue, ask whether its keys are unique.** If they
  are, the order is a property of the comparison, not of the heap, and the
  implementation is free. If they are not, stability is a silent correctness
  requirement.
- **A result-neutral knob stays out of `_run_prefix`.** `SOLVER` sits in
  `test_runner_paths.EXCLUDED`, and that placement *is* the claim that the
  solvers agree. A run started under one resumes under the other.
- **Assert the first-seen extremes.** Two solvers that agree on `nodes_explored`
  might still discover in a different order; `min_relator`/`max_relator` strings
  catch that, and cost nothing.
- **A fixed-width encoding needs a full-width, prefix-heavy, last-symbol-differing
  corpus.** The shallow 7225-pair corpus passes for a *wrong* packer.
- **Warm the JIT before you measure memory**, and never calibrate on macOS
  `ru_maxrss`.

## Related

[gb-per-pres-sized-from-measured-memory](gb-per-pres-sized-from-measured-memory.md)
— why the guard is system-pressure-based, and the `ru_maxrss` trap.
[high-speedup-boxing-and-memory](high-speedup-boxing-and-memory.md) — the first
round of this fight: boxing was the cost, memory the cap, and the packed key had
to sort like `(str, str)`. This lesson is that argument taken one layer further.
[test-budget-ceiling](test-budget-ceiling.md) — why none of the above needed a
search above 1,000 nodes.
