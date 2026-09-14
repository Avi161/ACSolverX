# Results: a hash-free, table-free solver for the AC19 Aut-minimal census and MS-640

All numbers below are from records in `records/` (JSONL with certificates, one row per
presentation); every solved row's certificate was replayed by an independent verifier
before it was written (`verified` counts).  Budget is 1,000 work units per row (one
per popped state, accepted automorphism, image evaluation or substitution move).
Machine: this session's 4-core container, CPython 3.11, numba 0.63; MS-640 timings are
single-core with `NUMBA_NUM_THREADS=1`.

## Headline

| set | rows | census policy (hashed closed set + BS tables) | this solver, rank-two engine (`fast`) | this solver, final (`hybrid`, penalty 5) |
|---|---:|---:|---:|---:|
| AC19 Aut-minimal census | 72,779 | 72,052 | 72,738 | **72,779** (`records/final3_census.jsonl.gz`, median 27 units, 99th percentile 128, max 954; 95 s wall on 4 workers) |
| the policy's 727 leftovers | 727 | 0 | 696 (673 without permutation canonicalisation) | **727** (`records/final3_u727.jsonl`) |
| the 9 rows unsolved by every fixed-basis arm at 10M nodes | 9 | 0 | 9 (7 at ≤ 318 units; 2 need permutation canonicalisation, 440–545) | 9 |
| random census sample (seed 1) | 2,000 | — | 1,997 | 2,000 (`records/final3_s2000.jsonl`) |
| MS-640, 1,000 units | 640 | 640 (cascade) | 640 | 640 (2.22 s search, 5.76 s batch under the cascade's protocol, one core) |
| the whole `data/AC19_extended.txt` file, every row in its ORIGINAL spelling (not the Aut-minimal representative) | 156,762 | — | — | **156,762** (`records/final3_extended.jsonl.gz`, median 31 units, 99th percentile 125, max 954; 177 s wall on 4 workers) |

MS-640 timing on one core, measured the way the cascade measured itself (search clock
around the solver only; the batch clock includes verification by two independent
replayers, serialisation, progress output and twelve 0.25 s cooldowns, one after every
50 rows): cascade 2.36 s search / 6.32 s batch (`results/heuristic_search/goal_frontiers/MS640_RESULTS.md`);
**final hybrid 2.22 s search / 5.76 s batch**, at most 283 units on a row (cascade: 404),
`records/final3_ms640_hybrid_protocol.jsonl` (`run_ms640.py --cascade-protocol`).  Without
the cooldowns and with one replayer the same run is 2.27 s / 2.55 s
(`records/final3_ms640_hybrid.jsonl`).  Earlier builds for reference: rank-two engine
3.01 s / 7.11 s (`records/ms640_fast_v2.jsonl`); hybrid before lazy define children,
pop-time permutation canonicalisation and the packed gate precheck 4.98 s / 7.00 s
(`records/final_ms640_hybrid.jsonl`).

Certificate scope in the hybrid census run: 72,591 rows have ordinary rank-two
certificates (products and automorphism transport, expanded to AC moves by the
repository's existing decoder contract); 188 rows use `define`/`eliminate`
steps and are therefore certificates of *stable* AC-triviality of a trivial-group
presentation (Lemma 11 of arXiv:2408.15332, composites not expanded), exactly as in
`research/ac_dynamic_rank_20260913`.  Every one of the 727 leftovers and of the 41
rows the rank-two engine could not finish at 1,000 units has a rank-two certificate at
a larger budget: `records/left31_fast_hash_perms_b20k.jsonl` (the 31 hardest, 1,094–10,080
units, all replayed) and `records/census41_fast_v2.jsonl`.

Independent replay after the fact (`verify_all.py` over the final records
`records/final3_*` and key earlier ones): every stored certificate replays, 0 failures
(77,531 in the first final pass, 76,187 and 76,827 in the re-validations of the final build).

## The whole AC19_extended file in its original spelling

`run_extended.py` runs the same final solver, same two tuned numbers, same 1,000-unit
budget, over every one of the 156,762 rows of `data/AC19_extended.txt` as written
(the 634 solved MS-640 rows the file opens with, the 140,240 further rows of length
<= 19 and the 15,888 rows of length 20-33), not over the 72,779 Aut-minimal
representatives.  The Aut-minimal census is a quotient of this file (the `members`
column of `data/AC19_extended_aut_min.csv` partitions exactly these 156,762 indices),
but solving a representative says nothing about the budget its orbit-mates need from
their own spelling, so this is a separate measurement.

| rows | solved | verified | units median / p99 / p99.9 / max | stage B / C / search | rank-two certificates | stable certificates |
|---:|---:|---:|---|---|---:|---:|
| 156,762 | **156,762** | 156,762 | 31 / 125 / 242 / 954 | 14,788 / 40,478 / 101,496 | 156,435 | 327 |

- length <= 19: 140,874 / 140,874 (max 954 units); length 20-33: 15,888 / 15,888 (max 827);
  the 634 MS rows: 634 / 634 (max 278).  25 rows need more than 500 units, one more
  than 900 (`ext_61616`, `YYXYxyxxYYx / YXXYxxyx`, 954 units, a rank-two certificate).
- The 327 stable certificates (define/eliminate steps, Lemma-11 composites unexpanded)
  are almost exactly the orbit-mates of the 188 census representatives that needed one:
  326 of the 156,762 rows belong to such an orbit, 325 of them get a stable certificate
  here and one a rank-two certificate; two further rows in orbits whose representative
  had a rank-two certificate need a stable one from their own spelling.
- Wall clock 176.9 s on the 4-worker pool including verification (641.7 CPU-s of
  search, at most 2.43 s on a row).  Replayed after the fact by `verify_all.py`:
  156,762 / 156,762, 0 failures.

## What each ingredient buys (the 727 policy leftovers, 1,000 units)

| engine | closed set | Nielsen edges | signed-perm canonical | solved / rows | record |
|---|---|---|---|---:|---|
| best-first, length | none (parent chain only) | no | no | 9 / 604 | `records/controls/u727_memoryless_bestfirst_len_partial604.jsonl` |
| beam 8, length | none | no | no | 9 / 604 | `records/controls/u727_memoryless_beam8_len_partial604.jsonl` |
| best-first, length | sorted array | no | no | 31 / 180 | `records/controls/u727_sorted_nonielsen_len_partial180.jsonl` |
| best-first, length | sorted array | **yes** | no | **673 / 727** | `records/u727_bf_len_sorted_nielsen.jsonl` |
| … the 54 left, with signed perms | sorted array | yes | **yes** | 23 / 54 | `records/left54_perms.jsonl` |
| hybrid (rank two + define/eliminate), penalty 5 | sorted arrays | yes | yes | **727 / 727** | `records/hy727_p5.jsonl` |

Two facts settle the "no hashing" question empirically.  (1) Memory of visited states
is indispensable at this budget: without it best-first and beams thrash on the
inverse-move and commuting-move duplicates and solve 1.5% of the leftovers; a
parent-chain cycle check of any depth and frontier-only deduplication do not help
(`records/…` and the session tests).  (2) That memory does not need a hash table: a
block-sorted array with bisection reproduces the hashed control pop for pop (identical
unit counts on every tested row, pinned in `test_hfcascade.py`).

The single largest gain is the four Nielsen maps as search edges (31/180 → 673/727 on
the same engine).  The Aut-minimal spelling sits at the bottom of a length well
(`ORIGINALS_AT_10M.md`, `WORKED_EXAMPLE.md` on branch
`claude/ac19-leftover-solver-notebook-6yan6d`); with basis changes as edges, seven of
the nine 10M-node failures solve in 137–318 units.

## The nine rows no fixed-basis arm solved at 10,000,000 nodes

| row | rank-two engine, units | final hybrid, units | certificate |
|---|---:|---:|---|
| ac19_16286 | 116 | 98 | rank two |
| ac19_27254 | 174 | 98 | rank two |
| ac19_28131 | 121 | 103 | rank two |
| ac19_44381 | 238 | 134 | rank two |
| ac19_50841 | 136 | 124 | rank two |
| ac19_51034 | 550 | 668 | rank two |
| ac19_59576 | 116 | 98 | rank two |
| ac19_65753 | 445 | 502 | rank two |
| ac19_7284 | 116 | 98 | rank two |

All nine have ordinary rank-two certificates (products and Nielsen automorphisms) found
within the budget; `records/final3_u727.jsonl` carries them.

## Dynamic rank on the residue

The 41 rows the rank-two engine leaves at 1,000 units need 1,094–10,080 rank-two units
(length ordering; S20 ordering 829–9,994).  The dynamic-rank search of
`research/ac_dynamic_rank_20260913` (cap 8, ceiling L+8, generator-permutation
canonical form, length priority) solves 40 of them within 650 pops
(`records/dyn_census41_p1000.jsonl`), but on its own it is weaker than the rank-two
engine elsewhere (213/300 of the leftovers and 689/800 of the sample at 1,000 pops,
partial runs in `records/controls/`).  The hybrid keeps the rank-two engine's
behaviour and adds the dynamic moves to the same frontier; the one parameter is the
priority penalty per generator above two:

| penalty | 41 rank-two leftovers | 7 pinch-family rows (`YYXXyxx` donors) | all 727 |
|---:|---:|---:|---:|
| 2 | 41 | 0 | — |
| 4 | 41 | 0 | 720 |
| **5** | **41** | **7** | **727** |
| 6 | 32 | 7 | — |
| 8 | 2 | 7 | — |

Penalty 5 alone left one census row (`ac19_38723`, 647 rank-two units) unsolved: its
rank-two search was crowded out by 429 higher-rank pops.  The final rule keeps two
frontiers and serves the higher-rank one only while its pops are at most half the
rank-two pops plus 20 (deferring, never dropping, its states); with it the 41, the
pinch rows, `ac19_38723`, all 727 leftovers and the whole census solve
(`records/hy41_p5r2.jsonl`, `records/hy13_p5r2.jsonl`, `records/final3_*`).

A small penalty lets rank-three states crowd out rank-two states that a length-ordered
search needs to reach the pinch structure; a large one delays the dynamic moves past
the budget.  Five is the value that solves everything measured; it was chosen on these
rows and then applied unchanged to the whole census and to MS-640.

## The 727 leftovers, structurally

`analyse727.py`: none has a primitive relator; 88 have a conjugation-shaped relator
`g^a h^p g^-a h^q` (56 of them `x^-2 y x^2 = y^2`, a squared stable letter that the
census tables cannot see); 639 are generic 4–12-syllable pairs; plain length-first greedy
with a hashed closed set solves 333 of them within 10,000 nodes.

## Caveats

* The solver was developed against the census policy's leftovers; the full census and
  MS-640 were each run once with the final configuration (no per-set tuning except the
  penalty chosen as described).
* `define`/`eliminate` certificates are stable-AC certificates conditional on the
  trivial-group hypothesis, which holds for every AC19 row by construction (the set was
  enumerated and greedy-solved); they are not rank-two AC paths.  Rank-two paths exist
  for all 727 leftovers at ≤ 10,080 units.
* Units are heterogeneous (pops of different ranks, evaluations, moves), as in the
  census policy; wall times are reported alongside.
* The rank-two kernel canonicalises exactly as the repository's `canon_pair`; the
  verifier uses its own implementation and compares canonically.
