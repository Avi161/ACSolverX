# applied: B1's radius-2 trick on the presentations nothing on record solves

**Question.** `ATLAS.md` shows that on the 28 AC19 orbits plain greedy cannot solve at
10,000,000 pops, `S20_MK2` solves 6/28 from the row as given but 26/28 from some radius-2
`Aut(F2)`-image at <= 20,000 pops.  Does the same trick crack anything that has never been
solved: the 124 unsolved Miller-Schupp classes (both forms), and the two level-9 AC19
orbits the atlas ball missed?  The answer is in `APPLIED.md`; this file is the how.

Git head when the targets were built and phase 1 started:
`460904f9850ee20e3fe7772704a17db36f44f707` on `claude/ac19-theorem-strength-8v1wp6`
(`targets_manifest.json`).  This session made no commits; an outside orchestrator committed
the campaign directory as `7fa813ae` and the phase-1 records as `85b5d079` at 21:44-21:45 UTC,
so the phase-2 outputs, `APPLIED.md`, `applied_summary.json`, `certify_short_states.py`,
`short_states.json`, `verify_applied.json` and the final edits to this file and
`analyze_applied.py` are in the working tree on top of `85b5d079`.  Everything lives in this
directory; B1's files (`orbit.py`, `engine.py`, `features.py`, `atlas.jsonl`) and B2's
`predictor/rank_images.py` are only read; nothing outside
`research/autchoice_20260910/applied/` was written.

## Files

| file | what it does |
|---|---|
| `common.py` | paths; `search(pair, budget, cap)` = `greedy_search_hcompact` under `S20_MK2` with `track_path=True`, keeping `min_total_length_seen` (the engine's `min_relator_length`) and replaying any claimed solve from the image with `words.replay_move` (`engine.replay`); `make_record` = one `atlas.jsonl`-shaped line plus `orig_r1, orig_r2, start_len, phase, radius`, with `s20.verified` = image replay AND `engine.verify_from_original` from the target's own pair |
| `build_targets.py` -> `targets.csv`, `targets_manifest.json` | the 250 targets (below), input hashes |
| `run_phase1.py` -> `phase1.jsonl`, `phase1_run.json`, `phase1_run.log`, `phase1_rejects.log` | radius-2 ball x `S20_MK2` @ 20,000 on every target; resumable |
| `run_phase2.py` -> `phase2.jsonl`, `phase2_selection.json`, `phase2_ranking.json`, `phase2_run.json`, `phase2_run.log` | radius-3 depth-3 images @ 20,000 and the top-3 images @ 200,000 on the 2 leftovers + the 10 closest aca targets; resumable |
| `verify_applied.py` -> `verify_applied.json` | fresh-process re-check of every claimed solve from the JSONL alone (no engine import) |
| `certify_short_states.py` -> `short_states.json` | for every record whose `min_total_length_seen` is below its class's best-known length: re-run the search, walk the solver's parent chain to the minimum, replay the AC moves with `words.replay_move` -- a certified path to a shorter representative |
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

All on the 4-core / 15 GB box, `OMP_NUM_THREADS=1 NUMBA_NUM_THREADS=1`, B2 on one core throughout,
an unrelated `run_ladder --workers 2` job on two cores from 21:45 UTC.

| step | workers | searches | budget | wall | started - finished (UTC) |
|---|---:|---:|---:|---:|---|
| `build_targets.py` | 1 | - | - | seconds | 20:22 |
| phase 1: radius-2 ball, 250 targets, 3,238 images | 3 | 2,100 distinct | 20,000 | 80.6 min | 20:24:28 - 21:45:07 |
| phase 2 stage A: depth-3 images of 12 targets | 2 | 184 | 20,000 | 7.1 min | 21:45:13 - 21:52 |
| phase 2 stage B: top-3 images of 12 targets | 2 | 36 | 200,000 | 13.1 min | 21:52 - 22:05:25 |
| `certify_short_states.py` (5 re-runs at 20,000) | 1 | 5 | 20,000 | ~0.5 min | 21:51 |
| `verify_applied.py`, `analyze_applied.py` | 1 | - | - | seconds each | 22:06 |

Search wall 1.68 h of the brief's 3 h (phase 1 within its 2.5 h budget; phase 2 within its 1 h
cap).  Projection printed after the first 30 phase-1 searches: 0.87 h for 2,100, so
`aca_best` was kept.  A censored 20,000-pop run takes 3.4-5 s on this box (B1 measured
5.5 s with two ladder workers alive); a censored 200,000-pop run 64 s and 2.6 GB peak
(measured once before phase 1), which is why stage B is 2-3 workers, never 4.

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
5. A *shorter state* (not a solve) is reported only if `certify_short_states.py` replayed a
   move-by-move AC path from the image to exactly the recorded state (`replay_ok`) and the
   automorphism sequence from the row lands on the image (`aut_ok`).

## Deviations from the brief

- **Identical pairs searched once.** 88 classes have `aca_N == acabest_N`, so 1,138 of the
  3,238 phase-1 (row, image) records are copies of another record's search (`s20.shared`);
  2,100 distinct searches were run.  The engine is deterministic (3 random records re-run
  bit-for-bit: `nodes`, `min_total_length_seen`, `max_expanded`, `min_relator`), so the
  copies are the runs they would have been.
- **A concurrent resume of phase 1 was launched from outside this session** at 21:38 UTC
  (`--workers 3`, same budget and cap; its log is `b3_phase1_resume.log` in the session
  scratchpad).  It re-ran 338 not-yet-written searches in parallel with the original run
  and appended 209 duplicate (row, image) records before it was stopped; the same outside
  chain de-duplicated `phase1.jsonl` when the original run finished (3,447 -> 3,238 lines,
  one record per (row, image), 250 rows).  Every kept record carries budget 20,000 / cap 48,
  and the engine's determinism (above) makes the duplicates identical to the kept lines.
  The 80.6 min phase-1 wall in `phase1_run.json` is the original run's; the resume cost the
  box about 12 extra core-minutes of the same searches.  The verification counts in
  `verify_applied.json` are from the final standalone run over the de-duplicated file.
- **Phase 2 was started by that same outside chain**, with the shipped `run_phase2.py`
  defaults but `--workers 2`, right when phase 1 ended; a `benchmark.ladder.run_ladder
  --workers 2` job unrelated to this brief was started on the box at the same minute, so 2
  workers was the right count (4 cores, B2 on one).  Nothing about the phase-2 protocol
  differs from this README's command except the worker count.
- `min_total_length_seen` was added to the record (the brief's record shape lists
  `solved, nodes, path_moves, max_expanded, verified`); the analysis needs it, and it is the
  engine's own `min_relator_length`, not a new computation.  The record also carries
  `orig_r1, orig_r2, start_len, phase, radius, min_relator, wall, shared`.
- Phase-2 selection uses `ball_min` (absolute) first, then the count of images below the
  start, then the count of images whose search got back down to the row's own length, then
  the drop, then the name; with `drop = 0` on 110/124 `aca_initial` and 124/124 `aca_best`
  rows the brief's two criteria alone would have left the choice to the name.
- `certify_short_states.py` is an addition: the analysis found one class whose search
  reached below its best-known length, and a state without a path is not a result.
- The predictor's `rank(pair, radius=3)` (B2's `pairwise_logistic` weights) existed when
  stage B ran and matched all 29 radius-3 images; the `h_s20mk2` fallback was not needed.
  `phase2_ranking.json` records the ranker per target.
