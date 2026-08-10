# A/B — solved_1hop_autclean, budget 100,000, cap 48

86 complete presentations (all 5 arms present; 0 partial rows ignored). Job order was presentation-major.

| arm | 1,000 | 5,000 | 10,000 | 25,000 | 50,000 | 100,000 |
|---|---|---|---|---|---|---|
| baseline | 65/86 | 73/86 | 73/86 | 75/86 | 76/86 | 76/86 |
| s12 | 69/86 | 72/86 | 75/86 | 78/86 | 78/86 | 78/86 |
| s28 | 67/86 | 70/86 | 71/86 | 73/86 | 78/86 | 78/86 |
| s20_mk2 | 66/86 | 71/86 | 77/86 | 79/86 | 80/86 | 82/86 |
| s24_k1_mk2 | 66/86 | 71/86 | 75/86 | 80/86 | 82/86 | 83/86 |

## Δ vs length baseline (complete rows only)

| arm | 1,000 | 5,000 | 10,000 | 25,000 | 50,000 | 100,000 | verdict |
|---|---|---|---|---|---|---|---|
| s12 | +4 | -1 | +2 | +3 | +2 | +2 | flat |
| s28 | +2 | -3 | -2 | -2 | +2 | +2 | still widening |
| s20_mk2 | +1 | -2 | +4 | +4 | +4 | +6 | still widening |
| s24_k1_mk2 | +1 | -2 | +2 | +5 | +6 | +7 | still widening |
