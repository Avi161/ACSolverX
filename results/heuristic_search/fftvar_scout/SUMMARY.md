# fftvar scout — paired synthesis

Updated `2026-08-04T20:57:59.262017+00:00`

Entry point for [`RESULTS.md`](work/surf/ACSolverX/results/heuristic_search/fftvar_scout/RESULTS.md) (13 transforms, slice A), [`CONFIRM.md`](CONFIRM.md) (weight sweep + slice B) and [`SLICE_C.md`](SLICE_C.md) (pre-registered slice C).

## Why paired, not totals

| arm | slice A | slice B | slice C |
|---|---:|---:|---:|
| `length` | 0/20 | 0/20 | 0/20 |
| `lag345 @ wF=4` | 1/20 | 4/20 | 10/20 |
| `cplxlo @ wF=4` | 6/20 | 6/20 | — |
| `cplxlo @ wF=8` | 9/20 | — | 10/20 |
| `dftlo @ wF=4` | 7/20 | 2/20 | — |

The shipped `lag345` scores **1, 4 and 10 out of 20** on three disjoint slices of the same split at the same weight. Slice-to-slice variance swamps every between-arm gap, so a difference of totals at n=20 carries almost no information — which is exactly why slice A's 13-arm ranking put `dftlo` first and slice B then knocked it from 7/20 to 2/20. Pairing removes that variance: both arms see the same presentation, presentations neither solves drop out, and only the discordant pairs count.

## Paired comparisons (all three slices pooled)

| A vs B | n | both | only A | only B | exact p |
|---|---:|---:|---:|---:|---:|
| `lag345 @ wF=4` vs `cplxlo @ wF=4` | 40 | 5 | **0** | **7** | 0.0156 |
| `lag345 @ wF=4` vs `cplxlo @ wF=8` | 40 | 7 | **4** | **12** | 0.0768 |
| `lag345 @ wF=4` vs `dftlo @ wF=4` | 40 | 2 | **3** | **7** | 0.3438 |
| `length` vs `lag345 @ wF=4` | 60 | 0 | **0** | **15** | 0.0001 |
| `length` vs `cplxlo @ wF=4` | 40 | 0 | **0** | **12** | 0.0005 |

`only A` / `only B` are the discordant pairs; `p` is the exact two-sided sign test on them. A zero in `only A` means B solved a **strict superset**.

### The headline comparison, split by slice

Pooling the selection slice into the significance test flatters it, so the same paired comparison is broken out. **Slice A selected `cplxlo`; slice B did not.**

| slice | role | n | both | only `lag345` | only `cplxlo` | exact p |
|---|---|---:|---:|---:|---:|---:|
| A | selection | 20 | 1 | **0** | **5** | 0.0625 |
| B | confirmation | 20 | 4 | **0** | **2** | 0.5000 |
| A+B | pooled | 40 | 5 | **0** | **7** | 0.0156 |

## Read

- **Direction is consistent, magnitude is not established.** Across 40 paired presentations `cplxlo` solves 7 that `lag345` misses and **0** the other way — it never loses a discordant pair on either slice. But the pooled p = 0.0156 leans on slice A, which is the slice `cplxlo` was *selected* on; the clean confirmation slice B is only 2-vs-0 (p = 0.50) and cannot carry the claim alone. Treat this as a promising direction with a clean sign, not a result.
- Matched weight is the control that matters, because the two features have similar spread on start states (std 0.32 for `cplxlo`, 0.36 for `lag345`), so `cplxlo` wins with slightly *less* effective push, not more. The win is the transform, not the scale.
- `cplxlo` is also one of the four variants **invariant under the x<->X relabel** — the documented wart of the shipped `lag345`, which scores two AC-identical states differently. It is the only *spectral* variant with that property.
- Raising the weight to 8 buys more solves in total but stops being a superset (4 presentations regress), so `wF` is a real knob and 4 is not obviously its best value.
- The `length` control is **0/60** across all three slices. Every spectral term beats it; that floor is the only thing here that n=20 measures reliably.

## What this does not show

- All of it is on `L + wF*F` — the *pure* spectral arm. It says nothing about whether `cplxlo` adds anything **on top of `S20_MK2`**, which is where the shipped heuristic lives and where the original Fourier term failed. The pure-F comparison is a transform ranking, not a promotion case.
- Budget 1,000, 60 train presentations, no holdout read. The decision run is the full train 120 and then both holdouts, on Colab.
- Both holdouts remain unspent by this work.
