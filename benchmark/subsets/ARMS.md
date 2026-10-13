# Best-known cost per presentation, per technique

**TL;DR.** `benchmark_subset_{10,20,40,60}_arms.{csv,json}` give, per presentation, what each technique costs to solve
it (**nodes explored**) and the **path length** found. On subset 60 all three arms solve 60/60, but at their own
different budgets and caps; at the **matched budget of 10,000 nodes and cap 24** the counts are greedy **40/60**, best
CoV **52/60** (an oracle) and the withdrawn heuristic **47/60**. These are run outputs from a research branch
(`experiments/analysis/benchmark_arms.py`, on search logs not in this repository); nothing here regenerates them. The
frozen `benchmark_subset_{N}.{csv,json}` are untouched.

## Not every row has been tested

The four subsets are *not* nested (`nested: false` in each `benchmark_subset_<N>.json`), and the CoV and heuristic
sweeps ran on **subset 60's** rows only:

| subset | rows | tested | not tested |
|---|---|---|---|
| **subset-10** | 10 | 4 | 6 |
| **subset-20** | 20 | 18 | 2 |
| **subset-40** | 40 | 25 | 15 |
| **subset-60** | 60 | 60 | — |

A not-tested row has `tested = False`, `-1` in every numeric arm column and `none` in every string one, `*_solved`
included. **`none` is not `False`**: it means "not run", not "ran and failed", and every summary counts only `tested`
rows. The `greedy_*` columns are filled on every row (from the baseline's 10⁶-node run, where all 640 solve).

## The heuristic (withdrawn)

The baseline greedy with only the priority replaced:

```
priority(r1, r2) = L + 2.53*K + 6.418*MK + 8.458*S + 3.292*xyimb   (one segment, no length threshold)
```

| term | weight | what it measures |
|---|---|---|
| `L` | 1.0 | total length \|r1\| + \|r2\| -- the baseline greedy's entire ordering |
| `K` | 2.53 | knot sum knots(r1) + knots(r2), where knots(w) = 0 for a pure power, else max(#x-blocks, #y-blocks) read cyclically |
| `MK` | 6.418 | max knots over the two relators |
| `S` | 8.458 | smaller mean block -- the mean run length of the thinner generator |
| `xyimb` | 3.292 | generator imbalance \|#x - #y\| / L, scale-free |

Lower pops first; every term is a pure, rotation-invariant function of the state. `RECOMMENDED` shipped with the
original code (`experiments/search/heuristics.py`) and is **withdrawn as overfit** here: no code, see
[docs/RESULTS.md](../../docs/RESULTS.md) ("Tried"). Its numbers below are kept as recorded.

## Columns

| prefix | technique | budget (nodes) | cap | source |
|---|---|---|---|---|
| `greedy_*` | baseline greedy, best known | 1,000,000 | 24 | `benchmark_subset_60.json`, columns `nodes_1M` / `path_1M` |
| `bestcov_*` | best change of variables over the whole subword family | 20,000 | 24 | CoV sweep, research branch |
| `heur_*` | the heuristic above | 100,000 | 48 | EXP-28 scale run, `arm=recommended`, research branch |
| `m10k_*` | **matched**: all three arms | 10,000 | 24 | its builder refuses to write unless its length-only control reproduces plain greedy pop for pop on all 60 rows |

> ⚠ **The first three ran at different budgets and caps**: never read a ratio across them. A head-to-head claim
> belongs in the matched `m10k_*` block.

`bestcov_z` is the change of variables that won and `bestcov_class` how it acts (`relabel` = a pure renaming, most of
them; a rename is not a no-op, because greedy reads strings, not orbits).

## What the numbers say

Subset 60, each arm at its own budget and cap. **Read the median**: second-hump rows dominate the mean (greedy: mean
45,244 against median 1,310, a 35× skew).

| arm | solved | median nodes | mean nodes | median path | mean path |
|---|---|---|---|---|---|
| greedy @ 1,000,000, cap 24 | 60/60 | 1,310.5 | 45,244.2 | 46.5 | 142.62 |
| best CoV @ ≤20,000, cap 24 | 60/60 | 34.5 | 2,383.1 | 16.5 | 97.05 |
| heuristic @ 100,000, cap 48 | 60/60 | 226.5 | 10,244.0 | 38.0 | 102.73 |

Both transformed arms cost **less** than greedy on the same rows and return **shorter** derivations. At the matched
10,000 nodes and cap 24: greedy **40/60**, best CoV **52/60**, heuristic **47/60**.

> The best-CoV column is an **oracle**: 2,383 mean nodes is what the winning `z` costs *once you know which `z` wins*;
> finding it cost ~2.2M nodes per presentation of sweeping. It bounds a transformed route from below and is not a
> runnable procedure. The heuristic is one search with one fixed ordering.
