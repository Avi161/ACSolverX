# Equal-proportion K + MK + S at budget 1,000 (subset-60)

Best one-feature peaks were `L+8·K` (37), `L+8·MK` (38), `L+24·S` (37). Those make unequal mean contributions on this set (~36.3 / ~20.8 / ~26.2). This run standardizes each feature by its subset-60 mean so the three enter in **equal proportions**, then sweeps shared strength `α`:

```
score = L + α · (K/4.53333 + MK/2.6 + S/1.09)
```

Equivalent raw weights: `w_K = α/μ_K`, `w_MK = α/μ_MK`, `w_S = α/μ_S`. At typical starts each feature contributes `α`. `α ≈ 28` matches the average one-feature peak contribution (27.7). Cap 24; no xyimb.

`S` = smaller mean block (thinner generator over the pair), not shorter-relator length.

Mean/median nodes and path are over **solved** rows only.

| arm | solved | mean nodes | med nodes | mean path | med path |
|---|---:|---:|---:|---:|---:|
| b1k_greedy (L only) | **29/60** | 175.5 | 61 | 19.2 | 16 |
| b1k_heur (RECOMMENDED) | **43/60** | 214.7 | 106 | 33.0 | 25 |

| α | raw (w_K, w_MK, w_S) | solved | mean nodes | med nodes | mean path | med path |
|---:|---|---:|---:|---:|---:|---:|
| 1 | (0.221, 0.385, 0.917) | **33/60** | 220.2 | 93 | 26.1 | 21 |
| 2 | (0.441, 0.769, 1.835) | **32/60** | 178.5 | 87 | 21.7 | 19 |
| 3 | (0.662, 1.154, 2.752) | **35/60** | 217.5 | 85 | 24.9 | 21 |
| 4 | (0.882, 1.538, 3.670) | **37/60** | 214.2 | 95 | 28.7 | 23 |
| 5 | (1.103, 1.923, 4.587) | **40/60** | 236.1 | 125 | 35.1 | 27 |
| 6 | (1.324, 2.308, 5.505) | **40/60** | 190.2 | 100 | 34.0 | 26 |
| 8 | (1.765, 3.077, 7.339) | **39/60** | 155.8 | 68 | 32.7 | 25 |
| 10 | (2.206, 3.846, 9.174) | **39/60** | 158.7 | 61 | 25.4 | 23 |
| 15 | (3.309, 5.769, 13.761) | **39/60** | 124.6 | 67 | 23.4 | 22 |
| 20 | (4.412, 7.692, 18.349) | **39/60** | 144.2 | 70 | 22.8 | 22 |
| 28 | (6.176, 10.769, 25.688) | **39/60** | 197.4 | 95 | 21.8 | 22 |
| 40 | (8.824, 15.385, 36.697) | **39/60** | 319.3 | 120 | 22.1 | 22 |

## Verdict

- Best tune(s): `α=5` and `α=6` → **40/60**
  - `α=5` raw: `L + 1.103·K + 1.923·MK + 4.587·S`
  - `α=6` raw: `L + 1.324·K + 2.308·MK + 5.505·S`
- vs length-only 29/60 and full RECOMMENDED 43/60 (RECOMMENDED also has xyimb).
- One-feature peaks for context: `L+8·MK` = 38/60, `L+8·K` = 37/60, `L+24·S` = 37/60.
- Stronger equal mixes (`α≥8`) plateau at 39/60 — weaker equal mix beats copying the one-feature peak scale (`α≈28`).

## vs length-only / RECOMMENDED

- α=1: +4 over greedy, -0 vs greedy; vs RECOMMENDED +0 / -10
- α=2: +3 over greedy, -0 vs greedy; vs RECOMMENDED +0 / -11
- α=3: +6 over greedy, -0 vs greedy; vs RECOMMENDED +0 / -8
- α=4: +8 over greedy, -0 vs greedy; vs RECOMMENDED +0 / -6
- α=5: +11 over greedy, -0 vs greedy; vs RECOMMENDED +0 / -3
- α=6: +11 over greedy, -0 vs greedy; vs RECOMMENDED +0 / -3
- α=8: +10 over greedy, -0 vs greedy; vs RECOMMENDED +0 / -4
- α=10: +10 over greedy, -0 vs greedy; vs RECOMMENDED +0 / -4
- α=15: +10 over greedy, -0 vs greedy; vs RECOMMENDED +0 / -4
- α=20: +10 over greedy, -0 vs greedy; vs RECOMMENDED +0 / -4
- α=28: +10 over greedy, -0 vs greedy; vs RECOMMENDED +0 / -4
- α=40: +10 over greedy, -0 vs greedy; vs RECOMMENDED +0 / -4

## Source

- Input: [`cov_heur_b1k_subset60.csv`](cov_heur_b1k_subset60.csv)
- Table: [`kms_equal_b1k_subset60.csv`](kms_equal_b1k_subset60.csv)
- Runner: `experiments/heuristic_search/runners/run_kms_equal_b1k.py`
- Prior one-feature: [`K_VS_KDEN_B1K.md`](K_VS_KDEN_B1K.md), [`MK_B1K.md`](MK_B1K.md), [`S_B1K.md`](S_B1K.md)

