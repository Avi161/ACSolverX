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
| pops/s per lane | 1.0x | ~1.7x | measured at 50k to 100k pops on the lab box; projected to campaign scale |
| throughput per 512 GiB box | 1.0x | ~3.4x | 2x lanes x 1.7x per lane |
| cost per 186/node row, on-demand r6a.16xlarge at $3.63/h | ~$5.4 | ~$1.6 | 3 h -> ~1.75 h per row, 4 lanes |

Caveats a verifier should keep: the per-lane speed factor was measured at
50k to 100k pops on a Xeon lab box, where candidates are 38 to 43 symbols;
at campaign scale relators are longer and the expansion kernel's share is
inferred to be at least as large, but the factor there is a projection
until a campaign row reports its `seconds`. The lane counts are exact
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
