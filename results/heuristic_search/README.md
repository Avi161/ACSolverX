# `results/heuristic_search/`

Everything the heap-ordering work produced. Two programs ran here, in order: a **sweep** of hand-written orderings (17/60 → 30/60 at budget 100), then a 28-experiment **hyperparameter program** over a config-driven ordering space.

**Start at [`BEST_HEURISTIC.md`](BEST_HEURISTIC.md)** — the ordering to actually use. Everything else is the evidence behind it.

| path | what it holds |
|---|---|
| [`BEST_HEURISTIC.md`](BEST_HEURISTIC.md) | ⭐ the recommendation, by nodes and by solves |
| [`FINDINGS.md`](FINDINGS.md) | the winner on the automorphism-disjoint split, per budget, overfit priced |
| [`SCALE_RUN_PLAN.md`](SCALE_RUN_PLAN.md) | the 10⁶-node Colab campaign over the 124 unsolved classes |
| [`HCOMPACT.md`](HCOMPACT.md) | the tuned ordering on the packed arena — same search, less memory |
| [`runs/`](runs/README.md) | the EXP-01…EXP-28 program: one `.jsonl` of raw rows + one `.md` report per experiment |
| `splits/` | the frozen evaluation splits — written once, thereafter read-only |
| [`sweep/`](sweep/README.md) | the earlier ordering sweep: `sweep.json`, `top2_1000.json`, `tune_multi.json`, `cost_profile.json` |
| `synthesis.json`, `hyper.json`, `verify_fast.json` | machine-readable summaries, read by `gen_page.py` and `exp10_refine.py` |

Producers live in [`experiments/heuristic_search/`](../../experiments/heuristic_search/README.md).

## Why `splits/` is its own directory

`splits.json` (difficulty-stratified) and `splits_aut.json` (automorphism-disjoint) partition the same 66 rows differently, and `splits_ms640.json` is a third slice the program had never read. They are **inputs to selection**, not outputs of it: regenerating one silently changes what "held out" means for every number under `runs/`. Their own directory is what makes "written once, never regenerated" visible.

State any published number as a **pair** — selected on X, evaluated on Y. "Held out" alone is ambiguous once a project has two splits ([why](../../experiments/lessons/held-out-means-held-out-from-selection.md)).

> This directory used to be `tests/heuristic_search/logs/` — 81 result files inside the test tree. `tests/heuristic_search/` now holds only its six test modules.
