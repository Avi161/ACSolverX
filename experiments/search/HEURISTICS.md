# Heap orderings for the greedy substitution search

The greedy solver in [`greedy_baseline.py`](greedy_baseline.py) is a best-first search over presentations: pop the most promising open state, apply every Definition 2.1 substitution move, reduce, canonicalise, push whatever is new. "Most promising" is the only judgement it makes, and the baseline makes it with one number — **total length**, `len(r1) + len(r2)`. This document describes the heuristics in [`heuristics.py`](heuristics.py), which replace that one number and change nothing else.

**The result.** On twenty presentations of `data/ms640_solved.txt`, two from each of ten difficulty bins, at a node budget of 1,000: the baseline solves 10, the recommended ordering solves 15, and it does not lose a single presentation the baseline solved. Pinned in [`../../tests/test_greedy_heuristic.py`](../../tests/test_greedy_heuristic.py).

**Selected on, evaluated on.** State those two separately or the number reads as more than it is. `RECOMMENDED`'s weights were tuned on a difficulty-stratified slice, and **14 of these 20 rows are in that slice** — 4 are in the held-out half, and 2 appear in neither. So 10 → 15 is a *regression pin*, not held-out validation: it says the shipped weights still do what they did, on rows they were largely chosen against. The held-out reading is the four-row one, where the baseline solves 1 and the recommended ordering solves 3, and 2 of the 5 flips overall land there.

## Using it

```python
from experiments.search.heuristics import greedy_search_h, RECOMMENDED

stats = greedy_search_h(r1, r2, node_budget=100_000, max_relator_length=24,
                        config=RECOMMENDED)     # config=None  =>  the baseline, exactly
```

`greedy_search_h` returns **exactly** the dict `greedy_baseline.greedy_search` returns — same eleven keys, same order, same types — so an existing call site switches ordering by passing one argument and touches nothing downstream. `config=None` is the baseline search pop for pop, so the ordering can be turned on and off without maintaining two code paths.

Three other names are public: `phi(r1, r2)` returns the feature vector, `make_priority(config)` compiles a config into the callable the heap pushes with (for scoring or tuning without running a search), and `PRESETS` maps `"baseline"` / `"recommended"` / `"lean_small_budget"` to the configs below.

## Where the features come from

A relator is a **cyclic** word — the ring has no first letter. Its **blocks** are the maximal runs of a single generator read around that ring, where a letter and its inverse count as the same generator (`x` and `X` do not start a new block, so `xXxX` is one block of four). A run that wraps the seam is one block, not two: counting it twice would let a feature see where the canonicaliser happened to cut the word, which measures the tie-break rather than the presentation.

Two block statistics separate solved from unsolved presentations: the **knot count** (how many blocks a relator is chopped into) and the **smaller mean block** (how thick the thinner generator's runs are). Everything below is built from the block decomposition of the pair.

One caveat worth stating plainly: a feature that classifies well is *not* automatically a good search priority. A classifier is scored on the start state ("does this look hard?"); a heap priority is scored on its gradient across the search ("does moving this way help?"). `S` is the strongest classifier of the set and the weakest single ordering — yet it carries the largest weight in the tuned blend. Features were tuned jointly for that reason; testing them one at a time would have discarded it.

## The features

`phi(r1, r2)` computes all seventeen in one pass over the two words, cached on the word and on the pair. Every one is rotation-invariant. A 17-feature weighted config runs within noise of pure length, so the ordering layer is free and only the search trajectory moves the clock.

| # | name | what it measures | why it might help |
|---|---|---|---|
| 0 | `L` | total length, `len(r1) + len(r2)` | the baseline's entire ordering; the trivial state is the shortest state, so length is the obvious distance-to-go proxy |
| 1 | `Lmin` | length of the shorter relator | the trivial state needs *both* relators at length 1; a short one is half the job already done |
| 2 | `Lmax` | length of the longer relator | the relator that still has to come down; `L` alone cannot tell `12+12` from `2+22` |
| 3 | `imbal` | `Lmax - Lmin` | a lopsided pair has one relator doing all the work, which is a different regime from two medium ones |
| 4 | `K` | knot sum, `knots(r1) + knots(r2)` | the headline structural feature: knot reduction is rare and hard, so a state that bought one should be expanded before a state that merely got shorter |
| 5 | `MK` | max knots over the two relators | the worse-tangled relator; a pair is only as reducible as its harder half |
| 6 | `mK` | min knots | nonzero means *both* relators are genuinely mixed words — no pure power to work with |
| 7 | `S` | smaller mean block: mean run length of the thinner generator | thin runs of one generator are where cancellation can start; the strongest classifier in the set |
| 8 | `Bmax` | larger mean block | the other side of `S`; a pair of long uniform runs is a different shape from a finely alternating one |
| 9 | `B1` | number of length-1 blocks | isolated letters — the thin spots, where a substitution can cancel a whole block at once |
| 10 | `Bmin` | shortest block anywhere in the pair | the single most fragile spot; `B1` counts them, this one says whether any exists |
| 11 | `nb` | total number of blocks across both relators | how chopped-up the pair is overall, unnormalised |
| 12 | `xyimb` | `abs(#x − #y) / L` | generator imbalance, scale-free: a pair leaning heavily on one generator is closer to a pure power |
| 13 | `Bmaxrun` | longest single block anywhere | `Bmax` is the larger *mean*, which hides a spike; this sees the spike |
| 14 | `Bspread` | longest block − shortest block | how uneven the blocking is; a uniform pair and a spiky pair can share every mean above |
| 15 | `ratio` | `Lmin / Lmax` | imbalance as a ratio, where `imbal` is the raw difference — the two rank differently at different scales |
| 16 | `density` | `nb / L` | blocks per letter: how finely the pair alternates, scale-free |

Knots are `0` for a **pure power** (a relator in which one generator does not appear at all), because there is nothing to be tangled with. Otherwise a relator's knot count is `max(#x-blocks, #y-blocks)`.

## How a config turns features into a priority

A config is a list of length-keyed **segments**:

```python
{"segments": [{"upto": 16,   "w": {"L": 1.0}},
              {"upto": None, "w": {"L": 1.0, "K": 8.936, "xyimb": -5.978}}]}
```

Segments are tried in order and the **first** whose `upto` covers the state's total length wins; the last one should carry `"upto": None`, read as `+inf`, or nothing will match a long state. Within a segment the score is the plain dot product of the weights with the features, and the key the heap sees is `(segment_index, score)`.

That leading index is load-bearing twice over. It makes every state in an earlier (shorter) segment outrank every state in a later one — which is the whole point of an **endgame boundary**: the trivial state has zero knots and length 2, so once a presentation is short the remaining work is cancellation, not restructuring, and the search should revert to plain length. And because two segments' scores are never compared against each other, their weight vectors need not be on a common scale. It also guarantees the key is always an `(int, float)` pair, so `heapq` never has to compare an `int` against a tuple and raise mid-search.

## The presets

| preset | config | when |
|---|---|---|
| `BASELINE_CONFIG` | one segment, `{"L": 1.0}` | the control. Identical to `config=None`, and identical to `greedy_search` pop for pop. |
| `RECOMMENDED` | one segment, `{"L": 1.0, "K": 2.53, "MK": 6.418, "S": 8.458, "xyimb": 3.292}` | the default for a real run. No boundary: an endgame threshold measured **inert** for a climb that already carries `S` and `MK`. |
| `LEAN_SMALL_BUDGET` | `{"L": 1.0}` below length 16, then `{"L": 1.0, "K": 8.936, "xyimb": -5.978}` | small budgets (~500 nodes). It *does* need the boundary: with only a knot term it would otherwise keep chasing knots where nothing structural is left to buy. |

The baseline is inside the config space deliberately. A tuner whose search space cannot express "no change" will always appear to beat its control.

## Two invariants, if you change anything here

**The control gate is the foundation.** `config=None` must reproduce `greedy_search` *pop for pop* — the same `solved` flag **and** the same `nodes_explored` on every presentation. Scoring the same is not being the same: a change to the reduction, the cap or the heap tie-break could still tie on a benchmark, and every reported delta would then be measuring that change instead of the ordering. No number in this document is interpretable if that assertion fails.

**The priority must be a pure function of the state.** The visited set dedups canonical states on first discovery and there is no decrease-key, so a state's priority is fixed by whichever path reached it first. Under a non-length ordering that path is not the shortest one, so any term reading `depth` — or reading the parent, e.g. "did this move drop a knot?" — makes the pop order depend on discovery order and stop being reproducible. A knot *reduction* is already carried by the **absolute** knot count: a state that bought one sorts above a state that did not, with nothing path-dependent entering the key.

Two smaller rules that have cost time elsewhere. Compare nodes as a **mean** over the both-solved set, never as a sum — each arm's both-solved set has its own size, so a sum ranks an arm that solves fewer presentations as the cheaper one. And never raise a node budget to chase a result in a test: a search at budget `B` is exactly the first `B` pops of any longer search, so a bigger budget buys a slower test, never different behaviour.
