# The twelve-row benchmark: cascade against s20_mk2 on identical rows

The twelve Aut-minimal representatives the cascade could not settle at its
100,000-node ceiling, run through both arms at every budget each can reach.
No pre-filtering: rows another arm had already solved were run anyway,
because the point is to measure THIS algorithm, not to close orbits.

## The table

| arm | budget | solved / 12 | s/row |
|---|---:|---:|---:|
| cascade501 | 1,000 | 0 | 0.918 |
| cascade501 | 10,000 | 0 | -- |
| cascade501 | 100,000 | 0 | 111.842 |
| s20_mk2 | 1,000 | 0 | -- |
| s20_mk2 | 10,000 | 0 | -- |
| s20_mk2 | 100,000 | 0 | -- |
| **s20_mk2** | **1,000,000** | **9** | -- |

The three that survive everything: `ac19_44381`, `ac19_51034`, `ac19_65753`.

## Why the cascade lost these rows, and it is not difficulty

Per-row nodes for the nine s20_mk2 settled at 1,000,000:

    229,165  155,673  156,624  151,745  149,461
    149,792  229,844  228,598  110,115

Every one lands between 110k and 230k -- **1.1x to 2.3x above the
cascade's 100,000 cap**. The cascade did not fail because these rows are
hard; it failed because its ceiling sits just below where they solve.
Confirmed directly: at a 250,000-node budget, 9 of the 12 solve and the
same three do not.

The three genuine survivors burned the full 1,000,000 (250.3 s, 221.2 s,
221.5 s) and had already burned 10,000,000 in `ac19_10m` without solving.

## What raising the cap would and would not buy

Raising the cascade's cap to 250,000 would take 9 of these 12 -- but by
the FALL-THROUGH, not by the algorithm. `cascade_heuristics.py:15` caps
`starter_budget` and `rewrite_budget` at 10,000 each, so every node above
that goes to the `s20_mk2` component. Measured on `ac19_44381` at 100,000:

| component | nodes | share |
|---|---:|---:|
| normalization | 0 | 0.0% |
| rewrite | 1 | 0.0% |
| s40_gen | 500 | 0.5% |
| **s20_mk2** | **99,499** | **99.5%** |

So "cascade at 250k" is a budget increase that makes the cascade a strict
superset of s20_mk2 at the same budget. Worth having. Not an advance.

**The untested lever is `s40_gen`.** It is capped at 10,000 and has only
ever been run at 500 -- and at 500 it solved six representatives in 120 to
252 nodes that s20_mk2 could not solve in 10,000,000. Nobody has given it
10,000. That experiment is pure Python at small budgets and costs nothing.

## The cap is not a confound

The cascade ran at mrl 255 and s20_mk2 at mrl 64. On all twelve rows, at a
250,000-node budget, the two caps explore **identical state sets**:

| row | states (cap 64 = cap 255) | longest relator |
|---|---:|---:|
| ac19_20270 | 34,156,353 | 31 |
| ac19_39288 | 17,674,093 | 27 |
| ac19_43611 | 17,787,805 | 27 |
| ac19_44381 | 36,515,155 | 28 |
| ac19_49095 | 17,264,554 | 27 |
| ac19_51034 | 30,548,444 | 31 |
| ac19_54616 | 17,053,703 | 27 |
| ac19_54765 | 17,087,592 | 27 |
| ac19_57992 | 34,286,028 | 31 |
| ac19_65206 | 34,051,516 | 31 |
| ac19_65753 | 30,553,423 | 31 |
| ac19_72328 | 12,916,988 | 29 |

12/12 identical, longest relator 27 to 31 against a cap of 64. The cap
never binds, so the comparison is clean.
