# Heap ordering for the greedy substitution search

[`greedy_baseline.py`](greedy_baseline.py) is a best-first search: pop the most promising open state, apply every Definition 2.1 substitution move, reduce, canonicalise, push what is new. The baseline picks "most promising" by **total length**. [`heuristics.py`](heuristics.py) replaces that expression and nothing else.

## No weight vector ships here

This module is the **mechanism** — a feature set, a config schema, a solver that reads the config, and a control gate. `BASELINE_CONFIG` (`{"L": 1.0}`, plain total length) is the only config it defines, and it is the control, not a recommendation.

An earlier `RECOMMENDED` vector was withdrawn. It read

```
L + 2.53·K + 6.418·MK + 8.458·S + 3.292·xyimb
```

and it was selected on a slice of rows that contained **fourteen of the twenty** rows it was then validated against. Every margin reported for it — the 10/20 → 15/20 headline, the 60-row cost tables — was therefore measured largely on its own tuning set, which is a statement about the tuner, not about the ordering. It is gone rather than demoted because a name importable from this module becomes the thing every call site passes, and the provenance that makes a number readable does not travel with an import.

The numbers it produced still exist as the `heur_*` columns of the benchmark arms tables, labelled there as the output of a withdrawn vector. `benchmark_subset_*_arms.json` carries the weights themselves as provenance for those columns and is now their only record.

**If you tune a replacement, validate it on rows disjoint from the ones you tuned on**, and report the held-out count as the headline.

## Using it

```python
from experiments.search.heuristics import greedy_search_h

stats = greedy_search_h(r1, r2, node_budget=100_000, max_relator_length=24,
                        config=my_config)       # config=None  =>  the baseline, exactly
```

Returns `greedy_search`'s eleven-key dict — same keys, order, types — so a call site switches ordering with one argument. `phi(r1, r2)` gives the feature vector; `make_priority(config)` compiles a config into the heap's key function.

## Config shape

`{"segments": [{"upto": <ceiling>, "w": {feature: weight}}, ...]}`. Segments are tried in order; the first whose `upto` covers the state's total length wins, and the last should carry `"upto": None`. A single segment is one linear ordering; two or more switch weights at a length boundary.

The heap key is `(segment_index, score)`. The leading index makes every state below a boundary outrank every state above it, and stops two segments' scores — on unrelated scales — from being compared.

## The features

A relator is a **cyclic** word. Its **blocks** are the maximal runs of one generator read around the ring, where a letter and its inverse are the same generator (`xXxX` is one block of four). A run wrapping the seam is one block, not two — counting it twice would read where the canonicaliser cut the word instead of the presentation.

`phi(r1, r2)` computes all seventeen in one pass, cached; every one is rotation-invariant.

| # | name | what it measures | why it might help |
|---|---|---|---|
| 0 | `L` | total length, `len(r1) + len(r2)` | the baseline's entire ordering; the trivial state is the shortest, so length is the obvious distance-to-go proxy |
| 1 | `Lmin` | length of the shorter relator | the trivial state needs *both* at length 1; a short one is half the job done |
| 2 | `Lmax` | length of the longer relator | what still has to come down; `L` cannot tell `12+12` from `2+22` |
| 3 | `imbal` | `Lmax - Lmin` | a lopsided pair has one relator doing all the work |
| 4 | `K` | knot sum, `knots(r1) + knots(r2)` | knot reduction is rare and hard, so a state that bought one should outrank one that merely got shorter |
| 5 | `MK` | max knots over the two relators | a pair is only as reducible as its harder half |
| 6 | `mK` | min knots | nonzero means *both* relators are mixed words — no pure power to work with |
| 7 | `S` | smaller mean block: mean run length of the thinner generator | thin runs are where cancellation can start |
| 8 | `Bmax` | larger mean block | long uniform runs are a different shape from fine alternation |
| 9 | `B1` | number of length-1 blocks | isolated letters — where a substitution can cancel a whole block |
| 10 | `Bmin` | shortest block in the pair | the most fragile spot; `B1` counts them, this says whether any exists |
| 11 | `nb` | total blocks across both relators | how chopped-up the pair is, unnormalised |
| 12 | `xyimb` | `abs(#x − #y) / L` | generator imbalance, scale-free: leaning on one generator is closer to a pure power |
| 13 | `Bmaxrun` | longest single block | `Bmax` is a *mean* and hides a spike; this sees it |
| 14 | `Bspread` | longest − shortest block | how uneven the blocking is; a uniform and a spiky pair share every mean above |
| 15 | `ratio` | `Lmin / Lmax` | imbalance as a ratio — ranks differently from `imbal` at different scales |
| 16 | `density` | `nb / L` | blocks per letter: how finely the pair alternates, scale-free |

Knots are `0` for a **pure power** (one generator absent) — nothing to be tangled with. Otherwise `max(#x-blocks, #y-blocks)`.

## Two invariants

**The control gate.** `config=None` must reproduce `greedy_search` *pop for pop* — same `solved` flag **and** same `nodes_explored`. Scoring the same is not being the same: a changed reduction, cap or tie-break could still tie on a benchmark, and every reported delta would then measure that change instead of the ordering. It also keeps the baseline inside the config space — a space that cannot express "no change" always appears to beat its control.

**The priority must be a pure function of the state.** The visited set dedups on first discovery and there is no decrease-key, so a state's priority is fixed by whichever path reached it first. Any term reading `depth` or the parent ("did this move drop a knot?") would make pop order depend on discovery order. A knot *reduction* is already carried by the **absolute** knot count.

## What CI runs

The mechanism only — the control gate, the drop-in dict contract, certificate replay, the feature definitions, and the subset/arms table integrity checks. There is no "the shipped ordering beats the baseline" test, because nothing ships. See [`test_greedy_heuristic.py`](../../tests/test_greedy_heuristic.py).
