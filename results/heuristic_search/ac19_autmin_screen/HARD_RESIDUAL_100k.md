# Hard residual after budget 10k → Colab @ 100k

## 4 parallel Colabs (one arm each — own 10k failures)

Open each notebook, Runtime → Run All. Separate Drive dirs; can run together.

| # | notebook | arm | CSV | n | Drive |
|---:|---|---|---|---:|---|
| 1 | [`hsearch_colab_ac19_hard100k_baseline.ipynb`](../../experiments/heuristic_search/hsearch_colab_ac19_hard100k_baseline.ipynb) | `baseline` | [`unsolved_10k_baseline.csv`](unsolved_10k_baseline.csv) | 831 | `…/hsearch_ac19_hard100k_baseline` |
| 2 | [`hsearch_colab_ac19_hard100k_s20_mk2.ipynb`](../../experiments/heuristic_search/hsearch_colab_ac19_hard100k_s20_mk2.ipynb) | `s20_mk2` | [`unsolved_10k_s20_mk2.csv`](unsolved_10k_s20_mk2.csv) | 259 | `…/hsearch_ac19_hard100k_s20_mk2` |
| 3 | [`hsearch_colab_ac19_hard100k_s20_mk2_mK2.ipynb`](../../experiments/heuristic_search/hsearch_colab_ac19_hard100k_s20_mk2_mK2.ipynb) | `s20_mk2_mK2` | [`unsolved_10k_s20_mk2_mK2.csv`](unsolved_10k_s20_mk2_mK2.csv) | 507 | `…/hsearch_ac19_hard100k_s20_mk2_mK2` |
| 4 | [`hsearch_colab_ac19_hard100k_s20_f4.ipynb`](../../experiments/heuristic_search/hsearch_colab_ac19_hard100k_s20_f4.ipynb) | `s20_f4` | [`unsolved_10k_s20_f4.csv`](unsolved_10k_s20_f4.csv) | 753 | `…/hsearch_ac19_hard100k_s20_f4` |

Budget **100,000**, cap 48, `RESUME=True`. Each notebook asserts its CSV row count so a stale clone fails loudly.

These answer: *of the presentations this arm missed @10k, how many does it solve @100k?*  
They are **not** a cross-arm ranking on the same hard set.

## Union Colab (cross-arm hard-tail A/B)

[`hsearch_colab_ac19_hard100k.ipynb`](../../experiments/heuristic_search/hsearch_colab_ac19_hard100k.ipynb)  
→ [`hard_residual_10k_union.csv`](hard_residual_10k_union.csv) (**1183**) × all 4 arms = **4732** searches.

Use this when you want *which arm wins on the hard residual* (common denominator).

| arm | unsolved @10k (own) |
|---|---:|
| `baseline` | 831 |
| `s20_mk2` | 259 |
| `s20_mk2_mK2` | 507 |
| `s20_f4` | 753 |
| **union (any fail)** | **1183** |

Coverage: every per-arm unsolved name ⊆ union (asserted).

## Optional gap fill (not hard)

[`gap_fill_10k.csv`](gap_fill_10k.csv) — 3514 incomplete/never-run with no recorded failure. Do not mix into hard-tail headlines.
