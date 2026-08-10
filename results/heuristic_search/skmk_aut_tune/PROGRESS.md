# Aut-disjoint S+K+MK tune — progress

Updated `2026-07-29T18:19:12.178105+00:00`

- Engine: numba hcompact + HIGH_SPEEDUP 4-worker fork pool (~10 cells/s)
- Train cells: **21489 / 40320** (53.3%)
- **Baseline:** every arm compared to length-only greedy (`arm=length`)

## Interim vs length baseline (63/120 complete train idxs)

| arm | solved | Δ vs length |
|---|---:|---:|
| `length` | 0/63 | +0 |
| `S20_K0_MK10` | 26/63 | +26 |
| `S24_K0_MK2` | 26/63 | +26 |
| `S24_K0_MK4` | 26/63 | +26 |
| `S24_K0_MK10` | 26/63 | +26 |
| `S24_K1_MK8` | 26/63 | +26 |
| `S24_K1_MK10` | 26/63 | +26 |
| `S8_K0_MK8` | 25/63 | +25 |
| `S8_K0_MK10` | 25/63 | +25 |

Length ≈0 here by construction (pool = length-failures @1k). Production
verdict needs the same Δ at Colab budget 200k where baseline can move.
