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
| `stable_ac/` | the **stable-AC umbrella**. Shared core at the top level: `solvern.py` (general-`n` numba solver, spec-trace-equal at `n_gen≤3`) + `word_families.py` (A1/A2/A3). One self-contained folder per pipeline — `nocov/` (**Branch A**: runner + yaml + notebook + tests) and `cov/` (**Branch B**, one-shot change of variables: transform + runner + yaml + notebook + tests) | [→](stable_ac/README.md) |
| `analysis/` | the stable-AC **benchmark**: difficulty ladder + reach tier + the combined (solved+unsolved) sets | [→](analysis/README.md) |
| `equivalence_classes/` | proves the 261 unsolved reps are **124 distinct problems**, with certificates | [→](equivalence_classes/README.md) |
| `lessons/` | 38 write-ups of bugs that shipped. Read via the index, not by browsing. | [→](lessons/README.md) |

## Tests

```bash
.venv/bin/python3 -m pytest experiments/greedy_tests -q            # after ANY pipeline change
.venv/bin/python3 -m pytest experiments/greedy_tests -q --runslow  # before any push or result claim
.venv/bin/python3 -m pytest experiments/stable_ac -q               # after any stable_ac pipeline change
.venv/bin/python3 -m pytest experiments/equivalence_classes -q     # after any equivalence change
```

A bare `pytest` collects all four suites plus `tests/` (see `pytest.ini`). The stable-AC solver
core (`solvern.py`, `word_families.py`) is tested in `greedy_tests/` (spec parity needs the spec);
each pipeline's harness tests are colocated in its own folder (`stable_ac/{nocov,cov}/test_*.py`).

**A green default tier says nothing about what it skipped** — `--runslow` carries the multiprocessing
path, the golden regressions, and the deep parity matrix. Never push behind a default-tier green.

## Two rules that bite

**Never run a search above a `node_budget` of 1,000 locally.** A search at budget `B` is exactly the
first `B` pops of any longer search, so a bigger budget buys a slower repro, never a different
behaviour. Production budgets are the user's, on Colab.

**Never modify the solvers or the runner casually.** `search/`, `run_baseline.py`, and the notebook
are the live pipeline; `results/greedy_baseline/` is its resume contract. See
[`CLAUDE.md`](CLAUDE.md) for the file→lesson map — each entry is a bug that already shipped once.
