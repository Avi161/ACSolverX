# EXP-19 — the joint search at budget 1000, over all 17 features

Slice `aut_train` (45), budget 1000, cap 48, 320 configs. Half the random draws are **threshold-free** single weight vectors, which is the shape the current recommendation takes (EXP-18). The held-out slice is not read — it was spent on the finalists.

Decidable subset **31** rows. Baseline **20**.

## The incumbents

| ordering | decidable |
|---|---|
| richer (recommended) | 28/31 |
| richer phased | 28/31 |
| blocks | 28/31 |

## Best-of-N optimism, measured on aut_train

- gain on the half it was **chosen** on: **+4.50**
- gain on the half it was **not**: **+2.85**
- optimism of a best-of-320 pick: **1.65** presentations
- 7 distinct half-split winners

## Did the search find anything better?

- best incumbent: **28/31**
- best of 320: `[<=inf]Bmax-2.185+L1+S5.668` — **28/31** (**+0**)

**Nothing in the enlarged space beats the incumbent.** Searching 17 features at the budget that matters, with the threshold free to vanish, does not improve on the ordering already recommended — which is the strongest statement this program can make that the recommendation is at its local ceiling.

## Do the second-family features show up in the top arms?

| feature | appearances in the top 15 |
|---|---|
| `Bmaxrun` | 3 |
| `Bspread` | 3 |
| `density` | 4 |
| `ratio` | 0 |

## Top 15

| config | decidable | net | p | mean nodes |
|---|---|---|---|---|
| `[<=inf]Bmax-2.185+L1+S5.668` ← incumbent | 28/31 | +8 | 0.008 | 58 |
| `[<=16]L1[<=inf]K2.53+L1+MK6.418+S8.458+xyimb3.292` ← incumbent | 28/31 | +8 | 0.008 | 104 |
| `[<=inf]K2.53+L1+MK6.418+S8.458+xyimb3.292` ← incumbent | 28/31 | +8 | 0.008 | 117 |
| `[<=20]L1[<=inf]Bspread1.506+L1+Lmin0.413+imbal9.992` | 28/31 | +8 | 0.008 | 142 |
| `[<=16]L1[<=inf]Bmaxrun1.18+Bmin-0.683+K10.634+L1+MK0` | 27/31 | +7 | 0.016 | 70 |
| `[<=16]L1[<=inf]K6.396+L1+density4.242` | 27/31 | +7 | 0.016 | 79 |
| `[<=20]L1[<=inf]Bmaxrun0.906+L1+MK7.725+S-3.278+imbal` | 27/31 | +7 | 0.016 | 122 |
| `[<=inf]L1+MK10.119+S6.064+mK-4.31` | 27/31 | +7 | 0.016 | 215 |
| `[<=16]L1[<=inf]Bmax0.382+L1+imbal2.063` | 26/31 | +6 | 0.031 | 84 |
| `[<=12]L1[<=inf]Bmin0.254+L1+S0.951+density0.468+imba` | 26/31 | +6 | 0.031 | 110 |
| `[<=20]L1[<=inf]B14.071+L1+MK4.225+S11.811` | 26/31 | +6 | 0.031 | 153 |
| `[<=inf]Bmaxrun-0.235+Bspread0.228+K1.428+L1+Lmax1.06` | 25/31 | +5 | 0.180 | 30 |
| `[<=inf]Bmin1.385+K6.075+L1+Lmin0.268+S5.006` | 25/31 | +5 | 0.125 | 56 |
| `[<=inf]B1-0.425+K6.45+L1+density0.332` | 25/31 | +5 | 0.125 | 80 |
| `[<=16]L1[<=inf]Bspread-1.818+L1+Lmax9.454+density-8.` | 25/31 | +5 | 0.062 | 85 |
