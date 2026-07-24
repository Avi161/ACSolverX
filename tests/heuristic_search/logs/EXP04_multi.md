# EXP-04 — joint weight search, with the selection bias measured

Slice: `train` (40). Budget 500, cap 48, 700 configs (random weights over 11 features + a length-keyed threshold). Control = baseline, **17/40**.

## What best-of-N selection is worth on its own

Choosing the best config on a random half of `train` and scoring it on the other half, 40 times:

- gain on the half it was **chosen** on: **+5.10** presentations
- gain on the half it was **not** chosen on: **+4.90**
- so the optimism of a best-of-700 pick is **0.20** presentations
- 1 distinct configs won across the 40 splits; the most frequent won 100% of them

Any headline below smaller than that optimism figure is selection, not signal.

## Top 20 by training solves

| config | solved | net | p | mean nodes | mean path | Δmin |
|---|---|---|---|---|---|---|
| `[<=16]L1[<=inf]K8.936+L1+xyimb-5.978` | 27/40 | +10 | 0.002 | 62 | 14.3 | +1.54 |
| `[<=8]L1[<=inf]B10.307+L1+MK4.962+S6.408` | 25/40 | +8 | 0.008 | 57 | 16.5 | +1.00 |
| `[<=16]L1[<=inf]K2.53+L1+MK6.418+S8.458+xyimb3.292` | 25/40 | +8 | 0.008 | 60 | 14.9 | +1.47 |
| `[<=16]L1[<=inf]B11.25+K7.884+L1` | 25/40 | +8 | 0.008 | 102 | 14.4 | +1.13 |
| `[<=8]L1[<=inf]Bmin-0.113+K1.809+L1+imbal0.743+xyimb-0.118` | 24/40 | +7 | 0.016 | 47 | 16.7 | +1.12 |
| `[<=8]L1[<=inf]Bmax-3.046+Bmin-0.499+L1+MK0.612+xyimb-0.109` | 24/40 | +7 | 0.016 | 77 | 14.6 | +1.19 |
| `[<=inf]K7.119+L1+xyimb-2.169` | 24/40 | +7 | 0.016 | 80 | 14.8 | +1.00 |
| `[<=12]L1[<=inf]B1-0.272+K1.325+L1+MK-0.499+imbal1.031` | 23/40 | +6 | 0.031 | 40 | 18.5 | +0.82 |
| `[<=16]L1[<=inf]Bmax-2.185+L1+S5.668` | 23/40 | +6 | 0.031 | 49 | 14.4 | +1.18 |
| `[<=16]L1[<=inf]K2.51+L1+Lmax5.895+mK13.556` | 23/40 | +6 | 0.031 | 50 | 14.2 | +0.94 |
| `[<=16]L1[<=inf]K4.769+L1+imbal0.291` | 23/40 | +6 | 0.031 | 55 | 14.4 | +0.88 |
| `[<=16]L1[<=inf]Bmin0.29+L1+Lmax0.333+xyimb-10.785` | 23/40 | +6 | 0.031 | 59 | 14.9 | +0.41 |
| `[<=inf]K-0.322+L1+Lmax4.993` | 23/40 | +6 | 0.031 | 60 | 14.9 | +0.47 |
| `[<=inf]B1-0.537+K2.21+L1+Lmax12.02+xyimb0.688` | 23/40 | +6 | 0.031 | 60 | 15.5 | +1.06 |
| `[<=10]L1[<=inf]Bmax0.228+L1+Lmax10.895` | 23/40 | +6 | 0.031 | 60 | 15.1 | +0.88 |
| `[<=6]L1[<=inf]Bmax0.147+L1+Lmax11.396` | 23/40 | +6 | 0.031 | 60 | 15.1 | +0.88 |
| `[<=16]L1[<=inf]K5.579+L1+xyimb-1.066` | 23/40 | +6 | 0.031 | 61 | 14.3 | +0.88 |
| `[<=16]L1[<=inf]K0.524+L1+Lmax0.235+S0.175+mK12.546` | 23/40 | +6 | 0.031 | 61 | 14.4 | +0.71 |
| `[<=16]L1[<=inf]B1-0.315+L1+Lmin-0.569+xyimb-0.687` | 23/40 | +6 | 0.031 | 63 | 15.8 | +0.00 |
| `[<=12]L1[<=inf]Bmax0.394+K7.948+L1+imbal0.162` | 23/40 | +6 | 0.031 | 67 | 14.8 | +1.00 |

## The robustness pick

Best *worst-half* score over the inner splits: `[<=16]L1[<=inf]K8.936+L1+xyimb-5.978` — 27/40 overall, net +10. Same as the greedy pick.

