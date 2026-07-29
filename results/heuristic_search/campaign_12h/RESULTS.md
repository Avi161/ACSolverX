# Campaign 12h — anti-overfit heuristic evaluation

Updated: `2026-07-29T02:31:21.126851+00:00` · wall end `2026-07-29T14:01:44+00:00` · remaining `11.51 h`

Advisor **BLOCK**ed fitting on the CoV/automorphic unsolved-descended pool; this run is **evaluation-only** on never-read AC1M (+ ms640 clean null), budget 1000, cap 48. Negatives mean unsolved within budget 1000.

## Screen (length-only denominator)

- Screened rows: **6500**
- Easy (solved <100 nodes): 4166
- Mid (solved 100–999 nodes): 1236
- Hard (unsolved at 1000): 1098

- Solve rate @1000: **5402/6500** (83.1%)

## Go / no-go (dynamic range)

Mid-band size (length-only solved in [100,1000)): **1236**.

**GO for evaluation** — mid-band large enough to compare pre-registered arms (still no fitting).

## Pre-registered arms on mid-band

| arm | solved | n | mean nodes (solved) |
|---|---:|---:|---:|
| `length` | **635/635** | 635 | 198.2 |
| `recommended` | **619/635** | 635 | 288.2 |
| `mk8` | **580/635** | 635 | 361.2 |
| `k8` | **332/635** | 635 | 173.0 |
| `kms5` | **622/635** | 635 | 228.8 |
| `s24` | **628/635** | 635 | 149.5 |

## Matched mid-band: vs length-only

- `recommended` vs length: better 240 / worse 395 / same 0
- `mk8` vs length: better 178 / worse 457 / same 0
- `k8` vs length: better 231 / worse 403 / same 1
- `kms5` vs length: better 291 / worse 339 / same 5
- `s24` vs length: better 478 / worse 154 / same 3

## Method notes

- Denominator fixed by length-only screen before any other arm.
- AC1M rows excluding exact string pairs from ms640 / 1190MS / solved-aut / unsolved-124 tables.
- No unsolved ACA reps used for selection (there is no selection).
- See [`PLAN.md`](PLAN.md).

