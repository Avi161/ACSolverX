# Block/knot heap orderings vs the baseline greedy

**Question.** The baseline greedy orders its open set by total length alone. The block analysis in `results/clustering/` found that *thickness* (`smaller mean block`) and *knot count* separate solved from unsolved presentations. Does either make a better search priority at a fixed node budget?

**What changes.** Only the heap priority. `experiments/heuristic_search/hsearch.py` subclasses `GreedyBaselineSolver`, so the move generator, free reduction, Booth canonicalisation, per-relator cap, visited set and the `(priority, depth, key)` tie-break are all the baseline's. A difference between arms is attributable to the ordering and nothing else.

**Control gate.** The `length` arm is asserted to reproduce `greedy_search` *pop for pop* — same solved flag and same `nodes_explored` on every presentation, at every budget — before any comparison is read. Pinned in `tests/heuristic_search/test_hsearch.py`. A control that merely scores the same is not the same search.

**Move set.** The substitution move still requires a cancelling seam (`greedy_baseline.py:220`). Dropping that requirement would change the branching factor and the ordering simultaneously; it is a separate experiment, not a knob turned mid-run.

## Headline: benchmark subset 20, at the 1,000-node ceiling

| priority | @500 | @1000 | nodes/search @1000 |
|---|---|---|---|
| `length` (baseline) | 9/20 | 10/20 | 167.6 |
| `length + 4·knots` | 11/20 (+2) | **13/20** (+3, 3W-0L) | **86.0 — ×0.51** |
| `knots_first@endgame16` | 11/20 (+2) | **14/20** (+4, 4W-0L) | 133.8 — ×0.80 |

**The advantage widens with budget rather than converging** (+2 → +3 and +2 → +4). That distinction is the point of running 1,000 at all: a search at budget B is the first B pops of any longer search, so an ordering that merely *arrives sooner* would see the baseline catch up here. Neither does — they are reaching states the length ordering never ranks highly.

`length + 4·knots` solves one fewer than the endgame arm but does it in **half the nodes** of the baseline, consistently (×0.53 at 500, ×0.51 at 1000).

**Significance.** Neither result is significant *on 20 presentations*: the exact paired sign test gives p = 0.25 and p = 0.12. Both arms are strictly non-losing at 1,000 (0 losses each). For a number that carries weight, see the pooled validation below.

## It replicates on untouched presentations (budget 500)

| priority | tune (20) | exploratory (22) | **confirm (34, untouched)** |
|---|---|---|---|
| `length` (baseline) | 9 | 9 | 18 |
| `length + 4·knots` | 11 (+2) | 11 (+2) | 20 (+2) |
| `knots_first@endgame16` | 11 (+2) | 12 (+3) | **23 (+5)** |
| `length + 4·smb` | 10 (+1) | 9 (=) | 21 (+3) |

Pooling the paired win/loss outcomes over the **two validation sets only** — 56 presentations, tuning set excluded because that is where the arm was selected:

| priority | pooled W–L | exact sign test |
|---|---|---|
| `knots_first@endgame16` | **10W–2L** | **p = 0.039** |
| `length + 4·smb` | 3W–0L | p = 0.250 |
| `length + 4·knots` | 6W–2L | p = 0.289 |

**Caveat on that 0.039.** Three arms were carried from tuning into validation, so a Bonferroni correction over those three puts it at p ≈ 0.12. It is the strongest signal here and it survives on data used for nothing else, but it is a single-digit number of discordant pairs and should be confirmed at production budget before it is treated as established.

**Why the knot ordering wins where the linear blend does not.** `knots_first` expands *any* state that reduced the knot count before any state that merely got shorter — which is the user's original observation, that a knot reduction is rare and therefore worth following immediately. The `@endgame16` switch is what stops that from being self-defeating: below total length 16 it reverts to pure length, because near the trivial state the remaining work is cancellation, not restructuring. Without the switch, plain `knots_first` scores 8/20 at 500 — *below* the baseline. The threshold is doing real work, and 16 was selected from {4, 6, 8, 10, 12, 14, 16, 20} on the tuning set.

## Protocol

Tuning on `benchmark_subset_20`; the winner is pre-registered from the tuning set alone, then looked at once elsewhere. Two validation sets, because the first was compromised:

- **exploratory (22)** — the members of subset-40 not in subset-20. Already inspected under a buggy tie-break (see below), so it can no longer serve as a clean confirmation and is labelled accordingly.
- **confirm (34)** — the members of subset-60 in neither set above. Untouched.

### The tie-break bug, recorded

The first ranking compared arms by the raw **sum** of nodes over each arm's own both-solved set. Those sets differ in size, so 537 nodes over 8 presentations "beat" 582 over 9 — when the per-presentation means are 67.1 against 64.7, the opposite order. It picked the wrong pre-registered winner, and it was only caught because the held-out numbers looked odd. `compare()` now reports `nodes_both_mean` and the ranking uses it.
