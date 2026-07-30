# Long Proof Process Guard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a fail-closed, opt-in two-phase guard for one foreground AK(3) proof experiment lasting at most ten minutes.

**Architecture:** Preserve the existing short runner and singleton lock, then add one long-run coordinator that executes an identical command first as a short preflight and then as the bounded experiment under the same lock. A standard-library safety monitor checks the captured direct OS launcher, guard coordinator, phase leader, descendant escapes, and whole exact-group CPU from a safe-field process table; a bounded internal helper reads macOS thermal state. Every failure cleans only the exact active phase group, with separate exact-group cleanup for the helper itself.

**Tech Stack:** Python 3.9 standard library, pytest, POSIX process groups, macOS Foundation through `ctypes`.

## Global Constraints

- Work only in `/Users/avigyapaudel/Documents/Obsidian Vault/surf/ACSolverX/.claude/worktrees/codex-proofs`.
- Do not stage or modify the paused Task 5 files `.scratch/period_two_old_new_cut_load_certificate.py` and `.scratch/test_period_two_old_new_cut_load_certificate.py`.
- Every computational proof, checker, census, test, or search uses the guard as
  the single foreground computation. Short mode stays at a 30-second default
  and a 60-second maximum, and an unchanged timed-out command is never rerun.
- Long mode requires `60 < --timeout-seconds <= 600` and a successful identical-command preflight with `0 < --preflight-seconds <= 60`.
- Execute the exact same command arguments in both phases under one lock.
- Permit exactly one experiment, foreground only, with one numerical CPU thread;
  only the procedural root Codex launcher may launch it. Distinguish that
  authorization from the captured direct OS launcher PID, guard coordinator,
  and current phase leader. Verify their direct OS parent chain before preflight
  and during phases without claiming that it cryptographically proves Codex
  identity.
- Send `SIGTERM` first; use `SIGKILL` only if the exact child group survives the grace period.
- Never signal the controlling shell, Codex/ChatGPT, terminal, application infrastructure, or an escaped ambiguous PID.
- Require `1 <= --progress-seconds <= 60` and emit flushed progress without exposing commands, arguments, or environment values; the procedural root Codex launcher must update the user within every 60-second window.
- Request only PID, PPID, PGID, CPU percentage, state, and executable name from `ps`; evaluate CPU across the whole exact PGID and detect captured-launcher/coordinator loss or reparenting, phase-leader loss or reparenting, and descendant escapes.
- Run Foundation only in a fixed-argument internal helper under one absolute thermal-plus-`ps` deadline; emit the fixed, PID-free deadline transition and clean the helper's exact group with `SIGTERM` then `SIGKILL` only if needed.
- Treat numeric exit status as non-authoritative because completed child statuses
  can collide with guard codes. For every completed long invocation require a
  fresh mode-`0600` `.scratch/process-guard/last-run.json` with matching
  provenance, `state=finalized`, semantic `classification`, top-level
  `guard_status`/`return_status`, and per-phase outcome, PGID, `guard_status`,
  `child_exit_status`, and `exact_group_absent`. A duplicate `73` creates no new
  audit and must not be confused with the active owner's record.
- Finalize the exact audit while the singleton is held, recheck all observed
  phase PGIDs, record `lock_release_pending: true`, and only then release. The
  procedural root independently verifies the active lock is absent and scans
  externally for stale project Python, pytest, uv, or Numba processes because
  one-second sampling cannot exclude an unobserved double fork.
- Treat every failed or timed-out preflight, experiment timeout, nonzero child
  exit, interruption, thermal or process stop, safety or cleanup failure, audit
  or write stop, and every other unsuccessful bounded result only as a bounded
  failure, never as evidence against AC or stable AC. Never rerun an unchanged
  timed-out experiment; commit, bind the push log, and push the bounded result.
- The guard's focused synthetic test suite is the sole direct-run exception.

---

### Task 1: Pin long-mode CLI and two-phase behavior

**Files:**
- Modify: `tests/test_run_proof_guarded.py`
- Modify: `scripts/run_proof_guarded.py`

**Interfaces:**
- Consumes: `parse_args(argv)` and `main(argv)`.
- Produces: parsed `long_run`, `preflight_seconds`, and `progress_seconds`; invalid-limit status 2, singleton status 73, experiment-timeout status 124, preflight status 125, and safety/cleanup status 126.

- [ ] **Step 1: Write failing CLI tests**

Add subprocess tests proving that ordinary timeout 61 still exits 2, long-run
timeout 60 and 601 exit 2 before a marker is written, preflight 61 exits 2, and
progress below one second or above 60 exits 2. Add direct parser tests for the
finite bounds.

- [ ] **Step 2: Run the focused tests to verify RED**

Run: `PYTHONPYCACHEPREFIX=.scratch/pycache uv run --with pytest pytest -q tests/test_run_proof_guarded.py -k 'long_run or preflight or progress'`

Expected: FAIL because the new options are not recognized.

- [ ] **Step 3: Add minimal argument parsing**

Add constants `MAX_LONG_TIMEOUT_SECONDS = 600.0`,
`DEFAULT_PREFLIGHT_SECONDS = 60.0`, `DEFAULT_PROGRESS_SECONDS = 60.0`,
`MIN_PROGRESS_SECONDS = 1.0`, `PREFLIGHT_EXIT = 125`, and
`SAFETY_EXIT = 126`. Add `--long-run`, `--preflight-seconds`, and
`--progress-seconds`. Validate all values as finite; require
`60 < timeout_seconds <= 600` in long mode, retain `timeout_seconds <= 60` in
short mode, require `0 < preflight_seconds <= 60`, and require
`1 <= progress_seconds <= 60`.

- [ ] **Step 4: Run the CLI tests to verify GREEN**

Run the Step 2 command and require every selected test to pass.

### Task 2: Execute the same command in two clean phases

**Files:**
- Modify: `tests/test_run_proof_guarded.py`
- Modify: `scripts/run_proof_guarded.py`

**Interfaces:**
- Consumes: `limited_environment(phase: str | None)` and the existing `terminate_group()`.
- Produces: `run_long_guarded(command, preflight_seconds, experiment_seconds, progress_seconds, grace_seconds, monitor)`.

- [ ] **Step 1: Write failing two-phase tests**

Use one synthetic command that appends `ACSOLVERX_PROOF_PHASE` and its numerical
thread variables to a temporary JSON-lines file. Assert the same command writes
exactly `preflight` then `experiment`, both phases receive only `"1"` thread
values, and the lock remains owned throughout. Add commands whose preflight
exits nonzero or sleeps beyond an injected subsecond limit; assert return 125,
no experiment record, no surviving exact-group PID, and no lock.

- [ ] **Step 2: Run the new tests to verify RED**

Run the named two-phase tests directly and require failures at the missing
coordinator rather than fixture setup.

- [ ] **Step 3: Implement phase execution**

Extend `limited_environment` to set `ACSOLVERX_PROOF_PHASE` only when provided.
Factor one monitored phase launcher around `subprocess.Popen(...,
start_new_session=True, shell=False)`. Run preflight and experiment sequentially
under the `ProcessLock` already owned by `main`; never mutate the command
sequence. Map preflight nonzero/timeout to 125, experiment timeout to 124, and
return the experiment's actual non-timeout status.

- [ ] **Step 4: Enforce post-phase group absence**

After the phase leader exits, check `group_exists(child.pid)`. If a group member
lingers, terminate that exact group and return 126. Do not begin the experiment
after any preflight cleanup violation.

- [ ] **Step 5: Run the two-phase tests to verify GREEN**

Run the Step 2 command and require all new and existing cleanup assertions to
pass.

### Task 3: Add fail-closed thermal and process monitoring

**Files:**
- Modify: `tests/test_run_proof_guarded.py`
- Modify: `scripts/run_proof_guarded.py`

**Interfaces:**
- Produces: immutable `ProcessInfo` and `SafetySample` records;
  `read_bounded_macos_thermal_state(deadline: float) -> int`;
  `SafetyMonitor.sample(child_pid: int, process_group_id: int, launcher_pid: int, coordinator_pid: int, sample_deadline: float | None = None) -> SafetySample`.
- Consumes: injected monitor samples in the phase loop.

- [ ] **Step 1: Write failing pure monitor tests**

Construct process tables with an exact-group leader and child, an escaped
descendant, lost or reparented captured-launcher/coordinator links, and aggregate
CPU values above and below 125.
Assert escaped PID reporting, group process count, and CPU sum. Mock thermal
states nominal, fair, serious, critical, and unreadable; assert every nonzero or
unreadable value is a safety failure.

- [ ] **Step 2: Write failing phase safety tests**

Inject deterministic monitor samples into `run_long_guarded`. Prove that one
high-CPU sample does not abort, three consecutive high samples do; thermal
pressure, captured-launcher/coordinator loss or reparenting, and an escaped
descendant each return 126; and each case sends cleanup only to the phase's exact
process group. Verify the escaped PID is reported but never passed to `os.kill`
or `os.killpg`.

- [ ] **Step 3: Implement the macOS thermal reader**

Add a fixed `--internal-thermal-probe` mode that bypasses lock acquisition and
recursive long-run startup. Launch only `[sys.executable, absolute_guard_path,
--internal-thermal-probe]` in a new helper group with the one-thread environment;
the helper loads Foundation and libobjc with `ctypes` and calls
`NSProcessInfo.processInfo.thermalState`. Bound it by the sample's absolute
deadline, accept only enum values 0 through 3, emit only the fixed sanitized
deadline transition, and clean the helper's exact group with `SIGTERM` followed
by `SIGKILL` only if needed. Long mode accepts only nominal enum value 0 and
fails closed on unsupported platforms, deadline, parse, API, or cleanup failure.

- [ ] **Step 4: Implement safe process-table sampling**

After thermal probing, pass only the time remaining under the same absolute
sample deadline to `ps -axo pid=,ppid=,pgid=,%cpu=,state=,ucomm=` with
`check=True`, and text output. Parse only those fields. Build descendants from
PPID edges, sum CPU for every process in the exact PGID, and return every descendant whose
PGID differs. Never request or print command arguments or environment data.

- [ ] **Step 5: Implement monitor policy**

Sample immediately and then once per second. Abort immediately for captured-launcher/coordinator loss, zombie state, or reparenting, phase-leader loss or reparenting,
thermal state other than nominal, sampling failure, or escaped descendants.
Count consecutive exact-group CPU samples above 125 percent and abort on the
third; reset the count after a compliant sample.

- [ ] **Step 6: Run monitor and phase tests to verify GREEN**

Run the Task 3 test names, then the entire focused guard suite. Require no lock
and no synthetic PID after pytest exits.

### Task 4: Add safe progress and preserve signal cleanup

**Files:**
- Modify: `tests/test_run_proof_guarded.py`
- Modify: `scripts/run_proof_guarded.py`

**Interfaces:**
- Consumes: `SafetySample` from Task 3.
- Produces: sanitized phase-start and periodic progress lines.

- [ ] **Step 1: Write failing progress tests**

Use an injected clock and samples to cross two progress boundaries quickly.
Assert each line contains phase, elapsed seconds, exact-group process count,
aggregate CPU, and thermal label, while a sentinel command argument and a
sentinel environment value are absent.

- [ ] **Step 2: Implement progress output**

Print and flush one start line for each phase. During the experiment print and
flush at every configured one-to-sixty-second boundary. Format only
the sanitized sample fields; do not retain or interpolate the command.

- [ ] **Step 3: Re-run interruption tests**

Run the existing SIGHUP/SIGTERM/timeout/group-cleanup cases plus the new
progress tests. Require SIGTERM-before-SIGKILL behavior, exact-group absence,
and lock removal on every path.

### Task 5: Make project policy match the new authorization

**Files:**
- Modify: `AGENTS.md`
- Read back: `AGENTS.md`
- Verify/modify: `docs/superpowers/specs/2026-07-29-long-proof-process-guard-design.md`
- Verify/modify: `docs/superpowers/plans/2026-07-29-long-proof-process-guard.md`

**Interfaces:**
- Consumes: the new long-run CLI.
- Produces: one procedural-root-only rule for preflight, launch, reporting,
  post-run audit, bounded-failure language, and unchanged-timeout prohibition.

- [ ] **Step 1: Supersede the old sixty-second lesson without deleting it**

Mark the earlier maximum-60 rule `[SUPERSEDED]`. Append a dated `[WORKS]`
entry requiring `--long-run`, exact-command preflight, one foreground thread,
procedural-root launch only, distinct captured-launcher/coordinator/phase-leader
roles, user progress within sixty seconds, thermal and
process anomaly stops, exact-group termination, post-run audit, and immediate
commit/log/push of the bounded result.

- [ ] **Step 2: Read the lesson back immediately**

Read the changed section and verify every listed rule is present and the old
rule remains visible as superseded history.

- [ ] **Step 3: Align and read back the design and plan**

Verify and modify both guard documents in this Task 5 scope. Require active
short-mode policy, fixed PID-free deadline wording, the four distinct actors and
limited ancestry claim, non-authoritative numeric statuses, the private fresh
final audit contract and duplicate isolation, exact under-lock finalization,
independent lock/process checks, exhaustive bounded-failure language, and the
sole focused-suite exception. Read both documents back against this checklist.

### Task 6: Verify and publish the safety checkpoint

**Files:**
- Verify: `scripts/run_proof_guarded.py`
- Verify: `tests/test_run_proof_guarded.py`
- Verify: `AGENTS.md`
- Verify: `docs/superpowers/specs/2026-07-29-long-proof-process-guard-design.md`
- Verify: `docs/superpowers/plans/2026-07-29-long-proof-process-guard.md`
- Modify: `logs/29-07-2026.md`

**Interfaces:**
- Produces: a pushed `codex/proofs` safety checkpoint that precedes every
  experiment above sixty seconds.

- [ ] **Step 1: Run authoritative verification**

Run the guard's focused pytest suite directly through `uv run --with pytest`
because it is the sole guard exception. Run `py_compile`, `git diff --check`,
and a targeted process/lock audit. Require all tests pass, compilation exits 0,
the lock is absent, and no stale project Python, pytest, uv, or Numba process
exists.

- [ ] **Step 2: Review only the safety files**

Inspect the working and cached diffs. Stage only the two documents, guard,
guard tests, `AGENTS.md`, and the required push log; leave the paused Task 5
files unstaged and unchanged.

- [ ] **Step 3: Commit with the mandatory two-commit log binding**

Append `## HH:MM:SS UTC · `PENDING`` plus one to three linked sentences to
`logs/29-07-2026.md`, commit the safety files and log body, obtain that commit's
short SHA, replace only `PENDING` with it, and create the follow-up log-binding
commit. Do not amend in pursuit of a self-hash.

- [ ] **Step 4: Push before any long experiment**

Push `codex/proofs`, verify the remote tip, and re-run the targeted process and
lock audit. Only then may the procedural root Codex launcher resume the compact
proof-certificate generator/replay task and consider one preflight-gated long
experiment.
