# COLAB_RECOMMENDATION — 5× High-RAM (≈51 GB) sessions

Generated: `2026-07-29T16:12:48.814709+00:00` after 10h mini-research wall.

## What to run

Open **five** notebooks (one Colab High-RAM runtime each):

| session | notebook | `CHUNK_INDEX` |
|---:|---|---:|
| 1 | `experiments/heuristic_search/hsearch_colab_5x51_c1.ipynb` | **1** |
| 2 | `experiments/heuristic_search/hsearch_colab_5x51_c2.ipynb` | **2** |
| 3 | `experiments/heuristic_search/hsearch_colab_5x51_c3.ipynb` | **3** |
| 4 | `experiments/heuristic_search/hsearch_colab_5x51_c4.ipynb` | **4** |
| 5 | `experiments/heuristic_search/hsearch_colab_5x51_c5.ipynb` | **5** |

All five share `CHUNKS=5`, same `ARMS` / `NODE_BUDGET`. Stride sharding is result-neutral; merge jsonls after (concat is fine — rows keyed by `(arm, name)`).

## Frozen CONFIG (edit only `CHUNK_INDEX` per session — already set)

```python
ARMS      = ['baseline', 's12', 's28', 'recommended']
DATASET   = "unsolved124"   # primary target; also run bench66 if time
NODE_BUDGET = 200_000
CHECKPOINTS = [1000, 5000, 10000, 25000, 50000, 100000, 200000]
MAX_RELATOR_LENGTH = 64     # EXP-12 parity on the 124
ENGINE    = "hcompact"      # REQUIRED for multi-worker @ this RAM
KEEP_PATH = True
N_WORKERS = "auto"          # memory-capped; expect ~6 on 51 GB @200k
CHUNKS    = 5
RESUME    = True
```

## Why these arms / budget

- Primary S-arm from fresh_hard @10k: **`s12`** (scores={'length': (36, 0, 60), 's12': (43, 24, 60), 's20': (43, 21, 60), 'recommended': (31, 12, 60)}).
- Extra L-slice @10k: {'k8': (70, 58, 80), 'mk8': (75, 66, 80), 's16': (75, 68, 80), 's20_k2': (75, 67, 80), 's20_neg_xy': (75, 69, 80), 's28': (76, 68, 80), 's8': (75, 69, 80)}.
- Secondary S (if any): `s28`.
- `recommended` kept as different-family control (not another S weight).
- `baseline` = length-only control.
- Budget **200_000**: sized for ~10–20 h wall × 5 sessions × ~6 workers using EXP-28 Colab pops/s (~400–650), not this host's rates.
- Per search RAM @200k hcompact ≪ 51 GB; workers are core/memory auto-capped.

## High-speedup checklist (already in the notebooks)

- `ENGINE=hcompact` (~78 B/state)
- spawn workers + parent-only jsonl writes + local stage + Drive whole-file mirror
- flock on stage (no double-compute on Restart)
- time-based heartbeat
- Drive path under `/content/drive/MyDrive/...` only

## After all five finish

Copy the five `*.jsonl` from Drive into one folder and:

```bash
python3 -m experiments.heuristic_search.runners.merge_colab_chunks \
  --glob 'hsearch_colab5_c*of5_*.jsonl' --out merged_colab5.jsonl
```

Hand the merged file (+ per-chunk files) back into the repo under `results/hsearch/`.

## AK(3) note

AK3 proofs-inspired mini-runs did **not** produce a solve or minL<13 at ≤10k. Do **not** burn the 5×51GB fleet on AK3 until a scout shows dynamic range; keep this fleet on `unsolved124` / hard AC1M if extended.

