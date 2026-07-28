# L + w·MK at budget 1,000 (subset-60)

Priority `L + w * max(knots(r1), knots(r2))`. Cap 24. No K / S / xyimb. Compared to shipped `b1k_greedy` (length-only) and `b1k_heur` (full RECOMMENDED).

Mean MK on these starts is ~2.6; RECOMMENDED's MK coefficient is 6.418. Grid: `{2, 4, 6.418, 8, 10, 12, 16, 24}`.

Mean/median nodes and path are over **solved** rows only.

| arm | solved | mean nodes | med nodes | mean path | med path |
|---|---:|---:|---:|---:|---:|
| b1k_greedy (L only) | **29/60** | 175.5 | 61 | 19.2 | 16 |
| b1k_heur (RECOMMENDED) | **43/60** | 214.7 | 106 | 33.0 | 25 |
| `L + 2·MK` | **33/60** | 195.5 | 94 | 22.4 | 21 |
| `L + 4·MK` | **35/60** | 233.7 | 155 | 24.4 | 21 |
| `L + 6.418·MK` | **37/60** | 256.7 | 211 | 29.2 | 21 |
| `L + 8·MK` | **38/60** | 286.9 | 211 | 31.4 | 21 |
| `L + 10·MK` | **37/60** | 286.7 | 226 | 31.3 | 21 |
| `L + 12·MK` | **36/60** | 290.4 | 265 | 29.4 | 20 |
| `L + 16·MK` | **34/60** | 307.8 | 322 | 27.1 | 19 |
| `L + 24·MK` | **34/60** | 408.9 | 495 | 27.1 | 19 |

## Verdict

- Best weight: `L + 8·MK` → **38/60**
- vs length-only 29/60 and full RECOMMENDED 43/60.
- Nearby one-feature peaks for context: `L+8·K` = 37/60, `L+10·K_den` = 32/60.

## vs length-only / RECOMMENDED

- w=2: +4 over greedy, -0 vs greedy; vs RECOMMENDED +0 / -10
- w=4: +7 over greedy, -1 vs greedy; vs RECOMMENDED +0 / -8
- w=6.418: +9 over greedy, -1 vs greedy; vs RECOMMENDED +0 / -6
- w=8: +10 over greedy, -1 vs greedy; vs RECOMMENDED +0 / -5
- w=10: +9 over greedy, -1 vs greedy; vs RECOMMENDED +0 / -6
- w=12: +8 over greedy, -1 vs greedy; vs RECOMMENDED +0 / -7
- w=16: +7 over greedy, -2 vs greedy; vs RECOMMENDED +0 / -9
- w=24: +7 over greedy, -2 vs greedy; vs RECOMMENDED +0 / -9

## Source

- Input: [`cov_heur_b1k_subset60.csv`](cov_heur_b1k_subset60.csv)
- Table: [`mk_b1k_subset60.csv`](mk_b1k_subset60.csv)
- Runner: `experiments/heuristic_search/runners/run_mk_b1k.py`

