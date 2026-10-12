# Relabeling classes: `rankn_bf_ms640_b1000_cap24_r5`

The 640 presentations are 319 classes of copies (the same presentation after renaming x, y, X, Y, up to the order, rotation and inversion of the relators); class sizes 2: 318, 4: 1.

## How far a relabeling alone moves the search

Pairs of searches that differ only by the relabeling. Node gap = |a - b| / max(a, b) when both solve.

| searches | pairs | solved flag differs | both solve | same nodes | median gap | p90 gap | p99 gap |
|---|---|---|---|---|---|---|---|
| control | 324 | 0 (0.0%) | 281 | 65.8% | 0.0% | 15.4% | 30.4% |

## Headline counts, one vote per presentation and one per class

Gained = some start solves and the control does not. Cheaper = the best start uses fewer nodes than the control (a gain counts). Per class: the control and the starts both take their best copy.

| starts | per presentation | some start solves | gained | of those, the control solves a copy | lost | cheaper | cheaper by more than 17% | cheaper than every copy of the control | classes: control solves | some start solves | gained | lost | cheaper |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| every 3 words up to length 2 (rank 5) | 120 | 416 | 0 | 0 | 138 | 12 | 3 | 9 | 276 | 209 | 0 | 67 | 8 |

Control: 554 of 640 presentations.
