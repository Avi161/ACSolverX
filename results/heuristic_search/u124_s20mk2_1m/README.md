# unsolved124 × `s20_mk2` @ 1M / mrl 64 (CoV-reduced starts)

**Non-comparative census** (single arm, no baseline A/B). Same 124 `aca_*`
ids as original aca124. **Search starts = μ-ladder `best_rep`**: the 36 CoV
descenders begin at their shorter Aut-orbit floor witness; the other 88 keep
Aut-min (identical to `best_rep`). Arm = **`s20_mk2 = L+20S+2MK`**. Heap depth
tie-break = shipped **`+depth`**. Cap 64 is per-relator (incomplete at the
length ceiling). “Unsolved” means unsolved within 1M / cap 64 — never a
counterexample.

Ladder source:
`results/stable_ac/mu_scan/mu_ladder_big_aca124_r256_b64_mrl24.jsonl`

## What to open (4 Colabs)

| Notebook | Chunk | Presentations |
|---|---:|---:|
| [`experiments/heuristic_search/hsearch_colab_u124_s20mk2_1m_c1.ipynb`](../../experiments/heuristic_search/hsearch_colab_u124_s20mk2_1m_c1.ipynb) | 1 | 31 |
| [`experiments/heuristic_search/hsearch_colab_u124_s20mk2_1m_c2.ipynb`](../../experiments/heuristic_search/hsearch_colab_u124_s20mk2_1m_c2.ipynb) | 2 | 31 |
| [`experiments/heuristic_search/hsearch_colab_u124_s20mk2_1m_c3.ipynb`](../../experiments/heuristic_search/hsearch_colab_u124_s20mk2_1m_c3.ipynb) | 3 | 31 |
| [`experiments/heuristic_search/hsearch_colab_u124_s20mk2_1m_c4.ipynb`](../../experiments/heuristic_search/hsearch_colab_u124_s20mk2_1m_c4.ipynb) | 4 | 31 |

**GitHub branch:** `cursor/heur-u124-s20mk2-a42e`

**Drive output dir (each notebook writes here):**  
`/content/drive/MyDrive/acsolverx/hsearch_u124_s20mk2_covstart_1m/`

**Per-chunk jsonl:**  
`hsearch_u124_s20mk2_covstart_c{K}of4_dpos_covstart_unsolved124_b1000000_mrl64.jsonl`  
(or `…_dpos_covstart_…` if `OUT_STEM` already contains `covstart` once — the
runner always stamps `covstart` so a stale CONFIG cell cannot resume Aut-min
jsonls).

## How to run (including already-open notebooks)

1. Open each notebook from GitHub on branch `cursor/heur-u124-s20mk2-a42e`
   (four separate Colab runtimes) — **or**, if already open:
2. **Runtime → Restart session → Run all**. SETUP does
   `git fetch` + `reset --hard` + `sys.modules` purge, so the CoV-start
   runner lands without re-opening the file. The runner forces a `covstart`
   filename tag even if CONFIG’s `OUT_STEM` is still the old Aut-min stem.
3. Confirm the RUN log prints
   `starts: μ-ladder best_rep (… CoV-reduced, … Aut-min unchanged) [tag=covstart]`
   and the jsonl path contains `covstart`.
4. Leave each session up until the final Drive mirror finishes.

## After all four finish — merge + verify

```bash
PYTHONPATH=. python3 -m experiments.heuristic_search.runners.merge_colab_chunks \
  --dir /content/drive/MyDrive/acsolverx/hsearch_u124_s20mk2_covstart_1m \
  --glob '*covstart*unsolved124_b1000000_mrl64.jsonl' \
  --out /content/drive/MyDrive/acsolverx/hsearch_u124_s20mk2_covstart_1m/merged_u124_s20mk2_covstart_b1m_mrl64.jsonl

PYTHONPATH=. python3 -m experiments.heuristic_search.verify.verify_u124_s20mk2 \
  --expect-n 124 \
  /content/drive/MyDrive/acsolverx/hsearch_u124_s20mk2_covstart_1m/merged_u124_s20mk2_covstart_b1m_mrl64.jsonl
```

## Jsonl keys

`arm`, `name`, `dataset`, `budget`, `mrl`, `engine`, `depth_tie`,
`start_source`, `cov_reduced`, `mu_in`, `best_mu`, `r1_autmin`, `r2_autmin`,
`r1`, `r2`, `start_total`,
`solved`, `solved_at`, `nodes_explored`, `path_length`,
`min_relator_length`, `min_relator`, `min_delta`, `improved`,
`max_relator_length_expanded`, `path_moves`, `path_pending`, `secs`

- `r1`,`r2` = search start (= μ-ladder `best_rep`)
- `r1_autmin`,`r2_autmin` = freeze Aut-min (pre-CoV)
- `cov_reduced` = true for the 36 descenders
- `start_total = |r1|+|r2|` of the **CoV start** (not Aut-min)
- `min_relator` = concrete pair achieving `min_relator_length` (solver-reported
  discovery witness; **no move path to that pair is stored**)
- `min_delta = start_total - min_relator_length`
- `improved = min_delta > 0` ← primary interest

## Heartbeat (60 s)

Each in-search beat prints nodes/s **and** the presentation's current
`min_relator_length` vs start. If the floor fell since the previous beat the
line ends with `DROP -k`; otherwise `(no drop)`.

## Runner

`experiments/heuristic_search/runners/run_unsolved124_s20mk2.py`
