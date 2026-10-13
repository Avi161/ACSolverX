# `benchmark/`: the frozen evaluation sets

**TL;DR.** Fixed row lists so two techniques are scored on the same presentations. Every row is a verbatim
presentation from `data/` and can be checked against it. The headline benchmark is the **difficulty ladder** (ten
levels, from a few pops to "only the cascades solve it"; main testers `ladder60`, `ladder100`, `ladder200`); the
**bench10 to bench60** subsets span MS640's difficulty bins; **`ac1m_hard_holdout60`** is a holdout read once. Results
are not kept here ([docs/RESULTS.md](../docs/RESULTS.md)).

Run one by name, `python run.py --config configs/<method>.toml --set benchmark=<name>`, or load it with
`acx.data.rows(name)`: `ms640`, `1190ms`, `bench10`..`bench60`, `ladder20`..`ladder500`,
`ladder20_s20hard`..`ladder300_s20hard`, `ac1m_hard_holdout60`, `ac19_autmin`, `ac1m_autmin`, `u124`
([docs/USAGE.md](../docs/USAGE.md) lists their row ids). `u124` is `data/ms_unsolved_reps/aca_124_initial.csv`, the
same rows as `ladder/unsolved_124.csv`. Tables without relator columns (`ladder_pairs.csv`, ...) are reference data.

## The difficulty ladder (`ladder/`)

Difficulty is the node count `g` of plain length-ordered greedy **on record**; every row is solved by something on
record. Panels of 20, 40, 60, 100, 200, 300 and 500 rows are nested, capped by population at 99, 188, 268 and 377
(not 100, 200, 300, 500); the S20-hard variants (`ladder_{20..300}_s20hard`) keep the rows S20_MK2 finds hardest.
`ladder_200` holds 144 AC19 Aut-min orbits (`data/AC19_extended_aut_min.csv`, same names and presentations) and 44
MS640 rows. Full method: [`ladder/LADDER.md`](ladder/LADDER.md).

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

**Caps.** Levels were graded at each row's own `greedy_cap`: 24 for MS-640, 48 for AC19 up to 1M pops, 64 above. At
that cap a row reproduces its `greedy_nodes` pop for pop (checked on the easy rows in `tests/test_data.py`); at the
default cap 24 an AC19 row can differ or fail (29 of the 30 AC19 rows of levels 1-3 in `ladder_200` still solve at the
recorded pops).

| file | what |
|---|---|
| `ladder_{20,40,60,100,200,300,500}.csv` (+ `.json`) | the spread panels |
| `ladder_{20,40,60,100,200,300}_s20hard.csv` (+ `.json`) | the S20-hard panels |
| `originals_45.csv` | the 45 pre-Aut-min originals: pool rows, never on a panel |
| `ladder_pairs.csv` | 45 original-to-representative pairs |
| `unsolved_124.csv` | the 124 Miller-Schupp classes no method has solved, in the form first found |
| `unsolved_all_forms.csv` | 1,059 rows: the same classes in four forms |
| `ladder_manifest.json` | pool size (73,464), level bands, hashes of the inputs |

All CSVs share one schema (`name, r1, r2, level, source, form, ...`, the grading columns, `aut_class`). Not in this
checkout: `ladder_all.csv` (the 73,464-row pool, 8.6 MB), the build and run scripts, `runs/` and `sources/`, which
stay on the ladder's source branch ([docs/PROVENANCE.md](../docs/PROVENANCE.md)).

## MS640 (full)

`data/ms640_solved.txt`, 640 Miller-Schupp presentations, `id` = line index. The baseline greedy solves every row at
10^6 pops, so a technique that fails one has failed a solvable problem.

## `subsets/`: bench10, bench20, bench40, bench60

Rows are picked across ten bins of `log10(nodes_explored)` at a 1M-pop budget (each bin 3.37x the one below, from 3
nodes to about 575,000): an equal number per bin, preferring Aut(F2)-distinct rows within a bin. Subset 60 spans 45 of
the 640's 113 classes. The subsets are not nested.

| file | what |
|---|---|
| `benchmark_subset_{10,20,40,60}.{csv,json}` | the rows: presentation, bin, Aut(F2) class, baseline cost |
| `benchmark_subset_{10,20,40,60}_arms.{csv,json}` | what each technique costs on those rows ([`ARMS.md`](subsets/ARMS.md)) |
| `subset_coverage.png` | where each subset's picks land across the ten bins |

## AC1M hard, Aut-disjoint split (`splits/`)

`splits/splits_ac1m_hard_aut.json`: length-hard AC1M presentations, deduplicated by Aut(F2) class, split 2:1 into 120
train and 60 holdout rows (stratified by length, zero Aut overlap; `idx` = AC1M line). Train picked a method; the
holdout was read once, after the choice was frozen. Load with
`load_split("benchmark/splits/splits_ac1m_hard_aut.json", "holdout")`; `tests/test_data.py` checks the holdout rows
against their AC1M lines.

## `difficulty_bins.csv`

All 640 MS640 rows (`pres_id` = line) with their bin, difficulty rank, the baseline's nodes and path length at 1M, the
Aut(F2) class and minimal total, and progress at 50k nodes: the table the subsets were picked from.

## `speed.py`: the CI speed check

Times every config on a slice of its benchmark, with and without paths, on `main` and on a change, fails when one is
more than 2% slower, and comments on the pull request how much faster or slower each one is
([docs/PERFORMANCE.md](../docs/PERFORMANCE.md#speed-check-in-ci)).

## Related data (`data/`, not benchmarks)

- `AC19_extended_aut_min.csv` (72,779 Aut-min orbits of `AC19_extended`; the ladder's `ac19_N` rows) and
  `AC1M_aut_min.csv.gz` (71,283 orbits of AC1M): `rows("ac19_autmin")`, `rows("ac1m_autmin")`.
- `ms_unsolved_reps/aca_124_{initial,reduced,best}.csv` and `README_aca_124.md`: the 124 unsolved classes before and
  after the mu-ladder reduction; use `aca_124_best`.
- `equivalence_classes/certificates.json`: the certificates joining the 124 classes (261 presentations, 137 edges: 93
  change-of-variables edges, 44 AC edges of which 6 are pure AC paths); `acx.aut.equivalence.check` re-checks every
  edge (moves, automorphisms, meeting points).
