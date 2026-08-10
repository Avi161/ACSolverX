# AC19 extended Aut-min screen — cleaned comparison

Updated `2026-07-31T06:29:45.006286+00:00`

Source: `results/heuristic_search/hsearch_ac19_autmin_1k/` (5 Colab chunks × budget 1k full arms + budget 10k on the top 4).

## Cleaning

- Raw rows: 1k=576,796, 10k=286,201. No duplicate `(arm, name, budget)` keys.
- Complete intersection (all arms present): 1k **68,962** / 72,779; 10k **69,224** / 72,779.
- Selection-overlap Aut reps excluded for a secondary rate: 1k −131, 10k −132 (remaining clean n=68,831 / 69,092).
- Partial arm rows (resume holes) are dropped from the denominator — never imputed.

## Headline — budget 1,000 (8 arms)

| arm | solved | rate | Δ vs baseline | median nodes (own solved) | median path |
|---|---:|---:|---:|---:|---:|
| `baseline` | **62591/68962** | 90.76% | +0 | 12 | 10 |
| `s20_mk2` | **64863/68962** | 94.06% | +2272 | 13 | 10 |
| `s28` | **63631/68962** | 92.27% | +1040 | 15 | 11 |
| `s28_mk2_f8` | **63989/68962** | 92.79% | +1398 | 24 | 12 |
| `k8` | **55878/68962** | 81.03% | -6713 | 12 | 10 |
| `s20_mk2_mK2` | **64326/68962** | 93.28% | +1735 | 12 | 10 |
| `mk6` | **63826/68962** | 92.55% | +1235 | 14 | 10 |
| `s20_f4` | **64566/68962** | 93.63% | +1975 | 16 | 12 |

Solved by **all 8 arms**: **53,439** (77.5% of complete).

### Joint subset (solved by every arm) — fair cost compare

| arm | median nodes | mean nodes | median path | mean path |
|---|---:|---:|---:|---:|
| `baseline` | 11 | 50 | 9 | 14 |
| `s20_mk2` | 11 | 31 | 9 | 14 |
| `s28` | 12 | 43 | 10 | 15 |
| `s28_mk2_f8` | 17 | 51 | 10 | 16 |
| `k8` | 11 | 52 | 9 | 14 |
| `s20_mk2_mK2` | 11 | 30 | 9 | 14 |
| `mk6` | 11 | 42 | 9 | 14 |
| `s20_f4` | 12 | 42 | 10 | 16 |

### Paired vs `baseline` (McNemar discordants)

| arm | arm-only | base-only | both | Δ solves |
|---|---:|---:|---:|---:|
| `s20_mk2` | 2673 | 401 | 62190 | **+2272** |
| `s20_f4` | 2365 | 390 | 62201 | **+1975** |
| `s20_mk2_mK2` | 2308 | 573 | 62018 | **+1735** |
| `s28_mk2_f8` | 2257 | 859 | 61732 | **+1398** |
| `mk6` | 1942 | 707 | 61884 | **+1235** |
| `s28` | 2004 | 964 | 61627 | **+1040** |
| `k8` | 1367 | 8080 | 54511 | **-6713** |

### Anytime (complete denominator)

| arm | 5 | 10 | 25 | 50 | 100 | 250 | 500 | 1,000 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `baseline` | 5059 | 26367 | 41023 | 46262 | 51879 | 56646 | 60372 | 62591 |
| `s20_mk2` | 5195 | 24737 | 42544 | 50112 | 55273 | 60674 | 62780 | 64863 |
| `s28` | 4721 | 23217 | 39942 | 47592 | 52970 | 59127 | 61445 | 63631 |
| `s28_mk2_f8` | 4921 | 18493 | 32533 | 39887 | 50724 | 58351 | 61802 | 63989 |
| `k8` | 4804 | 24875 | 38292 | 44205 | 46434 | 52010 | 54261 | 55878 |
| `s20_mk2_mK2` | 5195 | 25517 | 42826 | 50269 | 55146 | 59680 | 61738 | 64326 |
| `mk6` | 4807 | 25458 | 41895 | 47311 | 49649 | 57235 | 60162 | 63826 |
| `s20_f4` | 4909 | 21880 | 38341 | 46214 | 52351 | 59488 | 62001 | 64566 |

## Headline — budget 10,000 (4 arms: baseline + top prospects)

| arm | solved | rate | Δ vs baseline | median nodes (own) | median path |
|---|---:|---:|---:|---:|---:|
| `baseline` | **68412/69224** | 98.83% | +0 | 14 | 10 |
| `s20_mk2` | **68971/69224** | 99.63% | +559 | 14 | 11 |
| `s20_mk2_mK2` | **68725/69224** | 99.28% | +313 | 13 | 11 |
| `s20_f4` | **68498/69224** | 98.95% | +86 | 19 | 12 |

Solved by **all 4 arms**: **68,082**.

### Joint subset @10k

| arm | median nodes | mean nodes | median path | mean path |
|---|---:|---:|---:|---:|
| `baseline` | 14 | 300 | 10 | 22 |
| `s20_mk2` | 14 | 186 | 11 | 26 |
| `s20_mk2_mK2` | 13 | 223 | 10 | 25 |
| `s20_f4` | 19 | 200 | 12 | 26 |

### Paired vs `baseline` @10k

| arm | arm-only | base-only | both | Δ solves |
|---|---:|---:|---:|---:|
| `s20_mk2` | 591 | 32 | 68380 | **+559** |
| `s20_mk2_mK2` | 388 | 75 | 68337 | **+313** |
| `s20_f4` | 331 | 245 | 68167 | **+86** |

### Anytime @10k (includes >1k thresholds)

| arm | 5 | 10 | 25 | 50 | 100 | 250 | 500 | 1,000 | 2,500 | 5,000 | 10,000 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `baseline` | 5057 | 26353 | 41049 | 46300 | 51884 | 56721 | 60515 | 62759 | 65288 | 67831 | 68412 |
| `s20_mk2` | 5200 | 24760 | 42576 | 50156 | 55350 | 60821 | 62967 | 65062 | 67241 | 68607 | 68971 |
| `s20_mk2_mK2` | 5200 | 25539 | 42876 | 50291 | 55230 | 59829 | 61911 | 64522 | 66716 | 68089 | 68725 |
| `s20_f4` | 4927 | 21921 | 38399 | 46230 | 52416 | 59624 | 62184 | 64762 | 67088 | 68091 | 68498 |

## 1k → 10k lift (names in both complete sets, 4 shared arms)

Common presentations: **65,731**.

| arm | solved@1k | solved@10k | new solves in (1k,10k] | still unsolved@10k |
|---|---:|---:|---:|---:|
| `baseline` | 59571/65731 | 64961/65731 | **5390** | 770 |
| `s20_mk2` | 61762/65731 | 65486/65731 | **3724** | 245 |
| `s20_mk2_mK2` | 61245/65731 | 65254/65731 | **4009** | 477 |
| `s20_f4` | 61476/65731 | 65046/65731 | **3570** | 685 |

## Verdict

- **Most promising overall: `s20_mk2` (L+20S+2MK).** Wins total solves at both budgets (64863/68962 @1k, 68971/69224 @10k), best McNemar Δ vs baseline, and on the joint subset cuts **mean nodes** without inflating median path.
- **Runner-up: `s20_mk2_mK2`.** Close at 1k, still #2 at 10k, but weaker residual coverage (more left unsolved @10k).
- **`s20_f4`:** strong @1k, collapses toward baseline @10k, longer paths — not the scale pick.
- **`s28_mk2_f8`:** slow-start + longer certificates; dominated by `s20_mk2`.
- **`k8`:** strictly below length baseline. Dead.
- Joint path lengths for `baseline`/`s20_mk2`/`s20_mk2_mK2` are nearly identical (median ~9–11); the win is nodes-to-solve, not shorter paths.

## Graphs

- Anytime 1k: `anytime_b1000.png`
- Anytime 10k: `anytime_b10000.png`
- Nodes / path — own solved & all-solved: `nodes_*`, `path_*`.


## Next: hard residual @ 100k

See [`HARD_RESIDUAL_100k.md`](HARD_RESIDUAL_100k.md) — **1183** presentations (union of any-arm failures @10k).
Colab: `experiments/heuristic_search/hsearch_colab_ac19_hard100k.ipynb`.
