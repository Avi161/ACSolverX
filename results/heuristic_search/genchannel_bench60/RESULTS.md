# Generator channel on subset-60 — `L + wF*F`, budget 1,000

Updated `2026-08-04T21:30:24.516537+00:00`

Generator ring: **x, X -> +1 ; y, Y -> -1**, exponent never read. Motivated by `r -> r^-1` being an AC symmetry, so inversion carries no invariant information.

**Pool** subset-60, MRL **24**, budget 1000. **Control gate passed**: `wF=0` reproduces `greedy_search` pop for pop on all 60, and `length` scores 29/60 — the documented baseline. Wall 8.0 min.

> **No holdout.** subset-60 is the benchmark. The whole weight curve is below rather than only its best cell, because choosing a weight on the same 60 that score it is selection. Also, 60 rows are only **45 Aut(F2) orbits**, so an orbit column is reported alongside the row count.

## Does the Parseval argument actually cover this channel?

| variant | R² vs 17 feats | R² vs {L, K, xyimb} | mean | std |
|---|---:|---:|---:|---:|
| **`genlo`** | 0.730 | 0.449 | 1.336 | 0.404 |
| **`genhi`** | 0.770 | 0.636 | 1.325 | 0.294 |
| **`genpeak`** | 0.746 | 0.642 | 0.601 | 0.165 |
| **`gencent`** | 0.858 | 0.723 | 1.277 | 0.168 |
| **`genflat`** | 0.818 | 0.233 | 1.199 | 0.211 |
| **`genlag345`** | 0.715 | 0.489 | 0.744 | 0.179 |
| `lag345` | 0.445 | 0.134 | 0.574 | 0.261 |
| `cplxlo` | 0.560 | 0.191 | 1.859 | 0.187 |
| `dftlo` | 0.488 | 0.181 | 1.854 | 0.194 |

The identities `A_gen[1] = L - 4K` and `P_gen[0] = (L*xyimb)²` predict that the **{L, K, xyimb}** column alone should explain a generator-channel variant. Where it does not, that variant was never covered by the argument that set the channel aside.

## Weight curve — solved / 60

| variant | channel | wF=0.5 | wF=1 | wF=2 | wF=4 | wF=8 | wF=16 | best | @ wF | orbits |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **`genlo`** | generator | 31 | 32 | 32 | 31 | 19 | 14 | **32** | 1 | 32 |
| `cplxlo` | complex | 29 | 29 | 29 | 31 | 30 | 13 | **31** | 4 | 31 |
| **`genhi`** | generator | 29 | 30 | 29 | 25 | 19 | 11 | **30** | 1 | 30 |
| **`genflat`** | generator | 30 | 30 | 30 | 30 | 29 | 12 | **30** | 0.5 ⚠ | 30 |
| **`genpeak`** | generator | 29 | 29 | 29 | 29 | 22 | 17 | **29** | 0.5 ⚠ | 29 |
| `dftlo` | sign | 29 | 29 | 29 | 27 | 21 | 8 | **29** | 0.5 ⚠ | 29 |
| `lag345` | sign | 28 | 28 | 28 | 26 | 25 | 21 | **28** | 0.5 ⚠ | 28 |
| **`genlag345`** | generator | 28 | 28 | 28 | 28 | 17 | 19 | **28** | 0.5 ⚠ | 28 |
| **`gencent`** | generator | 28 | 28 | 28 | 28 | 26 | 17 | **28** | 0.5 ⚠ | 28 |
| `length` (control) | — | 29 | 29 | 29 | 29 | 29 | 29 | **29** | — | 29 |

⚠ marks a best cell sitting on the **low edge** of the grid — the optimum may be outside it, so that arm's score is a lower bound, not a peak.

## Best generator arm vs the incumbents, per difficulty bin

| arm | bin 0 | bin 1 | bin 2 | bin 3 | bin 4 | bin 5 | bin 6 | bin 7 | bin 8 | bin 9 | total | mean nodes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `length` | 6 | 6 | 6 | 6 | 5 | 0 | 0 | 0 | 0 | 0 | **29/60** | 176 |
| `genlo @ wF=1` | 6 | 6 | 6 | 6 | 6 | 2 | 0 | 0 | 0 | 0 | **32/60** | 182 |
| `cplxlo @ wF=4` | 6 | 6 | 6 | 6 | 5 | 2 | 0 | 0 | 0 | 0 | **31/60** | 209 |

Each bin holds 6 presentations, bin 0 easiest, and each bin is 3.37x the nodes of the one below.

## Paired against the control

| arm | solves control misses | control solves it misses |
|---|---:|---:|
| `genlo @ wF=1` | 3 | 0 |
| `cplxlo @ wF=4` | 2 | 0 |

## Notes

- Every generator-channel variant is exactly invariant under the x<->X relabel by construction — it cannot read the exponent — so the shipped `lag345`'s documented relabel wart cannot arise here at all.
- `length` is flat across the weight columns by definition (`wF` multiplies nothing); it is repeated so the row reads against the others.
- Unsolved = unsolved within budget 1,000.
