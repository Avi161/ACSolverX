# AC-SolverX

**Code and datasets for *The Two-Hump Problem: Bridging the Difficulty Gap in
Mathematical Reinforcement Learning* (ICML 2026), and the stable Andrews-Curtis follow-up.**

- **Project page:** https://icml.cc/virtual/2026/poster/64251
- **arXiv:** https://arxiv.org/abs/2606.21611

The Andrews-Curtis (AC) conjecture says that every balanced presentation of the trivial group,
`<x, y | r1, r2>`, reaches the trivial presentation `<x, y | x, y>` by AC moves (invert a relator,
multiply one relator by another, conjugate a relator). *Stable* AC also allows adding and removing a
generator with a matching relator (AC4/AC5). This repository is `acx`, one small package that searches
for such paths and **verifies every path it reports by replaying it on the presentation it claims to
solve**. A solve is typed: an **`ac_path`** (AC moves on the row), an **aut-assisted** `ac_path` (the search
changed basis; the path is carried back and replayed on the row), or a **`stable_cert`** (proves stable
AC-triviality; reported separately, never merged into `ac_path`).

## Install and quickstart

```bash
python3.12 -m venv .venv && . .venv/bin/activate
pip install -e .[dev]            # numpy 2.1.3, numba 0.63.1, pytest;  add [rl] for torch
                                 # (editable: acx reads data/ and benchmark/ from the checkout)
export NUMBA_NUM_THREADS=1       # one core per search; use run.py's workers for parallel rows
python run.py --config configs/smoke.toml      # about a second: 20 MS640 rows, every path replayed
```

```python
from acx import Presentation, SearchConfig, search, replay

p = Presentation.parse("xxYXY", "xyyXY")
res = search(p, SearchConfig(backend="fast", budget=1000))
res.solved, res.pops, res.path_length          # (True, 7, 5)
replay(p, res.path)                            # raises ReplayError unless the path reaches <x, y | x, y>
res.stats["cap_would_pop"]                     # 0: the relator cap (24) did not change this search
```

`python run.py --config configs/<name>.toml [--set key=value ...] [--rows a:b] [--out dir] [--fresh]`:
`--set` overrides any config value (dotted keys reach sections, `--set search.cap=none`), `--rows` slices the benchmark,
results go to `results/<name>/{config.json, paths.jsonl, summary.json}`, and an interrupted run resumes.
`--set benchmark=<name>` picks the rows: `ms640`, `1190ms`, `bench10`..`bench60`, `ladder20`..`ladder500`,
`ladder20_s20hard`..`ladder300_s20hard`, `ac1m_hard_holdout60`, `ac19_autmin`, `ac1m_autmin`, `u124`
([benchmark/README.md](benchmark/README.md)).

## Methods

Each is one config in `configs/` and one `method` of `run.py`. A method reads only its own sections; any other
section, unknown key or invalid value is an error at load.

| method | what it does | config | sections |
|---|---|---|---|
| **greedy**, `spec` | best-first search over substitution moves (S-moves), ordered by total length (the baseline); pure Python, the reference | `baseline_spec.toml` | `[search]` |
| **greedy**, `fast` | the same search step for step on numba, about 30x faster; length or **S20_MK2** (`L + 20 S + 2 MK`) | `greedy_fast.toml`, `s20_mk2_fast.toml`, `ladder.toml` | `[search]` |
| **aut** | search the Whitehead (Aut(F2)-minimal) representative, carry the path back to the row | `aut.toml` | `[search]` |
| **cov** | one-shot change of variables (family `subnc2pxysb`) before the search; a solve of an image outside the row's orbit is a `stable_cert` | `cov.toml` | `[search]`, `[cov]` |
| **hybrid** | the solve-everything mode: Nielsen/pinch cascade, then one best-first search over rank two and higher rank; certificate written as elementary (and AC4/AC5) moves | `hybrid.toml` | `[hybrid]` |
| **ngen** | n-generator search, with the transform to relators of length <= 3 (SAC) and its lift to a stable path | `ngen_sac.toml` | `[search]`, `[ngen]` |
| **rl** (optional) | the paper's PPO policy, step 1000, as a beam search; needs `pip install -e .[rl]` | `rl.toml` | `[rl]` |
| **rankn** | rank-3/4/5 brute force: stabilise each row with every short word and search each start; writes per-row `rows/<id>.npz` and a summary, not `paths.jsonl` ([docs/RANK3.md](docs/RANK3.md)) | `rank3_bf.toml`, `rank4_bf.toml`, `rank5_bf.toml` | `[search]`, `[rankn]` |

`[search]` keys: `priority` (`length` or `s20_mk2`), `cap` (default 24, `"none"` = uncapped), `budget` (pops, default
10,000), `backend` (`spec` or `fast`), `cyclic`. `[hybrid]` keys: `budget` (work units), `r2_cap`, `dyn_cap`, `slack`,
`penalty`, `dyn_ratio`, `min_uses`, `backend`. [docs/METHODS.md](docs/METHODS.md) defines each method.

```bash
python run.py --config configs/greedy_fast.toml                       # LENGTH greedy, MS640, 10k pops
python run.py --config configs/s20_mk2_fast.toml --rows 0:100         # S20_MK2, first 100 rows
python run.py --config configs/hybrid.toml --set benchmark=ac19_autmin --set workers=4
python run.py --config configs/rank3_bf.toml --rows 0:40              # rank-3 brute force, seconds
```

## The relator cap

Children with a relator longer than `cap` are not searched. The cap is a config value, and every search counts what
it dropped and whether a dropped child would have been popped with a larger cap: six fields in every record
(`cap`, `cap_dropped`, `cap_dropped_min_total`, `cap_would_pop`, `cap_first_bind`, `cap_needed`) and a `caps` block in
`summary.json`. `cap_would_pop == 0` means the same run at any larger cap; otherwise `cap_needed` is the cap to raise
to. The counting is one module, `acx/core/capcount.py`, that knows no heuristic. See [docs/CAP.md](docs/CAP.md).

## Verify

```bash
pytest                    # the default selection, a few minutes
pytest -m ""              # adds the slow parity and census sets
```

Every record is written only after its certificate replays on its row (`acx.verify.replay`: legal moves, `|det| = 1`
throughout, the cap, a trivial end). The `spec` and `fast` backends are tested to pop the same states in the same order
and report the same statistics, cap counters included.

## Headline numbers

Reproduced on this branch with `python run.py`; each is a `results/<run>/summary.json`. Cap 24 and the fast backend
unless stated; cost is heap pops for searches and work units for the hybrid. The full table, path lengths and the
command of every run are in [docs/RESULTS.md](docs/RESULTS.md) section 0.

| benchmark (rows) | length greedy, 10k pops | S20_MK2, 10k pops | hybrid, 1,000 units |
|---|---:|---:|---:|
| MS640 (640) | 606 (`spec` and `fast`, row for row) | 626 | **640** (25,064 units) |
| bench60 (60) | 40 | 52 | **60** |
| ladder200 (188) | 40 | 116 | **188** |
| AC19 Aut-min (72,779) | | | **72,779** (188 of them `stable_cert`) |

The ladder ([benchmark/README.md](benchmark/README.md)) has ten levels of increasing difficulty; level 9 is defined by
"length greedy fails at 10M pops, S20_MK2 solves", level 10 by "both fail, only the cascades solve". Those 10M grades
are by record and were not rerun here. U124, the 124 Miller-Schupp classes nobody has solved, stays at 0/124.

## Layout

```
run.py                  the one CLI
configs/                one TOML per method / run
acx/core/               words, moves, priorities, SearchConfig, capcount (the cap counter)
acx/search/             best-first search: spec (Python) and fast (numba) backends
acx/verify/             replay (the only judge), elementary decoder
acx/aut/  cov/  hybrid/  ngen/  rl/     the methods
acx/runner.py  acx/data.py              config + rows + results folder; datasets and benchmarks by name
data/  benchmark/       datasets, frozen evaluation sets and the ladder
tests/                  pytest (default selection; -m "" for the slow sets)
results/                committed summary.json / config.json of the quoted runs (paths.jsonl is regenerated)
docs/                   METHODS, CAP, ARCHITECTURE, RANK3, RESULTS, PROVENANCE
```

## Docs

- [docs/METHODS.md](docs/METHODS.md): moves, the cap, the search, priorities, backends and their parity contract,
  automorphisms and transport, units, hybrid, change of variables, n-generator search, RL, verification.
- [docs/CAP.md](docs/CAP.md): the relator cap and its counters.
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): the module map and the exact interfaces.
- [docs/RANK3.md](docs/RANK3.md): the rank-n brute force and the n-generator package.
- [docs/RESULTS.md](docs/RESULTS.md): every number with its source; what was tried and dropped; open experiments.
- [docs/PROVENANCE.md](docs/PROVENANCE.md): component -> branch -> commit for everything here.
- [benchmark/README.md](benchmark/README.md): the frozen evaluation sets, the ladder, the AC1M hard split.
- Theory (no code here): the AK(3) and U124 notes live on `codex/proofs`, `fable/proofs` and
  `cursor/u124-stable-ac-1b54`; the equivalence certificates of the 124 unsolved classes ship as
  `data/equivalence_classes/certificates.json`, checked by `acx.aut.equivalence.check`.

## Datasets (`data/`)

Each `.txt` line is a flat list of two zero-padded relators (`x -> 1`, `y -> 2`, inverses negative, `0` padding).

- **`1190MS.txt`**: the 1,190 Miller-Schupp benchmark, in canonical form. **`ms640_solved.txt`**: 640 Miller-Schupp
  presentations (MS640), every one solved by the length greedy at 1,000,000 pops.
- **`AC19_extended.txt`**: 156,762 presentations (the first 634 are the first 634 of `1190MS.txt`, then AC19 and
  longer ones); **`AC19.txt`**: 140,535 of length <= 19. **`AC19_extended_aut_min.csv`**: its 72,779 Aut(F2) orbits.
- **`AC1M.txt.gz`**: 1,136,154 presentations; **`AC1M_aut_min.csv.gz`**: its 71,283 orbits.
- **`ms_unsolved_reps/`**: the unsolved Miller-Schupp representatives and the 124 classes (U124).
- **`equivalence_classes/certificates.json`**: certificates joining the 261 U124 presentations into 124 classes.

Large certificate and path files are not committed: `run.py` regenerates them (`results/<name>/paths.jsonl`).

## License

- **Code** is released under the [MIT License](LICENSE).
- **Datasets** (`data/`, including AC-19 and AC-1M) are released under [CC BY 4.0](LICENSE-DATA).
- Two binary files are kept on purpose: the RL checkpoint `acx/rl/checkpoint/610model_1000.pt` (0.6 MB, the paper's
  step-1000 weights) and `benchmark/subsets/subset_coverage.png`. No other binaries or PDFs are tracked.

## Citation

```bibtex
@inproceedings{fagan2026twohump,
  title     = {The Two-Hump Problem: Bridging the Difficulty Gap in Mathematical Reinforcement Learning},
  author    = {Fagan, Lucas and Tarquini, Michele and Shehper, Ali and Manko, Maksymilian and Gruen, Angus and Huang, Coco and Butbaia, Giorgi and Passaro, Davide and Gukov, Sergei},
  booktitle = {Proceedings of the 43rd International Conference on Machine Learning (ICML)},
  year      = {2026},
}
```
