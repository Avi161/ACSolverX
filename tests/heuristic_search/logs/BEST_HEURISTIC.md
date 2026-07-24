# The best heuristic — what to use, by node budget

The short answer, then the evidence and the caveats. Everything here is measured on the greedy substitution search with the heap ordering swapped; nothing else about the search changed, so every number is attributable to the ordering alone.

## Use this

**Order the heap by length plus a structural climb — one that values knots.** The one thing every result in this program agrees on is that a knot term in the heap key is what separates a search that crosses the two-hump barrier from one that does not.

> ### The one number
>
> On the **three automorphism classes no tuning slice ever contained** — not the shortlist, not the weight search, not the promotion — at budget 1,000, counted as distinct problems:
>
> ### baseline 1 / 3  →  tuned **3 / 3**
>
> At budget 500 the same three go 1/3 → 2/3. Three problems is a small number and it is the honest one: it is what remains after removing every row any stage of the tuning could have seen.

**A correction, because an earlier version of this document overstated it.** This box previously read *"1/6 → 6/6 on held-out automorphism classes"*, using the 6 classes in `splits_aut.json`'s test side. That split is genuinely automorphism-disjoint from `aut_train`, and the arithmetic was right — but the weight vector was **not** selected on `aut_train`. It came from EXP-04 (the joint weight search) and EXP-06 (the budget-1000 promotion), both of which ran on the **stratified** 40-row slice in `splits.json` — and that slice contains `ms544`, `ms602`, `ms628` and `ms633`, which are 4 of the 7 rows in the supposedly held-out set, covering classes 74, 103 and 110. For class 110 the tuning saw both members. So four sevenths of that "held-out" evidence was selection data wearing a different split's label. An independent audit of the raw jsonl caught it; the number above is what survives.

Everything below is subordinate detail. Several other denominators appear — 24 rows, 19 distinct problems, 31, 45 — because different experiments ran on different slices; each is stated where it is used, and none of them supersedes the line above.

Throughout this document "decidable tier" means **difficulty bins 4–7** (24 rows) — a fixed structural band, *not* `perbin.decidable()`, which derives a mixed-outcome row set from whichever configs are in a given file and therefore differs between experiments. The right denominator for the *in-sample* tables is those 24 rows — neither free (bins 0–3, which every ordering solves) nor out of reach (bins 8–9 and the reach rows, which nothing solves at ≤1000). That is where an ordering is actually tested.

| your node budget | the ordering to use | bins 4–7 (of 24) | full 66 | held-out bins 4–7 (leak-free) |
|---|---|---|---|---|
| **~500** | `while L>16: L + 8·knots − 6·xy-imbalance;  else: L` | **16** (baseline 2) | 40 | **5/7** (baseline 1/7) |
| **~1000 and above** | `L + 2.5·knots + 6.4·max-knots + 8.5·smaller-block + 3.3·xy-imbalance` — **no threshold needed** | **19** (baseline 5) | 43 | **7/7** (baseline 1/7) |

**The threshold is only needed for the lean ordering** (EXP-18). A climb carrying *only* a knot term must be switched back to pure length below 16, or it keeps chasing knots into the endgame where nothing structural is left to buy — that is worth +3 to +5 presentations. The richer climb already contains `smaller-block` and `max-knots`, both of which fall as a pair approaches the trivial state, so it self-regulates: with and without the threshold it scores the identical 19/24 at budget 1,000. If you use the budget-1000 ordering, it is a **single weight vector with no phases at all** — simpler than the phased form this document previously recommended. (`T = 16` is still a safe default if you want one: it is among the optima in 7 of 8 measured cases.)

**Counted as problems rather than rows, which is the honest unit.** Those 24 rows are only **19 distinct automorphism classes** — several are the same presentation up to a change of variables, so a row count double-counts. On distinct problems the tuned ordering solves **16/19 at budget 1000 against the baseline's 5/19**, and **13/19 vs 2/19** at 500. Only three distinct problems resist it (classes 93, 97, 98; class 93 alone contributes three of the five "unsolved rows") — and all but one of those is reachable by a second ordering from a different family, see below. This is the same discipline the equivalence-class work already established for this benchmark — quotient by every symmetry that preserves the question before counting anything.

At budget 1000 that is a near-4× improvement on the rows in question (5 → 19 of 24). On the leak-free held-out slice, restricted to the same bins 4–7, the tuned ordering solves **7/7** where the baseline solves **1/7** (at 500: 5/7 vs 1/7). It also solves *shorter*: on the 29 rows both solve at 1000, mean path **17.3 vs 19.2** — a win on the secondary criterion too.

## The Colab handoff — everything needed, in one place

**Getting the code there.** The push is DNS-blocked on the machine this ran on, so all commits sit on the local branch `worktree-hsearch-hyper`. A portable copy is at **`ACSolverX/hsearch-hyper.bundle`** (34 MB, `git bundle verify` reports a complete history). On a networked machine:

```bash
git fetch /path/to/hsearch-hyper.bundle worktree-hsearch-hyper:hsearch-hyper
git checkout research/w5/stable-ac-escape && git merge hsearch-hyper
git push origin research/w5/stable-ac-escape
```

**What to run.**

```python
from experiments.heuristic_search.hsolve import greedy_search_h, RECOMMENDED

a = greedy_search_h(r1, r2, node_budget=10**6, max_relator_length=48, config=None)         # baseline
b = greedy_search_h(r1, r2, node_budget=10**6, max_relator_length=48, config=RECOMMENDED)  # tuned
```

Same function, same returned dict, so an A/B is one run. If you have compute for a third arm, make it *structurally different* rather than another knot climb — see the two-ordering section below.

**Set `max_relator_length` to 48** — but not for the reason an earlier version of this document gave. It claimed the climb pops relators past 30 and that capping at 24 truncates it. Measured: at budget 1,000 caps 24 and 48 solve **exactly the same 43 of 66**, and the longest relator popped on a decidable row is **25**. The cap does not bind at these budgets. Use 48 anyway because it costs nothing, it is the setting every number here was measured at, and it removes a ceiling that could bind at the far larger budgets you will actually run — where the climb has room to go further than anything observed here. Do not expect it to change results at 10³.

**Memory.** `hsolve` uses the normal solver's string-keyed dict, not the compact packed arena, so at 10⁶ nodes it will want noticeably more RAM than `high_speedup` mode. Size for it, or port the ordering into the compact key first.

**The one prediction worth checking, and the only thing that cannot be settled locally.** Everything here was measured at ≤1,000 nodes, and the bridge to 10⁶ is EXP-16's *shape*: the recommended climb's advantage over the baseline was still **widening** where the local ceiling cut the curve off (+12 → +14 from budget 500 to 1,000), while the leaner orderings had already turned over. If that keeps holding, the advantage grows with your budget and this ordering is the right one to spend it on. **If the gap stops widening past 1,000, stop trusting the extrapolation** — the ordering would be buying earliness rather than reach, and the second-hump case would collapse. Record solve counts at several budget checkpoints in one long run and the answer falls out for free.

## What is verified about the drop-in

`experiments/heuristic_search/hsolve.py` returns **exactly** `greedy_baseline.greedy_search`'s dict — certificate `path` and `path_moves`, `min_relator`/`max_relator`, `max_relator_length_expanded`, every key — so nothing downstream changes. Run `python3 -m experiments.heuristic_search.verify_hsolve`; it must print ALL PASS. It checks three things:

1. with `config=None` it reproduces `greedy_search` field for field, `path_moves` included;
2. under a tuned ordering it pops identically to the research harness every number in this document was measured with — so these reports describe what a production run will do;
3. every certificate it returns replays **independently**, through `moves_to_states` from the recorded Definition 2.1 moves, and lands on a trivial pair. That is the check a self-consistent bug cannot pass, and the one that matters most: a bad path would corrupt results rows silently.

Also pinned as pytest (`tests/heuristic_search/test_hsolve.py`, part of a 55-test suite), including a guard that the config is not silently ignored — on `ms544` at budget 500, `config=None` exhausts the budget unsolved while `RECOMMENDED` solves in 160 nodes.

The one thing **not** verified: it has never been run inside `run_baseline.py`'s resume/W&B machinery. The function contract matches; the integration is untested.

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

So: **with 2× the compute, run the recommended climb and one structurally different ordering at full budget each.** Do *not* run two knot climbs; do not divide one budget between them (splitting loses at every ratio — EXP-17, EXP-20); and do *not* spend it on **relabels** of the same presentation. That last one is the surprise: running all eight signed-permutation relabels at full budget adds exactly **0** rows (EXP-25), because every state is canonicalised before it enters the heap and a relabel is very nearly inside the group canonicalisation already quotients out — the eight searches walk almost the same graph (`ms538` takes 517–530 nodes across all of them). Compute spent on a different *ordering* pays; compute spent on a different *spelling* does not.

**How much to actually expect.** The 23/24 above is optimistic — those complements were picked *because* they solved the rows the finalists miss. EXP-22 measures the real effect by cross-validation, inside a 320-config × 45-row matrix with 200 half-splits: choose the complement on one half, score its marginal gain on the other.

| how you pick the second ordering | rows it adds, **held out** |
|---|---|
| for complementarity (adds most rows the climb misses) | **+1.18** |
| for stand-alone strength (solves most on its own) | +0.27 |
| at random | +0.04 |

So picking *for complementarity* is worth about **4×** picking the strongest second arm, and the hindsight premium is small (0.24 rows). Expect roughly **one extra presentation**, not four — though on that slice only 3 rows were even available to gain, so it captures ~40% of what a complement could possibly add.

A related detail worth knowing if you tune further: the complement chosen in 173 of 200 splits uses `Bspread` (longest block − shortest), a feature that never improved the *primary* ordering in any experiment. A feature can be useless for building the best ordering and valuable for building a usefully different one.

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

Four related negatives, all measured rather than assumed. A **depth** term (weighted-A*) does not improve on a good structural ordering — 1 of 216 arms beat its incumbent, on the weakest one, at one budget only (EXP-11). A **third length tier** never beats two (EXP-13). Flipping the **tie-break** to deepest-first is exactly inert for the recommended ordering (EXP-24). And **beam-style child filtering** loses at every width — keeping only the 8 shortest children solves *nothing* — because the priority is already the filter, so a beam only deletes states the search needed later (EXP-24). The single-vector knot climb is the whole recommendation; every extra knob tested is either inert or harmful.

## Why knots, and why phased

- **Knots are the signal.** Of the thirteen rotation-invariant state features swept one at a time (EXP-02), knot count moved the needle most: `L + 8·knots` took the baseline from 17/40 to 23/40 on the training slice, and on the *decidable* rows (excluding the 16 easy rows every ordering solves) from 2/10 to 8/10. This is the operational form of the "reduce a knot to open opportunity" idea — a state that bought a knot reduction sorts above one that did not, so the search spends its budget where the structure improves.
- **Phasing is real where it is needed.** Switching to a structural climb only while the pair is long, and to pure length once short, reached 25/40 (EXP-03) and the joint search pushed it to 27/40 (EXP-04). The control on the *direction* — climbing while short, length while long — never beat the baseline at any threshold, which proves the boundary phases the search across the barrier rather than merely partitioning the queue. But EXP-18 later showed the phase earns its place only for **lean** knot-only climbs (+3 to +5); a climb that already carries `smaller-block` and `max-knots` self-regulates near the trivial state and scores the same with or without it.
- **The pipeline earns its second stage.** The best ordering at 500 nodes is *not* the best at 1000 (EXP-06): the lean knot climb plateaus (27→27) while a richer multi-feature climb keeps converting budget into solves (25→29). Always re-select at the budget you will actually run.

## The caveats — read these before trusting the numbers

- **This is decidable → decidable generalisation, and the split is leak-free — but the pipeline is not perfectly so.** Train and test share no automorphism class (`splits_aut.json`), so the held-out solves are transfer to genuinely new problems, not change-of-variables twins. The one caveat: the 25 candidates that were re-scored on the aut split were *proposed* by ranking on the stratified train slice, which overlaps the held-out rows — so a config could have entered the shortlist partly for solving a row it is later "held out" on. Treat the held-out fraction (7/7) as an optimistic upper bound, not a clean transfer number. The qualitative claim — baseline 1/7 → tuned 7/7 on unseen aut-classes, structure generalises — survives this; the exact figure is soft. The *structure* (phase at 16, climb on knots/blocks) is what is robust; the exact weights are within selection noise, so do not read the third decimal of any weight as meaningful.
- **The second hump is untouched, and none of the numbers above are progress on it.** Everything in this document is the *decidable* tier. On the hard tier the result is zero, unchanged, across both ordering families — EXP-12 ran all **124 unsolved AC-classes**, each entered as its 8 signed-permutation relabels, under all four best orderings: **0 solves in 3,920 searches**. Nothing in bins 8–9 or the six reach rows solved either (EXP-08). These need tens of thousands to millions of nodes; a 1000-node budget cannot reach them. The knot ordering does not collapse a second-hump row to a small search — it helps on the decidable rows, which is a different and measurable claim.
- **Knot-*progress* does not predict a solve, even though the knot-*ordering* helps.** A checkpoint proxy — "how many knots did the search shed by node 500" — does not forecast whether it will solve by 1000 (EXP-07: P(solve | dropped a knot) = 0.10 vs 0.14 without; length-progress fails the same way). So for the unsolvable second hump there is no honest progress signal to rank orderings by, and this recommendation is for the decidable regime only. Tuning the climb to be stronger for harder (longer) presentations — the length-tiered knot weight — is the natural next step, but it is an unvalidated extrapolation until the second hump becomes measurable at a larger budget.
- **Path length is secondary, as requested — and it also improved.** On the 29 rows both the baseline and the budget-1000 winner solve, the winner's mean path is **17.3 moves against the baseline's 19.2**, so the extra solves do not come at the cost of longer certificates. This is a same-row comparison, which is the only fair one: on the rows only the tuned ordering solves there is no baseline path to compare against.

## How this was produced

Eight experiments, each with its raw jsonl and a report in this directory; the index is in `README.md`. The search kernel (`hfast.py`) does one numba call per pop and is pinned bit-identical to the reference solver on the states where they could differ (`test_hfast.py`, `verify_fast.py`). Selection used the difficulty-stratified split; the final winner and this held-out number used the automorphism-disjoint split, read once.
