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
| [EXP-01](EXP01_mrl.md) | does raising the relator cap above 24 do anything? | **inert under length-ordering** — 24/32/48/64 bit-identical at both budgets |
| [EXP-02](EXP02_single.md) | which single features carry signal, and at what sign? | running |
