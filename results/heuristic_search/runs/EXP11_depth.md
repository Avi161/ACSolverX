# EXP-11 — does a depth term help? (the axis the earlier rounds argued away)

A segment may carry `depth: w`, adding `w · depth` to its score — the `g` of a weighted A*, with the structural features as `h`. Positive prefers **shallow** states, negative prefers **deep** ones. Swept over the orderings that already won, so a gain must beat a strong incumbent, not the length baseline.

`all` = depth in every segment · `long` = only the structural climb · `short` = only the endgame (the placement control).

## Budget 500

| base | placement | d=-2 | d=-1 | d=-0.5 | d=-0.25 | d=0.25 | d=0.5 | d=1 | d=2 | d=4 | d=0 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| length | all | 12 | 12 | 11 | 13 | **18** | 15 | 12 | 8 | 3 | 17 |
| phasedK8 | all | 20 | 18 | 22 | 23 | 24 | 21 | 19 | 16 | 11 | 25 |
| phasedK8 | long | 20 | 18 | 22 | 22 | 24 | 21 | 19 | 19 | 15 | 25 |
| phasedK8 | short | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 14 | 25 |
| win500 | all | 21 | 23 | 22 | 22 | 25 | 22 | 19 | 16 | 11 | 27 |
| win500 | long | 21 | 23 | 22 | 22 | 25 | 23 | 21 | 19 | 15 | 27 |
| win500 | short | 27 | 27 | 27 | 27 | 27 | 27 | 27 | 27 | 16 | 27 |
| win1000 | all | 18 | 17 | 17 | 20 | 22 | 23 | 22 | 18 | 12 | 25 |
| win1000 | long | 18 | 17 | 17 | 20 | 22 | 23 | 23 | 21 | 17 | 25 |
| win1000 | short | 25 | 25 | 24 | 24 | 25 | 25 | 24 | 23 | 16 | 25 |

## Budget 1000

| base | placement | d=-2 | d=-1 | d=-0.5 | d=-0.25 | d=0.25 | d=0.5 | d=1 | d=2 | d=4 | d=0 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| length | all | 13 | 12 | 12 | 15 | 20 | 17 | 14 | 10 | 3 | 20 |
| phasedK8 | all | 21 | 18 | 22 | 24 | 24 | 23 | 20 | 21 | 15 | 27 |
| phasedK8 | long | 21 | 18 | 22 | 24 | 24 | 23 | 20 | 21 | 16 | 27 |
| phasedK8 | short | 27 | 27 | 27 | 27 | 27 | 27 | 27 | 27 | 23 | 27 |
| win500 | all | 22 | 23 | 24 | 23 | 25 | 24 | 21 | 19 | 15 | 27 |
| win500 | long | 22 | 23 | 24 | 23 | 25 | 24 | 22 | 20 | 16 | 27 |
| win500 | short | 27 | 27 | 27 | 27 | 27 | 27 | 27 | 27 | 25 | 27 |
| win1000 | all | 18 | 18 | 22 | 29 | 27 | 25 | 25 | 21 | 17 | 29 |
| win1000 | long | 18 | 18 | 22 | 29 | 27 | 25 | 25 | 21 | 19 | 29 |
| win1000 | short | 29 | 29 | 29 | 29 | 29 | 29 | 29 | 29 | 27 | 29 |

## Verdict

1 depth arms beat their own zero-depth incumbent:

- budget 500, `length` + depth 0.25 @all: **18/40** vs 17/40

A single arm beating its incumbent on 40 rows is within the noise of a 216-arm sweep; treat a gain as real only if it repeats at both budgets and in the same placement.

