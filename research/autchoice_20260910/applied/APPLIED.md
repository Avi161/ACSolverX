# The applied campaign: B1's radius-2 trick on the presentations nothing solves

Targets: the 124 unsolved Miller-Schupp classes in both forms (`aca_N` as first found, `acabest_N` mu-reduced) and the two AC19 level-9 orbits whose radius-2 ball did not solve at 20,000 pops in the atlas (`ac19_27254`, `ac19_7284`); 250 rows, 250 run.  Phase 1: every radius-2 image (cap 48, relabel-deduped) searched with `S20_MK2` at 20,000 pops; 3,238 records, 2100 distinct searches (identical pairs searched once).  Phase 2: 220 records (below).  Built by `analyze_applied.py` from `phase1.jsonl` / `phase2.jsonl`.

## The answer

**1 target(s) with at least one verified solving image** 0 aca_initial, 0 aca_best, 1 ac19_level9_leftover.

**On the 124 unsolved Miller-Schupp classes: zero new solves.**  Neither form solved from any of its 3,212 radius-2 images at 20,000 pops, nor from the 152 depth-3 images at 20,000 or the 30 ranked images at 200,000 pops on the 10 closest classes.  The trick that turns 26/28 unsolvable-at-10M AC19 representatives into sub-20k solves does not touch the MS residue at these budgets; what it did reach is below.

| target | form | image | depth | seq (AUTOS) | phi | image r1, r2 | pops | AC moves | budget |
|---|---|---:|---:|---|---|---|---:|---:|---:|
| ac19_7284 | ac19_level9_leftover | 17 | 3 | 9 9 9 | x->x, y->XXXy | `YXyxYXXXyxx`, `YXXXyXXYxxx` | 14,030 | 75 | 20,000 |

| form | targets | run | with a solving image | any image below start length | ball min < identity min | identity below start | images | images below start | images back to start length | targets where every image got back |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| aca_initial | 124 | 124 | 0 | 14 | 7 | 8 | 1606 | 55 | 777 | 7 |
| aca_best | 124 | 124 | 0 | 0 | 0 | 0 | 1606 | 0 | 567 | 2 |
| ac19_level9_leftover | 2 | 2 | 1 | 2 | 1 | 1 | 26 | 5 | 10 | 0 |

Per class (`aca_N` and `acabest_N` together): 0/124 classes solved, 14/124 with any image below the start length in either form.  Against the class's **best-known length** (the `acabest_N` start length): 1 classes where any image's search found a state shorter than the best-known form (111); 123 where the ball's minimum equals it.  On the un-reduced `aca_initial` rows the ball reaches the best-known length on 97/124 (the identity alone on 95/124), i.e. a drop below the `aca_initial` start is the known mu-reduction rediscovered, not new ground.

No engine claim failed either replay (0 rejected, 0 unverified).

## What the ball reached (non-solves)

`ball_min` is the smallest total relator length the search discovered from any radius-2 image (the engine's `min_relator_length`); `identity min` the same from the row as given; `drop` = `ball_min - start_len`.  A negative drop means some image's search found a state shorter than the target; zero means nothing below the start was ever seen.  `images back to start` counts images (usually longer than the row) whose search rediscovered a state no longer than the row.  Images longer than the row are the norm (B1: the cheapest image is longer than the row on 99/114), so `images longer` says how the ball sits.

| form | run | drop min / median / max | histogram of drop (drop: targets) |
|---|---:|---|---|
| aca_initial | 124 | -3 / 0.0 / 0 | -3: 4, -2: 7, -1: 3, 0: 110 |
| aca_best | 124 | 0 / 0.0 / 0 | 0: 124 |
| ac19_level9_leftover | 2 | -2 / -1.5 / -1 | -2: 1, -1: 1 |

### Per target (sorted by ball_min, then drop)

| target | form | start len | best-known len | identity min | identity max exp | ball min | drop | vs best-known | at image (idx, depth, seq, len) | images below start | images back to start | images longer / shorter than row | r3 min | 200k min |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---|---:|---:|
| aca_115 | aca_initial | 13 | 13 | 13 | 25 | 13 | 0 | 0 | 0, d0, id, 13 | 0/13 | 11/13 | 12 / 0 | 13 | 13 |
| acabest_115 | aca_best | 13 | 13 | 13 | 25 | 13 | 0 | 0 | 0, d0, id, 13 | 0/13 | 11/13 | 12 / 0 | - | - |
| aca_116 | aca_initial | 14 | 14 | 14 | 27 | 14 | 0 | 0 | 0, d0, id, 14 | 0/13 | 13/13 | 12 / 0 | 14 | 14 |
| aca_117 | aca_initial | 14 | 14 | 14 | 26 | 14 | 0 | 0 | 0, d0, id, 14 | 0/7 | 7/7 | 6 / 0 | 14 | 14 |
| acabest_116 | aca_best | 14 | 14 | 14 | 27 | 14 | 0 | 0 | 0, d0, id, 14 | 0/13 | 13/13 | 12 / 0 | - | - |
| acabest_117 | aca_best | 14 | 14 | 14 | 26 | 14 | 0 | 0 | 0, d0, id, 14 | 0/7 | 7/7 | 6 / 0 | - | - |
| aca_1 | aca_initial | 15 | 15 | 15 | 35 | 15 | 0 | 0 | 0, d0, id, 15 | 0/13 | 7/13 | 12 / 0 | 15 | 15 |
| aca_10 | aca_initial | 15 | 15 | 15 | 31 | 15 | 0 | 0 | 0, d0, id, 15 | 0/13 | 7/13 | 12 / 0 | 15 | 15 |
| aca_11 | aca_initial | 15 | 15 | 15 | 30 | 15 | 0 | 0 | 0, d0, id, 15 | 0/13 | 5/13 | 12 / 0 | 15 | 16 |
| aca_118 | aca_initial | 15 | 15 | 15 | 29 | 15 | 0 | 0 | 0, d0, id, 15 | 0/13 | 9/13 | 12 / 0 | 15 | 15 |
| aca_12 | aca_initial | 15 | 15 | 15 | 31 | 15 | 0 | 0 | 0, d0, id, 15 | 0/13 | 5/13 | 12 / 0 | 15 | 17 |
| aca_14 | aca_initial | 15 | 15 | 15 | 36 | 15 | 0 | 0 | 0, d0, id, 15 | 0/13 | 3/13 | 12 / 0 | - | - |
| aca_8 | aca_initial | 15 | 15 | 15 | 32 | 15 | 0 | 0 | 0, d0, id, 15 | 0/13 | 11/13 | 12 / 0 | 15 | 15 |
| aca_9 | aca_initial | 15 | 15 | 15 | 31 | 15 | 0 | 0 | 0, d0, id, 15 | 0/13 | 7/13 | 12 / 0 | 15 | 15 |
| acabest_1 | aca_best | 15 | 15 | 15 | 35 | 15 | 0 | 0 | 0, d0, id, 15 | 0/13 | 7/13 | 12 / 0 | - | - |
| acabest_10 | aca_best | 15 | 15 | 15 | 31 | 15 | 0 | 0 | 0, d0, id, 15 | 0/13 | 7/13 | 12 / 0 | - | - |
| acabest_11 | aca_best | 15 | 15 | 15 | 30 | 15 | 0 | 0 | 0, d0, id, 15 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_118 | aca_best | 15 | 15 | 15 | 29 | 15 | 0 | 0 | 0, d0, id, 15 | 0/13 | 9/13 | 12 / 0 | - | - |
| acabest_12 | aca_best | 15 | 15 | 15 | 31 | 15 | 0 | 0 | 0, d0, id, 15 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_120 | aca_best | 15 | 15 | 15 | 37 | 15 | 0 | 0 | 0, d0, id, 15 | 0/13 | 1/13 | 12 / 0 | - | - |
| acabest_121 | aca_best | 15 | 15 | 15 | 36 | 15 | 0 | 0 | 0, d0, id, 15 | 0/13 | 2/13 | 12 / 0 | - | - |
| acabest_14 | aca_best | 15 | 15 | 15 | 36 | 15 | 0 | 0 | 0, d0, id, 15 | 0/13 | 3/13 | 12 / 0 | - | - |
| acabest_8 | aca_best | 15 | 15 | 15 | 32 | 15 | 0 | 0 | 0, d0, id, 15 | 0/13 | 11/13 | 12 / 0 | - | - |
| acabest_9 | aca_best | 15 | 15 | 15 | 31 | 15 | 0 | 0 | 0, d0, id, 15 | 0/13 | 7/13 | 12 / 0 | - | - |
| aca_36 | aca_initial | 18 | 16 | 18 | 39 | 16 | -2 | 0 | 11, d2, 15 9, 21 | 3/13 | 8/13 | 12 / 0 | - | - |
| aca_119 | aca_initial | 16 | 16 | 16 | 31 | 16 | 0 | 0 | 0, d0, id, 16 | 0/13 | 6/13 | 12 / 0 | - | - |
| aca_120 | aca_initial | 16 | 15 | 16 | 33 | 16 | 0 | 1 | 0, d0, id, 16 | 0/13 | 11/13 | 12 / 0 | - | - |
| aca_121 | aca_initial | 16 | 15 | 16 | 30 | 16 | 0 | 1 | 0, d0, id, 16 | 0/13 | 13/13 | 12 / 0 | - | - |
| aca_13 | aca_initial | 16 | 16 | 16 | 35 | 16 | 0 | 0 | 0, d0, id, 16 | 0/13 | 7/13 | 12 / 0 | - | - |
| aca_2 | aca_initial | 16 | 16 | 16 | 39 | 16 | 0 | 0 | 0, d0, id, 16 | 0/13 | 1/13 | 12 / 0 | - | - |
| aca_7 | aca_initial | 16 | 16 | 16 | 36 | 16 | 0 | 0 | 0, d0, id, 16 | 0/13 | 6/13 | 12 / 0 | - | - |
| acabest_119 | aca_best | 16 | 16 | 16 | 31 | 16 | 0 | 0 | 0, d0, id, 16 | 0/13 | 6/13 | 12 / 0 | - | - |
| acabest_122 | aca_best | 16 | 16 | 16 | 36 | 16 | 0 | 0 | 0, d0, id, 16 | 0/13 | 2/13 | 12 / 0 | - | - |
| acabest_13 | aca_best | 16 | 16 | 16 | 35 | 16 | 0 | 0 | 0, d0, id, 16 | 0/13 | 7/13 | 12 / 0 | - | - |
| acabest_2 | aca_best | 16 | 16 | 16 | 39 | 16 | 0 | 0 | 0, d0, id, 16 | 0/13 | 1/13 | 12 / 0 | - | - |
| acabest_34 | aca_best | 16 | 16 | 16 | 39 | 16 | 0 | 0 | 0, d0, id, 16 | 0/13 | 1/13 | 12 / 0 | - | - |
| acabest_36 | aca_best | 16 | 16 | 16 | 35 | 16 | 0 | 0 | 0, d0, id, 16 | 0/13 | 1/13 | 12 / 0 | - | - |
| acabest_7 | aca_best | 16 | 16 | 16 | 36 | 16 | 0 | 0 | 0, d0, id, 16 | 0/13 | 6/13 | 12 / 0 | - | - |
| ac19_7284 | ac19_level9_leftover | 19 | - | 17 | 40 | 17 | -2 | - | 0, d0, id, 19 | 2/13 | 5/13 | 12 / 0 | 2 | 2 |
| aca_15 | aca_initial | 17 | 17 | 17 | 34 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_16 | aca_initial | 17 | 17 | 17 | 33 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 11/13 | 12 / 0 | - | - |
| aca_17 | aca_initial | 17 | 17 | 17 | 34 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_18 | aca_initial | 17 | 17 | 17 | 34 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_19 | aca_initial | 17 | 17 | 17 | 34 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_20 | aca_initial | 17 | 17 | 17 | 34 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_21 | aca_initial | 17 | 17 | 17 | 34 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_22 | aca_initial | 17 | 17 | 17 | 34 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_23 | aca_initial | 17 | 17 | 17 | 34 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_24 | aca_initial | 17 | 17 | 17 | 33 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 10/13 | 12 / 0 | - | - |
| aca_25 | aca_initial | 17 | 17 | 17 | 34 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_26 | aca_initial | 17 | 17 | 17 | 34 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_27 | aca_initial | 17 | 17 | 17 | 34 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_28 | aca_initial | 17 | 17 | 17 | 34 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_29 | aca_initial | 17 | 17 | 17 | 35 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_3 | aca_initial | 17 | 17 | 17 | 33 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_30 | aca_initial | 17 | 17 | 17 | 35 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 10/13 | 12 / 0 | - | - |
| aca_31 | aca_initial | 17 | 17 | 17 | 37 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 7/13 | 12 / 0 | - | - |
| aca_32 | aca_initial | 17 | 17 | 17 | 38 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 6/13 | 11 / 0 | - | - |
| aca_33 | aca_initial | 17 | 17 | 17 | 38 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 5/13 | 11 / 0 | - | - |
| acabest_123 | aca_best | 17 | 17 | 17 | 37 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 2/13 | 12 / 0 | - | - |
| acabest_15 | aca_best | 17 | 17 | 17 | 34 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_16 | aca_best | 17 | 17 | 17 | 33 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 11/13 | 12 / 0 | - | - |
| acabest_17 | aca_best | 17 | 17 | 17 | 34 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_18 | aca_best | 17 | 17 | 17 | 34 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_19 | aca_best | 17 | 17 | 17 | 34 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_20 | aca_best | 17 | 17 | 17 | 34 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_21 | aca_best | 17 | 17 | 17 | 34 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_22 | aca_best | 17 | 17 | 17 | 34 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_23 | aca_best | 17 | 17 | 17 | 34 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_24 | aca_best | 17 | 17 | 17 | 33 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 10/13 | 12 / 0 | - | - |
| acabest_25 | aca_best | 17 | 17 | 17 | 34 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_26 | aca_best | 17 | 17 | 17 | 34 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_27 | aca_best | 17 | 17 | 17 | 34 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_28 | aca_best | 17 | 17 | 17 | 34 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_29 | aca_best | 17 | 17 | 17 | 35 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_3 | aca_best | 17 | 17 | 17 | 33 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_30 | aca_best | 17 | 17 | 17 | 35 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 10/13 | 12 / 0 | - | - |
| acabest_31 | aca_best | 17 | 17 | 17 | 37 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 7/13 | 12 / 0 | - | - |
| acabest_32 | aca_best | 17 | 17 | 17 | 38 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 6/13 | 11 / 0 | - | - |
| acabest_33 | aca_best | 17 | 17 | 17 | 38 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 5/13 | 11 / 0 | - | - |
| acabest_58 | aca_best | 17 | 17 | 17 | 41 | 17 | 0 | 0 | 0, d0, id, 17 | 0/13 | 1/13 | 12 / 0 | - | - |
| ac19_27254 | ac19_level9_leftover | 19 | - | 19 | 39 | 18 | -1 | - | 1, d1, 8, 19 | 3/13 | 5/13 | 9 / 0 | 15 | 18 |
| aca_55 | aca_initial | 19 | 18 | 18 | 40 | 18 | -1 | 0 | 0, d0, id, 19 | 5/13 | 5/13 | 12 / 0 | - | - |
| aca_0 | aca_initial | 18 | 18 | 18 | 36 | 18 | 0 | 0 | 0, d0, id, 18 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_122 | aca_initial | 18 | 16 | 18 | 35 | 18 | 0 | 2 | 0, d0, id, 18 | 0/13 | 13/13 | 12 / 0 | - | - |
| aca_34 | aca_initial | 18 | 16 | 18 | 37 | 18 | 0 | 2 | 0, d0, id, 18 | 0/13 | 8/13 | 12 / 0 | - | - |
| aca_35 | aca_initial | 18 | 18 | 18 | 40 | 18 | 0 | 0 | 0, d0, id, 18 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_4 | aca_initial | 18 | 18 | 18 | 40 | 18 | 0 | 0 | 0, d0, id, 18 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_53 | aca_initial | 18 | 18 | 18 | 37 | 18 | 0 | 0 | 0, d0, id, 18 | 0/13 | 6/13 | 12 / 0 | - | - |
| acabest_0 | aca_best | 18 | 18 | 18 | 36 | 18 | 0 | 0 | 0, d0, id, 18 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_35 | aca_best | 18 | 18 | 18 | 40 | 18 | 0 | 0 | 0, d0, id, 18 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_4 | aca_best | 18 | 18 | 18 | 40 | 18 | 0 | 0 | 0, d0, id, 18 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_43 | aca_best | 18 | 18 | 18 | 41 | 18 | 0 | 0 | 0, d0, id, 18 | 0/13 | 1/13 | 12 / 0 | - | - |
| acabest_44 | aca_best | 18 | 18 | 18 | 39 | 18 | 0 | 0 | 0, d0, id, 18 | 0/13 | 1/13 | 12 / 0 | - | - |
| acabest_53 | aca_best | 18 | 18 | 18 | 37 | 18 | 0 | 0 | 0, d0, id, 18 | 0/13 | 6/13 | 12 / 0 | - | - |
| acabest_55 | aca_best | 18 | 18 | 18 | 40 | 18 | 0 | 0 | 0, d0, id, 18 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_72 | aca_best | 18 | 18 | 18 | 42 | 18 | 0 | 0 | 0, d0, id, 18 | 0/13 | 1/13 | 12 / 0 | - | - |
| acabest_81 | aca_best | 18 | 18 | 18 | 43 | 18 | 0 | 0 | 0, d0, id, 18 | 0/13 | 1/13 | 12 / 0 | - | - |
| acabest_85 | aca_best | 18 | 18 | 18 | 39 | 18 | 0 | 0 | 0, d0, id, 18 | 0/13 | 2/13 | 12 / 0 | - | - |
| aca_78 | aca_initial | 21 | 19 | 20 | 39 | 19 | -2 | 0 | 1, d1, 8, 28 | 7/13 | 9/13 | 12 / 0 | - | - |
| aca_37 | aca_initial | 19 | 19 | 19 | 39 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 8/13 | 12 / 0 | - | - |
| aca_38 | aca_initial | 19 | 19 | 19 | 39 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 8/13 | 12 / 0 | - | - |
| aca_39 | aca_initial | 19 | 19 | 19 | 39 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_40 | aca_initial | 19 | 19 | 19 | 39 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_41 | aca_initial | 19 | 19 | 19 | 39 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_42 | aca_initial | 19 | 19 | 19 | 39 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_43 | aca_initial | 19 | 18 | 19 | 38 | 19 | 0 | 1 | 0, d0, id, 19 | 0/13 | 8/13 | 11 / 0 | - | - |
| aca_44 | aca_initial | 19 | 18 | 19 | 38 | 19 | 0 | 1 | 0, d0, id, 19 | 0/13 | 10/13 | 12 / 0 | - | - |
| aca_45 | aca_initial | 19 | 19 | 19 | 39 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_46 | aca_initial | 19 | 19 | 19 | 39 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_47 | aca_initial | 19 | 19 | 19 | 39 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_48 | aca_initial | 19 | 19 | 19 | 39 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_49 | aca_initial | 19 | 19 | 19 | 39 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_5 | aca_initial | 19 | 19 | 19 | 40 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_50 | aca_initial | 19 | 19 | 19 | 39 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_51 | aca_initial | 19 | 19 | 19 | 39 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_52 | aca_initial | 19 | 19 | 19 | 39 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_54 | aca_initial | 19 | 19 | 19 | 37 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_56 | aca_initial | 19 | 19 | 19 | 42 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 6/13 | 12 / 0 | - | - |
| aca_57 | aca_initial | 19 | 19 | 19 | 42 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_6 | aca_initial | 19 | 19 | 19 | 39 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_37 | aca_best | 19 | 19 | 19 | 39 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 8/13 | 12 / 0 | - | - |
| acabest_38 | aca_best | 19 | 19 | 19 | 39 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 8/13 | 12 / 0 | - | - |
| acabest_39 | aca_best | 19 | 19 | 19 | 39 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_40 | aca_best | 19 | 19 | 19 | 39 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_41 | aca_best | 19 | 19 | 19 | 39 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_42 | aca_best | 19 | 19 | 19 | 39 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_45 | aca_best | 19 | 19 | 19 | 39 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_46 | aca_best | 19 | 19 | 19 | 39 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_47 | aca_best | 19 | 19 | 19 | 39 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_48 | aca_best | 19 | 19 | 19 | 39 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_49 | aca_best | 19 | 19 | 19 | 39 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_5 | aca_best | 19 | 19 | 19 | 40 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_50 | aca_best | 19 | 19 | 19 | 39 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_51 | aca_best | 19 | 19 | 19 | 39 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_52 | aca_best | 19 | 19 | 19 | 39 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_54 | aca_best | 19 | 19 | 19 | 37 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_56 | aca_best | 19 | 19 | 19 | 42 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 6/13 | 12 / 0 | - | - |
| acabest_57 | aca_best | 19 | 19 | 19 | 42 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_6 | aca_best | 19 | 19 | 19 | 39 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_71 | aca_best | 19 | 19 | 19 | 42 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 1/13 | 12 / 0 | - | - |
| acabest_78 | aca_best | 19 | 19 | 19 | 39 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 1/13 | 12 / 0 | - | - |
| acabest_80 | aca_best | 19 | 19 | 19 | 37 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 6/13 | 12 / 0 | - | - |
| acabest_88 | aca_best | 19 | 19 | 19 | 43 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 1/13 | 12 / 0 | - | - |
| acabest_95 | aca_best | 19 | 19 | 19 | 43 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 1/13 | 12 / 0 | - | - |
| acabest_97 | aca_best | 19 | 19 | 19 | 45 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 1/13 | 12 / 0 | - | - |
| acabest_98 | aca_best | 19 | 19 | 19 | 40 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 2/13 | 12 / 0 | - | - |
| acabest_99 | aca_best | 19 | 19 | 19 | 43 | 19 | 0 | 0 | 0, d0, id, 19 | 0/13 | 1/13 | 12 / 0 | - | - |
| aca_123 | aca_initial | 20 | 17 | 20 | 38 | 20 | 0 | 3 | 0, d0, id, 20 | 0/13 | 13/13 | 12 / 0 | - | - |
| aca_58 | aca_initial | 20 | 17 | 20 | 41 | 20 | 0 | 3 | 0, d0, id, 20 | 0/13 | 8/13 | 12 / 0 | - | - |
| aca_59 | aca_initial | 20 | 20 | 20 | 40 | 20 | 0 | 0 | 0, d0, id, 20 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_60 | aca_initial | 20 | 20 | 20 | 43 | 20 | 0 | 0 | 0, d0, id, 20 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_61 | aca_initial | 20 | 20 | 20 | 43 | 20 | 0 | 0 | 0, d0, id, 20 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_71 | aca_initial | 20 | 19 | 20 | 42 | 20 | 0 | 1 | 0, d0, id, 20 | 0/13 | 8/13 | 12 / 0 | - | - |
| aca_72 | aca_initial | 20 | 18 | 20 | 42 | 20 | 0 | 2 | 0, d0, id, 20 | 0/13 | 8/13 | 12 / 0 | - | - |
| acabest_100 | aca_best | 20 | 20 | 20 | 45 | 20 | 0 | 0 | 0, d0, id, 20 | 0/13 | 1/13 | 12 / 0 | - | - |
| acabest_59 | aca_best | 20 | 20 | 20 | 40 | 20 | 0 | 0 | 0, d0, id, 20 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_60 | aca_best | 20 | 20 | 20 | 43 | 20 | 0 | 0 | 0, d0, id, 20 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_61 | aca_best | 20 | 20 | 20 | 43 | 20 | 0 | 0 | 0, d0, id, 20 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_66 | aca_best | 20 | 20 | 20 | 44 | 20 | 0 | 0 | 0, d0, id, 20 | 0/13 | 1/13 | 12 / 0 | - | - |
| acabest_67 | aca_best | 20 | 20 | 20 | 44 | 20 | 0 | 0 | 0, d0, id, 20 | 0/13 | 1/13 | 12 / 0 | - | - |
| acabest_87 | aca_best | 20 | 20 | 20 | 45 | 20 | 0 | 0 | 0, d0, id, 20 | 0/13 | 1/13 | 12 / 0 | - | - |
| acabest_90 | aca_best | 20 | 20 | 20 | 45 | 20 | 0 | 0 | 0, d0, id, 20 | 0/13 | 1/13 | 12 / 0 | - | - |
| aca_88 | aca_initial | 23 | 19 | 23 | 46 | 21 | -2 | 2 | 1, d1, 8, 27 | 2/13 | 8/13 | 12 / 0 | - | - |
| aca_62 | aca_initial | 21 | 21 | 21 | 43 | 21 | 0 | 0 | 0, d0, id, 21 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_63 | aca_initial | 21 | 21 | 21 | 43 | 21 | 0 | 0 | 0, d0, id, 21 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_64 | aca_initial | 21 | 21 | 21 | 43 | 21 | 0 | 0 | 0, d0, id, 21 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_65 | aca_initial | 21 | 21 | 21 | 43 | 21 | 0 | 0 | 0, d0, id, 21 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_66 | aca_initial | 21 | 20 | 21 | 43 | 21 | 0 | 1 | 0, d0, id, 21 | 0/13 | 6/13 | 12 / 0 | - | - |
| aca_67 | aca_initial | 21 | 20 | 21 | 43 | 21 | 0 | 1 | 0, d0, id, 21 | 0/13 | 6/13 | 12 / 0 | - | - |
| aca_68 | aca_initial | 21 | 21 | 21 | 42 | 21 | 0 | 0 | 0, d0, id, 21 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_69 | aca_initial | 21 | 21 | 21 | 42 | 21 | 0 | 0 | 0, d0, id, 21 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_70 | aca_initial | 21 | 21 | 21 | 42 | 21 | 0 | 0 | 0, d0, id, 21 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_73 | aca_initial | 21 | 21 | 21 | 42 | 21 | 0 | 0 | 0, d0, id, 21 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_74 | aca_initial | 21 | 21 | 21 | 43 | 21 | 0 | 0 | 0, d0, id, 21 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_75 | aca_initial | 21 | 21 | 21 | 43 | 21 | 0 | 0 | 0, d0, id, 21 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_76 | aca_initial | 21 | 21 | 21 | 46 | 21 | 0 | 0 | 0, d0, id, 21 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_77 | aca_initial | 21 | 21 | 21 | 46 | 21 | 0 | 0 | 0, d0, id, 21 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_79 | aca_initial | 21 | 21 | 21 | 43 | 21 | 0 | 0 | 0, d0, id, 21 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_80 | aca_initial | 21 | 19 | 21 | 42 | 21 | 0 | 2 | 0, d0, id, 21 | 0/13 | 5/13 | 10 / 0 | - | - |
| aca_95 | aca_initial | 21 | 19 | 21 | 45 | 21 | 0 | 2 | 0, d0, id, 21 | 0/13 | 3/13 | 12 / 0 | - | - |
| acabest_105 | aca_best | 21 | 21 | 21 | 47 | 21 | 0 | 0 | 0, d0, id, 21 | 0/13 | 1/13 | 12 / 0 | - | - |
| acabest_106 | aca_best | 21 | 21 | 21 | 47 | 21 | 0 | 0 | 0, d0, id, 21 | 0/13 | 1/13 | 12 / 0 | - | - |
| acabest_62 | aca_best | 21 | 21 | 21 | 43 | 21 | 0 | 0 | 0, d0, id, 21 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_63 | aca_best | 21 | 21 | 21 | 43 | 21 | 0 | 0 | 0, d0, id, 21 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_64 | aca_best | 21 | 21 | 21 | 43 | 21 | 0 | 0 | 0, d0, id, 21 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_65 | aca_best | 21 | 21 | 21 | 43 | 21 | 0 | 0 | 0, d0, id, 21 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_68 | aca_best | 21 | 21 | 21 | 42 | 21 | 0 | 0 | 0, d0, id, 21 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_69 | aca_best | 21 | 21 | 21 | 42 | 21 | 0 | 0 | 0, d0, id, 21 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_70 | aca_best | 21 | 21 | 21 | 42 | 21 | 0 | 0 | 0, d0, id, 21 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_73 | aca_best | 21 | 21 | 21 | 42 | 21 | 0 | 0 | 0, d0, id, 21 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_74 | aca_best | 21 | 21 | 21 | 43 | 21 | 0 | 0 | 0, d0, id, 21 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_75 | aca_best | 21 | 21 | 21 | 43 | 21 | 0 | 0 | 0, d0, id, 21 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_76 | aca_best | 21 | 21 | 21 | 46 | 21 | 0 | 0 | 0, d0, id, 21 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_77 | aca_best | 21 | 21 | 21 | 46 | 21 | 0 | 0 | 0, d0, id, 21 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_79 | aca_best | 21 | 21 | 21 | 43 | 21 | 0 | 0 | 0, d0, id, 21 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_100 | aca_initial | 25 | 20 | 25 | 50 | 22 | -3 | 2 | 1, d1, 8, 29 | 2/13 | 8/13 | 12 / 0 | - | - |
| aca_107 | aca_initial | 25 | 22 | 22 | 49 | 22 | -3 | 0 | 0, d0, id, 25 | 5/13 | 5/13 | 12 / 0 | - | - |
| aca_110 | aca_initial | 25 | 22 | 22 | 49 | 22 | -3 | 0 | 0, d0, id, 25 | 5/13 | 5/13 | 12 / 0 | - | - |
| aca_99 | aca_initial | 25 | 19 | 25 | 50 | 22 | -3 | 3 | 2, d1, 9, 39 | 2/13 | 8/13 | 12 / 0 | - | - |
| aca_81 | aca_initial | 22 | 18 | 22 | 44 | 22 | 0 | 4 | 0, d0, id, 22 | 0/13 | 8/13 | 12 / 0 | - | - |
| aca_82 | aca_initial | 22 | 22 | 22 | 45 | 22 | 0 | 0 | 0, d0, id, 22 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_83 | aca_initial | 22 | 22 | 22 | 47 | 22 | 0 | 0 | 0, d0, id, 22 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_84 | aca_initial | 22 | 22 | 22 | 47 | 22 | 0 | 0 | 0, d0, id, 22 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_85 | aca_initial | 22 | 18 | 22 | 42 | 22 | 0 | 4 | 0, d0, id, 22 | 0/13 | 13/13 | 12 / 0 | - | - |
| aca_86 | aca_initial | 22 | 22 | 22 | 45 | 22 | 0 | 0 | 0, d0, id, 22 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_107 | aca_best | 22 | 22 | 22 | 49 | 22 | 0 | 0 | 0, d0, id, 22 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_110 | aca_best | 22 | 22 | 22 | 49 | 22 | 0 | 0 | 0, d0, id, 22 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_82 | aca_best | 22 | 22 | 22 | 45 | 22 | 0 | 0 | 0, d0, id, 22 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_83 | aca_best | 22 | 22 | 22 | 47 | 22 | 0 | 0 | 0, d0, id, 22 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_84 | aca_best | 22 | 22 | 22 | 47 | 22 | 0 | 0 | 0, d0, id, 22 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_86 | aca_best | 22 | 22 | 22 | 45 | 22 | 0 | 0 | 0, d0, id, 22 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_109 | aca_initial | 25 | 23 | 23 | 47 | 23 | -2 | 0 | 0, d0, id, 25 | 5/13 | 5/13 | 12 / 0 | - | - |
| aca_111 | aca_initial | 25 | 24 | 23 | 47 | 23 | -2 | -1 | 0, d0, id, 25 | 5/13 | 5/13 | 12 / 0 | - | - |
| aca_113 | aca_initial | 25 | 23 | 23 | 50 | 23 | -2 | 0 | 0, d0, id, 25 | 5/13 | 5/13 | 12 / 0 | - | - |
| aca_114 | aca_initial | 25 | 23 | 23 | 50 | 23 | -2 | 0 | 0, d0, id, 25 | 5/13 | 5/13 | 12 / 0 | - | - |
| aca_87 | aca_initial | 23 | 20 | 23 | 47 | 23 | 0 | 3 | 0, d0, id, 23 | 0/13 | 8/13 | 12 / 0 | - | - |
| aca_89 | aca_initial | 23 | 23 | 23 | 45 | 23 | 0 | 0 | 0, d0, id, 23 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_90 | aca_initial | 23 | 20 | 23 | 47 | 23 | 0 | 3 | 0, d0, id, 23 | 0/13 | 8/13 | 12 / 0 | - | - |
| aca_91 | aca_initial | 23 | 23 | 23 | 47 | 23 | 0 | 0 | 0, d0, id, 23 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_92 | aca_initial | 23 | 23 | 23 | 47 | 23 | 0 | 0 | 0, d0, id, 23 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_93 | aca_initial | 23 | 23 | 23 | 47 | 23 | 0 | 0 | 0, d0, id, 23 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_94 | aca_initial | 23 | 23 | 23 | 46 | 23 | 0 | 0 | 0, d0, id, 23 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_96 | aca_initial | 23 | 23 | 23 | 45 | 23 | 0 | 0 | 0, d0, id, 23 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_109 | aca_best | 23 | 23 | 23 | 47 | 23 | 0 | 0 | 0, d0, id, 23 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_113 | aca_best | 23 | 23 | 23 | 50 | 23 | 0 | 0 | 0, d0, id, 23 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_114 | aca_best | 23 | 23 | 23 | 49 | 23 | 0 | 0 | 0, d0, id, 23 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_89 | aca_best | 23 | 23 | 23 | 45 | 23 | 0 | 0 | 0, d0, id, 23 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_91 | aca_best | 23 | 23 | 23 | 47 | 23 | 0 | 0 | 0, d0, id, 23 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_92 | aca_best | 23 | 23 | 23 | 47 | 23 | 0 | 0 | 0, d0, id, 23 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_93 | aca_best | 23 | 23 | 23 | 47 | 23 | 0 | 0 | 0, d0, id, 23 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_94 | aca_best | 23 | 23 | 23 | 46 | 23 | 0 | 0 | 0, d0, id, 23 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_96 | aca_best | 23 | 23 | 23 | 45 | 23 | 0 | 0 | 0, d0, id, 23 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_105 | aca_initial | 25 | 21 | 25 | 50 | 24 | -1 | 3 | 2, d1, 9, 39 | 2/13 | 8/13 | 12 / 0 | - | - |
| aca_106 | aca_initial | 25 | 21 | 25 | 50 | 24 | -1 | 3 | 1, d1, 8, 39 | 2/13 | 8/13 | 12 / 0 | - | - |
| aca_97 | aca_initial | 24 | 19 | 24 | 47 | 24 | 0 | 5 | 0, d0, id, 24 | 0/13 | 8/13 | 12 / 0 | - | - |
| aca_98 | aca_initial | 24 | 19 | 24 | 45 | 24 | 0 | 5 | 0, d0, id, 24 | 0/13 | 13/13 | 12 / 0 | - | - |
| acabest_108 | aca_best | 24 | 24 | 24 | 55 | 24 | 0 | 0 | 0, d0, id, 24 | 0/13 | 1/13 | 12 / 0 | - | - |
| acabest_111 | aca_best | 24 | 24 | 24 | 54 | 24 | 0 | 0 | 0, d0, id, 24 | 0/13 | 1/13 | 12 / 0 | - | - |
| acabest_112 | aca_best | 24 | 24 | 24 | 55 | 24 | 0 | 0 | 0, d0, id, 24 | 0/13 | 1/13 | 12 / 0 | - | - |
| aca_101 | aca_initial | 25 | 25 | 25 | 49 | 25 | 0 | 0 | 0, d0, id, 25 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_102 | aca_initial | 25 | 25 | 25 | 50 | 25 | 0 | 0 | 0, d0, id, 25 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_103 | aca_initial | 25 | 25 | 25 | 50 | 25 | 0 | 0 | 0, d0, id, 25 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_104 | aca_initial | 25 | 25 | 25 | 50 | 25 | 0 | 0 | 0, d0, id, 25 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_108 | aca_initial | 25 | 24 | 25 | 47 | 25 | 0 | 1 | 0, d0, id, 25 | 0/13 | 5/13 | 12 / 0 | - | - |
| aca_112 | aca_initial | 25 | 24 | 25 | 47 | 25 | 0 | 1 | 0, d0, id, 25 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_101 | aca_best | 25 | 25 | 25 | 49 | 25 | 0 | 0 | 0, d0, id, 25 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_102 | aca_best | 25 | 25 | 25 | 50 | 25 | 0 | 0 | 0, d0, id, 25 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_103 | aca_best | 25 | 25 | 25 | 50 | 25 | 0 | 0 | 0, d0, id, 25 | 0/13 | 5/13 | 12 / 0 | - | - |
| acabest_104 | aca_best | 25 | 25 | 25 | 50 | 25 | 0 | 0 | 0, d0, id, 25 | 0/13 | 5/13 | 12 / 0 | - | - |

## States shorter than a class's best-known form

`certify_short_states.py` re-ran every search whose `min_total_length_seen` is below the class's best-known length, walked the solver's parent chain to the minimum, and replayed the AC moves with `words.replay_move` from the image (and the automorphism sequence from the row): 5 certified, 0 failed (`short_states.json` has the moves).

| class | best-known len | new state | len | from row / image (seq) | image len | AC moves | peak len on the path |
|---|---:|---|---:|---|---:|---:|---:|
| aca_111 | 24 | `YYXXYxyxxyX`, `YYYYYYXXXyxx` | 23 | aca_111 / 0 (id) | 25 | 42 | 41 |
| aca_111 | 24 | `YYXXYxyxxyX`, `YYYYYYXXXyxx` | 23 | aca_111 / 3 (14) | 28 | 37 | 41 |
| aca_111 | 24 | `YYXXYxyxxyX`, `YYYYYYXXXyxx` | 23 | aca_111 / 4 (15) | 26 | 47 | 41 |
| aca_111 | 24 | `YYXXYxyxxyX`, `YYYYYYXXXyxx` | 23 | aca_111 / 10 (14 14) | 31 | 32 | 41 |
| aca_111 | 24 | `YYXXYxyxxyX`, `YYYYYYXXXyxx` | 23 | aca_111 / 12 (15 15) | 29 | 52 | 41 |

So 1 of the 124 classes (aca_111) now has a representative strictly shorter than `data/ms_unsolved_reps/aca_124_best.csv`'s -- found from the **un-reduced** form (the mu-reduced one, a local minimum, never discovers it), over a hump the strict descent cannot cross.  It is a shorter start, not a solve.

## The two AC19 level-9 leftovers

- **ac19_27254** (`YXXXyXYx`, `YXXyxxxxyxx`, length 19): not solved.  Radius 2 at 20k: identity min 19, ball min 18 over 13 images (3 below the start); radius-3 images at 20k: 16 more, min 15 (2 below); 3 images at 200k: min 18.
- **ac19_7284** (`YYXXXyXX`, `YXyxYXXXyxx`, length 19): SOLVED.  Radius 2 at 20k: identity min 17, ball min 17 over 13 images (2 below the start); radius-3 images at 20k: 16 more, min 2 (1 below); 3 images at 200k: min 2.  Best solve: image 17 seq 9 9 9 at 14,030 pops, 75 AC moves.

## Phase 2

Selection (2 leftovers + up to n_aca unsolved aca targets by (ball_min, -n_below_start, -n_at_or_below_start, ball_min-start_len, name), identical pairs once): ac19_27254, ac19_7284, aca_115, aca_116, aca_117, aca_8, aca_118, aca_1, aca_10, aca_9, aca_11, aca_12.

| target | form | start len | r2 ball min | r3 images | r3 min | below start (r3) | 200k runs | ranker | 200k images (idx, depth, seq): min len, pops |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| ac19_27254 | ac19_level9_leftover | 19 | 18 | 16 | 15 | 2 | 3 | predictor.rank_images[pairwise_logistic] | (2, d1, 9): 18, 200,000; (19, d3, 9 15 9): 25, 200,000; (8, d2, 9 15): 21, 200,000 |
| ac19_7284 | ac19_level9_leftover | 19 | 17 | 16 | 2 | 1 | 3 | predictor.rank_images[pairwise_logistic] | (19, d3, 9 15 9): 30, 200,000; (17, d3, 9 9 9): 2, 14,030 SOLVED; (11, d2, 15 9): 24, 200,000 |
| aca_115 | aca_initial | 13 | 13 | 16 | 13 | 0 | 3 | predictor.rank_images[pairwise_logistic] | (10, d2, 14 14): 13, 200,000; (3, d1, 14): 13, 200,000; (16, d3, 8 14 14): 13, 200,000 |
| aca_116 | aca_initial | 14 | 14 | 16 | 14 | 0 | 3 | predictor.rank_images[pairwise_logistic] | (8, d2, 9 15): 14, 200,000; (4, d1, 15): 14, 200,000; (25, d3, 15 9 9): 14, 200,000 |
| aca_117 | aca_initial | 14 | 14 | 8 | 14 | 0 | 3 | predictor.rank_images[pairwise_logistic] | (6, d2, 9 15): 14, 200,000; (4, d2, 8 14): 14, 200,000; (13, d3, 9 15 9): 14, 200,000 |
| aca_8 | aca_initial | 15 | 15 | 16 | 15 | 0 | 3 | predictor.rank_images[pairwise_logistic] | (20, d3, 9 15 15): 15, 200,000; (12, d2, 15 15): 15, 200,000; (8, d2, 9 15): 15, 200,000 |
| aca_118 | aca_initial | 15 | 15 | 16 | 15 | 0 | 3 | predictor.rank_images[pairwise_logistic] | (24, d3, 14 14 14): 15, 200,000; (10, d2, 14 14): 15, 200,000; (23, d3, 14 14 8): 15, 200,000 |
| aca_1 | aca_initial | 15 | 15 | 16 | 15 | 0 | 3 | predictor.rank_images[pairwise_logistic] | (12, d2, 15 15): 15, 200,000; (15, d3, 8 14 8): 17, 200,000; (11, d2, 15 9): 15, 200,000 |
| aca_10 | aca_initial | 15 | 15 | 16 | 15 | 0 | 3 | predictor.rank_images[pairwise_logistic] | (8, d2, 9 15): 15, 200,000; (19, d3, 9 15 9): 15, 200,000; (11, d2, 15 9): 15, 200,000 |
| aca_9 | aca_initial | 15 | 15 | 16 | 15 | 0 | 3 | predictor.rank_images[pairwise_logistic] | (27, d3, 15 15 9): 15, 200,000; (25, d3, 15 9 9): 15, 200,000; (8, d2, 9 15): 15, 200,000 |
| aca_11 | aca_initial | 15 | 15 | 16 | 15 | 0 | 3 | predictor.rank_images[pairwise_logistic] | (23, d3, 14 14 8): 16, 200,000; (8, d2, 9 15): 16, 200,000; (19, d3, 9 15 9): 16, 200,000 |
| aca_12 | aca_initial | 15 | 15 | 16 | 15 | 0 | 3 | predictor.rank_images[pairwise_logistic] | (8, d2, 9 15): 17, 200,000; (19, d3, 9 15 9): 17, 200,000; (25, d3, 15 9 9): 19, 200,000 |

## Compute

| phase | budget (pops) | cap | workers | records | searches | wall |
|---|---:|---:|---:|---:|---:|---:|
| 1 (radius 2) | 20,000 | 48 | 3 | 3,238 | 2,100 | 80.6 min (2026-09-10T20:24:28Z - 2026-09-10T21:45:07Z) |
| 2a (depth 3) | 20,000 | 48 | 2 | 184 | 184 | 7.1 min |
| 2b (top images) | 200,000 | 48 | 2 | 36 | 36 | 13.1 min |
| 2 total | | | | 220 | | 20.2 min (2026-09-10T21:45:13Z - 2026-09-10T22:05:25Z) |

Total search wall 1.68 h (phase-1 budget 2.5 h, phase-2 cap 1 h).  Identical pairs are searched once (the engine is deterministic) and the result re-recorded under every (row, image) carrying them with `s20.shared`; the per-row `verify_from_original` is never shared.

## Verification

In-run: every claimed solve replayed from the image with `words.replay_move` (`common.search`) and from the target's own pair through the elementary automorphism sequence (`engine.verify_from_original`).  Fresh process (`verify_applied.py`, reads only `applied/*.jsonl` + `targets.csv`, imports nothing from the engine): 3,458 records, 2 claimed solves checked, 2 ok, 0 failed.

## Caveats

- Costs are censored at the budget; "not solved at 20k" is not "unsolvable" -- the same images at 200k (phase 2) are the escalation, and the atlas showed the trick's wins at <= 14,071 pops on AC19.
- `min_total_length_seen` is the length of the shortest *discovered* state, which need not lie on any path the search will ever complete; it is a proxy for "how close", not a distance.
- The ball is relabel-deduplicated and the run image is the first discovered in BFS order (B1's convention), so an image's cost is that of one representative of its relabel class.
