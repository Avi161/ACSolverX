# `experiments/stable_ac/`

**Branch A (No CoV)** of the stable-AC plan: for each benchmark presentation `⟨x,y | r1,r2⟩` and
each word `w(x,y)` from a family, solve `⟨x,y,z | r1, r2, z⁻¹w⟩` at `n_gen = 3` with the same greedy
best-first S-move search as the baseline, and compare against baseline at the same node budget.

| file | what it is |
|---|---|
| `solvern.py` | **general-`n` numba solver** — int8 signed codec, works at any `n_gen ≤ 26`, any `n_rel ≥ 2`. Trace-equal to `greedy_tests/spec/` at `n_gen ≤ 3` (`test_solvern.py` pins it); `n_gen = 4+` is seamless. Entry: `search_n(pres, budget, cap, cyclic, progress)`. |
| `word_families.py` | z-word builders, n-agnostic: **A1** curated `\|w\| ≤ 4` · **A2** prefixes of all cyclic rotations of each relator (raw count `Σ\|rᵢ\|²`, deduped; `A2_MAX_WORDS` caps it — A2 dominates cost) · **A3** proportion grid `r1[:p] + r2[:q]`. |
| `run_nocov.py` | the sweep runner: one jsonl per `(benchmark, family, budget)`, row identity `(name, z_word)`, date-agnostic glob resume, Drive staging, optional minimal W&B (`job_type stable_ac_nocov`). |
| `config_nocov.yaml` | the production config — every knob commented. The notebook loads it and merges `OVERRIDES`. |

Run on Colab via `experiments/stable_ac_nocov.ipynb` (CONFIG / SETUP / RUN, branch
`test/stable-ac-moves-w4`). Locally:

```bash
# never above budget 1000 locally; >1000 refuses without ACSOLVERX_ALLOW_BIG=1
.venv/bin/python3 -c "
import yaml; from experiments.stable_ac.run_nocov import run_nocov
cfg = yaml.safe_load(open('experiments/stable_ac/config_nocov.yaml'))
cfg.update({'USE_WANDB': False, 'MOUNT_DRIVE': False})
run_nocov(cfg, 1000, 'A1')"
```

Outputs → `results/stable_ac/nocov/` (see its section in `results/README.md`). Benchmark input →
`results/benchmark/combined/benchmark_combined_{11,22,44,66}.json`
(`experiments/analysis/combined_benchmark.py`). Scoring rules (ladder = speedup ratios, reach =
`solved`/`bar_to_beat`, never mixed) live in the week-4 plan and `analysis/README.md`.

Traps already encoded in tests: two symbol orders (booth for canonical form, ASCII for the heap
tie-break) must never be conflated; min/max stats are first-crossing, not set-min; paths are stored
as `"i_j_s_k1_k2"` move strings and decoded only by replay (`moves_to_states`).
