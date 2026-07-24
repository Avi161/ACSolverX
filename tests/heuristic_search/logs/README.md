# Heuristic-search hyperparameter program — experiment log

One file per experiment, written as it runs. `EXP<nn>_<name>.jsonl` is the raw per-(config, presentation) rows; `EXP<nn>_<name>.md` is the report derived from it. Both are committed, because the jsonl is what makes a claim re-checkable without re-running anything.

## The question

The previous push found that block/knot features make a better heap ordering than total length (17/60 → 30/60 at budget 100). This program asks what else is in that space: which of thirteen state features carry signal, at what weights, whether the ordering should change as the search descends, and whether letting relators grow past the traditional 24-letter cap buys anything.

## Rules this program runs under

**The control is the baseline search, not a re-implementation of it.** `BASELINE_CONFIG` must reproduce `greedy_search` presentation by presentation — same solved flag, same `nodes_explored` — at **every** cap used, because raising `max_relator_length` changes the baseline itself. Pinned in `tests/heuristic_search/test_hlab.py`; nothing below is readable if it fails.

**The priority is a pure function of the state.** The visited set dedups on first discovery with no decrease-key, so a state's key is fixed by whichever path found it first. Any term reading `depth`, or reading the parent (e.g. "did this move drop a knot?"), makes pop order depend on discovery order and stop being reproducible. "Dynamic by depth and length" is therefore implemented as *length-keyed segments* that switch the whole weight vector — not as a depth term.

**Frozen splits, test read once.** There are two (see *Two splits* below); neither is regenerated. `splits.json` was written before the first evaluation: 40 train / 20 test, stratified 4/2 across all ten difficulty bins, plus the 6 reach rows held apart. Everything is selected on `train`. `test` is read at the end and never used to choose anything. With a dozen parameters against a benchmark this small, best-of-N selection is upward-biased by construction, and the only defence is a slice nothing was chosen on.

**The 6 reach rows are scored on progress, not solves.** They are open problems — none will solve at 1,000 nodes, and none is expected to. Their metric is `min_total` (this repo's `min_relator_length`, the *sum* of the pair) against each row's `bar_to_beat`.

## Index

| exp | question | verdict |
|---|---|---|
| [EXP-01](EXP01_mrl.md) | does raising the relator cap above 24 do anything? | **inert under length-ordering** — 24/32/48/64 bit-identical; must be tested as an interaction (→ EXP-05) |
| [EXP-02](EXP02_single.md) | which single features carry signal, and at what sign? | **knots win** — `L+8K` 17/40→23/40 (p=0.031); decidable 2/10→8/10; winner pops a 28-letter relator |
| [EXP-03](EXP03_segments.md) | should the ordering change phase as the state shortens? | **yes** — `[<=16]L1[<=inf]K8+L1` 25/40 (p=0.008); climb while long, revert to length when short; inverted never beats control |
| [EXP-04](EXP04_multi.md) | joint weight search, with best-of-N optimism measured | **27/40, optimism only 0.20** — phased `K8.9+xyimb-6`, margin is signal not selection |
| [EXP-07](EXP07_knot_proxy.md) | does knot-progress predict a solve? (gate before ranking the 2nd hump on it) | **NO** — P(solve\|knot drop)=0.10 vs 0.14; length-progress fails too; rank the 2nd hump on real solves only |
| [EXP-05](EXP05_cap.md) | does the cap bind once the ordering climbs? | **reaches the cap but no extra solves** — climb pops maxpop 31 (vs 19 for length), yet 27/40 at every cap 24–96 |
| [EXP-06](EXP06_promote.md) | do the 500-node winners hold at budget 1,000? | **no — the winner changes** — richer knot climb 25→29 while the lean 500-winner plateaus 27→27 |
| [EXP-08](EXP08_reach.md) | can any ordering crack a 2nd-hump row at ≤1,000? | **none** (as expected — needs 60k–10M+ nodes) |
| [EXP-09](EXP09_fullbench.md) | the finalists on the full 66-benchmark | **26→40 at 500, 29→43 at 1000** (+14 solves each) |
| [FINDINGS](FINDINGS.md) | winner on the aut-disjoint split, per budget, overfit priced | held-out bins 4–7: baseline 1/7 → **5/7** (500), **7/7** (1000) |
| [EXP-10](EXP10_refine.md) | does a finer search near the winners beat them at budget 1,000? | **no — a dead tie** (20/24 both); best-of-400 optimism 1.23, so stop |
| [EXP-11](EXP11_depth.md) | does a depth term (weighted A*) help? — the axis ruled out on principle earlier | **no** — 1 of 216 arms beat its incumbent, on the weakest one, one budget only |
| [EXP-13](EXP13_tiers.md) | does a third length tier help, and should the knot weight rise with length? | **no to both** — 3 tiers only ever match 2; the weight wants to FALL with state length |
| [EXP-14](EXP14_newfeats.md) | does a second feature family (Bmaxrun/Bspread/ratio/density) add anything? | **unlocks nothing** — though the winner already solves all 27 decidable rows, so there was no headroom |
| [EXP-12](EXP12_unsolved124.md) | can any ordering crack one of the 124 unsolved AC-classes at 1,000? | **no** — 0 solves in 3,920 searches (124 classes x 8 relabels x 4 orderings) |
| [EXP-15](EXP15_wbd.md) | is a knot worth more on a HARD presentation? (the user's intuition, directly) | **yes, as a threshold** — hard stratum solves 0 below k=3, then 3/8; easy stratum solves all at any k |
| [EXP-16](EXP16_scaling.md) | how does the advantage scale with budget? (the bridge to Colab) | **only the richer climb is still growing** at the ceiling (+12→+14); the lean 500-winner turns over (+14→+11) |
| [EXP-17](EXP17_portfolio.md) | at fixed budget, one deep search or a portfolio over the 8 relabels? | **depth wins, monotonically** — k=1 > 2 > 4 > 8 for every ordering; the alternates almost never fire |
| [EXP-18](EXP18_threshold.md) | is the endgame threshold 16 still right for the ordering that won? | **it is inert for the winner** — worth +3..+5 for lean knot-only climbs, +0 for multi-feature ones |
| [EXP-19](EXP19_joint1000.md) | joint search at budget 1000 over all 17 features, threshold optional | **nothing beats the incumbent** (28/31, +0 against 1.65 optimism) — the recommendation is at its ceiling |
| [EXP-20](EXP20_cportfolio.md) | at fixed budget, split across different *orderings*? | **no** — pairs average 15.5/24 vs singles' 18.0; but later members DO fire, so the complementarity is real |
| [EXP-21](EXP21_complement.md) | with more compute, what makes a good *second* ordering? | **a different family** — a weaker knot-free climb adds 4 rows (19→23/24); another finalist adds 0 |
| [EXP-22](EXP22_complement_cv.md) | is the complement strategy real, or hindsight? (200 half-splits, no new searches) | **real** — +1.18 rows held out vs +0.27 strongest-arm, +0.04 random; premium only 0.24 |
| [EXP-23](EXP23_hump_diverse.md) | the second hump, attacked from the *other* ordering family | **still nothing** — the negative is no longer specific to knot climbs |
| [EXP-24](EXP24_tie_topk.md) | the tie-break sign and beam-style child filtering — 2 knobs never swept | **neither changes the recommendation** — filtering loses at every width (topk=8 solves 0); tie inert for the winner |
| **[BEST_HEURISTIC](BEST_HEURISTIC.md)** | **the recommendation to use, by node budget** | **held-out, distinct problems: baseline 1/6 → tuned 6/6**; climb on knots, no threshold needed at 1000 |

## Two splits

- `splits.json` — difficulty-stratified, 40/20/6. Used for **feature discovery** (EXP-02…06). Leaks 6 aut-classes across train/test.
- `splits_aut.json` — automorphism-disjoint, 45/15/6, whole classes to one side. Used for the **final selection + one test read** (`synthesize`), so the held-out number is transfer to new problems, not change-of-variables twins. Measures decidable→decidable generalisation — **not** the decidable→second-hump gap, which is unmeasurable at ≤1,000 nodes.
