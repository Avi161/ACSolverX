# `experiments/stable_ac/`

The stable-AC umbrella: shared solver core at this level, one **self-contained folder per
pipeline** (code + config yaml + Colab notebook + tests, all in one place).

## Shared core

| file | what it is |
|---|---|
| `solvern.py` | **general-`n` numba solver** — int8 signed codec, works at any `n_gen ≤ 26`, any `n_rel ≥ 2`. Trace-equal to `greedy_tests/spec/` at `n_gen ≤ 3` (`greedy_tests/test_solvern.py` pins it); `n_gen = 4+` is seamless. Entry: `search_n(pres, budget, cap, cyclic, progress)`. |
| `solvern_fast.py` | **`search_n_fast` — the HIGH_SPEEDUP twin**: same search, fused `@njit` expansion + packed-bytes keys, ~5× faster, EVERY result field bit-identical (paths included; whole-dict parity pinned by `greedy_tests/test_solvern_fast.py`). Toggled per run by `HIGH_SPEEDUP` in the nocov config; result-neutral, so files resume across modes. |
| `word_families.py` | z-word builders, n-agnostic: **A1** curated `\|w\| ≤ 4` · **A2** prefixes of all cyclic rotations of each relator (raw count `Σ\|rᵢ\|²`, deduped; `A2_MAX_WORDS` caps it — A2 dominates cost) · **A3** proportion grid `r1[:p] + r2[:q]`. |
| `verify_results.py` | the **certificate verifier**: replays every `solved: true` row's move path through the pure-Python spec (never through a solver — a solver bug cannot self-certify), checking move legality, the per-relator cap at every step, a genuinely trivial endpoint, `abs_det` preservation, and cross-file **budget invariance**. Handles both pipelines' formats. Run it on any results before believing them. |

The core's tests live in `tests/greedy/` (`test_solvern.py`, `test_word_families.py`)
because spec-parity needs the spec and its fixtures (which stay under `experiments/greedy_tests/`).

## `nocov/` — Branch A (No CoV)

For each benchmark presentation `⟨x,y | r1,r2⟩` and each word `w(x,y)` from a family, solve
`⟨x,y,z | r1, r2, z⁻¹w⟩` at `n_gen = 3` and compare against baseline at the same node budget.

| file | what it is |
|---|---|
| `PIPELINE.md` | **the full walkthrough** — what the experiment is, every knob, exact schemas, measured numbers. Read this first. |
| `run_nocov.py` | the sweep runner: one jsonl per `(benchmark, family, budget)`, row identity `(name, z_word)`, date-agnostic glob resume, Drive staging, optional minimal W&B (`job_type stable_ac_nocov`). |
| `config_nocov.yaml` | the production config — every knob commented. The notebook loads it and merges `OVERRIDES`. |
| `stable_ac_nocov.ipynb` | the 3-cell Colab notebook (CONFIG / SETUP / RUN, branch `test/stable-ac-moves-w4`). |
| `test_run_nocov.py` | harness tests: schema, resume, torn-line repair, filename identity, yaml sanity, budget guard, one real budget-100 micro-run. |

Locally:

```bash
# never above budget 1000 locally; >1000 refuses without ACSOLVERX_ALLOW_BIG=1
.venv/bin/python3 -c "
import yaml; from experiments.stable_ac.nocov.run_nocov import run_nocov
cfg = yaml.safe_load(open('experiments/stable_ac/nocov/config_nocov.yaml'))
cfg.update({'USE_WANDB': False, 'MOUNT_DRIVE': False})
run_nocov(cfg, 1000, 'A1')"
```

Outputs → `results/stable_ac/nocov/`. Benchmark input →
`results/benchmark/combined/benchmark_combined_{11,22,44,66}.json`
(`experiments/analysis/combined_benchmark.py`). Scoring rules (ladder = speedup ratios, reach =
`solved`/`bar_to_beat`, never mixed) live in the week-4 plan and `analysis/README.md`.

Traps already encoded in tests: two symbol orders (booth for canonical form, ASCII for the heap
tie-break) must never be conflated; min/max stats are first-crossing, not set-min; paths are stored
as `"i_j_s_k1_k2"` move strings and decoded only by replay (`moves_to_states`).

## `cov/` — Branch B (one-shot change of variables, case i)

`⟨x,y | r1,r2⟩` → introduce `z = w(x,y)`, substitute, isolate `x`, remove it → a new 2-gen pair
that feeds the **existing** 2-gen numba greedy unchanged.

| file | what it is |
|---|---|
| `cov.py` | the transform: `substitute_word` → `isolate` → `substitute_generator` → relabel; naive `NAIVE_Z_FAMILY` picker (`Z_FAMILY_TAG` is part of the run identity — bump it when the family changes). |
| `run_cov.py` | the runner: benchmark CSV rows → CoV (or identity, `mode: baseline`) → 2-gen greedy → one jsonl per budget in `results/stable_ac/cov/`. Reuses `run_baseline`'s seams by import. |
| `config_cov.yaml` | the reviewable config. |
| `cov_baseline.ipynb` | the 3-cell Colab notebook. |
| `test_cov.py` | the paper's §4 worked example pinned exactly, family fallbacks, runner schema/resume. |

```bash
.venv/bin/python3 -m experiments.stable_ac.cov.run_cov --config experiments/stable_ac/cov/config_cov.yaml
```

## Tests

```bash
.venv/bin/python3 -m pytest tests/stable_ac -q     # both pipelines' harness tests
.venv/bin/python3 -m pytest tests/greedy -q        # solver core (spec parity, contract)
```

Both are collected by a bare `pytest` (see `pytest.ini`).

## Verifying results (do this before believing any run)

```bash
.venv/bin/python3 -m experiments.stable_ac.verify_results          # everything under results/stable_ac
.venv/bin/python3 -m experiments.stable_ac.verify_results <files>  # specific jsonl(s)
```

Runs no searches (safe anywhere, seconds even on production files); exits non-zero and lists every
failing certificate. `results/README.md` records the current standing count. Every row also carries
`git_commit` — the exact code that produced it. `greedy_tests/test_verify_results.py` keeps the
verifier honest by tampering with real certificates and requiring it to fail.
