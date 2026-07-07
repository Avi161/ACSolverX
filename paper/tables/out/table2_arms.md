| Arm | Solved/640 | Exhausted | Nodes (median) | Nodes (mean) | Path len (median) | ⊆ baseline? |
|---|---|---|---|---|---|---|
| baseline | 634 | 6 | 11 | 1662.0 | 8 | — |
| r1 | 619 | 21 | 13 | 2802.6 | 12 | yes |
| r2 | 602 | 38 | 13 | 3637.1 | 11 | yes |
| x | 540 | 100 | 10 | 14680.7 | 9 | yes |
| y | 523 | 117 | 10 | 21832.7 | 9 | yes |

*Note: ⊆ baseline? tests whether the arm's solved-idx set is a subset of the baseline's solved-idx set, computed directly from the 640-row calibration streams (not assumed).*

*Note: Nodes/Path-len statistics are computed over SOLVED presentations only (budget-exhausted rows report nodes_explored == budget_nodes, which would otherwise dominate the mean).*
