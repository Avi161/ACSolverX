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

## Running the tester

```bash
PYTHONPATH=. python3 -m benchmark.ladder.run_ladder --panel benchmark/ac19_ladder/ladder_60.csv --engine greedy --budget 100000 --workers 4
PYTHONPATH=. python3 -m benchmark.ladder.run_ladder --panel benchmark/ac19_ladder/ladder_60.csv --engine s20_mk2 --budget 100000 --workers 4
PYTHONPATH=. python3 -m benchmark.ladder.run_ladder --panel benchmark/ac19_ladder/ladder_60.csv --engine policy --policy K3p_notable --budget 1000
```

`run_ladder.py` and `report_ladder.py` are the ladder's; the panels carry a `level`
column, so the per-level report works unchanged.
