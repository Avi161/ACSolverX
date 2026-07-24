# EXP-20 — split the budget across ORDERINGS instead of relabels

Fixed total budget **1000 nodes** per row on the decidable band (bins 4–7, 24 rows). A team of `k` orderings gives each one `1000/k` nodes and stops at the first solve. Singles are the controls.

The motivation is measured, not assumed: the best single ordering solves 19 of these rows while the union over every ordering tried in this program solves 23, and the knot ordering is known to *reorder* difficulty rather than uniformly improve it (it cracks a 26,838-node row in 108 nodes and misses rows the baseline solves in 16k). Orderings that find different things hard are complementary by construction.

### Singles — the control (1000 nodes each)

| team | solved |
|---|---|
| `richer` | 19/24 |
| `blocks` | 19/24 |
| `K8` | 16/24 |

### Pairs (500 nodes each)

| team | solved |
|---|---|
| `blocks+richer` | 17/24 |
| `K+xyimb` | 16/24 |
| `K8+richer` | 16/24 |
| `K8+blocks` | 13/24 |

### Triples (333 nodes each)

| team | solved |
|---|---|
| `K+xyimb+blocks` | 17/24 |
| `K+xyimb+K8` | 16/24 |
| `K+xyimb+richer` | 16/24 |
| `K8+blocks+richer` | 12/24 |

## Do combinations beat singles as a class?

The honest comparison. Picking the single best team out of 8 combinations is a best-of-N choice and would flatter them; comparing the *distributions* does not.

| group | n | mean solved | best | worst |
|---|---|---|---|---|
| singles | 3 | 18.0/24 | 19/24 | 16/24 |
| pairs | 4 | 15.5/24 | 17/24 | 13/24 |
| triples | 4 | 15.2/24 | 17/24 | 12/24 |

## Verdict

Pairs average **15.5** against singles' **18.0**, so combining does **not** help as a class. Halving the budget costs more than the complementarity buys — the same lesson EXP-17 found for relabels, arriving now on the axis that had a mechanism behind it.

**No combination beats the best single ordering** (19/24). The complementarity is real but only pays when each ordering gets a full budget — which is a statement about running them in sequence with more compute, not about dividing a fixed budget.

## Inside the teams: which member actually solves?

| team | solved | first member | later member |
|---|---|---|---|
| `blocks+richer` | 17/24 | 11 | 6 |
| `K+xyimb+blocks` | 17/24 | 16 | 1 |
| `K+xyimb` | 16/24 | 16 | 0 |
| `K8+richer` | 16/24 | 12 | 4 |
| `K+xyimb+K8` | 16/24 | 16 | 0 |
| `K+xyimb+richer` | 16/24 | 16 | 0 |
| `K8+blocks` | 13/24 | 12 | 1 |
| `K8+blocks+richer` | 12/24 | 12 | 0 |
