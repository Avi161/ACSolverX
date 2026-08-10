# hsearch_bench60_1m — organized results

Pulled tip `349e338`. Merged chunks: **290** rows (expected 300 = 60×5; missing **10** cells).

Comparison denominator: **60** ladder presentations with frozen greedy `nodes_1M`/`path_1M` and all four treatment arms present.

Frozen greedy baseline from `benchmark/subsets/benchmark_subset_60.json` (length-greedy @1M). Colab also re-ran `baseline` under hcompact/mrl48.

## Solve counts

| arm | solved / present |
|---|---:|
| `greedy_baseline` | 60/60 |
| `baseline` | 50/50 |
| `s12` | 60/60 |
| `s28` | 60/60 |
| `s20_mk2` | 60/60 |
| `s24_k1_mk2` | 60/60 |

## Mean / median (solved rows only)

| arm | mean nodes | median nodes | mean path | median path |
|---|---:|---:|---:|---:|
| `greedy_baseline` | 45244.2 | 1310.5 | 142.6 | 46.5 |
| `baseline` | 6265.2 | 418.0 | 75.2 | 32.0 |
| `s12` | 16209.0 | 364.5 | 143.1 | 40.0 |
| `s28` | 16635.6 | 274.0 | 145.2 | 45.5 |
| `s20_mk2` | 4693.8 | 358.5 | 154.3 | 41.5 |
| `s24_k1_mk2` | 7210.9 | 313.0 | 147.9 | 47.0 |

## Figures

- `bench60_1m_nodes_explored.png`
- `bench60_1m_path_length.png`
- `bench60_1m_mean_median.png`

## Missing cells

10 missing `(name, arm)` — sample: `[('ms605', 'baseline'), ('ms610', 'baseline'), ('ms625', 'baseline'), ('ms622', 'baseline'), ('ms634', 'baseline'), ('ms635', 'baseline'), ('ms637', 'baseline'), ('ms639', 'baseline'), ('ms638', 'baseline'), ('ms636', 'baseline')]`

## Speedup vs frozen greedy (nodes ratio arm/greedy)

| arm | geo-mean ratio | median ratio | fraction faster |
|---|---:|---:|---:|
| `s12` | 0.456 | 0.442 | 54/60 |
| `s28` | 0.442 | 0.530 | 50/60 |
| `s20_mk2` | 0.300 | 0.342 | 53/60 |
| `s24_k1_mk2` | 0.349 | 0.359 | 53/60 |

Per-row lowest-nodes winner (greedy + 4 treatments): `{'greedy': 6, 's12': 18, 's28': 7, 's24_k1_mk2': 11, 's20_mk2': 18}`

### Notes
- All four treatments **solved 60/60**. Colab `baseline` finished **50/60** (10 hardest missing); on those 50 it matches frozen greedy exactly (ratio 1.0) — good engine cross-check.
- Path length is **not** improved systematically (often longer). Gain is **node efficiency**, not shorter certificates.
- **s20_mk2** best geo/mean nodes; **s28** best median nodes. Neither dominates every bin — not a single decisive general replacement for length, but **S-family clearly beats length on this ladder**.
