# COLAB_RECOMMENDATION — 5× High-RAM (≈51 GB) sessions

Updated: `2026-07-29T17:54:00+00:00` — **no recommended / no xyimb**.

Arm mix finalized after Aut-disjoint `skmk_aut_tune` (in progress — see
[`../skmk_aut_tune/PROGRESS.md`](../skmk_aut_tune/PROGRESS.md)). Until that
holdout read lands, notebooks ship the interim S-only shortlist below.

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
ARMS      = ['baseline', 's12', 's28']  # + best S+K / S+MK / S+K+MK from skmk_aut_tune
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

**`baseline` (length-only greedy) is mandatory** — every treatment arm is
reported as solved/N **and** Δ vs baseline at the same budget. Without that
column we cannot say better/worse. Do not drop it to free a Colab slot.

**Do not add `recommended` / xyimb** — overfits; weight selection is S+K+MK only
on Aut-disjoint train/holdout (`results/heuristic_search/splits/splits_ac1m_hard_aut.json`).

## Why these arms / budget

- Primary S-arm from fresh_hard @10k: **`s12`** (tied with s20 at 43/60; cheaper).
- Secondary S: `s28` (L-slice winner among pure-S at 10k).
- Mix arms: **pending** Aut-disjoint 336-cell @1k (`skmk_aut_tune`) — select on train 120, one holdout read on 60. Contaminated `skmk_tune`/`skmk_mix` (idx-prefix, Aut leakage) are **not** used for selection.
- `baseline` = length-only control.
- Budget **200_000**: sized for ~10–20 h wall × 5 sessions × ~6 workers using EXP-28 Colab pops/s (~400–650), not this host's rates.

## High-speedup checklist (already in the notebooks)

- `ENGINE=hcompact` (~78 B/state) — numba
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
