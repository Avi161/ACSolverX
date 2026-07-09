# [2026-07-09] HIGH_SPEEDUP held every SOLVED row in RAM until the run ended [TRAP]

## Symptom

A 261×1M sweep on `ms_reps_unsolved` was writing rows normally, but `pres_id 12` never
appeared in the jsonl even though its search had finished. Presentations 7 and 8 were
missing too. Every row that *had* landed carried `"solved": false`, and they arrived out of
`pres_id` order (`0,1,2,3,5,6,4,9,11,10,13,14`) — the `imap_unordered` signature of the
`HIGH_SPEEDUP` pool.

## Cause

The heavy solver does not track paths, so `run_baseline.run_dataset` deferred any solved
presentation to a post-pool serial re-solve — and wrote **no row at all** until then:

```python
if high and stats["solved"]:
    deferred.append((pres_id, r1, r2))   # nothing written; lives only in RAM
else:
    _emit(pres_id, r1, r2, stats, elapsed)
```

So a presentation was invisible in the jsonl *precisely because it solved* — the only
outcome anyone cares about. `deferred` is a plain list in the parent process, and the
recovery loop runs the memory-hungry **normal** solver at the full budget, in the parent,
serially, after every presentation has finished. Consequences:

1. **Solved results were memory-only for hours.** A Colab disconnect, an OOM, or a
   `KeyboardInterrupt` during recovery lost every one of them.
2. **Resume could not help.** `_read_done` only sees rows in the file, so a lost solved
   presentation was re-searched from scratch on the next run — and deferred again. The
   expensive work never converged to disk.
3. **One failure killed the rest.** The recovery loop had no `try/except`, so the first
   `MemoryError` aborted the loop and took every *remaining* deferred row with it.

Reproduced on `ms640_solved[620:640]` @20k with `N_WORKERS=2`: the run printed
`solved 8/20 (40.0%)` while the jsonl contained **zero** solved rows. With recovery forced
to raise, all 8 were lost; `RESUME=True` re-ran them and lost them again.

## Fix

Write the heavy search result the moment it exists, marked `path_pending`, then fill the
path in afterwards:

- `_emit(..., path_pending=True)` for a heavy solved presentation — the row is durable
  immediately, with `solved=true` and `path_length=null`.
- Recovery replaces that row **in place** via `_update_row` (temp file + `os.replace`, so a
  crash leaves the previous valid file), setting `path_recovered=true`.
- Recovery is wrapped per presentation: a failure prints, keeps `path_pending`, and lets the
  other presentations finish.
- `_read_done` returns a `pending` set; resume seeds `deferred` from it and **never
  re-searches** — it only retries the cheap path recovery.
- `_write_path` is idempotent (guarded by the pres_ids already in `*_paths.jsonl`), and runs
  *before* `_update_row`, so the invariant `path_recovered ⇒ path row exists` survives a
  crash between the two.

Two incidental bugs fixed on the way:

- `wandb_tracking.finish_run` logged `logger.table`, accumulated during the run. A recovered
  row rewrites its earlier `path_pending` version, so the incremental table kept the stale,
  path-less copy. The table is now built from the jsonl (`build_results_table`), matching
  what `finish_run`'s own docstring already promised ("recompute everything from the jsonl").
- The pool block read `todo[0]` unconditionally; resuming a run with nothing left to search
  (but paths to recover) raised `IndexError`. Now guarded by `and jobs`.

## Verified

Regression tests: `experiments/greedy_tests/test_runner_recovery.py` (5 tests, fast tier,
budget 500). Checked non-vacuous — **3 of the 5 fail against the pre-fix `run_baseline.py`**,
each with the `MemoryError` escaping `run_dataset`. The other two pin invariants the *fix*
could break (one row per pres_id; a second resume is a no-op).

`pytest experiments/greedy_tests` → 471 passed / 1 xfailed; `--runslow` → 514 passed.
`tests/wandb_offline_integration.py heavy` independently reports "4 unique rows,
1 solved+recovered (no duplicate rows from the deferred/recovery loop)".

Ad-hoc, before the suite existed: `ms640_solved[620:640]`, `N_WORKERS=2`, at **10k and 5k**
budgets — crash-during-recovery → resume → recover reproduces a clean never-crashed run
field-for-field, every recovered path replays to the trivial state. `fork` == `spawn` ==
serial, heavy == normal. Two budgets rather than one big one: nothing in the fix references a
budget, so agreement at 5k and 10k is the evidence it holds at 1M
(see [local-run-budget-cap](local-run-budget-cap.md)).

Note `min_relator`/`max_relator` **strings** are excluded from every cross-run comparison:
the normal solver takes `min()`/`max()` over a `set`, so it breaks equal-length ties by
`PYTHONHASHSEED`. Their *lengths* are deterministic and are compared.

## Rules

- **A computed result must reach disk before anything else is attempted with it.** Never park
  finished work in a Python list across a phase that can crash — least of all the successes.
- A post-processing step (path recovery) is *enrichment*, not a precondition for persistence.
  Persist the fact, then enrich it in place.
- If a row can be rewritten, no accumulated in-memory mirror of it (a W&B Table, a cache) may
  be the thing you finally publish. Rebuild from the source of truth.
- When a resume key is derived from the output file, any state kept only in RAM is invisible
  to resume and will be recomputed forever. Make `_read_done` see everything that matters.
