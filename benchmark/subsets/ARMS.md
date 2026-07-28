# Best-known cost per presentation, per technique

`benchmark_subset_{10,20,40,60}_arms.{csv,json}` give one row per presentation: what each technique costs to solve it, in **nodes explored** and the **path length** that came with those nodes. Produced by `experiments/analysis/benchmark_arms.py`; the frozen `benchmark_subset_{N}.{csv,json}` are untouched.

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

Shipped as `RECOMMENDED` in `experiments/heuristic_search/core/hsolve.py`; the producer asserts these weights against it, so the two cannot drift apart.

## Columns

**Best known** — each arm at its own budget and cap. This is what a row costs in practice.

| prefix | technique | budget | cap | source |
|---|---|---|---|---|
| `greedy_*` | baseline greedy, best known | 1,000,000 | 24 | `benchmark/subsets/benchmark_subset_60.json (nodes_1M / path_1M)` |
| `bestcov_*` | best change of variables over the whole subword family | 20,000 | 24 | `results/comparison/greedy_vs_bestcov_subset60_nodes_path.csv` |
| `heur_*` | recommended heap ordering (formula above) | 100,000 | 48 | `results/heuristic_search/runs/EXP28_colab_scale.jsonl, arm=recommended` |

> ⚠ **The three ran at different budgets and different relator caps.** Never read a ratio across them — a CoV row compared against a control at a different `max_relator_length` is not a comparison. Use the matched block for that.

**Matched** — `m10k_*`, all three arms at budget 10,000 and cap 24, from `results/comparison/three_way_b10k_subset60.csv`, whose builder refuses to write unless its length-only control reproduces the plain greedy pop for pop on all 60 rows. A head-to-head claim belongs here.

`bestcov_z` is the change of variables that produced the win and `bestcov_class` how it acts (`relabel` = a pure renaming, which is most of them — a rename is not a no-op, because the greedy reads strings, not orbits).

**Combined** — `b1k_*`, the 2×2 of *transform the start* × *change the ordering*, every arm one search at budget 1,000, from `results/comparison/cov_heur_b1k_subset60.csv`. It is the only block whose arms do **not** all solve: an unsolved row there carries `nodes = 1,000` and a blank path, so never take a mean across it. Read it in the section below.

## What the numbers say

On subset-60 all three arms solve **60/60**, so every row below is a like-for-like row. **Read the median, not the mean** — both are given because the mean is dominated by a handful of second-hump rows (greedy: mean 45,244 against a median of 1,310, a 35× skew).

| arm | solved | median nodes | mean nodes | median path | mean path |
|---|---|---|---|---|---|
| greedy @ 1,000,000, cap 24 | 60/60 | 1,310 | 45,244 | 46 | 142.62 |
| best CoV @ ≤20,000, cap 24 | 60/60 | 34 | 2,383 | 16 | 97.05 |
| heuristic @ 100,000, cap 48 | 60/60 | 226 | 10,244 | 38 | 102.73 |

Both transformed arms cost **less** than the untransformed greedy on the same rows, and return **shorter** derivations — path length is not being traded for reach.

At the matched budget of 10,000 and cap 24, the solve counts are greedy **40/60**, best CoV **52/60**, heuristic **47/60**. That is the controlled comparison; the table above is best-known cost, where each arm ran at a different budget.

> The best-CoV column is an **oracle**: 2,383 median nodes is what the winning `z` costs *once you know which `z` wins*, and finding it cost ~2.2M nodes per presentation of sweeping. It is a lower bound on a transformed route, not a runnable procedure ([why that distinction matters](../../experiments/lessons/price-the-untransformed-route.md)). The heuristic column has no such caveat — it is one search, with one fixed ordering.

## Combining them: transform × ordering at budget 1,000

`b1k_covheur_*` is the combination the CoV work and the heuristic work each point at: singly destabilise with the winning `z` (`bestcov_z`), then search the transformed pair with the recommended ordering. Every arm here is **one** search at budget 1,000.

**The comparison that is controlled** — `b1k_covheur_*` against `b1k_covgreedy_*`: same transformed start, same per-row cap, the ordering is the only difference.

| arm on the best-CoV start | solved | gained | lost |
|---|---|---|---|
| length-only ordering (`b1k_covgreedy_*`) | 45/60 | — | — |
| recommended ordering (`b1k_covheur_*`) | **43/60** | 0 | 2 |

**The ordering does not add to the transform.** It gains **0** rows and loses **2** (634 (bin 9), 635 (bin 9)): the solved sets are nested, covheur ⊂ covgreedy. The union of all four `b1k_*` arms is 45/60 — nothing anywhere in the block reaches a row the transform alone misses.

On the 43 rows both CoV arms solve it is not paying for those losses in nodes: the medians tie at 15 nodes and the mean nearly halves, 49.3 against 88.6 — cheaper on 19 rows, equal on 13, dearer on 11. What the ordering costs on this start is reach at the hard end, not nodes on the rows it reaches.

**Reference, not a matched comparison** — the same two orderings on the *untransformed* pair are `b1k_greedy_*` 29/60 and `b1k_heur_*` 43/60. Do not read those against the CoV row as a clean 2×2: a CoV lengthens relators, so a transformed arm runs at `b1k_cov_cap` = longest + 16 (24–46 on these rows) while an untransformed one runs at 24, and [a CoV row compared against a control at a different `max_relator_length` is not a comparison](../../experiments/lessons/control-with-no-dynamic-range.md). The cap is carried per row so the confound stays visible.

> Two caveats the controlled contrast cannot shed. **The `z` is a doubly-selected oracle**: it is the cheapest of ~80–174 subword CoVs (~2.2M nodes per presentation to find) *and* it was ranked by what **length-only** ordering cost at ≤20,000 nodes. So `b1k_covheur_*` runs the recommended ordering from a start chosen to suit the other ordering, which is not a clean measurement of either. **And on 29 of the 60 rows more than one transformed start ties for cheapest** (`b1k_cov_n_tied_starts`); the winner is a first-seen tie-break, so on those rows the transformed pair is arbitrary among starts that are equally cheap *for length-only ordering*. The 2 lost rows are not among them — each has a unique cheapest CoV start, so the tie-break did not choose their start for them.
