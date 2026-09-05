# u124: 124 unsolved Miller-Schupp AC classes at 10M nodes (cap 64)

The u124 campaign (`results/stable_ac/fable/aca_124.csv`, 124 rows) under
s20_mk2 at a 10,000,000-node budget, max relator length 64, engine
hcompact, engine_mem_gen 2. Runs on AWS r6a-class Spot boxes; the campaign
is LIVE — files here are snapshots and will be superseded.

## Files

- `u124_10m_s20_mk2_b10000000_mrl64.jsonl` — snapshot of 2026-08-31,
  rows aca_0..aca_8: **9 full-budget completions, 0 solved** (every row
  exhausted 10M without reaching a shorter total). The two `aca_0`/`aca_1`
  error records at the top are the reservation-exhaustion deaths under the
  original 110 states/node floor (both rows exceeded it at ~111 and
  ~123/node; the grow doubling cannot fit under the child's RLIMIT_AS);
  both were retried and completed under the 1.5B reserve. Readers dedupe
  by name preferring finished records.
- `run_log_u124.log` — the campaign run.log for the same period: the two
  `reservation exceeded` lines (trip at ~1,100,016,9xx states, doubling
  target 2,200,067,600) and the width-ladder `rows widen` lines, including
  aca_1's 24B->32B repack at 1,095,951,220 states that produced its
  158.021 GB peak.

## Verification (2026-09-01)

The campaign was independently verified to be running s20_mk2 correctly:
the production CLI (`--campaign u124 --arm s20_mk2`, budget 1,000, cap 64)
was re-run twice on rows aca_0..aca_59 on a different machine (4-core
x86 container vs the campaign's 64-vCPU EPYC). The two runs are
bit-identical; all ten 12B->24B widen points in `run_log_u124.log`
(aca_0..aca_9: 523 / 2,415 / 423 / 348 / 837 / 816 / 378 / 2,127 /
13,999 / 10,641 states) reproduce to the digit -- widen points are
content-determined, so they fingerprint the search; and the pure-Python
reference `greedy_search_h` with the S20_MK2 config
(`{"L": 1.0, "S": 20.0, "MK": 2.0}`) agrees with the engine records on
every shared field for the rows spot-checked. The 24B->32B widens
(113M-1.1B states) are correctly absent at a 1k budget.

## Memory profile change (engine_mem_gen 4, 2026-09-05)

Rows recorded from gen 4 on differ from the snapshot above in two ways:

- **No path capture.** u124 runs with `track_path=False` (every completed
  row so far is unsolved, so the 8 B/state parent+move arrays were dead
  weight: 16 GiB of address space per lane at the 2.14B reservation). A
  row that solves is recorded with `solved: true`, its `path_length`, and
  EMPTY `path`/`path_moves`. Its certificate is recovered by re-running
  that one row with paths on at its recorded node count -- the search is
  deterministic, so the re-run pops the identical sequence and ends on the
  same solve (one row's time per solved row):

      python -m experiments.search.rerun_row --row aca_N --campaign u124 \
          --arm s20_mk2 --budget <nodes_explored> \
          --reserve-states 2140016900 --out-dir <dir>

  (`rerun_row` captures paths by default; pass the campaign's reservation
  so the re-run never grows.) Certify the result by replaying `path_moves`
  through `greedy_baseline.moves_to_states`, as for AC19.
- **No width-repack transient.** The arena is one full-width allocation
  and rows widen in place, so aca_1's 158.0 GB peak (old 24B rows + new
  32B rows + fixed arrays + table, held at once during the copy) can no
  longer occur: the same row now peaks at its steady state, ~109 GB. The
  allocation-backed worst per lane at the 214 states/node floor is
  181.4 GiB (was 205 with paths and a 12 B/state table amortisation):
  two lanes on a 512 GiB box, one on the 256 GiB class (zero before),
  eight on 1.5 TiB.

## Memory profile change (engine_mem_gen 5, 2026-09-05)

The engine now packs symbols at 2 bits (32 B per state at cap 64 instead
of 64) with a length-aware comparator proved and pinned to reproduce the
old tie-break order exactly, and its expansion kernel allocates nothing
per child. The search is bit-identical to every earlier generation
(oracle and frozen-engine gates in `experiments/heuristic_search/core/
perf_lab/`); the numbers that change are memory and speed:

- allocation-backed worst per lane at the 214 floor, no paths: 117.6 GiB
  (was 181.4): four lanes on a 512 GiB box, two on the 256 GiB class,
  twelve on 1.5 TiB;
- physical peak of a 186 states/node row: ~104 GiB (was ~160);
- pops per second per lane: unchanged at campaign length for the
  `3093592d` build (the lab's 1.7x was a short-relator artefact; first
  four rows ran 12,320 to 13,428 s against 11,202 to 13,775 s before, at
  96.7 to 101.1 GB peak against 155 to 156 GB). The campaign-length work
  that followed (cut-shift skip and packed-word canonicalisation, REPORT.md
  section 8) measures 2.34x at 300k pops on aca_47 on the lab box against
  that build, pending the operator's confirmation on the campaign box.

The widen lines now print 2-bit widths ("6B -> 12B" where the archived
log says "12B -> 24B"); the "at N states" figures, which are the search's
fingerprint, are unchanged. Full method, tables and verification commands:
`experiments/heuristic_search/core/perf_lab/REPORT.md`.

## Notable

All nine completions are rigid at this budget: `min_relator_length`
equals the starting total and `min_relator` is the starting pair,
unchanged, for every row. Peaks span 87.7-158.0 GB; the only row above
~140 is aca_1, whose peak is the width-repack transient, not steady
state. Widest expansions reach totals of 41-54 against the per-relator
cap of 64.
