# Colab: AC19_extended Aut-min difficulty screen @ budget 1,000

Branch: **`cursor/heur-12h-anti-overfit-a42e`**

## What it runs

| | |
|---|---|
| Dataset | `data/AC19_extended_aut_min.csv` — **72,779** Aut(F₂) orbits |
| Arms | `baseline` (length / HIGH_SPEEDUP hcompact) · `s20_mk2` (L+20S+2MK) |
| Budget | **1,000** nodes · cap 48 · `KEEP_PATH=False` |
| Engine | `hcompact` + `N_WORKERS="auto"` |

## Notebooks (5 chunks, run in parallel)

| # | file | CHUNK_INDEX |
|---:|---|---:|
| 1 | `experiments/heuristic_search/hsearch_colab_ac19_autmin_1k_c1.ipynb` | 1 |
| 2 | `experiments/heuristic_search/hsearch_colab_ac19_autmin_1k_c2.ipynb` | 2 |
| 3 | `experiments/heuristic_search/hsearch_colab_ac19_autmin_1k_c3.ipynb` | 3 |
| 4 | `experiments/heuristic_search/hsearch_colab_ac19_autmin_1k_c4.ipynb` | 4 |
| 5 | `experiments/heuristic_search/hsearch_colab_ac19_autmin_1k_c5.ipynb` | 5 |

Drive: `/content/drive/MyDrive/acsolverx/hsearch_ac19_autmin_1k/`

Stride sharding: chunk *k* gets rows where `i % 5 == k-1` (~14,556 orbits × 2 arms ≈ **29k searches** / notebook).

## Realistic wall time

Local rate samples @ budget 1k / hcompact / `keep_path=False`:

| slice | rate (serial) |
|---|---:|
| random / mid-length | ~35–60 searches/s |
| longest μ tail | ~3.4 searches/s |

Weighted over the 72,779 orbits (mostly μ≤19):

| setup | estimate |
|---|---|
| 1× Colab, 8 workers, ~50% pool efficiency | **~20–40 min** for the full set |
| **5 Colabs in parallel** (recommended) | **~10–25 min** wall |
| conservative (Drive I/O + hard tail) | budget **30–45 min** wall with 5 sessions |

Most orbits are short and solve early; the L>19 tail (~5.6k orbits) dominates the clock.

## After the run

Merge the five chunk jsonls, then compare anytime curves (`baseline` vs `s20_mk2`) on complete rows only. Difficulty bins = length-baseline `solved_at` (unsolved censored at 1000).
