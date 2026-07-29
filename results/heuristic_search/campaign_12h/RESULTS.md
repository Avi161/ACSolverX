# Campaign 12h — anti-overfit heuristic evaluation

Updated: `2026-07-29T12:45:10.832914+00:00` · wall end `2026-07-29T14:01:44+00:00` · remaining `1.28 h`

Advisor **BLOCK**ed fitting on the CoV/automorphic unsolved-descended pool; this run is **evaluation-only** on never-read AC1M (+ ms640 clean null), budget 1000, cap 48. Negatives mean unsolved within budget 1000.

## Screen (length-only denominator)

- Screened rows: **24173**
- Easy (solved <100 nodes): 15437
- Mid (solved 100–999 nodes): 4517
- Hard (unsolved at 1000): 4219

- Solve rate @1000: **19954/24173** (82.5%)

## Go / no-go (dynamic range)

Mid-band size (length-only solved in [100,1000)): **4517**.

**GO for evaluation** — mid-band large enough to compare pre-registered arms (still no fitting).

## Pre-registered arms on mid-band

| arm | solved | n | mean nodes (solved) |
|---|---:|---:|---:|
| `length` | **1372/1372** | 1372 | 157.0 |
| `recommended` | **1344/1372** | 1372 | 236.4 |
| `mk8` | **1288/1372** | 1372 | 300.5 |
| `k8` | **798/1372** | 1372 | 145.0 |
| `kms5` | **1353/1372** | 1372 | 188.7 |
| `s24` | **1364/1372** | 1372 | 122.3 |

## Matched mid-band: vs length-only

- `recommended` vs length: better 496 / worse 873 / same 3
- `mk8` vs length: better 344 / worse 1028 / same 0
- `k8` vs length: better 545 / worse 826 / same 1
- `kms5` vs length: better 585 / worse 779 / same 8
- `s24` vs length: better 1060 / worse 297 / same 15

## Method notes

- Denominator fixed by length-only screen before any other arm.
- AC1M rows excluding exact string pairs from ms640 / 1190MS / solved-aut / unsolved-124 tables.
- No unsolved ACA reps used for selection (there is no selection).
- See [`PLAN.md`](PLAN.md).

