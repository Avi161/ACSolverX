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
solve**:

- **greedy**: best-first search over substitution moves (one S-move = multiply a relator by a conjugate of
  the other, at least one letter cancelling), ordered by total length (the baseline) or by **S20_MK2**
  (`L + 20 S + 2 MK`). Two backends: `spec` (pure Python, the reference) and `fast` (numba, the same search
  step for step, about 40x faster). The fast kernels are a library the other methods run on.
- **aut**: search the Whitehead (Aut(F2)-minimal) representative, then transport the path back to the row.
- **cov**: one-shot change of variables (family `subnc2pxysb`); a solve is a stable-AC certificate.
- **hybrid**: the solve-everything mode: Nielsen/pinch cascade, then one best-first search over rank two
  and higher rank; every certificate is written out as elementary (and stable) moves on the row.
- **ngen**: n-generator search and the transform to relators of length <= 3 (SAC), lifted to a stable path.
- **rl** (optional, PyTorch): the paper's 610model PPO policy (step 1000) as a beam search.

Every solve is typed: an **`ac_path`** (AC moves on the row), an **aut-assisted** `ac_path` (the search
changed basis; the path is carried back to the row and replayed there), or a **`stable_cert`** (proves
stable AC-triviality; reported separately, never merged into `ac_path`).

## Install and run

```bash
python3.12 -m venv .venv && . .venv/bin/activate
pip install -e .[dev]            # numpy 2.1.3, numba 0.63.1, pytest;  add [rl] for torch
                                 # (install editable: acx reads data/ and benchmark/ from the checkout)
pytest                           # default selection, a few minutes;  pytest -m "" runs the slow tests too
python run.py --config configs/smoke.toml      # seconds
```

One command per method (`--set key=value` overrides any config value, dotted keys reach sections;
`--rows a:b` slices the benchmark; results go to `results/<name>/{paths.jsonl, summary.json}`):

| method | command |
|---|---|
| slow baseline (pure-Python length greedy) | `python run.py --config configs/baseline_spec.toml` |
| fast greedy, length / S20_MK2 | `python run.py --config configs/greedy_fast.toml` / `configs/s20_mk2_fast.toml` |
| Aut-min + transport | `python run.py --config configs/aut.toml` |
| change of variables | `python run.py --config configs/cov.toml` |
| hybrid | `python run.py --config configs/hybrid.toml` |
| n-generator SAC | `python run.py --config configs/ngen_sac.toml` |
| RL beam (needs `pip install -e .[rl]`) | `python run.py --config configs/rl.toml` |
| the difficulty ladder | `python run.py --config configs/ladder.toml` |

Benchmarks by name (`--set benchmark=...`): `ms640`, `1190ms`, `bench10`..`bench60`, `ladder20`..`ladder500`,
`ladder20_s20hard`..`ladder300_s20hard`, `ac1m_hard_holdout60`, `ac19_autmin`, `ac1m_autmin`, `u124`
([benchmark/README.md](benchmark/README.md)). In Python: `from acx import search, replay, Presentation`
([docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)).

## Headline numbers

Reproduced on this branch: every number below is a `results/<run>/summary.json` written by `run.py` with the current
code, each record replayed on its row before it was written, and checked against an independent replay and against the
original code's per-row reference (0 mismatches in solved flag, pops or units, and path length). Shared 4-core VM, one
core per worker, cap 24 unless stated. Path lengths are totals over the solved rows (median per row) in two units:
**S-moves** (substitution moves of the search; for the hybrid its S-move steps, automorphism steps not counted) and
**elementary** moves (invert / swap / conjugate by a letter / multiply: the path replayed on the row). The length
columns count AC paths only (`ac_path`, aut-assisted included); `stable_cert` lengths are in the footnotes, never in
these columns. Cost is heap pops for searches and work units for the hybrid.

| benchmark | method (run) | solved | ac_path / aut-assisted / stable_cert | cost | S-moves | elementary |
|---|---|---:|---|---:|---:|---:|
| MS640 (640) | length greedy, 10k pops, `spec` (`ms640_length_spec`) | 606 | 606 / 0 / 0 | 576,053 pops | 12,103 (8) | 114,828 (54) |
| MS640 | length greedy, 10k pops, `fast` (`ms640_length_fast`) | 606 | 606 / 0 / 0 | 576,053 pops | 12,103 (8) | 114,828 (54) |
| MS640 | S20_MK2, 10k pops (`ms640_s20_mk2_fast`) | 626 | 626 / 0 / 0 | 382,718 pops | 16,872 (9) | 168,702 (56.5) |
| MS640 | hybrid, 1,000 units (`ms640_hybrid`) | **640** | 128 / 512 / 0 | 25,064 units | 12,346 (10) | 89,055 (54) |
| AC19 Aut-min (72,779) | hybrid (`ac19_hybrid`) | **72,779** | 36,811 / 35,780 / 188 [a] | 2,489,726 units | 1,232,877 (11) | 7,341,111 (71) |
| AC1M Aut-min (71,283) | hybrid (`ac1m_hybrid`) | **71,281** | 34,649 / 36,508 / 124 [b] | 2,384,509 units | 1,136,288 (11) | 7,239,114 (71) |
| bench60 (60) | length greedy, 10k pops (`bench60_length`) | 40 | 40 / 0 / 0 | 248,227 pops | 1,475 (24) | 15,028 (217) |
| bench60 | S20_MK2, 10k pops (`bench60_s20_mk2`) | 52 | 52 / 0 / 0 | 141,740 pops | 3,237 (31.5) | 34,173 (281) |
| bench60 | hybrid (`bench60_hybrid`) | **60** | 7 / 53 / 0 | 4,783 units | 3,382 (16.5) | 27,641 (170) |
| ac1m_hard holdout 60 | length / S20_MK2, 10k pops (`holdout60_length`, `holdout60_s20_mk2`) | 44 / 50 | all ac_path | 329,601 / 165,049 pops | 2,447 / 3,069 | 26,589 / 33,345 |
| ac1m_hard holdout 60 | length / S20_MK2, 1k pops, cap 48, the published protocol (`holdout60_*_1k_cap48`) | 0 / 33 | all ac_path | 60,000 / 41,953 pops | - / 1,465 (36) | - / 15,128 (342) |
| ac1m_hard holdout 60 | hybrid (`holdout60_hybrid`) | **60** | 0 / 60 / 0 | 3,770 units | 1,697 (16) | 17,593 (223.5) |
| U124 (124) | S20_MK2 10k pops; hybrid 1,000 units (`u124_s20_mk2`, `u124_hybrid`) | **0 / 0** | | 1,149,399 pops; 124,000 units | | |
| ladder200 (188) | length / S20_MK2, 10k pops (`ladder200_length`, `ladder200_s20_mk2`) | 40 / 116 | all ac_path | 1,551,196 / 1,063,702 pops | 1,991 / 7,697 | 21,108 / 86,172 |
| ladder200 | hybrid (`ladder200_hybrid`) | **188** | 8 / 173 / 7 [c] | 22,319 units | 7,612 (20) | 80,878 (301) |

[a] the 188 stable certificates: 2,722 S-moves and 93,692 elementary and AC4/AC5 moves. [b] 124: 1,662 and 62,312;
misses `ac1m_54083`, `ac1m_68740`. [c] 7: 117 and 6,051. The hybrid's MS640 finishing stages are relator descent 98,
pinch cascade 328, search 214, each row's units and stage equal to the original code's run.

Commands, as run (`python run.py --config configs/<file>.toml --set name=<run> ...`; the full list is in
[docs/RESULTS.md](docs/RESULTS.md) section 0): MS640 rows use the configs as shipped (`baseline_spec`, `greedy_fast`,
`s20_mk2_fast`, `hybrid`); the others add `--set benchmark=<name> --set workers=4`, e.g.
`python run.py --config configs/hybrid.toml --set name=ac19_hybrid --set benchmark=ac19_autmin --set workers=4`
(about 4.5 minutes on 4 cores); the published holdout protocol adds `--set search.budget=1000 --set search.cap=48`.

The ladder (the headline benchmark; [benchmark/README.md](benchmark/README.md)) by level, `ladder200`, 10k pops at
cap 24 (`configs/ladder.toml`, `--set search.priority=length`, and `configs/hybrid.toml --set benchmark=ladder200`):

| level | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| rows | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 19 | 9 |
| length greedy | 20 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| S20_MK2 | 20 | 20 | 13 | 14 | 12 | 18 | 7 | 6 | 6 | 0 |
| hybrid (1,000 units) | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 19 | 9 |

Level 9 is defined by "length greedy fails at 10M pops, S20_MK2 solves"; level 10 by "both fail at 10M, only the
cascades solve". Those 10M grades are by record (a 10M-pop run needs about 50 GB) and were not rerun; at 10,000 pops no
greedy arm solves level 10 and the hybrid solves every row. Published lines (not rerun here;
[docs/RESULTS.md](docs/RESULTS.md)): the paper's PPO agent solves 610 Miller-Schupp presentations against 457 for the
prior RL baseline (`main`'s README says "610 of the 1,190" in one place and "610 of the first 634" in another; confirm
the denominator against the paper before quoting it); S20_MK2 solves 72,519 of the 72,779 AC19 Aut-min orbits at 10k
pops (cap 48) against 71,936 for length greedy; U124 stays at 0/124 under S20_MK2 at 10,000,000 pops (cap 64) and every
other probe on record.

## Docs

- [docs/METHODS.md](docs/METHODS.md): moves, the cap, the search, priorities, backends and their parity
  contract, automorphisms and transport, units, hybrid, change of variables (what `subnc2pxysb` means),
  n-generator search, verification.
- [docs/RESULTS.md](docs/RESULTS.md): every number with its source; what was tried and dropped; open experiments.
- [docs/PROVENANCE.md](docs/PROVENANCE.md): component -> branch -> commit for everything here.
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): the module map and the exact interfaces.
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

Large certificate and path files are not committed: `run.py` regenerates them (`results/<name>/paths.jsonl`); the
`summary.json` and `config.json` behind every number above are committed under `results/`.

## License

- **Code** is released under the [MIT License](LICENSE).
- **Datasets** (`data/`, including AC-19 and AC-1M) are released under [CC BY 4.0](LICENSE-DATA).
- Two binary files are kept on purpose: the RL checkpoint `acx/rl/checkpoint/610model_1000.pt` (0.6 MB, the paper's
  step-1000 weights) and `benchmark/subsets/subset_coverage.png` (from `main`). No other binaries or PDFs are tracked.

## Citation

```bibtex
@inproceedings{fagan2026twohump,
  title     = {The Two-Hump Problem: Bridging the Difficulty Gap in Mathematical Reinforcement Learning},
  author    = {Fagan, Lucas and Tarquini, Michele and Shehper, Ali and Manko, Maksymilian and Gruen, Angus and Huang, Coco and Butbaia, Giorgi and Passaro, Davide and Gukov, Sergei},
  booktitle = {Proceedings of the 43rd International Conference on Machine Learning (ICML)},
  year      = {2026},
}
```
