# `experiments/`

All experiment code. **CPU + numba only** on this branch — no JAX, no GPU, no PPO. The JAX stack at
the repo root (`envs/`, `network.py`, `ppo_ac_s.py`) is a *spec to port from, never to import*.

| directory / file | what it is | its README |
|---|---|---|
| `search/` | **the solvers.** `greedy_baseline.py` (heavy: bool arrays + dict) and `greedy_compact.py` (nibble arena + int32 heap, ~3× smaller, **pops identically**) | — |
| `run_baseline.py` | the runner: jsonl, resume, memory guard, multiprocessing, W&B | — |
| `wandb_tracking.py` | W&B run identity, panels, live metrics | — |
| `greedy_baseline.ipynb` | the 3-cell Colab notebook (CONFIG / SETUP / RUN) | — |
| `greedy_tests/` | the pipeline's test suite — a general-`n` spec, an invariant the solver never computes, and a `SolverAdapter` seam the stable-AC port plugs into | [→](greedy_tests/README.md) |
| `stable_ac/` | **Branch A (No CoV)**: `solvern.py` (general-`n` numba solver, spec-trace-equal at `n_gen≤3`), `word_families.py` (A1/A2/A3), `run_nocov.py` + `config_nocov.yaml` | [→](stable_ac/README.md) |
| `stable_ac_nocov.ipynb` | the Branch-A 3-cell Colab notebook (CONFIG / SETUP / RUN) | — |
| `analysis/` | the stable-AC **benchmark**: difficulty ladder + reach tier + the combined (solved+unsolved) sets | [→](analysis/README.md) |
| `equivalence_classes/` | proves the 261 unsolved reps are **126 distinct problems**, with certificates | [→](equivalence_classes/README.md) |
| `lessons/` | 38 write-ups of bugs that shipped. Read via the index, not by browsing. | [→](lessons/README.md) |

## Tests

```bash
.venv/bin/python3 -m pytest experiments/greedy_tests -q            # after ANY pipeline change
.venv/bin/python3 -m pytest experiments/greedy_tests -q --runslow  # before any push or result claim
.venv/bin/python3 -m pytest experiments/equivalence_classes -q     # after any equivalence change
```

A bare `pytest` collects all three suites plus `tests/` (see `pytest.ini`).

**A green default tier says nothing about what it skipped** — `--runslow` carries the multiprocessing
path, the golden regressions, and the deep parity matrix. Never push behind a default-tier green.

## Two rules that bite

**Never run a search above a `node_budget` of 1,000 locally.** A search at budget `B` is exactly the
first `B` pops of any longer search, so a bigger budget buys a slower repro, never a different
behaviour. Production budgets are the user's, on Colab.

**Never modify the solvers or the runner casually.** `search/`, `run_baseline.py`, and the notebook
are the live pipeline; `results/greedy_baseline/` is its resume contract. See
[`CLAUDE.md`](CLAUDE.md) for the file→lesson map — each entry is a bug that already shipped once.
