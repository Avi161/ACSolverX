# Heap ordering for the greedy substitution search

The greedy solver in [`greedy_baseline.py`](greedy_baseline.py) is a best-first search: pop the most promising open state, apply every Definition 2.1 substitution move, reduce, canonicalise, push whatever is new. "Most promising" is the only judgement it makes, and the baseline makes it with one number — **total length**, `len(r1) + len(r2)`. [`heuristics.py`](heuristics.py) replaces that number and changes nothing else.

## The ordering

```
priority(r1, r2) = L + 2.53·K + 6.418·MK + 8.458·S + 3.292·xyimb
```

That is `RECOMMENDED` in full — five of the seventeen features, one weight vector, no length boundary. Lower pops first, so every term pushes a state **down** the queue: a state is preferred for being short (`L`), for being less tangled (`K`, `MK`), for having thicker runs of its thinner generator (`S`), and for using its two generators evenly (`xyimb`). The weights were tuned jointly, not one at a time — `S` is the weakest of the five as a solo ordering and carries the largest weight here, so a one-at-a-time search would have thrown it away.

`BASELINE_CONFIG` is the control: one segment, `{"L": 1.0}`, which is plain total length and reproduces `greedy_search` exactly.

## Using it

```python
from experiments.search.heuristics import greedy_search_h, RECOMMENDED

stats = greedy_search_h(r1, r2, node_budget=100_000, max_relator_length=24,
                        config=RECOMMENDED)     # config=None  =>  the baseline, exactly
```

`greedy_search_h` returns **exactly** `greedy_search`'s eleven-key dict — same keys, same order, same types — so an existing call site switches ordering by passing one argument and touches nothing downstream. `phi(r1, r2)` returns the feature vector and `make_priority(config)` compiles a config into the callable the heap pushes with, for scoring or tuning without running a search.

## The result

Twenty presentations at a node budget of 1,000: baseline **10/20**, `RECOMMENDED` **15/20**, with no presentation traded away and fewer nodes on the mean over the both-solved set. Pinned in [`../../tests/test_greedy_heuristic.py`](../../tests/test_greedy_heuristic.py).

Which twenty: `benchmark/subsets/benchmark_subset_20.json` verbatim, in file order. That file lives on the research branch and is not in this repo, so the ids are inlined in the test. They are line numbers of `data/ms640_solved.txt`, binned into ten equal-width slices of `log10(nodes_explored)` for a 10⁶-node baseline run (each bin 3.37× the one below), two rows per bin, picked to minimise Aut(F₂)-equivalent pairs and then spread evenly over path length.

**Read 10 → 15 as a regression pin, not held-out validation:** 14 of those 20 rows are in the slice these weights were tuned on. On the 4 that were held out, baseline solves 1 and `RECOMMENDED` solves 3.

## The features

A relator is a **cyclic** word — the ring has no first letter. Its **blocks** are the maximal runs of a single generator read around that ring, where a letter and its inverse count as the same generator (`x` and `X` do not start a new block, so `xXxX` is one block of four). A run that wraps the seam is one block, not two: counting it twice would let a feature see where the canonicaliser happened to cut the word, which measures the tie-break rather than the presentation.

`phi(r1, r2)` computes all seventeen in one pass over the two words, cached. Every one is rotation-invariant. The five in **bold** are the ones `RECOMMENDED` uses; the rest are available to a config of your own.

| # | name | what it measures | why it might help |
|---|---|---|---|
| 0 | **`L`** | total length, `len(r1) + len(r2)` | the baseline's entire ordering; the trivial state is the shortest state, so length is the obvious distance-to-go proxy |
| 1 | `Lmin` | length of the shorter relator | the trivial state needs *both* relators at length 1; a short one is half the job already done |
| 2 | `Lmax` | length of the longer relator | the relator that still has to come down; `L` alone cannot tell `12+12` from `2+22` |
| 3 | `imbal` | `Lmax - Lmin` | a lopsided pair has one relator doing all the work, a different regime from two medium ones |
| 4 | **`K`** | knot sum, `knots(r1) + knots(r2)` | the headline structural feature: knot reduction is rare and hard, so a state that bought one should be expanded before a state that merely got shorter |
| 5 | **`MK`** | max knots over the two relators | the worse-tangled relator; a pair is only as reducible as its harder half |
| 6 | `mK` | min knots | nonzero means *both* relators are genuinely mixed words — no pure power to work with |
| 7 | **`S`** | smaller mean block: mean run length of the thinner generator | thin runs of one generator are where cancellation can start |
| 8 | `Bmax` | larger mean block | the other side of `S`; long uniform runs are a different shape from fine alternation |
| 9 | `B1` | number of length-1 blocks | isolated letters — the thin spots, where a substitution can cancel a whole block at once |
| 10 | `Bmin` | shortest block anywhere in the pair | the single most fragile spot; `B1` counts them, this says whether any exists |
| 11 | `nb` | total number of blocks across both relators | how chopped-up the pair is overall, unnormalised |
| 12 | **`xyimb`** | `abs(#x − #y) / L` | generator imbalance, scale-free: a pair leaning on one generator is closer to a pure power |
| 13 | `Bmaxrun` | longest single block anywhere | `Bmax` is the larger *mean*, which hides a spike; this sees the spike |
| 14 | `Bspread` | longest block − shortest block | how uneven the blocking is; a uniform and a spiky pair can share every mean above |
| 15 | `ratio` | `Lmin / Lmax` | imbalance as a ratio, where `imbal` is the raw difference — the two rank differently at different scales |
| 16 | `density` | `nb / L` | blocks per letter: how finely the pair alternates, scale-free |

Knots are `0` for a **pure power** (a relator in which one generator does not appear at all) — there is nothing to be tangled with. Otherwise a relator's knot count is `max(#x-blocks, #y-blocks)`.

## Config shape

A config is a list of length-keyed **segments**, each a weight vector: `{"segments": [{"upto": <ceiling>, "w": {feature: weight}}, ...]}`. Segments are tried in order and the first whose `upto` covers the state's total length wins; the last should carry `"upto": None`. Both configs here use a single segment — multi-segment configs switch weight vectors at a length boundary, and the schema keeps that open because the research harness this was ported from speaks the same format.

The heap key is `(segment_index, score)`. The leading index makes every state below a boundary outrank every state above it, and keeps two segments' scores — which sit on unrelated scales — from ever being compared.

## Two invariants, if you change anything here

**The control gate.** `config=None` must reproduce `greedy_search` *pop for pop* — the same `solved` flag **and** the same `nodes_explored` on every presentation. Scoring the same is not being the same: a change to the reduction, the cap or the heap tie-break could still tie on a benchmark, and every reported delta would then be measuring that change instead of the ordering. It also keeps the baseline inside the config space — a tuning space that cannot express "no change" will always appear to beat its control.

**The priority must be a pure function of the state.** The visited set dedups canonical states on first discovery and there is no decrease-key, so a state's priority is fixed by whichever path reached it first. Any term reading `depth` — or the parent, e.g. "did this move drop a knot?" — would make pop order depend on discovery order and stop being reproducible. A knot *reduction* is already carried by the **absolute** knot count.
