# EXP-01 — the relator cap: what expansion buys and what it costs

Slice: `train` (40 presentations). Ordering: the baseline (`L`) throughout — this experiment is about the reachable space, not about the heap order. `min_total` is the shortest total length reached; `Δmin` averages it over the presentations that did **not** solve, against the cap-24 arm.

| budget | cap | solved | mean nodes (solved) | mean path | mean min_total (unsolved) |
|---|---|---|---|---|---|
| 500 | 24 | 17/40 | 114 | 16.0 | 17.78 |
| 500 | 32 | 17/40 | 114 | 16.0 | 17.78 |
| 500 | 48 | 17/40 | 114 | 16.0 | 17.78 |
| 500 | 64 | 17/40 | 114 | 16.0 | 17.78 |
| 1000 | 24 | 20/40 | 201 | 19.6 | 17.85 |
| 1000 | 32 | 20/40 | 201 | 19.6 | 17.85 |
| 1000 | 48 | 20/40 | 201 | 19.6 | 17.85 |
| 1000 | 64 | 20/40 | 201 | 19.6 | 17.85 |

Wall clock for the whole sweep: 0.8 min on 9 workers.

