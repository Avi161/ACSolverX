# Colab: AC19_extended Aut-min difficulty screen @ budget 1,000

Branch: **`cursor/heur-12h-anti-overfit-a42e`**

**ac-advisor:** REVISE caveats still apply (Aut-min reps, stratify L>19, exclude 142 selection overlaps in write-up).

## What it runs

| | |
|---|---|
| Dataset | `data/AC19_extended_aut_min.csv` — **72,779 Aut-minimal representatives** |
| Arms | `baseline` · `s20_mk2` · `s28` · `s28_mk2_f8` |
| Budget | **1,000** nodes · cap 48 |
| Engine | `hcompact` + `N_WORKERS="auto"`; **F arm** via `search_signlag` |

No `s12`, no `s24_k1_mk2`.

## Notebooks (5 chunks, run in parallel)

| # | file | CHUNK_INDEX |
|---:|---|---:|
| 1 | `experiments/heuristic_search/hsearch_colab_ac19_autmin_1k_c1.ipynb` | 1 |
| 2 | `experiments/heuristic_search/hsearch_colab_ac19_autmin_1k_c2.ipynb` | 2 |
| 3 | `experiments/heuristic_search/hsearch_colab_ac19_autmin_1k_c3.ipynb` | 3 |
| 4 | `experiments/heuristic_search/hsearch_colab_ac19_autmin_1k_c4.ipynb` | 4 |
| 5 | `experiments/heuristic_search/hsearch_colab_ac19_autmin_1k_c5.ipynb` | 5 |

Drive: `/content/drive/MyDrive/acsolverx/hsearch_ac19_autmin_1k/`

~14,556 reps × **4 arms** ≈ **58k searches** / notebook.

## Realistic wall time (4 arms)

| setup | estimate |
|---|---|
| **5 Colabs in parallel** | **~25–45 min** wall |
| conservative (+ Drive I/O) | budget **~60 min** |
| 1× Colab | ~40–90 min (2 vs 8 vCPU) |

Roughly **2×** the prior 2-arm estimate.

## After the run

Merge five chunk jsonls; report anytime curves stratified by L≤19 / L>19; exclude the 142 selection-overlap names when scoring `s20_mk2` / `s28_mk2_f8`.
