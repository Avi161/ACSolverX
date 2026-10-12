# Searches ended by the cap

Unsolved searches that stopped below the node budget: the frontier was empty, every remaining child was over the cap.

| file | kind | budget | cap | searches | unsolved | of those, stopped before the budget | presentations with one | fewest nodes of those |
|---|---|---|---|---|---|---|---|---|
| `rank3_bf_ms640_b10000_cap24_L1.npz` | rank 3, length 1 | 10,000 | 24 | 1,280 | 365 | 0 | 0 |  |
| `rank3_bf_ms640_b10000_cap24_L2.npz` | rank 3, length 2 | 10,000 | 24 | 3,840 | 760 | 0 | 0 |  |
| `rank3_bf_ms640_b10000_cap24_L3.npz` | rank 3, length 3 | 10,000 | 24 | 11,520 | 2,223 | 0 | 0 |  |
| `rank3_bf_ms640_b10000_cap24_L4.npz` | rank 3, length 4 | 10,000 | 24 | 34,560 | 6,293 | 0 | 0 |  |
| `rank3_bf_ms640_b10000_cap24_L5.npz` | rank 3, length 5 | 10,000 | 24 | 103,680 | 19,286 | 0 | 0 |  |
| `rank3_bf_ms640_b10000_cap24_L6.npz` | rank 3, length 6 | 10,000 | 24 | 311,040 | 59,215 | 0 | 0 |  |
| `rank3_bf_ms640_b10000_cap24_L7.npz` | rank 3, length 7 | 10,000 | 24 | 933,120 | 179,717 | 0 | 0 |  |
| `rank3_bf_ms640_b10000_cap24_control.jsonl` | control | 10,000 | 24 | 640 | 34 | 0 | 0 |  |
| `rank3_bf_ms640_b10000_cap24_relsub.jsonl.gz` | relator subwords | 10,000 | 24 | 69,816 | 20,544 | 0 | 0 |  |
| `rank3_bf_ms640_b1000_cap24_L1.npz` | rank 3, length 1 | 1,000 | 24 | 1,280 | 511 | 0 | 0 |  |
| `rank3_bf_ms640_b1000_cap24_L10.npz` | rank 3, length 10 | 1,000 | 24 | 25,194,240 | 8,643,543 | 0 | 0 |  |
| `rank3_bf_ms640_b1000_cap24_L1_inv.npz` | rank 3, length 1, inverse words | 1,000 | 24 | 1,280 | 511 | 0 | 0 |  |
| `rank3_bf_ms640_b1000_cap24_L2.npz` | rank 3, length 2 | 1,000 | 24 | 3,840 | 1,213 | 0 | 0 |  |
| `rank3_bf_ms640_b1000_cap24_L2_inv.npz` | rank 3, length 2, inverse words | 1,000 | 24 | 3,840 | 1,207 | 0 | 0 |  |
| `rank3_bf_ms640_b1000_cap24_L3.npz` | rank 3, length 3 | 1,000 | 24 | 11,520 | 3,478 | 0 | 0 |  |
| `rank3_bf_ms640_b1000_cap24_L3_inv.npz` | rank 3, length 3, inverse words | 1,000 | 24 | 11,520 | 3,473 | 0 | 0 |  |
| `rank3_bf_ms640_b1000_cap24_L4.npz` | rank 3, length 4 | 1,000 | 24 | 34,560 | 10,864 | 0 | 0 |  |
| `rank3_bf_ms640_b1000_cap24_L4_inv.npz` | rank 3, length 4, inverse words | 1,000 | 24 | 34,560 | 10,859 | 0 | 0 |  |
| `rank3_bf_ms640_b1000_cap24_L5.npz` | rank 3, length 5 | 1,000 | 24 | 103,680 | 33,869 | 0 | 0 |  |
| `rank3_bf_ms640_b1000_cap24_L5_inv.npz` | rank 3, length 5, inverse words | 1,000 | 24 | 103,680 | 33,845 | 0 | 0 |  |
| `rank3_bf_ms640_b1000_cap24_L6.npz` | rank 3, length 6 | 1,000 | 24 | 311,040 | 103,152 | 0 | 0 |  |
| `rank3_bf_ms640_b1000_cap24_L6_inv.npz` | rank 3, length 6, inverse words | 1,000 | 24 | 311,040 | 103,000 | 0 | 0 |  |
| `rank3_bf_ms640_b1000_cap24_L7.npz` | rank 3, length 7 | 1,000 | 24 | 933,120 | 312,480 | 0 | 0 |  |
| `rank3_bf_ms640_b1000_cap24_L8.npz` | rank 3, length 8 | 1,000 | 24 | 2,799,360 | 946,046 | 0 | 0 |  |
| `rank3_bf_ms640_b1000_cap24_L9.npz` | rank 3, length 9 | 1,000 | 24 | 8,398,080 | 2,862,579 | 0 | 0 |  |
| `rank3_bf_ms640_b1000_cap24_control.jsonl` | control | 1,000 | 24 | 640 | 86 | 0 | 0 |  |
| `rank3_bf_ms640_b1000_cap24_relsub.jsonl.gz` | relator subwords | 1,000 | 24 | 69,816 | 29,848 | 0 | 0 |  |
| `rankn_bf_ms640_b1000_cap24_r4.npz` | rank 4 | 1,000 | 24 | 224,640 | 91,779 | 0 | 0 |  |
| `rankn_bf_ms640_b1000_cap24_r5.npz` | rank 5 | 1,000 | 24 | 76,800 | 35,649 | 0 | 0 |  |

Total: 40,098,032 searches, 13,516,429 unsolved, 0 stopped before the budget.

## Children the cap dropped

A child is dropped when one of its relators is longer than the cap. "Could bind" counts the searches in which a dropped child had a heap key (total length, depth) no larger than a state popped later, so a larger cap could have popped it first. Every other search is the same search at any larger cap.

| file | kind | budget | cap | searches | cap dropped a child | could bind | of those, solved | of those, unsolved | children dropped |
|---|---|---|---|---|---|---|---|---|---|
| `rank3_bf_ms640_b10000_cap24_L1.npz` | rank 3, length 1 | 10,000 | 24 | 1,280 | 0 | 0 | 0 | 0 | 0 |
| `rank3_bf_ms640_b10000_cap24_L2.npz` | rank 3, length 2 | 10,000 | 24 | 3,840 | 0 | 0 | 0 | 0 | 0 |
| `rank3_bf_ms640_b10000_cap24_L3.npz` | rank 3, length 3 | 10,000 | 24 | 11,520 | 4 | 0 | 0 | 0 | 440,902 |
| `rank3_bf_ms640_b10000_cap24_L4.npz` | rank 3, length 4 | 10,000 | 24 | 34,560 | 10 | 0 | 0 | 0 | 296,488 |
| `rank3_bf_ms640_b10000_cap24_L5.npz` | rank 3, length 5 | 10,000 | 24 | 103,680 | 198 | 0 | 0 | 0 | 29,730,824 |
| `rank3_bf_ms640_b10000_cap24_control.jsonl` | control | 10,000 | 24 | 640 | 26 | 0 | 0 | 0 | 12,195,104 |
| `rank3_bf_ms640_b10000_cap24_relsub.jsonl.gz` | relator subwords | 10,000 | 24 | 69,816 | 10,708 | 0 | 0 | 0 | 176,302,798 |
| `rank3_bf_ms640_b1000_cap24_L1.npz` | rank 3, length 1 | 1,000 | 24 | 1,280 | 0 | 0 | 0 | 0 | 0 |
| `rank3_bf_ms640_b1000_cap24_L1_inv.npz` | rank 3, length 1, inverse words | 1,000 | 24 | 1,280 | 0 | 0 | 0 | 0 | 0 |
| `rank3_bf_ms640_b1000_cap24_L2.npz` | rank 3, length 2 | 1,000 | 24 | 3,840 | 0 | 0 | 0 | 0 | 0 |
| `rank3_bf_ms640_b1000_cap24_L2_inv.npz` | rank 3, length 2, inverse words | 1,000 | 24 | 3,840 | 0 | 0 | 0 | 0 | 0 |
| `rank3_bf_ms640_b1000_cap24_L3.npz` | rank 3, length 3 | 1,000 | 24 | 11,520 | 4 | 0 | 0 | 0 | 187,836 |
| `rank3_bf_ms640_b1000_cap24_L3_inv.npz` | rank 3, length 3, inverse words | 1,000 | 24 | 11,520 | 4 | 0 | 0 | 0 | 187,000 |
| `rank3_bf_ms640_b1000_cap24_L4.npz` | rank 3, length 4 | 1,000 | 24 | 34,560 | 4 | 0 | 0 | 0 | 72,202 |
| `rank3_bf_ms640_b1000_cap24_L4_inv.npz` | rank 3, length 4, inverse words | 1,000 | 24 | 34,560 | 4 | 0 | 0 | 0 | 72,202 |
| `rank3_bf_ms640_b1000_cap24_L5.npz` | rank 3, length 5 | 1,000 | 24 | 103,680 | 68 | 0 | 0 | 0 | 2,392,624 |
| `rank3_bf_ms640_b1000_cap24_L5_inv.npz` | rank 3, length 5, inverse words | 1,000 | 24 | 103,680 | 68 | 0 | 0 | 0 | 2,395,130 |
| `rank3_bf_ms640_b1000_cap24_L6.npz` | rank 3, length 6 | 1,000 | 24 | 311,040 | 140 | 0 | 0 | 0 | 1,278,290 |
| `rank3_bf_ms640_b1000_cap24_L6_inv.npz` | rank 3, length 6, inverse words | 1,000 | 24 | 311,040 | 140 | 0 | 0 | 0 | 1,278,076 |
| `rank3_bf_ms640_b1000_cap24_L7.npz` | rank 3, length 7 | 1,000 | 24 | 933,120 | 1,862 | 0 | 0 | 0 | 55,854,194 |
| `rank3_bf_ms640_b1000_cap24_L8.npz` | rank 3, length 8 | 1,000 | 24 | 2,799,360 | 21,431 | 0 | 0 | 0 | 335,186,728 |
| `rank3_bf_ms640_b1000_cap24_control.jsonl` | control | 1,000 | 24 | 640 | 14 | 0 | 0 | 0 | 446,142 |
| `rank3_bf_ms640_b1000_cap24_relsub.jsonl.gz` | relator subwords | 1,000 | 24 | 69,816 | 10,630 | 0 | 0 | 0 | 8,450,096 |

Total with counters: 4,960,112 searches, the cap dropped a child in 45,315, could bind in 0 (0 solved, 0 unsolved).
