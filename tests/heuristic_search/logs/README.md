# Heuristic-search hyperparameter program — experiment log

One file per experiment, written as it runs. `EXP<nn>_<name>.jsonl` is the raw per-(config, presentation) rows; `EXP<nn>_<name>.md` is the report derived from it. Both are committed, because the jsonl is what makes a claim re-checkable without re-running anything.

## The question

The previous push found that block/knot features make a better heap ordering than total length (17/60 → 30/60 at budget 100). This program asks what else is in that space: which of thirteen state features carry signal, at what weights, whether the ordering should change as the search descends, and whether letting relators grow past the traditional 24-letter cap buys anything.

## Rules this program runs under

**The control is the baseline search, not a re-implementation of it.** `BASELINE_CONFIG` must reproduce `greedy_search` presentation by presentation — same solved flag, same `nodes_explored` — at **every** cap used, because raising `max_relator_length` changes the baseline itself. Pinned in `tests/heuristic_search/test_hlab.py`; nothing below is readable if it fails.

**The priority is a pure function of the state.** The visited set dedups on first discovery with no decrease-key, so a state's key is fixed by whichever path found it first. Any term reading `depth`, or reading the parent (e.g. "did this move drop a knot?"), makes pop order depend on discovery order and stop being reproducible. "Dynamic by depth and length" is therefore implemented as *length-keyed segments* that switch the whole weight vector — not as a depth term.

**One frozen split, read once.** `splits.json` was written before the first evaluation: 40 train / 20 test, stratified 4/2 across all ten difficulty bins, plus the 6 reach rows held apart. Everything is selected on `train`. `test` is read at the end and never used to choose anything. With a dozen parameters against a benchmark this small, best-of-N selection is upward-biased by construction, and the only defence is a slice nothing was chosen on.

**The 6 reach rows are scored on progress, not solves.** They are open problems — none will solve at 1,000 nodes, and none is expected to. Their metric is `min_total` (this repo's `min_relator_length`, the *sum* of the pair) against each row's `bar_to_beat`.

## Index

| exp | question | verdict |
|---|---|---|
| [EXP-01](EXP01_mrl.md) | does raising the relator cap above 24 do anything? | **inert under length-ordering** — 24/32/48/64 bit-identical; must be tested as an interaction (→ EXP-05) |
| [EXP-02](EXP02_single.md) | which single features carry signal, and at what sign? | **knots win** — `L+8K` 17/40→23/40 (p=0.031); decidable 2/10→8/10; winner pops a 28-letter relator |
| [EXP-03](EXP03_segments.md) | should the ordering change phase as the state shortens? | **yes** — `[<=16]L1[<=inf]K8+L1` 25/40 (p=0.008); climb while long, revert to length when short; inverted never beats control |
| [EXP-04](EXP04_multi.md) | joint weight search, with best-of-N optimism measured | running |
| [EXP-05](EXP05_cap.md) | does the cap bind once the ordering climbs? | queued |
| [EXP-06](EXP06_promote.md) | do the 500-node winners hold at budget 1,000? | queued |
| [EXP-07](EXP07_knot_proxy.md) | does knot-progress predict a solve? (gate before ranking the 2nd hump on it) | **NO** — P(solve\|knot drop)=0.10 vs 0.14; length-progress fails too; rank the 2nd hump on real solves only |
| [EXP-08](EXP08_reach.md) | can any ordering crack a 2nd-hump row at ≤1,000? | queued (expected: none) |
| [FINDINGS](FINDINGS.md) | the winner, on the aut-disjoint split, with the overfit price | queued |

## Two splits

- `splits.json` — difficulty-stratified, 40/20/6. Used for **feature discovery** (EXP-02…06). Leaks 6 aut-classes across train/test.
- `splits_aut.json` — automorphism-disjoint, 45/15/6, whole classes to one side. Used for the **final selection + one test read** (`synthesize`), so the held-out number is transfer to new problems, not change-of-variables twins. Measures decidable→decidable generalisation — **not** the decidable→second-hump gap, which is unmeasurable at ≤1,000 nodes.
