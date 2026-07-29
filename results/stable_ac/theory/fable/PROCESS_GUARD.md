# Process guard for long CPU proof experiments (fable line)

STATUS: **IN FORCE.** Instrument: `experiments/stable_ac/fable/guarded_run.py`.
Tests: `tests/fable/test_guarded_run.py` — 31 tests, all passing; full suite
635 passed / 5 skipped. This is an engineering-safety note, not a mathematical claim.

## What changed and why

The session policy previously capped experiments at 60 seconds. It now authorises longer
CPU runs when theoretically justified, at **10 minutes maximum per experiment**, in
exchange for a hard process discipline. Nothing may run long until that discipline is in
code, tested, committed and pushed — this file is the log of that change.

## The rules, and where each is enforced

| rule | enforcement |
|---|---|
| Max runtime 10 minutes | `HARD_MAX_RUNTIME_S = 600`, a ceiling no flag can raise; `--timeout` above it is REFUSED |
| Successful ≤60 s preflight on the same code path first | `preflight_ok()`; a long run without a matching preflight is REFUSED. `HARD_MAX_PREFLIGHT_S = 60` |
| Exactly one experiment at a time | `GuardLock`, an `O_EXCL` lock file; a second run is REFUSED. Locks held by a dead guard are reclaimed, and say so |
| Foreground only, no detached/background processes | the runner blocks on its child; no `&`, no `nohup`, no `setsid` daemonising. Subagents are barred from starting computation at the orchestration level |
| One CPU thread | `SINGLE_THREAD_ENV` pins `OMP/OPENBLAS/MKL/NUMEXPR/NUMBA/VECLIB` to 1 in the child's environment |
| Never kill the controlling shell, harness, terminal, or infrastructure | the child is started with `start_new_session=True`, so it is its own session and group leader and `pgid == child pid`. `terminate_group()` RAISES if asked to signal the guard's own process group or an init-adjacent group (pgid ≤ 1) |
| Terminate only the experiment's exact child process group | `os.killpg(child_pgid, ...)` — never a bare `kill`, never a pattern match on process names |
| Progress at least every 60 s | heartbeat lines with elapsed/CPU/process-count/temperature; `--heartbeat` above `MAX_HEARTBEAT_S = 60` is REFUSED |
| SIGTERM first, SIGKILL only if ignored | `terminate_group()` sends SIGTERM, waits `SIGTERM_GRACE_S = 10`, and escalates only if live members remain |
| Never rerun an unchanged timed-out experiment | every run appends to `guard_ledger.jsonl`; a command whose `(command_key, code_fingerprint)` already timed out is REFUSED |
| Stop early on thermal pressure | `/sys/class/thermal` polled; stop at `THERMAL_LIMIT_C = 95` |
| Stop early on abnormal CPU behaviour | child CPU time frozen for `STALL_LIMIT_S = 180` s while the wall clock advances ⇒ stop |
| Stop early on unexpected child processes | group membership above `--max-children` (default 16) ⇒ stop |
| Stop early on loss of the controlling task | `os.getppid() == 1` (reparented to init) ⇒ stop |
| Verify cleanup afterwards | every exit path records `children_exited`, `surviving_pids`, `lock_removed`, and any stale Python/pytest/uv/Numba processes |
| A timeout is not evidence about AC | every ledger row carries a `note` saying so, and `verdict` is only ever a process outcome (`ok`, `nonzero_exit`, `timeout`, `stopped_early`, `interrupted`, `error`) — never a mathematical one |

## Two design decisions worth recording

**Path.** The guard is NOT at `scripts/run_proof_guarded.py`. The codex line added a guard
at exactly that path in `b617123..813a6d1`, and colliding on it would hand the user a merge
conflict in safety-critical code. This is the fable line's own guard, in the fable
namespace, and the two can coexist.

**"Same code path" is content-hashed, not mtime-based.** `code_fingerprint()` is a SHA-256
over every `.py` file under `experiments/stable_ac/fable`. Any edit anywhere in that
directory invalidates both a stale preflight and a timeout record. This is deliberately
conservative in the safe direction: after a real code change a timed-out experiment may be
retried, and a preflight stops vouching for code it never ran.

## A real bug the tests caught, worth remembering

The first test run escalated a clean SIGTERM exit to SIGKILL. The child had already died
(`rc = -15`) but lingered as a **zombie** in `/proc` until reaped, and the group-membership
scan counted it as a live survivor. Two consequences, both wrong: a needless SIGKILL, which
is precisely what "SIGTERM first" exists to prevent, and `children_exited = False` reported
for a child that had exited. Fixed by excluding state `Z` from `pgid_members()`. Symptom to
recognise: the guard reports `sigkill_sent` together with a negative return code of −15,
which is self-contradictory — a process that died of SIGTERM cannot have needed SIGKILL.
Secondary tell: the test file's runtime fell from 143 s to 36 s once fixed, because several
tests had been sitting through the full 10-second grace window.

## How to run an experiment under it

```
# 1. preflight, small corpus, same code path (hard cap 60 s)
python3 -m experiments.stable_ac.fable.guarded_run --preflight --timeout 55 \
    -- python3 experiments/stable_ac/fable/<module>.py <small args>

# 2. the real run (hard cap 600 s); refused without step 1
python3 -m experiments.stable_ac.fable.guarded_run --timeout 550 \
    -- python3 experiments/stable_ac/fable/<module>.py <full args>
```

Ledger: `results/stable_ac/fable/guard_ledger.jsonl`.
Child output: `results/stable_ac/fable/guard_logs/`.
