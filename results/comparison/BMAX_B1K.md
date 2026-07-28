# L + w·Bmax at budget 1,000 (subset-60)

Priority `L + w * Bmax`, where `Bmax = max(mean_x, mean_y)` — the **thicker** generator's mean run length over the pair (same pooling as `S`, but `max` instead of `min`). Cap 24. No K / MK / xyimb.

Mean Bmax on these starts is ~3.23 (vs S ~1.09). Weight grid is contribution-matched to the S sweep (`w_B ≈ w_S · μ_S/μ_B`).

Mean/median nodes and path are over **solved** rows only.

| arm | solved | mean nodes | med nodes | mean path | med path |
|---|---:|---:|---:|---:|---:|
| b1k_greedy (L only) | **29/60** | 175.5 | 61 | 19.2 | 16 |
| b1k_heur (RECOMMENDED) | **43/60** | 214.7 | 106 | 33.0 | 25 |
| `L + 1·Bmax` | **28/60** | 146.5 | 50 | 23.0 | 16 |
| `L + 2·Bmax` | **27/60** | 171.3 | 50 | 23.1 | 15 |
| `L + 3·Bmax` | **27/60** | 223.7 | 55 | 19.3 | 16 |
| `L + 4·Bmax` | **24/60** | 143.5 | 52 | 21.1 | 18 |
| `L + 6·Bmax` | **24/60** | 177.4 | 64 | 22.1 | 19 |
| `L + 8·Bmax` | **21/60** | 95.3 | 71 | 18.2 | 17 |
| `L + 10·Bmax` | **21/60** | 112.0 | 90 | 19.0 | 18 |
| `L + 12·Bmax` | **22/60** | 177.9 | 102 | 19.7 | 18 |
| `L + 16·Bmax` | **23/60** | 185.9 | 109 | 22.7 | 22 |

## Verdict

- Best weight(s): `L + 1·Bmax` → **28/60**
- vs length-only 29/60 and full RECOMMENDED 43/60.
- Contrast: best `L+w·S` (`min`) was **37/60** at w=24 ([`S_B1K.md`](S_B1K.md)). Clustering already found larger mean block near-useless as a classifier (AUC ≈ 0.47); this checks it as a search ordering.

## vs length-only / RECOMMENDED

- w=1: +1 over greedy, -2 vs greedy; vs RECOMMENDED +0 / -15
- w=2: +1 over greedy, -3 vs greedy; vs RECOMMENDED +0 / -16
- w=3: +0 over greedy, -2 vs greedy; vs RECOMMENDED +0 / -16
- w=4: +0 over greedy, -5 vs greedy; vs RECOMMENDED +0 / -19
- w=6: +0 over greedy, -5 vs greedy; vs RECOMMENDED +0 / -19
- w=8: +0 over greedy, -8 vs greedy; vs RECOMMENDED +0 / -22
- w=10: +0 over greedy, -8 vs greedy; vs RECOMMENDED +0 / -22
- w=12: +0 over greedy, -7 vs greedy; vs RECOMMENDED +0 / -21
- w=16: +0 over greedy, -6 vs greedy; vs RECOMMENDED +0 / -20

## Source

- Input: [`cov_heur_b1k_subset60.csv`](cov_heur_b1k_subset60.csv)
- Table: [`bmax_b1k_subset60.csv`](bmax_b1k_subset60.csv)
- Runner: `experiments/heuristic_search/runners/run_bmax_b1k.py`
- Min counterpart: [`S_B1K.md`](S_B1K.md)

