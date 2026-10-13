# Using `run.py` and `compare.py`

`python run.py --config <file.toml> [options]` runs one method on a set of presentations and writes one folder per run,
`results/<name>/`: a record per presentation (`paths.jsonl`), a summary (`summary.json`) and the config
(`config.json`). `python compare.py` puts finished runs side by side. What each method does is in
[METHODS.md](METHODS.md); the relator cap and its counters in [CAP.md](CAP.md).

## Run

```bash
python run.py --config configs/greedy_fast.toml                                  # the config's benchmark (MS640)
python run.py --config configs/s20_mk2_fast.toml --set benchmark=bench60 --rows 0:10
python run.py --config configs/hybrid.toml --input examples/presentations.csv      # your own file
python run.py --config configs/hybrid.toml --pres "xxYYY, xyxYXY" --pres "YYXyx, Yx"
```

| flag | what it does |
|---|---|
| `--config FILE` | the run's config (required): one per method in `configs/`, every key in `configs/template.toml` |
| `--set KEY=VALUE` | override a config value, repeatable; a dotted key reaches a section (`--set search.cap=none`); the value is read as TOML, else as a plain string |
| `--input PATH` | run every presentation of your own file (formats below) instead of the config's `benchmark` and `rows` |
| `--pres "R1, R2"` | run a presentation typed here, repeatable; it is saved as `<out>/<name>/input.txt`, and after the run one line per presentation is printed (id, solved, kind, cost, sub_moves, elem_moves) |
| `--rows SPEC` | only some rows: a slice `a:b` (or `a:b:c`, integers only) of the row list, else ids `3, 17` (an id may hold a colon, `ms:1`) |
| `--solved-from RUN_DIR` | only the rows that `RUN_DIR/paths.jsonl` marks solved, in its order (not with `--rows`); see "Decode later" |
| `--out DIR` | the results root (default `results`) |
| `--fresh` | delete this run name's earlier results first |

## Presentations in

**Shipped sets**, by name (`--set benchmark=<name>`; [benchmark/README.md](../benchmark/README.md) says what each is):

| names | row id |
|---|---|
| `ms640`, `1190ms`, `ms_unsolved`, `ac19`, `ac19_extended`, `ac1m` (the datasets in `data/`) | the line number, from 0 |
| `bench10`, `bench20`, `bench40`, `bench60` | the `pres_id` column (the MS640 line) |
| `ladder20` .. `ladder500`, `ladder20_s20hard` .. `ladder300_s20hard`, `ac19_autmin`, `ac1m_autmin`, `u124` | the `name` column |
| `ac1m_hard_holdout60` | `idx` (the AC1M line) |

`python -c "import acx.data as d; print(*d.DATASETS, *d.BENCHMARKS, *d.SPLITS)"` lists them, and so does the error
for an unknown name.

**Your own file** (`--input PATH` or `benchmark = "PATH"`), UTF-8 text, optionally gzipped (`.txt.gz`, ...). Generators
are the 26 letters in the order `x y z a b c ... w`; upper case is the inverse; past the 26th they are
`g27`, `g28`, ... (`G27` the inverse), as in `g27x, G27g28`. The samples
`examples/presentations.{txt,csv,jsonl}` hold the same eight presentations in each format.

| format | one presentation | row id |
|---|---|---|
| `.txt` | a line of relators separated by commas or spaces, `xxYYY, xyxYXY`; `#` starts a comment, blank lines are skipped. A line of integers (`x = 1`, `y = 2`, negative = inverse, the two relators zero-padded to equal halves) is the layout of `data/*.txt` and also loads | its position among the presentations, from 0 |
| `.csv` | a header with relator columns `r1, r2, ... rN` (empty cells are skipped) | the `id` column, else `name`, else `pres_id`, else the position |
| `.jsonl` | `{"id": "ak2", "relators": ["xxYYY", "xyxYXY"]}` per line | `id`, else the position |

Any number of generators and relators loads; which presentations a method can take is up to the method (below).
Other CSV columns and JSON keys are kept as the row's `meta`. A bad line stops the run with `<file>:<line>: <what is
wrong>`, and a repeated id is an error. A file that is not UTF-8 text stops it with `<file>: not UTF-8 text ...`,
and a `.gz` file that is not whole gzip with `<file>: not a whole gzip file ...`.

What the methods take: `greedy` with the `length` priority and `ngen` take any number of generators; `s20_mk2`, `aut`,
`cov`, `hybrid` and `rl` take two generators and two relators (`rl` also at most 24 letters each). A row a method
cannot take, or with `|det| != 1` (never AC-trivial), is written as unsolved with an `error`, and the run goes on.

## Run names, resume and `--fresh`

A run writes `<out>/<name>/`. The name is the config's `name` key, else the config file's stem (`greedy_fast`). With
`--input` or `--pres` and no `--set name=...`, it is `<config name>_<file stem>` or `<config name>_pres`:
`configs/hybrid.toml --input examples/presentations.csv` writes `results/hybrid_presentations/`.

- **Resume.** Rows already in `paths.jsonl` are skipped, so an interrupted run continues where it stopped, and running
  again with other `--rows` adds those rows to the same folder. A record counts only for the presentation in its `pres`:
  if a line of your file changed (or two lines swapped), that row is solved again and its old record dropped; records
  written before `pres` existed count as done. `summary.json` is rewritten each time and covers every record in the
  folder. A row recorded with an `error` is not retried. A cut-off last line of `paths.jsonl` (an interrupted write)
  is dropped; a bad line before others stops the run with `<file>:<line>: not a record ...`.
- **Another config under the same name is refused** (`holds a run with another config: pass --fresh or another
  name`): `config.json` must match, `rows` and `workers` aside. `--pres` with other presentations is refused the same
  way.
- **`--fresh`** deletes that name's `paths.jsonl`, `config.json` and `summary.json` before the run. The folders shipped
  in `results/` hold the published numbers: never `--fresh` them. Pick a new name (`--set name=mine`) or another
  `--out`. A run of fewer rows into such a folder (a `summary.json` and no `paths.jsonl`) is refused, as it would
  replace the published summary; a rerun of all its rows reproduces it.

## The config

A TOML file: top-level keys, then one section per part of the method. [`configs/template.toml`](../configs/template.toml)
lists every key with its default and a comment. An unknown key, a section the method does not read or an invalid
value is an error before anything is written.

| top-level key | default | meaning |
|---|---|---|
| `name` | the file's stem | the run folder |
| `method` | required | `greedy`, `aut`, `cov`, `hybrid`, `ngen`, `rl` or `rankn` |
| `benchmark` | required | a shipped name or a file path |
| `rows` | every row | as `--rows` |
| `workers` | 1 | processes (an int >= 1); rows are solved in parallel |
| `decode` | true | count each S-move path in elementary moves too (`elem_moves`); the hybrid and aut give it either way, as their certificates are elementary moves |
| `path` | true | keep and replay each path; false is faster (below) |
| `fields` | every key | write only these record keys (below) |

- `[search]` (greedy, aut, cov, ngen, rankn): the best-first search: `priority` (`length` or `s20_mk2`), `cap` (24,
  or `"none"`), `budget` (pops, 10,000), `backend` (`fast`, numba, by default in a run; `spec` is the pure-Python
  reference, the same steps 27x slower, which only `baseline_spec.toml` sets), `cyclic`.
- `[cov]`: the change of variables: pops per row over all its searches, and which images are searched.
- `[ngen]`: `sac`, the transform to relators of length at most 3 before the search.
- `[hybrid]`: `budget` in work units, the three limits `r2_cap`, `dyn_cap`, `slack` (each an int or `"none"`;
  `r2_cap` also `"parent"`), the queue knobs and `backend` (`fast` by default).
- `[rl]`: the beam's `width`, `steps`, `alpha` and `cap`.
- `[rankn]`: the stabilising words of the rank-n sweep ([RANK3.md](RANK3.md)).

## What a run writes

`config.json` is the config the records were made with. `paths.jsonl` has one record per row:

| field | meaning |
|---|---|
| `id`, `pres`, `solved` | the row, its presentation as a LETTERS line (`xxYYY, xyxYXY`; resume compares it), and whether it was solved |
| `kind` | `ac_path` (AC moves on the row) or `stable_cert` (stable AC: AC4/AC5 moves or a change of variables); null if unsolved |
| `aut_assisted` | an `ac_path` found in another basis and carried back to the row |
| `cost` | what the row spent, solved or not: heap pops, hybrid work units or network evaluations (rl) |
| `sub_moves` | substitution moves (S-moves) of the path |
| `elem_moves` | elementary AC moves of the path on the row: null without `path`, for a CoV `stable_cert`, and without `decode` except for the hybrid and aut (their certificates are elementary moves) |
| `path` | the S-moves, `[i, j, s, k1, k2]` each (`acx.core.moves.decode_path`) |
| `elementary` | the elementary moves, packed (`acx.verify.decode.unpack`); aut-assisted, hybrid, n-generator and CoV paths |
| `verified` | the path was replayed on the row before the record was written (once: by the search, CoV, the hybrid's `certify` or rl, or by the runner for aut and ngen) |
| `error` | only on a row that was not searched or whose method failed: `Type: message` |
| `seconds`, `cpu_seconds` | the row's wall and CPU time, replay and decoding included |
| `cap`, `cap_dropped`, `cap_dropped_min_total`, `cap_would_pop`, `cap_first_bind`, `cap_needed` | the cap counters ([CAP.md](CAP.md)); the hybrid adds them under `dyn_cap_` and `slack_`, CoV adds `cap_legs_bound` |
| method extras | `rep` (aut: the Aut-minimal form searched), `image` (cov: the image that solved), `steps` (cov `stable_cert`, hybrid: the certificate steps), `stage` (hybrid: `terminal`, `B`, `C` or `H`), `rank` (ngen: generators searched), `skipped` (rl: why a row was not searched) |

`summary.json`:

| key | meaning |
|---|---|
| `name`, `method`, `benchmark`, `config` | what ran (`config` without `rows` and `workers`) |
| `rows`, `solved`, `errors`, `skipped` | counts over the records |
| `ac_path`, `aut_assisted`, `stable_cert` | solves by kind (`ac_path` counts the plain ones) |
| `cost` | `unit`, `total` over all rows, `on_solved` |
| `cost_unit`, `cost_mean`, `cost_median` | `pops`, `units` or `evaluations`, and the mean and median per row over all rows |
| `path_length` | per kind, `sub_moves` and `elem_moves`: `n`, `sum`, `mean`, `median`, `max` |
| `caps` | the cap counters over the rows, one block per limit ([CAP.md](CAP.md)) |
| `wall_seconds`, `row_seconds`, `cpu_seconds` | this invocation's wall time; the rows' summed wall and CPU time (null when `fields` leaves out `cpu_seconds`) |
| `us_per_cost` | CPU microseconds per pop, unit or evaluation: `cpu_seconds` over the total cost (null without `cpu_seconds`) |

The rank-n sweep (`rankn`) writes per-row `rows/<id>.npz` files and its own summary instead ([RANK3.md](RANK3.md)).

## Faster runs

- **`path = false`** (`--set path=false`): the searches keep no parent links, and the hybrid writes out no
  elementary path, so nothing is decoded, replayed or stored. CoV is the exception: it still captures and checks the
  paths of its searches, and only the record leaves them out. Records keep `solved`, `kind`, `cost`, `sub_moves` and
  the cap counters; `path` and `elementary` are null, `verified` is false, so a solve is not checked, and
  `elem_moves` is null (but for a CoV path carried back from an image). Rerun with `path = true` to get and check
  the paths, or decode later (below).
- **Decode later.** `--solved-from RUN_DIR` runs only the rows that run solved. After a `path = false` run, the same
  config with `path = true` recomputes just those rows, and the searches are deterministic, so it finds the same
  solves at the same cost, now decoded and replayed (`verified: true`):

  ```bash
  python run.py --config configs/hybrid.toml --set path=false --set name=ms640_fast
  python run.py --config configs/hybrid.toml --set path=true --solved-from results/ms640_fast --set name=ms640_fast_paths
  ```

  Give the same benchmark (or `--input`/`--pres`) and another name, as the config differs. A folder without
  `paths.jsonl` (the shipped `results/`) or with no solved row stops the command with one line.
- **`fields = ["solved", "cost", "sub_moves"]`** keeps the records small; `id`, `pres`, `solved` and `error` are
  always written. `summary.json` reads the records as written, so a dropped key leaves its entries empty (without
  `kind`, every kind counts 0; without `cpu_seconds`, `cpu_seconds` and `us_per_cost` are null).
- **`workers = 4`** solves rows in four processes. Keep `NUMBA_NUM_THREADS=1`.
- Before its rows, a run (each worker) solves AK(2) once, unrecorded, so that compiling the numba kernels and
  loading the rl policy are not timed in the first row. Time a method over many pops: on a few tiny rows fixed costs
  still dominate `us_per_cost`.
- **`cap = "none"`** pushes every child, whatever its relator length: nothing is dropped and nothing is counted, but
  the search graph is larger, so each pop costs more and memory grows. How much slower it is, per benchmark, is in
  [PERFORMANCE.md](PERFORMANCE.md) (the uncapped-cost section); when the cap matters at all is in [CAP.md](CAP.md).

## Compare runs

```bash
python run.py --config configs/greedy_fast.toml --input examples/presentations.csv     # results/greedy_fast_presentations
python run.py --config configs/hybrid.toml --input examples/presentations.csv          # results/hybrid_presentations
python compare.py results/greedy_fast_presentations results/hybrid_presentations
python compare.py results/greedy_fast_presentations results/hybrid_presentations --common --html compare.html
```

One markdown table, a row per run: rows, solved (%), mean and median cost of the solved rows in the run's unit, mean
`sub_moves` and `elem_moves` (`n=k` when only k solved rows have one), CPU seconds per row, CPU µs per pop/unit
(`us_per_cost`: CPU of all rows, verification included, over their total cost), raise-cap rows (a cap dropped a state
the search would have popped) and errors. Two runs of one benchmark also get a head-to-head line (solved by only one,
by both, by neither).

- **Units.** greedy, aut, cov and ngen count heap pops; the hybrid counts work units (pops of its two queues plus the
  automorphisms, Nielsen images and S-moves of its cascade and gates); rl counts network evaluations. A unit is not a
  pop: compare cost and µs per pop/unit only between runs counted in the same unit, and compare solve rates across all.
- **`--common`** averages cost, moves and CPU over the rows every run solved (runs of one benchmark), so a method is
  not made to look cheap by solving only easy rows.
- **`--html FILE`** also writes one self-contained page: the table and three bar charts (solve rate, mean cost per
  solved row on a log scale, CPU µs per pop/unit), with a panel per unit.
- Values marked `*` are wall-clock seconds, from runs that predate `cpu_seconds`.
- compare.py reads `paths.jsonl`, which only runs made on your machine have. The folders shipped in `results/` keep
  `summary.json` and `config.json`: their row comes from the summary, with `-` for the median and the CPU columns,
  and they take no part in `--common` or the head-to-head line (rerun a config for those; [RESULTS.md](RESULTS.md)
  section 0 has each command).

## From Python

```python
from acx import replay, search
from acx.data import parse_presentation, rows

p = parse_presentation("xxYXY, xyyXY")
res = search(p, backend="fast", budget=1000)      # any SearchConfig field; cap=None is uncapped
res.solved, res.pops, res.path_length             # (True, 7, 5)
replay(p, res.path)                               # raises ReplayError unless the path reaches <x, y | x, y>
res.stats["cap_would_pop"]                        # 0: the cap (24) did not change this search
rows("bench60")[0]                                # Row(id, pres, meta)
```

To check a finished run again, replay its records ([METHODS.md](METHODS.md) section 14).
