# The AC19 ladder

Every AC19 presentation, in both forms, graded by the plain greedy search and by
S20_MK2, sorted into the ten difficulty levels of [`../ladder/LADDER.md`](../ladder/LADDER.md),
with six nested panels that keep, per level, the rows **S20_MK2 finds hardest**.

| file | what |
|---|---|
| `pool.csv` | every row: the 72,779 aut-min orbit representatives + the 131,905 distinct dataset originals |
| `ladder_{10,20,40,60,100,200}.csv` (+ `.json`) | the panels: 1 / 2 / 4 / 6 / 10 / 20 rows per level, hardest for S20_MK2 first |
| `ungraded.csv` | originals plain greedy left unsolved at the last rung — **empty**: greedy solved all of them |
| `sources/originals_panel.csv` | the run panel: which lines of `data/AC19_extended.txt` are the 131,905 originals |
| `sources/runs/orig_<engine>_b<budget>_c48.jsonl.gz` (+ `.summary.json`) | the grading runs, one file per escalation rung, paths stripped |
| `manifest.json` | populations, level rules, `E`, hashes of every input |

Built by [`build_ac19_ladder.py`](build_ac19_ladder.py); the run panel by
[`originals_panel.py`](originals_panel.py). Tests: `tests/test_ac19_ladder.py`.

## The pool

`data/AC19_extended.txt` has 156,762 presentations. Aut-minimising them gives the 72,779
orbit representatives of `data/AC19_extended_aut_min.csv` (`ac19_N`), graded on record by
the greedy escalation 10k → 100k → 1M → 5M → 10M and by S20_MK2 the same way; their
grades, levels and `solved_by` are copied verbatim from `../ladder/ladder_all.csv`.

The originals are canonicalised (`words.canon_pair`, the form every search starts from)
and deduplicated: 9 lines repeat another line, and **24,848 lines are already their own
representative** (the same canonical pair as an `ac19_N` row), so they are not rows twice.
The remaining **131,905** are `ac19x_<line>` and were graded here:

- plain greedy, then S20_MK2, each escalated **1k → 10k → 100k pops, cap 48**, only the
  rows the previous rung left unsolved going up (`run_ladder.py --panel …`, 4 workers).
  Plain greedy needs no more: **119,990 solved at 1k, 9,997 at 10k, 1,918 at 100k —
  all 131,905**, so every original has an exact greedy grade and none is above level 4;
- every solve replayed independently (`words.replay_move` over the recorded moves); the
  shipped run files keep `nodes`, `path_length`, `verified` and drop the move lists;
- S20_MK2 needs no more either: **124,398 at 1k, 7,184 at 10k, 323 at 100k — all
  131,905**, the most expensive original costing it 34,228 pops. So both engines grade
  every original exactly, and nothing was escalated to 1M (`ungraded.csv` is empty; the
  1M rung, 11.8 GB and 4–5 min per row on this box, was never needed).

`pool.csv` columns: `name, r1, r2, level, form (autmin | original), orbit,
greedy_solved, greedy_nodes, greedy_budget, greedy_run, greedy_path_length,
s20_solved, s20_nodes, s20_budget, s20_run, s20_path_length, start_len, solved_by`.
`*_run` is the rung that graded the row (`1k`, `10k`, …, `unsolved@1M`, `unsolved@10M`);
`*_budget` the pops that rung had, so an unsolved row's cost reads as "more than
`*_budget`".

## Levels and panels

Levels are bands of the plain greedy node count `g` (levels 1–8), then the greedy
residue split by whether S20_MK2 solves it (9) or only the cascades do (10); the 7 / 8
edge `E = 2,253,802` is the ladder's. Originals only reach levels 1–6 (graded to 1M).

Inside a level the rows are ranked **hardest for S20_MK2 first**: largest `s20_nodes`,
a row S20_MK2 never solved counting as its censoring budget + 1 (10,000,001 for the
aut-min rows unsolved at 10M, 1,000,001 for originals unsolved at 1M), ties by greedy
pops (largest first), then name. Panel `ladder_{10k}` takes the first `k` of that list
per level and stores them in that order, so each level of a panel reads top-down from
the row S20_MK2 found most expensive. Rows solved at the root pop are never picked.
Nested by construction: `ladder_10 ⊂ ladder_20 ⊂ … ⊂ ladder_200`. A level shorter than
`k` gives what it has (`per_level_actual` in the JSON).

## Populations and panels

| level | rule (`g` = plain greedy pops) | aut-min | originals | in `ladder_60` (6 / level) |
|---|---|---:|---:|---|
| 1 | `g < 1,000` | 66,082 | 119,985 | S20_MK2 7,550–7,674 pops on rows greedy does in ~390 |
| 2 | `1,000 ≤ g < 10,000` | 5,854 | 10,002 | 15,780–15,791 |
| 3 | `10,000 ≤ g < 31,623` | 394 | 1,440 | 32,919–33,834, five of the six are originals |
| 4 | `31,623 ≤ g < 100,000` | 226 | 478 | 34,221–38,131 |
| 5 | `100,000 ≤ g < 316,228` | 98 | | 53,670–89,261 |
| 6 | `316,228 ≤ g < 1,000,000` | 37 | | 20,234–95,944 |
| 7 | `1,000,000 ≤ g < E` | 30 | | 156,376–1,383,279 |
| 8 | `E ≤ g ≤ 10,000,000` | 30 | | 161,384–323,525 |
| 9 | greedy unsolved at 10M; S20_MK2 solves it | 19 | | 770,382–1,299,594 |
| 10 | both unsolved at 10M; only the cascades solve it | 9 | | S20_MK2 unsolved (10,000,001) |

The originals stop at level 4 — the dataset forms are easy for plain greedy (max 90,644
pops), which is the `ORIGINALS_AT_10M` finding at full scale: only the aut-min forms
reach levels 5–10. Panel sizes: `ladder_10/20/40/60` exact, `ladder_100` has 99 rows
(level 10 holds 9), `ladder_200` has 188 (levels 9 / 10 hold 19 / 9). In `ladder_200` the
originals are 10 / 6 / 14 / 2 of the 20 picks at levels 1–4. Levels 1–2's picks are the
rows where the S20 ordering is *worse* than plain length order (7.6k S20 pops against
~390 greedy), exactly as in the old ladder's S20-hard family; level 10 is the nine rows
nothing but the cascades solve.

## Per-level statistics of the main panels

Rows per level, the plain-greedy `nodes_explored` range and mean, and the S20_MK2 range and mean, for the three panels most runs will use. Levels 9–10 are greedy-unsolved at 10M and level 10 is S20_MK2-unsolved too, so those entries are censored (`>10M`). Generated from the panel CSVs.

### `ladder_60` — 60 rows, 6 per level

| level | n | aut-min / originals | greedy min | greedy max | greedy mean | S20_MK2 min | S20_MK2 max | S20_MK2 mean |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | 6 | 5 / 1 | 389 | 435 | 414 | 7,550 | 7,674 | 7,595 |
| 2 | 6 | 3 / 3 | 1,064 | 1,317 | 1,187 | 15,780 | 15,791 | 15,784 |
| 3 | 6 | 1 / 5 | 12,879 | 18,341 | 15,557 | 32,919 | 33,834 | 33,507 |
| 4 | 6 | 4 / 2 | 59,549 | 78,774 | 65,993 | 34,221 | 38,131 | 36,816 |
| 5 | 6 | 6 / 0 | 175,765 | 238,691 | 212,255 | 53,670 | 89,261 | 74,219 |
| 6 | 6 | 6 / 0 | 363,426 | 654,496 | 549,030 | 20,234 | 95,944 | 60,348 |
| 7 | 6 | 6 / 0 | 1,077,421 | 2,184,020 | 1,720,910 | 156,376 | 1,383,279 | 583,316 |
| 8 | 6 | 6 / 0 | 2,274,604 | 5,309,101 | 3,826,988 | 161,384 | 323,525 | 195,853 |
| 9 | 6 | 6 / 0 | >10M | >10M | >10M | 770,382 | 1,299,594 | 1,045,835 |
| 10 | 6 | 6 / 0 | >10M | >10M | >10M | >10M | >10M | >10M |

### `ladder_100` — 99 rows, 10 per level

| level | n | aut-min / originals | greedy min | greedy max | greedy mean | S20_MK2 min | S20_MK2 max | S20_MK2 mean |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | 10 | 8 / 2 | 345 | 435 | 401 | 7,546 | 7,674 | 7,576 |
| 2 | 10 | 6 / 4 | 1,064 | 3,515 | 2,118 | 14,373 | 15,791 | 15,220 |
| 3 | 10 | 2 / 8 | 10,554 | 18,341 | 14,113 | 32,914 | 33,834 | 33,271 |
| 4 | 10 | 8 / 2 | 54,456 | 78,774 | 61,383 | 33,976 | 38,131 | 35,680 |
| 5 | 10 | 10 / 0 | 132,155 | 291,932 | 200,451 | 48,090 | 89,261 | 65,397 |
| 6 | 10 | 10 / 0 | 363,426 | 654,496 | 516,376 | 6,132 | 95,944 | 41,564 |
| 7 | 10 | 10 / 0 | 1,077,421 | 2,184,020 | 1,715,288 | 30,933 | 1,383,279 | 383,348 |
| 8 | 10 | 10 / 0 | 2,274,604 | 5,309,101 | 3,811,698 | 149,792 | 323,525 | 178,895 |
| 9 | 10 | 10 / 0 | >10M | >10M | >10M | 229,165 | 1,299,594 | 772,074 |
| 10 | 9 | 9 / 0 | >10M | >10M | >10M | >10M | >10M | >10M |

### `ladder_200` — 188 rows, 20 per level

| level | n | aut-min / originals | greedy min | greedy max | greedy mean | S20_MK2 min | S20_MK2 max | S20_MK2 mean |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | 20 | 10 / 10 | 337 | 436 | 393 | 7,407 | 7,674 | 7,523 |
| 2 | 20 | 14 / 6 | 1,064 | 3,515 | 2,681 | 10,315 | 15,791 | 13,983 |
| 3 | 20 | 6 / 14 | 10,554 | 18,341 | 13,214 | 32,913 | 33,834 | 33,092 |
| 4 | 20 | 18 / 2 | 39,441 | 78,774 | 51,914 | 33,238 | 38,131 | 34,533 |
| 5 | 20 | 20 / 0 | 104,005 | 291,932 | 203,658 | 10,880 | 89,261 | 40,225 |
| 6 | 20 | 20 / 0 | 363,426 | 948,266 | 631,896 | 3,192 | 95,944 | 23,135 |
| 7 | 20 | 20 / 0 | 1,077,421 | 2,207,081 | 1,788,683 | 7,353 | 1,383,279 | 202,113 |
| 8 | 20 | 20 / 0 | 2,274,604 | 8,204,360 | 3,925,308 | 16,681 | 323,525 | 119,954 |
| 9 | 19 | 19 / 0 | >10M | >10M | >10M | 4,944 | 1,299,594 | 422,461 |
| 10 | 9 | 9 / 0 | >10M | >10M | >10M | >10M | >10M | >10M |

Reading across the sizes: levels 1–2's picks are rows where S20_MK2 is ~20× *worse* than plain greedy (7.6k pops against ~400) — the ordering's bad starts; level 3's S20 cost barely moves with panel size (33.8k → 32.9k) because the pool has 1,834 rows there; levels 5–9 run out of hard rows quickly (37–98 rows in the whole pool), so their cheapest picks fall from tens of thousands of S20 pops at 60 rows to a few thousand at 188.

## Running the tester

```bash
PYTHONPATH=. python3 -m benchmark.ladder.run_ladder --panel benchmark/ac19_ladder/ladder_60.csv --engine greedy --budget 100000 --workers 4
PYTHONPATH=. python3 -m benchmark.ladder.run_ladder --panel benchmark/ac19_ladder/ladder_60.csv --engine s20_mk2 --budget 100000 --workers 4
PYTHONPATH=. python3 -m benchmark.ladder.run_ladder --panel benchmark/ac19_ladder/ladder_60.csv --engine policy --policy K3p_notable --budget 1000
```

`run_ladder.py` and `report_ladder.py` are the ladder's; the panels carry a `level`
column, so the per-level report works unchanged.
