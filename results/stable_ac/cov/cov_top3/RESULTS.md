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

**The canonical form belongs as a dedup, not as a third sort key.** Two candidates that differ only by a cyclic rotation of a relator are the *same state* to the solver, which Booth-canonicalises: across both arms, **all 605** within-presentation groups of Booth-canonically identical picks returned bit-identical `(solved, nodes_explored, path_length)` — 407 groups on `abel`, 198 on `len`, none dissenting. As a sort key the canonical form cannot help — equal keys sort adjacent, so both rotations still enter the top 3. As a dedup applied before the top 3 is taken, it recovers a wasted search on the **407/640** presentations (`abel`; 198/640 for `len`) whose shipped top 3 contains such a pair. The shipped arms show the same asymmetry, though the figures first published here for it did not survive re-derivation and are corrected below. Exact `(r1, r2)` duplicates are already zero in both, which is why this only shows up under canonicalisation.

**Correction (2026-08-11) — the shipped arms' duplicate bill, re-derived.** The original sentence read "`len` spent 325,963 nodes on 126 searches that repeated a canonically identical earlier rank; abel spent 707 nodes on 38". Re-measuring it from `manifest_ms640_{rule}_top3.jsonl` against the shipped results jsonl (the two agree on the start pair for all 1,920 rows of each arm, so there is no data-source ambiguity) does not reproduce either count, and the accounting the numbers were taken under was never recorded. Under **census** (every duplicate search, whatever it cost) with each relator Booth-canonicalised in place: `len` **326,277 nodes on 158 searches**, abel **403,465 on 451**. Under census with the pair Booth-canonicalised as a sorted pair (`canonical_pair_nj`, which is what the solver actually keys on): `len` **440,122 on 218**, abel **517,870 on 553**. Under **deployed** billing — only ranks at or before the arm's first solve, which is what the rule would cost as a solver — `len` **200,000 nodes on 2 searches** and abel **0 on 0**, because every abel duplicate sits after that arm's first solve. The published `len` node figure is within 314 nodes of the order-sensitive census (326,277 vs 325,963) so that half is probably that measurement with a small filter; the abel figure of 707/38 matches none of the four and should not be cited. Quote a duplicate bill only with its accounting named — census and deployed differ by three orders of magnitude on the abel arm, and the choice between them is the whole claim.

**Correction, second pass (2026-08-11) — two more figures from the same unrecorded measurement.** The paragraph above this one originally read "all 150 within-presentation groups" and "the 112/640 presentations". Neither reproduces under any accounting, and both came from the same pass that produced the discarded 707/38. Re-derived with the repo's own `words.canon_pair`: the group count is **605** (407 `abel` + 198 `len`), and the presentation count is **407/640** on `abel` and **198/640** on `len`. Both errors were conservative — the true numbers make the case for deduping *stronger*, not weaker — and both are now corrected in place. The lesson generalises past this file: when one number from a measurement fails to reproduce, re-derive its neighbours rather than only the number that was challenged.

**Relabels, not just rotations.** Booth dedup catches two candidates that differ by a cyclic rotation. It does not catch the larger class: two candidates that are the same presentation *renamed*, under one of the 8 signed permutations of `{x, y}`. Measured with the repo's own `words.relabel_key` (cross-checked against its numba twin `autcanon_fast.relabel_min`, identical partitions), the abel arm's 1,920 picks contain **723 slots over 500 of 640 presentations** whose relabel class repeats an earlier pick, and `len` contains **424 over 343** — against 553 and 218 for Booth alone. Whether those slots are waste depends on the budget, and not in the way theory suggests: a relabel is an automorphism, so it maps AC paths to AC paths bijectively and both the existence of a solution and its **minimal** length are relabel-invariant — but "minimal" is the true minimal AC length, which the greedy never computes; the `path_length` it reports is the depth one truncated best-first search happened to reach, and its tie-break reads strings, so siblings pop in different orders. Over the 169 abel sibling groups that are relabel-equivalent yet Booth-distinct, `nodes_explored` disagrees on 48 and `path_length` on 6 — while `solved` disagrees on **0 at every budget from 300 to 100,000, and on 1 at budget 100**. So at the production budget a sibling contributed nothing its partner had not, and the slot is free; at budget 100 that is no longer true. The `len` arm, never previously measured, is safer still: 204 sibling groups, 104 node disagreements, 3 path disagreements, and **0 solved-disagreements at every budget including 100**. **Scope, stated explicitly:** this is a measured property of *these* high-ranked ms640 candidates, not a law — every one of them solves comfortably inside 100,000 nodes, so no sibling sits at the budget boundary where a tie-break difference could decide the outcome. Carrying this dedup to a set whose searches do sit at that boundary — the 261 unsolved reps, AK(3) — requires re-running the measurement there rather than inheriting this result. This is not in tension with the separate finding that relabels supply 14 of 17 unsolved→solved flips as *alternative starts* at low budget, and the reason is structural rather than a judgement call about portfolios. `AUTOMORPHISMS_COV.md` classifies a row as a "relabel" by `aut_canon_cov == aut_canon_orig` — equality of the **full `Aut(F₂)` orbit** — while this dedup keys on `words.relabel_key`, the **8 signed permutations only**, a tiny subgroup of it. Two candidates lying in the same Aut-orbit but in different signed-permutation classes are therefore *both kept*. The 14-of-17 flips are untouched by this filter **by construction**, not by a decision to tolerate them. (The portfolio-vs-top-3 distinction is also true, but it is the weaker argument and should not be the one carrying the claim.)

**What the candidate pool actually is, by symmetry (2026-08-11).** Every one of the 6,177 subset-60 candidates is related to its original in one of exactly three ways, and the deck now carries the census: **512 (8%)** are *just a relabel* — one of the 8 signed permutations of `{x, y}`; **4,863 (79%)** are an automorphism of `F₂` that is **not** a relabel — the same `Aut(F₂)` orbit, a different string; **802 (13%)** are **not an automorphism** of the original at all, a different orbit. Priced per presentation against that row's own untransformed control (median over the 29 rows where both solve, flips counted on the 31 where the control fails): a relabel is worth **1.07× — nothing — and rescues 0**; the non-relabel automorphisms are worth **3.52×** and rescue **14**; the different orbits **2.25×** and **14**. They supply **45 of the 45** cheapest solving candidates and relabels supply **0**. That is the measurement the design rests on.

**And the pool-level dedup is mostly Booth, not the renames.** Comparing candidates to *each other* rather than to the original, keeping one representative per relabel class takes 6,177 → **1,616** (103 → 27 per presentation). But `relabel_key` runs `canon_pair` before it minimises over the 8 permutations, so it quotients by Booth canonicalisation first: **4,099 of the 4,561 dropped slots are a cyclic rotation or the two relators swapped** — already the same state to the solver — and the 8 renames remove **462 more** on top. Reporting the 4,561 as "renames" overstates them by ~9×. (It is also why a relabel class can hold more than 8 members, up to 21 here: the 8 bounds distinct *canonical pairs*, not raw candidate rows, and exact `(r1, r2)` repeats within a presentation are 0.)

**Why the quotient must stay the 8 name changes and must never be widened to the orbit.** This is a design constraint, not a tuning choice, and it is worth stating with the number that enforces it. Measured on subset-60: of the 45 rows with a solving CoV, **0 of 45** best picks lie in the same signed-permutation class as the original — so the shipped dedup can never delete a winning start — while **32 of 45 lie in the same full `Aut(F₂)` orbit as the original**. Orbit-level dedup would therefore discard most of the winners. The candidate pool shows the same thing: 6,177 raw candidates fall to 1,616 (26%) under the 8 signed permutations, but to **489 (8%)** under full `Aut` canonicalisation — a 12.6× collapse to ~8 candidates per presentation, against the 3 the rule needs. (An earlier pass here printed 399 for that second figure; it reproduces under nothing — the per-presentation sum is 489 and the global distinct count is 353 — and 489 is the one comparable to the 1,616, both being per-presentation sums.) This is the whole point of the change of variables: the greedy reads *strings*, not orbits, so a start in the same orbit but a different string is a genuinely different search. Quotienting by the orbit would delete exactly what the method produces. Only the pure renames are safe to drop, and only because a rename is not a new coordinate system. The gate is `experiments/stable_ac/cov/run/cov_top3_relabel.py` — seven rules (`abel_rd`, `len_rd`, `abel_len_rd`, `abel_len_rd_s`, `len_rd_s`, `abel_len_rd_mk`, `len_rd_mk`), manifests built at zero search nodes, every one of the 640 presentations having at least 3 relabel-distinct candidates in every arm. What the freed slots buy cannot be read off *this* run for the same reason the Booth re-score above is a lower bound — the replacements were never searched here — but it can be read off the frozen subset-60 sweeps, which searched every candidate of every row.

**What the dedup is actually worth, priced (2026-08-11).** [`COV_RELABEL_B1K.md`](../../../comparison/COV_RELABEL_B1K.md) re-ranks those sweeps under all three base keys × {shipped, +dedup, +dedup+MK} at budget 1,000 and 10,000. The dedup is **paired-identical on every arm at both budgets** — 0 wins, 0 losses, and on the two abel arms the deployed node total does not move by a single node. Its one measured gain anywhere is `(total)` at budget 10,000, where top-3 goes 49→50 — invisible in the paired column, which scores only rows both arms solve. (`len`+dedup's mean first-solve rises 1,797.8→2,319.3 there; that is the denominator absorbing one expensive new solve, not a regression.)

**But read that null against the right denominator (2026-08-11).** "0 wins / 0 losses on 60 rows" reads as 60 measurements and is nothing of the kind. Two facts collapse it. **Every unsolved search burns the entire budget** — 0 of 6,177 unsolved searches stop short — and **the dedup never changes rank 1**, because it keeps the first-ranked member of each relabel class (verified end to end: rank 1 is identical on 640/640 presentations for `abel_rd` vs `abel` and for `len_rd` vs `len`). So the deployed bill can only move on a row whose rank 1 fails *and* whose ranks 2–3 the dedup rewrote. That is **3, 1 and 2 of 60 rows** on `(abel)`, `(abel, total)` and `(total)` at budget 1,000, and **0, 1 and 2** at 10,000. On `(abel)` at 10,000 the "does not move by a single node" result is therefore *mathematically forced* — no row could have moved — which is [control-with-no-dynamic-range](../../../../experiments/lessons/control-with-no-dynamic-range.md) inside the very document that cites it. The correct summary is 0 win / 0 loss over roughly **nine informative row-opportunities across all six arm-budget cells**, not over 360. Note also that the one cell with the most range (`(total)`, 2 rows) is exactly where the dedup won.

**The dedup is not inert; the metric is blind.** The same study now reports `promoted`, the count of rows whose top-3 *membership* the dedup actually rewrites: **51/60 on `(abel)`, 48/60 on `(abel, total)`, 37/60 on `(total)`**. So the dedup rewrites five-sixths of the top-3 lists and the bill still does not move, because the bill cannot see ranks 2–3 on all but a handful of rows. "Hygiene, not headroom" remains the right verdict — it makes *k* mean *k* distinct searches and removes 72–83 slots per arm that were re-searching a start under another name — but it is hygiene that changes most of the lists, not a filter that rarely fires.

**`MK` changes sign with the budget, so subset-60 cannot decide it.** As the last key before the name tie-break, `MK` (max knots over the two relators) helps `(abel)` at budget 1,000 — 7/34/0 win/tie/loss, k=1 38→40, −2,250 nodes — and **hurts the same arm at 10,000**: 8/39/5, k=1 52→50, +28,457 nodes. On `(abel, total)` it helps at both (1/40/0 and 2/50/0, never losing a paired row); on `(total)` it wins nothing at either budget and loses one row at 1,000. A key whose sign depends on the budget on a 60-row set is the shape of [control-with-no-dynamic-range](../../../../experiments/lessons/control-with-no-dynamic-range.md) and [gap-metric-saturates](../../../../experiments/lessons/gap-metric-saturates-when-the-treatment-wins.md), not an established property.

**And the sign flip is not even the strongest objection — the firing asymmetry is.** `MK` rewrites the top-3 on **22 of 60** rows of `(abel)`, the arm where it costs 28,457 nodes and two rank-1 solves at budget 10,000; it rewrites only **3 of 60** rows of `(abel, total)`, the arm whose 1-and-2-row wins are the entire case for keeping it. So the arm where `MK` is measured to help is the arm where it barely does anything, and its two wins are drawn from three presentations on which the key has any effect at all. That is not a margin that a larger *budget* can settle; it needs more *rows*.

**Counts are not sets, so the writeup checks membership too.** A rule that leaves *k* unchanged can still be solving a different *k* rows, which would make any figure keyed on the shipped arm depict rows the text does not describe. `COV_RELABEL_B1K.md` now carries the membership table for the recommended rule against the shipped `(abel)`: at budget 1,000 top-3 is **41 vs 41 and the same 41 presentations**, while rank 1 is 38→40 as a **strict superset** (gains 565 and 575, loses nothing); at 10,000 both *k* are 52 and identical. That last cell is the concrete argument for keeping the length term under `MK` — bare `(abel)` + `MK` drops rank 1 from 52 to 50 at that budget, and `(abel, total)` + `MK` does not lose a single row.

**Which of the five is worth 640 × 3 × 100,000 nodes (2026-08-11).** Not all of them, and one is a no-op that can be settled today at zero search. On the shipped 100,000-node runs **abel's rank 1 already solves 640/640** (`len`'s solves 633/640, failing on 425, 435, 573, 599, 601, 634, 635; its top-3 recovers 5 of those 7, reaching 638/640). Since the dedup provably preserves rank 1, and rank 1 already solves everything on the abel arm, **`abel_rd`'s solve count and its rank-1 deployed bill of 458,688 nodes are identical to shipped `abel` by construction** — running it buys census numbers and nothing else. It should not be queued. The solve ceiling is likewise already 640/640 for every abel-first arm, so on ms640 at this budget *no abel arm has any solve headroom at all*; only node cost can move. The arm with genuine dynamic range is **`len_rd` against shipped `len`**: 7 rank-1 failures to work with, and the dedup rewrites the top-3 on 5 of them. The `MK` question is answered by **`abel_len_rd_mk` against `abel_len_rd`**, which differ at rank 1 on 17 of 640 presentations — so that pair is powered on 17 rank-1 changes and a cost comparison, not on a solve count that is pinned at its ceiling. Calling the 640-row run "the powered test" without those qualifiers overstates it.

**The third term is `S`, not `MK` (2026-08-11).** The intended rule was always **abel → length → S**: `S` is the smaller mean block, the feature carrying the heaviest weight in the project's one sanctioned heuristic `L + 20·S + 2·MK`. An earlier pass here used `MK` in that slot; that was a substitution, not the design, and it is corrected. Both are now measured. On `(abel, total)` — the arm actually used — they are **indistinguishable**: at budget 10,000 both take k=1 from 51 to 52, and their deployed totals differ by 8 nodes on ~294,000 (`S` 294,036, `MK` 294,028); at 1,000 both are within a handful of nodes of adding nothing. On the **length** arm `S` is clearly the better of the two: −171 nodes at budget 1,000 and −6,395 with **top-3 +2** at 10,000, against `MK`'s +1,000 and −2,125 with top-3 +1. `S` also fires about twice as often (6/60 rows vs 3/60). So `S` is the rule on both design grounds and measurement; `MK` is retained in `RULES` only so the comparison stays reproducible, never as the recommendation.

The recommended rule is therefore `(abel, total transformed length)` for ranking, **relabel dedup of the candidate list before the top k** (which subsumes the Booth dedup — the 8 signed permutations include the identity, so a Booth repeat is a relabel repeat), **`S` at the last slot**, canonical-lex last for determinism. Two cautions carry over: the re-score above only reorders picks that were already searched, so it is a lower bound and not an evaluation of the full rule; and each added term is another variable, which is why `abel_rd` and `len_rd` exist — they change the shipped arms in exactly one way, so a difference against the frozen runs is attributable.

**All 640 at budget 1,000, every rank searched (2026-08-11).** Four fresh runs — `abel`, `abel → length → S`, `len`, `length → S` — over every ms640 presentation at `node_budget = 1,000`, with all three ranks searched on every row even when rank 1 solves, so a presentation costs at most 3,000 nodes. All 7,680 rows verify (`verify_results`: 6,820 solved certificates, 0 budget-invariance violations). The plain-greedy control is the **same baseline truncated to 1,000 nodes**, not its own 1,000,000-node run: a search at *B* is the first *B* pops of a longer one, so truncation gives the exact budget-1,000 control at zero new search — quoting the baseline's own 640/640 would compare against a 1,000× larger budget.

| arm | rank 1 | top 3 | deployed nodes | all-3-ranks nodes |
|---|---|---|---|---|
| plain greedy, truncated to 1,000 | — | 554 | 122,208 | 122,208 |
| `abel` (shipped) | 584 | 596 | 168,906 | 249,413 |
| **`abel → length → S`** | **590** | 596 | **161,629** | 333,815 |
| `len` (shipped) | 573 | 587 | 215,176 | 315,088 |
| `length → S` | 572 | **588** | 213,206 | 331,050 |

This is the dynamic range subset-60 could not supply, where `S` moved 6 nodes and nothing else because almost no row had headroom. **`S` earns its slot at rank 1 and only there**: 584 → 590 solves and 7,277 fewer deployed nodes on the abel arm, and one extra top-3 row on the length arm (587 → 588). Top-3 on the abel arm is 596 either way — and the *same* 596 presentations, not merely the same count — so what `S` buys is a better first pick, not a better list. **Priced as the run was actually executed it is the dearer arm**: 249,413 → 333,815 nodes, because the picks it promotes into slots 2 and 3 solve markedly worse (580/580 → 524/543 by rank). The mechanism is [diversity-only-pays-at-full-depth](../../../../experiments/lessons/diversity-only-pays-at-full-depth.md) seen from the other side — the name tie-break fills those slots with unlike starts, `S` with near-copies of the rank-1 pick — so the two accountings must be reported as separate columns, per [price-the-untransformed-route](../../../../experiments/lessons/price-the-untransformed-route.md). **`k = 2` reaches the top-3 count on all four arms**, so the third search buys nothing *at this budget*; that does not transfer to 100,000, where abel's rank 1 already solves 640/640.

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
