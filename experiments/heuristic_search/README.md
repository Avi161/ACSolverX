# `heuristic_search/` — block/knot heap orderings for the greedy

> **📊 Full write-up, every table and chart:** <https://claude.ai/code/artifact/b9e07614-f290-44cd-807c-2d02e327ec98>
> (sections *A search heuristic*, *The 25 orderings*, *Tuned multi-feature*, *What it costs*)

**The question.** The baseline greedy orders its open set by total length alone. The block analysis in [`../clustering/`](../clustering/README.md) found that *knot count* and *block thickness* separate solved from unsolved presentations. Do they make a better search priority at a fixed node budget?

**The answer.** Yes, and substantially. A tuned linear blend takes subset-60 from **17/60 to 30/60 at budget 100** and **29/60 to 43/60 at budget 1,000** — never losing a presentation at any budget, using under a third of the nodes, at equal or shorter path length.

## Layout

| dir | n | role |
|---|---|---|
| `core/` | 7 | The reusable library, and the only subpackage the others import. `hsearch.py` holds `HeuristicSolver` (it subclasses `GreedyBaselineSolver` and replaces **only** the priority expression) plus the `PRIORITIES` registry of 25 orderings; `hlab.py` is the lab harness every experiment imports (benchmark, splits, `phi` features, the `RESULTS`/`LOGS`/`SPLITS` output roots); `hfast.py`, `hsolve.py`, `hcompact.py` are the numba solvers; `lab.py`, `perbin.py` the shared reporting. |
| `exp/` | 27 | The numbered experiment log, `exp01_mrl` … `exp27_retune_fresh` — one question per file, run once. Read these for *why* a knob is set the way it is. Five of them (`exp02`, `exp03`, `exp04`, `exp05`, `exp26`) are imported by later experiments, so they are library and log at once. |
| `splits/` | 3 | The split freezers. They write the frozen train/test/reach partitions to `results/heuristic_search/splits/`; re-running one silently invalidates every held-out number reported against the old split. |
| `verify/` | 4 | Cross-checks that one implementation reproduces another (`verify_fast`, `verify_hcompact`, `verify_hsolve`, `verify_keep_path`) — the correctness net under the fast solvers. |
| `runners/` | 10 | The entry points you actually invoke: `tune_multi` (**the headline result**), `run_sweep` (the 25-arm sweep at 100/200/500 with the tune / exploratory / confirm protocol), `run_top2_1000`, `run_ab`, `cost_profile` (nodes + path length, because solve rate alone cannot say an ordering is *better*), `three_way_b10k`, `cov_heur_b1k` (the transform × ordering 2×2 at budget 1,000), `measure_memory`, `synthesize`, `gen_page`. |
| `hsearch_ab.ipynb` | 1 | The Colab notebook for the scaled A/B campaign — CONFIG / SETUP / RUN over `runners/run_ab.py`. |

Outputs: [`results/heuristic_search/`](../../results/heuristic_search/README.md) (`sweep.json`, `top2_1000.json`, `tune_multi.json`, `cost_profile.json`).

```bash
.venv/bin/python3 -m experiments.heuristic_search.runners.tune_multi     # the headline (~2 min)
.venv/bin/python3 -m experiments.heuristic_search.runners.cost_profile   # nodes + path
.venv/bin/python3 -m pytest tests/heuristic_search -q --runslow
```

## Before you change anything here

- **The control gate is the foundation.** `PRIORITIES["length"]` and `tune_multi.BASELINE` must reproduce `greedy_search` **pop for pop** — same solved flag *and* same `nodes_explored` on every presentation. Not "scores the same": *is* the same search. Both are asserted in `tests/heuristic_search/test_hsearch.py`, and no number in this directory is interpretable if either fails.
- **Keep the baseline inside the tuner's search space.** The all-zero weight vector is in the candidate pool on purpose. A space that cannot express "no change" will always appear to beat the control.
- **Never raise a budget above 1,000** ([why](../lessons/local-run-budget-cap.md)). A search at budget `B` is exactly the first `B` pops of a longer one, so a bigger budget buys a slower repro, never different behaviour. Production budgets are the user's, on Colab.
- **A priority may return tuples of different lengths, but the first element must be an int** wherever two shapes can meet — the endgame switch emits `(0, L)` and `(1, ...)`, and without the leading int heapq compares an int against a tuple and raises mid-search.
- **Compare nodes as a MEAN, never a sum.** Each arm's both-solved set has its own size, so a sum ranks an arm that solves less as cheaper. This picked the wrong pre-registered winner once (537 over 8 "beat" 582 over 9; the means are 67.1 vs 64.7).
- **The substitution move still requires a cancelling seam** (`../search/greedy_baseline.py:220`). Dropping that changes the branching factor *and* the ordering at once; it is a separate experiment, not a knob to turn mid-run.
- **Most files here resolve the repo root by counting `os.path.dirname` levels from `__file__`, so moving one between these subdirectories breaks it silently** — the chain encodes the file's depth, and a wrong root does not raise, it just reads and writes under the wrong directory. Only `core/hlab.py`, `core/hsearch.py`, `runners/three_way_b10k.py` and `runners/cov_heur_b1k.py` use the walk-up idiom the rest of `experiments/` is supposed to use. Convert a file to the walk-up when you touch it, and re-check the count if you move one.

## What surprised us

`smaller mean block` is the **strongest classifier** of solved vs unsolved (AUC 0.912) and the **weakest single search priority** — it flatlines to +0 at budget 1,000. Knots are the reverse: chance-level as a classifier under the provenance control, best single heuristic by a clear margin. Yet in the tuned blend `smaller mean block` carries the **largest weight**. Testing features one at a time would have discarded it.

A classifier is scored on the start state ("does this look hard?"); a heap priority is scored on its gradient across the search ("does moving this way help?"). Those are different questions and this directory is the evidence that they have different answers.
