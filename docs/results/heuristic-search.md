# Heuristic search — `S20_MK2` and how it was chosen

## The recommended ordering

```
priority(r1, r2) = L + 20·S + 2·MK        # lower pops first
```

`S20_MK2` is the recommended heap ordering for the greedy substitution search. It lives in
[`experiments/search/heuristics.py`](../../experiments/search/heuristics.py); the API, the
feature definitions, and the headline tables are in
[`experiments/search/HEURISTICS.md`](../../experiments/search/HEURISTICS.md) and are not
duplicated here. This file holds the provenance chain and the scales it was validated at.

## Selection

A 240-arm grid (|S| = 8 × |MK| = 6 × |F| = 5 weight settings) at budget 1,000, cap 48, on
the `ac1m_hard_aut` train slice of 120 presentations:

| arm | train 120 |
|---|---:|
| length control | 0/120 |
| `S20` | 49/120 |
| **`S20_MK2`** | **54/120** |
| `S28_MK2_F8` (grid maximum) | 57/120 |

## The two holdouts

The grid's arms were then scored on a *spent* holdout of 60 (rows other stages had touched)
and a **fresh, automorphism-disjoint holdout of 60** that no stage of selection ever read:

| arm | spent 60 | fresh 60 |
|---|---:|---:|
| length control | 0/60 | 0/60 |
| `S20` | 30/60 | **27/60** |
| **`S20_MK2`** | 33/60 | **27/60** |
| `S28_MK2_F8` | 28/60 | **22/60** |

Two honest readings. First, the grid's own top scorer collapsed on the fresh holdout —
taking the training maximum would have repeated the `RECOMMENDED` mistake (below). Second,
on the fresh holdout `S20` and `S20_MK2` **tie** at 27/60: the `MK` term's +5 on train and
+3 on the spent holdout did not demonstrably transfer. `S20_MK2` shipped on the strength of
the larger-scale screens below, where the `MK` term does separate.

## bench60 at budget 10,000

Rescored from the 1M-node runs by `solved_at` (a prefix property, so no new search):

| arm | solved | median nodes (40 jointly solved) |
|---|---:|---:|
| greedy (length) | 40/60 | 197 |
| **`s20_mk2`** | **52/60** | **86** |

Δ = +12, McNemar **12–0** — a strict superset; nothing the greedy solved was lost. Gains
concentrate in the hard bins: bin 6 4/6→6/6, bin 7 0/6→6/6, bin 8 0/6→2/6, bin 9 0/6→2/6.
**Cap caveat:** the `s20_mk2` runs used `mrl=48` against the frozen greedy column's
`mrl=24` — read the solve delta as primary, node ratios as indicative.

## The AC19 aut-min screen (~69k presentations)

The largest validation: one `Aut(F₂)`-minimal representative per orbit over
`data/AC19_extended.txt` (see [`benchmarks.md`](benchmarks.md#tier-2-the-ac19-aut-min-subset)).

| arm | @1k | @10k |
|---|---:|---:|
| baseline (length) | 62,591/68,962 = 90.76% | 68,412/69,224 = 98.83% |
| **`s20_mk2`** | **64,863 = 94.06%** (+2,272) | **68,971 = 99.63%** (+559) |

McNemar @10k: 591 arm-only vs 32 base-only. Of the seven sibling arms screened, `s20_mk2`
won outright; `k8` (knots alone) was **worse than length** by 6,713 solves — the knot term
is a light correction, not a signal on its own. On the hard-100k A/B over **70,723 Aut
orbits** at budget 100,000: length leaves 221 orbits unsolved, `s20_mk2` leaves **39** —
182 recovered, none lost.

## solved_1hop, stratified (432 Aut orbits × 5 arms)

All 2,160 runs complete, 2,020/2,020 solved certificates replayed:

| budget | baseline | `s20_mk2` |
|---|---:|---:|
| 1,000 | 304/432 | 334 |
| 10,000 | 363/432 | 392 |
| 100,000 | 389/432 | **416** |

The hard tail is where it matters: bin 8 (n = 47) at 100k goes **4/47 → 31/47**. Node
geo-mean ratio vs baseline on the 388 rows all arms solved: **0.671**.

## bench60 at 1M nodes

All treatment arms reach 60/60; the question becomes cost. `s20_mk2`'s node ratio vs the
frozen greedy: geo-mean **0.300**, median 0.342, faster on 53/60 rows. Path length is *not*
improved (mean 154.3 vs 142.6) — the win is node efficiency, not shorter certificates.

## Abelianized top-3 CoV selection

Ranking change-of-variables candidates by abelianized magnitude and searching only the
top 3 at budget 10,000 recovers the best-CoV oracle exactly: **52/60, 0 misses**
(length-ranked top-3: 49/60; random top-3: 48.5/60; plain greedy: 40/60). It does **not**
carry down to budget 1,000 — 43/60 there even with a second CoV hop. A budget-10k result,
labelled as one. (Source: PR #14's branch; see `BRANCH_MAP.md`.)

## Withdrawn: the former `RECOMMENDED`

`L + 2.53·K + 6.418·MK + 8.458·S + 3.292·xyimb` was withdrawn because its published
margins were in-sample: it was selected on a slice containing **14 of the 20 rows** it was
then validated against, and its 60-row campaign used subset-60 as its own row list. The
name and the weight map are both guarded against returning by
`tests/test_greedy_heuristic.py::test_module_ships_no_overfit_weight_vector`.

Two nuances the one-line version loses:

- The claim is "every number published *in this repo* for it was in-sample", not "it never
  generalised": the EXP-26 clean-null campaign later measured it at **50/75 vs length's
  20/75** on 75 presentations no stage of that program had read.
- The runs it produced are real and are kept as the record of what that campaign cost —
  the `heur_*` columns of the arms tables, relabelled with their provenance. The
  recommendation was withdrawn, not the data.

## Where the raw runs live

All on `origin/cursor/heur-u124-s20mk2-a42e` (and its ancestor `heur-12h-anti-overfit`):
`results/heuristic_search/smk_f_grid/` (grid + holdouts + bench60 rescore),
`ac19_autmin_screen/SUMMARY.md`, `hsearch_solved1hop_100k/RESULTS.md`,
`hsearch_bench60_1m/RESULTS.md`, `runs/EXP*.md`. Retrieval commands in
[`../BRANCH_MAP.md`](../BRANCH_MAP.md).
