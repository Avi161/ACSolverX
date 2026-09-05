# hcompact performance lab: results, what was promoted, how to verify

Date: 2026-09-05. Baseline engine: `5d047da5` (nibble rows, in-place
widen, u124 without path capture). Everything below was measured on the
lab box (4 cores, 15 GB, Intel Xeon 2.8 GHz nominal, one NUMA node) unless
a line says otherwise, with the harness under
`experiments/heuristic_search/core/perf_lab/`. Campaign boxes are AMD
Milan (r6a) or Naples (r5a); absolute pops/s differ there, ratios are the
claim.

## 1. What changed in the engine (all promoted, all bit-identical)

| change | where | effect measured | identity argument |
|---|---|---|---|
| 2-bit symbol packing: code-1 in two bits, most-significant field first, regions of `(cap+3)//4` bytes, length-aware comparator `_row_less_h` | `hcompact.py` | bytes/state 83 -> 51 at cap width without paths (-38.6%); 56.4 -> 44.4 at the starting width (-21.3%); peak RSS -23% to -27% at 100k pops; pops/s 1.00x to 1.03x | the comparator reproduces the nibble memcmp order pair for pair (proof in its docstring; sort corpus of ~171M ordered pairs against `greedy_compact.pack_row`); metadata arrays unchanged; widen events land on the same pops |
| expansion kernel: exact rotation index instead of a modulo, inverse relators hoisted out of the per-child loop, zero allocations per child (scratch-buffer reduce, Booth canonicalisation, inverse) | `greedy_baseline.py` | pops/s 1.72x to 1.74x on four rows (50k pops, 3 reps); per-pop time 672.9 -> 403.8 us (aca_0), 1044.6 -> 608.2 (aca_4), 1123.3 -> 622.3 (aca_5) | every produced value and its order is unchanged: golden 741/741 real popped states against a pre-change snapshot and against `expand_node_nj`; `tests/test_expand_kernel.py` pins it |
| candidate hash indexed through uint64 | `hcompact.py` `_hash_codes` | hash phase -28% to -36%; pop-level 1.01x median (noise) | same 64-bit value on every input (`tests/test_hcompact_kernels.py`: three-way equality with `_hash_row` and the frozen engine's hash on thousands of random states at every width and on real rows) |

Rejected or deferred, with the measurement that decided it:

- Zero-terminator equality (infer stored lengths from zero padding, skip the
  `len1`/`len2` reads): implemented and unit-tested on nibble rows, but 2-bit
  rows have no spare code for padding, so it cannot coexist with the memory
  change. Dropped. Its ceiling was the probe's 8% to 11% share anyway.
- Word-at-a-time hash: no faster than FNV-1a below ~60 symbols per
  candidate (52.7 vs 52.7 ns), 19% to 30% faster at 80; candidates are 38 to
  43 symbols at 50k pops. Rejected (changes values for no gain).
- Intra-pop candidate dedup: 24% to 29% of a pop's candidates repeat a
  candidate of the same pop, but on a phase that is 9% to 11% of the pop the
  ceiling is ~3%. Deferred.
- Tagged / bucketized hash tables, higher load factors, Bloom filters,
  priority-queue redesigns: rejected on arithmetic in the research memo
  (94% of lookups are hits that must dereference the row regardless; the
  heap is under 1% of a pop).

## 2. The phase split that ordered the work

Replay micro-benchmarks (`perf_lab/phase_split.py`, method in
`PHASE_SPLIT.md`), 50,000 pops, S20_MK2, cap 64, medians of 3 reps:

| phase | aca_0 | aca_4 | aca_5 |
|---|---|---|---|
| expand | 551.2 us (81.9%) | 854.0 us (81.7%) | 958.3 us (85.3%) |
| la-scan | 2.8 us | 4.5 us | 5.2 us |
| hash | 7.2 us (1.1%) | 11.4 us (1.1%) | 13.1 us (1.2%) |
| probe | 53.0 us (7.9%) | 80.5 us (7.7%) | 87.9 us (7.8%) |
| pack | 7.0 us | 9.5 us | 10.6 us |
| heap sifts | 5.2 us (0.8%) | 8.5 us (0.8%) | 7.2 us (0.6%) |
| total per pop | 672.9 us | 1044.6 us | 1123.3 us |

After the expansion change: 403.8 / 608.2 / 622.3 us per pop; expansion is
then ~70% of a pop and the dedup side ~16%.

Diagnostics at the same budget: 172 to 241 candidates per pop, 38 to 43
symbols per candidate, miss rate 51% to 59%, 1.1 to 1.2 slots visited per
lookup, 1.00 row compares per lookup.

## 3. Measured results per track

Memory track, final bench (100k pops, 3 reps, core 3, frozen nibble engine
vs 2-bit engine, both on the old expansion kernel):

| row | B/state | peak RSS GiB | pops/s ratio |
|---|---|---|---|
| aca_0 | 56.4 -> 44.4 | 1.665 -> 1.218 | 1.0035 |
| aca_1 | 56.4 -> 44.4 | 1.665 -> 1.217 | 1.0203 |
| aca_3 | 56.4 -> 44.4 | 0.858 -> 0.653 | 1.0035 |
| aca_4 | 56.4 -> 44.4 | 1.665 -> 1.219 | 1.0277 |
| aca_5 | 56.4 -> 44.4 | 1.663 -> 1.218 | 1.0173 |
| aca_8 | 56.4 -> 44.4 | 0.833 -> 0.637 | 1.0065 |

Speed track, expansion-kernel bench (50k pops, 3 reps, core 2, frozen
kernels vs new kernel, both on nibble rows):

| row | pops/s frozen -> new | ratio |
|---|---|---|
| aca_0 | 1,502.7 -> 2,589.7 | 1.7234 |
| aca_4 | 985.6 -> 1,708.3 | 1.7332 |
| aca_5 | 964.0 -> 1,677.3 | 1.7399 |
| aca_8 | 1,722.9 -> 2,999.1 | 1.7407 |

Combined: the integrated engine (2-bit rows + new expansion kernel + hash
cleanup) against the fully frozen engine, 100k pops, 3 reps:

| row | pops/s frozen -> integrated | ratio | peak RSS GiB frozen -> integrated | B/state |
|---|---|---|---|---|
| aca_0 | 1,385.7 -> 2,342.5 | 1.6905 | 1.663 -> 1.217 | 56.4 -> 44.4 |
| aca_1 | 1,253.1 -> 2,130.7 | 1.7003 | 1.665 -> 1.217 | 56.4 -> 44.4 |
| aca_3 | 1,597.5 -> 2,772.3 | 1.7355 | 0.859 -> 0.654 | 56.4 -> 44.4 |
| aca_4 | 927.0 -> 1,653.2 | 1.7833 | 1.665 -> 1.217 | 56.4 -> 44.4 |
| aca_5 | 904.3 -> 1,635.8 | 1.8089 | 1.664 -> 1.217 | 56.4 -> 44.4 |
| aca_8 | 1,592.0 -> 2,784.5 | 1.7491 | 0.833 -> 0.636 | 56.4 -> 44.4 |

Median ratio 1.7423, geometric mean 1.7441; record fingerprints agree on
every row and every rep (the two engines search identically); core 2,
wall 40m50s; raw output in `perf_lab/results/combined_bench_2026-09-05.json`.

## 4. Campaign-level expectations (u124, 214 states/node floor, no paths)

| quantity | before (`5d047da5`) | after | basis |
|---|---|---|---|
| bytes per reserved state | 83 | 51 | allocation arithmetic |
| allocation per lane at 2,140,016,900 states | 181.4 GiB | 117.6 GiB | `plan_memory` |
| lanes on 512 GiB (489 admissible) | 2 | 4 | governor arithmetic |
| lanes on the 256 GiB class (246) | 1 | 2 | governor arithmetic |
| lanes on 1.5 TiB (1532) | 8 | 12 | governor arithmetic |
| physical peak of a 186 states/node row at cap width | ~160 GiB | ~104 GiB | 1.86B x 51 B + 16 GiB table |
| pops/s per lane | 1.0x | ~1.0x (0.95x to 1.15x) | MEASURED on the campaign box at 34% depth, see section 7; the lab's 1.7x did not carry to campaign-length relators |
| throughput per 512 GiB box | 1.0x | ~2.0x | lanes only: 2 -> 4 |
| cost per 186/node row, on-demand r6a.16xlarge at $3.63/h | ~$5.4 | ~$2.7 | 3 h per row, 4 lanes |

Caveats a verifier should keep: the per-lane speed factor of 1.7x was
measured at 50k to 100k pops on a Xeon lab box, where candidates are 38 to
43 symbols. On the campaign box at campaign length it is ~1.0x (section 7):
the kernel change removed per-child overhead, and at 50 symbols per
candidate the per-symbol loops dominate. The memory figures carried over
exactly. The lane counts are exact
arithmetic on the new allocation and will show in `run_remote.sh plan`.
Rows already recorded under earlier engine generations remain valid
results (the search is identical); only their recorded peaks describe a
different memory profile and are not used to seed the governor.

## 5. How to verify (exact commands, repo root as cwd, PYTHONPATH=.)

Frozen references: `perf_lab/hcompact_baseline.py` (engine at `5d047da5`,
imports the LIVE kernels, so it isolates engine-layout changes only) and
`perf_lab/frozen/` (engine plus verbatim `greedy_baseline.py` and
`hfast.py` at the harness commit, lab SHA `9b98e313` = campaign-branch
`25170c5d`, identical trees, so it isolates everything). The bench and gates
purge numba caches first; numba's cache is keyed on the caller's file, so
without that an unchanged caller silently reloads an old kernel.

    # identity: oracle (Python reference solver) and twin (frozen engine),
    # widen lines compared by state count because the byte widths differ
    python3 experiments/heuristic_search/core/perf_lab/gates.py --oracle \
        --twin --twin-rows 6 --twin-budget 30000 --frozen --widen-lines states
    # speed and memory, frozen everything vs the live engine
    python3 experiments/heuristic_search/core/perf_lab/bench.py \
        --engines frozen,candidate --budget 100000 --reps 3 --cpu 1 --out bench.json
    # the phase split
    python3 experiments/heuristic_search/core/perf_lab/phase_split.py \
        --rows aca_0,aca_4,aca_5 --budget 50000 --reps 3 --cpu 1 --out split.json
    # direct kernel pins and the full suite
    python3 -m pytest tests/test_hcompact_kernels.py tests/test_expand_kernel.py -q
    python3 -m pytest tests/test_leftovers_5m.py -q

Promotion criteria used: every gate bit-identical; then either median
pops/s >= +10% with bytes/state within +1%, or bytes/state <= -15% with
pops/s within -3%. Both tracks cleared their criterion independently and
the integrated engine cleared the gates again.

## 6. Commits on the campaign branch (`claude/ac19-leftover-solver-notebook-6yan6d`)

In order on top of `5d047da5` (the baseline this report measures against):

| commit | content |
|---|---|
| `25170c5d` | perf lab harness: frozen baseline engine copy, `bench.py`, `gates.py`, README |
| `7b521698` | 2-bit row primitives, `_row_less_h` with its proof, the sort-corpus test (engine not yet wired) |
| `bf198274` | engine switched to 2-bit rows; `gates.py --widen-lines`; `_hash_row == _hash_codes` test |
| `14cb7c36` | runner sizing routed to `hcompact.row_width_h`; every pinned figure and lane count updated |
| `d90e415b` | one width test re-pinned for 2-bit `storage_width` semantics |
| `6b38ebff` | `phase_split.py` and `PHASE_SPLIT.md` (the replay phase split) |
| `40df3641` | expansion kernel: exact rotation index, hoisted inverses, zero allocations per child; `perf_lab/frozen/`; `tests/test_expand_kernel.py` |
| `794289a0` | candidate hash indexed through uint64; `tests/test_hcompact_kernels.py` |
| `2d42bde7` | phase-split recorder and kernel test ported to the 2-bit engine |
| `06095611` | ENGINE_MEM_GEN 5; u124 campaign notes and RESULTS.md updated |

The lab branches these were developed on (`lab/base`, `lab/memory`,
`lab/speed`, `lab/integrate`) are local to the session that produced them
and are not pushed; every change is on the campaign branch above and the
frozen copies under `perf_lab/` are the references a verifier needs.

Gate logs. Integrated engine vs the fully frozen harness-commit engine: oracle
60 rows at 1,000 PASS; twin 6 rows at 30,000, decode-max 2,000,000,
widen-lines states PASS; wall 11m33s. Full suite on the campaign branch
(`test_leftovers_5m`, `test_hcompact_kernels`, `test_expand_kernel`,
`test_greedy_heuristic`, `test_autcanon`, `test_leftovers_1m`) with fresh
numba caches: 275 passed in 11m40s.

## 7. Campaign-box measurement after roll-out (operator, 2026-09-05)

Box: r8ib.24xlarge (Xeon 6975P-C, 48c/96t, 743 GB), rolled to `3093592d`,
6 lanes seated by the governor (4 on the previous build), 254 GB used at
33% depth, no swap. Per-lane rate at 34% of a 10M row: 792 to 870 pops/s
against 891 at 30% on `5d047da5` for the same row family, so per lane is
0.95x to 1.15x, not the lab's 1.74x. Per box: 6 x 865 against 4 x 891 is
about 1.46x, which is the memory change realised as lanes.

Why the lab number did not carry, measured on the same box with the
campaign untouched:

- `perf stat` on a live worker at 50% depth, 60 s: IPC 2.68, dTLB load
  misses 23M in 60 s, THP on with ~373 GB in 2 MiB pages. The lane is
  instruction-bound, not memory-latency-bound; NUMA pinning and probe
  batching are not justified.
- `phase_split.py --rows aca_47 --budget 300000 --reps 1` on an idle core:
  expand 806.6 us (85.7%), la-scan 4.6, hash 8.4 (0.9%), probe 73.1
  (7.8%), pack 7.8, sift 5.3 (0.6%), residual 36.0, total 941.6 us per pop
  (1,062 pops/s, the campaign per-lane rate). 331.7 candidates per pop at
  49.5 symbols each (the 50k-pop lab rows had 172 to 241 at 38 to 43),
  146.9 inserts per pop, miss rate 0.443, intra-pop duplicate fraction
  0.350, 1.23 slots per lookup, 24 B rows, 1 widen, 1 grow.

Reading: the 1.74x lived in per-child overhead (allocations, the modulo,
the per-child inverse) that is a large share of a 38-symbol child and a
small share of a 50-symbol one, where the per-symbol loops inside
`expand_and_score_nj` dominate. The next measurement is therefore a split
INSIDE the expansion kernel at campaign length (generation and reduce,
canonicalisation, the pass-1 filter, feature scoring), and the candidate
changes are ones that cut per-symbol work or skip work on candidates that
dedup discards, both bit-identical by construction. Anything promoted
from here is held to the operator's bar: gates green, and at least 1.1x
at 300k pops on a real row measured on the campaign box, or more lanes
per GB.

## 8. Campaign-length expansion work (2026-09-05, after section 7)

Measured on the lab box at the operator's regime: row aca_47 at 300,000
pops (49.5 symbols per candidate, 331.7 candidates per pop), one run each,
every ratio against `perf_lab/frozen2/`, a verbatim copy of the build the
campaign runs (`a1d1be23`, engine-identical to `3093592d`).

The split inside `expand_and_score_nj` (`EXPAND_SPLIT.md`, replay method
one level down; stages sum to the expand phase within 0.7%):

| stage | us / pop | share of pop |
|---|---|---|
| pass-1 filter (seam test on 1,085 (k1, k2) pairs, seam-reduced length on 332) | 14.3 | 2.1% |
| raw child word + free/cyclic reduce | 67.1 | 9.9% |
| canonicalise: two Booth passes, the inverse, the lexicographic pick | 302.9 | 44.7% |
| pair order-normalise + encode | 27.1 | 4.0% |
| blob assembly and per-pop arrays | 23.6 | 3.5% |
| features (`_feats_nj`) + segment pick + weighted sum | 49.4 | 7.3% |
| expand total | 484.4 | 71.5% |

So deferred scoring (7.3% ceiling) was not built. Two changes were, both
in a new hcompact-only module `experiments/heuristic_search/core/hexpand.py`;
the shared kernels in `greedy_baseline.py` and `hfast.py` that the Python
oracle and the other engines use are untouched.

| step | change | identity argument | gates (vs frozen2) | aca_47 300k, current -> candidate |
|---|---|---|---|---|
| 1 `a8a6b3a4` | skip the cut-shift repeats before generating them: in one (target, sign) block the child of (k1, k2) is the child of (k1-1, k2+1 mod n) whenever the seam cancels, because the two raw words are conjugate and the cyclically reduced canonical form is a conjugacy-class invariant; 48.9% of all children at this depth | the skipped child is exactly a child emitted earlier in the same pop, so its lookup would have found it and inserted nothing; the skip is taken only when the predecessor is actually in the stream (per-block bitmap), and enumeration order is unchanged; verified on 48,639,570 flagged children with 0 violations and pinned by `tests/test_hexpand.py` on 2,000 real popped states per row | oracle 60 at 1,000 PASS; twin 6 at 30,000 PASS; wall 482 s | 1,439.9 -> 2,237.8 pops/s, ratio 1.5541 |
| 2 `f6f38a7d` | canonicalise on 2-bit-packed words: a word of up to 32 symbols is one uint64 in the numeric image of the symbol order, rotations are shifts, the least rotation is a min over m shifted values for the word and its inverse; 33 to 64 symbols on a (hi, lo) pair; beyond 64 the Booth path verbatim | the least rotation of a word is a unique string, so any correct algorithm returns Booth's answer; pinned against `canonical_relator_nj` on every word of up to 8 symbols (87,380), 104,000 random words of 9 to 64 symbols with the 32/33 and 64 boundaries covered, and every child of 2,000 real popped states per row | oracle PASS; twin PASS; wall 457 s | 1,452.9 -> 3,401.5 pops/s, ratio 2.3412 cumulative |

Fingerprints agree on every run; bytes per state 40.1 on both engines at
this depth (memory profile unchanged, ENGINE_MEM_GEN stays 5).

Campaign-box facts from the operator for the `3093592d` build, first four
completed rows on the r8ib.24xlarge at 6 lanes: aca_47 12,320 s at
96.7 GB peak, aca_50 12,331 s at 96.8, aca_49 12,617 s at 97.0, aca_48
13,428 s at 101.1; the previous build's rows at 4 lanes ran 11,202 to
13,775 s at 155 to 156 GB. Per-row wall time unchanged within the
row-to-row spread; peak RSS 1.55x to 1.60x lower, which is what seats 6
lanes; box peak 548 GB with all six rows past 90%, no OOM.

Expected from this section, subject to the operator's confirmation with
one 300k phase split on aca_47 on the campaign box: per-lane pops per
second about 2.3x on the same lanes, so per-row wall time about 12,500 s
to about 5,400 s at the same six lanes, with no change in memory.

### Final bench and what was not built (lab branch `lab/expand`, docs commit `34c3297b`)

Not done, with the number that decided it: deferred scoring (features +
scoring are 7.3% of the pop, of which only the duplicate fraction is
recoverable: 2% to 4%), and the pass-1 filter (2.1% of the pop). The
decision benches ran with the gates on another core; the final bench
below ran alone.

Final bench, box idle, core 2, candidate (`f6f38a7d`) over `current`
(`a1d1be23`): `aca_47` at 300,000 pops, 1 rep, 1,462.6 -> 3,385.0 pops/s,
**2.3144** (wall 346 s). The default six rows at 100,000 pops, 3 reps
(wall 1,082 s), median pops/s current -> candidate and ratio: aca_0
2,889.0 -> 5,509.6 (1.9071), aca_1 2,616.5 -> 5,470.0 (2.0906), aca_3
3,638.9 -> 7,993.7 (2.1968), aca_4 2,069.8 -> 4,402.9 (2.1272), aca_5
1,999.9 -> 4,280.2 (2.1402), aca_8 3,573.4 -> 8,182.8 (2.2899); median
2.1337, geometric mean 2.1220; bytes/state 44.4 on both, peak RSS within
0.003 GiB, record fingerprints agree on every row and every rep. Memory is
neutral by construction: the kernel allocates per pop (the emitted bitmap
is at most n1 x n2 bytes), nothing per state. Raw output:
`perf_lab/results/final_bench_aca47_300k.json`,
`perf_lab/results/final_bench_6rows_100k_x3.json`, the two decision
benches beside them, and the split in `expand_split_aca47_300k.json`.

Full suite on the campaign branch at `edfa8c68`, numba caches purged:
292 passed across the whole tests directory. (On the lab branch the same
tree shows the ten branch-name pins failing by construction, plus the
rerun observer's end-to-end test, whose 2,000-pop toy row now finishes
inside the observer's first poll; the observer samples before it polls
since `edfa8c68`.)

### On-box confirmation and roll (operator, 2026-09-05 13:20Z)

Confirmation before the roll, from a worktree at `edfa8c68` on an idle core
of the r8ib.24xlarge: `phase_split.py --rows aca_47 --budget 300000` gave
209.8 us per pop against 941.6 on `3093592d`, a 4.49x on the Xeon 6975P-C
(above the lab box's 2.34x), with the search statistics identical:
44,077,944 states discovered, 331.728 candidates per pop, 146.926 inserts
per pop, intra-pop duplicate fraction 0.350, final load factor 0.328.
Tooling caveat on this build: the split's sub-phase timers summed to
505.9 us with `expand` at 408 us and a negative residual, because the
expand replay runs the unskipped reference kernel; the plain per-pop total
is the valid figure (RUNBOOK.md rule 5).

Rolled at 13:20Z: presync, boot script re-pinned to `edfa8c68`, verify
PASS, governor admitting against 117.6 GB per row, six lanes. Four minutes
in: aca_53 6,203, aca_54 4,781, aca_57 3,886, aca_58 3,875 pops/s at 100%
CPU and 24 to 25 GB RSS each, against 1,000 to 1,300 at the same depth on
`3093592d`. 53 of 124 rows complete at the roll; first row times on this
build expected at 2,500 to 4,000 s against 12,300 to 13,800 s before.

First four completed rows on `edfa8c68` (six lanes, gen 5, 10,000,000 nodes
each, unsolved): aca_54 2,349.7 s at 89.98 GB peak, aca_58 2,525.4 s at
90.68, aca_57 2,794.2 s at 98.45, aca_56 2,839.1 s at 100.44. Against the
`3093592d` rows on the same box (12,320 to 13,428 s at 96.7 to 101.1 GB)
that is 4.4x to 5.2x per row with peak RSS unchanged, matching the 300k
split (209.8 vs 941.6 us per pop). Box aggregate about 23,000 nodes/s
across six lanes, against about 5,400 on `3093592d` and about 3,600 on
`5d047da5`. 59 of 124 rows complete at 2026-09-05, projected finish the
same day, remaining cost about $15.

### Positive control on the running build (operator, 2026-09-05)

`ac19_15866` (s20_mk2 solves it at 17,369 nodes; greedy does not at 5M)
run on the campaign box on `edfa8c68` via `rerun_row`, campaign untouched:
under the u124 configuration (cap 64, budget 1,000,000) solved true,
nodes_explored 17,369, path_length 96, 97 path states ending at the
trivial pair, 96 moves, min/max relator 2/35, engine_mem_gen 5, 1.97 s,
peak 1.31 GB; under the archived configuration (cap 48, budget 200,000)
the identical 17,369 / 96 / 2 / 35; the moves replay into the recorded
path. Recipe and expected values in RUNBOOK.md section 7.
