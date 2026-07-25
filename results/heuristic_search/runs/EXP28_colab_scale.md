# EXP-28 — the Colab run at 100,000 nodes: the extrapolation, settled

The one claim no local experiment could verify was the bridge from budget 1,000 to Colab scale: EXP-16 saw the recommended climb's gap over the baseline still widening (+12 → +14) where the local ceiling cut the curve off, and everything recommended for large budgets leaned on that shape continuing. This run is the user-executed test: both arms on all 66 benchmark rows at budget 100,000, cap 48, one search per (arm, row), `solved_at` giving every checkpoint below. 1.57 h of Colab; raw rows committed as `EXP28_colab_scale.jsonl`.

## The pre-registered metric said "turned over" — and then the row level says why that reading is wrong

The gap-vs-budget curve was the pre-registered decision metric, and honestly reported it fails: +11 → **+14** (at 1,000 — exactly where the tuning lived) → +9 → +7 → +10 → +4 → +4 → **+6**. Verdict printed by the runner: **turned over**.

But the metric silently lost its dynamic range at 62,534 nodes, because **the recommended ordering finished the benchmark there: 60 of 60 graded rows solved**. Its six remaining "misses" are `AK(3)`, `14_1`, `17_41`, `19_40`, `25_1`, `25_17` — the open reach problems, which nothing was expected to solve at 10⁵. From 62.5k to 100k the treatment had nothing left to gain, so the gap could only compress while the baseline caught up on rows the treatment had long finished. A trend metric whose treatment saturates mid-run reads as "turned over" precisely when the treatment wins hardest — the mirror image of the [control-with-no-dynamic-range](../../../experiments/lessons/control-with-no-dynamic-range.md) trap.

## What the run actually established

- **The strict superset holds at 10⁵, as it did at 10³.** Baseline-only solves: **none**. The tuned ordering's six exclusive solves are `ms634`–`ms639` — **all of bin 9, 6/6, where the baseline scores 0/6 at 100,000 nodes**.
- **Against the baseline's historical 1M-node data** (`nodes_1M`; measured at cap 24 — caveat, this run is cap 48, though the caps solved identically wherever compared):

| row | bin | tuned `solved_at` | baseline `nodes_1M` | multiplier |
|---|---|---|---|---|
| ms634, ms635 | 9 | ~25,000 | ~574,300 | **~23×** |
| ms636–ms639 | 9 | ~62,500 | 213,900–273,000 | 3.4–4.4× |
| ms605, ms610 | 8 | ~8,200 | ~61,000 | ~7.4× |
| ms628, ms633 | 7 | ~107 | ~26,800 | ~250× |
| ms622–ms625 | 8 | ~62,500 | 59,700–78,800 | ~1× |

- **The multiplier is heterogeneous, not a constant**: median 1.5× over the 54 both-solved rows (dominated by easy rows both arms crack instantly), quartiles 1.1×/3.6×, extremes 0.66×–253×. Five rows were slower under the tuned ordering, worst by ~3k nodes. Difficulty is *reordered* — the conclusion the 250× result already forced — and the reordering favors exactly the deep bins.
- **A curious cluster**: eight hard rows (`ms622`–`ms625`, `ms636`–`ms639`) all solve within 25 nodes of 62,510. Independent searches landing that close means their state spaces are near-isomorphic (aut-related structure cracking at the same depth of the same climb), not an artifact of the runner.

## What this means for the 124 campaign — the gate resolves to FIRE

The campaign gate asked whether budget keeps converting to solves at scale. Answer, on the rows with headroom: yes, with a hump-band multiplier of **3.4×–23×**. The 124 are the classes the baseline could not solve at 10⁷ nodes; a tuned run at 10⁶ probes a baseline-equivalent ~3.4M–23M, and at 3×10⁶ (feasible under `hcompact`'s ~78 B/state) a baseline-equivalent ~10M–70M — **beyond the regime known to fail** at the range's midpoint and above. The honest prior for solves stays low (the 124 also resisted every ordering at 10³, and the bin-8 parity rows show the multiplier can be ~1×), but this is the first probe of a genuinely new region rather than a slower replay of a failed one.

Two operational facts from the run, folded into [SCALE_RUN_PLAN](../SCALE_RUN_PLAN.md): the user's VM sustained ~170–820 nodes/s on the full-burn rows (state-size dependent; budget hours from ~200/s, not the earlier 700/s guess), and **the baseline arm is retired from all future runs** — its results to 10⁶ exist row-for-row in `nodes_1M`, so re-running it purchases nothing (user directive).
