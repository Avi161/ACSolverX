# Colab: bench60 ladder @ 1M — 5 arms HIGH_SPEEDUP

Branch: **`cursor/heur-12h-anti-overfit-a42e`**

Difficulty-stratified **benchmark_subset_60** (first 60 of `bench66` = ladder only).
Baseline greedy @1M already lives in `benchmark/`; this run is the 5-arm A/B.

## Open these five (one High-RAM Colab each)

| session | notebook | chunk |
|---:|---|---:|
| 1 | `experiments/heuristic_search/hsearch_colab_bench60_1m_c1.ipynb` | 1 |
| 2 | `experiments/heuristic_search/hsearch_colab_bench60_1m_c2.ipynb` | 2 |
| 3 | `experiments/heuristic_search/hsearch_colab_bench60_1m_c3.ipynb` | 3 |
| 4 | `experiments/heuristic_search/hsearch_colab_bench60_1m_c4.ipynb` | 4 |
| 5 | `experiments/heuristic_search/hsearch_colab_bench60_1m_c5.ipynb` | 5 |

Runtime → Run all. Restart → Run all resumes.

## CONFIG (same in all five; only `CHUNK_INDEX` differs)

```python
BRANCH    = "cursor/heur-12h-anti-overfit-a42e"
DATASET   = "bench66"
SUBSET    = 60                          # ladder only (6 per log-bin)
ARMS      = ['baseline', 's12', 's28', 's20_mk2', 's24_k1_mk2']
NODE_BUDGET = 1_000_000
MAX_RELATOR_LENGTH = 48
ENGINE    = "hcompact"
N_WORKERS = "auto"
CHUNKS    = 5
KEEP_PATH = True
RESUME    = True
```

- **baseline** = length-only greedy (mandatory comparison column)
- **s12 / s28** = pure-S
- **s20_mk2 / s24_k1_mk2** = interim Aut-tune S+MK and S+K+MK (no xyimb)
- Drive out: `/content/drive/MyDrive/acsolverx/hsearch_bench60_1m/`

## Merge after all five finish

```bash
python3 -m experiments.heuristic_search.runners.merge_colab_chunks \
  --glob 'hsearch_bench60_1m_c*of5_*.jsonl' --out merged_bench60_1m.jsonl
```

Report every arm as solved/N **and Δ vs baseline** at each checkpoint.
