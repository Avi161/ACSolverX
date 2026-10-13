# Searches ended by the cap

Unsolved searches that stopped below the node budget: the frontier was empty, every remaining child was over the cap.

| file | kind | budget | cap | searches | unsolved | of those, stopped before the budget | presentations with one | fewest nodes of those |
|---|---|---|---|---|---|---|---|---|
| `rank3_bf_ms640_b10000_cap24_L1.npz` | rank 3, length 1 | 10,000 | 24 | 1,280 | 365 | 0 | 0 |  |
| `rank3_bf_ms640_b10000_cap24_L2.npz` | rank 3, length 2 | 10,000 | 24 | 3,840 | 760 | 0 | 0 |  |
| `rank3_bf_ms640_b10000_cap24_L3.npz` | rank 3, length 3 | 10,000 | 24 | 11,520 | 2,223 | 0 | 0 |  |
| `rank3_bf_ms640_b10000_cap24_L4.npz` | rank 3, length 4 | 10,000 | 24 | 34,560 | 6,293 | 0 | 0 |  |
| `rank3_bf_ms640_b10000_cap24_control.jsonl` | control | 10,000 | 24 | 640 | 34 | 0 | 0 |  |
| `rank3_bf_ms640_b10000_cap24_relsub.jsonl` | relator subwords | 10,000 | 24 | 69,816 | 20,544 | 0 | 0 |  |

Total: 121,656 searches, 30,219 unsolved, 0 stopped before the budget.

## Children the cap dropped

A child is dropped when one of its relators is longer than the cap. "Could bind" counts the searches in which a dropped child had a heap key (total length, depth) no larger than a state popped later, so a larger cap could have popped it first. Every other search is the same search at any larger cap.

| file | kind | budget | cap | searches | cap dropped a child | could bind | of those, solved | of those, unsolved | children dropped |
|---|---|---|---|---|---|---|---|---|---|
| `rank3_bf_ms640_b10000_cap24_L1.npz` | rank 3, length 1 | 10,000 | 24 | 1,280 | 0 | 0 | 0 | 0 | 0 |
| `rank3_bf_ms640_b10000_cap24_L2.npz` | rank 3, length 2 | 10,000 | 24 | 3,840 | 0 | 0 | 0 | 0 | 0 |
| `rank3_bf_ms640_b10000_cap24_L3.npz` | rank 3, length 3 | 10,000 | 24 | 11,520 | 4 | 0 | 0 | 0 | 440,902 |
| `rank3_bf_ms640_b10000_cap24_L4.npz` | rank 3, length 4 | 10,000 | 24 | 34,560 | 10 | 0 | 0 | 0 | 296,488 |
| `rank3_bf_ms640_b10000_cap24_control.jsonl` | control | 10,000 | 24 | 640 | 26 | 0 | 0 | 0 | 12,195,104 |
| `rank3_bf_ms640_b10000_cap24_relsub.jsonl` | relator subwords | 10,000 | 24 | 69,816 | 10,708 | 0 | 0 | 0 | 176,302,798 |

Total with counters: 121,656 searches, the cap dropped a child in 10,748, could bind in 0 (0 solved, 0 unsolved).
