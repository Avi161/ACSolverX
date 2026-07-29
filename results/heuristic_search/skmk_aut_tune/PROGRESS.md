# Aut-disjoint S+K+MK tune — progress

Updated `2026-07-29T18:10:54.073559+00:00`

- Engine: numba `greedy_search_hcompact` + HIGH_SPEEDUP 4-worker fork pool (~10 cells/s)
- Train cells: **15654 / 40320** (38.8%)
- Remain ≈ 24666 → ETA ~41 min
- Split: Aut-disjoint 120/60; **no xyimb**

## Interim (46/120 complete train idxs — not for selection yet)

| family | best so far |
|---|---|
| length | 0/46 |
| pure S | S12 → 16/46 |
| S+MK | S20_K0_MK10 → 19/46 |
| S+K+MK | S24_K1_MK8 → 19/46 |

Final ranking waits for full 120×336.
