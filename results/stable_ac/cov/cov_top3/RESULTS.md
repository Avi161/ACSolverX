# Two CoV top-3 rules on all 640 ms640 presentations, budget 100,000 — results

Both arms finished. Method, gates and the design argument for running every rank: [`COV_TOP3_MS640.md`](../../../../experiments/stable_ac/cov/run/COV_TOP3_MS640.md). Files below are the production output; every number on this page is `summarize()` / `compare_rules()` reading them, nothing transcribed by hand.

| arm | file | rows |
|---|---|---|
| `abel` | `abeltop3_100000_640_subnc2pxysb_mrl24_cyc_ms640_08_10_26.jsonl` | 640 × 3 = 1,920 |
| `len` | `lentop3_100000_640_subnc2pxysb_mrl24_cyc_ms640_08_10_26.jsonl` | 640 × 3 = 1,920 |

**Certificates: all 3,813 solved rows of these two files verify, exit 0.** The repo-wide standing count is now `ALL 13649 SOLVED-ROW CERTIFICATES VERIFY (45633 rows across 14 files)`, budget-invariance 6,608 jobs at more than one budget, 0 violations.

## Headline

**Abelian mass solves all 640. It is the only arm that does, and it beats the node-matched control.**

| arm | solved | first-solve nodes (median / mean / total) | path (median / mean) |
|---|---:|---|---|
| **abel top-3** | **640 / 640** | **9 / 717 / 458,688** | **8 / 28.6** |
| `len` top-3 | 638 / 640 | 9 / 1,758 / 1,121,736 | 7 / 29.7 |
| plain greedy, one search @ 100,000 | 634 / 640 | — | — |
| plain greedy @ 300,000 (node-matched to 3 × 100,000) | 638 / 640 | — | — |
| plain greedy @ 1,000,000 (its own cost) | 640 / 640 | 11 / 4,963 / 3,176,297 | 9 / 36.8 |

Paired against plain greedy over all 640: **6.9× cheaper on the mean, 21× on the max** (26,963 against 574,959), cheaper on 511 presentations, tied on 49, dearer on 80. Paths are shorter on 511, tied on 85, longer on 44. Head-to-head on the 638 both rules solve, abel costs **694 nodes to `len`'s 1,758** — 2.5×.

The solve count was expected to have almost no room in it, and that is still the right reading of the middle of the dataset: the node-matched control already takes 638. The room was in **cost**, and it is where the result is.

## The six rows plain greedy cannot take at 100,000

This is the sharp end of the dataset. Abel's **rank-1** pick takes every one of them, for a fraction of what the untransformed route costs at the budget where it actually succeeds.

| pres | abel top-3, first solve | plain greedy, its own cost @ 1,000,000 | speedup | `len` top-3 |
|---|---:|---:|---:|---|
| 634 | 7,840 (r1) | 574,348 | **73×** | unsolved at 3 × 100,000 |
| 635 | 7,875 (r1) | 574,959 | **73×** | unsolved at 3 × 100,000 |
| 636 | 19,340 (r1) | 213,882 | 11× | 19,340 (r1) |
| 637 | 18,435 (r1) | 271,866 | 15× | 18,435 (r1) |
| 638 | 14,470 (r1) | 213,878 | 15× | 18,435 (r1) |
| 639 | 19,340 (r1) | 272,953 | 14× | 19,340 (r1) |

634 and 635 are the two rows the node-matched control cannot reach at all, and abel takes both for under 8,000 nodes. The method doc's earlier note that no CoV in the family solves 636–639 was a **budget-10,000** statement and is superseded here: all four solve at rank 1, in 14,470–19,340 nodes, which is exactly why a 10,000-node sweep could not see them.

## Cost, stratified

The pooled mean is tail-dominated, so it is reported by difficulty band — binned on plain greedy's *own* cost, so the bands are defined by the control and not by the treatment.

| plain greedy's cost | n | greedy median | abel median | greedy mean | abel mean | abel cheaper on |
|---|---:|---:|---:|---:|---:|---|
| < 10 nodes | 295 | 6 | **4** | 6 | 12 | 217 / 295 |
| 10 – 100 | 159 | 23 | **11** | 33 | 76 | 131 / 159 |
| 100 – 1,000 | 100 | 224 | **34** | 291 | 440 | 90 / 100 |
| 1,000 – 10,000 | 52 | 2,441 | **611** | 3,843 | **1,405** | 45 / 52 |
| ≥ 10,000 | 34 | 18,330 | **6,760** | 86,478 | **9,586** | 28 / 34 |

Abel's median wins in every band, and the mean crosses over exactly where it matters: 2.7× on the 1k–10k band and **9.0×** above 10,000. The three easy bands are the only place the mean favours greedy, and the absolute quantity there is negligible — abel is dearer on 80 presentations for **70,929 excess nodes in total**, median excess **4 nodes**, and 60 of the 80 cost under 100 extra nodes. One row (453: 204 → 26,963) is a third of that total.

## Does the ranking rule order the family? Only abel's does

This is what running every rank below a solve bought, and the two arms answer it in opposite directions.

| rank | abel solved | abel mean nodes | | `len` solved | `len` mean nodes |
|---|---:|---:|---|---:|---:|
| r1 | **640** | **717** | | 633 | 2,042 |
| r2 | 635 | 1,486 | | 635 | 1,609 |
| r3 | 633 | 1,769 | | 637 | 1,262 |

Abel is monotone in both columns — rank 1 solves the most and costs the least. **`len` is inverted**: its rank 3 solves more often *and* costs less than its rank 1. Shortest-transformed-pair is not merely a weaker key than abelian mass, it is anti-correlated with quality when used as the primary key. It is also why `len` needs its lower ranks at all — rank 1 alone is 633/640, *below* plain greedy's 634 at a single search, and only the union of three reaches 638.

For abel the same block says the opposite: rank 1 alone is already 640/640, so **the deployable policy is k = 1**. That costs 458,688 nodes against the census's 2,541,652 — the top-3 census is a measurement, not the method's price.

## What the census cost, and what it wasted

| arm | census nodes | core-hours | non-solving searches | nodes burnt by them |
|---|---:|---:|---:|---:|
| abel | 2,541,652 | 1.2 | 12 (5 at r2, 7 at r3) | 1,200,000 = **47%** |
| `len` | 3,143,988 | 1.2 | 15 (7 at r1, 5 at r2, 3 at r3) | 1,500,000 = **48%** |

Roughly half of each bill is a handful of searches that run to the full 100,000 and return nothing. The 1,908 (abel) and 1,905 (`len`) searches that do solve average **703** and **863** nodes.

## The ranking key: what the data says about the tie-break

Abelian mass is a **filter, not a ranking**. Over all 640 families it leaves a median of 5 candidates tied at its minimum and collapses to a single candidate on only 86/640, so on 462 of 640 presentations all three shipped picks carry the *same* abel value and the tie-break is doing the choosing.

Total transformed length is the right thing to break that tie with, and it is measured, not assumed:

- On the 431 abel-flat families whose picks differ in length and all solved, **a shortest pick was also a cheapest one on 398 (92%)** — 284 strictly, 114 tied — against roughly 33% by chance over three picks.
- Re-scoring the **already-searched** top 3 under `(abel, total length, lex)` costs **420,419 nodes instead of 458,688** — 8% cheaper, better on 81 presentations, worse on 27, tied on 532, at zero new search. A different pick is promoted to rank 1 on 289 of 640.
- Adding length as the second key raises the collapse-to-one rate from 86/640 to **378/640** and drops the surviving-candidate mean from 6.4 to 2.1. A third key still has to decide something on 262/640.

**The canonical form belongs as a dedup, not as a third sort key.** Two candidates that differ only by a cyclic rotation of a relator are the *same state* to the solver, which Booth-canonicalises: across both arms, all **150** within-presentation groups of Booth-canonically identical picks returned bit-identical `(solved, nodes_explored, path_length)`. As a sort key the canonical form cannot help — equal keys sort adjacent, so both rotations still enter the top 3. As a dedup applied before the top 3 is taken, it recovers a wasted search on the 112/640 presentations whose `(abel, length, lex)` top 3 contains such a pair. The shipped arms show the same asymmetry: `len` spent **325,963 nodes (10% of its census) on 126 searches that repeated a canonically identical earlier rank**; abel spent 707 nodes on 38. Exact `(r1, r2)` duplicates are already zero in both, which is why this only shows up under canonicalisation.

The recommended rule is therefore `(abel, total transformed length)` for ranking, **Booth-canonical dedup of the candidate list before the top k**, canonical-lex last for determinism. Two cautions before it is run as a third arm: the re-score above only reorders picks that were already searched, so it is a lower bound on the effect and not an evaluation of the full rule (the full rule pulls in candidates never searched); and the dedup is a second variable, so an abel-vs-new comparison that changes both cannot attribute the difference to either.

## Reproducing

```bash
# read-only: summarize() and verify_results run zero searches
ACSOLVERX_ALLOW_BIG=1 .venv/bin/python3 -c "
import experiments.stable_ac.cov.run.cov_top3_run as R
D='results/stable_ac/cov/cov_top3'
R.summarize(D+'/abeltop3_100000_640_subnc2pxysb_mrl24_cyc_ms640_08_10_26.jsonl', rule='abel', budget=100000)
R.summarize(D+'/lentop3_100000_640_subnc2pxysb_mrl24_cyc_ms640_08_10_26.jsonl',  rule='len',  budget=100000)
R.compare_rules(D+'/abeltop3_100000_640_subnc2pxysb_mrl24_cyc_ms640_08_10_26.jsonl',
                D+'/lentop3_100000_640_subnc2pxysb_mrl24_cyc_ms640_08_10_26.jsonl')"

.venv/bin/python3 -m experiments.stable_ac.verify_results results/stable_ac/cov/cov_top3
```

## Provenance note

The abel arm's 640 rank-1 rows carry `git_commit eec965fa` and its 1,280 rank-2/3 rows carry `ebf4d76f`. That is the all-ranks change landing mid-run and the resume filling in behind it: under the early-exit code rank 1 solved every presentation and the file stopped at 640 rows, and the restart added ranks 2 and 3 for all 640 without re-searching rank 1. It is `test_restart_fills_in_the_ranks_after_a_solve` holding in production — had `_finished` kept treating a solve as finishing a presentation, the file would have looked complete at 640 rows and the per-rank block above could never have been computed.
