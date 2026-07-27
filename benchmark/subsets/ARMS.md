# Best-known cost per presentation, per technique

`benchmark_subset_{10,20,40,60}_arms.{csv,json}` give one row per presentation: what each technique costs to solve it, in **nodes explored** and the **path length** that came with those nodes. The frozen `benchmark_subset_{N}.{csv,json}` are untouched.

These are run outputs, generated on the research branch by `experiments/analysis/benchmark_arms.py` from search logs that are not part of this repo. They ship here as data; nothing on `main` regenerates them.

## Not every row has been tested

The four subsets are *not* nested (`nested: false` in each file), and both the CoV sweep and the heuristic campaign were run against **subset-60's** row list. So the smaller subsets contain presentations no transformed arm has ever run on:

| subset | rows | tested | not tested |
|---|---|---|---|
| **subset-10** | 10 | 4 | 6 |
| **subset-20** | 20 | 18 | 2 |
| **subset-40** | 40 | 25 | 15 |
| **subset-60** | 60 | 60 | — |

A not-tested row carries `tested = False`, `-1` in every numeric arm column and `none` in every string one — including `*_solved`. **`none` is not `False`.** A blank or a `False` there would read as "we ran it and it did not solve", which is a far stronger claim than "we have not run it"; every summary below counts only `tested` rows, because scoring an untested row as a failure would understate the transformed arms on exactly the subsets they were never run on.

The `greedy_*` columns are populated on **every** row of every subset — they come from the baseline's own 10⁶-node run, where all 640 presentations solve.

## The heuristic

The recommended heap ordering — the baseline greedy with **only** the priority expression replaced, so any difference is attributable to the ordering and nothing else:

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

Lower is popped first. Every term is a pure function of the state and rotation-invariant — a priority reading `depth` or the parent would make pop order depend on discovery order and stop being reproducible. It is a **single segment with no length threshold**: the earlier phased form is unnecessary here, because `S` and `MK` both fall as a pair approaches the trivial state, so the climb self-regulates.

Shipped as `RECOMMENDED` in [`experiments/search/heuristics.py`](../../experiments/search/heuristics.py), documented in [`HEURISTICS.md`](../../experiments/search/HEURISTICS.md), and pinned by `test_recommended_is_the_formula_the_docs_publish` in [`tests/test_greedy_heuristic.py`](../../tests/test_greedy_heuristic.py) — the weights above and the code cannot drift apart.

## Columns

**Best known** — each arm at its own budget and cap. This is what a row costs in practice.

| prefix | technique | budget | cap | source |
|---|---|---|---|---|
| `greedy_*` | baseline greedy, best known | 1,000,000 | 24 | `benchmark_subset_60.json`, columns `nodes_1M` / `path_1M` |
| `bestcov_*` | best change of variables over the whole subword family | 20,000 | 24 | CoV sweep, research branch |
| `heur_*` | recommended heap ordering (formula above) | 100,000 | 48 | EXP-28 scale run, `arm=recommended`, research branch |

> ⚠ **The three ran at different budgets and different relator caps.** Never read a ratio across them — a CoV row compared against a control at a different `max_relator_length` is not a comparison. Use the matched block for that.

**Matched** — `m10k_*`, all three arms at budget 10,000 and cap 24. Its builder refuses to write unless its length-only control reproduces the plain greedy pop for pop on all 60 rows. A head-to-head claim belongs here.

`bestcov_z` is the change of variables that produced the win and `bestcov_class` how it acts (`relabel` = a pure renaming, which is most of them — a rename is not a no-op, because the greedy reads strings, not orbits).

## What the numbers say

All three arms solve subset-60 **60/60**. **Read the median, not the mean** — the mean is dominated by a handful of second-hump rows (greedy: mean 45,244 against a median of 1,310, a 35× skew).

| arm | solved | median nodes | mean nodes | median path | mean path |
|---|---|---|---|---|---|
| greedy @ 1,000,000, cap 24 | 60/60 | 1,310.5 | 45,244.2 | 46.5 | 142.62 |
| best CoV @ ≤20,000, cap 24 | 60/60 | 34.5 | 2,383.1 | 16.5 | 97.05 |
| heuristic @ 100,000, cap 48 | 60/60 | 226.5 | 10,244.0 | 38.0 | 102.73 |

Both transformed arms cost **less** than the untransformed greedy on the same rows, and return **shorter** derivations — path length is not being traded for reach.

At the matched budget of 10,000 and cap 24, the solve counts are greedy **40/60**, best CoV **52/60**, heuristic **47/60**. That is the controlled comparison; the table above is best-known cost, where each arm ran at a different budget.

> The best-CoV column is an **oracle**: 2,383 median nodes is what the winning `z` costs *once you know which `z` wins*, and finding it cost ~2.2M nodes per presentation of sweeping. It is a lower bound on a transformed route, not a runnable procedure. The heuristic column has no such caveat — it is one search, with one fixed ordering.
