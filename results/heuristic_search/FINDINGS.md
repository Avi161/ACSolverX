# The heuristic — synthesis on the automorphism-disjoint split

Selection and the held-out read both live inside `splits_aut.json`, where no automorphism class appears on both sides — so the held-out number is transfer to genuinely new problems, not memorised change-of-variables twins. **This measures decidable → decidable generalisation; the decidable → second-hump gap is not measurable at ≤1,000 nodes.**

The winner is chosen and validated separately at each budget, because the best ordering at 500 nodes is not the best at 1,000 (EXP-06).

## The recommendation, by node budget

| budget | heuristic | aut_train decidable | aut_test decidable (held-out) |
|---|---|---|---|
| **500** | `[<=16]L1[<=inf]K8.936+L1+xyimb-5.978` | 10/11 (baseline 0/11) | **4/6** (baseline 0/6) |
| **1000** | `[<=16]L1[<=inf]Bmax-2.185+L1+S5.668` | 10/11 (baseline 2/11) | **6/6** (baseline 0/6) |

### Budget 500: `[<=16]L1[<=inf]K8.936+L1+xyimb-5.978`

On held-out aut-classes the gain **shrinks out of sample (+4 test vs +10 train) — some of the training margin was selection**. Per bin on the test slice (floor bins shown so the gain is visibly in the hard bins, not the saturated ones):

| config | bin 0 | bin 1 | bin 2 | bin 3 | bin 4 | bin 5 | bin 6 | bin 7 | decidable |
|---|---|---|---|---|---|---|---|---|---|
| `[<=inf]L1` ← ctrl | 2/2 | 2/2 | 2/2 | 2/2 | 1/2 | 0/2 | 0/1 | 0/2 | **0/4** |
| `[<=16]L1[<=inf]K8.936+L1+xyimb-5.9` | 2/2 | 2/2 | 2/2 | 2/2 | 1/2 | 2/2 | 0/1 | 2/2 | **4/4** |

### Budget 1000: `[<=16]L1[<=inf]Bmax-2.185+L1+S5.668`

On held-out aut-classes the gain **holds out of sample (+6 test vs +8 train)**. Per bin on the test slice (floor bins shown so the gain is visibly in the hard bins, not the saturated ones):

| config | bin 0 | bin 1 | bin 2 | bin 3 | bin 4 | bin 5 | bin 6 | bin 7 | decidable |
|---|---|---|---|---|---|---|---|---|---|
| `[<=inf]L1` ← ctrl | 2/2 | 2/2 | 2/2 | 2/2 | 1/2 | 0/2 | 0/1 | 0/2 | **0/6** |
| `[<=16]L1[<=inf]Bmax-2.185+L1+S5.66` | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 1/1 | 2/2 | **6/6** |

