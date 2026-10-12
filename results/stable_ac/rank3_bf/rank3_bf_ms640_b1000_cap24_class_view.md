# Relabeling classes: `rank3_bf_ms640_b1000_cap24`

The 640 presentations are 319 classes of copies (the same presentation after renaming x, y, X, Y, up to the order, rotation and inversion of the relators); class sizes 2: 318, 4: 1.

## How far a relabeling alone moves the search

Pairs of searches that differ only by the relabeling. Node gap = |a - b| / max(a, b) when both solve.

| searches | pairs | solved flag differs | both solve | same nodes | median gap | p90 gap | p99 gap |
|---|---|---|---|---|---|---|---|
| control | 324 | 0 (0.0%) | 281 | 65.8% | 0.0% | 15.4% | 30.4% |
| starts, word length 1 | 324 | 5 (1.5%) | 203 | 87.2% | 0.0% | 1.1% | 42.1% |
| starts, word length 2 | 332 | 0 (0.0%) | 218 | 74.8% | 0.0% | 14.3% | 55.5% |
| starts, word length 3 | 1,636 | 10 (0.6%) | 1,145 | 57.9% | 0.0% | 11.7% | 43.2% |
| starts, word length 4 | 2,988 | 28 (0.9%) | 1,959 | 59.6% | 0.0% | 16.5% | 75.7% |
| starts, word length 5 | 10,884 | 74 (0.7%) | 7,262 | 56.1% | 0.0% | 14.3% | 74.3% |
| starts, word length 6 | 26,892 | 289 (1.1%) | 17,579 | 51.4% | 0.0% | 18.2% | 83.1% |
| starts, word length 7 | 86,436 | 1,103 (1.3%) | 56,678 | 53.4% | 0.0% | 18.2% | 75.5% |
| starts, word length 8 | 242,028 | 3,522 (1.5%) | 157,618 | 51.3% | 0.0% | 18.8% | 79.5% |
| starts, word length 9 | 743,364 | 12,385 (1.7%) | 484,629 | 49.8% | 0.3% | 20.0% | 81.9% |

## Headline counts, one vote per presentation and one per class

Gained = some start solves and the control does not. Cheaper = the best start uses fewer nodes than the control (a gain counts). Per class: the control and the starts both take their best copy.

| starts | per presentation | some start solves | gained | of those, the control solves a copy | lost | cheaper | cheaper by more than 17% | cheaper than every copy of the control | classes: control solves | some start solves | gained | lost | cheaper |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| words up to length 1 | 2 | 403 | 0 | 0 | 151 | 0 | 0 | 0 | 276 | 203 | 0 | 73 | 0 |
| words up to length 2 | 8 | 472 | 0 | 0 | 82 | 35 | 26 | 35 | 276 | 235 | 0 | 41 | 19 |
| words up to length 3 | 26 | 516 | 0 | 0 | 38 | 60 | 46 | 54 | 276 | 258 | 0 | 18 | 28 |
| words up to length 4 | 80 | 540 | 4 | 0 | 18 | 134 | 115 | 129 | 276 | 269 | 2 | 9 | 68 |
| words up to length 5 | 242 | 546 | 8 | 0 | 16 | 156 | 142 | 155 | 276 | 272 | 4 | 8 | 79 |
| words up to length 6 | 728 | 562 | 16 | 0 | 8 | 180 | 163 | 179 | 276 | 280 | 8 | 4 | 91 |
| words up to length 7 | 2,186 | 572 | 20 | 0 | 2 | 188 | 174 | 185 | 276 | 285 | 10 | 1 | 94 |
| words up to length 8 | 6,560 | 576 | 22 | 0 | 0 | 193 | 177 | 190 | 276 | 287 | 11 | 0 | 97 |
| words up to length 9 | 19,682 | 576 | 22 | 0 | 0 | 198 | 187 | 198 | 276 | 287 | 11 | 0 | 102 |

Control: 554 of 640 presentations.
