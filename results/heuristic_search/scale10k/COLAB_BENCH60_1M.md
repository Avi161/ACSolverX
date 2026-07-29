# Colab: bench60 ladder @ 1M — HIGH_SPEEDUP

Branch: **`cursor/heur-12h-anti-overfit-a42e`**

## HIGH_SPEEDUP (this stack)

There is **no** `HIGH_SPEEDUP=True` boolean here (that flag is `greedy_baseline` only).
The same path is:

```python
ENGINE    = "hcompact"   # REQUIRED at 1M
N_WORKERS = "auto"       # min(cores, floor((MemAvailable-2)/GB_per_search))
```

On ~51 GB / 8-core Colab at budget 1M / mrl48: **~6 workers** (7.6 GB/search) —
memory-capped from 8 so total stays under ~50 GB. Do not pin `N_WORKERS=8` at 1M.

### Mini verification (budget 1000, hard unsolved124×8 × 5 arms = 40 jobs)

| mode | workers | wall | 
|---|---:|---:|
| serial | 1 | 17.22 s |
| parallel auto | 4 | 6.06 s |
| **speedup** | | **2.84×** (71% of ideal 4×) |

Result-neutral: 0/40 mismatches. Ideal Colab bound at 1M ≈ **6×** (6 workers).

## Notebooks

| # | file | CHUNK_INDEX |
|---:|---|---:|
| 1 | `experiments/heuristic_search/hsearch_colab_bench60_1m_c1.ipynb` | 1 |
| 2 | `experiments/heuristic_search/hsearch_colab_bench60_1m_c2.ipynb` | 2 |
| 3 | `experiments/heuristic_search/hsearch_colab_bench60_1m_c3.ipynb` | 3 |
| 4 | `experiments/heuristic_search/hsearch_colab_bench60_1m_c4.ipynb` | 4 |
| 5 | `experiments/heuristic_search/hsearch_colab_bench60_1m_c5.ipynb` | 5 |

```python
DATASET / SUBSET = bench66 / 60
ARMS = ['baseline', 's12', 's28', 's20_mk2', 's24_k1_mk2']
NODE_BUDGET = 1_000_000
ENGINE = hcompact ; N_WORKERS = auto
```

Drive: `/content/drive/MyDrive/acsolverx/hsearch_bench60_1m/`
