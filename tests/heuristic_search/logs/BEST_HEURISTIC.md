# The best heuristic — what to use, by node budget

The short answer, then the evidence and the caveats. Everything here is measured on the greedy substitution search with the heap ordering swapped; nothing else about the search changed, so every number is attributable to the ordering alone.

## Use this

**Order the heap by length plus a structural climb — one that values knots.** The one thing every result in this program agrees on is that a knot term in the heap key is what separates a search that crosses the two-hump barrier from one that does not.

The right denominator is **the 24 rows in difficulty bins 4–7** — the ones that are neither free (bins 0–3, which every ordering solves) nor out of reach (bins 8–9 and the reach rows, which nothing solves at ≤1000). That is where an ordering is actually tested.

| your node budget | the ordering to use | bins 4–7 (of 24) | full 66 | held-out bins 4–7 (leak-free) |
|---|---|---|---|---|
| **~500** | `while L>16: L + 8·knots − 6·xy-imbalance;  else: L` | **16** (baseline 2) | 40 | **5/7** (baseline 1/7) |
| **~1000 and above** | `L + 2.5·knots + 6.4·max-knots + 8.5·smaller-block + 3.3·xy-imbalance` — **no threshold needed** | **19** (baseline 5) | 43 | **7/7** (baseline 1/7) |

**The threshold is only needed for the lean ordering** (EXP-18). A climb carrying *only* a knot term must be switched back to pure length below 16, or it keeps chasing knots into the endgame where nothing structural is left to buy — that is worth +3 to +5 presentations. The richer climb already contains `smaller-block` and `max-knots`, both of which fall as a pair approaches the trivial state, so it self-regulates: with and without the threshold it scores the identical 19/24 at budget 1,000. If you use the budget-1000 ordering, it is a **single weight vector with no phases at all** — simpler than the phased form this document previously recommended. (`T = 16` is still a safe default if you want one: it is among the optima in 7 of 8 measured cases.)

**Counted as problems rather than rows, which is the honest unit.** Those 24 rows are only **19 distinct automorphism classes** — several are the same presentation up to a change of variables, so a row count double-counts. On distinct problems the tuned ordering solves **16/19 at budget 1000 against the baseline's 5/19**, and **13/19 vs 2/19** at 500. Only three distinct problems resist it (classes 93, 97, 98; class 93 alone contributes three of the five "unsolved rows") — and all but one of those is reachable by a second ordering from a different family, see below. This is the same discipline the equivalence-class work already established for this benchmark — quotient by every symmetry that preserves the question before counting anything.

At budget 1000 that is a near-4× improvement on the rows in question (5 → 19 of 24). On the leak-free held-out slice, restricted to the same bins 4–7, the tuned ordering solves **7/7** where the baseline solves **1/7** (at 500: 5/7 vs 1/7). It also solves *shorter*: on the 29 rows both solve at 1000, mean path **17.3 vs 19.2** — a win on the secondary criterion too.

## How to actually run it

`experiments/heuristic_search/hsolve.py` is a drop-in for `greedy_baseline.greedy_search`. It returns **exactly** the same dict — the certificate `path` and `path_moves`, `min_relator`/`max_relator`, `max_relator_length_expanded`, every key — so nothing downstream needs to change:

```python
from experiments.heuristic_search.hsolve import greedy_search_h, RECOMMENDED

stats = greedy_search_h(r1, r2, node_budget=10**6,
                        max_relator_length=48, config=RECOMMENDED)
```

`config=None` orders by length and reproduces the baseline exactly, so you can A/B the two in one run. `RECOMMENDED` is the budget-1000 ordering above; `LEAN_SMALL_BUDGET` is the ~500 one.

**What is verified** (`python3 -m experiments.heuristic_search.verify_hsolve`, and it must print ALL PASS):

1. with `config=None` it reproduces `greedy_search` field for field, `path_moves` included;
2. under a tuned ordering it pops identically to the research harness every number in this document was measured with — so the reports describe what a production run will do;
3. every certificate it returns replays **independently**, through `moves_to_states` from the recorded Definition 2.1 moves, and lands on a trivial pair. That is the check a self-consistent bug cannot pass, and it is the one that matters: a bad path would corrupt results rows silently.

Two caveats worth keeping. It has not been run inside `run_baseline.py`'s resume/W&B machinery — the function contract matches, but the integration itself is untested. And it uses the string-keyed dict of the normal solver, not the compact solver's packed arena, so at very large budgets it will want more memory than `high_speedup` mode; size accordingly or port the ordering into the compact key as a follow-up.

`L` = total length of the pair. `knots` = `max(#x-blocks, #y-blocks)` summed over both relators. `max-knots` = the larger relator's knot count. `xy-imbalance` = `|#x − #y| / L`. `smaller-block` = the smaller of the two generators' mean run-lengths. **Let relators grow to ~48** (they climb to ~30; capping at 24 loses nothing at these budgets but nothing is gained by capping either — see caveats).

What shifts with budget is how rich the climb should be. At 500 a lean knots + generator-imbalance climb is best — a richer one wastes early pops — and it needs the length-16 boundary to stop it chasing knots into the endgame. At 1000 the richer climb overtakes it (bins 4–7: 11 → 19 with budget, where the lean one holds at 16) and no longer needs the boundary at all. That crossover is the whole reason to re-tune at the budget you actually run.

**One honest wrinkle on the 1000 pick.** The selection procedure actually chose a *block* climb (`L − 2·max-block + 5·smaller-block`, also threshold-free) — it and the knot climb both reach 43/66 and both solve 7/7 on the held-out bins 4–7, a dead tie. I recommend the knot climb above because it is the more principled (it is what the whole study points at) and it is what the budget-1000 promotion (EXP-06) selected; the block config is an equally-good empirical alternative, not a better one. If you want one ordering for both budgets, use the 500 row.

## If you have compute for two runs, make the second one *different*

The single most useful thing found late in this program, and it inverts the obvious move. At budget 1,000 on the decidable band:

| second ordering, run at **full** budget alongside the recommended climb | alone | union with the climb |
|---|---|---|
| `blocks` — another finalist, equally strong | **19**/24 | 19/24 — **adds nothing** |
| `while L>16: L + 7.5·smaller-block + 1.2·imbal`, **no knot term at all** | 15/24 | **23**/24 — adds 4 rows |

A *weaker* ordering from a **different family** is worth far more as a partner than an equally strong one from the same family. At budget 1,000 the union of all five finalists is 19/24 — exactly what the best single reaches — so they are redundant with one another: they find the same presentations easy and the same ones hard. The four extra rows (`ms568`, `ms573`, `ms578`, `ms583`) come from leaving the knot family entirely.

So: **with 2× the compute, run the recommended climb and one structurally different ordering at full budget each.** Do *not* run two knot climbs, and do not divide one budget between them — splitting loses at every ratio tested (EXP-17, EXP-20).

One caveat on the number: those complements were picked *because* they solved rows the finalists miss, so 23/24 is optimistic on exactly those rows. The qualitative claim — a different family reaches different presentations — is what the experiment supports; treat the count as a demonstration, not an out-of-sample estimate.

## Which one to run at Colab scale

Both orderings above were measured at ≤1,000 nodes, and you run at 10⁵–10⁶. The bridge is the *shape* of the advantage, not its level (EXP-16): read each ordering's solve count as a curve against budget and look at what the gap is doing where the local ceiling cuts it off.

| ordering | gap over baseline @500 | @1000 | tail |
|---|---|---|---|
| `L + 8·knots − 6·xy-imbalance` (the 500 winner) | +14 | +11 | **turning over** |
| `L + 8·knots` | +10 | +11 | flat (±1) |
| **the richer climb** | +12 | **+14** | **still growing** |

Only the richer climb is still converting budget into new solves at the ceiling. The lean orderings peak mid-range and give ground back — they find their solutions early and then stop finding new ones. **Two independent measurements agree on this**: the scaling curve here, and the promotion test (EXP-06), where the richer climb gained 25→29 with budget while the lean winner plateaued at 27→27. That agreement is the strongest evidence in this program for what to run large, so: **use the richer climb for any serious run.**

## The most striking number: it does not just solve more, it reorders difficulty

Counting solves understates what happens. On the rows it does crack, the reduction against the length baseline's own measured cost is enormous:

| presentation | baseline needs | knot ordering | reduction |
|---|---|---|---|
| `ms633` | 26,838 nodes | **108** | **248×** |
| `ms628` | 26,774 nodes | **107** | **250×** |
| `ms575` | 14,383 nodes | 422 | 34× |
| `ms581` | 9,567 nodes | 385 | 25× |

And yet the three problems it fails on cost the baseline only ~13k–16k nodes — *less* than the two it solves 250× faster. **Difficulty under length ordering does not predict difficulty under the knot ordering.** The two orderings find different things hard, which is why the difficulty bins (graded under the baseline) are the right axis to report *against* and the wrong thing to tune toward.

This is also the strongest reason to expect the ordering to matter at Colab scale rather than only here: a 250× reduction on a 27k-node problem is the kind of effect that moves a 10⁶-node search into range, not a constant-factor speedup.

## Your knot intuition, tested directly

The claim was that on a very hard presentation, reducing even one knot opens up opportunities worth a longer path. Measured per difficulty stratum (EXP-15), sweeping only the knot coefficient:

| stratum | k=0.5 | k=1 | k=2 | k=3 | k=4 | k=8 | k=16 | reading |
|---|---|---|---|---|---|---|---|---|
| easy (bins 0–3) | 16 | 16 | 16 | 16 | 16 | 16 | 16 | knots are **irrelevant** — everything solves at any weight |
| hard (bins 6–7) | 0 | 0 | 0 | **3** | 3 | 3 | 3 | **nothing solves at all** until the knot term is heavy enough |

**Supported, in the form that matters.** On the hard stratum the knot term is not merely *worth more* — it is the difference between solving three problems and solving **none**. On the easy stratum it does nothing. That is a stronger statement than the original intuition.

**Not supported, in the form it was posed.** The optimum does not keep climbing with difficulty: past the threshold the magnitude stops mattering. It is a threshold to clear, not a dial to turn up — so there is nothing to gain from conditioning the weight on the presentation, and a single value comfortably above it (the 8–9 the winners already use) serves every stratum at once.

Two related negatives, both measured rather than assumed: a **depth** term (weighted-A*) does not improve on a good structural ordering — 1 of 216 arms beat its incumbent, on the weakest one, at one budget only (EXP-11) — and a **third length tier** never beats two (EXP-13). The two-phase, single-knot-weight shape is the whole recommendation; the extra knobs are not worth their parameters.

## Why knots, and why phased

- **Knots are the signal.** Of the thirteen rotation-invariant state features swept one at a time (EXP-02), knot count moved the needle most: `L + 8·knots` took the baseline from 17/40 to 23/40 on the training slice, and on the *decidable* rows (excluding the 16 easy rows every ordering solves) from 2/10 to 8/10. This is the operational form of the "reduce a knot to open opportunity" idea — a state that bought a knot reduction sorts above one that did not, so the search spends its budget where the structure improves.
- **Phasing is real where it is needed.** Switching to a structural climb only while the pair is long, and to pure length once short, reached 25/40 (EXP-03) and the joint search pushed it to 27/40 (EXP-04). The control on the *direction* — climbing while short, length while long — never beat the baseline at any threshold, which proves the boundary phases the search across the barrier rather than merely partitioning the queue. But EXP-18 later showed the phase earns its place only for **lean** knot-only climbs (+3 to +5); a climb that already carries `smaller-block` and `max-knots` self-regulates near the trivial state and scores the same with or without it.
- **The pipeline earns its second stage.** The best ordering at 500 nodes is *not* the best at 1000 (EXP-06): the lean knot climb plateaus (27→27) while a richer multi-feature climb keeps converting budget into solves (25→29). Always re-select at the budget you will actually run.

## The caveats — read these before trusting the numbers

- **This is decidable → decidable generalisation, and the split is leak-free — but the pipeline is not perfectly so.** Train and test share no automorphism class (`splits_aut.json`), so the held-out solves are transfer to genuinely new problems, not change-of-variables twins. The one caveat: the 25 candidates that were re-scored on the aut split were *proposed* by ranking on the stratified train slice, which overlaps the held-out rows — so a config could have entered the shortlist partly for solving a row it is later "held out" on. Treat the held-out fraction (7/7) as an optimistic upper bound, not a clean transfer number. The qualitative claim — baseline 1/7 → tuned 7/7 on unseen aut-classes, structure generalises — survives this; the exact figure is soft. The *structure* (phase at 16, climb on knots/blocks) is what is robust; the exact weights are within selection noise, so do not read the third decimal of any weight as meaningful.
- **The second hump is out of reach at ≤1000 nodes, and that is now measured over the whole target set.** EXP-12 ran all **124 unsolved AC-classes**, each entered as its 8 signed-permutation relabels, under all four best orderings: **0 solves in 3,920 searches**. Nothing in bins 8–9 or the six reach rows solved either (EXP-08). These need tens of thousands to millions of nodes; a 1000-node budget cannot reach them. The knot ordering does not collapse a second-hump row to a small search — it helps on the decidable rows, which is a different and measurable claim.
- **Knot-*progress* does not predict a solve, even though the knot-*ordering* helps.** A checkpoint proxy — "how many knots did the search shed by node 500" — does not forecast whether it will solve by 1000 (EXP-07: P(solve | dropped a knot) = 0.10 vs 0.14 without; length-progress fails the same way). So for the unsolvable second hump there is no honest progress signal to rank orderings by, and this recommendation is for the decidable regime only. Tuning the climb to be stronger for harder (longer) presentations — the length-tiered knot weight — is the natural next step, but it is an unvalidated extrapolation until the second hump becomes measurable at a larger budget.
- **Path length is secondary, as requested — and it also improved.** On the 29 rows both the baseline and the budget-1000 winner solve, the winner's mean path is **17.3 moves against the baseline's 19.2**, so the extra solves do not come at the cost of longer certificates. This is a same-row comparison, which is the only fair one: on the rows only the tuned ordering solves there is no baseline path to compare against.

## How this was produced

Eight experiments, each with its raw jsonl and a report in this directory; the index is in `README.md`. The search kernel (`hfast.py`) does one numba call per pop and is pinned bit-identical to the reference solver on the states where they could differ (`test_hfast.py`, `verify_fast.py`). Selection used the difficulty-stratified split; the final winner and this held-out number used the automorphism-disjoint split, read once.
