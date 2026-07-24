# The three-way cost table — standard greedy vs best CoV vs the tuned heuristic

Matched comparison: same 60 benchmark presentations, same node budget (10,000), same per-relator cap (24), one search per arm. Source: `three_way_b10k_subset60.csv` (built by `experiments/heuristic_search/three_way_b10k.py`), with the CoV portfolio cost recovered from `results/stable_ac/cov/covsweep_10000_66_subnc2pxysb_mrl24_cyc_s60r6_07_20_26.jsonl`. The runner's control gate passed on all 60 rows: the length-only ordering reproduces the greedy column pop for pop, so any difference below is attributable to the heap ordering alone.

## The winner

Roughly **2,270 config-arms across 28 experiments** (EXP-01 … EXP-28) reduce to one shipped ordering, `RECOMMENDED` in `experiments/heuristic_search/hsolve.py:45`:

```
priority = L + 2.53·K + 6.418·MK + 8.458·S + 3.292·xyimb        # one weight vector, no phases
```

`L` = total length of the pair. `K` = knot count (`max(#x-blocks, #y-blocks)` summed over both relators). `MK` = the larger relator's knot count. `S` = the smaller of the two generators' mean block lengths (letters of that generator ÷ its block count, pooled over both relators). `xyimb` = `|#x letters − #y letters| / L` — letter counts, not block counts.

All features read the **block decomposition**: maximal runs of a single generator, sign ignored (`x`/`X` both count as x), with the word read as a ring so the first and last run merge (`hfast.py:50-76`). Rotation-invariance is required — a feature that could see where the canonicaliser cut the cyclic word would be scoring the tie-break rather than the presentation. Note that `S ≥ 1` with equality at the trivial pair, and `xyimb = 0` there too, so on a min-heap both positive weights are goal-directed penalties that decay as a state approaches the target — this is the mechanism behind the threshold-free climb "self-regulating" near the endgame.

**Two honest qualifications on "the winner".** The automated budget-1000 selection actually chose a *phased block* climb (`[<=16]L1[<=inf]Bmax-2.185+L1+S5.668`, the config named in `FINDINGS.md`); the knot climb above was shipped on principle and on the EXP-06 promotion, and the two are a **documented dead tie** — both reach 43/66 and both 7/7 on the held-out bins 4–7. And `RECOMMENDED` was tuned at budget **1,000** while the table below runs at **10,000**, so the heuristic column is a lower bound on what a config re-selected at 10k would do.

## Solve counts, budget 10,000, cap 24

| bin | n | greedy | best CoV | heuristic |
|---|---|---|---|---|
| 0–4 | 30 | 30 | 30 | 30 |
| 5 | 6 | 6 | 6 | 6 |
| 6 | 6 | 4 | 6 | 6 |
| 7 | 6 | 0 | 6 | 5 |
| 8 | 6 | 0 | 2 | 0 |
| 9 | 6 | 0 | 2 | 0 |
| **total** | **60** | **40** | **52** | **47** |

The heuristic is a **strict superset of greedy** — 7 rows gained (`ms573`, `ms575`, `ms568`, `ms578`, `ms583`, `ms628`, `ms633`), 0 lost — and its solved set is a **strict subset of best CoV's**: at this budget it adds no reach CoV does not already have (`union(CoV, heur) = 52 = CoV alone`).

## Nodes explored — the 40 rows all three arms solve

| arm | mean nodes | median | total | mean path |
|---|---|---|---|---|
| standard greedy | 1,206 | 197 | 48,227 | 36.9 |
| **tuned heuristic** | **215** | **100** | **8,597** | 31.1 |
| best CoV *(oracle)* | 72 | 14 | 2,878 | **19.6** |
| best CoV *(greedy-first, deployable)* | 1,206 | — | 48,227 | — |

**The CoV column needs two numbers, and the difference is the whole point.** `bestcov_nodes` is the cheapest of the ~80–174 subword-CoV starts tried per presentation — an **oracle**: it prices the winning `z` as if you knew it in advance. You don't. The full portfolio costs a mean of **172,867** nodes per presentation (6.9M over these 40 rows), and even that overstates the deployable cost, because the sweep's `n_cov = 0` start *is the original presentation* — verified identical to the greedy arm in `nodes_explored` and `solved` on **all 60 rows**. So any sane CoV strategy runs the original first and diversifies only on failure, which costs **exactly greedy's 1,206** on every row greedy already solves. CoV's portfolio tax is paid only where greedy fails.

Priced that way the three arms separate cleanly:

- **On rows greedy can solve, the heuristic is ~5.6× cheaper (215 vs 1,206) and CoV buys nothing at all.** The ordering is free — same solver, same budget, one weight vector.
- **On the 7 rows greedy cannot solve, the heuristic gets them for 106–7,641 nodes; CoV gets them for a deployable 21,277–63,211.** Two of them (`ms628`, `ms633`) the heuristic cracks in **~107 nodes** against greedy's exhausted 10,000.
- **On the 5 rows only CoV reaches (`ms596`, `ms605`, `ms610`, `ms634`, `ms635`), CoV pays ~32,000 nodes each.** That is a genuine *reach purchase*, not a cost win — CoV is buying states the ordering cannot reach at this budget, at roughly 3× the budget in total work.

CoV also wins **path length** outright (19.6 vs 31.1 vs 36.9). Its certificates are the shortest of the three.

## What it suggests

**The heap ordering and the change of variables are complementary, not competing.** They win on different axes: the ordering is a pure efficiency gain (5.6× fewer nodes, free, strictly non-losing), and CoV is a pure reach gain (bins 8–9, bought with ~3× the budget in portfolio work). Neither dominates. The obvious untested move is stacking them — run the tuned ordering *on the CoV starts* — since nothing in this table prices that combination.

**Difficulty is reordered, not merely compressed.** The heuristic's speedups concentrate exactly where greedy is worst: 24.8× on `ms581` (9,567→385), 23.6× on `ms586`, 11.3× on `ms543`. `ms628`/`ms633` are stronger still but cannot be quoted as a ratio here — greedy exhausts 10,000 nodes on them without solving, and against greedy's *actual* measured cost at a 1M budget (26,774 / 26,838 nodes) the reduction to ~107 is the **250×** reported in `BEST_HEURISTIC.md`. Only 3 of 40 rows got slower under the heuristic, all trivially (`ms589` 558→575, `ms43` 13→14, `ms247` 46→70). A search ordering that pays off most on the hardest rows is the kind of effect that moves a large budget into range rather than a constant-factor speedup — which is what EXP-28 then confirmed at Colab scale: at budget **100,000, cap 48**, the tuned ordering finished the graded benchmark at 62,534 nodes (**60/60**), taking all of bin 9 (6/6) where the baseline scores 0/6, with a hump-band multiplier of 3.4×–23× against the baseline's 1M-node data. *(Keep that table separate from this one — different budget and cap; 47/60 here is not in tension with 60/60 there.)*

**The bin-8/9 wall is shared at this budget — and it *is* a budget artifact.** `ms622`–`ms625` and `ms636`–`ms639` are unsolved by every arm here, and the CoV sweep found **0 solving starts out of ~170** on each at 10,000 nodes. Doubling the budget to 20,000 and changing nothing else, **all eight escape**: 39–50 of those same ~170 starts solve, the cheapest in 14,352 nodes, with every pair joined back to its own 10,000-node row to prove the cap and reduction setting were identical ([`ESCAPE.md`](../stable_ac/cov/allcov_escape/ESCAPE.md)). This document already contained its own refutation two paragraphs up: EXP-28's tuned ordering takes all of bin 9 at budget 100,000. And these eight are `ms640_solved` rows — **trivial by construction** — so they were never the second hump in the first place; that is the 124 unsolved classes, a different population, where every arm still scores 0.

The escape does not make CoV the right tool for them. Priced against the untransformed route, the best-CoV oracle cost ~2.2M nodes per presentation to find; a blind CoV restart — the runnable version — wins 2.58×–3.38× on the four bin-9 rows but is a coin-flip (0.95×–1.26×) on the four bin-8 rows; and the tuned ordering beats both on all eight, at ~62.5k nodes in a single search. Two caveats on those ratios, both in `ESCAPE.md`: they are a **best case over the collection budget** (20,000 is the most favourable choice on four of the eight rows; at 15,000 the restart loses on six of eight), and the bin-9 win is the **denominator moving** — the restart is nearly flat at 62.5k–83.0k across all eight while the greedy goes 59.7k–78.8k on bin 8 to 213.9k–273.0k on bin 9. The lesson that produced: [price the untransformed route](../../experiments/lessons/price-the-untransformed-route.md).
