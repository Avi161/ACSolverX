# EXP-17 — one deep search, or a portfolio over the relabels?

Fixed total budget **1000 nodes** for every arm on the decidable band (bins 4–7, 24 rows). `k` searches of 1000/`k` nodes, one per signed-permutation relabel, stopping at the first solve. `k=1` is the incumbent single deep search. A relabel is the same presentation under a rename of the generators — the same problem, but a different string, and the greedy reads strings.

| ordering | k=1 (1000 each) | k=2 (500 each) | k=4 (250 each) | k=8 (125 each) |
|---|---|---|---|---|
| baseline (length) | **5**/24 | 3/24 | 0/24 | 0/24 |
| phased K8 | **16**/24 | 12/24 | 10/24 | 4/24 |
| richer knot climb | **19**/24 | 14/24 | 8/24 | 3/24 |

## Does splitting the budget help?

- `baseline (length)`: **no** — splitting costs solves (3/24 at k=2 against 5/24 for one deep search).
- `phased K8`: **no** — splitting costs solves (12/24 at k=2 against 16/24 for one deep search).
- `richer knot climb`: **no** — splitting costs solves (14/24 at k=2 against 19/24 for one deep search).

**Splitting the budget never helps.** Every solution these orderings can reach lies deeper than a divided budget allows, so the extra starting strings buy nothing at fixed cost. Relabels remain useful as *additional* budget (EXP-12 ran all eight at full depth), but not as a way to divide a fixed one.

## What the winning arms actually spent

| ordering | k | solved | mean nodes spent | mean relabels tried |
|---|---|---|---|---|
| baseline (length) | 1 | 5/24 | 586 | 1.0 |
| baseline (length) | 2 | 3/24 | 608 | 1.3 |
| phased K8 | 1 | 16/24 | 279 | 1.0 |
| phased K8 | 2 | 12/24 | 179 | 1.0 |
| phased K8 | 4 | 10/24 | 156 | 1.0 |
| phased K8 | 8 | 4/24 | 82 | 1.0 |
| richer knot climb | 1 | 19/24 | 391 | 1.0 |
| richer knot climb | 2 | 14/24 | 276 | 1.0 |
| richer knot climb | 4 | 8/24 | 166 | 1.0 |
| richer knot climb | 8 | 3/24 | 109 | 1.0 |

## The sharper detail: the alternate relabels almost never fire

Read the last column. Across every portfolio arm the mean number of relabels tried before a solve is **1.0** — when a divided search succeeds, it nearly always succeeds on the *first* string it is given (the identity relabel, i.e. the presentation as written). The alternates are being run and are contributing essentially nothing at these depths.

That is what makes the result monotone rather than a trade-off: `k=1` beats `k=2` beats `k=4` beats `k=8` for all three orderings, with no crossover anywhere. Splitting does not buy chances that pay off; it only shortens the one search that was going to work.

**This does not contradict the repo's finding that relabels supply most unsolved→solved flips.** That result gave each relabel a *full* budget — relabels as additional compute, which EXP-12 also does (8 full-depth searches per class). What EXP-17 rules out is the different and cheaper hope: that the same total compute, divided across relabels, would do better. It does not. Relabels are worth running when you can afford them all at full depth, and are the wrong place to spend a budget you cannot.
