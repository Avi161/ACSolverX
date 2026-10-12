# AC-SolverX

AC-SolverX searches for Andrews-Curtis paths that reduce balanced presentations of the trivial group, such as
`<x, y | xxYYY, xyxYXY>`, to the trivial presentation, with several search methods behind one command. Give it a
shipped benchmark or your own file of presentations, and it tells you per presentation whether it was solved, what the
search cost and how long the path is, having replayed every path on the presentation it claims to solve.

Code and datasets for *The Two-Hump Problem: Bridging the Difficulty Gap in Mathematical Reinforcement Learning*
(ICML 2026; [project page](https://icml.cc/virtual/2026/poster/64251), [arXiv](https://arxiv.org/abs/2606.21611)),
and the stable Andrews-Curtis follow-up. A solve is an **`ac_path`** (AC moves on the presentation, `aut_assisted` when
found in another basis and carried back) or a **`stable_cert`** (stable AC: AC4/AC5 moves or a change of variables),
always reported apart.

## Install

```bash
python3.12 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"          # numpy, numba, pytest; ".[rl]" adds PyTorch for the rl method
export NUMBA_NUM_THREADS=1       # one core per search; a config's `workers` solves rows in parallel
```

The install is editable because `acx` reads `data/` and `benchmark/` from the checkout. The first run compiles the
numba kernels (under a minute) and caches them.

## Quick start

```bash
python run.py --config configs/smoke.toml                                 # 20 MS640 rows, about a second
python run.py --config configs/s20_mk2_fast.toml --set benchmark=bench60  # a shipped benchmark by name
python run.py --config configs/hybrid.toml --input examples/presentations.csv   # your file -> results/hybrid_presentations/
python run.py --config configs/greedy_fast.toml --pres "xxYYY, xyxYXY"    # one presentation -> results/greedy_fast_pres/
python run.py --config configs/greedy_fast.toml --set benchmark=bench60 --set path=false --set name=bench60_nopath
python run.py --config configs/greedy_fast.toml --input examples/presentations.csv   # the same file, another method
python compare.py results/greedy_fast_presentations results/hybrid_presentations --html compare.html
```

A run writes `results/<name>/`: `paths.jsonl` (one record per presentation), `summary.json` and `config.json`; run it
again and it resumes. `path=false` skips writing and replaying the paths, which is faster. `compare.py` prints one
table of solve rate, cost, path length and CPU per pop, and `--html` adds charts. Input formats, every flag, the
config keys and every output field are in [docs/USAGE.md](docs/USAGE.md).

## Methods

Each is a `method` of `run.py` with a ready config in `configs/`; [docs/METHODS.md](docs/METHODS.md) defines them.

| method | what it does | config |
|---|---|---|
| **greedy** | best-first search over substitution moves, ordered by total length (the baseline) or **S20_MK2** (`L + 20 S + 2 MK`); a pure-Python `spec` backend and a numba `fast` one that takes the same steps | `greedy_fast.toml`, `s20_mk2_fast.toml`, `baseline_spec.toml`, `ladder.toml` |
| **aut** | search the Aut(F2)-minimal (Whitehead) form of the row, carry the path back to the row | `aut.toml` |
| **cov** | the row, then its changes of variables, in one budget; a solve outside the row's orbit is a `stable_cert` | `cov.toml` |
| **hybrid** | a Nielsen/pinch cascade, then one best-first search over rank two and higher rank; the most solves | `hybrid.toml` |
| **ngen** | n-generator search, after a transform to relators of length <= 3, lifted to a stable path | `ngen_sac.toml` |
| **rl** (optional) | the paper's PPO policy (step 1000) as a beam search; needs `pip install -e ".[rl]"` | `rl.toml` |
| **rankn** | rank-3/4/5 brute force: stabilise each row with every short word and search each start ([docs/RANK3.md](docs/RANK3.md)) | `rank3_bf.toml`, `rank4_bf.toml`, `rank5_bf.toml` |

Children with a relator longer than `cap` (default 24, `"none"` = uncapped) are not searched, and every search counts
whether that changed what it popped ([docs/CAP.md](docs/CAP.md)); the counting is one package, `acx/core/capcount/`.

## Numbers

Each published run is a `results/<run>/summary.json`, with its command, in [docs/RESULTS.md](docs/RESULTS.md); CPU cost
per pop and the cost of an uncapped search are in [docs/PERFORMANCE.md](docs/PERFORMANCE.md). Cap 24, fast backend:

| benchmark (rows) | length greedy, 10k pops | S20_MK2, 10k pops | hybrid, 1,000 units |
|---|---:|---:|---:|
| MS640 (640) | 606 | 626 | **640** |
| bench60 (60) | 40 | 52 | **60** |
| ladder200 (188) | 40 | 116 | **188** |
| AC19 Aut-min (72,779) | | | **72,779** (188 `stable_cert`) |

## Tests

```bash
pytest                    # the default selection, a few minutes
pytest -m ""              # adds the slow parity and census sets
```

## Layout

```
run.py, compare.py      the two commands
configs/                one TOML per method; template.toml lists every key
examples/               sample input files (.txt, .csv, .jsonl)
acx/core/               words, moves, priorities, SearchConfig, capcount/ (the cap counters)
acx/search/             best-first search: spec (Python) and fast (numba) backends
acx/verify/             replay (the only judge), elementary decoder
acx/aut/ cov/ hybrid/ ngen/ rl/    the methods
acx/runner/, data.py, report.py    configs, rows and results folders; datasets by name; compare.py's tables
data/, benchmark/       datasets, frozen evaluation sets and the ladder
results/                summary.json and config.json of the published runs (paths.jsonl is regenerated)
```

## Docs

- [docs/USAGE.md](docs/USAGE.md): inputs, flags, run names, config keys, output fields, comparing runs.
- [docs/METHODS.md](docs/METHODS.md): moves, the search, priorities, backends, automorphisms, hybrid, change of
  variables, n-generator search, RL, verification.
- [docs/CAP.md](docs/CAP.md): the relator cap and its counters.
- [docs/RESULTS.md](docs/RESULTS.md) and [docs/PERFORMANCE.md](docs/PERFORMANCE.md): every number, and what it costs.
- [docs/RANK3.md](docs/RANK3.md): the rank-n brute force and the n-generator package.
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): the module map and the interfaces.
- [docs/PROVENANCE.md](docs/PROVENANCE.md): where each part comes from.
- [benchmark/README.md](benchmark/README.md): the evaluation sets and the difficulty ladder.

## Datasets (`data/`)

- **`1190MS.txt`**: the 1,190 Miller-Schupp benchmark. **`ms640_solved.txt`**: 640 of them (MS640), every one solved by
  the length greedy at 1,000,000 pops.
- **`AC19_extended.txt`**: 156,762 presentations; **`AC19.txt`**: the 140,535 of length <= 19;
  **`AC19_extended_aut_min.csv`**: its 72,779 Aut(F2) orbits. **`AC1M.txt.gz`**: 1,136,154 presentations;
  **`AC1M_aut_min.csv.gz`**: its 71,283 orbits.
- **`ms_unsolved_reps/`**: the unsolved Miller-Schupp representatives and the 124 classes nobody has solved (U124);
  **`equivalence_classes/certificates.json`** joins their 261 presentations into the 124 classes
  (`acx.aut.equivalence.check` re-checks it).

## License

Code: [MIT](LICENSE). Datasets (`data/`, including AC-19 and AC-1M): [CC BY 4.0](LICENSE-DATA). Two binary files are
kept on purpose: the RL checkpoint `acx/rl/checkpoint/610model_1000.pt` (0.6 MB, the paper's step-1000 weights) and
`benchmark/subsets/subset_coverage.png`.

## Citation

```bibtex
@inproceedings{fagan2026twohump,
  title     = {The Two-Hump Problem: Bridging the Difficulty Gap in Mathematical Reinforcement Learning},
  author    = {Fagan, Lucas and Tarquini, Michele and Shehper, Ali and Manko, Maksymilian and Gruen, Angus and Huang, Coco and Butbaia, Giorgi and Passaro, Davide and Gukov, Sergei},
  booktitle = {Proceedings of the 43rd International Conference on Machine Learning (ICML)},
  year      = {2026},
}
```
