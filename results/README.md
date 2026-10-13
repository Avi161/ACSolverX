# results/

**TL;DR.** Two kinds of folder. **Runs** (`results/<run>/`) are what `run.py` writes; git tracks their small
`summary.json` and `config.json`, the numbers quoted in [README.md](../README.md) and
[docs/RESULTS.md](../docs/RESULTS.md), and the paths regenerate with the command in RESULTS.md section 0.
**Studies** (`results/stable_ac/<study>/`) are sweeps made on other branches, carried as compact files with a
`MANIFEST.json` of the raw files not in git.

## Runs

`python run.py --config configs/<file>.toml --set name=<run> [--set ...]` writes `results/<run>/`:

- `paths.jsonl`: one record a row (`id`, `solved`, `kind`, `aut_assisted`, `cost`, `sub_moves`, `elem_moves`, the
  certificate, the cap counters, `seconds`), written only after the certificate replays. Gitignored; a rerun skips rows
  already in it, `--fresh` starts over.
- `summary.json`: solves by kind (`ac_path` / `aut_assisted` / `stable_cert`), cost, wall time, path lengths per kind
  in S-moves and elementary moves, the `caps` block.
- `config.json`: the config the records were made with (the budget and cap of the run).

Fields in full: [docs/USAGE.md](../docs/USAGE.md). The rank-n runs (`rankn`) write `rows/<id>.npz` (not for git) and
their own `summary.json`, whose `cap_counters` block counts searches that dropped a child and searches where the cap
could bind ([docs/RANK3.md](../docs/RANK3.md)).

### Cap counters

Every record of a capped search carries the six fields of [docs/CAP.md](../docs/CAP.md) (`cap`, `cap_dropped`,
`cap_dropped_min_total`, `cap_would_pop`, `cap_first_bind`, `cap_needed`); the hybrid repeats them under `dyn_cap_`
and `slack_`, CoV adds `cap_legs_bound`. An uncapped run has `cap: null`, `cap_dropped: 0` and `null` elsewhere.
`summary.json`'s `caps` block, one entry per prefix:

| key | meaning |
|---|---|
| `cap` | the cap(s) watched |
| `rows`, `rows_dropped` | rows, and rows where the cap dropped anything |
| `rows_would_pop` | rows where raising the cap changes the search; **0 means the whole run is independent of the cap** |
| `raise_ids` | those rows, up to 100 ids: rerun them with `--rows <ids>` and the limit raised to the needed value (`--set search.cap=25`; the hybrid's `--set hybrid.dyn_cap=13`) |
| `dropped`, `would_pop` | sums over the rows |
| `dropped_min_total`, `first_bind_min`, `needed_min`, `needed_max` | least over the rows, and the range of `cap_needed` |
| `cap_legs_bound` | CoV only: searches of its rows in which the cap bound |

### Naming a new run folder

`<benchmark>_<method>[_<variant>]`: the benchmark's short name (`ms640`, `bench60`, `ladder60`, `ladder200`,
`holdout60`, `ac19`, `ac1m`, `u124`); the method (`hybrid`, `aut`, `cov`, `ngen_sac`, `rl`, the greedy by its priority
`length` or `s20_mk2`); then variants in order: the backend where both are published (`_fast`, `_spec`), budget and cap
when not the config's (`b<budget>`, `cap<N>`, as in the studies' `..._ms640_b1000_cap24_...`; the two older
`holdout60_*_1k_cap48` folders write `1k`), a row subset (`ms640_rl30`: the first 30 rows). A run without
`--set name=...` keeps its config's stem (`smoke`, `rank3_bf`). Studies keep their source's names.

## Studies

A study is a sweep made on another branch with its own code, carried as its compact files (summaries, tables, graphs,
check logs), byte for byte the source's apart from the README, plus a `MANIFEST.json`. `run.py` never writes there.
Each README opens with what is here, what is not, and how acx reproduces it.

| study | what | budget a start | source branch, commit | raw files not in git |
|---|---|---|---|---|
| [`rank3_bf/`](stable_ac/rank3_bf/README.md) | 3-, 4- and 5-generator brute force on MS640, cap 24 | 1,000 and 10,000 pops | `rank3/brute-force-baseline`, `f2d53ced` | 102 (`*.npz`, `*.jsonl`, `*.jsonl.gz`), 70.5 MB |
| [`cov_all/`](stable_ac/cov_all/README.md) | exhaustive CoV sweep (`suballpxyb8`) on MS640 | 100, 10,000 and 100,000 pops | `cov/all-subsets-sweep`, `fb84a588` | 5 (the 100 and 10,000 `.jsonl.gz`, the three `.jsonl`), 280 MB |

`results/rank3_bf/` is acx's rerun of the rank-3 study at word lengths 1 to 4 (equal cell for cell); `rank4_bf/` and
`rank5_bf/` are row slices of ranks 4 and 5. The CoV sweep has no acx driver: `[cov] family = "suballpxyb8"`
enumerates its starts, and its README shows how to check its records with `acx.cov` and `acx.verify`.

**Manifests.** Each `MANIFEST.json` names its source (`branch`, `commit`, `dir`) and lists every raw file with `path`,
`bytes`, `sha256` and `in_repo`. The one raw file in git is `cov_all/cov_all_suballpxyb8_ms640_b100000.jsonl.gz` (4.1
MB, the transform of every start). Fetch another from a clone that has the source branch, e.g.
`git show f2d53ced:results/stable_ac/rank3_bf/<file> > results/stable_ac/rank3_bf/<file>` (the three uncompressed
`.jsonl` of `cov_all/` are only in S3; the S3 prefixes are in each manifest's `s3` and README).
`tests/test_rank3_study.py` and `tests/test_cov_all_study.py` check a fetched file against its size and sha256, and
`.gitignore` keeps `*.npz`, `*.jsonl` and `*.jsonl.gz` under `results/stable_ac/` (apart from that one file) out of
git.
