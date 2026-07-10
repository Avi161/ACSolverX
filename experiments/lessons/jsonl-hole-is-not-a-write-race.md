# [2026-07-09] A hole in the jsonl is never a write race — and a flushed row is not a saved row [TRAP]

## What happened

A 1M-budget `HIGH_SPEEDUP` run over `ms_reps_unsolved.txt`, writing its jsonl straight to
Colab's Google Drive mount, was missing rows for presentations 7 and 8. Three workers ran
concurrently, so the obvious reading was a raced parallel dump. That reading is wrong, and
chasing it costs hours.

## Why a write race is impossible here

`out_f.write(...)` lives in `_emit`, a **closure defined in `run_dataset`** — the parent.
`_solve_one` (the worker) computes stats and *returns* them; the only file it ever opens is the
optional `hb_stack_<pid>.txt` debug dump. Every row is serialized through one parent-side
handle. There is exactly one writer.

Verified at budget 1,000 (never higher — see [local-run-budget-cap](local-run-budget-cap.md)):
3 forked workers, 12 presentations → `rows=12 order=[0,1,2,3,5,4,6,7,8,9,10,11] missing=[] dupes=0`.
Rows arrive out of order — that is `imap_unordered`, and it is normal — but none are lost.

Also verified *on the Drive mount itself*: a long-lived append handle, opened before a forked
`Pool`, flushing per row, loses nothing in isolation. The write pattern is not the problem.

## The three things that actually produce a hole

**1. The memory guard deferred it, and its row comes at the very end.** This is by design and is
the first thing to check, because it looks exactly like data loss:

```python
if exc is not None:                                   # run_baseline.py:996
    print(f"    pres {pres_id}: memory guard tripped ({exc}); deferring to a serial retry")
    aborted.append((pres_id, r1, r2, exc)); continue  # <-- no _emit, so no row
```

The row is not written until the pool has finished **all** presentations and the serial retry
runs. Observed live: `pres 18: memory guard tripped (20.4 GB > 15.9 GB after 819,200 nodes)`.
Grep the console for `memory guard tripped` before suspecting anything else. Note the guard
requires the worker to be over its `1/n` share **and** the machine to be under `_MEM_RESERVE_GB`
free, so only the genuinely heavy searches trip it — 18 and 19 did; the other 259 did not.
The partial search is discarded, so its nodes are re-searched from scratch on the retry.

**2. A pool worker died and its task was silently dropped.** `mp.Pool.imap_unordered` does not
detect worker death (unlike `concurrent.futures`, which raises `BrokenProcessPool`). The pool
*repopulates*, so later presentations keep completing at full throughput — and the dead worker's
result never arrives, so the iterator blocks forever once the last job is dispatched:

```python
pool = mp.get_context("fork").Pool(3)
it = pool.imap_unordered(work, range(6))   # work(1) SIGKILLs itself
# -> yields [0, 2, 3, 4, 5]; never raises StopIteration. HANG.
```

Signature: a hole at the killed ids, normal progress after, a hang at the end.

**3. The filesystem accepted the write and threw it away.** This is what actually happened.
`_emit` ran for 7 and 8 — the `[budget] k/n | pres P` line prints *after* `write()` and
`flush()` return, and the run printed `1/249 … pres 7` and `2/249 … pres 8`. Rows 12, 16, 15,
17 went through the identical code path seconds later and are on disk. 7 and 8 are not.

The boundary in the data is clean: all five **serial** ms640 files on the same Drive mount are
complete (640/640, no dupes), and they append a row every couple of seconds. The **pooled** 1M
run opens its handle, sits idle ~17 minutes while numba warms and the first searches run, and
loses the first two rows written after that idle. `flush()` only hands bytes to the OS; nothing
forced the FUSE layer to commit them.

Because the lost ids never entered `done`, **every resume re-searched them and lost them again**
— ~35 minutes of compute per attempt, forever. That is what makes this severe rather than
cosmetic.

## What was done about it

- `_persist(f)` — `flush()` **then** `os.fsync()`, tolerating `OSError` from a filesystem that
  refuses fsync. Used by `_emit`, `_write_path` and `_update_row` (which already fsynced, and
  whose unguarded `os.fsync` a new test caught).
- `_report_lost_rows(out_path, done_before, todo_ids)` — after a clean run, compares the ids the
  runner believes it wrote against `_read_done`, and says so loudly. A warning, never an
  exception: a 30-hour run must not die at the finish line over rows you can simply re-run.
- **Operationally: do not write the jsonl to a Drive mount.** `cfg["MOUNT_DRIVE"] = False` with
  `LOCAL_OUT_DIR` on `/content`, and mirror to Drive with a `cp` loop. The output directory is
  not part of the resume key, so resume reattaches to the same file.

## Two claims that were wrong along the way

- *"The `N already done` / `wc -l` mismatch means `_repair_jsonl` dropped a torn final line."*
  It didn't. The pre-run file had exactly 12 rows and the runner said `12 already done`. There
  was never a torn line. The arithmetic only looked off because the pasted jsonl had been read
  **mid-run**, after this run had appended its row for pres 12.
- *"The OOM killer took the workers."* The guard would have to be silent for that, and here it
  was loudly firing. Both `drive + pool` and `local + pool` repros lose nothing.

Both were plausible, both were reasoned from real evidence, and both were refuted by one cheap
test. That is the point of the tests.

## Rules

- **A missing row is a lost result or a lost write — never a raced write.** One process writes.
- **Grep for `memory guard tripped` first.** A deferred presentation has no row until the pool
  finishes every other one. It is not missing; it is late.
- **Out-of-order rows are `imap_unordered` working correctly**, not corruption.
- **`flush()` is not durability.** On any network or FUSE filesystem, `fsync` or lose data.
- **Never trust a filesystem you have not tested to keep a fsynced write.** Write results to
  local disk and copy them to the network share.
- **If the completion line printed, the row was written.** If it is not on disk, the filesystem
  ate it — look there, not at the runner.

## Related

[`heavy-mode-defers-solved-rows`](heavy-mode-defers-solved-rows.md) is the same principle one
layer up: a computed result must reach disk before anything else is attempted with it.
[`gb-per-pres-sized-from-measured-memory`](gb-per-pres-sized-from-measured-memory.md) explains
why the guard is deliberately not share-based.
[`forked-workers-block-cause-unknown`](forked-workers-block-cause-unknown.md) is the other
failure with a hole-shaped symptom. Distinguish from the console: count distinct pids in
`[hb] pres N started (worker pid P)` (more than `n_workers` → replaced → died) and read
`[hb] N solving` (`3` → full throughput; `1` → two workers blocked).
