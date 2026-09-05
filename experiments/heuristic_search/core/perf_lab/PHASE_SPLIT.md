# Phase split of one `hcompact` pop (the memo's M0)

Measured with `phase_split.py` on this box (4 cores / 15 GB, Intel Xeon @ 2.8 GHz
nominal, 1 MiB L2 per core, 33 MiB shared L3, one NUMA node), pinned to core 2
while another agent's jobs ran on cores 1 and 3. Rows `aca_0`, `aca_4`, `aca_5`
from `results/stable_ac/fable/aca_124.csv`; config `S20_MK2`; cap 64; **50,000
pops** per row; three replay reps per phase, medians reported. The engine was
the working copy of `hcompact.py` at commit `9b98e313` (identical to the frozen
baseline for everything this measures).

    PYTHONPATH=. python3 experiments/heuristic_search/core/perf_lab/phase_split.py \
        --rows aca_0,aca_4,aca_5 --budget 50000 --reps 3 --cpu 2 --out split.json

## How it was measured (replay, not instrumentation of the engine)

1. A `RecordingSolver` runs the live engine's `solve()` with a verbatim copy of
   `_run_chunk_h` that additionally stores, per pop, the popped state id and the
   discovered-count after that pop's children. The engine file is untouched; the
   recording run's wall time matched a plain `greedy_search_hcompact` run within
   1-3 % on every row (33.6 vs 34.1 s, 52.2 vs 51.1 s, 56.2 vs 55.9 s), and its
   final scalars (`nodes`, min/max/expanded totals) are asserted equal.
2. Each phase is then replayed on its own, in an `@njit` kernel over batches of
   64 pops, against the run's final arrays:
   - **expand**: `_decode` + `expand_and_score_nj` over the recorded pop sequence.
   - **lascan**: the per-candidate scan for the separator byte that yields `la`.
   - **hash**: `_hash_codes` over every candidate (candidates materialised first).
   - **probe**: `_lookup_codes` for every candidate against the final table/arena,
     hash precomputed.
   - **pack**: zero + nibble-pack a row for each candidate that was new.
   - **sift**: the whole heap replayed (pop / sift-down, then push / sift-up of the
     recorded id ranges). The replay asserts `heap[0] == popped[i]` at every one
     of the 150,000 pops -- it did -- which is what proves the replay is the run.
3. `total` is the plain engine's measured wall time per pop; `residual` is
   `total - sum(phases)`.

## The split

| phase    | aca_0            | aca_4            | aca_5            |
|----------|------------------|------------------|------------------|
| expand   | 551.2 us  81.9 % | 854.0 us  81.7 % | 958.3 us  85.3 % |
| lascan   |   2.8 us   0.4 % |   4.5 us   0.4 % |   5.2 us   0.5 % |
| hash     |   7.2 us   1.1 % |  11.4 us   1.1 % |  13.1 us   1.2 % |
| probe    |  53.0 us   7.9 % |  80.5 us   7.7 % |  87.9 us   7.8 % |
| pack     |   7.0 us   1.0 % |   9.5 us   0.9 % |  10.6 us   0.9 % |
| sift     |   5.2 us   0.8 % |   8.5 us   0.8 % |   7.2 us   0.6 % |
| residual |  46.6 us   6.9 % |  76.3 us   7.3 % |  41.0 us   3.7 % |
| **total**| **672.9 us**     | **1044.6 us**    | **1123.3 us**    |

Diagnostics from the same replay (the memo's M2, M3, M5, M10):

| quantity                         | aca_0     | aca_4     | aca_5     |
|----------------------------------|-----------|-----------|-----------|
| states discovered at 50k pops    | 5,058,499 | 6,081,190 | 6,173,152 |
| candidates / pop                 | 172.0     | 236.8     | 240.7     |
| symbols / candidate              | 38.2      | 42.6      | 42.8      |
| mean popped total length         | 28.1      | 31.3      | 31.4      |
| inserts / pop                    | 101.2     | 121.6     | 123.5     |
| miss rate (new / candidates)     | 0.588     | 0.514     | 0.513     |
| intra-pop duplicate fraction     | 0.239     | 0.287     | 0.293     |
| slots visited / lookup (final)   | 1.218     | 1.107     | 1.109     |
| row compares / lookup (final)    | 1.003     | 1.001     | 1.001     |
| final table load factor          | 0.302     | 0.181     | 0.184     |
| row bytes at the end             | 48        | 48        | 48        |
| widens / grows                   | 1 / 0     | 1 / 1     | 1 / 1     |

## What it says

- **The pop is compute-bound in the expansion kernel, not memory-bound in the
  dedup probe.** `expand_and_score_nj` is 82-85 % of the pop on all three rows.
  The whole dedup side (lascan + hash + probe + pack) is 10-11 %; the heap is
  under 1 %. The memo's "FNV-1a is ~40 % of the pop" is off by a factor of ~35 at
  this budget (1.1 %), and "dedup DRAM traffic 30-50 %" by ~4-6x (7.8 %).
- **Why the memo's premise failed here:** at 50k pops the popped states are
  ~28-31 symbols and candidates ~38-43 symbols, not the ~86 the memo inferred
  from campaign-scale candidate counts, and the candidate count is 172-241 per
  pop, not ~1,850. Every memory-side cost scales linearly with symbols, while
  expansion's canonicalisation per child is Booth's algorithm twice plus a
  reduce, all with per-child allocations, and its pass-1 filter is quadratic in
  the relator lengths -- so at campaign lengths expansion's share would, if
  anything, grow. (That last sentence is an inference from the operation
  counts, not a measurement; the campaign box is where it should be checked.)
- **The miss rate is 51-59 %, not 6 %.** Half of all candidates are new states at
  this budget. That halves the value of anything that only helps the hit path.
- **Intra-pop duplicates are 24-29 % of candidates** (M3), which is large as a
  fraction -- but they land on a phase that is ~9 % of the pop, so skipping their
  global probe is worth at most ~2-3 % here. Re-evaluate after the expansion
  work, when the dedup share is larger.
- **Probe geometry is benign:** 1.1-1.2 slots per lookup, essentially one row
  compare per lookup, final load factor 0.18-0.30. FNV's low bits are not
  clustering here.

## Caveats on the replay

- The probe replay hits the final table, in which every candidate is present;
  in the live run 51-59 % of lookups ended at an empty slot instead of a row.
  Both cost about one dependent line (the row, or the length arrays before it),
  so the phase is the right order of magnitude, but it is not the live number.
- The heap replay runs back to back, cache-warmer than the live interleaving;
  the sift figure is a floor.
- Each phase is timed in isolation, so any out-of-order overlap the live loop
  gets between phases is lost; that, plus `_insert`, the min/max bookkeeping,
  the Python chunk loop and (on `aca_4`/`aca_5`) one reservation-exceeded grow
  copy of ~5M states, is the residual of 4-7 %.

## Decision: the order of work

The split reorders the memo's shortlist. Expansion first (the memo's item 3:
exact-index rotation, hoisted inverse relators, scratch buffers instead of
per-child allocations), because 82-85 % of the pop lives there and each of
those transformations is provable by construction. Then the zero-terminator
equality (item 2 in the memo, step 1 in the plan), whose ceiling here is a few
percent of the pop but whose share doubles once expansion is cheaper. Then the
hash, which at 1.1 % can only be kept as a pure cleanup with no loss. Intra-pop
dedup and prefetching are re-decided after re-running this split.

A second finding from the hash micro-bench that fed the design (not part of
the table above, measured on core 0 with synthetic candidates of 45 symbols):
numba emits a signed-index wraparound check on every `blob[o + t]`, and
FNV-1a with unsigned indices runs 35 ns/candidate against 52.5 ns with signed
ones -- the same values, one third less time. The serial `xor`/`imul` chain the
memo blamed is not the bottleneck: a 4-lane variant that breaks the chain is no
faster than single-lane FNV below ~60 symbols. The same wraparound cost applies
to every 2-D `rel[i, 0]` read in the expansion kernels.
