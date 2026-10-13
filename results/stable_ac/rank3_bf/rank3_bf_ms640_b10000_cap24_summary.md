# Rank-3 brute force on ms640: budget 10,000, cap 24, every z-word to length 7

1,399,040 searches: 2,186 words on each of 640 presentations, 354 core-hours. Start `<x,y,z | r1, r2, Z·w>`; control `<x,y | r1, r2>` (identical to the null stabilization). Percentages are means over presentations of the per-presentation fraction of words.

## At 100 nodes (control solves 455/640)

| \|w\| | words | solved | on control-solved | on control-unsolved | faster than control | same | slower | lost | best single word (solves) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 2 | 53.6% | 75.4% | 0.0% | 0.0% | 0.0% | 75.4% | 24.6% | `x` (350) |
| 2 | 6 | 57.7% | 81.0% | 0.4% | 1.4% | 0.0% | 79.6% | 19.0% | `Xy` (379) |
| 3 | 18 | 56.9% | 79.9% | 0.1% | 0.6% | 0.0% | 79.3% | 20.1% | `xyX` (400) |
| 4 | 54 | 55.6% | 78.1% | 0.5% | 0.8% | 0.0% | 77.2% | 21.9% | `yXYx` (421) |
| 5 | 162 | 55.7% | 78.1% | 0.3% | 0.7% | 0.0% | 77.4% | 21.9% | `yyXYx` (447) |
| 6 | 486 | 55.6% | 78.0% | 0.3% | 0.6% | 0.0% | 77.4% | 22.0% | `yXXYxx` (424) |
| 7 | 1,458 | 55.7% | 78.3% | 0.2% | 0.5% | 0.0% | 77.7% | 21.7% | `yyyXYxY` (437) |

All lengths together, on control-solved presentations: faster 0.6%, same 0.0%, slower 77.6%, lost 21.8%.

Without the 3,718 (presentation, word) pairs where w is a whole rotation of a relator (the control in disguise: 0 faster, 0 same, 3063 slower): faster 0.6%, same 0.0%, slower 77.5%, lost 21.8%.

| words up to | words | solved by some word (oracle) | gained over control | some word faster than control | some word that is not a relator rotation faster |
|---|---|---|---|---|---|
| 1 | 2 | 350 | 0 | 0 | 0 |
| 2 | 8 | 408 | 2 | 31 | 31 |
| 3 | 26 | 442 | 4 | 49 | 49 |
| 4 | 80 | 480 | 28 | 71 | 71 |
| 5 | 242 | 487 | 35 | 77 | 77 |
| 6 | 728 | 501 | 49 | 84 | 84 |
| 7 | 2,186 | 511 | 56 | 86 | 86 |

Price of the oracle: running the words in shortlex order until the first solve reaches 511 presentations, median 10 nodes; it is cheaper than the control (or solves where the control does not) on 56.

One fixed word for all presentations: 0 words solve more presentations than the control, 0 the same. Chosen on one half, scored on the other:

- even->odd: `XYxyy` solves 227/320, control 231.
- odd->even: `yyXYx` solves 219/320, control 224.

Words that are a subword of a relator of their presentation solve 57.7% and are faster than the control 0.8% of the time; the other words 55.6% and 0.6%.

## At 1,000 nodes (control solves 554/640)

| \|w\| | words | solved | on control-solved | on control-unsolved | faster than control | same | slower | lost | best single word (solves) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 2 | 60.1% | 69.4% | 0.0% | 0.0% | 0.0% | 69.4% | 30.6% | `x` (403) |
| 2 | 6 | 68.4% | 79.0% | 0.0% | 1.3% | 0.1% | 77.7% | 21.0% | `yX` (449) |
| 3 | 18 | 69.8% | 80.6% | 0.0% | 0.7% | 0.0% | 80.0% | 19.4% | `Yxy` (478) |
| 4 | 54 | 68.6% | 79.2% | 0.2% | 1.2% | 0.0% | 77.9% | 20.8% | `yXYx` (506) |
| 5 | 162 | 67.3% | 77.8% | 0.2% | 1.0% | 0.0% | 76.8% | 22.2% | `yxYYX` (490) |
| 6 | 486 | 66.8% | 77.2% | 0.2% | 0.8% | 0.0% | 76.4% | 22.8% | `yyXYxY` (508) |
| 7 | 1,458 | 66.5% | 76.8% | 0.1% | 0.7% | 0.0% | 76.1% | 23.2% | `yxYYYXy` (512) |

All lengths together, on control-solved presentations: faster 0.7%, same 0.0%, slower 76.3%, lost 22.9%.

Without the 3,718 (presentation, word) pairs where w is a whole rotation of a relator (the control in disguise: 0 faster, 0 same, 3442 slower): faster 0.7%, same 0.0%, slower 76.2%, lost 23.0%.

| words up to | words | solved by some word (oracle) | gained over control | some word faster than control | some word that is not a relator rotation faster |
|---|---|---|---|---|---|
| 1 | 2 | 403 | 0 | 0 | 0 |
| 2 | 8 | 472 | 0 | 35 | 35 |
| 3 | 26 | 516 | 0 | 60 | 60 |
| 4 | 80 | 540 | 4 | 130 | 130 |
| 5 | 242 | 546 | 8 | 148 | 148 |
| 6 | 728 | 562 | 16 | 164 | 164 |
| 7 | 2,186 | 572 | 20 | 168 | 168 |

Price of the oracle: running the words in shortlex order until the first solve reaches 572 presentations, median 10 nodes; it is cheaper than the control (or solves where the control does not) on 20.

One fixed word for all presentations: 0 words solve more presentations than the control, 0 the same. Chosen on one half, scored on the other:

- even->odd: `YXYxyy` solves 252/320, control 281.
- odd->even: `yyyXYYx` solves 245/320, control 273.

Words that are a subword of a relator of their presentation solve 70.1% and are faster than the control 1.3% of the time; the other words 66.6% and 0.7%.

## At 10,000 nodes (control solves 606/640)

| \|w\| | words | solved | on control-solved | on control-unsolved | faster than control | same | slower | lost | best single word (solves) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 2 | 71.5% | 75.5% | 0.0% | 0.0% | 0.0% | 75.5% | 24.5% | `x` (471) |
| 2 | 6 | 80.2% | 84.7% | 0.0% | 1.2% | 0.1% | 83.5% | 15.3% | `yy` (526) |
| 3 | 18 | 80.7% | 85.2% | 0.0% | 0.6% | 0.0% | 84.6% | 14.8% | `xyX` (551) |
| 4 | 54 | 81.8% | 86.3% | 1.0% | 1.3% | 0.0% | 85.0% | 13.7% | `xYXy` (563) |
| 5 | 162 | 81.4% | 85.9% | 0.6% | 1.1% | 0.0% | 84.8% | 14.1% | `yyxYY` (570) |
| 6 | 486 | 81.0% | 85.4% | 1.3% | 0.9% | 0.0% | 84.5% | 14.6% | `yyxYXY` (572) |
| 7 | 1,458 | 80.7% | 85.2% | 0.9% | 0.8% | 0.0% | 84.4% | 14.8% | `XYYxyyy` (565) |

All lengths together, on control-solved presentations: faster 0.8%, same 0.0%, slower 84.5%, lost 14.7%.

Without the 3,718 (presentation, word) pairs where w is a whole rotation of a relator (the control in disguise: 0 faster, 0 same, 3580 slower): faster 0.8%, same 0.0%, slower 84.4%, lost 14.7%.

| words up to | words | solved by some word (oracle) | gained over control | some word faster than control | some word that is not a relator rotation faster |
|---|---|---|---|---|---|
| 1 | 2 | 471 | 0 | 0 | 0 |
| 2 | 8 | 552 | 0 | 35 | 35 |
| 3 | 26 | 572 | 0 | 61 | 61 |
| 4 | 80 | 592 | 4 | 144 | 144 |
| 5 | 242 | 596 | 4 | 164 | 164 |
| 6 | 728 | 600 | 4 | 182 | 182 |
| 7 | 2,186 | 608 | 6 | 190 | 190 |

Price of the oracle: running the words in shortlex order until the first solve reaches 608 presentations, median 11 nodes; it is cheaper than the control (or solves where the control does not) on 6.

One fixed word for all presentations: 0 words solve more presentations than the control, 0 the same. Chosen on one half, scored on the other:

- even->odd: `YXYxyy` solves 280/320, control 304.
- odd->even: `yyxYXY` solves 282/320, control 302.

Words that are a subword of a relator of their presentation solve 82.3% and are faster than the control 1.4% of the time; the other words 80.8% and 0.8%.

The 6 presentations some word solves and the control does not, against the control at 100,000 nodes: the control solves 6 of them; the best word (hindsight) uses fewer nodes than the control on 6, and the words run in shortlex order until the first solve on 0.

## Relator subwords (the CoV word set, searched in rank 3)

69,816 rows, 59,486 in the CoV family.

- proper: some subword solves 592/640 (gained over control 4), mean solve rate 80.9%, faster than control 1.3%.
- all: some subword solves 610/640 (gained over control 4), mean solve rate 82.4%, faster than control 1.1%.

| | presentations solved |
|---|---|
| control | 606 |
| rank 3, some relator subword | 592 |
| CoV, some class | 626 |
| control or rank 3 | 610 |
| control or CoV | 626 |

Same presentation and same word, on the 9,759 (presentation, word) pairs that have a CoV row (CoV keeps one row per class of outputs, under one representative word): rank 3 uses fewer nodes than the best CoV start 725 times, the same 456, more 6,018; only rank 3 solves 36, only CoV 1,350, neither 1,174. CoV rows ran at cap max(24, longest relator + 16), median 33; rank 3 at cap 24.

Control at larger budgets: 455 at 100, 554 at 1,000, 606 at 10,000, 634 at 100,000.
