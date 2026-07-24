# EXP-12 — the 124 unsolved AC-classes, under the best orderings

Every class from `unsolved_124_aca_classes.csv`, started from each of its **8 signed-permutation relabels** (980 starts over 124 classes), at budget 1000 with cap 64. A relabel is the same presentation under a rename of the generators, so it is the same problem — but the greedy reads strings, so each image is a different search and any one solving settles the class.

Scored on solves alone — EXP-07 showed no checkpoint proxy predicts a solve, so `min_total`/`min_K` below are for reading, not ranking.

**No class solved, under any ordering, from any of its 8 relabels.** That is the expected result and it is now measured over the whole target set rather than assumed from a six-row sample: these classes survived a 10^6-node search, and 1000 nodes is three orders of magnitude short. The heuristic's demonstrated value is on the decidable tier; carrying it to these classes means running it at a Colab-scale budget, which this program cannot do locally.

## What each ordering reached (descriptive — not a ranking)

| ordering | solved | mean shortest total reached | classes reaching fewer knots |
|---|---|---|---|
| baseline (length) | 0/980 | 19.8 | 74/124 |
| phased K+xyimb (win500) | 0/980 | 19.6 | 94/124 |
| phased knot climb (win1000) | 0/980 | 19.7 | 94/124 |
| phased blocks | 0/980 | 19.7 | 92/124 |

