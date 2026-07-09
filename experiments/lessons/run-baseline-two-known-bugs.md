# [2026-07-09] Two real bugs in run_baseline.py: pinned as xfail, then fixed [TRAP]

Found while mapping the runner for the test suite. Under the repo rule "do not modify existing
code" they were first *pinned*, not fixed: `experiments/greedy_tests/test_known_gaps.py` asserted
the **desired** behaviour under `xfail(strict=True)`, so the suite stayed green and the tests would
turn RED the moment someone fixed the bug.

**Both are now fixed.** The markers are gone and the tests live in
`experiments/greedy_tests/test_crash_resume.py` as ordinary regressions.

1. **`todo[0]` before the empty check.** `_w1, _w2 = todo[0][1], todo[0][2]` ran unconditionally
   inside `if high and n_workers > 1`. Re-running a **fully-resumed** heavy sweep (`n_todo == 0`)
   just to confirm it was complete raised `IndexError` in the numba warm-up instead of printing
   "nothing to do". The crash preceded `ctx.Pool`, so no worker was ever spawned. Guarded with
   `and jobs`, which also stops it forking a pool for zero work. Fixed alongside
   [heavy-mode-defers-solved-rows](heavy-mode-defers-solved-rows.md), which needed the same
   resume-with-nothing-to-search path to work.

   **The lifecycle worked exactly as designed:** the strict xfail XPASSed the moment the fix landed,
   which is how the fixer learned to delete the marker. That is the whole argument for `xfail(strict=True)`
   over `skip`.

2. **Unguarded `json.loads` in `_read_done`.** A truncated trailing line — exactly what a Colab
   disconnect mid-write produces — crashed the resume that the jsonl exists to enable. Blank lines
   were skipped; a partial JSON object was not.

## The part that a reader-side guard does NOT fix

Bug 2 looks like a missing `try/except`. It is not. Rows are appended with `open(out_path, "a")`,
and a torn line has **no trailing newline**, so the next appended row is concatenated onto the stub:

```
{"pres_id": 2, "solv{"pres_id": 2, "solved": true}
```

That line is now in the *middle* of the file. No trailing-line tolerance in any reader can ever
recover it. Worse, `_read_done` is not even the only reader: `wandb_tracking.read_jsonl` (called
~15 lines later, under the production `USE_WANDB=True`), plus `_read_pending`, `_read_paths_done`
and `_update_row`, all parse the same file unguarded. Guarding `_read_done` alone would not have
stopped the original crash.

So the fix is `_repair_jsonl(path)`: truncate back to the last newline **before anything opens the
file for append**, called right after `_resolve_paths` and *not* gated on `RESUME` (a non-resumed run
also opens the file `"a"`). One repair at the entry point covers all five readers. It may discard one
complete row whose newline was lost; that row is then simply absent from `done` and gets re-run.
Losing one search is cheaper than guessing whether a partial line was complete. `_read_done` keeps a
tolerant guard too, but only so that reading an unrepaired file works — and it **raises** on an
unparseable *interior* line, since only the final line can be a torn write and silently skipping the
rest would drop a presentation from `done`.

Verified against the pre-fix file: old `_read_done` raises `JSONDecodeError`; appending onto the stub
produces the corrupt interior line above. Neutering `_repair_jsonl` turns
`test_appending_after_a_torn_write_keeps_the_file_parseable` and `test_a_paths_file_is_repaired_too`
red while the reader-level tests stay green — which is the proof that those two test the fix.

**Rules:**
- When a repo forbids touching existing code, `xfail(strict=True)` is the right home for a known
  defect — it documents the bug, keeps the suite green, and fails loudly once the bug is gone. A
  plain `skip` would rot silently.
- **A crash-recovery test that only exercises the reader tests nothing.** The damage is done by the
  *writer*. Drive a real append over a damaged file, and prove the test fails without the fix.
- An append-only log needs its trailing line repaired **before the first append**, not tolerated at
  read time. Tolerance hides a truncation; the next append makes it permanent.
- Repair at the single entry point, not at each reader. Chasing `json.loads` call sites is
  scope creep that still leaves the file corruptible.
