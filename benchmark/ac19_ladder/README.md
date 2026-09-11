# The AC19 ladder

Every AC19 presentation, in both forms, graded by the plain greedy search and by
S20_MK2, sorted into the ten difficulty levels of [`../ladder/LADDER.md`](../ladder/LADDER.md),
with six nested panels that keep, per level, the rows **S20_MK2 finds hardest**.

| file | what |
|---|---|
| `pool.csv` | every row: the 72,779 aut-min orbit representatives + the 131,905 distinct dataset originals |
| `ladder_{10,20,40,60,100,200}.csv` (+ `.json`) | the panels: 1 / 2 / 4 / 6 / 10 / 20 rows per level, hardest for S20_MK2 first |
| `ungraded.csv` | originals plain greedy leaves unsolved at 1,000,000 pops (no level, off the panels) |
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
- the S20_MK2 escalation stops at 100k on this box (a 1M-pop search peaks at 11.8 GB);
  the rows it leaves unsolved there are ranked as costing "more than 100,000" until the
  1M rung below is run elsewhere. (`ungraded.csv` exists for originals greedy cannot
  solve at the last rung walked; with greedy complete it is empty.)

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

## The 1M rungs (run elsewhere)

Plain greedy finished at 100k. S20_MK2 did not: the rows it leaves unsolved at 100k are
`sources/unsolved_at_100k_s20_mk2.csv` (count in `manifest.json`), and a single 1M-pop
search peaks at **11.8 GB** and takes 4–5 minutes on this box, so that rung runs on a
bigger machine. Only `numpy`, `numba` and `PyYAML` are needed. From a clone of this
branch:

```bash
pip install numpy==2.1.3 numba==0.63.1 PyYAML==6.0.2
export PYTHONPATH=.
# W = floor((RAM_GB - 2) / 12): each 1M-pop worker holds ~12 GB
python3 -m benchmark.ladder.run_ladder --engine s20_mk2 --budget 1000000 --cap 48 --workers W --big-workers \
    --panel benchmark/ac19_ladder/sources/unsolved_at_100k_s20_mk2.csv \
    --out benchmark/ac19_ladder/sources/runs --tag orig_s20_mk2_b1000000_c48
```

The run resumes by row name if interrupted (re-run the same command). It writes
`<tag>.jsonl` (every solve replayed; `verified` per row) and `<tag>.summary.json`.
Then, back here, with that file in `sources/runs/` (`.jsonl` or `.jsonl.gz`):

```bash
PYTHONPATH=. python3 -m benchmark.ac19_ladder.build_ac19_ladder --force        # max budget 1M, the default
PYTHONPATH=. python3 -m pytest tests/test_ac19_ladder.py -q
```

which re-ranks every level by the new S20_MK2 costs (levels do not move: they are greedy
bands, and greedy is complete).

## Running the tester

```bash
PYTHONPATH=. python3 -m benchmark.ladder.run_ladder --panel benchmark/ac19_ladder/ladder_60.csv --engine greedy --budget 100000 --workers 4
PYTHONPATH=. python3 -m benchmark.ladder.run_ladder --panel benchmark/ac19_ladder/ladder_60.csv --engine s20_mk2 --budget 100000 --workers 4
PYTHONPATH=. python3 -m benchmark.ladder.run_ladder --panel benchmark/ac19_ladder/ladder_60.csv --engine policy --policy K3p_notable --budget 1000
```

`run_ladder.py` and `report_ladder.py` are the ladder's; the panels carry a `level`
column, so the per-level report works unchanged.
