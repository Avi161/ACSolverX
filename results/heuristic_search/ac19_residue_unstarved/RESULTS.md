# The AC19 residue with `s40_gen` un-starved

What happens to the 2,130 orbits the 501-node cascade screen left unsolved
when the `s40_gen` component is given more than its pinned 500 nodes.

Read [the framing section](#what-this-is-and-is-not) before quoting any
number here. Most of these rows were already solved in the archive. The new
thing is **which stage of the pipeline solves them and at what cost**, plus
four rows of genuinely new coverage. Stage-by-stage attribution over the
whole 72,779-orbit screen is in
[pipeline attribution](#pipeline-attribution-which-stage-returns-the-certificate).

## The runs

Both used `experiments/search/run_ac19_cascade_screen.py` and the
`--starter-budget` flag added in `18e57232`. Before that flag the starter
budget was an imported constant, so every rung of the shipped ladder gave
`s40_gen` exactly 500 nodes and handed the extra rope to `s20_mk2`.

| rung | invocation | rows in |
|---|---|---:|
| 1 | `--budget 1000 --starter-budget 1000` | 2,130 |
| 2 | `--budget 100000 --starter-budget 10000` | 1,496 |

Rung 1 sets `budget == starter_budget` on purpose: `s20_mk2` gets an
allowance of zero and never runs, so whatever solves is `s40_gen` alone and
the attribution is unambiguous. That is the same arithmetic that makes the
stage unreachable at the shipped default -- see
[below](#s20_mk2-is-structurally-unreachable-at-the-shipped-default).

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

## Pipeline attribution: which stage returns the certificate

`cascade_heuristics.search()` is one algorithm with four stages, not an arm
plus a fallback. The deciding stage is recorded per row in `winner`, so the
whole screen can be attributed without re-running anything. Regenerate this
table with `PYTHONPATH=. python experiments/search/stage_attribution.py`.

Over all 72,779 orbits, each taken at the highest rung it reached:

| stage | rows | share | AC-certified | `aut_assisted` |
|---|---:|---:|---:|---:|
| Nielsen descent alone | 0 | 0.000% | 0 | 0 |
| special rewrite (BS collapse) | 18,839 | 25.885% | 18,839 | 0 |
| 500-pop L+40S (`s40_gen`) | 53,624 | 73.681% | 8,324 | 45,300 |
| `s20_mk2` after the frontier discard | 307 | 0.422% | 307 | 0 |
| terminal pre-check | 1 | 0.001% | 1 | 0 |
| unsolved | 8 | 0.011% | -- | -- |

Folded up: 70,649 settled at the 501 rung, plus 634 at rung 1 and 1,488 at
rung 2, is **72,771 of 72,779 settled and 8 open** -- 27,471 AC-certified,
45,300 `aut_assisted`.

**Descent alone is empty, and that is a measurement rather than a gap in the
recording.** A descent that landed on (x,y) would reach `bs_collapse` and
come back with `reason='terminal'`. All 18,839 rewrite rows carry
`reason='collapsed'` instead. The basis descent never lands on (x,y) by
itself anywhere on this set; it feeds the rewrite stage and nothing else.

The decoder exposure sits in exactly one bucket. The rewrite and `s20_mk2`
stages are 100% AC-certified; all 45,300 `aut_assisted` rows come from
`s40_gen`.

### What the special rewrite recognises

The Baumslag-Solitar relation `b^-1 a b a^-2`. `_recognize` in
`bs_collapse.py` scans the 16 ordered generator pairs `(a,b)` over `xXyY`
with `a != b`, forms that word, canonicalises it, and compares it against a
relator of length **exactly 5**; the companion relator must then carry
`b`-exponent `+-1`. Recognition is structural, not a lookup -- 16 candidate
reductions, constant time, no table. The archive confirms the gate: **all
18,839** rewrite rows have a relator of length exactly 5, against 14,195 of
51,810 for every other stage combined.

The collapse then runs three certified phases -- pinch the companion down to
a single stable letter, use it to eliminate `b` from the relation leaving
`a^-1`, then use that generator to kill every remaining `a`. Each phase is
proof-carrying: every rewrite is realised as a concrete AC move
`(target+1, sign, target_cut, cut)` and checked by
`replay_move(state, move) == desired_pair`, which raises rather than emit an
unverified step. Certificates run 2 to 256 moves, median 15, p99 103.

### `s20_mk2` is structurally unreachable at the shipped default

The stage allowances are `min(starter_budget, B - spent)` for `s40_gen` and
`min(B, B - spent)` for `s20_mk2`, and the loop skips any stage whose
allowance is `<= 0`. Across all 53,939 rows that reached `s40_gen` at the 501
rung, normalization plus rewrite cost **exactly 1 node, every time**. So at
the shipped default:

    spent before s20_mk2 = 1 + 500 = 501
    allowance            = min(501, 501 - 501) = 0   -> stage skipped

**Zero of the 72,779 rows at the 501 rung carry an `s20_mk2` attempt.** The
same arithmetic holds at rung 1 here (`B` = 1,000 with `starter_budget` =
1,000). Only rung 2 (`B` = 100,000, `starter_budget` = 10,000) enters the
stage at all, with exactly 89,999 pops.

This is the starvation finding stated from the other end, and it is the
cleaner statement of it. The shipped 501-node screen is not a four-stage
pipeline whose last stage rarely fires; it is a **three-stage pipeline with a
fourth stage that provably cannot be entered at that budget**. `B - 501` is
the right formula for what `s20_mk2` would receive -- at `B = 501` it
evaluates to zero.

## What this is, and is not

**It is not 2,122 new solves.** The shipped ladder already settled almost
all of these by its 100,000 rung, at much higher cost. Those rung results
live in S3, not in this repo, which is part of why the distinction is easy
to lose.

**It is stage attribution inside one pipeline.** The 307 rows `s20_mk2`
settles at rung 2 are not a fallback outside the algorithm: `s20_mk2` is the
fourth stage of `cascade_heuristics.search()`, entered after the frontier is
discarded and the original pair restarted. Attributing them to `s20_mk2`
names the stage that paid, not a competing arm that won.

**The efficiency claim is therefore a within-pipeline one.** Un-starved,
`s40_gen` takes 1,181 of the 1,488 rung-2 solves -- 79% -- at a median of
2,173 nodes, on rows the shipped ladder had to carry all the way to its
`s20_mk2` stage. That is the honest version: a cheap early stage absorbing
work an expensive late stage was doing, within the same algorithm.

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
| `../../../experiments/search/stage_attribution.py` | regenerates the pipeline attribution table and re-checks the `s20_mk2` allowance |

The `_sb<N>` in the filenames is the non-default starter budget. Runs at the
pinned default keep their original names, so nothing here can be confused
with the archive or appended to it by resume.
