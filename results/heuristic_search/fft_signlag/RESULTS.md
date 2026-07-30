# FFT / sign-lag scout — AC1M-hard Aut

Updated `2026-07-30T01:24:46.782355+00:00`

Mentor: map X/Y → Fourier for knots. Advisor REVISE: **sign channel** + short-lag autocorrelations (FFT band-energy equivalent; generator-bipolar ≈ K / xyimb).

Budget 1000, cap 48. Engine: `search_signlag` (hfast expand + Fsign).

**selected_on** = ac1m_hard_aut train (120)  
**evaluated_on (primary)** = fft fresh holdout (60)  
**evaluated_on (confirmatory, 2nd read)** = spent holdout (60)

## Redundancy (train starts vs 17-dim φ)

- R²(sign-lag F vs 17 feats) = **0.274**
- R²(FFT FspecK sign vs 17) = **0.237**

## Train ranking (selection)

| rank | arm | solved | mean nodes |
|---:|---|---:|---:|
| 1 | `s20_mk2_F4` | 55/120 | 437 |
| 2 | `s20_mk2_F2` | 54/120 | 398 |
| 3 | `s20_mk2` | 54/120 | 454 |
| 4 | `s20_mk2_F8` | 50/120 | 422 |
| 5 | `s20` | 49/120 | 432 |
| 6 | `s20_F2` | 47/120 | 420 |
| 7 | `s20_F4` | 47/120 | 442 |
| 8 | `s20_F8` | 41/120 | 463 |
| 9 | `s20_mk2_F16` | 39/120 | 539 |
| 10 | `length_F4` | 30/120 | 513 |
| 11 | `s20_F16` | 29/120 | 368 |
| 12 | `length_F8` | 29/120 | 500 |
| 13 | `length_F16` | 23/120 | 430 |
| 14 | `length_F2` | 15/120 | 674 |
| 15 | `length` | 0/120 | — |

Promoted for holdout read: `s20_mk2_F4` (best control on train: `s20_mk2` 54/120).

## Fresh holdout (primary)

| arm | solved | mean nodes |
|---|---:|---:|
| `s20_mk2_F4` | 29/60 | 480 |
| `s20_mk2` | 27/60 | 449 |
| `s20` | 27/60 | 496 |
| `length` | 0/60 | — |

## Spent holdout (confirmatory — already used for S+K+MK tune)

| arm | solved | mean nodes |
|---|---:|---:|
| `s20_mk2` | 33/60 | 453 |
| `s20` | 30/60 | 449 |
| `s20_mk2_F4` | 27/60 | 361 |
| `length` | 0/60 | — |

## Notes

- Headline against **s20_mk2 / s20**, not length (length is 0 on this pool).
- Fsign is not invariant under generator-inversion relabel (x↔X); rotation and r→r⁻¹ are fine.
- Unsolved = unsolved within budget 1000.
