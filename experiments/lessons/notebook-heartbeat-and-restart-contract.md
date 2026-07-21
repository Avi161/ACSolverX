# [2026-07-21] Every notebook runner needs the standard heartbeat + the restart contract [WORKS]

User directive (nb6, stable-ac-escape): progress visibility and restartability are REQUIREMENTS for every long-running Colab notebook, not niceties. Two parts:

**1. The heartbeat.** The runner the notebook launches must print, streamed live through `run_cli_mirrored`:
- a per-unit line as each row/cell completes, carrying the work identifier, the result summary, and a **running pops/s (or nodes/s) average** — e.g. `[aca_2] t48 r plain/-1 95->16 pops=50 (830 pops/s run-avg)`;
- a periodic cumulative line with **units done / total, running SOLVED count, total pops, and an ETA** — e.g. `aca_2: 7 rows (6.0s) | 3/124 pres, 0 solved rows, 0.7k pops, ETA ~4.2h`;
- loud `*** ... SOLVE LEAD` lines for anything solve-adjacent (verification-bar language, aca_115 tripwire).
Reference implementation: `experiments/stable_ac/cov/inflate_descend.py` `run_inflate._emit` (climb pops attributed to each branch-tier's unique plain-arm row so nothing double-counts). `run_baseline.py`'s chunk heartbeat is the older reference. A worker process cannot print (parent-side only — see `heartbeat-worker-cannot-print.md`); never print from a background thread.

**2. The restart contract.** The user must be able to Runtime → Restart → Run All on an ALREADY-OPEN notebook and have everything continue — never re-open or re-upload it. That holds iff: `UPDATE_REPO = True` fetch+hard-reset in SETUP (pulls the latest branch), the `experiments.*` `sys.modules` purge, `seed_from_drive(local_dir)` before the run (fresh VM pulls its jsonls back), dateless resume-keyed jsonl output, and — critically — **every hotfix lands in `.py` modules only, never in notebook cells** (a cell edit is exactly what would force a re-open; see `colab-hotfix-py-only` memory and `notebook-push-does-not-reach-colab.md`).

**Rule:** any new notebook or notebook-launched runner ships with BOTH parts, and a review of either checks the other.
