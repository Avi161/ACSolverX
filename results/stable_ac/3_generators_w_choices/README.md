# 3-generator `z=w` stable-AC greedy sweep — results

Greedy GS-Sub results for the **3-generator** stable-AC experiment: each balanced presentation is
stabilized by adding a third generator `z` and a relator `z = w`, then trivialized by the same greedy
substitution search as the 2-gen baseline. The four **arms** are the choice of the dumb word `w`:

| arm | `w` (the added relator `z = w`) |
|-----|---------------------------------|
| `r1` | relator 1 of the presentation |
| `r2` | relator 2 of the presentation |
| `x`  | generator `x` |
| `y`  | generator `y` |

Produced by `experiments/stable_ac/one_generator/run_greedy_sweep.py` (driver:
`run_greedy_sweep.ipynb`) at a **500k node budget**. Records use the `calibrate_probe.probe` schema;
the canonical identity of a record is `(dataset, idx, arm, budget_nodes)`. Every file is a single
budget (500k) and is **sorted ascending by `idx`** (unique idx per file).

## Layout — split by dataset, one file per relator (arm)

```
ms640/                     # the 640 solved MS(1190) presentations (this sweep)
  runs/  calibration_<arm>.jsonl   # per-idx run record: solved AND unsolved rows together
  paths/ paths_<arm>.jsonl         # replayable move+state path, one per SOLVED idx
ms_reps_unsolved/          # older run over the 261 hard MS reps (preserved; runs-only)
  runs/  calibration_<arm>.jsonl
```

`runs/` (formerly `solved/`) holds **every idx tested** — each row carries `"solved": true|false` and
`"exhausted_budget"`, so one file is the full picture for that relator, solved and unsolved together.
`paths/` holds only solved idx (a path exists only for a solve).

## `ms640/` — solved counts @ 500k (dataset `1190MS`, the 640-set)

| arm | solved | exhausted | of |
|-----|-------:|----------:|---:|
| `r1` | 619 | 21 | 640 |
| `r2` | 602 | 38 | 640 |
| `x`  | 540 | 100 | 640 |
| `y`  | 523 | 117 | 640 |

Each `runs/calibration_<arm>.jsonl` is exactly 640 rows (idx `0..639`); `paths/paths_<arm>.jsonl` has
one row per solved idx.

## `ms_reps_unsolved/` — older 261-reps run

`runs/calibration_<arm>.jsonl` only, 261 rows each (idx `0..260`), 0 solved — these are the hard reps.
No paths file (no solves to record). Preserved from the pre-existing folder; not part of the 640-set
deliverable.

## Provenance & reproduce

- Streams are written **append-only, crash-safe, resumable** by the sweep (`append + flush + fsync`,
  skip idx already recorded for a `(dataset, arm, budget)`); the files here have since been deduped,
  filtered to 500k, and sorted by idx for the archive.
- Merge/compare across arms and datasets by keying on `(dataset, idx, arm, budget_nodes)`.
- Regenerate / extend:
  `python experiments/stable_ac/one_generator/run_greedy_sweep.py --arms r1,r2,x,y --budget 500000 --end 640 --out_dir <dir>`
  The sweep emits `<dir>/solved/calibration_<arm>.jsonl` + `<dir>/paths/paths_<arm>.jsonl`; fold the
  `solved/` stream into `ms640/runs/` (rename `solved/`→`runs/`) and `paths/` into `ms640/paths/`,
  keyed by the identity above (fresh-wins on collision), then re-sort by idx.
