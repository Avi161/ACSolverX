# Campaign 12h RESULTS — anti-overfit heuristic evaluation

Updated: `2026-07-29T07:19:01.568831+00:00` · branch `cursor/heur-12h-anti-overfit-a42e`

## Advisor gate

`ac-advisor` **BLOCK**ed fitting on the CoV/automorphic unsolved-descended pool. Evaluation-only on never-read AC1M (Aut-expanded AC19 family; row≠independent problem). Budget 1000, cap 48.

## Screen (length-only)

- Screened: **24173** (easy/mid/hard = 15437/4517/4219)
- Solve rate @1000: **19954/24173**

## Hard recoveries (590 complete)

| arm | recovered |
|---|---:|
| `length` | **0/590** |
| `recommended` | **119/590** |
| `mk8` | **87/590** |
| `k8` | **50/590** |
| `kms5` | **105/590** |
| `s24` | **204/590** |

## Mid speed (1372 complete)

| arm | solved | mean nodes |
|---|---:|---:|
| `length` | 1372/1372 | 157.0 |
| `recommended` | 1344/1372 | 236.4 |
| `mk8` | 1288/1372 | 300.5 |
| `k8` | 798/1372 | 145.0 |
| `kms5` | 1353/1372 | 188.7 |
| `s24` | 1364/1372 | 122.3 |

## S-grid (select/holdout)

| w | select | holdout |
|---:|---:|---:|
| 4 | 66/396 | 61/404 |
| 8.458 | 146/396 | 143/404 |
| 12 | 170/396 | 148/404 |
| 16 | 161/396 | 147/404 |
| 20 | 160/396 | 153/404 |
| 24 | 146/396 | 145/404 |
| 32 | 135/396 | 128/404 |
| 40 | 133/396 | 127/404 |

## ms640 clean null

- `kms5`: 43/75
- `length`: 20/75
- `mk8`: 36/75
- `recommended`: 50/75

## Files

- `screen_length_ac1m.jsonl`, `arms_on_band.jsonl`, `arms_hard_full.jsonl`, `s_grid_hard.jsonl`, `aut_disjoint_null.jsonl`

