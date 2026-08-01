# Process and computation safety

No subagent may start proof, checker, census, search, or test computation. Only the procedural root launcher may start a guarded computation. Run one foreground guarded job at a time through `scripts/run_proof_guarded.py`; short mode defaults to 30 seconds and may not exceed 60 seconds. Do not rerun an unchanged timeout: first change a material condition.

A longer experiment needs the guard's explicit `--long-run` mode, a successful identical preflight, and the authorization boundary in `ac-theory.md`. Keep one numerical CPU thread, report progress at least every 60 seconds, and stop for thermal pressure, an escaped descendant, or unexpected process-tree state.

After a long run or interruption and before handoff, audit the exact relevant process tree using only safe fields. Terminate only a process proven stale, use `SIGTERM` before bounded escalation, and re-scan to prove exit. A timeout, nonzero result, safety stop, or incomplete audit is a bounded failure, not evidence against AC or stable AC.
