# unsolved124 × `s20_mk2` @ 1M / mrl 64

**Non-comparative census** (single arm, no baseline A/B). Aut-min 124 class
reps as starts (unchanged). Arm = **`s20_mk2 = L+20S+2MK`**. Heap depth
tie-break = shipped **`+depth`** (shallowest-first). Cap 64 is per-relator
(incomplete at the length ceiling). “Unsolved” means unsolved within 1M / cap
64 — never a counterexample.

## What to open (4 Colabs)

| Notebook | Chunk | Presentations |
|---|---:|---:|
| [`experiments/heuristic_search/hsearch_colab_u124_s20mk2_1m_c1.ipynb`](../../experiments/heuristic_search/hsearch_colab_u124_s20mk2_1m_c1.ipynb) | 1 | 31 |
| [`experiments/heuristic_search/hsearch_colab_u124_s20mk2_1m_c2.ipynb`](../../experiments/heuristic_search/hsearch_colab_u124_s20mk2_1m_c2.ipynb) | 2 | 31 |
| [`experiments/heuristic_search/hsearch_colab_u124_s20mk2_1m_c3.ipynb`](../../experiments/heuristic_search/hsearch_colab_u124_s20mk2_1m_c3.ipynb) | 3 | 31 |
| [`experiments/heuristic_search/hsearch_colab_u124_s20mk2_1m_c4.ipynb`](../../experiments/heuristic_search/hsearch_colab_u124_s20mk2_1m_c4.ipynb) | 4 | 31 |

**GitHub branch:** `cursor/heur-u124-s20mk2-a42e`

**Drive output dir (each notebook writes here):**  
`/content/drive/MyDrive/acsolverx/hsearch_u124_s20mk2_1m/`

**Per-chunk jsonl:**  
`hsearch_u124_s20mk2_c{K}of4_unsolved124_b1000000_mrl64.jsonl`

## How to run

1. Open each notebook from GitHub on branch `cursor/heur-u124-s20mk2-a42e` (four separate Colab runtimes).
2. **Runtime → Run all** on each. Resume-safe: Restart → Run all continues.
3. Leave each session up until the final Drive mirror finishes.

## After all four finish — merge + verify

```bash
PYTHONPATH=. python3 -m experiments.heuristic_search.runners.merge_colab_chunks \
  --dir /content/drive/MyDrive/acsolverx/hsearch_u124_s20mk2_1m \
  --glob 'hsearch_u124_s20mk2_c*of4_unsolved124_b1000000_mrl64.jsonl' \
  --out /content/drive/MyDrive/acsolverx/hsearch_u124_s20mk2_1m/merged_u124_s20mk2_b1m_mrl64.jsonl

PYTHONPATH=. python3 -m experiments.heuristic_search.verify.verify_u124_s20mk2 \
  --expect-n 124 \
  /content/drive/MyDrive/acsolverx/hsearch_u124_s20mk2_1m/merged_u124_s20mk2_b1m_mrl64.jsonl
```

## Jsonl keys

`arm`, `name`, `dataset`, `budget`, `mrl`, `engine`, `depth_tie`,
`r1`, `r2`, `start_total`,
`solved`, `solved_at`, `nodes_explored`, `path_length`,
`min_relator_length`, `min_relator`, `min_delta`, `improved`,
`max_relator_length_expanded`, `path_moves`, `path_pending`, `secs`

- `start_total = |r1|+|r2|` of the Aut-min start
- `min_relator` = concrete pair achieving `min_relator_length`
- `min_delta = start_total - min_relator_length`
- `improved = min_delta > 0` ← primary interest
- `path_pending` = solved but certificate recovery failed (row still kept)

μ-ladder “36/124 descenders” uses Aut-orbit floor μ — different ruler from
greedy `min_relator_length`.

## Runner

`experiments/heuristic_search/runners/run_unsolved124_s20mk2.py`
