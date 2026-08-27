# Spectral-transform scout — `L + 4*F_i` @ budget 1,000

Updated `2026-08-04T20:48:45.973467+00:00`

Sweeps the **transform** at a fixed weight, where the shipped work swept the 
weight at a fixed transform. Every variant is normalised to a per-relator [0,1] 
range, so one weight is portable across arms.

**selected_on** = ac1m_hard_aut **train**, first 20 by index (holdouts untouched — a 15-arm sweep would spend one).
Budget 1000, cap 48, weight 4. Engine: `search_fftvar` (`search_signlag` twin). Wall 1.6 min.

> **Scope.** 20 presentations is a *ranking* scout, not a decision: at this n a one-arm gap is noise. It says which transforms are worth a Colab run on the full train 120, and which are already dead.

## Invariance + redundancy (no search — the cheap screen)

| variant | rot-inv | x<->X inv | R² vs 17 feats | mean | std |
|---|:--:|:--:|---:|---:|---:|
| `lag345` | yes | no | 0.253 | 0.756 | 0.362 |
| `lag12` | yes | no | 0.277 | 0.878 | 0.395 |
| `lag68` | yes | no | 0.315 | 0.617 | 0.385 |
| `lagall` | yes | no | 0.268 | 0.807 | 0.354 |
| `dftlo` | yes | no | 0.375 | 1.277 | 0.486 |
| `dfthi` | yes | no | 0.173 | 0.728 | 0.504 |
| `dftpeak` | yes | no | 0.219 | 0.472 | 0.184 |
| `dftcent` | yes | no | 0.229 | 0.825 | 0.350 |
| `dftflat` | yes | no | 0.171 | 0.912 | 0.467 |
| `cplxlo` | yes | **yes** | 0.684 | 1.410 | 0.321 |
| `cplxpeak` | yes | **yes** | 0.300 | 0.664 | 0.170 |
| `same` | yes | **yes** | 0.371 | 0.491 | 0.179 |
| `diff` | yes | **yes** | 0.424 | 0.462 | 0.227 |

All thirteen are rotation-invariant (asserted — a variant that failed would not be a ring feature). `R²` is against the 17 heap features on start states: high means the heap already knows it.

## Search — `L + 4*F_i`, budget 1000

| rank | arm | solved | mean nodes (own solves) | mean min-relator |
|---:|---|---:|---:|---:|
| 1 | `F4_dftlo` | 7/20 | 500 | 11.4 |
| 2 | `F4_cplxlo` | 6/20 | 474 | 11.9 |
| 3 | `F4_cplxpeak` | 4/20 | 746 | 13.5 |
| 4 | `F4_diff` | 3/20 | 385 | 13.8 |
| 5 | `F4_dfthi` | 2/20 | 244 | 14.6 |
| 6 | `F4_dftflat` | 2/20 | 264 | 14.6 |
| 7 | `F4_dftcent` | 2/20 | 326 | 14.6 |
| 8 | `F4_same` | 2/20 | 458 | 14.7 |
| 9 | `F4_lag12` | 1/20 | 226 | 15.3 |
| 10 | `F4_lagall` | 1/20 | 444 | 15.2 |
| 11 | `F4_lag68` | 1/20 | 463 | 15.2 |
| 12 | `F4_dftpeak` | 1/20 | 487 | 15.3 |
| 13 | `F4_lag345` | 1/20 | 496 | 15.2 |
| 14 | `F4_lag345_max` | 1/20 | 641 | 14.8 |
| 15 | **`length`** | **0/20** | — | 16.1 |

## Notes

- Control `length` = 0/20 on this slice.
- `mean nodes` is over each arm's **own** solved set, so arms that solve different presentations are not directly comparable on it — it is a cost sanity check, not a ranking key.
- `mean min-relator` is the shortest total relator length reached, averaged over **all** presentations including unsolved ones — a graded progress signal that does not need a solve, which is what makes n=20 readable at all.
- `F4_lag345_max` swaps the house sum for `2*max` over the two relators (the move that made MK beat K); same transform, different aggregation.
- Unsolved = unsolved within budget 1,000.
