# L + w·K_den vs L + w·K at budget 1,000 (subset-60)

One-feature orderings, no xyimb / MK / S. Cap 24. Compared to shipped `b1k_greedy` (length-only) and `b1k_heur` (full RECOMMENDED).

## Why the weight ranges differ

On this set the original starts have mean `K ≈ 4.53` and `K_den ≈ 0.247` (mean `L ≈ 19.3`). Matching priority contribution `w_K · K ≈ w_den · K_den` gives `w_K ≈ w_den / L`:

| `w_den` | ≈ matching `w_K` |
|---:|---:|
| 5 | 0.27 |
| 10 | 0.55 |
| 20 | 1.09 |
| 40 | 2.18 |
| 80 | 4.36 |

So the `K_den` grid stays at `{5, 10, 20, 40, 80}` (prior peak was `w=10` → 32/60; 160 collapsed to 1/60 and is dropped). The raw-`K` grid starts at `{0.5, 1, 2, 2.53, 5}` (dens-band map + RECOMMENDED `2.53` + one step above) and extends to `{8, 10, 16}` after the mapped-band edge won the first pass.

Mean/median nodes and path are over **solved** rows only.

| arm | solved | mean nodes | med nodes | mean path | med path |
|---|---:|---:|---:|---:|---:|
| b1k_greedy (L only) | **29/60** | 175.5 | 61 | 19.2 | 16 |
| b1k_heur (RECOMMENDED) | **43/60** | 214.7 | 106 | 33.0 | 25 |

### `L + w·K_den`

| arm | solved | mean nodes | med nodes | mean path | med path |
|---|---:|---:|---:|---:|---:|
| `L + 5·K_den` | **29/60** | 157.6 | 61 | 19.4 | 16 |
| `L + 10·K_den` | **32/60** | 218.2 | 79 | 24.3 | 22 |
| `L + 20·K_den` | **28/60** | 154.9 | 45 | 21.0 | 17 |
| `L + 40·K_den` | **31/60** | 136.7 | 77 | 26.8 | 21 |
| `L + 80·K_den` | **28/60** | 174.0 | 105 | 33.1 | 30 |

### `L + w·K` (total knots)

| arm | solved | mean nodes | med nodes | mean path | med path |
|---|---:|---:|---:|---:|---:|
| `L + 0.5·K` | **31/60** | 198.4 | 98 | 20.1 | 17 |
| `L + 1·K` | **30/60** | 195.4 | 104 | 21.4 | 18 |
| `L + 2·K` | **30/60** | 153.6 | 67 | 22.7 | 20 |
| `L + 2.53·K` | **32/60** | 196.8 | 72 | 27.9 | 20 |
| `L + 5·K` | **36/60** | 192.8 | 95 | 31.4 | 21 |
| `L + 8·K` | **37/60** | 156.8 | 97 | 28.2 | 21 |
| `L + 10·K` | **36/60** | 170.3 | 104 | 28.2 | 21 |
| `L + 16·K` | **36/60** | 270.6 | 117 | 28.2 | 21 |

## Verdict

- Best density arm: `L + 10·K_den` → **32/60**
- Best raw-K arm: `L + 8·K` → **37/60**
- Winner (solve count): `L + 8·K` (37/60)
- Both vs length-only 29/60 and full RECOMMENDED 43/60.

## vs length-only / RECOMMENDED

### K_den

- w=5: +0 over greedy, -0 vs greedy; vs RECOMMENDED +0 / -14
- w=10: +3 over greedy, -0 vs greedy; vs RECOMMENDED +0 / -11
- w=20: +1 over greedy, -2 vs greedy; vs RECOMMENDED +0 / -15
- w=40: +5 over greedy, -3 vs greedy; vs RECOMMENDED +0 / -12
- w=80: +9 over greedy, -10 vs greedy; vs RECOMMENDED +0 / -15

### K

- w=0.5: +2 over greedy, -0 vs greedy; vs RECOMMENDED +0 / -12
- w=1: +2 over greedy, -1 vs greedy; vs RECOMMENDED +0 / -13
- w=2: +3 over greedy, -2 vs greedy; vs RECOMMENDED +0 / -13
- w=2.53: +5 over greedy, -2 vs greedy; vs RECOMMENDED +0 / -11
- w=5: +9 over greedy, -2 vs greedy; vs RECOMMENDED +0 / -7
- w=8: +10 over greedy, -2 vs greedy; vs RECOMMENDED +0 / -6
- w=10: +9 over greedy, -2 vs greedy; vs RECOMMENDED +0 / -7
- w=16: +9 over greedy, -2 vs greedy; vs RECOMMENDED +0 / -7

## Best arms head-to-head

- Only density (`w=10`): ['538', '548', '589']
- Only raw K (`w=8`): ['549', '565', '575', '581', '586', '606', '628', '633']
- Both: 29; neither of these two: 20

## Source

- Input: [`cov_heur_b1k_subset60.csv`](cov_heur_b1k_subset60.csv)
- Table: [`k_vs_kden_b1k_subset60.csv`](k_vs_kden_b1k_subset60.csv)
- Runner: `experiments/heuristic_search/runners/run_k_vs_kden_b1k.py`
- Prior dens-only sweep: [`KDEN_B1K.md`](KDEN_B1K.md)
