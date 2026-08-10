# A/B — bench66, budget 1,000, cap 48

3 presentations. Each curve is read off ONE run per (arm, presentation): a search at budget B is the first B pops of any longer search, so the node count at the solve gives every checkpoint below it.

| arm | 100 | 500 | 1,000 |
|---|---|---|---|
| baseline | 3/3 | 3/3 | 3/3 |
| s20 | 3/3 | 3/3 | 3/3 |
| s24 | 3/3 | 3/3 | 3/3 |

## The gap over the baseline — the thing worth watching

| arm | 100 | 500 | 1,000 | verdict |
|---|---|---|---|---|
| s20 | +0 | +0 | +0 | flat |
| s24 | +0 | +0 | +0 | flat |

The local study (≤1,000 nodes) predicted **still widening** for `recommended`. If this run shows it turning over, the extrapolation to large budgets does not hold and the ordering is buying earliness rather than reach — which is worth knowing and worth reporting either way.

