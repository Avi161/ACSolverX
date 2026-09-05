# Inside the expansion kernel at campaign length (aca_47, 300,000 pops)

The operator's campaign-box measurement (REPORT.md section 7) put
`expand_and_score_nj` at 85.7% of a pop at 34% depth on a 10M row, with
331.7 candidates a pop at 49.5 symbols each. This splits that kernel into its
stages at the same length, on the lab box, by the replay method of
`PHASE_SPLIT.md` taken one level down.

    PYTHONPATH=. python3 experiments/heuristic_search/core/perf_lab/phase_split.py \
        --rows aca_47 --budget 300000 --reps 1 --cpu 2 --sub \
        --out experiments/heuristic_search/core/perf_lab/results/expand_split_aca47_300k.json

Box: 4 cores / 15 GB, Intel Xeon @ 2.10 GHz, 8 MiB L2 (4 instances), 260 MiB L3,
idle apart from this run, pinned to core 2. Engine and kernels at `a1d1be23`
(the build the campaign runs, `perf_lab/frozen2/`). Config `S20_MK2`, cap 64,
300,000 pops, one replay rep (the stage figures are single measurements, read
them as shares). Wall clock 24m07s: plain run 203.4 s (1,475 pops/s), recording
run 203.9 s, outer replay, then the sub-split 683.8 s. Peak ~2.5 GB.

## How the sub-split is measured

`expand_and_score_nj` is `expand_node_topk_nj` -- pass 1 (for every `(k1, k2)`
the seam test, then the seam-reduced length for the pairs whose seam cancels,
then the cap filter) and pass 2 (the raw child word by index, the free and
cyclic reduce into scratch, the canonical form by two Booth passes plus the
inverse plus the lexicographic pick, the pair order-normalisation, the code
encoding) -- followed by the blob assembly and the feature/score loop. Six
kernels (`phase_split.py`, section 2b) are that pipeline cut off after one
more stage each, their code copied verbatim from the live kernels with the
helpers imported, each consuming its last stage's output in a checksum. Each
is replayed over the recorded 300,000 pops exactly like `replay_expand`; a
stage's cost is the difference between successive cuts, and the last cut IS
the full kernel, so the stages sum to the expand phase by construction (the
x_full cut came out at 484.4 us against `replay_expand`'s 481.2 us, 0.7%
apart). The caveat is inherent to differencing: every cut is compiled on its
own, so a stage carries whatever LLVM does differently with a truncated
pipeline; read the stages as shares.

## The split

Outer phases first (same method as PHASE_SPLIT.md), so the stages can be read
as shares of the pop:

| phase | us / pop | share of pop |
|---|---|---|
| expand | 481.2 | 71.0% |
| la-scan | 4.6 | 0.7% |
| hash | 10.3 | 1.5% |
| probe | 86.8 | 12.8% |
| pack | 9.0 | 1.3% |
| heap sifts | 8.6 | 1.3% |
| residual | 77.5 | 11.4% |
| **total** | **677.9** | 100% |

Inside expand:

| stage | us / pop | share of expand | share of pop |
|---|---|---|---|
| (c) pass-1 filter: seam test on 1,085 pairs + seam-reduced length on 332 | 14.3 | 3.0% | 2.1% |
| (a) raw child word + free/cyclic reduce | 67.1 | 13.9% | 9.9% |
| (b) canonicalise: two Booth passes, the inverse, the lex pick (+ the two hoisted per-pop canonicals) | 302.9 | 63.0% | 44.7% |
| (b') pair order-normalise + encode to codes + output arrays | 27.1 | 5.6% | 4.0% |
| (e) blob assembly (offs, klens, tots, key bytes with separators) and the other per-pop arrays | 23.6 | 4.9% | 3.5% |
| (d) features (`_feats_nj`) + segment pick + weighted sum | 49.4 | 10.3% | 7.3% |
| **sum (= the x_full cut)** | **484.4** | 100.7% | 71.5% |

Cumulative cut times, us/pop: pass1 14.3, +gen 81.4, +canon 384.3,
+child (= `expand_node_topk_nj`) 411.4, +blob 435.0, +full
(= `expand_and_score_nj`) 484.4.

## Candidates, before and after the filters, and what becomes of them

| quantity | per pop | note |
|---|---|---|
| `(k1, k2)` pairs enumerated by pass 1 | 1,085.2 | 325,561,900 in all |
| pairs whose seam cancels (seam-reduced length computed) | 331.7 | 30.6% of the pairs |
| candidates after the cap filter (= children generated) | 331.7 | the cap filter removed NOTHING at this depth: popped pairs are 36.4 symbols, children 49.5, cap 64 |
| symbols per candidate | 49.5 | |
| candidates NEW (inserted) | 146.9 | miss rate 0.443 |
| candidates that duplicate a state from an earlier pop | 68.7 | 0.207 |
| candidates that duplicate a state first discovered in THIS pop | 116.1 | 0.350 |
| candidates flagged by the cut-shift criterion (below) | 162.1 | **0.489 of all candidates**; 48,639,570 flagged, 0 violations |
| states discovered at 300k pops | 44,077,944 | |

"Duplicate" totals 55.7% of candidates, of which the intra-pop share counted
by the recorder (a repeat of a state this pop discovered) is 35.0%; a repeat
of a candidate of this pop that was itself a global duplicate is counted
under the global 20.7%, which is why the cut-shift criterion can flag 48.9%
of candidates while the intra-pop line says 35.0%.

The cut-shift criterion (candidate change 4): in one (target, sign) block,
with `A = roll(r_i, k1)` and `B = roll(o, k2)`, the child of `(k1, k2)` for
`k1 >= 1` is the child of `(k1 - 1, k2 + 1 mod n_o)` whenever `A[0]` and
`B[-1]` are inverse, because the two raw words are conjugate
(`a . (A[:-1] B[1:]) . a^-1` against `A[:-1] B[1:]`) and the cyclically
reduced canonical form is a conjugacy-class invariant. `x_crit_check`
verified, for every one of the 48,639,570 flagged children of this run, that
the predecessor move exists earlier in the same pop's output and carries
identical `(la, lb, codes)`: 0 violations. The proof is in
`hexpand.py`'s docstring.

## What it says, and the order of work it fixes

1. **Canonicalisation is the pop.** Two Booth passes plus the inverse and the
   pick are 63.0% of the kernel and 44.7% of the pop at 49.5-symbol
   candidates. Nothing else in the kernel is above 14%.
2. **Half of the children are provably repeats of a child made earlier in
   the same pop**, and every one of them pays the whole of pass 2 (gen,
   reduce, canon, encode, blob, features) plus the engine's hash and probe
   before the table says "seen". 48.9% of candidates, 0 exceptions in
   99.5M. That is the largest single lever and it is exact by construction,
   so it goes first.
3. **Deferred scoring (candidate change 1) is under the bar.** Features and
   scoring are 7.3% of the pop; only the duplicate fraction of that is
   recoverable (55.7% before the cut-shift skip, about 29% after it, since
   the skip removes only duplicates), i.e. 2% to 4% of the pop. Below the
   10% threshold set for this campaign: skipped, and said so.
4. **The pass-1 filter (candidate change 3) is 2.1% of the pop**, not
   quadratic in any way that matters: 1,085 O(1) seam tests plus 332
   O(cancelled) seam lengths a pop. Below the threshold: skipped.
5. Word generation + reduce (9.9%), encode (4.0%) and blob (3.5%) are each
   under 10% and are left alone.

Order: the cut-shift skip (hcompact-only kernel, `hexpand.py`), then packed
canonicalisation on 2-bit words, each gated against `frozen2` and benched on
this row at 300k. The shared kernels in `greedy_baseline.py` / `hfast.py` are
not touched by either.
