# [2026-07-23] A reaped pool parent orphans its workers, and the bill lands on the user's editor [TRAP]

Second occurrence of the orphaned-worker defect (the first is [double-compute](orphaned-workers-double-compute.md)), with a different and worse consequence: this time the orphans took the machine, not the results.

## What happened

`experiments/heuristic_search/lab.py` evaluated configs through a `ProcessPoolExecutor(max_workers=9)`. Two separate sweeps were reaped by the harness mid-run. Each time the harness killed **only the parent** — the nine spawned children kept searching, detached, with no one reading their futures and nothing left to write their results to.

Eighteen orphans accumulated across the two batches. They were still expanding nodes at cap 48, where a single search's `visited` dict runs to ~1 GB. System swap reached **22.5 GB used with 50 million pageins**, and the user — editing in Cursor on the same machine — saw Cursor reporting a **75 GB** footprint and asked for an emergency fix.

Cursor was innocent. Its actual resident set was **0.82 GB across 37 processes**. macOS's memory column folds in compressed and swapped pages, so an application whose pages are being evicted and re-faulted under someone else's pressure reads as enormous. The number named the victim, not the cause.

## Why the first fix did not cover this

The earlier lesson produced a `flock` claim on the output jsonl, so an orphan could be *detected* by a later run and killed. That defends the data. It does nothing for the host in the window before a later run starts — and there may never be one. A guard that fires on the next launch cannot help a machine that is unusable *now*.

## The diagnostic trap

`ps aux | grep python3` returned nothing while all eighteen were running. Homebrew's framework binary is `.../Python.app/Contents/MacOS/Python` — capitalised, no version suffix. The grep that looks like it enumerates Python processes silently misses every one of them.

Search by RSS, not by name:

```bash
ps -Ao rss=,pid=,ppid=,args= | sort -rn | head -25
```

A parent whose `ppid` no longer exists, or resolves to `1`, is an orphan.

## Rule

**Locally, run searches serially — one config at a time, in-process.** Serial execution has no children, so the failure mode does not exist rather than being guarded against; that is strictly better than any orphan detector. Parallelism belongs on Colab, where the fleet is visible, disposable, and not sharing RAM with the user's editor.

Where a local pool is genuinely unavoidable, cap it from the environment (`ACSOLVERX_MAX_WORKERS`, default `1`) so the default cannot hurt anyone, and pair it with a `deadline` that stops cleanly between units of work — every finished unit is already fsynced, so an early stop costs nothing and resume picks up exactly there.

And when a user reports that application X is eating the machine, **measure X's own RSS before believing it.** On macOS the reported figure attributes compression and swap to whoever is being evicted, which is usually not whoever is doing the evicting.
