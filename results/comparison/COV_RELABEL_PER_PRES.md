# Rename dedup, one presentation at a time

Subset-60, budget 1,000, **6,177 candidate rows** over 60 presentations, regrouped from the frozen sweep at zero search nodes. `relabel` = keep only the lex-min representative of each class under the 8 signed permutations of `{x, y}` — literal images, no rotation and no cyclic reduction. `booth` = `words.canon_pair`. `union` = connected components of *share a key under either*. `shipped` = `words.relabel_key`, which canonicalises before renaming and is therefore coarser than the provable line.

**The rename filter is nearly inert.** 58 of the 60 presentations have zero rename duplicates. The entire yield is 23 slots (0.37%) in 2 presentations, every class is a pair, and all 23/23 of them are bit-identical — same `solved`, `nodes_explored`, `path_length`. A pure rename must match the *literal* string; in this pool collisions essentially only surface after rotation, which is why Booth cuts 4,099 where renaming cuts 23.

Both readings of "the 8 relabelings" agree: relator order held fixed gives 6,154 classes, order allowed to swap gives 6,154.

The **6 union-bridges** — pairs where a rename links two Booth classes — are localised here rather than inferred: 3 in pres 521 (26 → 23), 3 in pres 496 (22 → 19). Every other presentation has `booth == union`.

| pres | covs | relabel | booth | union | shipped | renames dropped |
|---:|---:|---:|---:|---:|---:|---|
| 628 | 173 | 173 | 39 | 39 | 34 | — |
| 633 | 173 | 173 | 40 | 40 | 34 | — |
| 637 | 173 | 173 | 41 | 41 | 33 | — |
| 638 | 173 | 173 | 41 | 41 | 34 | — |
| 639 | 172 | 172 | 40 | 40 | 33 | — |
| 636 | 172 | 172 | 42 | 42 | 34 | — |
| 632 | 169 | 169 | 48 | 48 | 36 | — |
| 625 | 169 | 169 | 39 | 39 | 32 | — |
| 622 | 169 | 169 | 38 | 38 | 32 | — |
| 624 | 169 | 169 | 37 | 37 | 31 | — |
| 623 | 169 | 169 | 38 | 38 | 31 | — |
| 521 | 143 | 135 | 26 | 23 | 18 | **8** (8/8 bit-identical) |
| 605 | 142 | 142 | 40 | 40 | 32 | — |
| 610 | 141 | 141 | 39 | 39 | 32 | — |
| 609 | 140 | 140 | 41 | 41 | 32 | — |
| 606 | 138 | 138 | 42 | 42 | 32 | — |
| 596 | 138 | 138 | 37 | 37 | 31 | — |
| 634 | 138 | 138 | 40 | 40 | 34 | — |
| 602 | 134 | 134 | 42 | 42 | 32 | — |
| 635 | 134 | 134 | 40 | 40 | 34 | — |
| 505 | 133 | 133 | 36 | 36 | 31 | — |
| 583 | 116 | 116 | 38 | 38 | 31 | — |
| 578 | 115 | 115 | 39 | 39 | 31 | — |
| 589 | 113 | 113 | 40 | 40 | 28 | — |
| 575 | 113 | 113 | 37 | 37 | 30 | — |
| 496 | 110 | 95 | 22 | 19 | 14 | **15** (15/15 bit-identical) |
| 579 | 109 | 109 | 39 | 39 | 29 | — |
| 580 | 109 | 109 | 39 | 39 | 29 | — |
| 565 | 109 | 109 | 34 | 34 | 28 | — |
| 573 | 109 | 109 | 43 | 43 | 32 | — |
| 586 | 109 | 109 | 44 | 44 | 32 | — |
| 581 | 109 | 109 | 43 | 43 | 32 | — |
| 568 | 108 | 108 | 34 | 34 | 27 | — |
| 548 | 91 | 91 | 36 | 36 | 29 | — |
| 546 | 90 | 90 | 36 | 36 | 27 | — |
| 544 | 89 | 89 | 35 | 35 | 28 | — |
| 549 | 89 | 89 | 37 | 37 | 26 | — |
| 455 | 85 | 85 | 42 | 42 | 31 | — |
| 538 | 85 | 85 | 33 | 33 | 24 | — |
| 543 | 85 | 85 | 41 | 41 | 30 | — |
| 367 | 70 | 70 | 34 | 34 | 25 | — |
| 533 | 69 | 69 | 35 | 35 | 24 | — |
| 331 | 65 | 65 | 31 | 31 | 22 | — |
| 333 | 65 | 65 | 30 | 30 | 24 | — |
| 380 | 63 | 63 | 35 | 35 | 26 | — |
| 327 | 58 | 58 | 31 | 31 | 23 | — |
| 247 | 55 | 55 | 29 | 29 | 25 | — |
| 265 | 52 | 52 | 29 | 29 | 21 | — |
| 203 | 49 | 49 | 26 | 26 | 19 | — |
| 201 | 48 | 48 | 28 | 28 | 19 | — |
| 288 | 48 | 48 | 33 | 33 | 23 | — |
| 323 | 46 | 46 | 20 | 20 | 17 | — |
| 228 | 43 | 43 | 27 | 27 | 20 | — |
| 77 | 43 | 43 | 23 | 23 | 19 | — |
| 217 | 43 | 43 | 27 | 27 | 20 | — |
| 141 | 40 | 40 | 26 | 26 | 19 | — |
| 43 | 36 | 36 | 21 | 21 | 17 | — |
| 155 | 36 | 36 | 26 | 26 | 21 | — |
| 48 | 32 | 32 | 20 | 20 | 16 | — |
| 0 | 11 | 11 | 9 | 9 | 6 | — |
| **total** | **6,177** | **6,154** | **2,078** | **2,072** | **1,616** | **23** |

As a generation-time filter the rename key is free but saves 0.37%. Keying on the **union** is equally provable — every group bit-identical — and saves 66.46% (2,072 searches kept of 6,177). `relabel_key` keeps only 1,616, but its extra merges are renames *of a rotation* and are not bit-identical; see `COV_POOL_DEDUP_LADDER.md`.

Reproduce: `.venv/bin/python3 -m experiments.heuristic_search.runners.cov_relabel_per_pres`
