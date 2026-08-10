# Pure nonsym CoV beam (no greedy, uncapped Aut-min) — bench60

Bias fix: the prior K-sweep charged up to 1000 Whitehead/`aut_min` calls **then** gave greedy another 1000 nodes — that is not a fair comparison to plain greedy@1k. This run drops greedy entirely.

Algorithm: non-automorphic CoV → Aut-min → keep top-K → loop until μ≤12 / closed / rungs=256 (structural backstop only; **no** `max_aut_canon`).

## Success metric

**`hits_stop`** = `best_mu ≤ 12`. That is a *stable*-AC triviality lead (MU_CRITERION / MM03), **not** an AC solve and not comparable to `b1k_covgreedy` node budgets.

## K sweep (uncapped)

| K | hits_stop (μ≤12) | descended | closed (no hit) | rung-cap (no hit) | mean n_aut_canon | max n_aut_canon | wall_s |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | **34**/60 | 53/60 | 18 | 8 | 383.4 | 2130 | 47.9 |
| 2 | **39**/60 | 53/60 | 13 | 8 | 743.4 | 4177 | 95.8 |
| 4 | **47**/60 | 53/60 | 2 | 11 | 1789.9 | 9052 | 186.0 |
| 8 | **50**/60 | 53/60 | 2 | 8 | 3086.4 | 16983 | 296.3 ← best |
| 10 | **50**/60 | 53/60 | 2 | 8 | 3936.7 | 22378 | 419.2 |
| 16 | **50**/60 | 53/60 | 2 | 8 | 6137.3 | 35381 | 621.7 |

**Best K = 8** by hits_stop (50/60), tie-break lower mean Aut-min work.
K=10 and K=16 tie on hits but cost more Aut-min work — plateau.

Open at K=8 (10 rows):
- `closed` (no more nonsym children): `496`, `521` (μ stayed 16 and 18)
- `rungs_exhausted` at 256 (still μ>12): the eight aut-class-106 rows
  `622–625`, `636–639` (best μ 17)

Those eight are the same family that need bestcov @20k for an AC solve.
Raising the rung backstop further is the only lever left for pure CoV;
uncapping Aut-min calls alone already ran them to 256 rungs.

Wall 1666.8s. Artifacts: `covbeam_nonsym_beam_pure_uncapped_subset60.*`.
