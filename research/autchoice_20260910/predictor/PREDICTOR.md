# Can anything cheap predict which Aut(F2)-image is cheapest to search from?

Data: `atlas.jsonl` -- 124 rows x 13 radius-2 images = 1612 S20_MK2 runs at budget 20,000 (715 solved, 897 censored at 20,000).  Built by `evaluate.py` (numbers) and `report.py` (this file); `results.json` holds every value below.

## Protocol

- **Group-disjoint CV.** 5 outer folds by *row* (a row's 13 images are never split; `data.split` asserts it), stratified by level, seed 0; fold sizes [27, 25, 25, 24, 23] rows.
- **Baselines** need no fitting and are scored on all 124 rows; `random` is the per-row mean over 20 seeds.
- **Learned rankers** are fitted on the 4 training folds and scored on the held-out fold only.  The L2 strength of a pairwise model is chosen inside the training folds by a 4-fold inner group CV (seed 1) on mean top1_regret over the grid [0.01, 0.1, 1.0, 10.0, 100.0]; the rule search and the seq prior are fitted on the training folds only.
- **Primary metric** (declared before looking): mean `top1_regret` = log10(cost of the pick) - log10(cost of the best image in the ball), censored = 20,000.  `top1_solved` / `top3_solved` / `top1_solved@5k`: the pick (best of the top 3; the pick at 5,000 pops) solves.  `rank_of_best`: position the ranker gives the truly cheapest image (1 = perfect; ties at the minimum take the best-placed one, so an all-censored ball scores 1 for everyone).
- **Portfolio at equal compute**: the top-k images are run with 20,000/k pops each; a row is solved iff some top-k image has atlas cost <= 20,000 // k.
- **Selection caveat.** Picking the shipped variant among the four pairwise variants on the same outer folds is a small selection step (4 candidates, 124 rows); the per-fold table shows the spread.

## Rankers

| ranker | what it does |
|---|---|
| identity | the row as given first ("do nothing"), then the atlas BFS order |
| shortest | smallest total length, ties by the relator strings |
| lowest_h | smallest `h_s20mk2 = L + 20 S + 2 MK` of the image itself, ties by (depth, seq) |
| depth2_first | depth-2 images, then depth-1, then the identity; ties by lowest_h |
| random | a seeded permutation |
| seq_prior | order the 13 sequences by their mean within-row cost rank on the training rows (no state feature) |
| rule | the best of 1,624 one- and two-feature orderings on the training rows (single feature either sign, with/without depth-2 priority; two-feature within-row rank sums) |
| pairwise | logistic regression on standardised feature differences of every (cheaper, dearer) image pair inside a row, L2, Newton; score = w.x, lower first |
| pairwise_rownorm | the same with every row given total pair weight 1 |
| pairwise_state_only | pairwise on the 28 state features only (no depth / generator columns) |
| pairwise_gen_only | pairwise on depth, is_identity, same_gen and the generator one-hots only (no state feature) |
| pairwise_rownorm_hedge | pairwise_rownorm plus an *identity bonus*: keep the row as given unless an image scores lower by more than the bonus (bonus chosen on inner out-of-fold scores) |

## Held-out metrics, all 124 rows

| ranker | top1_regret | top1_solved /124 | top3_solved /124 | top1_solved@5k /124 | rank_of_best | vs identity (top1 solved) W/L | vs lowest_h W/L | vs depth2_first W/L |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| identity | 0.720 | 94 | 101 | 64 | 8.58 | 0/0 | 28/5 | 39/17 |
| shortest | 1.040 | 62 | 97 | 33 | 6.23 | 2/34 | 2/11 | 7/17 |
| lowest_h | 0.961 | 71 | 105 | 41 | 5.86 | 5/28 | 0/0 | 13/14 |
| depth2_first | 0.787 | 72 | 105 | 50 | 4.16 | 17/39 | 14/13 | 0/0 |
| random | 0.979 | 54 | 94 | 35 | 6.53 | 23/90 | 46/67 | 46/68 |
| seq_prior | 0.720 | 94 | 104 | 64 | 5.91 | 0/0 | 28/5 | 39/17 |
| rule | 0.698 | 80 | 112 | 57 | 5.60 | 11/25 | 25/16 | 24/16 |
| pairwise_gen_only | 0.786 | 89 | 110 | 59 | 5.55 | 1/6 | 23/5 | 33/16 |
| pairwise_state_only | 0.443 | 92 | 113 | 71 | 4.15 | 14/16 | 33/12 | 34/14 |
| pairwise | 0.518 | 95 | 110 | 68 | 4.24 | 10/9 | 31/7 | 36/13 |
| pairwise_rownorm | 0.434 | 99 | 112 | 76 | 4.10 | 13/8 | 33/5 | 36/9 |
| pairwise_rownorm_hedge | 0.457 | 99 | 112 | 75 | 4.15 | 12/7 | 33/5 | 37/10 |
| oracle | 0.000 | 119 | 119 | 101 | 1.00 | 25/0 | 48/0 | 47/0 |

`random` counts are means over seeds, hence fractional.

### Top-1 solves at 20,000 by level (rows solved / rows)

| ranker | L1 /6 | L2 /24 | L3 /20 | L4 /26 | L5 /20 | L9 /28 | all |
|---|---:|---:|---:|---:|---:|---:|---:|
| identity | 6 | 24 | 18 | 25 | 15 | 6 | 94 |
| shortest | 1 | 4 | 15 | 19 | 17 | 6 | 62 |
| lowest_h | 1 | 7 | 16 | 22 | 17 | 8 | 71 |
| depth2_first | 0 | 4 | 14 | 21 | 15 | 18 | 72 |
| random | 4 | 13 | 10 | 13 | 7 | 5 | 54 |
| seq_prior | 6 | 24 | 18 | 25 | 15 | 6 | 94 |
| rule | 4 | 15 | 13 | 18 | 13 | 17 | 80 |
| pairwise_gen_only | 6 | 20 | 17 | 24 | 16 | 6 | 89 |
| pairwise_state_only | 6 | 19 | 14 | 21 | 15 | 17 | 92 |
| pairwise | 6 | 20 | 16 | 24 | 13 | 16 | 95 |
| pairwise_rownorm | 6 | 22 | 15 | 23 | 16 | 17 | 99 |
| pairwise_rownorm_hedge | 6 | 22 | 15 | 24 | 15 | 17 | 99 |
| oracle | 6 | 24 | 20 | 25 | 18 | 26 | 119 |

### Top-1 regret by level (mean log10 cost above the best image)

| ranker | L1 | L2 | L3 | L4 | L5 | L9 | all |
|---|---:|---:|---:|---:|---:|---:|---:|
| identity | 0.617 | 0.394 | 0.793 | 0.639 | 1.008 | 0.838 | 0.720 |
| shortest | 1.860 | 1.410 | 0.815 | 0.923 | 1.008 | 0.838 | 1.040 |
| lowest_h | 2.092 | 1.308 | 0.885 | 0.809 | 0.840 | 0.705 | 0.961 |
| depth2_first | 2.117 | 1.410 | 0.828 | 0.753 | 0.453 | 0.207 | 0.787 |
| random | 1.335 | 0.930 | 0.860 | 1.004 | 1.265 | 0.802 | 0.979 |
| seq_prior | 0.617 | 0.394 | 0.793 | 0.639 | 1.008 | 0.838 | 0.720 |
| rule | 1.464 | 0.851 | 0.815 | 0.771 | 0.474 | 0.413 | 0.698 |
| pairwise_gen_only | 0.617 | 0.643 | 0.801 | 0.717 | 1.008 | 0.838 | 0.786 |
| pairwise_state_only | 0.797 | 0.621 | 0.601 | 0.337 | 0.216 | 0.364 | 0.443 |
| pairwise | 0.569 | 0.605 | 0.640 | 0.562 | 0.381 | 0.402 | 0.518 |
| pairwise_rownorm | 0.569 | 0.473 | 0.535 | 0.590 | 0.163 | 0.350 | 0.434 |
| pairwise_rownorm_hedge | 0.569 | 0.491 | 0.653 | 0.590 | 0.163 | 0.350 | 0.457 |

### Top-1 solves at 5,000 by level

| ranker | L1 /6 | L2 /24 | L3 /20 | L4 /26 | L5 /20 | L9 /28 | all |
|---|---:|---:|---:|---:|---:|---:|---:|
| identity | 6 | 24 | 8 | 13 | 11 | 2 | 64 |
| shortest | 1 | 0 | 8 | 11 | 11 | 2 | 33 |
| lowest_h | 0 | 3 | 6 | 13 | 13 | 6 | 41 |
| depth2_first | 0 | 0 | 8 | 14 | 12 | 16 | 50 |
| random | 3 | 9 | 6 | 7 | 6 | 3 | 35 |
| seq_prior | 6 | 24 | 8 | 13 | 11 | 2 | 64 |
| rule | 2 | 9 | 9 | 13 | 12 | 12 | 57 |
| pairwise_gen_only | 6 | 19 | 8 | 13 | 11 | 2 | 59 |
| pairwise_state_only | 5 | 14 | 10 | 16 | 13 | 13 | 71 |
| pairwise | 6 | 15 | 9 | 13 | 12 | 13 | 68 |
| pairwise_rownorm | 6 | 19 | 10 | 13 | 14 | 14 | 76 |
| pairwise_rownorm_hedge | 6 | 19 | 9 | 13 | 14 | 14 | 75 |
| oracle | 6 | 24 | 16 | 20 | 15 | 20 | 101 |

### By form: top-1 solves at 20,000 / regret

| ranker | autmin (n=60) | ms_raw (n=19) | original (n=45) |
|---|---:|---:|---:|
| identity | 37 / 0.966 | 12 / 0.249 | 45 / 0.590 |
| shortest | 37 / 0.966 | 11 / 0.239 | 14 / 1.475 |
| lowest_h | 37 / 0.878 | 15 / 0.239 | 19 / 1.377 |
| depth2_first | 44 / 0.465 | 13 / 0.237 | 15 / 1.448 |
| random | 22 / 1.079 | 6 / 0.337 | 26 / 1.116 |
| seq_prior | 37 / 0.966 | 12 / 0.249 | 45 / 0.590 |
| rule | 42 / 0.618 | 9 / 0.229 | 29 / 1.003 |
| pairwise_gen_only | 37 / 0.966 | 12 / 0.242 | 40 / 0.775 |
| pairwise_state_only | 41 / 0.379 | 12 / 0.269 | 39 / 0.602 |
| pairwise | 43 / 0.464 | 12 / 0.239 | 40 / 0.708 |
| pairwise_rownorm | 45 / 0.331 | 13 / 0.238 | 41 / 0.655 |
| pairwise_rownorm_hedge | 45 / 0.368 | 13 / 0.245 | 41 / 0.665 |
| oracle | 58 / 0.000 | 16 / 0.000 | 45 / 0.000 |

### Portfolio at equal compute (rows solved with the top-k images at 20,000/k pops each)

| ranker | k=1 (20,000 pops each) | k=2 (10,000 pops each) | k=3 (6,666 pops each) | k=5 (4,000 pops each) | k=13 (1,538 pops each) |
|---|---:|---:|---:|---:|---:|
| identity | 94 | 87 | 86 | 85 | 75 |
| shortest | 62 | 67 | 79 | 90 | 75 |
| lowest_h | 71 | 79 | 89 | 92 | 75 |
| depth2_first | 72 | 92 | 88 | 92 | 75 |
| random | 54 | 67 | 74 | 82 | 75 |
| seq_prior | 94 | 91 | 89 | 92 | 75 |
| rule | 80 | 84 | 90 | 92 | 75 |
| pairwise_gen_only | 89 | 98 | 90 | 89 | 75 |
| pairwise_state_only | 92 | 97 | 92 | 93 | 75 |
| pairwise | 95 | 95 | 92 | 97 | 75 |
| pairwise_rownorm | 99 | 94 | 95 | 95 | 75 |
| pairwise_rownorm_hedge | 99 | 95 | 95 | 95 | 75 |
| oracle | 119 | 109 | 104 | 100 | 75 |

Level 9 only (28 representatives plain greedy cannot solve at 10M):

| ranker | k=1 | k=2 | k=3 | k=5 | k=13 |
|---|---:|---:|---:|---:|---:|
| identity | 6 | 7 | 7 | 8 | 10 |
| shortest | 6 | 9 | 9 | 14 | 10 |
| lowest_h | 8 | 12 | 15 | 17 | 10 |
| depth2_first | 18 | 21 | 20 | 19 | 10 |
| random | 5 | 8 | 10 | 10 | 10 |
| seq_prior | 6 | 13 | 15 | 13 | 10 |
| rule | 17 | 17 | 20 | 18 | 10 |
| pairwise_gen_only | 6 | 18 | 16 | 13 | 10 |
| pairwise_state_only | 17 | 19 | 17 | 17 | 10 |
| pairwise | 16 | 18 | 18 | 18 | 10 |
| pairwise_rownorm | 17 | 18 | 18 | 18 | 10 |
| pairwise_rownorm_hedge | 17 | 18 | 18 | 18 | 10 |
| oracle | 26 | 23 | 21 | 19 | 10 |

### Hedged portfolio: the row as given plus the top k-1 predicted images, 20,000/k pops each

(k=1 is the identity alone; k=13 is the whole ball.  For the oracle the k-1 extra images are the truly cheapest ones.)

| ranker | k=1 (20,000 pops each) | k=2 (10,000 pops each) | k=3 (6,666 pops each) | k=5 (4,000 pops each) | k=13 (1,538 pops each) |
|---|---:|---:|---:|---:|---:|
| identity | 94 | 87 | 86 | 85 | 75 |
| shortest | 94 | 90 | 86 | 90 | 75 |
| lowest_h | 94 | 91 | 88 | 90 | 75 |
| depth2_first | 94 | 98 | 98 | 97 | 75 |
| random | 94 | 88 | 86 | 84 | 75 |
| seq_prior | 94 | 91 | 89 | 92 | 75 |
| rule | 94 | 96 | 94 | 96 | 75 |
| pairwise_gen_only | 94 | 99 | 91 | 89 | 75 |
| pairwise_state_only | 94 | 97 | 99 | 96 | 75 |
| pairwise | 94 | 96 | 96 | 97 | 75 |
| pairwise_rownorm | 94 | 96 | 95 | 95 | 75 |
| pairwise_rownorm_hedge | 94 | 96 | 95 | 95 | 75 |
| oracle | 94 | 109 | 104 | 100 | 75 |

Level 9 only:

| ranker | k=1 | k=2 | k=3 | k=5 | k=13 |
|---|---:|---:|---:|---:|---:|
| identity | 6 | 7 | 7 | 8 | 10 |
| shortest | 6 | 9 | 9 | 14 | 10 |
| lowest_h | 6 | 9 | 12 | 15 | 10 |
| depth2_first | 6 | 17 | 19 | 19 | 10 |
| random | 6 | 9 | 10 | 9 | 10 |
| seq_prior | 6 | 13 | 15 | 13 | 10 |
| rule | 6 | 15 | 16 | 18 | 10 |
| pairwise_gen_only | 6 | 18 | 16 | 13 | 10 |
| pairwise_state_only | 6 | 17 | 19 | 16 | 10 |
| pairwise | 6 | 16 | 17 | 18 | 10 |
| pairwise_rownorm | 6 | 17 | 17 | 18 | 10 |
| pairwise_rownorm_hedge | 6 | 17 | 17 | 18 | 10 |
| oracle | 6 | 23 | 21 | 19 | 10 |

### Share of the identity-to-oracle gap closed (top-1 pick)

| ranker | all @20k | all @5k | level 9 @20k | level 9 @5k |
|---|---:|---:|---:|---:|
| identity | 0.000 | 0.000 | 0.000 | 0.000 |
| shortest | -1.280 | -0.838 | 0.000 | 0.000 |
| lowest_h | -0.920 | -0.622 | 0.100 | 0.222 |
| depth2_first | -0.880 | -0.378 | 0.600 | 0.778 |
| random | -1.600 | -0.784 | -0.050 | 0.056 |
| seq_prior | 0.000 | 0.000 | 0.000 | 0.000 |
| rule | -0.560 | -0.189 | 0.550 | 0.556 |
| pairwise_gen_only | -0.200 | -0.135 | 0.000 | 0.000 |
| pairwise_state_only | -0.080 | 0.189 | 0.550 | 0.611 |
| pairwise | 0.040 | 0.108 | 0.500 | 0.611 |
| pairwise_rownorm | 0.200 | 0.324 | 0.550 | 0.667 |
| pairwise_rownorm_hedge | 0.200 | 0.297 | 0.550 | 0.667 |

(gap = oracle 119 - identity 94 = 25 rows at 20k; at 5k oracle 101 - identity 64; level 9: 26 - 6.)

## The pairwise model

Shipped variant: **pairwise_rownorm** (best outer-CV primary metric; order ['pairwise_rownorm', 'pairwise_state_only', 'pairwise_rownorm_hedge', 'pairwise', 'pairwise_gen_only']), weights of `pairwise_rownorm` refitted on all 124 rows with lambda = 1.0 and identity bonus 0.0 (medians of the per-fold choices) -> `weights.json`.

### Per outer fold

| variant | fold | test rows | train pairs | chosen lambda | identity bonus | top1_regret | top1_solved | top3_solved | rank_of_best |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| pairwise | 0 | 27 | 4744 | 100.0 | - | 0.403 | 0.889 | 0.926 | 4.07 |
| pairwise | 1 | 25 | 4980 | 1.0 | - | 0.662 | 0.720 | 0.920 | 5.12 |
| pairwise | 2 | 25 | 4979 | 100.0 | - | 0.478 | 0.760 | 0.960 | 3.40 |
| pairwise | 3 | 24 | 5064 | 100.0 | - | 0.449 | 0.750 | 0.792 | 4.08 |
| pairwise | 4 | 23 | 5233 | 1.0 | - | 0.613 | 0.696 | 0.826 | 4.57 |
| pairwise_rownorm | 0 | 27 | 4744 | 1.0 | - | 0.298 | 0.926 | 0.926 | 3.85 |
| pairwise_rownorm | 1 | 25 | 4980 | 1.0 | - | 0.633 | 0.760 | 0.920 | 5.24 |
| pairwise_rownorm | 2 | 25 | 4979 | 1.0 | - | 0.362 | 0.880 | 0.960 | 3.12 |
| pairwise_rownorm | 3 | 24 | 5064 | 1.0 | - | 0.449 | 0.708 | 0.833 | 3.88 |
| pairwise_rownorm | 4 | 23 | 5233 | 10.0 | - | 0.442 | 0.696 | 0.870 | 4.48 |
| pairwise_rownorm_hedge | 0 | 27 | 4744 | 1.0 | 0.25 | 0.397 | 0.889 | 0.926 | 3.93 |
| pairwise_rownorm_hedge | 1 | 25 | 4980 | 1.0 | 0.0 | 0.633 | 0.760 | 0.920 | 5.24 |
| pairwise_rownorm_hedge | 2 | 25 | 4979 | 1.0 | 0.0 | 0.362 | 0.880 | 0.960 | 3.12 |
| pairwise_rownorm_hedge | 3 | 24 | 5064 | 1.0 | 0.5 | 0.454 | 0.750 | 0.833 | 4.04 |
| pairwise_rownorm_hedge | 4 | 23 | 5233 | 10.0 | 0.0 | 0.442 | 0.696 | 0.870 | 4.48 |
| pairwise_state_only | 0 | 27 | 4744 | 10.0 | - | 0.380 | 0.815 | 0.963 | 3.89 |
| pairwise_state_only | 1 | 25 | 4980 | 1.0 | - | 0.551 | 0.720 | 0.920 | 5.08 |
| pairwise_state_only | 2 | 25 | 4979 | 1.0 | - | 0.353 | 0.840 | 0.920 | 3.20 |
| pairwise_state_only | 3 | 24 | 5064 | 10.0 | - | 0.537 | 0.583 | 0.875 | 3.96 |
| pairwise_state_only | 4 | 23 | 5233 | 0.01 | - | 0.402 | 0.739 | 0.870 | 4.65 |
| pairwise_gen_only | 0 | 27 | 4744 | 0.01 | - | 0.936 | 0.741 | 0.889 | 6.30 |
| pairwise_gen_only | 1 | 25 | 4980 | 0.01 | - | 0.706 | 0.760 | 0.920 | 5.96 |
| pairwise_gen_only | 2 | 25 | 4979 | 0.01 | - | 0.816 | 0.720 | 0.880 | 3.92 |
| pairwise_gen_only | 3 | 24 | 5064 | 0.01 | - | 0.751 | 0.667 | 0.917 | 6.04 |
| pairwise_gen_only | 4 | 23 | 5233 | 0.01 | - | 0.700 | 0.696 | 0.826 | 5.48 |

Inner out-of-fold regret by identity bonus (variant `pairwise_rownorm`, training rows of each fold; the chosen bonus is the minimum):

| fold | bonus 0.0 | bonus 0.25 | bonus 0.5 | bonus 0.75 | bonus 1.0 | bonus 1.5 | bonus 2.0 | bonus 3.0 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 0.462 | 0.446 | 0.477 | 0.518 | 0.531 | 0.595 | 0.676 | 0.716 |
| 1 | 0.385 | 0.410 | 0.411 | 0.448 | 0.546 | 0.656 | 0.677 | 0.723 |
| 2 | 0.440 | 0.443 | 0.484 | 0.492 | 0.566 | 0.609 | 0.645 | 0.688 |
| 3 | 0.453 | 0.446 | 0.446 | 0.493 | 0.568 | 0.650 | 0.696 | 0.728 |
| 4 | 0.415 | 0.428 | 0.485 | 0.536 | 0.646 | 0.728 | 0.736 | 0.736 |

### Fixed-lambda sensitivity (variant `pairwise`, held-out folds; NOT the selection procedure)

| lambda | top1_regret | top1_solved | top3_solved | top1_solved@5k | rank_of_best |
|---|---:|---:|---:|---:|---:|
| 0.01 | 0.536 | 93 | 112 | 66 | 4.10 |
| 0.1 | 0.529 | 93 | 112 | 67 | 4.11 |
| 1.0 | 0.521 | 94 | 112 | 68 | 4.10 |
| 10.0 | 0.495 | 92 | 112 | 70 | 4.08 |
| 100.0 | 0.484 | 97 | 111 | 72 | 4.21 |

### Weights (standardised features; negative = the image looks cheaper when the feature is larger)

| # | feature | w |
|---|---:|---:|
| 1 | once_letter | +0.658 |
| 2 | ey1 | -0.658 |
| 3 | ey2 | -0.636 |
| 4 | B1 | -0.524 |
| 5 | Bmax | -0.454 |
| 6 | density | +0.300 |
| 7 | Bmaxrun | +0.247 |
| 8 | Bspread | +0.247 |
| 9 | ex1 | -0.241 |
| 10 | ratio | -0.240 |
| 11 | MK | +0.225 |
| 12 | S | +0.220 |
| 13 | h_s20mk2 | +0.206 |
| 14 | mK | -0.205 |
| 15 | is_identity | -0.183 |
| 16 | gen2_8 | +0.169 |
| 17 | gen2_14 | -0.168 |
| 18 | delta_len | +0.136 |
| 19 | gen2_15 | -0.130 |
| 20 | Lmin | +0.129 |
| 21 | min_len | +0.129 |
| 22 | xyimb | -0.122 |
| 23 | L | +0.120 |
| 24 | total_len | +0.120 |
| 25 | same_gen | -0.094 |

Columns absent from the table have weight exactly 0 (constant in the atlas: the AUTOS indices other than 8, 9, 14, 15 never occur, `Bmin` and `once_gen` are constant).  `delta_len` and `total_len` are collinear inside a row (the row offset cancels in a pairwise difference) so the L2 penalty splits their weight; likewise `is_identity` and `depth`.

## Rule search and seq prior (per fold)

| fold | rule selected on the training rows | train regret | held-out regret | held-out top1_solved |
|---|---:|---:|---:|---:|
| 0 | ranksum(low MK, high ex1) | 0.599 | 0.734 | 0.704 |
| 1 | ranksum(high ey1, high ey2) | 0.530 | 0.777 | 0.600 |
| 2 | ranksum(low Lmax, high ratio) | 0.575 | 0.684 | 0.720 |
| 3 | ranksum(low Lmax, high ratio) | 0.562 | 0.743 | 0.583 |
| 4 | ranksum(high ey1, high ey2) | 0.589 | 0.540 | 0.609 |

Seq prior (mean within-row cost rank of each sequence, training rows of each fold; lower = cheaper):

| fold | id | 15 15 | 15 | 9 9 | 9 | 15 9 | 14 | 9 15 | 14 14 | 8 | 8 8 | 8 14 | 14 8 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 4.96 | 5.77 | 6.18 | 6.37 | 6.43 | 6.69 | 7.06 | 7.21 | 7.72 | 7.75 | 7.81 | 8.23 | 8.83 |
| 1 | 5.01 | 6.06 | 6.24 | 6.62 | 6.38 | 6.78 | 6.54 | 7.45 | 7.41 | 7.87 | 7.90 | 8.19 | 8.55 |
| 2 | 4.90 | 6.12 | 6.54 | 6.41 | 6.62 | 7.19 | 6.85 | 7.66 | 7.72 | 7.41 | 7.43 | 7.65 | 8.51 |
| 3 | 4.87 | 6.07 | 6.25 | 6.64 | 6.67 | 7.12 | 6.53 | 7.26 | 7.36 | 7.63 | 7.70 | 8.12 | 8.79 |
| 4 | 5.04 | 6.09 | 6.57 | 6.42 | 6.50 | 7.07 | 6.66 | 7.61 | 7.54 | 7.50 | 7.56 | 7.78 | 8.64 |

## Which generators produce the cheapest image?

Over the 119 rows with at least one solved image (ties at the minimum go to the BFS-first image, as in `ATLAS.md`; the minimum is unique on 112 of them).  Under a uniform choice each of the 13 sequences would win 9.2 rows.

| seq (AUTOS indices, applied left to right) | rows | L1 | L2 | L3 | L4 | L5 | L9 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 15 15 | 30 | 2 | 10 | 2 | 3 | 2 | 11 |
| 9 9 | 18 | 0 | 1 | 2 | 6 | 2 | 7 |
| 15 9 | 14 | 0 | 2 | 2 | 1 | 9 | 0 |
| 8 14 | 10 | 0 | 4 | 1 | 4 | 0 | 1 |
| 14 14 | 8 | 0 | 0 | 4 | 2 | 0 | 2 |
| 9 15 | 7 | 2 | 1 | 2 | 0 | 0 | 2 |
| 8 8 | 6 | 0 | 0 | 3 | 1 | 1 | 1 |
| 8 | 6 | 0 | 1 | 2 | 3 | 0 | 0 |
| 14 | 6 | 2 | 1 | 1 | 1 | 1 | 0 |
| id | 5 | 0 | 3 | 0 | 2 | 0 | 0 |
| 14 8 | 4 | 0 | 0 | 0 | 2 | 0 | 2 |
| 9 | 3 | 0 | 1 | 1 | 0 | 1 | 0 |
| 15 | 2 | 0 | 0 | 0 | 0 | 2 | 0 |

Repeated generator at depth 2: 62; two different generators: 35; depth 1: 17; identity: 5.

| AUTOS index | automorphism | first in the cheapest seq | second in the cheapest seq |
|---|---:|---:|---:|
| 8 | x->x, y->yx | 22 | 10 |
| 9 | x->x, y->Xy | 28 | 32 |
| 14 | x->xy, y->y | 18 | 18 |
| 15 | x->Yx, y->y | 46 | 37 |

The labels are relative to each row's canonical naming (a relabelling swaps 8 with 9 and 14 with 15 as cyclic words), so the split between 8/9 and between 14/15 is not meaningful; the split between the y-family (8, 9) and the x-family (14, 15) is.

## Verdict

- The best hand-written rule by the primary metric is **identity** (regret 0.720, 94/124 top-1 solves).  `lowest_h` (0.961, 71) and `depth2_first` (0.787, 72) both lose to the identity on the pick, though they place the best image higher (rank_of_best 5.86 / 4.16 vs 8.58).
- The pairwise model without the hedge (`pairwise_rownorm`): regret 0.434, top-1 solves 99/124, top-1@5k 76/124, W/L vs identity 13/8.
- The shipped pairwise model (`pairwise_rownorm`) on held-out rows: regret 0.434, top-1 solves 99/124, top-3 solves 112/124, top-1@5k 76/124, rank_of_best 4.10.  Beats the identity: yes (W/L on top-1 solves 13/8); beats lowest_h: yes; beats depth2_first: yes; beats the in-fold rule search: yes; beats the seq prior: yes.
- The identity-bonus hedge (deviate from the row as given only on a clear margin) does not help: held-out regret 0.457 vs 0.434 without it, 99 vs 99 top-1 solves; the inner CV picks a bonus of [0.25, 0.0, 0.0, 0.5, 0.0] per fold, so the shipped bonus is 0.0.
- Where it wins and loses (top-1 solves at 20k, model vs identity vs oracle): autmin 45 vs 37 vs 58; ms_raw 13 vs 12 vs 16; original 41 vs 45 vs 45.  The gain is on the Aut-minimal representatives; on the dataset originals, which the identity already solves 45/45, the model gives back 4 rows at 20k (at 5k it is 33 vs 38).
- Gap closed by the single pick: 20% of the identity-to-oracle gap at 20k over all rows (32% at 5k); on level 9, 55% at 20k (17 vs identity 6 vs oracle 26).
- Where the signal is: state features alone give regret 0.443 (92 solves), the generator/depth columns alone 0.786 (89), the seq prior 0.720 (94), both together 0.434 (99).
- Equal compute with the shipped ranking, all rows: pure top-k solves k=1: 99, k=2: 94, k=3: 95, k=5: 95, k=13: 75; hedged (identity + top k-1) k=1: 94, k=2: 96, k=3: 95, k=5: 95, k=13: 75 (identity alone 94; oracle single pick 119).  Level 9: pure k=1: 17, k=2: 18, k=3: 18, k=5: 18, k=13: 10; hedged k=1: 6, k=2: 17, k=3: 17, k=5: 18, k=13: 10 (identity alone 6; oracle 26).  Best over all rows: **top-1 at 20,000 pops each** (99); on level 9: **top-2 at 10,000 pops each** (18).
- depth2_first, the best hand rule on level 9 alone (18 top-1 solves, hedged k=2 17), is not usable blind: it costs 22 rows over the whole panel.

**For B3.** Use `rank_images.rank` (learned weights).  Single pick: the top-1 image beats running the row as given (99 vs 94 at 20k, 76 vs 64 at 5k), and it is the best recipe at equal compute over the whole panel (**top-1 at 20,000 pops each**, 99 rows).  On hard rows the best is **top-2 at 10,000 pops each** (18 of 28 level-9 rows).  Insurance: identity + top-1 at 10,000 each solves 96 rows overall and 17 on level 9, never fewer than the identity at 10,000 (87), so use it when a run must not be worse than the row as given at the reduced budget.  Do not use the pick on inputs that are dataset originals if the budget is generous: there the row as given is already the best single start.  `rank` is deterministic, numpy-only, 13 images per call at radius 2, and falls back to `lowest_h` if `weights.json` is missing.

## Files

| file | role |
|---|---|
| `data.py` | atlas -> arrays, feature vector (`image_vector`), stratified group folds, standardisation |
| `baselines.py` | identity / shortest / lowest_h / depth2_first / random / bfs rankers |
| `metrics.py` | per-row metrics and aggregation |
| `train.py` | pairwise logistic ranker (Newton, L2), seq prior, rule search |
| `evaluate.py` | the CV driver; writes `results.json`, `weights.json`, this report |
| `report.py` | renders this file from `results.json` |
| `rank_images.py` | `rank(pair, radius=2, cap=48) -> [(score, image), ...]`, best first; CLI prints a ranking |
| `weights.json` | feature names, means, stds, weights, lambda, CV summary |
| `tests/test_predictor.py` | group-disjoint split, `rank` on a ladder_20 row, weights round-trip |

