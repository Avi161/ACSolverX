# [2026-07-23] A good ordering feature is not automatically a good progress proxy [TRAP]

The user's insight — for a very hard presentation, reducing even a single knot can open opportunities worth a longer path — is correct and load-bearing as an *ordering* principle. `L + 8·K` (order by length plus eight times the knot count) takes the greedy from 17/40 to 23/40 on the train slice, and the phased `[<=16]L1[<=inf]K8+L1` to 25/40. The knots-first direction is real signal.

The trap is one step past that: assuming the same quantity that makes a good *ordering* also makes a good *progress metric* for the rows that never solve. It does not, and the two questions are independent.

## Why the question came up

The target is the second hump: Miller–Schupp presentations that do not solve within ten million greedy nodes. Nothing in this local program (budget ≤ 1,000) will solve them, so they produce no `solved` signal to rank orderings by. The tempting move is to rank them on a proxy — "which ordering reduces knots the most on the hard rows" — and report that as the second-hump heuristic.

## The gate, and the result

Before selecting on the proxy, test whether it predicts the goal *where the goal is observable*: the boundary rows, not solved at 500 nodes but solved by 1,000. For every (config, row) window there, join the knot-progress measured at the 500 mark against the eventual solve at 1,000. 187 windows.

```
P(solve by 1000 | dropped a knot by 500) = 0.10
P(solve by 1000 | no knot drop by 500)   = 0.14      <- higher, wrong direction
mean knot drop @500:  eventual solvers +0.62,  never solved +0.75
```

Knot-progress is very slightly *anti*-correlated with solving. And the obvious replacement is no better: length-progress (`start_total − min_total` reached by 500) runs +5.05 for solvers against +5.87 for the never-solved — again the wrong way, and near-constant because almost every search shortens something in its first hundred pops. **Neither checkpoint proxy forecasts a solve.**

The mechanism: at these budgets a solve is a discrete find-the-path event, not the endpoint of a smooth descent. A search that wanders into a structurally simpler but dead region racks up knot- and length-progress and never finishes; the search that finishes may have looked unremarkable at the 500 mark. `min_K_len` (prefer the shorter witness at equal knots) guards the wandering only partially.

## Rule

**Validate a progress proxy against the real objective on the rows where both are visible, before ranking anything you cannot solve on that proxy.** A feature earning its place in the heap ordering (measured by solves) says nothing about whether the value it reaches predicts a solve — those are different claims and the second needs its own evidence. When the proxy fails the gate, report the unsolvable tier on real solves only, and say plainly that partial progress there is not evidence of advantage. This is the same shape as [control-with-no-dynamic-range](control-with-no-dynamic-range.md): a metric with no proven link to the outcome is not a weak signal, it is no signal.
