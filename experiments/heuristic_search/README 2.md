# `heuristic_search/` — block/knot heap orderings for the greedy

> **📊 Full write-up, every table and chart:** <https://claude.ai/code/artifact/b9e07614-f290-44cd-807c-2d02e327ec98>
> (sections *A search heuristic*, *The 25 orderings*, *Tuned multi-feature*, *What it costs*)

**The question.** The baseline greedy orders its open set by total length alone. The block analysis in [`../clustering/`](../clustering/README.md) found that *knot count* and *block thickness* separate solved from unsolved presentations. Do they make a better search priority at a fixed node budget?

**The answer.** Yes, and substantially. A tuned linear blend takes subset-60 from **17/60 to 30/60 at budget 100** and **29/60 to 43/60 at budget 1,000** — never losing a presentation at any budget, using under a third of the nodes, at equal or shorter path length.

## Files

| file | role |
|---|---|
| `hsearch.py` | the solver: `HeuristicSolver` subclasses `GreedyBaselineSolver` and replaces **only** the priority expression. Block features (`blocks`, `feats`) and the `PRIORITIES` registry of 25 orderings live here. |
| `run_sweep.py` | the 25-arm sweep at 100/200/500 over the frozen benchmark subsets, with the tune / exploratory / confirm split protocol and paired sign tests. |
| `run_top2_1000.py` | the best arms against the baseline at the 1,000-node ceiling on subset-20. |
| `tune_multi.py` | tunes `(T, a_knots, a_maxknots, a_smb)` by random search on bin-stratified halves of subset-60, scoring the winner on the held-out half. **This is the headline result.** |
| `cost_profile.py` | nodes explored and path length — solve rate alone cannot say an ordering is *better*. |

Outputs: [`results/heuristic_search/`](../../results/heuristic_search/README.md) (`sweep.json`, `top2_1000.json`, `tune_multi.json`, `cost_profile.json`).

```bash
.venv/bin/python3 -m experiments.heuristic_search.tune_multi        # the headline (~2 min)
.venv/bin/python3 -m experiments.heuristic_search.cost_profile      # nodes + path
.venv/bin/python3 -m pytest tests/heuristic_search -q --runslow     # 15 tests
```

## Before you change anything here

- **The control gate is the foundation.** `PRIORITIES["length"]` and `tune_multi.BASELINE` must reproduce `greedy_search` **pop for pop** — same solved flag *and* same `nodes_explored` on every presentation. Not "scores the same": *is* the same search. Both are asserted in `tests/heuristic_search/test_hsearch.py`, and no number in this directory is interpretable if either fails.
- **Keep the baseline inside the tuner's search space.** The all-zero weight vector is in the candidate pool on purpose. A space that cannot express "no change" will always appear to beat the control.
- **Never raise a budget above 1,000** ([why](../lessons/local-run-budget-cap.md)). A search at budget `B` is exactly the first `B` pops of a longer one, so a bigger budget buys a slower repro, never different behaviour. Production budgets are the user's, on Colab.
- **A priority may return tuples of different lengths, but the first element must be an int** wherever two shapes can meet — the endgame switch emits `(0, L)` and `(1, ...)`, and without the leading int heapq compares an int against a tuple and raises mid-search.
- **Compare nodes as a MEAN, never a sum.** Each arm's both-solved set has its own size, so a sum ranks an arm that solves less as cheaper. This picked the wrong pre-registered winner once (537 over 8 "beat" 582 over 9; the means are 67.1 vs 64.7).
- **The substitution move still requires a cancelling seam** (`../search/greedy_baseline.py:220`). Dropping that changes the branching factor *and* the ordering at once; it is a separate experiment, not a knob to turn mid-run.

## What surprised us

`smaller mean block` is the **strongest classifier** of solved vs unsolved (AUC 0.912) and the **weakest single search priority** — it flatlines to +0 at budget 1,000. Knots are the reverse: chance-level as a classifier under the provenance control, best single heuristic by a clear margin. Yet in the tuned blend `smaller mean block` carries the **largest weight**. Testing features one at a time would have discarded it.

A classifier is scored on the start state ("does this look hard?"); a heap priority is scored on its gradient across the search ("does moving this way help?"). Those are different questions and this directory is the evidence that they have different answers.
