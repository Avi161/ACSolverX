# Spectral-transform confirm — weight sweep + disjoint replication

Updated `2026-08-04T20:51:56.691469+00:00`

Tests the two ways [`RESULTS.md`](work/surf/ACSolverX/results/heuristic_search/fftvar_scout/RESULTS.md)'s ranking could be an illusion: a weight artifact (the variants have different spreads) and a slice artifact (the winner was chosen on slice A).

Budget 1000, cap 48. **Slice A** = ac1m_hard_aut train rows 0-19 (selection). **Slice B** = train rows 20-39, disjoint, arms frozen at wF=4. Holdouts untouched. Wall 2.1 min.

## 1. Weight sweep — slice A (selection)

| variant | wF=2 | wF=4 | wF=8 | best |
|---|---:|---:|---:|---:|
| **`lag345`** | 1/20 | 1/20 | 1/20 | 1 |
| `dftlo` | 4/20 | 7/20 | 2/20 | 7 |
| `cplxlo` | 4/20 | 6/20 | 9/20 | 9 |
| `dfthi` | 2/20 | 2/20 | 2/20 | 2 |
| `length` (control) | 0/20 | — | — | 0 |

## 2. Disjoint replication — slice B, wF=4, frozen

| variant | slice A | slice B | mean nodes (B) | mean min-relator (B) |
|---|---:|---:|---:|---:|
| `cplxlo` | 6/20 | **6/20** | 842 | 12.7 |
| **`lag345`** | 1/20 | **4/20** | 572 | 14.0 |
| `dftlo` | 7/20 | **2/20** | 684 | 15.2 |
| `dfthi` | 2/20 | **1/20** | 831 | 15.8 |
| `length` (control) | 0/20 | **0/20** | — | 16.5 |

## 3. Which presentations each arm solves (slice A, wF=4)

Pairing matters more than the counts at n=20: an arm that solves a strict superset is a different claim from one that trades solves.

| variant | solved idxs |
|---|---|
| `lag345` | 336077 |
| `dftlo` | 294623, 299840, 311026, 326724, 332599, 336077, 354031 |
| `cplxlo` | 299840, 311026, 326724, 332599, 336077, 354031 |
| `dfthi` | 299840, 336077 |

## Notes

- Slice B is read **once**, with arms frozen from slice A — no re-tuning.
- Both slices are train. Neither the spent nor the fresh holdout is touched, so the eventual Colab read is still clean.
- Unsolved = unsolved within budget 1,000.
