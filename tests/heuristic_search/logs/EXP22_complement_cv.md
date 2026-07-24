# EXP-22 — is the complement strategy real, or hindsight?

EXP-21 paired the recommended climb with a knot-free ordering and reached 23/24, having chosen that ordering *because* it solved the rows the climb misses. This measures the hindsight premium directly, inside EXP-19's existing matrix of **320 configs × 45 presentations at budget 1,000** — no new searches, no fresh slice spent.

Method: 200 random half-splits. On half A pick a second ordering; on half B measure how many rows it adds to the recommended climb's coverage. Three picking rules are compared, so the question is not 'does a second ordering help' but 'does picking it **for complementarity** beat picking it for raw strength'.

The recommended climb alone solves **28/45**; **3** rows are live (it misses them, something else gets them).

| picking rule | marginal gain on the half it was chosen on | on the held-out half |
|---|---|---|
| **complementarity** (adds most rows) | 1.42 | **1.18** |
| stand-alone strength (solves most) | 0.69 | 0.27 |
| random config | — | 0.04 |

Hindsight premium of picking for complementarity: **0.24** rows (1.42 on the chosen half against 1.18 held out).

2 distinct configs won across the 200 splits.

## Verdict

**The strategy is real.** Choosing a second ordering for *complementarity* adds **1.18** rows out of sample, against **0.27** for choosing the strongest stand-alone arm — the thing a reasonable person would do by default. The gap is the whole point of EXP-21's finding, and it survives cross-validation.

But the honest effect size is **1.18 rows**, not the 23/24 EXP-21 showed: that figure carried a 0.24-row hindsight premium. Use the strategy; quote this number.

## The configs that most often won the complement slot

| config | times chosen | solves alone | adds to the climb (all rows) |
|---|---|---|---|
| `[<=20]L1[<=inf]Bspread1.506+L1+Lmin0.413+imbal9.99` | 173/200 | 28/45 | 3 |
| `[<=inf]L1` | 27/200 | 20/45 | 0 |

## Two things worth reading off the winner

**The effect size is 1.18 rows, but that is against a ceiling of 3.** On this slice the recommended climb already solves 28 of 45 and only **3** rows are live — missed by the climb and reachable by something. So a complement chosen for complementarity captures roughly **40% of everything that is available to capture**, out of sample. That is a large share of a small opportunity, and it is the honest way to state it: the strategy works, and what limits it is how little the climb leaves on the table, not how well the complement is chosen.

**The winning complement uses a second-family feature — in the role those features are actually good for.** `Bspread` (longest block minus shortest) never improved the *primary* ordering: EXP-14 found it unlocked nothing, and EXP-19's 320-config sweep never put it in a winner. Yet the config chosen for the complement slot in 173 of 200 splits is `[<=20]L1[<=inf]Bspread1.506+L1+Lmin0.413+imbal9.99`, which solves exactly as many rows alone as the recommended climb (28/45) while overlapping it differently.

That is a distinction worth keeping: a feature can be useless for building the *best* ordering and valuable for building a *different* one. Screening features by whether they improve the leader — which is what EXP-14 did — cannot see that, and would have discarded `Bspread` entirely.
