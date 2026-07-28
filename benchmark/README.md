# `benchmark/` — the frozen evaluation set

What every technique in this repo is scored on. It is **derived** from `results/greedy_baseline/` but used as an **input** everywhere else, which is why it lives beside `data/` rather than under `results/`.

| path | what it is |
|---|---|
| `difficulty_bins.csv` | all 640 presentations labelled with a log-width difficulty bin, `difficulty_rank`, Aut class, and the 50k columns |
| `subsets/` | the efficiency ladder — `benchmark_subset_{10,20,40,60}`, solved rows, minimally automorphic, stratified across all ten bins |
| `reach/` | the unsolved tier — `reach_tier_{1,2,4,6}`, open problems scored on `min_total` against each row's `bar_to_beat`, never on a solve |
| `combined/` | what a technique actually runs on: `benchmark_combined_{11,22,44,66}` = subset_10+reach_1 … subset_60+reach_6 |

Ladder rows carry `source: "ladder"` and score speedup ratios. Reach rows carry `source: "reach"` and never enter a ratio.

## What each technique costs on it

[`subsets/ARMS.md`](subsets/ARMS.md) + `subsets/benchmark_subset_{N}_arms.{csv,json}` give the other half of the picture: per presentation, the **nodes explored** and the **path length** for the baseline greedy, the best change of variables, and the tuned heap ordering (whose formula is stated there). Rows no transformed arm has run on carry `tested = False` with `-1`/`none` rather than a `False` solve flag — untested is not failed. Regenerate with `.venv/bin/python3 -m experiments.analysis.benchmark_arms`.

The `b1k_*` columns add the **combination** at budget 1,000 — best CoV *and* the recommended ordering. Its controlled contrast is against the same transformed start under length-only ordering (same per-row cap, ordering the only difference): **43/60 against 45/60**, gaining 0 rows and losing 2 bin-9 rows. The untransformed arms in that block (29/60 and 43/60) are a reference only — they run at cap 24 while the CoV arms run at 24–46. Unlike the other blocks these arms do **not** all solve, so an unsolved row there carries `nodes = 1,000` and a blank path.

## Regenerating

All four regenerate from the baseline jsonl and the class table, and are checked by regenerating and requiring a zero diff:

```bash
.venv/bin/python3 -m experiments.analysis.difficulty_bins
.venv/bin/python3 -m experiments.analysis.benchmark_subsets
.venv/bin/python3 -m experiments.analysis.reach_tier
.venv/bin/python3 -m experiments.analysis.combined_benchmark
```

Producers live in [`experiments/analysis/`](../experiments/analysis/README.md); `tests/greedy/test_combined_benchmark.py` reads these files as fixtures.

> **These are frozen.** A row's `pres_id` indexes into them, so regenerating them against a different baseline run silently redefines every result keyed on a `pres_id`. `results/stable_ac/nocov/old_benchmark/` exists precisely because that happened once.
