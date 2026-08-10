# COLAB_RECOMMENDATION — INTERIM (pre-wall)

Updated from live scale10k / extra / portfolio before wall end.
**Final stamp runs at `2026-07-29T16:12:20Z` via `finalize_colab_handoff`.**

## Five High-RAM (~51 GB) notebooks

| # | notebook | CHUNK_INDEX |
|---:|---|---:|
| 1 | `experiments/heuristic_search/hsearch_colab_5x51_c1.ipynb` | 1 |
| 2 | `experiments/heuristic_search/hsearch_colab_5x51_c2.ipynb` | 2 |
| 3 | `experiments/heuristic_search/hsearch_colab_5x51_c3.ipynb` | 3 |
| 4 | `experiments/heuristic_search/hsearch_colab_5x51_c4.ipynb` | 4 |
| 5 | `experiments/heuristic_search/hsearch_colab_5x51_c5.ipynb` | 5 |

Shared: `CHUNKS=5`, `ENGINE=hcompact`, `N_WORKERS=auto`, `RESUME=True`,
Drive `/content/drive/MyDrive/acsolverx/hsearch_colab5`.

## Interim CONFIG (likely final)

```python
DATASET   = "unsolved124"
ARMS      = ["baseline", "s12", "s20", "recommended"]  # s28 optional add
NODE_BUDGET = 200_000
MAX_RELATOR_LENGTH = 64
ENGINE = "hcompact"
```

Evidence so far (@10k):

- **fresh_hard 60:** s12=s20=43/60 ≻ length 36 ≻ recommended 31
- **L-stratified 80:** s12=s20=76; extra s28=76 (tie-ish)
- **portfolio:** single s20 20/30 ≻ {12,20,32}@B/3 = 16/30 — **do not split budget**
- **unsolved124:** 0/124 all arms @10k (reach probe; Colab depth is the point)

## After runs

```bash
python3 -m experiments.heuristic_search.runners.merge_colab_chunks \
  --glob 'hsearch_colab5_c*of5_*.jsonl' --out merged_colab5.jsonl
```
