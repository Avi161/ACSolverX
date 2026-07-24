# [2026-07-24] Alternative starts are worth running, but never worth dividing a budget for [TRAP]

Two facts about this benchmark push in opposite directions, and it is easy to take the wrong one as licence to split a search budget.

**Fact one, which is real:** alternative starting strings matter enormously. A signed-permutation relabel is the same presentation under a rename of the generators — the same AC-class, the same difficulty in any orbit sense — but the greedy reads *strings*, so each image is a genuinely different search. This repo measured relabels supplying **14 of 17** unsolved→solved flips in the one-hop CoV sweep.

**Fact two, which is also real:** no single heap ordering dominates. The best single ordering solves 19 of the 24 decidable benchmark rows; the **union over every ordering tried across a 20-experiment program solves 23**. Only `ms596` (aut-class 97) resisted everything, across 607 recorded attempts.

Both facts say "diversity helps". Neither says diversity helps *at a fixed budget*, and that is the inference that fails.

## The measurement

EXP-17, at a fixed total of 1,000 nodes per row: one search of 1,000 versus `k` searches of `1000/k`, one per relabel, stopping at the first solve.

```
k=1 (1000 each)   k=2 (500)   k=4 (250)   k=8 (125)
richer climb   19        14           8           3
phased K8      16        12          10           4
baseline        5         3           0           0
```

Monotone, no crossover, every ordering. And the mechanism is visible in the run's own bookkeeping: the mean number of relabels tried before a solve was **1.0** across every portfolio arm. When a divided search succeeds it succeeds on the *first* string it is handed. The alternates are being run and are contributing essentially nothing at these depths, so splitting does not buy chances — it only truncates the search that was going to work.

## Why the two facts are compatible

The flips result gave each relabel a **full** budget. That is diversity as *additional compute*: eight searches of 1,000 nodes, of which one succeeds. EXP-12 uses it that way too, and it is a sound use. What fails is diversity as a *substitute* for depth — the hope that the same total compute, re-partitioned, finds more.

## Rule

**Before splitting a budget across restarts, measure how often the alternates actually fire.** If the successful runs almost always come from the first restart, the diversity is nominal at that depth and splitting is pure loss. Record "which member produced the solve" and "how many were tried" in the portfolio run itself — those two columns answer the question directly, and without them a monotone loss looks like an unlucky trade-off rather than a structural one.

And keep the two claims apart in any write-up: *"alternative starts unlock rows"* (true, and worth compute) is not *"alternative starts are worth dividing a budget for"* (false here). Related: [check the control can move](control-with-no-dynamic-range.md) — the same family of error, where an arm is measured under conditions that make its effect unobservable.
