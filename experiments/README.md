# `experiments/`

All experiment code. **CPU + numba only** on this branch — no JAX, no GPU, no PPO. The JAX stack at
the repo root (`envs/`, `network.py`, `ppo_ac_s.py`) is a *spec to port from, never to import*.

| directory / file | what it is | its README |
|---|---|---|
| `search/` | **the solvers.** `greedy_baseline.py` (heavy: bool arrays + dict) and `greedy_compact.py` (nibble arena + int32 heap, ~3× smaller, **pops identically**) | — |
| `run_baseline.py` | the runner: jsonl, resume, memory guard, multiprocessing, W&B | — |
| `wandb_tracking.py` | W&B run identity, panels, live metrics | — |
| `notebooks/` | every Colab notebook in the repo, consolidated — `greedy_baseline.ipynb` (the 3-cell CONFIG / SETUP / RUN pattern), `hsearch_ab.ipynb`, and `stable_ac/` (`cov_baseline.ipynb`, `mu_ladder_big.ipynb`, `nb2_big_ladder.ipynb`, `stable_ac_nocov.ipynb`) | [→](notebooks/README.md) |
| `greedy_tests/` | the test **SUPPORT** code (production imports it too, which is why it is not under `tests/`) — a general-`n` spec, an invariant the solver never computes, and a `SolverAdapter` seam the stable-AC port plugs into. The tests themselves are in [`tests/`](../tests/README.md) | [→](greedy_tests/README.md) |
| `stable_ac/` | the **stable-AC umbrella**. Shared core at the top level: `solvern.py` (general-`n` numba solver, spec-trace-equal at `n_gen≤3`) + `word_families.py` (A1/A2/A3). One self-contained folder per pipeline — `nocov/` (**Branch A**: runner + yaml) and `cov/` (**Branch B**, one-shot change of variables: transform + runner + yaml); both are tested in [`tests/stable_ac/`](../tests/README.md) and driven from `notebooks/stable_ac/` | [→](stable_ac/README.md) |
| `analysis/` | builds the frozen **benchmark** at [`benchmark/`](../benchmark/README.md) (difficulty ladder + reach tier + combined) and `benchmark_arms.py`, what each technique costs on it | [→](analysis/README.md) |
| `equivalence_classes/` | proves the 261 unsolved reps are **124 distinct problems**, with certificates | [→](equivalence_classes/README.md) |
| `clustering/` | **unsupervised** clustering of the 237 minimal automorphic states — does their shape know what is solved? | [→](clustering/README.md) |
| `heuristic_search/` | block/knot **heap orderings** for the greedy. Same moves, same budget, different priority: **17/60 → 30/60** at budget 100. `core/` `exp/` `runners/` `verify/` `splits/` `figures/` | [→](heuristic_search/README.md) |
| `lessons/` | 68 write-ups of bugs that shipped. Read via the index, not by browsing. | [→](lessons/README.md) |

## Tests

```bash
.venv/bin/python3 -m pytest tests/greedy tests/stable_ac tests/analysis -q               # after ANY pipeline change
.venv/bin/python3 -m pytest tests/greedy tests/stable_ac tests/analysis -q --runslow     # before any push or result claim
.venv/bin/python3 -m pytest tests/equivalence_classes -q                                 # after any equivalence change
```

All suites live under the root `tests/` (nested by area); a bare `pytest` collects them all (see
`pytest.ini`). The stable-AC solver core (`solvern.py`, `word_families.py`) is tested in `tests/stable_ac/`
(spec parity needs the spec, which stays under `experiments/greedy_tests/`);
every suite now lives under `tests/`, nested by area — nothing test-shaped remains under `experiments/`, and nothing results-shaped remains under `tests/`.

**A green default tier says nothing about what it skipped** — `--runslow` carries the multiprocessing
path, the golden regressions, and the deep parity matrix. Never push behind a default-tier green.

## Two rules that bite

**Never run a search above a `node_budget` of 1,000 locally.** A search at budget `B` is exactly the
first `B` pops of any longer search, so a bigger budget buys a slower repro, never a different
behaviour. Production budgets are the user's, on Colab.

**Never modify the solvers or the runner casually.** `search/`, `run_baseline.py`, and the notebook
are the live pipeline; `results/greedy_baseline/` is its resume contract. See
[`CLAUDE.md`](CLAUDE.md) for the file→lesson map — each entry is a bug that already shipped once.
