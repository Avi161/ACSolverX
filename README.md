# AC-SolverX

AC-SolverX searches for Andrews-Curtis paths that reduce balanced presentations of the trivial group, such as
`<x, y | xxYYY, xyxYXY>`, to the trivial presentation. Code and datasets for *The Two-Hump Problem: Bridging the
Difficulty Gap in Mathematical Reinforcement Learning* (ICML 2026; [project page](https://icml.cc/virtual/2026/poster/64251),
[arXiv](https://arxiv.org/abs/2606.21611)), and the stable Andrews-Curtis follow-up.

```bash
python3.12 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"          # editable: acx reads data/ and benchmark/; ".[rl]" adds PyTorch for the rl method
export NUMBA_NUM_THREADS=1       # one core per search; a config's `workers` solves rows in parallel
```

The first run compiles the numba kernels (under a minute) and caches them.

## `run.py`: one command for every method

`python run.py --config configs/<method>.toml` runs one search method on a set of presentations, row by row, and writes
what it found. **The config** (TOML) names the `method`, the `benchmark` and the method's settings (budget, priority,
relator cap); `configs/` has one per method and [`configs/template.toml`](configs/template.toml) lists every key with
its default. `--set key=value` overrides any of them for one run, `--rows 0:20` runs a slice.

```bash
python run.py --config configs/smoke.toml                                     # 20 MS640 rows, about a second
python run.py --config configs/s20_mk2_fast.toml --set benchmark=bench60      # a shipped benchmark by name
python run.py --config configs/hybrid.toml --pres "xxYYY, xyxYXY"            # one presentation -> results/hybrid_pres/
python run.py --config configs/hybrid.toml --input examples/presentations.csv # your file -> results/hybrid_presentations/
python run.py --config configs/greedy_fast.toml --input examples/presentations.csv     # the same file, another method
python compare.py results/greedy_fast_presentations results/hybrid_presentations --html compare.html
```

**Your own presentations**: `--input FILE` runs a `.txt` (one presentation per line, `xxYYY, xyxYXY`; upper case is
the inverse), `.csv` (columns `r1, r2, ...`) or `.jsonl` file, optionally gzipped; `--pres "r1, r2"` (repeatable) runs
presentations typed on the command line and prints one line each: solved or not, kind, cost and path length.
[`examples/`](examples/) holds the same eight presentations in each format.

**The output** is `results/<name>/`: `paths.jsonl` (one record per presentation: `solved`, `kind`, `cost`, `sub_moves`,
`elem_moves`, the path, `verified`, CPU time, the cap counters), `summary.json` (solve counts by kind, total and mean
cost, path lengths, CPU per pop) and `config.json`. Running the same command again resumes. `compare.py` puts finished
runs side by side. Every flag, input format, config key and output field: [docs/USAGE.md](docs/USAGE.md).

## Two pipelines: normal or high-speed

| | normal: `path = true` (default) | high-speed: `--set path=false` |
|---|---|---|
| solved, kind, nodes explored (`cost`: pops, hybrid units or rl evaluations) | yes | yes |
| path length in S-moves (`sub_moves`) | yes | yes |
| the path, decoded to elementary AC moves (`elem_moves`, `elementary`) | yes | no |
| every solve replayed on its own row (`verified: true`) | yes | no: not a certificate |

Use the high-speed pipeline to count solves or compare settings; how much CPU it saves, per method, is measured in
[docs/PERFORMANCE.md, "Recording the path"](docs/PERFORMANCE.md#recording-the-path). A result to quote needs the
normal one. **Decode later**: `--solved-from RUN_DIR` reruns only the rows that run solved, with `path = true`; the
search is deterministic, so it finds the same solves at the same cost, now with decoded and verified paths:

```bash
python run.py --config configs/hybrid.toml --set path=false --set name=ms640_fast
python run.py --config configs/hybrid.toml --set path=true --solved-from results/ms640_fast --set name=ms640_fast_paths
```

## MS640: what each method solves, explores and finds

The 640 Miller-Schupp rows of `data/ms640_solved.txt`, fast backend, relator cap 24 (the hybrid has its own limits),
from the shipped `results/ms640_*/summary.json` (normal pipeline, every path replayed). Kinds: plain `ac_path` /
aut-assisted `ac_path` / `stable_cert` (next section). Nodes explored cover every row, a miss spending its whole budget:
10,000 pops (greedy, aut, ngen; CoV in total), 1,000 hybrid units, an rl beam of 256 x 150. Path lengths: mean per solve.

| method (config) | solved / 640 | kinds | nodes explored, total | mean per row | S-moves | elementary moves |
|---|---:|---|---:|---:|---:|---:|
| greedy, LENGTH (`greedy_fast`) | 606 | 606 / 0 / 0 | 576,053 pops | 900.1 | 20.0 | 189.5 |
| greedy, S20_MK2 (`s20_mk2_fast`) | 626 | 626 / 0 / 0 | 382,718 pops | 598.0 | 27.0 | 269.5 |
| hybrid (`hybrid`) | **640** | 128 / 512 / 0 | 25,064 units | 39.2 | 19.3 | 139.1 |
| aut, S20_MK2 on the Aut-min form (`aut`) | 626 | 11 / 615 / 0 | 408,174 pops | 637.8 | 27.2 | 1,258.4 |
| change of variables (`cov`) | 584 | 554 / 0 / 30 | 693,162 pops | 1,083.1 | 14.3 | 99.2 (the 554 `ac_path`s) |
| n-generator, SAC (`ngen_sac`) | 298 | 0 / 0 / 298 | 3,729,167 pops | 5,826.8 | 16.9 | 769.1 (stable moves) |
| rl, first 30 rows only (`rl`, stored as `ms640_rl30`) | 30 / 30 | 30 / 0 / 0 | 9,650 evaluations | 321.7 | 4.4 | 28.2 |

A hybrid unit is not a pop: compare them by CPU, which [docs/PERFORMANCE.md, "Methods side by side"](docs/PERFORMANCE.md#methods-side-by-side)
gives per pop or unit, with bench60 and ladder200. [docs/RESULTS.md](docs/RESULTS.md) has every published run and its
command, such as the hybrid on all 72,779 AC19 Aut(F2) orbits: 72,779 solved, 188 as `stable_cert`.

### Two stored studies on MS640

Two larger sweeps were run on their own branches, with their own code, and are stored as their tables, summaries and
graphs under `results/stable_ac/`; each README says what is here, what is only listed in its `MANIFEST.json`, and how
`acx` reproduces it. Both count the **best start known in advance** (an oracle), so they measure what a start can do,
not what a solver finds:

| study | what was searched (LENGTH greedy, cap 24) | presentations solved of 640 |
|---|---|---|
| [n-generator brute force](results/stable_ac/rank3_bf/README.md) | add a generator `z = w` for every word `w` (rank 3), or two or three such generators (ranks 4 and 5); 40,098,032 searches in all | budget 1,000: control 554; some word of length 1 to 10, 578; the best single word, 528; rank 4, 506; rank 5, 416. Budget 10,000, lengths 1 to 7: control 606, some word 608 |
| [CoV sweep to budget 100,000](results/stable_ac/cov_all/README.md) | every change of variables of the exhaustive family `suballpxyb8`: 114,042 starts | best start 555 / 604 / 626 / 640 at 100 / 1,000 / 10,000 / 100,000 nodes, against the control's 455 / 554 / 606 / 634 |

`results/rank3_bf/` is acx's own rerun of the rank-3 lengths 1 to 4 (equal cell for cell), and
`[cov] family = "suballpxyb8"` enumerates the CoV sweep's starts. [results/README.md](results/README.md#studies) explains
the two kinds of folder.

## AC path or stable AC

| method | `ac_path` (AC moves on the row) | `stable_cert` (stable AC) |
|---|---|---|
| greedy, rl | always: the S-moves decode to elementary AC moves | never |
| aut | always; `aut_assisted` when the row is not its own Aut-minimal form | never |
| hybrid | when every step is at rank two; `aut_assisted` when one is an automorphism | when its search took higher-rank steps (new generators, AC4/AC5) |
| cov | when the row, or an image in its Aut(F2) orbit (`aut_assisted`), is solved | when an image outside the orbit is solved: a change of variables, no elementary path (`elem_moves` null) |
| ngen | when the SAC transform adds no generator | when it adds generators (all 298 MS640 solves): lifted to elementary stable moves |
| rankn | | its stabilised starts add generators; the sweep counts their solves, writes no certificate ([docs/RANK3.md](docs/RANK3.md)) |

**Automorphisms do not make a solve stable.** A solve found in another basis (the Aut-minimal form, a CoV image in
the orbit, the hybrid's Nielsen/pinch cascade) is decoded back to the row: `acx/aut/transport.py` (aut, cov) and
`acx/hybrid/elementary.py` (hybrid) map each move's conjugators through the inverse automorphism, end with the Nielsen
moves that turn the basis back into `x, y`, and replay the result on the row. Such a row is an ordinary `ac_path` of
elementary AC moves with `aut_assisted: true`; it needs `path = true`, or `--solved-from` after a high-speed run.

## Docs

- [docs/USAGE.md](docs/USAGE.md): inputs, flags, run names and resume, config keys, output fields, comparing runs.
- [docs/METHODS.md](docs/METHODS.md): moves, search, priorities, transport, the decoder, every method, verification.
- [docs/PERFORMANCE.md](docs/PERFORMANCE.md): CPU per pop or unit, recording the path, the uncapped search.
- [docs/RESULTS.md](docs/RESULTS.md): every published number and the command that reproduces it.
- [docs/CAP.md](docs/CAP.md): the relator cap (`cap`, default 24, `"none"` = uncapped) and its counters.
- [docs/RANK3.md](docs/RANK3.md): the rank-n brute force and the n-generator package.
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [docs/PROVENANCE.md](docs/PROVENANCE.md): the module map; sources.
- [benchmark/README.md](benchmark/README.md): the evaluation sets and the difficulty ladder.
- [results/README.md](results/README.md): run folders, the two stored studies and their manifests.
- [results/stable_ac/rank3_bf/README.md](results/stable_ac/rank3_bf/README.md): the 3-, 4- and 5-generator brute
  force on MS640.
- [results/stable_ac/cov_all/README.md](results/stable_ac/cov_all/README.md): the exhaustive CoV sweep on MS640 at
  budgets 100 to 100,000.

## Datasets (`data/`) and tests

- **`1190MS.txt`**: the 1,190 Miller-Schupp benchmark; **`ms640_solved.txt`**: the 640 (MS640) the length greedy solves
  at 1,000,000 pops. **`AC19_extended.txt`**: 156,762 presentations; **`AC19.txt`**: the 140,535 of length <= 19;
  **`AC19_extended_aut_min.csv`**: its 72,779 Aut(F2) orbits. **`AC1M.txt.gz`**: 1,136,154 presentations;
  **`AC1M_aut_min.csv.gz`**: its 71,283 orbits.
- **`ms_unsolved_reps/`**: the unsolved Miller-Schupp representatives and the 124 classes nobody has solved (U124);
  **`equivalence_classes/certificates.json`** joins their 261 presentations into the 124 classes.

`pytest` runs the default selection (a few minutes); `pytest -m ""` adds the slow parity and census sets.

## License

Code: [MIT](LICENSE). Datasets (`data/`, including AC-19 and AC-1M): [CC BY 4.0](LICENSE-DATA). Binary files kept on
purpose: the RL checkpoint `acx/rl/checkpoint/610model_1000.pt` (0.6 MB, the paper's step-1000 weights),
`benchmark/subsets/subset_coverage.png`, the eight graphs (`.png`) of the two studies under `results/stable_ac/`, and
the CoV sweep's budget-100,000 records `results/stable_ac/cov_all/cov_all_suballpxyb8_ms640_b100000.jsonl.gz` (4.1 MB,
the transform of every start). The studies' other raw files are not in git; each `MANIFEST.json` lists them with size
and sha256.

## Citation

```bibtex
@inproceedings{fagan2026twohump,
  title     = {The Two-Hump Problem: Bridging the Difficulty Gap in Mathematical Reinforcement Learning},
  author    = {Fagan, Lucas and Tarquini, Michele and Shehper, Ali and Manko, Maksymilian and Gruen, Angus and Huang, Coco and Butbaia, Giorgi and Passaro, Davide and Gukov, Sergei},
  booktitle = {Proceedings of the 43rd International Conference on Machine Learning (ICML)},
  year      = {2026},
}
```
