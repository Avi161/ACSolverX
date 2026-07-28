# L + w·S at budget 1,000 (subset-60)

Priority `L + w * S`, where `S` is the **smaller mean block** over the pair: pool all x-runs from `r1` and `r2`, same for y, take each generator's mean run length, then `S = min(mean_x, mean_y)`. Cap 24. No K / MK / xyimb.

Mean S on these starts is ~1.09 (almost all in `[1.0, 1.25]`); RECOMMENDED's S coefficient is 8.458. Grid: `{2, 4, 8.458, 12, 16, 20, 24, 32}`.

Mean/median nodes and path are over **solved** rows only.

| arm | solved | mean nodes | med nodes | mean path | med path |
|---|---:|---:|---:|---:|---:|
| b1k_greedy (L only) | **29/60** | 175.5 | 61 | 19.2 | 16 |
| b1k_heur (RECOMMENDED) | **43/60** | 214.7 | 106 | 33.0 | 25 |
| `L + 2·S` | **30/60** | 127.3 | 52 | 19.2 | 16 |
| `L + 4·S` | **33/60** | 176.8 | 62 | 24.2 | 20 |
| `L + 8.458·S` | **35/60** | 165.3 | 54 | 24.2 | 22 |
| `L + 12·S` | **35/60** | 142.6 | 48 | 24.4 | 22 |
| `L + 16·S` | **35/60** | 157.1 | 59 | 25.4 | 22 |
| `L + 20·S` | **36/60** | 160.7 | 84 | 25.4 | 19 |
| `L + 24·S` | **37/60** | 184.3 | 86 | 26.3 | 19 |
| `L + 32·S` | **36/60** | 172.1 | 80 | 26.1 | 18 |

## Verdict

- Best weight: `L + 24·S` → **37/60**
- vs length-only 29/60 and full RECOMMENDED 43/60.
- Nearby one-feature peaks: `L+8·MK` = 38/60, `L+8·K` = 37/60, `L+10·K_den` = 32/60.

## vs length-only / RECOMMENDED

- w=2: +1 over greedy, -0 vs greedy; vs RECOMMENDED +0 / -13
- w=4: +4 over greedy, -0 vs greedy; vs RECOMMENDED +0 / -10
- w=8.458: +6 over greedy, -0 vs greedy; vs RECOMMENDED +0 / -8
- w=12: +6 over greedy, -0 vs greedy; vs RECOMMENDED +0 / -8
- w=16: +6 over greedy, -0 vs greedy; vs RECOMMENDED +0 / -8
- w=20: +7 over greedy, -0 vs greedy; vs RECOMMENDED +0 / -7
- w=24: +8 over greedy, -0 vs greedy; vs RECOMMENDED +0 / -6
- w=32: +7 over greedy, -0 vs greedy; vs RECOMMENDED +1 / -8

## Source

- Input: [`cov_heur_b1k_subset60.csv`](cov_heur_b1k_subset60.csv)
- Table: [`s_b1k_subset60.csv`](s_b1k_subset60.csv)
- Runner: `experiments/heuristic_search/runners/run_s_b1k.py`

