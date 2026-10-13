# Searches ended by the cap

Unsolved searches that stopped below the node budget: the frontier was empty, every remaining child was over the cap.

| file | kind | budget | cap | searches | unsolved | of those, stopped before the budget | presentations with one | fewest nodes of those |
|---|---|---|---|---|---|---|---|---|
| `rank3_bf_ms640_b1000_cap24_L1.npz` | rank 3, length 1 | 1,000 | 24 | 1,280 | 511 | 0 | 0 |  |
| `rank3_bf_ms640_b1000_cap24_L2.npz` | rank 3, length 2 | 1,000 | 24 | 3,840 | 1,213 | 0 | 0 |  |
| `rank3_bf_ms640_b1000_cap24_L3.npz` | rank 3, length 3 | 1,000 | 24 | 11,520 | 3,478 | 0 | 0 |  |
| `rank3_bf_ms640_b1000_cap24_L4.npz` | rank 3, length 4 | 1,000 | 24 | 34,560 | 10,864 | 0 | 0 |  |
| `rank3_bf_ms640_b1000_cap24_L5.npz` | rank 3, length 5 | 1,000 | 24 | 103,680 | 33,869 | 0 | 0 |  |
| `rank3_bf_ms640_b1000_cap24_L6.npz` | rank 3, length 6 | 1,000 | 24 | 311,040 | 103,152 | 0 | 0 |  |
| `rank3_bf_ms640_b1000_cap24_control.jsonl` | control | 1,000 | 24 | 640 | 86 | 0 | 0 |  |
| `rank3_bf_ms640_b1000_cap24_relsub.jsonl` | relator subwords | 1,000 | 24 | 69,816 | 29,848 | 0 | 0 |  |

Total: 536,376 searches, 183,021 unsolved, 0 stopped before the budget.

## Children the cap dropped

A child is dropped when one of its relators is longer than the cap. "Could bind" counts the searches in which a dropped child had a heap key (total length, depth) no larger than a state popped later, so a larger cap could have popped it first. Every other search is the same search at any larger cap.

| file | kind | budget | cap | searches | cap dropped a child | could bind | of those, solved | of those, unsolved | children dropped |
|---|---|---|---|---|---|---|---|---|---|
| `rank3_bf_ms640_b1000_cap24_L1.npz` | rank 3, length 1 | 1,000 | 24 | 1,280 | 0 | 0 | 0 | 0 | 0 |
| `rank3_bf_ms640_b1000_cap24_L2.npz` | rank 3, length 2 | 1,000 | 24 | 3,840 | 0 | 0 | 0 | 0 | 0 |
| `rank3_bf_ms640_b1000_cap24_L3.npz` | rank 3, length 3 | 1,000 | 24 | 11,520 | 4 | 0 | 0 | 0 | 187,836 |
| `rank3_bf_ms640_b1000_cap24_L4.npz` | rank 3, length 4 | 1,000 | 24 | 34,560 | 4 | 0 | 0 | 0 | 72,202 |
| `rank3_bf_ms640_b1000_cap24_L5.npz` | rank 3, length 5 | 1,000 | 24 | 103,680 | 68 | 0 | 0 | 0 | 2,392,624 |
| `rank3_bf_ms640_b1000_cap24_L6.npz` | rank 3, length 6 | 1,000 | 24 | 311,040 | 140 | 0 | 0 | 0 | 1,278,290 |
| `rank3_bf_ms640_b1000_cap24_control.jsonl` | control | 1,000 | 24 | 640 | 14 | 0 | 0 | 0 | 446,142 |
| `rank3_bf_ms640_b1000_cap24_relsub.jsonl` | relator subwords | 1,000 | 24 | 69,816 | 10,630 | 0 | 0 | 0 | 8,450,096 |

Total with counters: 536,376 searches, the cap dropped a child in 10,860, could bind in 0 (0 solved, 0 unsolved).
