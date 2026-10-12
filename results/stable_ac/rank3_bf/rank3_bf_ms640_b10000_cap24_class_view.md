# Relabeling classes: `rank3_bf_ms640_b10000_cap24`

The 640 presentations are 319 classes of copies (the same presentation after renaming x, y, X, Y, up to the order, rotation and inversion of the relators); class sizes 2: 318, 4: 1.

## How far a relabeling alone moves the search

Pairs of searches that differ only by the relabeling. Node gap = |a - b| / max(a, b) when both solve.

| searches | pairs | solved flag differs | both solve | same nodes | median gap | p90 gap | p99 gap |
|---|---|---|---|---|---|---|---|
| control | 324 | 0 (0.0%) | 307 | 60.6% | 0.0% | 15.4% | 31.9% |
| starts, word length 1 | 324 | 5 (1.5%) | 237 | 75.1% | 0.0% | 19.1% | 64.7% |
| starts, word length 2 | 332 | 0 (0.0%) | 258 | 63.6% | 0.0% | 28.6% | 55.7% |
| starts, word length 3 | 1,636 | 6 (0.4%) | 1,296 | 51.4% | 0.0% | 11.8% | 51.5% |
| starts, word length 4 | 2,988 | 18 (0.6%) | 2,346 | 49.9% | 0.1% | 19.1% | 85.2% |
| starts, word length 5 | 10,884 | 56 (0.5%) | 8,764 | 46.8% | 0.4% | 15.4% | 76.8% |
| starts, word length 6 | 26,892 | 147 (0.5%) | 21,410 | 42.4% | 1.1% | 20.3% | 86.5% |

## Headline counts, one vote per presentation and one per class

Gained = some start solves and the control does not. Cheaper = the best start uses fewer nodes than the control (a gain counts). Per class: the control and the starts both take their best copy.

| starts | per presentation | some start solves | gained | of those, the control solves a copy | lost | cheaper | cheaper by more than 17% | cheaper than every copy of the control | classes: control solves | some start solves | gained | lost | cheaper |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| words up to length 1 | 2 | 471 | 0 | 0 | 135 | 0 | 0 | 0 | 302 | 237 | 0 | 65 | 0 |
| words up to length 2 | 8 | 552 | 0 | 0 | 54 | 35 | 26 | 35 | 302 | 275 | 0 | 27 | 19 |
| words up to length 3 | 26 | 572 | 0 | 0 | 34 | 61 | 46 | 54 | 302 | 285 | 0 | 17 | 28 |
| words up to length 4 | 80 | 592 | 4 | 0 | 18 | 148 | 129 | 143 | 302 | 295 | 2 | 9 | 75 |
| words up to length 5 | 242 | 596 | 4 | 0 | 14 | 168 | 154 | 167 | 302 | 297 | 2 | 7 | 85 |
| words up to length 6 | 728 | 600 | 4 | 0 | 10 | 186 | 169 | 185 | 302 | 299 | 2 | 5 | 94 |

Control: 606 of 640 presentations.
