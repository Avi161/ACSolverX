# applied: B1's radius-2 trick on the presentations nothing on record solves

**Question.** `ATLAS.md` shows that on the 28 AC19 orbits plain greedy cannot solve at
10,000,000 pops, `S20_MK2` solves 6/28 from the row as given but 26/28 from some radius-2
`Aut(F2)`-image at <= 20,000 pops.  Does the same trick crack anything that has never been
solved: the 124 unsolved Miller-Schupp classes (both forms), and the two level-9 AC19
orbits the atlas ball missed?  The answer is in `APPLIED.md`; this file is the how.

Git head: `460904f9850ee20e3fe7772704a17db36f44f707` on `claude/ac19-theorem-strength-8v1wp6`
(working tree; nothing committed).  Everything lives in this directory; B1's files
(`orbit.py`, `engine.py`, `features.py`, `atlas.jsonl`) are only read; nothing outside
`research/autchoice_20260910/applied/` was written.

## Files

| file | what it does |
|---|---|
| `common.py` | paths; `search(pair, budget, cap)` = `greedy_search_hcompact` under `S20_MK2` with `track_path=True`, keeping `min_total_length_seen` (the engine's `min_relator_length`) and replaying any claimed solve from the image with `words.replay_move` (`engine.replay`); `make_record` = one `atlas.jsonl`-shaped line plus `orig_r1, orig_r2, start_len, phase, radius`, with `s20.verified` = image replay AND `engine.verify_from_original` from the target's own pair |
| `build_targets.py` -> `targets.csv`, `targets_manifest.json` | the 250 targets (below), input hashes |
| `run_phase1.py` -> `phase1.jsonl`, `phase1_run.json`, `phase1_run.log`, `phase1_rejects.log` | radius-2 ball x `S20_MK2` @ 20,000 on every target; resumable |
| `run_phase2.py` -> `phase2.jsonl`, `phase2_selection.json`, `phase2_ranking.json`, `phase2_run.json`, `phase2_run.log` | radius-3 depth-3 images @ 20,000 and the top-3 images @ 200,000 on the 2 leftovers + the 10 closest aca targets; resumable |
| `verify_applied.py` -> `verify_applied.json` | fresh-process re-check of every claimed solve from the JSONL alone (no engine import) |
| `analyze_applied.py` -> `APPLIED.md`, `applied_summary.json` | every number in the report, computed from the JSONL |

## Targets (`targets.csv`: `name, r1, r2, source, form, note`)

| form | rows | what |
|---|---:|---|
| `aca_initial` | 124 | `aca_N`: the unsolved MS classes as first found (level 10 of `ladder_all.csv`) |
| `ac19_level9_leftover` | 2 | `ac19_27254`, `ac19_7284`: level-9 rows with no solved radius-2 image in `atlas.jsonl` (computed, asserted against `ATLAS.md`) |
| `aca_best` | 124 | `acabest_N`: the same classes, mu-reduced (the u124 probes' form) |

88 of the 124 classes have the identical pair in both forms (`canon_pair` equal), so those
balls coincide; the runner searches each distinct pair once and re-records the (deterministic)
result under every (row, image) that carries it, flagged `s20.shared`.  The per-row
`verify_from_original` is computed for each row from its own pair.  3,238 images, 2,100
distinct searches in phase 1.

## Commands (from the repo root, in this order)

```bash
PYTHONPATH=. python3 -m research.autchoice_20260910.applied.build_targets
OMP_NUM_THREADS=1 NUMBA_NUM_THREADS=1 PYTHONPATH=. python3 -m research.autchoice_20260910.applied.run_phase1 --budget 20000 --workers 3
OMP_NUM_THREADS=1 NUMBA_NUM_THREADS=1 PYTHONPATH=. python3 -m research.autchoice_20260910.applied.run_phase2 --workers 3
PYTHONPATH=. python3 -m research.autchoice_20260910.applied.verify_applied
PYTHONPATH=. python3 -m research.autchoice_20260910.applied.analyze_applied
```

Both runners call `verify_applied.py` in a subprocess when they finish; the standalone call
is the one whose output `verify_applied.json` ships.  `pgrep -fc run_atlas` was 0 before the
start (B1's atlas run had finished); B2's predictor work ran concurrently on the fourth core.

## Timings

__TIMINGS__

## Inputs and their hashes

| input | sha256 |
|---|---|
| `benchmark/ladder/ladder_all.csv` | `c8db8a749d1cd17e25a7deff247a2f807637f98e63274317bf514d0601d2d032` |
| `research/autchoice_20260910/atlas.jsonl` (leftover selection only) | `e162298fbeb4a4aedfebdfa072b9517715c2bfd6cddb383464a7953264687165` |
| `applied/targets.csv` (output of `build_targets.py`) | `c325b0a9111c835a7c5de13d080aca4f2dfe22062c9b3ddd77d97eb593eb98ab` |

## Verification protocol

1. In the worker, `common.search` replays every engine claim from the image through
   `words.replay_move` (pure Python); a claim that does not end on two distinct single
   letters is written with `s20.rejected` and counted as unsolved (`phase*_rejects.log`).
2. In the worker, `engine.verify_from_original(orig_pair, seq, path_moves)` applies the
   `AUTOS` sequence one Whitehead automorphism at a time from the target's own pair and
   replays the moves; `s20.verified` is the conjunction with (1).
3. `verify_applied.py` runs in a fresh process, reads only `applied/*.jsonl` and
   `targets.csv`, imports only `words` and `autcanon.AUTOS`, and re-does (2) for every
   record with `s20.solved`, additionally checking that the sequence lands on the recorded
   image and that `orig_r1, orig_r2` match `targets.csv`.  It was cross-checked on B1's
   atlas: 715/715 atlas solves pass, and two corrupted controls (a truncated certificate, a
   shortened sequence) fail.
4. `analyze_applied.py` counts a solve only if `s20.verified` is true and the record is not
   in `verify_applied.json`'s failures.

## Deviations from the brief

__DEVIATIONS__
