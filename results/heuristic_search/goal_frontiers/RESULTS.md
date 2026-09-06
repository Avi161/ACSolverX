# 60/60 with certified short-relator lookahead

The fixed rewrite/search hybrid solves **60/60** at both 1,000 and 10,000
charged steps per presentation. Its maximum is 404 steps on any row.
The fresh 10k comparison measures1.060101s total search wall time versus
greedy's40.565478s. On the exact 40 presentations both solve, the mean is
12.797500ms versus163.049177ms.

This meets the requested coverage, budget and speed target on subset 60.
It is an exploratory, in-sample benchmark result, not independent evidence
of generalization to arbitrary presentations.

## Fresh matched 10k results

| Method | Solved | Total charged nodes/pops | Total wall (s) | Total CPU (s) | Mean wall on 40 shared solves (ms) | Mean CPU on 40 shared solves (ms) |
|---|---:|---:|---:|---:|---:|---:|
| Greedy |40/60|248,227|40.565478|40.289806|163.049177|162.117775|
| Rewrite + S40 generator search + S20 fallback |60/60|6,286|1.060101|1.054007|12.797500|12.679675|

All 60 candidate paths and charged counts exactly match the prior 1k run.
All 60 greedy outcomes, pop counts and paths match the previous10k control.
Both independent substitution decoders verify every one of the 100 solved
records in the fresh matched run.

The fixed input list, alternate method order, single worker, thread limit 1,
source hashes, warmup, clocks and cooldowns are in `matched_10k/manifest.json`.
There is no timeout. Timers include normalization, rewrite construction,
failed attempts, fallback searches and path reconstruction. They exclude
warmup, explicit pre-search GC, certificate checking, output and cooldown.
Wall and CPU times are from one measured pass; no repeated-run uncertainty
or physical-core pinning is claimed.

## What the method actually does

First, apply deterministic length-decreasing Nielsen basis changes and
normalize over signed generator permutations. Recognize a short relator
of the form `b^-1 a b a^-2` and a companion with b-exponent sum±1.
Use the short relator to plan and execute explicit donor substitutions,
moving powers across b until the companion has one b. That companion then
eliminates b from the short relator, producing a generator; finish with it.
Every operation is an explicit replayable move.

If that branch does not solve, start L+40S with four generator-change moves
for at most 500 pops. S20_MK2 receives the unused remainder of the global
budget. On these 60 rows, **21 finish through rewriting and 39 through S40**;
none needs the S20 fallback.

No search decision uses IDs, Aut-class labels, prior results or saved paths.
The recognizer operates on the actual signed words. The final timing driver
reads previous paths solely to check unchanged output after the search.
See `CASCADE.md` for the algebra, full procedure and accounting.

## The important cap distinction

**This is not a cap 48 result.** Ordinary fallback search retains cap 48,
but the rewrite branch explicitly permits canonical relators up to 256.
The actual maximum in the certificates is 131. Three rewritten certificates
reach 67 and eight reach 131; those 11 exceed 48. Allowing these temporary
increases and pursuing the known reduction sequence are both parts of
the new method. The user authorized increasing the relator cap.

Budget counts include accepted basis-path transforms, every rewrite root
and elementary substitution, and every pop in every attempted fallback.
They sum to 6,286: 119 normalization steps, 2,724 rewrite charges, and 3,443
S40 pops. Extra candidate image evaluations used to select normalization
are separately counted and timed, as neighbor generation is in a search;
there is no hidden auxiliary AC search and no budget reset per component.

## The 1k filter and rejected approaches

The candidate first solved all four diagnostic rows at 1k, including two
from the formerly unsolved class, then all 60 at 1k before the 10k extension.
The full1k total was1.124607s wall, with the same 6,286 charges and 404 maximum.

Before this candidate, 14 beam/tie/normalization settings were screened at 1k
on 13 rows. None solved either remaining-class representative. The best
screen coverage was 9/13 for child normalization, with substantial scoring
overhead. Two fast pop-normalization variants received small 10k late-gain
checks: both solved the two class 97 test rows but neither class 106 row.
Those negative results remain in `screen1` and `late_probe`; they were not
relabelled as full-subset evaluations.

## Verification and reproduction

The rewrite and cascade passed 35 focused tests. Basis primitives and the
earlier frontier engine passed 22 focused tests separately. The final matched
run verifies word-level certificates and then independently replays every
substitution using the greedy-baseline decoder. Every basis image is checked
against literal word substitution. The complete results and source snapshots
are saved in `matched_10k`.

Run the matched comparison from the repository root into a fresh directory:

```sh
NUMBA_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 .venv/bin/python -m experiments.search.time_cascade --out results/heuristic_search/goal_frontiers/matched_repeat
```

The single-presentation API is `experiments.search.cascade_heuristics.search`.
This remains an experimental pipeline; production S20_MK2 is unchanged.

Evidence: `cascade_1k/{runs,summary,manifest}.json*`,
`matched_10k/{runs,summary,manifest}.json*`, `CASCADE.md`, `AUDIT.md` and
the retained source snapshots. The 1k snapshot precedes a tiny-budget guard
fix that cannot affect these rows; the final10k run confirms identical
paths and counts against it.
