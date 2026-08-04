# unsolved124 × `s20_mk2` @ 1M / mrl 64 (CoV-reduced starts)

**Non-comparative census** (single arm, no baseline A/B). Same 124 `aca_*`
ids as original aca124. **Search starts = μ-ladder `best_rep`**: the 36 CoV
descenders begin at their shorter Aut-orbit floor witness; the other 88 keep
Aut-min (identical to `best_rep`). Arm = **`s20_mk2 = L+20S+2MK`**. Heap depth
tie-break = shipped **`+depth`**. Cap 64 is per-relator (incomplete at the
length ceiling). “Unsolved” means unsolved within 1M / cap 64 — never a
counterexample.

A **solve** certifies the class **stably** AC-trivial (Prop A CoV chain +
`PROOFS.tex` Thm 3 `aut_canon` + replayed AC path) — never AC-trivial
unqualified (`MU_CRITERION.md` item 7).

Ladder source:
`results/stable_ac/mu_scan/mu_ladder_big_aca124_r256_b64_mrl24.jsonl`
(identity tag `covstart_r256b64m24`).

## What to open (4 Colabs)

| Notebook | Chunk | Presentations | CoV-reduced |
|---|---:|---:|---:|
| [`…_c1.ipynb`](../../experiments/heuristic_search/hsearch_colab_u124_s20mk2_1m_c1.ipynb) | 1 | 31 | 9 |
| [`…_c2.ipynb`](../../experiments/heuristic_search/hsearch_colab_u124_s20mk2_1m_c2.ipynb) | 2 | 31 | 7 |
| [`…_c3.ipynb`](../../experiments/heuristic_search/hsearch_colab_u124_s20mk2_1m_c3.ipynb) | 3 | 31 | 10 |
| [`…_c4.ipynb`](../../experiments/heuristic_search/hsearch_colab_u124_s20mk2_1m_c4.ipynb) | 4 | 31 | 10 |

**GitHub branch:** `cursor/heur-u124-s20mk2-a42e`

**Drive output dir:**  
`/content/drive/MyDrive/acsolverx/hsearch_u124_s20mk2_covstart_1m/`

(The runner **redirects** the old Aut-min Drive path to this one if a stale
CONFIG cell still has it.)

**Per-chunk jsonl (default OUT_STEM):**  
`hsearch_u124_s20mk2_covstart_r256b64m24_c{K}of4_dpos_unsolved124_b1000000_mrl64.jsonl`

## How to run (including already-open notebooks)

1. Open each notebook from GitHub on `cursor/heur-u124-s20mk2-a42e`, **or** if
   already open: **Runtime → Restart session → Run all**.
2. SETUP does `git fetch` + `reset --hard` + `sys.modules` purge.
3. Confirm RUN log:
   `starts: μ-ladder best_rep (… CoV-reduced …) [tag=covstart_r256b64m24]`
   and the jsonl path contains that tag (and lands under the covstart Drive dir).
4. Leave each session up until the Drive mirror finishes.

## After all four finish — merge + verify

```bash
PYTHONPATH=. python3 -m experiments.heuristic_search.runners.merge_colab_chunks \
  --dir /content/drive/MyDrive/acsolverx/hsearch_u124_s20mk2_covstart_1m \
  --dir /content/drive/MyDrive/acsolverx/hsearch_u124_s20mk2_1m \
  --glob '*covstart*unsolved124_b1000000_mrl64.jsonl' \
  --out /content/drive/MyDrive/acsolverx/hsearch_u124_s20mk2_covstart_1m/merged_u124_s20mk2_covstart_b1m_mrl64.jsonl

PYTHONPATH=. python3 -m experiments.heuristic_search.verify.verify_u124_s20mk2 \
  --expect-n 124 \
  /content/drive/MyDrive/acsolverx/hsearch_u124_s20mk2_covstart_1m/merged_u124_s20mk2_covstart_b1m_mrl64.jsonl

# Independent best_rep chain replay (no orbits dump needed; ~15 s):
PYTHONPATH=. python3 -m experiments.heuristic_search.verify.verify_cov_best_rep_chains
```

`--expect-n 124` is **mandatory** after merge (unique names + no duplicate rows).

## Jsonl keys

`arm`, `name`, `dataset`, `budget`, `mrl`, `engine`, `depth_tie`, `ladder_id`,
`start_source`, `cov_reduced`, `mu_in`, `best_mu`, `r1_autmin`, `r2_autmin`,
`r1`, `r2`, `start_total`,
`solved`, `solved_at`, `nodes_explored`, `path_length`,
`min_relator_length`, `min_relator`, `min_delta`, `improved`,
`mu_min`, `mu_min_rep`,
`max_relator_length_expanded`, `path_moves`, `path_pending`, `secs`

- `r1`,`r2` = search start (= μ-ladder `best_rep`)
- `mu_min` = `aut_canon(|min_relator|)` — orbit floor of the greedy witness
- `improved` compares raw pair-total to the CoV start (blind to same-length
  orbit switches; use `mu_min` for that)
- Late solves (`solved_at > 250k`) stay `path_pending` (in-parent recovery
  deferred to avoid Colab OOM)

## Runner

`experiments/heuristic_search/runners/run_unsolved124_s20mk2.py`
