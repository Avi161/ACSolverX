# CoV vs greedy baseline — node-explored comparison

Source: `results/stable_ac/cov/covsweep_100_66_subnc2pxysb_mrl24_cyc_s60r6_07_16_26.jsonl` (66-presentation benchmark, node_budget 100, cap 24). Baseline = the sweep's own control row per presentation (original strings, `z_word: null`, no CoV). "CoV" = every transformed start (relabel *and* moved). Figures: `fig1_composition.png`, `fig2_distribution_correlation.png`. Per-row data: `per_presentation.csv`, `solved_cov_points.csv`.

## Question

Does every change of variables reduce the greedy's `nodes_explored` vs the baseline — i.e. is the reduction *consistent*, or a cherry-picked / random effect?

## Answer: no. It is a difficulty-tracking lottery, not a consistent reduction.

**Solve landscape (66 presentations).** Baseline solves **17/66**; a CoV solves where the baseline could not (a "flip") on **17** more; **32** are never solved by anything. So the node-reduction question is only well-posed on the **17 baseline-solved** presentations (elsewhere the baseline has no finite node count to beat).

**Over those 17 presentations there are 1039 CoV variants. Split vs baseline:**

| outcome | count | share of all CoVs |
|---|---:|---:|
| solved, **fewer** nodes (better) | 359 | **34.6%** |
| solved, equal nodes | 91 | 8.8% |
| solved, **more** nodes (worse) | 381 | 36.7% |
| **did not solve** within 100 nodes (strictly worse) | 208 | 20.0% |

A random CoV reduces nodes only **~35%** of the time; ~65% are neutral-or-worse, and 1 in 5 fails to solve a problem the baseline solved. **In 0 of 17 presentations does *every* CoV beat the baseline.** The **best** CoV beats the baseline in **17/17** — but that is what taking the minimum over 11–143 draws straddling the baseline *is*, not a second finding: the payoff is entirely selection (best-of-many), exactly a restart-with-a-different-representation.

(The pooled percentages are variant-weighted, so a few high-variant presentations dominate them — pres 505 alone is 133 of the 1039 variants at 81% unsolved, and 521+496 add 253 more. The per-presentation bars in `fig1_composition.png` panel C are the honest unit; the conclusion holds there too — every presentation is under 60% "fewer", and 0/17 are all-fewer.)

**Correlation — it is not random noise.** Node counts track the group's intrinsic difficulty: Spearman(baseline nodes, best-CoV nodes) = **+0.92**, Spearman(baseline nodes, median solved-CoV nodes) = **+0.97**. Harder baselines keep harder CoVs; CoV does not erase problem difficulty. And the *chance* a CoV helps rises with how expensive the baseline is: Spearman(baseline nodes, % of CoVs that reduce) = **+0.46** — but this is largely a **floor/headroom effect**, not a causal property of CoV: node counts bottom out at ~2, so a baseline of 3 is nearly unbeatable (a CoV would have to hit exactly 2) while a baseline of 93 leaves huge room below it. Practical takeaway: don't bother applying CoV to cheap-baseline presentations — there is no headroom to win.

## Bottom line

Changing variables does **not** consistently reduce nodes. Per presentation the CoV node counts form a broad distribution centred near or above the baseline, with a good lower tail — so the family works as a cheap **restart mechanism** whose value is realised only by taking the minimum over many CoVs, not by any single change of variables being reliably better.

## Data note (flagged for the doc)

`AUTOMORPHISMS_COV.md` states "the control solves only 47/66" (§"What is not decided here"). Verified against this exact file three ways (by `z_word is null`, by `n_cov==0 & n_subs==0`, by direct `solved` count; all rows are budget 100): the control solves **17/66**, not 47. The internally consistent numbers are control 17 + flips 17 = union 34; nothing in the data equals 47. Likely a 17→47 typo. Recommend correcting that line.
