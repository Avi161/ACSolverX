# The AC19 residue with `s40_gen` un-starved

What happens to the 2,130 orbits the 501-node cascade screen left unsolved
when the `s40_gen` component is given more than its pinned 500 nodes.

Read [the framing section](#what-this-is-and-is-not) before quoting any
number here. Most of these rows were already solved in the archive. The new
thing is **which component solves them and at what cost**, plus four rows of
genuinely new coverage.

## The runs

Both used `experiments/search/run_ac19_cascade_screen.py` and the
`--starter-budget` flag added in `18e57232`. Before that flag the starter
budget was an imported constant, so every rung of the shipped ladder gave
`s40_gen` exactly 500 nodes and handed the extra rope to `s20_mk2`.

| rung | invocation | rows in |
|---|---|---:|
| 1 | `--budget 1000 --starter-budget 1000` | 2,130 |
| 2 | `--budget 100000 --starter-budget 10000` | 1,496 |

Rung 1 sets `budget == starter_budget` on purpose: the `s20_mk2` fallback
gets an allowance of zero and never runs, so whatever solves is `s40_gen`
alone and the attribution is unambiguous.

Cost: rung 2 was 2.43 core-hours, 5.849 s/row, three workers on one 4-core
dev box. No cloud box was used or needed.

## Results

| | rung 1 | rung 2 |
|---|---:|---:|
| rows | 2,130 | 1,496 |
| solved | **634** (29.8%) | **1,488** (99.5%) |
| errors | 0 | 0 |
| `s40_gen` wins | 634, median 667 nodes, max 1,000 | 1,181, median 2,173, max 9,939 |
| `s20_mk2` wins | — (allowance zero) | 307, median 14,091, max 99,180 |

**Combined: 2,122 of 2,130 = 99.62%.** Eight rows survive both, all of them
from the `bench12` hard tail.

`s40_gen`'s rung-2 median of **2,173 nodes** is the number that matters: it
is four times the 500 the shipped ladder allowed it, so these are rows the
component could reach all along and was never given the budget to.

## What this is, and is not

**It is not 2,122 new solves.** The shipped ladder already settled almost
all of these by its 100,000 rung, through the `s20_mk2` fallback, at much
higher cost. Those rung results live in S3, not in this repo, which is part
of why the distinction is easy to lose.

**It is component attribution.** `s40_gen` un-starved wins 1,181 of the
1,488 rung-2 solves — 79% — at a median of 2,173 nodes, on rows the archive
needed the fallback for. That is the efficiency claim, and it is the honest
version of it.

**The genuinely new coverage is twelve rows wide**, and it is enumerated
below rather than folded into a percentage.

## The `bench12` twelve, row by row

These are the rows that survived the whole shipped cascade ladder to
100,000 nodes. `s20_mk2` settled nine of them at the 1,000,000 rung; the
state counts are from [`../bench12/RESULTS.md`](../bench12/RESULTS.md).

| row | states, `s20_mk2` @1M | rung 1 (sb 1k) | rung 2 (sb 10k) | settled by |
|---|---:|---|---|---|
| `ac19_20270` | 34,156,353 | no (1,000) | no (100,000) | `s20_mk2` @1M only |
| `ac19_39288` | 17,674,093 | no (1,000) | no (100,000) | `s20_mk2` @1M only |
| `ac19_43611` | 17,787,805 | no (1,000) | no (100,000) | `s20_mk2` @1M only |
| `ac19_44381` | 36,515,155 | **solved, 985** (`s40_gen`) | — | hybrid |
| `ac19_49095` | 17,264,554 | no (1,000) | no (100,000) | `s20_mk2` @1M only |
| `ac19_51034` | 30,548,444 | no (1,000) | **solved, 4,273** (`s40_gen`) | hybrid |
| `ac19_54616` | 17,053,703 | no (1,000) | no (100,000) | `s20_mk2` @1M only |
| `ac19_54765` | 17,087,592 | no (1,000) | no (100,000) | `s20_mk2` @1M only |
| `ac19_57992` | 34,286,028 | no (1,000) | no (100,000) | `s20_mk2` @1M only |
| `ac19_65206` | 34,051,516 | no (1,000) | no (100,000) | `s20_mk2` @1M only |
| `ac19_65753` | 30,553,423 | no (1,000) | **solved, 4,275** (`s40_gen`) | hybrid |
| `ac19_72328` | 12,916,988 | no (1,000) | **solved, 5,866** (`s40_gen`) | hybrid |

Three things follow, and the second is the one usually left out.

**The three holdouts land exactly where predicted.** `ac19_44381` at 985
against 984 predicted, `ac19_51034` at 4,273 against 4,272, `ac19_65753` at
4,275 against 4,274 -- each one node over, which is the cascade's
normalization step that the bare `mixed_search` prediction did not count.

**The hybrid does not dominate.** Eight of the twelve ran their full budget
here and did not solve, and `s20_mk2` settles every one of them at the
1,000,000 rung. Un-starving `s40_gen` makes it far cheaper on the
overwhelming majority and leaves it strictly worse on part of the tail. Any
summary that quotes the efficiency ratios without this sentence is
misleading.

**`ac19_72328` is a new result.** It was never one of the three known
holdouts -- `s20_mk2` had it at the 1M rung, 12,916,988 states -- and the
un-starved `s40_gen` takes it in **5,866 nodes**. Nobody had pointed this
arm at it above 500.

## The censored comparison

Per-row node counts for `greedy` and `s20_mk2` over the 72,779 exist **only
as failure lists** -- `../ac19_autmin_screen/unsolved_*_{baseline,s20_mk2}.csv`,
where every `nodes_explored` is censored at the budget. There is no stored
cost for any row those arms solved, so an uncensored head-to-head over this
set cannot be built without re-running both arms.

What can be built is one-sided, and therefore a lower bound: of the rows
each arm **failed** at a given budget, how many does the hybrid settle, and
for how much. Hybrid cost is the best of the 501 screen and the two rungs
above.

| arm failed at | rows | hybrid solves | | median hybrid nodes | ratio at least |
|---|---:|---:|---:|---:|---:|
| `greedy` @10,000 | 831 | 823 | 99.0% | 217 | 46x |
| `s20_mk2` @10,000 | 259 | 251 | 96.9% | 516 | 19x |
| `greedy` @100,000 | 222 | 214 | 96.4% | 187 | 535x |
| `s20_mk2` @100,000 | 39 | 31 | 79.5% | 151 | 662x |
| `greedy` @1,000,000 | 88 | 80 | 90.9% | 197 | 5,076x |
| `s20_mk2` @1,000,000 | 14 | 14 | 100% | 156 | 6,431x |
| `greedy` @5,000,000 | 31 | 28 | 90.3% | 261 | 19,157x |
| **`s20_mk2` @5,000,000** | **9** | **9** | **100%** | **149** | **33,557x** |

The bottom row is the one to quote, with its caveat attached: `s20_mk2`
spent five million nodes on nine rows and solved none of them; the hybrid
settles all nine at a median of 149 nodes. The ratio is a lower bound
because the numerator is censored -- those searches were stopped at the
budget, not run to a solve.

## The cap never came close

`max_relator_length_seen` over all 3,626 row-runs peaks at **45** against a
cap of **255**. Length was never the constraint on this set.

Note the bound this rests on is narrower than the one in RUNBOOK section
10. That argument -- every relator of every child is bounded by the popped
total -- covers AC substitutions, where a child is
`r_i <- rot(r_i).rot(r_j^+-)`. It does **not** cover the Nielsen images
`s40_gen` puts in the same heap: `x -> xy` can roughly double a relator, so
on this arm a child can exceed the popped total. Measured directly on one
row: `max_relator_length_seen` 37 against `max_popped_total_seen` 28. The
verdict here therefore rests on the recorded field, not on the theorem.

## Files

| file | what |
|---|---|
| `ac19_cascade_screen_cascade501_b1000_mrl255_sb1000.jsonl` | rung 1, 2,130 rows, move-wise certificates |
| `ac19_cascade_screen_cascade501_b100000_mrl255_sb10000.jsonl` | rung 2, 1,496 rows, move-wise certificates |
| `unsolved_cascade501_b100000.csv` | the 8 survivors |
| `aut_assisted_cascade501_b100000.csv` | rung-2 solves whose path uses a basis change |
| `summary.json` | the numbers on this page, machine-readable |

The `_sb<N>` in the filenames is the non-default starter budget. Runs at the
pinned default keep their original names, so nothing here can be confused
with the archive or appended to it by resume.
