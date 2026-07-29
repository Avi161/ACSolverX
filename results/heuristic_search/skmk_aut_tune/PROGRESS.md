# Aut-disjoint S+K+MK tune — progress

Updated `2026-07-29T17:53:27.130604+00:00`

## Status

- **Engine:** `greedy_search_hcompact` (numba) + **HIGH_SPEEDUP** `ProcessPoolExecutor`
  (`fork`, `workers=4` = all CPUs), parent-only jsonl writes, resume-safe.
- **Split:** [`splits_ac1m_hard_aut.json`](../splits/splits_ac1m_hard_aut.json)
  train=120 / holdout=60 Aut-orbits, zero Aut overlap; prior scout orbits excluded.
- **Grid:** 336 arms (S×K×MK, **no xyimb**) × 120 train = **40,320** cells @ budget 1,000 / cap 48.
- **Done:** **5127 / 40,320** train cells (12.7%).
- **Throughput:** ~11–15 cells/s after JIT warm (was ~2.8/s serial before parallel resume).
- **ETA:** ~40–60 min for remaining train; then shortlist holdout (~40–50 arms × 60).

## What this is / is not

- **Is:** proper Aut-disjoint select-on-train / one-read-on-holdout weight tune for Colab arms.
- **Is not:** the contaminated `skmk_tune/` / `skmk_mix/` prefix-of-fresh_hard runs (Aut leakage risk).

## Next

1. Finish train ranking → family winners (pure S, S+K, S+MK, S+K+MK, …).
2. Holdout one-read on shortlist.
3. Restamp Colab `hsearch_colab_5x51_c{1..5}` with baseline + winners (**no recommended/xyimb**).
