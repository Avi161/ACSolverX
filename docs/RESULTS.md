# Results

Section 0 and the section "Relator-length cap" are measured on this branch with `python run.py` (every path replayed
before it is written). Sections 1 to 10 are read from files on source branches, written `branch:path`; the commit that
last touched each path is in [PROVENANCE.md](PROVENANCE.md). Two studies of source branches are stored in this
repository, in `results/stable_ac/` ([results/README.md](../results/README.md#studies)): the rank-n brute force (section
7) and the exhaustive CoV sweep (section 5); they are cited by their path here. A line tagged **[survey]** comes from
the branch survey and was not re-read at its source. A line tagged **[rerun]** was reproduced with the unmodified
original code (Python 3.12.3, numba 0.63.1, numpy 2.1.3, one single-threaded process per run); those reruns are
deterministic, and section 0 matches them exactly.

## 0. This branch: `python run.py`, every path replayed

**Reproduced on this branch** with the current code: every row below is the committed `results/<run>/summary.json`
(and `config.json`) of `python run.py --config configs/<config>.toml --set name=<run> <overrides>`; the certificates
(`paths.jsonl`, gitignored) regenerate with the same command. Every run folder of `results/` was regenerated with
`--fresh` after the cap counters were added, so each record carries the cap fields and each `summary.json` the `caps`
block (section "Relator-length cap"). The summaries were written before the timing and cost keys were added: they have
no `cpu_seconds`, `us_per_cost`, `cost_unit`, `cost_mean` or `cost_median`, and their `config` block still holds
`workers`. The same command today writes those keys. Fast backend unless stated, cap 24 unless stated, one core
per worker on a shared 4-core 2.8 GHz VM. Each record was written only after its certificate replayed on the row, and
after the reruns the stored paths of the solved records were replayed again from the files by a separate script (77,723
records of every run but `ac1m_hybrid`, 0 failures; the 103 CoV `stable_cert`s are checked by `acx.cov.verify` when written). Path lengths are totals over
solved rows (median per row): the S-move and elementary columns count AC paths (`ac_path`, aut-assisted included); the
**stable** columns count `stable_cert`s (S-moves of the search leg / elementary plus AC4/AC5 moves; a CoV `stable_cert`
has no elementary path). "aut" is an aut-assisted `ac_path`. CPU s is the sum of per-row seconds.

| run | config, overrides | solved | ac_path / aut / stable | cost | S-moves | elementary | stable S / elem | CPU s |
|---|---|---:|---|---:|---:|---:|---:|---:|
| `smoke` | `smoke` | 20 / 20 | 20 / 0 / 0 | 102 pops | 82 (4) | 450 (21.5) | | 0.6 |
| `ms640_length_spec` | `baseline_spec` (`spec`, 4 workers) | 606 / 640 | 606 / 0 / 0 | 576,053 pops | 12,103 (8) | 114,828 (54) | | 2,023 |
| `ms640_length_fast` | `greedy_fast` | 606 / 640 | 606 / 0 / 0 | 576,053 pops | 12,103 (8) | 114,828 (54) | | 64 |
| `ms640_s20_mk2_fast` | `s20_mk2_fast` | 626 / 640 | 626 / 0 / 0 | 382,718 pops | 16,872 (9) | 168,702 (56.5) | | 51 |
| `ms640_aut` | `aut`, `benchmark=ms640` | 626 / 640 | 11 / 615 / 0 | 408,174 pops | 16,998 (9) | 787,744 (249) | | 84 |
| `ms640_cov` | `cov`, `benchmark=ms640` | 584 / 640 | 554 / 0 / 30 | 693,162 pops | 6,700 (8) | 54,944 (48) | 1,652 / - | 75 |
| `ms640_hybrid` | `hybrid` | 640 / 640 | 128 / 512 / 0 | 25,064 units | 12,346 (10) | 89,055 (54) | | 12 |
| `ms640_ngen_sac` | `ngen_sac`, `benchmark=ms640` | 298 / 640 | 0 / 0 / 298 | 3,729,167 pops | | | 5,035 / 229,196 | 314 |
| `ms640_rl30` | `rl` (rows 0:30, width 256, 150 steps) | 30 / 30 | 30 / 0 / 0 | 9,650 evaluations | 133 (4) | 845 (25.5) | | 20 |
| `ac19_hybrid` | `hybrid`, `benchmark=ac19_autmin` (266 s wall) | 72,779 / 72,779 | 36,811 / 35,780 / 188 | 2,489,726 units | 1,232,877 (11) | 7,341,111 (71) | 2,722 / 93,692 | 987 |
| `ac1m_hybrid` | `hybrid`, `benchmark=ac1m_autmin` (255 s wall) | 71,281 / 71,283 | 34,649 / 36,508 / 124 | 2,384,509 units | 1,136,288 (11) | 7,239,114 (71) | 1,662 / 62,312 | 951 |
| `bench60_length` | `greedy_fast`, `benchmark=bench60` | 40 / 60 | 40 / 0 / 0 | 248,227 pops | 1,475 (24) | 15,028 (217) | | 27 |
| `bench60_s20_mk2` | `s20_mk2_fast`, `benchmark=bench60` | 52 / 60 | 52 / 0 / 0 | 141,740 pops | 3,237 (31.5) | 34,173 (281) | | 19 |
| `bench60_aut` | `aut` | 52 / 60 | 0 / 52 / 0 | 147,767 pops | 3,214 (30.5) | 176,856 (1,035.5) | | 24 |
| `bench60_cov` | `cov` | 39 / 60 | 29 / 0 / 10 | 246,744 pops | 557 (16) | 4,972 (119) | 485 / - | 29 |
| `bench60_ngen_sac` | `ngen_sac` | 8 / 60 | 0 / 0 / 8 | 531,923 pops | | | 147 / 8,152 | 53 |
| `bench60_hybrid` | `hybrid`, `benchmark=bench60` | 60 / 60 | 7 / 53 / 0 | 4,783 units | 3,382 (16.5) | 27,641 (170) | | 7 |
| `holdout60_length` | `greedy_fast`, `benchmark=ac1m_hard_holdout60` | 44 / 60 | 44 / 0 / 0 | 329,601 pops | 2,447 (44.5) | 26,589 (448) | | 31 |
| `holdout60_s20_mk2` | `s20_mk2_fast`, same | 50 / 60 | 50 / 0 / 0 | 165,049 pops | 3,069 (44.5) | 33,345 (457.5) | | 18 |
| `holdout60_length_1k_cap48` | `greedy_fast`, same, `search.budget=1000`, `search.cap=48` | 0 / 60 | 0 / 0 / 0 | 60,000 pops | | | | 7 |
| `holdout60_s20_mk2_1k_cap48` | `s20_mk2_fast`, same, `search.budget=1000`, `search.cap=48` | 33 / 60 | 33 / 0 / 0 | 41,953 pops | 1,465 (36) | 15,128 (342) | | 8 |
| `holdout60_hybrid` | `hybrid`, `benchmark=ac1m_hard_holdout60` | 60 / 60 | 0 / 60 / 0 | 3,770 units | 1,697 (16) | 17,593 (223.5) | | 4 |
| `u124_s20_mk2` | `s20_mk2_fast`, `benchmark=u124` | 0 / 124 | | 1,149,399 pops | | | | 75 |
| `u124_hybrid` | `hybrid`, `benchmark=u124` | 0 / 124 | | 124,000 units | | | | 566 |
| `ladder60_length` | `ladder`, `benchmark=ladder60`, `search.priority=length` | 12 / 60 | 12 / 0 / 0 | 508,744 pops | 644 (60.5) | 6,807 (604) | | 41 |
| `ladder60_s20_mk2` | `ladder`, `benchmark=ladder60` | 33 / 60 | 33 / 0 / 0 | 365,386 pops | 2,180 (64) | 24,343 (713) | | 32 |
| `ladder60_cov` | `cov`, `benchmark=ladder60` | 32 / 60 | 7 / 10 / 15 | 430,114 pops | 624 (26) | 31,515 (730) | 628 / - | 54 |
| `ladder60_hybrid` | `hybrid`, `benchmark=ladder60` | 60 / 60 | 1 / 57 / 2 | 8,077 units | 2,882 (22) | 30,794 (293.5) | 30 / 1,726 | 17 |
| `ladder200_length` | `ladder`, `search.priority=length` | 40 / 188 | 40 / 0 / 0 | 1,551,196 pops | 1,991 (30) | 21,108 (276.5) | | 127 |
| `ladder200_s20_mk2` | `ladder` | 116 / 188 | 116 / 0 / 0 | 1,063,702 pops | 7,697 (55) | 86,172 (587.5) | | 90 |
| `ladder200_cov` | `cov`, `benchmark=ladder200` | 92 / 188 | 21 / 23 / 48 | 1,357,023 pops | 1,215 (17) | 60,321 (640) | 2,077 / - | 155 |
| `ladder200_hybrid` | `hybrid`, `benchmark=ladder200` | 188 / 188 | 8 / 173 / 7 | 22,319 units | 7,612 (20) | 80,878 (301) | 117 / 6,051 | 38 |

Every run except the MS640 configs as shipped also sets `workers=4`; `ladder` already runs 4 workers.

| ladder level | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `ladder60` rows | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 60 |
| length greedy | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 12 |
| S20_MK2 | 6 | 6 | 4 | 4 | 2 | 6 | 3 | 0 | 2 | 0 | 33 |
| CoV (one-shot, length) | 6 | 5 | 4 | 2 | 3 | 3 | 3 | 3 | 2 | 1 | 32 |
| hybrid | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 60 |
| `ladder200` rows | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 19 | 9 | 188 |
| length greedy | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 40 |
| S20_MK2 | 20 | 20 | 13 | 14 | 12 | 18 | 7 | 6 | 6 | 0 | 116 |
| CoV (one-shot, length) | 20 | 16 | 5 | 4 | 11 | 12 | 8 | 11 | 4 | 1 | 92 |
| hybrid | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 19 | 9 | 188 |

- **Regenerated with the cap counters.** All 32 folders of the table and the three rank-n runs were rerun with `--fresh`
  once the cap counters were in, by the runner of that time (the summaries' missing keys are above). Every record of the
  32 (150,492 rows in all: solved, pops or units, S-move and elementary paths, certificates, stage) is identical to the
  earlier run, except the 11 plain `ac_path` rows of `ms640_aut` (below). The CPU s column keeps the timings of the
  earlier runs on an idle machine: the reruns shared the 4 cores with other jobs (1.1x to 4x the time) and used 2
  workers where the table says 4, so their `row_seconds` are not comparable. Runs split into row slices of the same
  config to stay under 15 minutes (`ms640_length_spec`, `u124_hybrid`, `ac19_hybrid`, `ac1m_hybrid`, `rank3_bf`) have a
  `wall_seconds` that is the sum of the slices.
- **Parity with the original code.** `spec` and `fast` give identical records (solved, pops, S-move path, elementary
  path, and the six cap-counter fields) on all 640 MS640 rows, and the per-row pops and path lengths equal the original
  `greedy_baseline` / `heuristics` reruns (`work/reference/`, not in git; 0 mismatches over 1,280 rows); the hybrid's
  per-row stage and units equal the original `hfhybrid` run on all 640 rows (stages B / C / H = 98 / 328 / 214; the
  reference's 4,759 stage-H steps are 3,258 S-moves plus 1,501 automorphism steps here); on the AC19 Aut-min census it
  reproduces the source's 2,489,726 units and its 72,591 rank-two / 188 stable split exactly (72,591 = 36,811 + 35,780
  here). On AC1M Aut-min it solves 71,281 of 71,283, the source's count (misses `ac1m_54083`, `ac1m_68740`).
- **Speed of `fast` against `spec`.** Over the whole MS640 LENGTH run, `spec` takes 32x the CPU of `fast` (2,023 against
  64 CPU s in the table: search, decoding and replay of every row). On search alone the ratio is larger: the slow test
  `tests/test_fast.py::test_speed` (MS640 rows 322 and 466, 2,000 pops under each priority) prints the ratio and
  asserts only more than 5x; one run of it printed 16,611 against 366 pops/s, 45x (`work/verify/NUMBERS.md`, not in
  git).
- **Ladder by level**: length greedy solves levels 1-2 only, as the levels are defined; S20_MK2 solves 6 of the 19
  level-9 rows at 10,000, as on record; the hybrid solves every row, 7 of `ladder200` as `stable_cert`. The 10M-pop
  grades of levels 9 and 10 are by record and were not rerun. The ladder rows were graded at their own caps (24 to 64);
  these runs use cap 24 for every row.
- **CoV at equal pops loses to plain search here.** With 1,000 pops per image and 10,000 in total, CoV solves 584 MS640
  rows (554 by the row's own first 1,000 pops plus 30 stable certificates) against 606 for one 10,000-pop search; on
  bench60 39 against 40. On MS640 and bench60 no image solve landed in the row's Aut orbit (`aut` 0), so every CoV gain
  there is a `stable_cert`; on the ladders some do (10 and 23 aut-assisted).
- **Aut-assisted paths are long**: MS640 through the Aut-min representative gives the same 626 solves as S20_MK2 on the
  rows, with 4.7x the elementary moves (787,744 against 168,702) for the transport and its Nielsen tail. 11 of them are
  plain `ac_path`s: their row is already its own Aut-minimal form (12 MS640 rows are; one is unsolved). The earlier
  figure was 809,842 (4.8x): those 11 rows used to store the transported path, and now store the shorter decoded path
  of the same S-moves (bug B2 fixed), so their elementary total fell from 29,997 to 7,899 (row 7: 58 to 13, row 590:
  17,378 to 4,454). Solved counts, pops, S-moves and the 615 aut-assisted paths are unchanged.
- **ac1m_hard holdout**: at the published protocol (budget 1,000, cap 48, the S20_MK2 selection's spent holdout) 0 and
  33 reproduce the published 0/60 and 33/60 (section 2); at 10,000 pops and cap 24 length greedy solves 44 and S20_MK2
  50; the hybrid solves all 60.
- **RL** (`configs/rl.toml`, the step-1000 610model checkpoint, beam 256 x 150): 30 of the first 30 MS640 rows.
- **Rank-n brute force** (`configs/rank{3,4,5}_bf.toml`, method `rankn`, [RANK3.md](RANK3.md)): add generators `z = w` for
  every word `w` of length 1-4 (rank 3) or every multiset of words (ranks 4 and 5) and search each start, budget 1,000,
  cap 24, LENGTH, with the plain 2-generator search as control. Each run writes `rows/<id>.npz` (gitignored),
  `summary.json` and `summary.md`; the long ones were run in row slices of the same config (`rank3_bf`: `--rows 0:160`,
  `160:320`, `320:480`, `480:640`).

| run | rows | starts per row | searches | control solves | solved by some start | the baseline's stored study |
|---|---:|---:|---:|---:|---:|---|
| `rank3_bf`, lengths 1-4 | 640 | 80 | 51,200 | 554 | 403 / 472 / 516 / 540 up to length 1 / 2 / 3 / 4 | the same 403 / 472 / 516 / 540; lost by every word 151 / 82 / 38 / 18 |
| `rank4_bf`, extra 2, lengths 1-3 (`--rows 0:201`, `207:640:20`) | 223 | 351 | 78,273 | 219 | 216 | slice of the baseline's 506 / 640, not comparable |
| `rank5_bf`, extra 3, lengths 1-2 (`--rows 0:640:20`) | 32 | 120 | 3,840 | 28 | 21 | slice of the baseline's 416 / 640, not comparable |

  The rank 4 and 5 runs are row slices (a full rank-4 run is two to three core-hours here). `rank4_bf` is every 20th
  row from 7 plus the first rows 0 to 200, which a full sweep had reached when it was stopped at the 15-minute limit; the
  first rows are the easy ones (the control solves 219 of its 223), so its numbers are not those of MS640. The rank-3
  run covers all of MS640 and equals the tables of the baseline's study, stored in
  [results/stable_ac/rank3_bf/](../results/stable_ac/rank3_bf/README.md) (random word solves 60.1% / 68.4% / 69.8% /
  68.6% of its starts at length 1 / 2 / 3 / 4).

## Relator-length cap

A search keeps a child only if both of its relators have at most `cap` letters; [CAP.md](CAP.md) defines the counters
and the guarantee (no row that would pop means the same run at any larger cap). Every folder of `results/` was
regenerated with the counters, and the tables below are read from the `caps` block of each `summary.json`. *Rows
dropping* is the number of rows where the cap kept a child out; *rows that would pop* the rows where raising the cap
changes the search (their ids are `caps.cap.raise_ids`, the first 100); *children dropped* is the sum of `cap_dropped`
(one per move) and *would-pop states* the sum of `cap_would_pop`; `cap_needed` is the range, over the rows, of the
smallest cap at which a row changes, and *first bind* the earliest pop at which a dropped state would have gone first.

### Searches under one cap

| run | solved | cap | rows dropping | rows that would pop | children dropped | would-pop states | `cap_needed` | first bind (pop) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `smoke` | 20 / 20 | 24 | 0 | 0 | 0 | 0 | - | - |
| `ms640_length_spec` | 606 / 640 | 24 | 26 | 0 | 12,195,104 | 0 | - | - |
| `ms640_length_fast` | 606 / 640 | 24 | 26 | 0 | 12,195,104 | 0 | - | - |
| `ms640_s20_mk2_fast` | 626 / 640 | 24 | 74 | 20 | 10,128,166 | 801 | 25 | 309 |
| `ms640_aut` | 626 / 640 | 24 | 76 | 20 | 12,013,436 | 1,224 | 25 | 766 |
| `ms640_cov` | 584 / 640 | 24 | 26 | 0 | 1,278,976 | 0 | - | - |
| `ms640_ngen_sac` | 298 / 640 | 24 | 0 | 0 | 0 | 0 | - | - |
| `ms640_rl30` | 30 / 30 | 24 | 5 | 5 | 23 | 23 | 25-27 | 5 |
| `bench60_length` | 40 / 60 | 24 | 17 | 0 | 8,478,448 | 0 | - | - |
| `bench60_s20_mk2` | 52 / 60 | 24 | 27 | 10 | 4,614,938 | 387 | 25 | 474 |
| `bench60_aut` | 52 / 60 | 24 | 27 | 10 | 5,739,822 | 668 | 25 | 766 |
| `bench60_cov` | 39 / 60 | 24 | 12 | 0 | 727,750 | 0 | - | - |
| `bench60_ngen_sac` | 8 / 60 | 24 | 0 | 0 | 0 | 0 | - | - |
| `holdout60_length` | 44 / 60 | 24 | 21 | 1 | 8,233,266 | 1,518 | 25 | 6,708 |
| `holdout60_s20_mk2` | 50 / 60 | 24 | 38 | 6 | 9,041,088 | 687 | 25 | 221 |
| `holdout60_length_1k_cap48` | 0 / 60 | 48 | 0 | 0 | 0 | 0 | - | - |
| `holdout60_s20_mk2_1k_cap48` | 33 / 60 | 48 | 0 | 0 | 0 | 0 | - | - |
| `u124_s20_mk2` | 0 / 124 | 24 | 122 | 93 | 223,308,466 | 9,753,771 | 25 | 21 |
| `ladder60_length` | 12 / 60 | 24 | 35 | 1 | 25,777,196 | 7,647 | 25 | 9,214 |
| `ladder60_s20_mk2` | 33 / 60 | 24 | 49 | 31 | 29,109,358 | 14,692 | 25-26 | 335 |
| `ladder60_cov` | 32 / 60 | 24 | 24 | 0 | 1,983,514 | 0 | - | - |
| `ladder200_length` | 40 / 188 | 24 | 95 | 3 | 64,040,488 | 31,115 | 25 | 9,211 |
| `ladder200_s20_mk2` | 116 / 188 | 24 | 157 | 77 | 77,900,696 | 53,637 | 25-26 | 304 |
| `ladder200_cov` | 92 / 188 | 24 | 65 | 0 | 5,480,806 | 0 | - | - |

- **Cap 24 changed nothing** in every LENGTH run (`ms640_length_*`, `bench60_length`), in CoV, in the n-generator
  search and in the two cap-48 holdout runs: 0 rows that would pop. LENGTH drops children in 26 of 640 MS640 rows,
  and the 26 rows run again uncapped pop the same states in the same order at every pop (traces compared), so
  606 holds at every cap. CoV reports `cap_legs_bound` 0 on all four runs (no search of any row was bound by the cap).
  The n-generator search stabilises to relators of length at most 3, so cap 24 is never reached. Cap 48 on the
  holdout is never reached either.
- **The cap matters under S20_MK2.** Its priority puts long relators early, so the cap drops children in 74 of 640 MS640
  rows and a dropped child would have been popped in 20 (`aut` searches the Aut-minimal form with the same priority:
  the same 20 rows). `cap_needed` is 25 in every one of those rows on MS640, bench60 and the holdout (25-26 on the
  ladders), so cap 25 is the smallest cap at which any of them changes. Cap 25 is also enough to make the count 0 on
  MS640 and bench60, but not on 4 of the 6 holdout rows, which still have `cap_would_pop` > 0 at 25 (`cap_needed`
  26, 26, 26 and 27); the study below therefore goes uncapped.
- **LENGTH has a few rows too**, deep in the budget: `holdout60_length` row 569291 (first bind at pop 6,708),
  `ladder60_length` row `ac19_50892` and `ladder200_length` rows `ac19_14060`, `ac19_27187` and `ac19_50892` (first
  binds 9,211 to 9,886). All four rows are unsolved at 10,000 pops, with and without the cap.
- **RL** has no queue: each of the 23 children the beam chose and the cap dropped took a slot a larger cap would have
  used, so `would_pop == dropped` (5 of 30 rows). The policy reads relators of at most 24 letters, so the cap cannot be
  raised, and the 5 rows (6, 13, 18, 26, 28) were all solved in these runs.
- **U124 under S20_MK2** loses the most: 122 of 124 rows drop children and 93 would pop. In 15 rows (`aca_99` to
  `aca_113`) the capped queue ran dry after 643 to 9,220 pops, before the budget, so cap 24 had exhausted the states
  it could reach; uncapped, the same rows spend all 10,000 pops. None is solved either way.

### The hybrid

Its three limits (`r2_cap`, `dyn_cap`, `slack`; [CAP.md](CAP.md)) are counted separately, with defaults `"parent"`, 8 and 8.

| run | solved | `r2_cap` ("parent") dropped | `dyn_cap` 8: rows dropping / would pop | `dyn_cap` dropped / would-pop | `dyn_cap_needed` | first bind | `slack` 8: rows dropping / would pop | `slack` dropped |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `ms640_hybrid` | 640 / 640 | 0 | 2 / 0 | 766 / 0 | - | - | 0 / 0 | 0 |
| `ac19_hybrid` | 72,779 / 72,779 | 0 | 409 / 344 | 4,704,033 / 8,010 | 9-13 | 3 | 11 / 0 | 33 |
| `ac1m_hybrid` | 71,281 / 71,283 | 0 | 290 / 238 | 3,540,728 / 5,807 | 9-23 | 4 | 19 / 0 | 81 |
| `bench60_hybrid` | 60 / 60 | 0 | 1 / 0 | 383 / 0 | - | - | 0 / 0 | 0 |
| `holdout60_hybrid` | 60 / 60 | 0 | 0 / 0 | 0 / 0 | - | - | 0 / 0 | 0 |
| `u124_hybrid` | 0 / 124 | 0 | 123 / 118 | 18,884,638 / 84,093 | 9-15 | 3 | 103 / 0 | 26,807 |
| `ladder60_hybrid` | 60 / 60 | 0 | 7 / 7 | 273,121 / 192 | 9-13 | 54 | 0 / 0 | 0 |
| `ladder200_hybrid` | 188 / 188 | 0 | 23 / 21 | 606,830 / 559 | 9-13 | 14 | 1 / 0 | 8 |

The `ladder200_hybrid` summary was written before the last change to the hybrid's limit counters: run again on the
current code it counts 507 `dyn_cap` would-pop states where the stored file has 559, with every other field equal
(solved, units, the other counters).

- **Reading the hybrid columns.** A hybrid `*_dropped` counts classes of dropped children (plus the tail moves of the
  solving pop), not moves, and `*_would_pop` counts distinct canonical pairs; a zero still means that a larger limit
  pops the same states, and a non-zero count says only that the run may change (the count is first order, see
  CAP.md). `r2_cap = "parent"` cannot reject, and rejected nothing in any run. `slack` 8 dropped children
  in `ac19_hybrid`, `ac1m_hybrid`, `u124_hybrid` and `ladder200_hybrid`, never one that would pop. `dyn_cap` 8 is the
  limit that binds: 344 AC19 rows and 238 AC1M rows would pop (`raise_ids` keeps 100), with `dyn_cap_needed` up to 13
  and 23, yet the totals 72,779 / 72,779, 71,281 / 71,283 and 2,489,726 and 2,384,509 units hold at 8. On MS640
  `dyn_cap` drops in 2 rows (766) and none would pop, so the published 640 / 640 in 25,064 units is independent of the
  limits.

### Rank-n brute force

The rank-n summary counts searches (one per start), not moves; the cap counters are stored per start.

| run | rows | searches | cap dropped a child in | a dropped child would have popped in |
|---|---:|---:|---:|---:|
| `rank3_bf` | 640 | 51,200 | 8 | 0 |
| `rank4_bf` | 223 | 78,273 | 0 | 0 |
| `rank5_bf` | 32 | 3,840 | 0 | 0 |
| baseline (stored study), ranks 3 to 5 | 640 | 40,098,032 | 2,331,711 | 0 |

So no rank-n result depends on the cap 24: in acx's runs a dropped child would have been popped in none, and in the
baseline's whole study (every one of its 40,098,032 searches stores the cap counters) the cap could bind in none; its
test is conservative, so a bind it rules out is ruled out here too.
`results/stable_ac/rank3_bf/cap/cap_counters_cap24.md`. The rows and slices of each run are in section 0.

### The 20 MS640 rows where S20_MK2 at cap 24 would pop

`ms640_s20_mk2_fast` reports 20 rows with `cap_would_pop` > 0 (527, 529, 616 to 625, 628 to 630, 633 and 636 to 639),
all with `cap_needed` 25. Rerun at cap 24, at cap 25 (the needed cap) and uncapped, with the pop trace kept:

| row | solved | pops at 24 | pops at 25 | pops uncapped | `cap_would_pop` at 24 / 25 | `cap_first_bind` | pop where the traces part | S-moves |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 527 | yes | 7,458 | 7,479 | 7,479 | 21 / 0 | 1,653 | 1,653 | 120 |
| 529 | yes | 7,445 | 7,466 | 7,466 | 21 / 0 | 1,653 | 1,653 | 114 |
| 628 | yes | 7,074 | 7,092 | 7,092 | 18 / 0 | 693 | 693 | 117 |
| 629 | yes | 7,254 | 7,275 | 7,275 | 21 / 0 | 1,353 | 1,353 | 86 |
| 630 | yes | 7,208 | 7,229 | 7,229 | 21 / 0 | 1,353 | 1,353 | 79 |
| 633 | yes | 7,063 | 7,081 | 7,081 | 18 / 0 | 693 | 693 | 111 |
| 619 | no | 10,000 | 10,000 | 10,000 | 9 / 0 | 309 | 309 | |
| 623 | no | 10,000 | 10,000 | 10,000 | 9 / 0 | 474 | 474 | |
| 636 | no | 10,000 | 10,000 | 10,000 | 77 / 0 | 4,036 | 4,036 | |
| 639 | no | 10,000 | 10,000 | 10,000 | 9 / 0 | 2,152 | 2,152 | |

- The 20 are confirmed: all of them change at cap 25. In each, the pop trace at cap 24 departs from the cap-25 trace at
  exactly pop `cap_first_bind`, and the cap-25 trace equals the uncapped trace at every pop (so `cap_needed` 25 is a
  sufficient cap here, and `cap_would_pop` is 0 at 25).
- The cap changes pops and not outcomes: the 6 solved rows solve at 24, 25 and uncapped, 18 to 21 pops later at the
  larger cap and with the same stored path; the other 14 stay unsolved at all three. So 626 of 640 holds at every cap
  from 24 up.

### Do the raise-the-cap rows change a count?

For every run whose `raise_ids` is not empty, the rows were rerun uncapped (hybrid: `dyn_cap` 13, the largest
`dyn_cap_needed` on those rows):

| run | rows rerun | solved | pops (units) before / after | S-moves of the solved rows |
|---|---:|---|---:|---:|
| `ms640_s20_mk2_fast` | 20 | 6 / 6 | 183,502 / 183,622 | 627 / 627 |
| `ms640_aut` | 20 | 6 / 6 | 185,090 / 185,222 | 684 / 684 |
| `bench60_s20_mk2` | 10 | 2 / 2 | 94,137 / 94,173 | 228 / 228 |
| `bench60_aut` | 10 | 2 / 2 | 95,030 / 95,074 | 228 / 228 |
| `holdout60_length` | 1 | 0 / 0 | 10,000 / 10,000 | |
| `holdout60_s20_mk2` | 6 | 1 / 1 | 51,450 / 51,451 | 88 / 88 |
| `u124_s20_mk2` | 93 | 0 / 0 | 839,399 / 930,000 | |
| `ladder60_length` | 1 | 0 / 0 | 10,000 / 10,000 | |
| `ladder60_s20_mk2` | 31 | 6 / 6 | 284,384 / 284,561 | 359 / 359 |
| `ladder200_length` | 3 | 0 / 0 | 30,000 / 30,000 | |
| `ladder200_s20_mk2` | 77 | 16 / 16 | 703,308 / 703,712 | 884 / 884 |
| `ladder60_hybrid` (`dyn_cap` 13) | 7 | 7 / 7 | 2,925 / 2,886 units | 146 / 157 |
| `ladder200_hybrid` (`dyn_cap` 13) | 21 | 21 / 21 | 7,202 / 6,960 units | 410 / 435 |

- **No solved count changed** in any run, and no solved greedy row got a different S-move or elementary length. The
  pops of a solved row move by a few (+1 to +21), because states the cap had removed sort in front of the solution;
  `u124_s20_mk2` spends more pops uncapped only because 15 of its capped queues had run dry.
- **The hybrid does change**, as its counters warned: at `dyn_cap` 13 the 21 `ladder200` rows still solve, in 3 percent
  fewer units, but with 25 more S-moves in total, and 36 states still would pop at 13 (a further raise changes the run
  again).
- To redo one: `python run.py --config configs/s20_mk2_fast.toml --rows 527 --set search.cap=25 --set
  name=ms640_s20_mk2_row527_cap25` (a hybrid row: `--set hybrid.dyn_cap=13`). Give a new name: without one the run
  goes to `results/s20_mk2_fast/`, and a published folder refuses a run of fewer rows.


## Reading the numbers

- **Budget** is heap pops (`nodes_explored`, "nodes"). A search at budget B is exactly the first B pops of any longer
  search of the same row, cap and priority, so a result at B can be read off a longer run.
- **Cap** is the per-relator length limit on generated children (`mrl`). **24, 48 and 64 are caps, never path
  lengths.** Only runs at the same cap are matched comparisons; a cap mismatch is flagged where it occurs.
- **Path length** is in substitution moves (S-moves) unless a line says "elementary". One S-move is one conjugated
  multiplication, which costs many elementary moves (see Decoder, below). The two units are never mixed.
- **Hybrid cost** is in "work units" (a popped state, an accepted automorphism, an image evaluation or a substitution
  move), not nodes. Unit counts and node counts are not comparable.
- **Certificate kinds.** `ac_path`: a replayed sequence of AC moves on the row as written. *Aut-assisted*: the search
  changed basis; it is an `ac_path` only after the decoder or transport expands it. `stable_cert`: proves *stable*
  AC-triviality (a change of variables, or define/eliminate steps) and says nothing about the length of an AC path on
  the original row.

### Corrections applied to the earlier survey

- 48 and 24 in "bench60 at 10k: 52/60 vs 40/60, mean path 48 vs 24" are the relator caps of the two arms, not path
  lengths. The published S20_MK2 column used cap 48 and the frozen greedy column cap 24, but a same-cap rerun at cap
  24 reproduces 52/60 against 40/60 and the node figures exactly (section 2), so the cap mismatch does not change the
  result. The mean paths are 62.25 (S20_MK2, own 52 solves) and 36.88 (length, own 40) S-moves. **[rerun]**
- "37/60 vs 29 at 1k" is S20_MK2 against length-only, not a depth tie-break result.
- "221 vs 39 unsolved on hard rows at 100k" is the AC19 Aut-min hard tail (70,723 orbits, cap 48), not MS640.
- AC19 Aut-min at 10k: quote the complete run, **72,519 vs 71,936 of 72,779**. The earlier 68,971 vs 68,412 of 69,224
  came from partly merged chunks.
- Two different CoV costs exist and are never interchangeable: a mean of **172,867 nodes per presentation** (the full
  CoV portfolio at budget 10,000, 40 rows) and **about 2.2M nodes per presentation** (finding the oracle start for
  the eight CoV-resistant rows at 20,000 nodes: 909 searches, 17,313,543 nodes).
- The CoV gains carry a **cap confound**: transformed starts run at `max(24, longest + 16)` (up to 41), controls at 24.
- The cascade's 70,649 solves are 27,164 substitution-only certificates plus 43,485 aut-assisted ones.
- The AC1M 1,136,135 total is 1,056,357 solved in the final pass (of 1,056,376 rows run) plus 79,778 carried over from
  earlier runs.

---

## 1. Baseline: length-only greedy

Best-first search ordered by total relator length, Definition 2.1 substitution moves, cap 24.

- **MS640 at 1,000,000 nodes, cap 24: 640/640 solved.** Nodes min/median/mean/max = 3 / 11 / 4,963.0 / 574,959; total
  3,176,297. Path (S-moves) min/median/mean/max = 2 / 9 / 36.77 / 708. At 50,000 nodes: 628/640.
  `claude/summer-results-docs-scoring-u6klsb:benchmark/BASELINE.md`, `benchmark/difficulty_bins.csv`.
- **Two-hump cost.** Bins 0 to 3 hold 529 of 640 rows and 0.69% of all nodes; the top six rows hold 66.8% and the top
  twenty 86.2%. The 640 rows fall in 113 Aut(F2) classes; class 106 spans 14,415 to 272,953 nodes, so cost is not an
  orbit invariant. Search cost and certificate length also disagree: rows 634/635 cost 574k nodes for an 80-move path,
  row 623 costs 59,710 nodes for a 708-move path. Same file.
- **bench60** (`benchmark/subsets/benchmark_subset_60.json`, six rows per difficulty bin): length-only greedy solves
  **29/60 at 1,000 nodes** (mean 176) and **40/60 at 10,000** (cap 24).
  `claude/heuristic-search-benchmark-e1f9l8:experiments/search/HEURISTICS.md`.
- **Smaller budgets, cap 24, all 640 rows [rerun]:** 606/640 at 10,000 nodes (mean path 19.97, median 8 S-moves;
  576,053 pops in total) and 554/640 at 1,000 (mean path 12.09; 122,208 pops). Per-row files:
  `work/reference/greedy_length_ms640_b{10000,1000}_cap24.csv` (not in git); on bench60 at 10,000, 40/60 with 48,227
  pops on the solved rows (`greedy_length_bench60_b10000_cap24.csv`).
- **Test oracle.** A pure-Python specification (AC4/AC5, the |det| = 1 invariant, general n-relator S-move) agrees
  with the numba baseline; 554 of the 640 rows solve within 1,000 nodes (ladder level 1).
  `test/greedy-test-suite:experiments/greedy_tests/`, `golden/greedy_golden.json`.

## 2. S20_MK2 priority (L + 20 S + 2 MK)

One linear vector over three of 17 block/knot features, lower pops first. It replaced the withdrawn `RECOMMENDED`
vector (Tried, below).

- **Selection protocol.** Selected on the `ac1m_hard_aut` train 120 (budget 1,000); evaluated on Aut-disjoint holdouts
  read once. Length-only scores 0/120, 0/60 and 0/60 on the three slices; S20_MK2 scores **54/120 (train), 33/60
  (spent holdout), 27/60 (fresh holdout)**. The grid's own top scorer `S28_MK2_F8` (57/120 on train) fell to 22/60 on the
  fresh holdout and was not shipped.
  `claude/heuristic-search-benchmark-e1f9l8:experiments/search/HEURISTICS.md`;
  `experiments/ppo:results/heuristic_search/smk_f_grid/HOLDOUT.md`; splits in
  `experiments/ppo:results/heuristic_search/splits/` (`splits_ac1m_hard_aut.json`, seed 20260729, 120 train / 60
  holdout; `splits_fft_fresh_holdout60.json`).
- **bench60.** 37/60 against 29/60 at 1,000 nodes (mean nodes 153 vs 176). At 10,000 nodes **52/60 against 40/60**, a
  strict superset (McNemar 12 to 0), median nodes 86 vs 197 and mean 280.1 vs 1,205.7 on the 40 rows both solve.
  The published S20_MK2 column ran at cap 48 against greedy's 24; **a same-cap rerun at cap 24 reproduces every one
  of these figures** (52 vs 40, 12 to 0, medians 86 vs 197, means 280.1 vs 1,205.7, and at 1,000 nodes 37 vs 29 with
  means 153 vs 176), so the cap mismatch does not move them. Paths are longer: mean 62.25 vs 36.88 S-moves on each
  arm's own solves, 36.08 vs 36.88 on the 40 shared. **[rerun]** `work/reference/greedy_*_bench60_b10000_cap24.csv`
  (not in git).
- **MS640 at 10,000 and 1,000 nodes, cap 24 [rerun].** At 10,000: S20_MK2 626/640 against length 606, a strict
  superset (20 to 0, 14 solved by neither); mean path 26.95 vs 19.97 on own solves; on the 606 shared rows 143,722 vs
  236,053 pops. At 1,000: 574 vs 554 (24 to 4, 62 neither). `work/reference/greedy_*_ms640_b{10000,1000}_cap24.csv`
  (not in git).
- **MS640 at 1,000,000 nodes, cap 24, same engine, only the ordering differs: 640/640 both.** Mean nodes **994.8 vs
  4,963.0** (4.99x), total 636,670 vs 3,176,297, max 34,438 vs 574,959; the 14 rows needing over 10,000 nodes under
  both orderings average 28,139 vs 96,150. **Paths are longer:** mean 42.88 vs 36.77 S-moves.
  `results/ms640-s20-mk2-1m:results/heuristic_search/ms640_s20_mk2_1m/RESULTS.md`.
- **AC19 Aut-min, all 72,779 orbits, budget 10,000, cap 48 (complete run).** Solved **72,519 vs 71,936** (unsolved 260
  vs 843); within 1,000 nodes 68,475 (94.1%) vs 66,086 (90.8%); mean path 25.9 vs 27.7 on solved rows. The 831 and 259
  archived failure lists reproduced bit for bit (verdict and node count).
  `claude/ac19-leftover-solver-notebook-6yan6d:results/heuristic_search/ac19_autmin_10k/RESULTS.md`.
- **AC19 hard tail at 100,000 nodes, cap 48, 70,723 orbits searched by both arms.** Unsolved **221 (length) vs 39
  (S20_MK2)**; 182 of length's failures are recovered and none the other way. On the 70,502 both solve: mean nodes
  563.3 vs 263.2, mean path 23.50 vs 26.57.
  `results/ms640-s20-mk2-1m:results/heuristic_search/hsearch_ac19_hard100k/RESULTS.md`.
- **Cost of the ordering.** The 17 features are computed once per state and cached, so a weighted config runs within
  noise of pure length; the search trajectory is what moves the clock. On mid-difficulty rows at 1,000 nodes the
  earlier S-family arms lost a few solves that length kept (`s24` 1,364/1,372, `recommended` 1,344/1,372, length
  1,372/1,372), so an S ordering trades a few easy rows for the hard tail.
  `cursor/heur-12h-anti-overfit-a42e:results/heuristic_search/campaign_12h/RESULTS.md` (the same page: on 590 hard
  never-read AC1M rows at 1,000 nodes, length 0, `recommended` 119, `s24` 204).
- **Depth term.** Adding `w * depth` to the score (EXP-11) beat its zero-depth incumbent in 1 arm of a 216-arm sweep
  (`length` + 0.25 depth at budget 500: 18/40 vs 17/40), which the page itself reads as noise.
  `cursor/heur-depth-tie-a42e:results/heuristic_search/runs/EXP11_depth.md`.

## 3. Fast engine (numba, packed states)

`hexpand` (fused child expansion and scoring) plus `hcompact` (2-bit packed arena, int32 heap, open-addressing visited
table). Every promoted change was gated bit-identical against the Python oracle and the frozen engine.

| change | measured | where |
|---|---|---|
| 2-bit symbol packing | 83 to 51 B/state at cap width without paths (-38.6%); 56.4 to 44.4 at starting width; peak RSS -23% to -27% | `perf_lab/REPORT.md` |
| zero-allocation expansion kernel | 1.72x to 1.74x pops/s (4 rows, 50k pops) | same |
| integrated (2-bit + kernel) | median 1.742x, geometric mean 1.744x (6 rows, 100k pops) | same |
| cut-shift duplicate skip | 1.554x on aca_47 at 300k pops | `perf_lab/EXPAND_SPLIT.md` |
| + packed canonicalisation | 2.341x cumulative (the step's own factor 1.506) | same |
| campaign box, per pop | **941.6 to 209.8 us (4.49x)**, same search statistics (44,077,944 states, 331.7 candidates per pop) | `perf_lab/REPORT.md` |
| 10M-node rows | 4.4x to 5.2x faster per row (12,320-13,428 s to 2,350-2,839 s); about 23,000 nodes/s over six lanes vs about 5,400 before | `results/heuristic_search/u124_10m/RESULTS.md` |

All on `codex/ac-elementary-decoder` (none is in this repository): the `perf_lab/` pages under
`experiments/heuristic_search/core/`, and the 10M-node row timings at
`codex/ac-elementary-decoder:results/heuristic_search/u124_10m/RESULTS.md`.

- **Which ratios carry.** The lab's 1.7x from the first two changes did not carry to campaign-length relators (per lane
  0.95x to 1.15x); the campaign gain of that step was memory turned into lanes (4 to 6, per box about 1.46x). The 4.49x
  is the later expansion work, measured on a different host (Xeon 6975P-C) from the lab (2.8 GHz Xeon, 4 cores). Absolute
  pops/s differ by host; ratios are the claim.
- **Reservation.** At 2,140,016,900 states a lane reserves 117.6 GiB instead of 181.4 GiB.
- **Other numba twins.** `solvern_fast` (n generators) is 4.6x to 5.9x faster with every result field bit-identical
  (`research/w5/stable-ac-escape:experiments/stable_ac/nocov/PIPELINE.md`). `autcanon_fast` (Whitehead canonical form)
  is about 15x end to end with identical rows (`research/w5/stable-ac-escape:CLAUDE.md`, pinned by
  `tests/stable_ac/test_autcanon_fast.py`). `greedy_nrel` went from 364 to about 3,300 nodes/s (9x)
  (`test/stable-ac-moves:CLAUDE.md`).
- **Superseded.** The 2.78x "heavy solver" (177 vs 492 us/node, 400 runs, 0 mismatches) on `test/greedy-test-suite` is
  replaced by the engine above; keep its parity runs as a test.
- **Path capture.** `hcompact` returns no path unless `track_path=True` (8 B/state, about 8% on top of the arena).
- **`acx.search.fast` (this branch)** ports the expansion kernel and the arena/heap/dedup design but not the 2-bit
  packing (it worked at two generators only): one byte per symbol, about 100 to 120 B per state at cap 24 with path
  capture, against 52 to 68 B in `hcompact`. Fine to about 1M pops a row; a 10M-pop campaign wants the packing back
  (open). Speed against `spec`: 32x the CPU over the whole MS640 LENGTH run, 45x in pops/s on search alone (section
  0 gives both workloads).

## 4. Hybrid solver ("solve everything")

`hfhybrid`: rank-two best-first search on the `hexpand` kernel, four Nielsen maps, signed-permutation canonical form,
and dynamic-rank `define`/`eliminate` moves on one frontier. It does not use `hcompact`; it runs a Python heap with
block-sorted closed sets, and its cost unit is the work unit. Budget 1,000 units unless stated.
`claude/vigilant-babbage-nnbuj0:research/ac_hashfree_cascade_20260914/RESULTS.md`.

| set | rows | solved | notes |
|---|---:|---:|---|
| MS640 | 640 | **640** | 2.22 s of search time on one core, by the source (5.76 s batch under the cascade's protocol, which includes verification and cooldowns); at most 283 units on a row. The cascade it replaces: 2.36 s / 6.32 s, max 404 |
| AC19 Aut-min census | 72,779 | **72,779** | 95 s wall on 4 workers; median 27 units, p99 128, max 954. 72,591 rank-two certificates plus **188 stable** |
| the 727 rows the earlier policy missed | 727 | 727 | |
| the 9 rows unsolved by every fixed-basis arm at 10M nodes | 9 | 9 | the rank-two engine already solves all 9 (7 at 318 units or fewer, 2 need permutation canonicalisation at 440 to 545) |
| `AC19_extended.txt`, original spelling | 156,762 | **156,762** | 177 s; 156,435 rank-two plus **327 stable** |
| AC1M Aut-min | 71,283 | 71,281 | the 2 misses solve at 1,035 and 1,138 units |
| AC1M raw | 1,136,154 | **1,136,135** | 1,056,376 rows run in the final pass (1,056,357 solved) plus 79,778 carried over; the 19 misses are members of the same 2 orbits and solve at 1,040 to 1,153 units |

- **MS640 rerun [rerun].** 640/640 solved and 640/640 replayed by the branch's own verifier at the default budget
  1,000, penalty 5, `dyn_ratio` 0.5; every certificate is an explicit rank-two certificate (no `define`/`eliminate`).
  Units: 25,064 in total, at most 283 on a row. Finishing stage: relator descent 98 rows, pinch cascade 328, best-first
  search 214 (the search part's path sums to 4,759 substitution steps, mean 22.24, max 72). Wall time of the rerun,
  warm: 2.4 s for all 640 on one core (the whole batch, not the search time of the table); the first call adds about
  36 s of numba compilation. `work/reference/hfhybrid_ms640_b1000.*` (not in git).
- **Certificate scope.** Rows with `define`/`eliminate` steps are `stable_cert`, not `ac_path`. Every stored certificate
  replays under two independent verifiers, 0 failures.
- **Ablation** (the 727 policy leftovers, 1,000 units). No closed set: 9/604 (best-first or beam 8). Block-sorted closed
  set, no Nielsen edges: 31/180. Plus the four Nielsen maps as edges: **673/727**, the largest single gain. Signed-
  permutation canonicalisation then takes 23 of the 54 left, and the hybrid all 727. "Hash-free" means no hash table:
  the visited set is a block-sorted array searched by bisection, which reproduces the hashed control pop for pop.
- **Cost accounting.** `acmoves` counts multiplication operations only (conjugation and inversion are free).
- **Lineage, in order.**
  - 501-node cascade (`s40_gen` with Nielsen images in the heap, plus `bs_collapse`): **70,649 of 72,779 (97.07%)**.
    27,164 are substitution-only certificates and 43,485 are aut-assisted. The AC-only control (`ac501`, same priority,
    no Nielsen image) certifies 64,541 (88.68%) at the same budget.
    `codex/ac-elementary-decoder:results/heuristic_search/ac19_cascade_screen/RESULTS.md`.
  - `cascade_bs` (the Baumslag-Solitar pattern tested at every popped state, not only the input) lifts 70,649 to 71,579
    at the same 501-node budget: the residue falls from 2,130 to 1,200 unsolved (-43.7%), nodes explored -10.1%.
    `claude/ac19-leftover-solver-notebook-6yan6d:results/heuristic_search/ac19_bs_probe/RESULTS.md`.
  - `final_policy`: 72,052/72,779 at 1,000 units.
    `claude/results-collection-org-wmvpxu:results/heuristic_search/ac19_final_policy_full_1k/README.md`.
  - Cascade without table 72,562; with the cap-14 backward ball 72,779 at 949,521 charged units against the policy's
    6,621,411 (**7.0x fewer**). The table has 12,803,449 states (281.7 MB npz, 1,612 s to build) and 66,151 of the
    72,779 roots (**91%**) lie inside it and cost 0 charged units, so the unit comparison is partly precomputation.
    `claude/ac19-theorem-strength-8v1wp6:research/residual_20260909/CAMPAIGN_REPORT.md`.

## 5. Change of variables (default one-shot, family `subnc2pxysb`)

CoV certifies **stable** AC-triviality of the original through a transformed two-generator pair. Every CoV path length
is in the transformed presentation's coordinates, so these are `stable_cert` results (METHODS.md).

- **10,000-node sweep, 66 presentations (bench60 plus 6).** Plain greedy 40/66; some CoV start solves **52/66** (12
  flips); 14 solved by nothing at this budget, of which 8 (one Aut class, `ms622` to `ms625`, `ms636` to `ms639`)
  escape at 20,000 nodes. On the 40 solved by both, best-CoV total nodes 2,878 vs 48,227 (16.76x), path shorter on all
  40. `research/w5/stable-ac-escape:results/stable_ac/cov/graphs/SUMMARY_b10000.md`.
- **That is an oracle.** On those 40 rows the best start costs a mean of 72 nodes (median 14) only once you know which
  `z` wins (over all 60 bench60 rows at budgets up to 20,000 the oracle's mean is 2,383, median 34.5). The full portfolio
  costs a mean **172,867 nodes per presentation** (6.9M over 40 rows), and a deployable strategy runs the original
  first, which costs exactly greedy's 1,206 mean on rows greedy can solve. Priced that way, with that report's tuned
  heuristic (the withdrawn `RECOMMENDED` vector, so in-sample): on rows greedy solves the heuristic is about 5.6x cheaper
  than greedy (215 vs 1,206) and CoV adds nothing; on the 7 rows greedy cannot solve within 10,000 nodes the heuristic
  gets them for 106 to 7,641 nodes and CoV for 21,277 to 63,211; only CoV reaches `ms596`, `ms605`, `ms610`, `ms634`,
  `ms635` (about 32,000 nodes each). The eight CoV-resistant rows cost about 2.2M
  nodes per presentation to find an escape start, ten times what running greedy longer costs.
  `research/w5/stable-ac-escape:results/comparison/THREE_WAY_COST.md`,
  `results/stable_ac/cov/allcov_escape/ESCAPE.md`.
- **bench60 at 10,000 nodes, cap 24 controls:** greedy 40/60, best-CoV oracle **52/60**, withdrawn `RECOMMENDED`
  47/60. At 1,000 nodes the one-hop oracle ceiling is 45/60 against greedy 29/60 and `RECOMMENDED` 43/60. **Cap
  confound:** transformed arms run at `max(24, longest + 16)`, up to 41 here (the exhaustive sweep's starts below: 24
  to 91); an Aut-min-only control at the same cap already reaches 36/60 at 1,000 nodes, against 29/60 for the original
  at the same cap.
  `claude/abelianized-exponents-verify-1i6muh:benchmark/subsets/ARMS.md`;
  `cursor/heur-u124-s20mk2-a42e:results/comparison/COVBEAM_K4_B1K_ADVISOR_REVISE.md`,
  `results/comparison/covbeam_nonsym_b1kfull_subset60.md` (the 36/60).
- **The exhaustive CoV sweep on MS640** (`cov/all-subsets-sweep` at `fb84a588`, stored in
  [results/stable_ac/cov_all/](../results/stable_ac/cov_all/README.md)): every start of the `suballpxyb8` family,
  114,042 CoV starts plus the 640 controls, each searched with the full budget, LENGTH, at budgets 100, 10,000 and
  100,000 (a smaller budget is read off a larger run's records, so 1,000 is given too). The paths below are in this
  repository.
- **Budget 100 on MS640, all 640 presentations** (1.086 CPU-hours). From the stored summary: untransformed control
  **455** (cap 24); best-start oracle over the exhaustive `suballpxyb8` family **555**, and over its one-pattern starts
  also **555**; 0 presentations are solved only by a multi-pattern start; summing every start, the oracle's real cost
  is a mean of 5,328.4 nodes per presentation (median 1,371.5, max 173,997).
  `results/stable_ac/cov_all/cov_all_suballpxyb8_ms640_b100_summary.md`. From the survey's rerun over the sweep's
  jsonl (`work/all_subsets_sweep.md`, not in git; tests 40/40 pass, the summary regenerates exactly): restricting the
  oracle to the default `subnc2pxysb` starts gives the same **555** (the same 100 gained presentations), with 21.4
  starts per presentation on average against 178.2 (about 8.3x the search work for 0 extra solves); bench60 17/60 to
  34/60; bins 7 to 9 stay at 0 either way; 90,234 of 90,234 stable certificates replay. Caveat: the oracle assumes the
  best start is known.
- **Budget 10,000 on MS640, all 640 presentations** (the same family and starts, 49.8 CPU-hours; read from its summary
  files): control **606**, best-start oracle **626** over all starts and **626** over one-pattern starts; at 1,000
  nodes 554 / 604 / 604. No presentation at any budget is solved only
  through a start outside the one-pattern set. The oracle's real cost is a mean of **164,758.7 nodes per presentation**
  (median 2,001.5, max 7,847,894). bench60: control 40, oracle 52. The 20 rows solved only from a CoV start (568 to 635)
  and the 14 that no start solves (616 to 625, 636 to 639) are **exactly** S20_MK2's 20 extra solves and 14 failures at
  10,000 pops in one search (section 0), at 598 pops per presentation on average. Both 626s are **oracle** arms (the
  best of 114,042 starts known in advance); the deployable one-shot CoV of this package reaches 584 (section 0). **Cap
  confound:** controls ran at cap 24, the CoV starts at `max_relator_length_cap` 24 to 91 (109,336 of the 114,042
  starts above 24). `results/stable_ac/cov_all/cov_all_suballpxyb8_ms640_b10000_summary.md`, `..._subset60_summary.md`;
  the caps from `cov_all_suballpxyb8_ms640_b10000.jsonl.gz` (not in git, listed in
  `results/stable_ac/cov_all/MANIFEST.json`).
- **Budget 100,000 on MS640, all 640 presentations** (335.2 CPU-hours): control **634**, best-start oracle **640** over
  all starts and over one-pattern starts; bench60: control 54, oracle 60. The control fails on rows 634 to 639, each
  solved by 16 or 17 of its starts, and these six stay unsolved by the control at cap 64 and uncapped, so they are not
  a cap artifact. The oracle's real cost is a mean of **657,198.0 nodes per presentation** (median 2,001.5, max
  55,122,480). A random start against the control: fewer nodes 33.7%, the same 9.6%, more 52.4%, unsolved 4.2% (at
  10,000: 33.0 / 9.6 / 48.2 / 9.2). By acx's typing (a start in the row's Aut orbit carries back to an `ac_path`), the
  best start of a presentation is the control on 3, a start in the orbit on 329 and a start outside it (a
  `stable_cert`) on 308; at every budget, each presentation that some start solves and the control does not also has a
  solving start in its orbit. `results/stable_ac/cov_all/cov_all_suballpxyb8_ms640_b100000_summary.md`, the study
  README.
- **The default family inside the sweep.** Restricted to the default `subnc2pxysb` family's 13,727 classes (searched
  once each, from the sweep's representative), the best start solves the same 555 / 604 / 626 / 640 presentations at
  100 / 1,000 / 10,000 / 100,000 nodes. Under the shipped one-shot policy (`configs/cov.toml`, 1,000 pops per image,
  10,000 per row), `family = "suballpxyb8"` solves bench60 39, MS640 584, ladder200 47 and ladder60 16, against
  39 / 584 / 92 / 32 for the default family: its enumeration order spends the legs on near-copies of the shortest `w`.
  Measured for this release with `acx.cov` (`class_key` over the stored records, `run.py` for the policy); the scripts
  are not in git. So the exhaustive family costs 8.3x the starts for no extra solve as an oracle, and solves fewer
  ladder rows as a policy.
- **Certificates.** Every solved-row certificate under `research/w5/stable-ac-escape:results/stable_ac/` (CoV and
  no-CoV runs alike) replays through the pure-Python specification: 13,649 solved rows (45,633 rows in 14 files), with
  0 budget-invariance violations over 6,608 jobs seen at more than one budget.
  `research/w5/stable-ac-escape:results/README.md`.

## 6. Automorphisms: Whitehead canonical form and certificate transport

- **Canonical form.** Aut(F2) orbits are identified by Whitehead's algorithm (peak reduction, then the lex-minimum of
  the minimal level set), a complete invariant. MS640 has 113 classes; `AC19_extended` (156,762 rows) has 72,779 orbits;
  AC1M (1,136,154 rows) has 71,283, of which 4,672 have no AC19 member.
- **Aut-minimising can make search harder.** On the 40 originals of the AC19 10M residue, greedy solves 40/40 (median
  5,720 nodes, max 52,143) and S20_MK2 18/18 (median 1,575, max 10,229), while **none of their Aut-minimal
  representatives solves at 10,000,000 nodes** (0 of 28 for greedy, 0 of 9 for S20_MK2). Aut-minimising shortens the start on 34 rows and raises the peak length
  on 40/40 (median 29 to 49). Within-orbit cost varies up to 31x.
- **Transport.** AC moves are Aut(F2)-equivariant (a move `r_i <- r_i . c^-1 r_j^s c` maps to the same move with
  `c -> phi(c)`), so an original's path carries to its representative step by step; the resulting basis is Nielsen-reduced
  by a 1 to 4 move tail. **58/58 certificates replay from the representative's own words** (40 greedy, 18 S20_MK2),
  with 2,211/2,211 and 1,069/1,069 steps checked equivariant. Over the 28 representatives the shortest transported
  certificate is min 25, median 56, max 137 S-moves. This is a certificate, not a search result: the representatives
  still do not solve. `claude/ac19-leftover-solver-notebook-6yan6d:results/heuristic_search/ac19_orig_10m/RESULTS.md`.
- **Decoder.** The elementary decoder turns all 640 saved MS640 cascade certificates into generator-level AC moves:
  **2,388,332 elementary moves**, median 226, mean 3,731.77, max 159,704 (`ms637`); 6.45 s wall for conversion and
  built-in replay, and every row replays from its input to `[x, y]`. The output is 28,785,317 bytes and regenerates in
  seconds. Elementary and S-move lengths are different units; these paths come from the cascade, not from greedy.
  `codex/ac-elementary-decoder:results/heuristic_search/ms640_elementary_ac/RESULTS.md`.

## 7. n-generator search

- `solvern` is trace-equal to the pure-Python specification at up to three generators and runs at any `n_gen`
  (26 or fewer) with any number of relators; `solvern_fast` is 4.6x to 5.9x faster, bit-identical.
  `research/w5/stable-ac-escape:experiments/stable_ac/`.
- **Adding a generator `z = w` to a two-generator presentation does not help plain greedy.** On MS640 at 500,000 nodes
  the four arms (`w` = r1, r2, x, y) solve 619, 602, 540 and 523 of 640, against 638 for the two-generator baseline at
  that budget (derived from the per-row costs: only rows 634 and 635, at about 574k nodes, exceed it); 0/261 on the hard
  Aut-class representatives. `test/stable-ac-moves:results/stable_ac/3_generators_w_choices/README.md`.
- **Every word, as an oracle** (the rank-n brute-force study: MS640, LENGTH, cap 24, stored in
  [results/stable_ac/rank3_bf/](../results/stable_ac/rank3_bf/README.md)). At budget 1,000, over the 59,048 words of
  length 1 to 10, some word solves 578 against the control's 554 (24 gained, 0 lost), but no single word solves as many
  as the control: the best, `yXYYYxyyy`, picked with hindsight, solves 528. At 10,000 (lengths 1 to 7) the oracle's
  edge is 608 against 606. Two or three added generators gain nothing: rank 4 (words of length 3 or less) 506, rank 5
  (length 2 or less) 416. `rankn` reruns rank 3 at lengths 1 to 4 cell for cell (section 0).
- **Inside the hybrid** the same idea is `define`/`eliminate`: 188 of the 72,779 census representatives (327 of the
  156,762 original spellings) needed a stable certificate. Section 4.
- **Transform to relators of length 3 or less.** `triangulate` (in `dynrank.py`) applies `define` to the most frequent
  cyclic digram until every relator has length at most 3 (rank 2 becomes rank 7 to 9 on hard AC19 rows); every step is
  a certificate step. Searching from that all-triangle root with the dictionary frozen is *worse* than not transforming:
  25/60 on bench60 at 2,000 pops against 34/60 for the same engine at rank two, and 0/4 on four hard AC19 rows (5/12 on
  an easy control panel). Letting `define`/`eliminate` change the dictionary throughout the search gives 42/60.
- **`acx.ngen` (this branch).** The SAC root searched at fixed rank (LENGTH, cap 24, budget 10,000, fast backend) solves
  **8/60** bench60 rows (rank two: 40/60) and **298/640** MS640 rows (rank two: 606), every solve a `stable_cert` lifted to
  an elementary stable path and replayed (MS640 median 690.5 elementary moves, max 2,230; the root's search path median
  15 S-moves); root rank 4 to 11 (mean 6.99). Every row the SAC root solves, rank two solves too. The 25/60 above used a
  different arm (eliminations allowed, cap 8, its own priority) and is not reproduced here by design.
  `claude/vigilant-babbage-nnbuj0:research/ac_dynamic_rank_20260913/RESULTS.md`,
  `research/ac19_triangle_expansion_20260912/RESULTS.md`.

## 8. RL: PPO and beam

- The paper's agent solves **610 of 1,190** Miller-Schupp presentations against 457 for the prior RL baseline (README
  claim on `main`; the paper is ICML 2026, "The Two-Hump Problem"). The same README's checkpoint section says the
  shipped `610model` "solves 610 of the first 634 presentations", so the denominator of the 610 should be confirmed
  against the paper before it is quoted.
- **PyTorch port** with a JAX-to-PyTorch parity test: max |d logprob| 3.8e-5 on the 610 checkpoint (2.8e-5 on CUDA),
  masks and argmax 256/256. An A100 smoke ran the 610 checkpoint's beam (1024 x 150) on 530 rows: **530/530 solved and
  certified in 300 s**. No training result exists. `experiments/ppo:experiments/ppo/PLAN.md`, `logs/10-08-2026.md`.
- **`acx.rl` (this branch).** The PyTorch port matches the upstream torch code exactly (0 move mismatches over 12,800
  transitions, policy outputs bit-identical) and JAX within 1e-4. Beam width 256, 150 steps, on the first 30 MS640 rows
  through `run.py` (`configs/rl.toml`): 30/30, 9,650 network evaluations, every path replayed by `acx.verify` (section 0;
  the module build's earlier 28/30 is not reproduced and is superseded); 1190MS rows 507 and 527 to 529 solve at 1024 x 150 (path lengths 20, 33, 7, 33).
- **Leakage.** The 610 checkpoint's 49/60 on bench60 (bins 0 to 6 all 6/6, bin 7 5/6, bin 8 0/6, bin 9 2/6) was measured on
  its own training rows: 54 of the 60 are in `AC19_extended`'s pinned prefix. It is a reference line, not a bar.
  `experiments/ppo:experiments/ppo/SHAPED_REWARD_PLAN.md`.
- **A bug as committed.** `main`'s `beam/beam_search.py` restores `solve_data` sized from the current `AC19_extended`
  line count (156,762), against 157,217 in the checkpoint [survey], and raises a shape error. Fixes exist on `test/eda`
  (best-effort restore) and `test/stable-ac-moves` (`--train_rows`).

## 9. The unsolved 124 (U124): 0/124 on every line

550 raw unsolved Miller-Schupp rows reduce to 261 Aut-equivalent representatives and 124 ACA classes (via 168 Aut
orbits [survey]).
Every attempt on them failed:

- 0/261 representatives by greedy at 1,000,000 nodes (cap 48); **0/124 by S20_MK2 at 10,000,000 nodes (cap 64)**;
  0/124 by every cascade probe at 10,000 units; 0/124 from any automorphic image within two Whitehead moves at 20,000
  nodes. `claude/ac19-theorem-strength-8v1wp6:benchmark/ladder/LADDER.md`.
- 0/124 by the dynamic-rank search at 2,000 pops per row; thirteen shorter states found as a by-product.
  `claude/vigilant-babbage-nnbuj0:research/ac_dynamic_rank_20260913/RESULTS.md`.
- 0/124 and no shorter presentation from nine probes at 10,000 units or pops each, among them the cap-14 cascade,
  S20_MK2 with and without Nielsen edges, Whitehead minimisation of every visited state, an *orbit search* that
  re-roots at the Whitehead-minimal representative after every move, and 4,276 automorphic starts. On the 36 classes
  the mu-ladder had shortened, run from their unreduced pairs, the orbit search reaches a shorter state in median 27
  pops (max 248) on 12 rows, against 628 (max 2,720) on 8 for plain S20_MK2.
  `claude/ac19-theorem-strength-8v1wp6:research/residual_20260909/u124/README.md`.
- Nothing here proves a U124 class is not (stably) AC-trivial. The mu-ladder (Tried, below) lowers the Aut-minimal total
  length of 36 classes and reaches the stable-solve line (mu of 12 or less) on none.

## 10. The difficulty ladder

Ten levels by plain greedy node count `g` (cap 24 for MS640, 48 and 64 for AC19 rungs, each row carrying its own
budget and cap), with nested panels of 20, 40, 60, 100, 200, 300 and 500 rows drawn from AC19 Aut-minimal orbits and
MS640 rows. Subsets 60, 100 and 200 are the main testers. Every row is solved by something on record; the U124 classes
are kept off the ladder in `unsolved_124.csv`.
`claude/ac19-theorem-strength-8v1wp6:benchmark/ladder/LADDER.md` and
`claude/ac19-theorem-strength-8v1wp6:benchmark/ac19_ladder/`.

| level | rule | AC19 orbits | MS640 rows |
|---|---|---:|---:|
| 1 | g < 1,000 | 66,082 | 554 |
| 2 | 1,000 to 10,000 | 5,854 | 52 |
| 3 | 10,000 to 31,623 | 394 | 20 |
| 4 | 31,623 to 100,000 | 226 | 8 |
| 5 | 100,000 to 316,228 | 98 | 4 |
| 6 | 316,228 to 1,000,000 | 37 | 2 |
| 7 | 1,000,000 to E (E = 2,253,802) | 30 | |
| 8 | E to 10,000,000 | 30 | |
| 9 | **greedy unsolved at 10M; S20_MK2 solves it** | 19 | |
| 10 | **greedy and S20_MK2 both unsolved at 10M; only the cascades solve it** | 9 | |

- Level 9: S20_MK2 solves 6 at 10,000 nodes, 2 at 100,000, 8 at 1M, 3 at 5M. Level 10: 7 rows by the table-free cascade
  and 2 only with the cap-14 backward table.
- Levels 7 to 9 are graded by record (a 10M-pop greedy run needs about 50 GB at the source's packing; the source's
  `run_ladder.py`, not shipped, refused budgets over 1M unless `LADDER_ALLOW_BIG=1`). `run.py` takes any budget; at one
  byte per symbol `acx.search.fast` needs about twice the source's memory per state (section 3).
- 45 "originals" (the pre-Aut-min spellings of hard orbits) are kept in the pool but off every panel; their partners sit
  in levels 8 to 10.

---

## Tried, no promise

One line each. These are write-up only; no code ships for them.

- **Abel top-3 selection** (rank CoV starts by `|Sx|+|Sy|`, search the top three): MS640 at 100,000 nodes solves 640/640
  with first-solve mean 717 nodes against greedy's 4,963 at 1M (6.9x on the mean, 21x on the max), mean path 28.6 vs 36.8
  (transformed coordinates), rank 1 alone is 640/640; at 10,000 nodes bench60 reaches the oracle's 52/60 (cap confound as
  in section 5), at 1,000 nodes only 41/60, two hops 43/60. `research/w5/stable-ac-escape:results/stable_ac/cov/cov_top3/RESULTS.md`;
  `claude/abelianized-exponents-verify-1i6muh:logs/05-08-2026.md`.
- **Nonsymmetric CoV beam** (K = 4, then greedy at 1,000 nodes): bench60 49/60 against greedy 29, oracle 45, 43 of 45 Aut
  classes; K was chosen in-sample, best-first reaches the same 49, and 19 of 60 rows ran at cap above 24 (same-cap Aut-min
  control 36/60), so "best CoV-then-AC" is overstated. `cursor/heur-u124-s20mk2-a42e:results/comparison/COVBEAM_K4_B1K_ADVISOR_REVISE.md`.
- **mu-ladder** (iterated CoV hops down the Aut-minimal total length): 346.8 CPU-hours over 5,579,015 orbits; 36 of 124
  classes descend, none to mu of 12 or less; every floor was first touched by rung 9, and the closed earlier census (35/124)
  gained one descender. `cursor/cloud-agent-1785265366483-2x3ne:results/stable_ac/mu_scan/MU_SCAN_FINDINGS.md`.
- **covmeet** (CoV-only meet-in-the-middle over the 124 classes): a 25.6-hour run discovered 14,627,414 orbits (9,336,325
  expanded) with 0 merges, 124/124 remain; the store audits clean, the raw snapshot is not in git.
  `experiments/ppo:results/stable_ac/covmeet/AUDIT_2026-08-16.md`.
- **RECOMMENDED** (L + 2.53 K + 6.418 MK + 8.458 S + 3.292 xyimb): withdrawn as overfit, 14 of its 20 validation rows were in
  the tuning slice; its published margins (10/20 to 15/20, the 60-row cost tables) are in-sample.
  `claude/heuristic-search-benchmark-e1f9l8:experiments/search/HEURISTICS.md`.
- **s40_gen** (L + 40 S with Nielsen images pushed into the heap): reaches 70,649 of 72,779 at 501 nodes but 43,485 of those
  are aut-assisted and need decoding; the AC-only control certifies 64,541. Subsumed by the hybrid.
  `codex/ac-elementary-decoder:results/heuristic_search/ac19_cascade_screen/RESULTS.md`.
- **asym** (abelianisation-Gram term `wA * |<ab(r1), ab(r2)>| / T` on top of S20_MK2 or S20): the train winner
  `s20_Arawm3` (59/120 against 54/120) reads 25/60 against 23/60 on its virgin holdout (McNemar p = 0.81); no robust gain.
  `experiments/ppo:results/heuristic_search/asym_scout/ASYM.md`.
- **Depth tie-break / depth term**: adding `w * depth` beat its zero-depth incumbent in 1 of 216 arms (noise, section 2);
  the shipped order keeps depth only as the second key of `(priority, depth, key)`.
- **Fsign / spectral terms** (`fftvar`, sign-lag): no robust gain; `S20_MK2_F4` scores 27/60 on the spent holdout against
  S20_MK2's 33, and 29/60 against 27 on the fresh one. `experiments/ppo:results/heuristic_search/smk_f_grid/HOLDOUT.md`.
- **Abelian mass as a learned ranker**: abelianised magnitude of a CoV start ranks a presentation's own starts with
  within-presentation AUC 0.92 (27 mixed presentations, budget 100) but is weak on the deep residual; a Simpson's-paradox
  trap sits in the pooled correlation. `research/w5/stable-ac-escape:experiments/IDEAS.md`. [survey: Spearman +0.81 within
  presentations]
- **Backward-ball endgame table** (cap 14, 12.8M states): closes the AC19 census at 1,000 units with 7.0x fewer charged
  units, but 91% of roots are precomputed, 282 MB, 27 minutes to build (section 4).
- **Macros** (conjugate-donor, `ncrw`): the macro arms tie their plain counterparts exactly, 29/60 (length) and 37/60
  (S20_MK2) at 1,000 nodes on bench60. `new_moves:experiments/search/NEW_MOVES.md`.
- **Supermoves** (ACM, AMEC, Morse internal collapse, Lackenby dual tree): theorem-level mechanisms replayed and
  certified on single U124 classes (for example `aca_115`), not search steps; none solves a U124 class; Lackenby needs
  Regina. `results/ms640-s20-mk2-1m:results/stable_ac/theory/`. The **Whitehead portal** (`new_moves`: Whitehead-reduce the
  start, then plain substitution search) reaches 49 vs greedy's 40 on bench60 at 10,000 nodes (36 vs 29 at 1,000), a
  strict superset. Because an automorphism preserves AC-triviality its claim is AC-triviality of the original
  (`AC_TRIVIAL_IFF`), but it stores no path on the original; transport (section 6) would supply one.
  `new_moves:experiments/search/NEW_MOVES.md`.
- **Stabilisation arms**: `z = w`, trivial-generator and rank-n stabilisation add nothing (section 7); five method
  families (greedy over 388 `z = w` arms, 1,937 solves over 1,006 Lemma-11 quotients, full stable-move best-first search
  to four generators, trivial-generator stabilisation, the RL beam to width 2048) all floor AK(3) at total length 13.
  Chord refinement and generator splitting with a length-2 definition are provably inert; a length-3 SPLIT is not.
  `test/stable-ac-moves:experiments/stable_ac/ak3_stable_proof/RESULTS.md`;
  `claude/stable-ac-conjecture-stabilization-rwo9as:experiments/lessons/stabilization-that-only-rebookkeeps-is-inert.md`.
- **AK(3) theory**: AK(3) funnels into exactly two length-13 floor presentations (AK(3) itself and F, 71% of the
  attractor, joined by a certified 21-move path); the capacity BFS closes at every cap up to 16; AK(3) is open in both
  directions. About 33k lines of theory, linked not shipped. `codex/proofs`, `fable/proofs`, `cursor/u124-stable-ac-1b54`.
- **Autchoice orbit images**: on a 124-row panel of *solved* ladder rows (not U124), choosing the best of the 13
  radius-2 Aut(F2) images (an oracle) raises S20_MK2 solves at 20,000 pops from 94/124 to 119/124 (64 to 101 at 5,000);
  no single Whitehead generator helps on average. On U124 the same images within two Whitehead moves solve 0/124 at
  20,000 (section 9). `claude/ac19-theorem-strength-8v1wp6:research/autchoice_20260910/ATLAS.md`.

## Open experiments

Planned or partly built, with no result on any branch. None has code in the new branch beyond what is listed.

- **Shaped-reward PPO.** Pre-registered A/B: control (the 610 reward) against a potential term `Phi = -0.2 (L + 20 S + 2 MK)`
  with `Phi = 0` at every episode end, on `AC19_extended` minus the 54 bench60 rows (580-index pin list). Never run.
  `experiments/ppo:experiments/ppo/SHAPED_REWARD_PLAN.md`.
- **U124 under S20_MK2 at 1,000,000 nodes, cap 64, from the CoV-reduced starts** (the 36 descenders start at their orbit
  floor). Runner and four notebooks exist, no results.
  `cursor/heur-u124-s20mk2-a42e:results/heuristic_search/u124_s20mk2_1m/README.md`.
- **A tuned 10^6-node run on the 124**, named in the survey as planned and never run. [survey]
- **Hybrid at 10,000,000** over the joint-survivor list: code and survivor list only.
  `codex/ac19-hybrid-10m:experiments/search/hybrid_10m.py`.
- **A full 1,190-row beam evaluation of the 610 checkpoint** and a replication of its training; only the 530-row smoke is
  recorded.
- **Reach tier**: progress on unsolved classes scored against each row's bar (AK(3) is slot 0); baseline greedy at 1M
  reaches progress 0 on all but 25_17. `cov/all-subsets-sweep:benchmark/reach/`.
