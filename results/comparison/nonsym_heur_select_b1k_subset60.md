# Nonsym CoV × RECOMMENDED priority → greedy @1k (bench60)

One hop only (fair cost): Aut-min parent → all non-automorphic CoVs (`n_subs>1` + orbit moved) → Aut-min each child → pick min RECOMMENDED start priority → length-greedy / RECOMMENDED @1000.

Shipped controls from `/workspace/results/comparison/cov_heur_b1k_subset60.csv` (not re-run).

## Solve rates @ budget 1000

| arm | start | search | solved |
|---|---|---|---:|
| `b1k_greedy` (shipped) | original | length | **29**/60 |
| `b1k_heur` (shipped) | original | RECOMMENDED | **43**/60 |
| `b1k_covgreedy` (shipped oracle) | best-of-all-CoV | length | **45**/60 |
| `nonsym_mumin` | lowest-μ nonsym Aut-min | length | **39**/60 |
| **`nonsym_heur`** | min RECOMMENDED prio nonsym Aut-min | length | **42**/60 |
| **`nonsym_heur_h`** | same start | RECOMMENDED | **43**/60 |

- Heur selector = μ-min selector on **47/60** rows (fallback to Aut-min original: 1).
- `nonsym_heur` vs `b1k_greedy`: new ['609', '538', '606', '544', '549', '543', '565', '602', '586', '581', '575', '628', '633']; lost —.
- `nonsym_heur` vs oracle `b1k_covgreedy`: new — (0).
- `nonsym_heur` vs `nonsym_mumin`: beats μ-pick on ['609', '538', '543', '602']; loses on ['632'].

Not comparable to the pure uncapped μ-beam's 50/60 μ≤12 leads (different finish line, multi-hop, no greedy).

Wall 41.9s. Artifacts: `nonsym_heur_select_b1k_subset60.*`.
