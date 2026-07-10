# [2026-07-09] A deferred result must reach disk before it is deferred [TRAP]

## What happened

`_MemGuard` stops a search that is about to exhaust the machine and hands the
presentation to a **serial retry**. That retry runs only after the pool has
drained *every other presentation* — ~29 hours for 261 presentations at a 1M node
budget, several times longer than a Colab session survives.

Until then the trip left **no trace at all**. No row, so the id was absent from
`done`, so the next resume handed it straight back to the pool, where it tripped
again on the same `1/n` share. Presentations 18 and 19 were re-searched every
session and never landed. The console said `deferring to a serial retry`, which
reads like a promise; the promise was only kept if the run survived to the end.

This is the same defect as
[heavy-mode-defers-solved-rows](heavy-mode-defers-solved-rows.md), one layer over.
That one parked **solved** rows in a RAM-only list until the run ended. This one
parks **aborted** rows. Second occurrence → it is a rule now, not a bug story.

## The fix

Write the row the instant the guard fires, flagged `mem_abort_pending`. Being on
disk puts the id in `done`, so the pool never re-searches it; `_read_mem_pending`
routes it to the serial retry instead, where it gets the whole machine.
`_finalize` then overwrites that placeholder **in place**, so one `pres_id` keeps
exactly one row.

Three states, and they must stay distinct:

| row | meaning | on resume |
|---|---|---|
| `mem_abort_pending` | tripped, retry never ran | retried **serially**, next session if need be |
| `mem_abort` alone | did not fit even alone | terminal; never re-searched |
| neither | a normal result | done |

Ordering matters: `out_f` must be **closed before** the retry loop, because
`_update_row` rewrites via `os.replace` and would orphan the append handle's fd.

Counting matters too: a resumed placeholder was already counted by `_read_done`,
so the retry must not increment `n_seen`/`processed` again — that would push
`processed` past `n_todo` and corrupt the running solve-rate.

## What mutation testing found

The suite was written first and passed on the first run, which is exactly when to
distrust it (see [cap-monotonicity-vacuous-guard](cap-monotonicity-vacuous-guard.md)).
Two mutations, both caught:

- blanking `_read_mem_pending` to `return set()` → 3 failures
- deleting the immediate `_emit` → 2 failures

The second mutation also exposed a **real latent bug** that no test had covered:
`_update_row` silently no-ops when the `pres_id` is absent, so `_finalize` — which
holds a result that exists nowhere else — would have discarded a completed search.
`_report_lost_rows` caught it as a warning (`!! 1 row(s) were written but are NOT
on disk`), but the result was gone. `_update_row` now returns whether it matched,
and `_finalize` appends rather than lose the row.

## Rules

- **A computed result must reach disk before anything else is attempted with it.**
  Not "before the run ends" — before the *next* step. A retry, a recovery, a
  re-solve: each is a step that can never happen.
- **"Deferred to the end" means "lost", on any run longer than a session.** If
  the deferral window is hours, the row must be persisted at the moment of
  deferral and enriched later, in place.
- **A placeholder must not look done.** It is in `done` so the pool skips it, and
  in a pending set so the retry finds it. Losing either half re-creates the bug.
- **An in-place update that cannot find its row must not fail silently.** Return
  whether it matched, and make the caller decide.
- **When a suite passes on the first run, mutate the fix and watch it fail.**
- **Never burn a row you learned nothing about.** If no retry could run (RAM
  unreadable), leave it `mem_abort_pending` for a later, bigger machine rather
  than writing a terminal `mem_abort` you have no evidence for.

## Related

[heavy-mode-defers-solved-rows](heavy-mode-defers-solved-rows.md) — the first
occurrence, on solved rows.
[jsonl-hole-is-not-a-write-race](jsonl-hole-is-not-a-write-race.md) — the other
reason a row goes missing, and why `memory guard tripped` is the first thing to
grep for.
[compact-solver-arena-heap](compact-solver-arena-heap.md) — the change that makes
the guard stop tripping in the first place. This fix is the hedge for when it
still does.
