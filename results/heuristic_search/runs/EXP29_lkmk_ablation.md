# EXP-29 — how much of RECOMMENDED is already in L, K and MK?

A controlled ablation on the frozen 60-row benchmark: one `hcompact` search per presentation at budget 1,000, cap 48. The ablation keeps the shipped coefficients `L + 2.53K + 6.418MK` and removes only `S` and `xyimb`; it is not re-tuned. Baseline and full RECOMMENDED are exact budget-1,000 checkpoints derived from `EXP28_colab_scale.jsonl` by `solved_at`, not new searches.

## Solve count

| arm | solved | bins 0–3 | bin 4 | bin 5 | bin 6 | bin 7 | bins 8–9 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Greedy baseline | **29/60** | 24/24 | 5/6 | 0/6 | 0/6 | 0/6 | 0/12 |
| Full RECOMMENDED | **43/60** | 24/24 | 6/6 | 6/6 | 5/6 | 2/6 | 0/12 |
| L + 2.53K + 6.418MK | **36/60** | 24/24 | 3/6 | 4/6 | 3/6 | 2/6 | 0/12 |

## Descriptive cost on each arm's own solved rows

These denominators differ and therefore describe each arm separately; they are not a head-to-head cost comparison. Unsolved rows are excluded because their `nodes_explored = 1,000` is censoring, not solution cost.

| arm | denominator | nodes mean | nodes median | path mean | path median |
|---|---:|---:|---:|---:|---:|
| Greedy baseline | 29 solved | 175.5 | 61 | 19.2 | 16 |
| Full RECOMMENDED | 43 solved | 214.7 | 106 | 33.0 | 25 |
| L + 2.53K + 6.418MK | 36 solved | 258.0 | 194.5 | 30.6 | 21.5 |

## Matched cost on the rows all three solve

All values below use the same **27 presentations**. This is the apples-to-apples comparison used in the figure.

| arm | denominator | nodes mean | nodes median | path mean | path median |
|---|---:|---:|---:|---:|---:|
| Greedy baseline | 27 shared solves | 143.4 | 57 | 17.9 | 15 |
| Full RECOMMENDED | 27 shared solves | 75.5 | 49 | 18.4 | 18 |
| L + 2.53K + 6.418MK | 27 shared solves | 184.6 | 183 | 18.2 | 17 |

## Provenance and checks

- New search: `EXP29_lkmk_bench66_b1000_mrl48.jsonl`, `hcompact`, `L=1; K=2.53; MK=6.418`, 60 rows.
- Reused searches: `EXP28_colab_scale.jsonl`, arms `baseline` and `recommended`, source budget 100,000/cap 48; the deterministic prefix property makes `solved_at <= 1,000` the exact budget-1,000 result.
- L/K/MK unsolved rows that exhausted the frontier before node 1,000: none.
- Raw row-level comparison: `EXP29_lkmk_ablation.csv`; figure: `EXP29_lkmk_ablation.png`.
