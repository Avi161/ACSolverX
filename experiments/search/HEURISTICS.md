# Heap ordering for the greedy substitution search

[`greedy_baseline.py`](greedy_baseline.py) is a best-first search: pop the most promising open state, apply every Definition 2.1 substitution move, reduce, canonicalise, push what is new. The baseline picks "most promising" by **total length**. [`heuristics.py`](heuristics.py) replaces that expression and nothing else.

## The ordering

`S20_MK2` is the **recommended** heap ordering — the one tuned vector this module ships.

```
priority(r1, r2) = L + 20·S + 2·MK
```

`S20_MK2` in full: three of seventeen features, one weight vector, no length boundary. Lower pops first, so both structural terms push a state down the queue — preferred for being short (`L`), for thicker runs of the thinner generator (`S`), and for having its harder half less tangled (`MK`). `S` carries the weight; `MK` is a light correction on top of it, worth +3 solves on the selection slice (`S20` 49/120 → `S20_MK2` 54/120).

**Stated as a pair, which is the only readable form:** *selected on* the ac1m_hard_aut train 120; *evaluated on* a fresh holdout that shares no automorphism class with it. "Held out" alone is ambiguous once a project has two splits.

`BASELINE_CONFIG` is the control — `{"L": 1.0}`, plain total length, reproduces `greedy_search` exactly.

## Withdrawn: the former `RECOMMENDED`

```
L + 2.53·K + 6.418·MK + 8.458·S + 3.292·xyimb        ← do not use
```

Retired as **overfit**, and removed rather than demoted — an importable name becomes the thing every call site passes, and provenance does not travel with an import. It was selected on a slice containing fourteen of the twenty rows it was then validated against, and its 60-row campaign used subset-60 as its own row list. So every margin ever published for it — 10/20 → 15/20, the 60-row cost tables — is largely in-sample: a statement about the tuner, not about the ordering.

Its runs were real and are kept, labelled as the output of a withdrawn vector, in the `heur_*` columns of the arms tables. Nothing imports it, and a test guards against the weights reappearing under another name.

## Using it

```python
from experiments.search.heuristics import greedy_search_h, S20_MK2

stats = greedy_search_h(r1, r2, node_budget=100_000, max_relator_length=24,
                        config=S20_MK2)         # config=None  =>  the baseline, exactly
```

Returns `greedy_search`'s eleven-key dict — same keys, order, types — so a call site switches ordering with one argument. `phi(r1, r2)` gives the feature vector; `make_priority(config)` compiles a config into the heap's key function.

## Results

### Where the ordering was chosen (`ac1m_hard_aut`, budget 1,000)

The selection slice and two holdouts. The fresh holdout is automorphism-disjoint from both the training slice and the spent one, so it is the number that carries.

| arm | train 120 | spent holdout 60 | **fresh holdout 60** | bench60 @1k |
|---|---|---|---|---|
| `length` (control) | 0/120 | 0/60 | **0/60** | 29/60 (mean 176) |
| `S20` | 49/120 | 30/60 | **27/60** | 36/60 (mean 161) |
| **`S20_MK2`** | 54/120 | 33/60 | **27/60** | **37/60 (mean 153)** |
| `S28_MK2_F8` | 57/120 | 28/60 | **22/60** | 38/60 (mean 218) |
| `MK6_418` | 16/120 | 5/60 | **9/60** | 37/60 (mean 257) |

Two things this table says. The length control solves **nothing at all** on the hard Aut slices — 0/120 and 0/60 — so the structural climb is not a marginal improvement there, it is the difference between solving and not. And the grid's own top scorer, `S28_MK2_F8` at 57/120, is **not** what ships: it falls to 22/60 on the fresh holdout where `S20_MK2` holds 27/60. Picking the training-set maximum would have been the overfit move a second time.

### On the 60-row benchmark ladder, budget 10,000

Rescored from existing 1M-node runs — a search at budget B is the first B pops, so no new search was needed. Greedy column is the frozen `m10k_greedy_*` in the arms table.

| arm | solved | median nodes (joint) | mean nodes (joint) |
|---|---|---|---|
| greedy (length) | 40/60 | 197 | 1,205.7 |
| **`S20_MK2`** | **52/60** | **86** | **280.1** |

**+12 solves, and a strict superset**: McNemar 12–0, no row lost. The gains are all in the hard tail — bin 6 +2, bin 7 **+6** (0/6 → 6/6), bin 8 +2, bin 9 +2 — where bins 0–5 were already saturated for both arms. Cost figures are on the 40 rows both solve.

⚠ **One cap mismatch.** The `S20_MK2` runs used `mrl=48`; the frozen greedy column is `mrl=24`. Read the Δ-solves as primary and the node ratios as indicative.

### The withdrawn vector's numbers, kept for the record

These are what the retired `RECOMMENDED` produced, and they are why it looked good. Read them as in-sample: subset-60 was that campaign's own row list.

| arm | solved | median nodes | mean nodes | median path | mean path |
|---|---|---|---|---|---|
| greedy baseline @ 10⁶/24 | 60/60 | 1,310.5 | 45,244.2 | 46.5 | 142.62 |
| best change of variables @ ≤20k/24 *(oracle)* | 60/60 | 34.5 | 2,383.1 | 16.5 | 97.05 |
| ~~withdrawn vector~~ @ 100k/48 | 60/60 | 226.5 | 10,244.0 | 38.0 | 102.73 |

Those columns ran at **different budgets and caps**, so a cross-column ratio is not a controlled speedup. Best CoV is an **oracle**: 2,383 is what the winning `z` costs once you know which `z` wins, and finding it cost ~2.2M nodes per presentation. The CSV's `m10k_*` columns hold all three at a matched 10,000/cap 24.

## What CI runs

The 20-row subset at budget 1,000, as a **regression pin on the mechanism** — the control gate (`config=None` reproduces the baseline pop for pop) is what it exists to protect. Those ids are [`benchmark/subsets/benchmark_subset_20.json`](../../benchmark/subsets/benchmark_subset_20.json) verbatim, in file order; they stay inlined in [`test_greedy_heuristic.py`](../../tests/test_greedy_heuristic.py) so CI measures a fixed row list even if the file changes, and `test_bench_ids_are_the_shipped_subset_20` pins the two together.

CI no longer asserts that any tuned ordering beats the baseline on those rows. That assertion was green and meaningless: 14 of the 20 are in the slice the withdrawn vector was tuned on, so it restated the tuning objective.

## The features

A relator is a **cyclic** word. Its **blocks** are the maximal runs of one generator read around the ring, where a letter and its inverse are the same generator (`xXxX` is one block of four). A run wrapping the seam is one block, not two — counting it twice would read where the canonicaliser cut the word instead of the presentation.

`phi(r1, r2)` computes all seventeen in one pass, cached; every one is rotation-invariant. **Bold** = used by `S20_MK2`.

| # | name | what it measures | why it might help |
|---|---|---|---|
| 0 | **`L`** | total length, `len(r1) + len(r2)` | the baseline's entire ordering; the trivial state is the shortest, so length is the obvious distance-to-go proxy |
| 1 | `Lmin` | length of the shorter relator | the trivial state needs *both* at length 1; a short one is half the job done |
| 2 | `Lmax` | length of the longer relator | what still has to come down; `L` cannot tell `12+12` from `2+22` |
| 3 | `imbal` | `Lmax - Lmin` | a lopsided pair has one relator doing all the work |
| 4 | `K` | knot sum, `knots(r1) + knots(r2)` | knot reduction is rare and hard, so a state that bought one should outrank one that merely got shorter |
| 5 | **`MK`** | max knots over the two relators | a pair is only as reducible as its harder half |
| 6 | `mK` | min knots | nonzero means *both* relators are mixed words — no pure power to work with |
| 7 | **`S`** | smaller mean block: mean run length of the thinner generator | thin runs are where cancellation can start |
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

## Config shape

`{"segments": [{"upto": <ceiling>, "w": {feature: weight}}, ...]}`. Segments are tried in order; the first whose `upto` covers the state's total length wins, and the last should carry `"upto": None`. Both `BASELINE_CONFIG` and `S20_MK2` use one segment — multi-segment configs switch weights at a length boundary, and the schema keeps that open because the research harness speaks the same format.

The heap key is `(segment_index, score)`. The leading index makes every state below a boundary outrank every state above it, and stops two segments' scores — on unrelated scales — from being compared.

## Two invariants

**The control gate.** `config=None` must reproduce `greedy_search` *pop for pop* — same `solved` flag **and** same `nodes_explored`. Scoring the same is not being the same: a changed reduction, cap or tie-break could still tie on a benchmark, and every reported delta would then measure that change instead of the ordering. It also keeps the baseline inside the config space — a space that cannot express "no change" always appears to beat its control.

**The priority must be a pure function of the state.** The visited set dedups on first discovery and there is no decrease-key, so a state's priority is fixed by whichever path reached it first. Any term reading `depth` or the parent ("did this move drop a knot?") would make pop order depend on discovery order. A knot *reduction* is already carried by the **absolute** knot count.
