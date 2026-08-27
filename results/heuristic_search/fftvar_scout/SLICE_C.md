# Slice C — pre-registered read of the complex-ring transform

Updated `2026-08-04T20:53:18.665770+00:00`

Arms frozen before the run; slice C read once. Selection provenance is in [`RESULTS.md`](work/surf/ACSolverX/results/heuristic_search/fftvar_scout/RESULTS.md) (transform) and [`CONFIRM.md`](CONFIRM.md) (weight + replication).

Budget 1000, cap 48. **Slice C** = ac1m_hard_aut train rows 40-59, disjoint from A (0-19) and B (20-39). Wall 0.3 min.

## Slice C

| arm | score | solved | mean nodes | mean min-relator |
|---|---|---:|---:|---:|
| `length` | `L` | **0/20** | — | 16.3 |
| `lag345_w4` | `L + 4*F_lag345` | **10/20** | 599 | 9.5 |
| `cplxlo_w8` | `L + 8*F_cplxlo` | **10/20** | 427 | 9.3 |

## All three train slices, arms common to all

| arm | A (0-19) | B (20-39) | C (40-59) | pooled |
|---|---:|---:|---:|---:|
| `length` | 0/20 | 0/20 | 0/20 | **0/60** |
| `lag345 @ wF=4` | 1/20 | 4/20 | 10/20 | **15/60** |
| `cplxlo @ wF=4` | 6/20 | 6/20 | not run | **12/40** |
| `cplxlo @ wF=8` | 9/20 | not run | 10/20 | **19/40** |

Pooling is honest only for `length` and `lag345 @ wF=4`, which were fixed before any slice was read. `cplxlo` rows mix a selection slice with a confirmation slice and are shown for size, not as an unbiased estimate.

## Notes

- 60 presentations at budget 1,000 is still a scout. The decision read is the full train 120 plus a holdout, on Colab.
- Both holdouts (`splits_ac1m_hard_aut` holdout 60, `splits_fft_fresh_holdout60`) remain unspent by this work.
- Unsolved = unsolved within budget 1,000.
