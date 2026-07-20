# [2026-07-20] Long background bash jobs get killed by a runtime wall — use a foreground + resume-safe parallel runner [TRAP]

## What happened

Running the `idea_bench` sweep (17 strategies × 22 presentations × 2 budgets = 748 greedy searches, each ≤1000 nodes) as a single `run_in_background` bash job got **killed twice** — a serial run and a parallel run both terminated mid-flight (task notifications came back `status: killed` / `was stopped`, not `completed`), around single-digit-to-~27 minutes of wall time, leaving a leaked-semaphore warning from the abruptly-torn `ProcessPoolExecutor`. Nothing in the script failed; the job was reaped from outside.

## Root cause

Background bash jobs in this environment are subject to a runtime wall that reaps long-running ones. A multi-minute compute loop launched with `run_in_background: true` cannot be relied on to finish. Foreground bash calls are NOT reaped this way — they are bounded by the tool's own `timeout` param (max 600000 ms), which *I* set and control.

## The fix (all three together)

1. **Parallelize** the work so it is short. A `ProcessPoolExecutor` (macOS default start method = spawn, which re-imports per worker and shares numba's on-disk `cache=True`, sidestepping the fork+numba deadlock in `forked-workers-block-cause-unknown.md`) cut ~2 h of serial work to ~15 min. cpu_count−2 workers.
2. **Make the runner resume-safe.** Write results to a fixed jsonl incrementally (`flush` per cell); on start, read the jsonl and skip every `(strategy, pres_id, budget)` cell already present; summarize keeps the *last* row per key so a redone interrupted cell is harmless. See `experiments/stable_ac/idea_bench/run_sweep.py`.
3. **Drive it foreground in bounded chunks.** Run with the Bash tool `timeout` at ~560000 ms; if it is reaped, relaunch — resume skips the done cells. Add a `--only <strategies>` filter so a slow tail (e.g. a huge-family enumeration) can be finished in its own short chunk.

Candidate generation was also made budget-independent (generate once per cell, search at every budget) — a free ~2× since the sweep ran two budgets.

## Rule

For any local compute that runs more than a couple of minutes, do NOT fire-and-forget a `run_in_background` bash job and wait for a completion notification — it may be reaped. Write a **resume-safe, incrementally-flushing** runner and drive it with **foreground** bash calls bounded by the tool `timeout`, relaunching until it reports nothing left to do. Parallelize with a spawn `ProcessPoolExecutor` to keep each chunk short.
