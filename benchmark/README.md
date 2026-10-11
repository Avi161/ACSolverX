# `benchmark/`: the frozen evaluation sets

Fixed row lists for scoring a search technique, so two techniques are compared on the same
presentations rather than on whichever ones each happened to run. Every row is a verbatim
presentation from `data/` (or from a record that is shipped there), so a row can be checked
against its source file. Load with `acx.data`:

- `load_csv(path)`: any CSV with `r1`, `r2` columns (id = `name`, else `pres_id`, else the index).
- `load_split(path, part)`: a split JSON, `part` = `"holdout"` or `"train"`.
- `load(name)`: the flat-int datasets in `data/` (`ms640`, `ac1m`, ...).

## The difficulty ladder (`ladder/`), the headline benchmark

Ten levels of Andrews-Curtis presentations, from "solved in a few heap pops" to "only the
cascades solve it", in nested panels of 20, 40, 60, 100, 200, 300 and 500 rows, plus
S20-hard variants (`ladder_{20..300}_s20hard`) picked as the hardest for S20_MK2. Difficulty
is the node count `g` of plain length-ordered greedy on record. Every row is solved by
something on record. The main testers are `ladder_60`, `ladder_100` and `ladder_200`.

Panel sizes are capped by population (99, 188, 268 and 377 rows, not 100, 200, 300 and 500).
`ladder_200` holds 144 AC19 aut-min orbits (`data/AC19_extended_aut_min.csv`, the same names
and presentations) and 44 MS-640 rows.

| level | rule (`g` = plain greedy pops on record) | AC19 orbits (pool) | MS-640 (pool) | `ladder_200` rows |
|---:|---|---:|---:|---:|
| 1 | `g < 1,000` | 66,082 | 554 | 20 |
| 2 | `1,000 <= g < 10,000` | 5,854 | 52 | 20 |
| 3 | `10,000 <= g < 31,623` | 394 | 20 | 20 |
| 4 | `31,623 <= g < 100,000` | 226 | 8 | 20 |
| 5 | `100,000 <= g < 316,228` | 98 | 4 | 20 |
| 6 | `316,228 <= g < 1,000,000` | 37 | 2 | 20 |
| 7 | `1,000,000 <= g < 2,253,802` | 30 | 0 | 20 |
| 8 | `2,253,802 <= g <= 10,000,000` | 30 | 0 | 20 |
| 9 | plain greedy unsolved at 10M; S20_MK2 solves it | 19 | 0 | 19 |
| 10 | plain greedy and S20_MK2 unsolved at 10M; only the cascades solve it | 9 | 0 | 9 |

Caps: the levels were graded at the cap each row carries (`greedy_cap`: 24 for MS-640 rows, 48 for
AC19 rows up to 1M pops, 64 above). Run a ladder row at its own `greedy_cap` to reproduce `greedy_nodes`
pop for pop (checked on the easy rows in `tests/test_data.py`); at the default cap of 24 an AC19 row can
differ or fail (29 of the 30 AC19 rows of levels 1-3 in `ladder_200` still solve at the recorded pops).

Files, all sharing one column schema (`name, r1, r2, level, source, form, ...`, the grading
columns and `aut_class`; see `ladder/LADDER.md`):

- `ladder_{20,40,60,100,200,300,500}.csv` (+ `.json`): the spread panels.
- `ladder_{20,40,60,100,200,300}_s20hard.csv` (+ `.json`): the S20-hard panels.
- `originals_45.csv`: the 45 pre-Aut-min originals. Pool rows only, never on a panel.
- `ladder_pairs.csv`: 45 original-to-representative pairs (the originals' aut-min partners).
- `unsolved_124.csv`: the 124 Miller-Schupp classes no method has solved, in the form first found.
- `unsolved_all_forms.csv`: 1,059 rows, the same classes in four forms (see `LADDER.md`).
- `ladder_manifest.json`: pool size (73,464), level bands and hashes of the inputs.
- `LADDER.md`: the method, the grading caveats, the S20-hard tables and the checks.

Not in this checkout: `ladder_all.csv` (the full 73,464-row pool, 8.6 MB), the build and run
scripts, `runs/` and `sources/`. They are on `origin/claude/ac19-theorem-strength-8v1wp6`
under `benchmark/ladder/`.

## MS-640 (full)

`data/ms640_solved.txt`, 640 Miller-Schupp presentations. `load("ms640")` returns all of them
with `id` = line index. Every row is solved by the baseline greedy at a 10^6-node budget, so
a technique that fails one has failed a solvable problem.

## `subsets/`: the efficiency subsets (bench10, bench20, bench40, bench60)

Rows are picked across ten bins of `log10(nodes_explored)` at 1M budget (each bin costs
3.37x the one below, from 3 nodes to about 575,000). Each subset takes an equal number per bin,
and within a bin picks first minimise `Aut(F2)`-equivalent pairs. Subset-60 spans 45 distinct
classes of the 640's 113. The subsets are not nested. The 20 ids in
`tests/test_greedy_heuristic.py` are `benchmark_subset_20.json` in file order.

| file | what |
|---|---|
| `benchmark_subset_{10,20,40,60}.{csv,json}` | the row lists: presentation, bin, `Aut(F2)` class, baseline cost |
| `benchmark_subset_{10,20,40,60}_arms.{csv,json}` | what each technique costs on those rows, see [`ARMS.md`](subsets/ARMS.md) |
| `subset_coverage.png` | where each rung's picks land across the ten bins |

## AC1M hard, Aut-disjoint split (`splits/`)

`splits/splits_ac1m_hard_aut.json`: AC1M presentations selected for length-hardness and
deduplicated by `Aut(F2)` class, split 2:1 into 120 train and 60 holdout rows (stratified by
length, zero Aut overlap). `idx` is the AC1M line index. Train was used to pick a method and the
holdout was read once, after the choice was frozen. Load with
`load_split("benchmark/splits/splits_ac1m_hard_aut.json", "holdout")`. The holdout rows are checked
to equal their AC1M lines in `tests/test_data.py`.

## MS-640 difficulty bins (`difficulty_bins.csv`)

All 640 MS-640 rows with the bin each falls in (`pres_id` = MS-640 line), the difficulty rank,
the baseline's nodes and path length at 1M, the `Aut(F2)` class and minimal total, and progress at
50k nodes. It is the table the subsets were picked from.

## Related data (in `data/`, not benchmarks)

- `AC19_extended_aut_min.csv` (72,779 aut-min orbits of `AC19_extended`) and
  `AC1M_aut_min.csv.gz` (71,283 orbits of AC1M, gzip). The ladder's `ac19_N` rows are the first
  table's rows; the second is read with `gzip` (`load_csv` does not open `.gz` yet).
- `ms_unsolved_reps/aca_124_{initial,reduced,best}.csv` and `README_aca_124.md`: the 124 unsolved
  classes before and after the mu-ladder reduction. `aca_124_best` is the one to use.
- `equivalence_classes/certificates.json`: the equivalence pipeline's certificates for the 124
  classes (261 presentations, 137 edges: 93 change-of-variables edges, 44 AC edges of which 6 are pure
  AC paths).
