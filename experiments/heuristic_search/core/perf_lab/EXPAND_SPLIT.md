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

## Results per step (each against `current` = frozen2 = a1d1be23)

Every step: `gates.py --oracle --twin --twin-rows 6 --twin-budget 30000
--widen-lines states --frozen2` (60 rows at 1,000 against the Python
oracle and the frozen engine; 6 rows at 30,000 bit-for-bit against the
frozen engine, every stored array, every decoded relator, the widen pops),
then `bench.py --rows aca_47 --budget 300000 --reps 1 --cpu 2 --engines
current,candidate`. The gates ran on core 0 while the decision bench ran on
core 2; the final bench below ran alone.

| step | what | gates (wall) | aca_47 300k pops/s current -> candidate | ratio | kept |
|---|---|---|---|---|---|
| 1 | cut-shift skip in pass 1 (`hexpand.expand_children_h`, emitted bitmap, Booth canon kept) | oracle PASS, twin PASS (482 s) | 1,439.9 -> 2,237.8 | **1.5541** | yes (a8a6b3a4) |
| 2 | + canonical form on 2-bit-packed words (`packed=True`) | oracle PASS, twin PASS (457 s) | 1,452.9 -> 3,401.5 | **2.3412** (step's own factor 1.506) | yes (f6f38a7d) |
| -- | deferred scoring (candidate change 1) | not run | -- | -- | skipped: 7.3% of the pop, 2% to 4% recoverable |
| -- | pass-1 filter rewrite (candidate change 3) | not run | -- | -- | skipped: 2.1% of the pop |

Record fingerprints agreed on every run; bytes/state 40.1 on both engines
at this budget (the kernels allocate per pop, not per state; the per-block
bitmap is at most n1 x n2 bytes a pop); peak RSS 3.15 GiB current, 3.17 to
3.18 GiB candidate on the 300k runs (the bench's RSS is dominated by the
reservation, which is identical). Bench wall: 393 s (step 1), 346 s
(step 2). A first version of step 1 that skipped on the bare criterion
without the emitted bitmap measured 1.5410 and also passed both gates
(490 s); it was replaced before commit by the bitmap version, which is
what is measured above.

## Final bench (box idle, core 2, `--engines current,candidate`)

`aca_47` at 300,000 pops, 1 rep (wall 346 s): current 1,462.6 -> candidate
3,385.0 pops/s, **ratio 2.3144**; peak RSS 3.156 -> 3.184 GiB; bytes/state
40.1 on both; record fingerprints agree.

The default six rows at 100,000 pops, 3 reps, engines alternating (wall
1,082 s for 36 measurements):

| row | median pops/s current -> candidate | candidate min .. max | ratio | peak RSS GiB | B/state |
|---|---|---|---|---|---|
| aca_0 | 2,889.0 -> 5,509.6 | 5,366.8 .. 5,932.6 | 1.9071 | 1.218 -> 1.221 | 44.4 -> 44.4 |
| aca_1 | 2,616.5 -> 5,470.0 | 5,348.6 .. 5,566.5 | 2.0906 | 1.218 -> 1.220 | 44.4 -> 44.4 |
| aca_3 | 3,638.9 -> 7,993.7 | 7,987.2 .. 7,995.0 | 2.1968 | 0.653 -> 0.656 | 44.4 -> 44.4 |
| aca_4 | 2,069.8 -> 4,402.9 | 4,304.6 .. 4,504.4 | 2.1272 | 1.218 -> 1.220 | 44.4 -> 44.4 |
| aca_5 | 1,999.9 -> 4,280.2 | 4,226.3 .. 4,298.3 | 2.1402 | 1.218 -> 1.219 | 44.4 -> 44.4 |
| aca_8 | 3,573.4 -> 8,182.8 | 8,137.3 .. 8,358.9 | 2.2899 | 0.637 -> 0.638 | 44.4 -> 44.4 |

Median ratio 2.1337, geometric mean 2.1220; record fingerprints agree on
every row and every rep (the two engines search identically). Against the
operator's bar of 1.1x at 300k on a real row: 2.31x on `aca_47` at 300k on
this box; the campaign box (Xeon 6975P) is where the per-lane number is to
be read, the shares in this document are what carry over.

## Full suite on the final tree (`f6f38a7d`)

`python -m pytest tests/ -q` after purging numba caches (core 0, wall
435 s): **281 passed, 11 failed**. Ten are the branch-name pins that fail
on this lab branch by construction (`test_leftovers_5m.py`:
`test_the_committed_notebook_is_what_the_generator_writes` x5 and
`test_the_branch_matches_the_branch_this_code_is_on`; `test_leftovers_1m.py`:
the same two names, parametrised `[greedy]` and `[s20_mk2]`, four
failures). The eleventh is
`tests/test_leftovers_5m.py::test_rerun_observes_a_tiny_row_end_to_end`,
which is this work's to explain: it runs `rerun_row.rerun` on `ac19_23156`
at a 2,000-pop budget with a 0.2 s RSS sampler and asserts at least one
live sample line in the CSV. The observer's loop blocks in
`proc.poll(timeout=1.0)` BEFORE its first sample; the 2,000-pop child now
finishes in 0.35 to 0.39 s of search (0.67 to 0.74 s of rerun, measured
three times from a script at `sample_secs` 0.2, 0.02 and 0.005: one CSV
line each time, `nodes_explored` 2,000), so by the time the loop samples,
the child has exited and `/proc/<pid>/status` returns nothing. On
`a1d1be23` the same search outlived the first poll. Every other assertion
of that test passes (record, node count, peak RSS, engine generation,
output naming). Not a search or memory regression; the fix belongs to the
harness (sample once right after the spawn, before the first poll, or give
the toy rerun a budget that outlives one second) and was not applied here
because no further code changes were to land on this branch.

## Ideas not implemented (each with the measurement that would decide it)

None of these is on the branch; they are written down so the next split
can order them. All are for `hexpand.py` (hcompact only); none touches the
shared kernels.

1. **The remaining intra-pop repeats.** 55.7% of candidates were repeats
   before step 1 and the cut-shift skip removes 48.9 points of that, so
   about 6.8% of the original candidates (about 13% of the survivors) are
   still repeats the engine's table has to find: chains that wrap through
   `k1 = 0` (the wrap member is emitted because its predecessor has
   `k1 = n_i - 1`, later in the order), and repeats across blocks or from
   periodic relators. Deciding measurement: re-run `phase_split.py --sub`
   with the recorder on the new engine and classify the survivors' repeats
   by mechanism (same block and a wrapped chain; other block; same move
   set). Only a class with an exact by-construction criterion is worth a
   step, and the ceiling is 13% of the survivors' per-child work.
2. **Deferred scoring** (candidate change 1): features + scoring were 7.3%
   of the pop before the steps; on the survivors the duplicate fraction is
   about 29%, so the recoverable part is 2% to 4% of the old pop and a
   larger share of the new, faster pop. Deciding measurement: the same
   `--sub` split on the new engine; take it only if (d) x duplicate
   fraction is at least 5% of the new pop. The engine-side code exists as
   a plan (score only survivors with `expand_and_score_nj`'s loop verbatim
   on the flat code buffer; `_feats_nj` already reads that layout).
3. **The probe on packed bytes.** With expansion at 2.3x, the probe
   (12.8% of the old pop) is now the second phase. `_codes_equal_row`
   decodes one 2-bit symbol per iteration; a candidate packed once into a
   scratch row could compare `(la + 3) // 4` bytes per region under
   `_region_cmp2`'s masks. Deciding measurement: the outer split's probe
   line on the new engine, and the per-candidate cost of the extra pack
   against the 1.23 slots a lookup visits.
4. **Word generation + reduce on packed words** (13.9% of the old kernel):
   the raw child word and the seam cascade could be built as packed
   windows of the doubled relators instead of symbol copies. Deciding
   measurement: stage (a) on the new engine; worth a step only if it is
   still above 10% of the pop.
5. **The pass-1 filter** (candidate change 3): 2.1% of the pop before the
   steps; even on the faster pop it stays under 10%. Not worth its gates
   unless a later split says otherwise.
