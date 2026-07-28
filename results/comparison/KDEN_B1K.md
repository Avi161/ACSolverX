# L + w·K_den at budget 1,000 (subset-60)

Priority `L + w * ((k1+k2)/L)`. Cap 24. Compared to shipped `b1k_greedy` (length-only) and `b1k_heur` (full RECOMMENDED).

Mean/median nodes and path are over **solved** rows only.

| arm | solved | mean nodes | med nodes | mean path | med path |
|---|---:|---:|---:|---:|---:|
| b1k_greedy (L only) | **29/60** | 175.5 | 61 | 19.2 | 16 |
| b1k_heur (RECOMMENDED) | **43/60** | 214.7 | 106 | 33.0 | 25 |
| `L + 10·K_den` | **32/60** | 218.2 | 79 | 24.3 | 22 |
| `L + 40·K_den` | **31/60** | 136.7 | 77 | 26.8 | 21 |
| `L + 80·K_den` | **28/60** | 174.0 | 105 | 33.1 | 30 |
| `L + 160·K_den` | **1/60** | 3.0 | 3 | 2.0 | 2 |

## vs length-only

- w=10: +3 over greedy, -0 vs greedy; vs RECOMMENDED +0 / -11
- w=40: +5 over greedy, -3 vs greedy; vs RECOMMENDED +0 / -12
- w=80: +9 over greedy, -10 vs greedy; vs RECOMMENDED +0 / -15
- w=160: +0 over greedy, -28 vs greedy; vs RECOMMENDED +0 / -42

## Source

- Input: [`cov_heur_b1k_subset60.csv`](cov_heur_b1k_subset60.csv)
- Table: [`kden_b1k_subset60.csv`](kden_b1k_subset60.csv)
- Runner: `experiments/heuristic_search/runners/run_kden_b1k.py`
