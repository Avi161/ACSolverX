# Proof Process Guard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prevent duplicate or leaked ACSolverX proof jobs from overheating the machine.

**Architecture:** A foreground Python wrapper owns one atomic worktree lock, launches one child process group, imposes a strict timeout and one-thread numerical environment, and cleans up the group on every exit path. The existing five-minute heartbeat remains an evidence-based independent backstop.

**Tech Stack:** Python standard library, pytest, macOS/POSIX process groups, Codex heartbeat automation.

## Global Constraints

- Work only in `/Users/avigyapaudel/Documents/Obsidian Vault/surf/ACSolverX/.claude/worktrees/codex-proofs`.
- Never start detached or background proof work.
- Default timeout is 30 seconds; absolute maximum is 60 seconds.
- Send `SIGTERM` first and use `SIGKILL` only after the configured grace period.
- Never store command arguments or environment secrets in the lock.
- Tests must use tiny synthetic children and finish in seconds.
- Do not spawn subagents for this implementation.

---

### Task 1: Pin the safety contract with failing integration tests

**Files:**
- Create: `tests/test_run_proof_guarded.py`

**Interfaces:**
- Consumes: command-line contract from the design document.
- Produces: subprocess-level assertions for exit codes 0, 73, 124, group cleanup, one-thread environment, and stale-lock recovery.

- [ ] **Step 1: Write the failing tests**

Create helpers that invoke the not-yet-existing script with `sys.executable`.
Use literal expected exit codes and temporary marker/PID files. Start one bounded
runner in the foreground through `subprocess.Popen`, wait for its lock, and
assert a second invocation returns 73 without writing its marker. Launch a
child that launches a sleeping grandchild, assert timeout status 124, then poll
both exact PIDs until neither exists. Assert all numerical worker variables are
`"1"`, a dead-owner lock is reclaimed, and timeout 61 is rejected with status 2.

- [ ] **Step 2: Run the tests to verify RED**

Run: `PYTHONPYCACHEPREFIX=.scratch/pycache pytest -q tests/test_run_proof_guarded.py`

Expected: FAIL because `scripts/run_proof_guarded.py` does not exist.

- [ ] **Step 3: Commit the red tests with the design and plan**

Run: `git add docs/superpowers/specs/2026-07-29-proof-process-guard-design.md docs/superpowers/plans/2026-07-29-proof-process-guard.md tests/test_run_proof_guarded.py`

Run: `git commit -m "Test proof process safety contract"`

---

### Task 2: Implement the bounded foreground runner

**Files:**
- Create: `scripts/run_proof_guarded.py`
- Test: `tests/test_run_proof_guarded.py`

**Interfaces:**
- Consumes: `main(argv: Sequence[str] | None = None) -> int` CLI arguments.
- Produces: `LockHeldError`, `ProcessLock.acquire()`, `terminate_group()`, and `run_guarded()` behavior exposed through the CLI.

- [ ] **Step 1: Implement atomic lock ownership**

Use `os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)`. Encode only
`pid`, `started_at`, and `worktree`. If the existing PID fails `os.kill(pid, 0)`,
remove that exact stale lock and retry once. Always unlink the lock in `finally`
only when the current process owns it.

- [ ] **Step 2: Implement bounded process-group execution**

Launch `subprocess.Popen(command, start_new_session=True, env=limited_env)` with
`shell=False`. Call `wait(timeout=timeout_seconds)`. On timeout or interruption,
send `SIGTERM` to `os.killpg(child.pid, ...)`, wait `grace_seconds`, then send
`SIGKILL` only if the group remains. Return 124 for timeout and the child's real
status otherwise.

- [ ] **Step 3: Validate arguments before acquiring the lock**

Require a non-empty command, positive timeout and grace values, and
`timeout_seconds <= 60`. Default to 30 seconds and two seconds of grace.

- [ ] **Step 4: Run focused tests to verify GREEN**

Run: `PYTHONPYCACHEPREFIX=.scratch/pycache pytest -q tests/test_run_proof_guarded.py`

Expected: PASS with no warnings, no surviving fixture PIDs, and no lock file.

- [ ] **Step 5: Run static checks**

Run: `PYTHONPYCACHEPREFIX=.scratch/pycache python3 -m py_compile scripts/run_proof_guarded.py tests/test_run_proof_guarded.py`

Expected: exit 0.

---

### Task 3: Make the workflow fail closed

**Files:**
- Modify: `AGENTS.md`
- Modify externally through the Codex automation API: `audit-stale-acsolverx-processes`

**Interfaces:**
- Consumes: the runner CLI and existing evidence-based audit prompt.
- Produces: a mandatory local workflow rule and one five-minute heartbeat.

- [ ] **Step 1: Append the incident lesson to `AGENTS.md`**

Record that four concurrent proof children outlived interrupted agents and
overheated the machine. Require every computational proof/checker command to use
the guard, prohibit a second proof job, prohibit unchanged retries after a
timeout, and require explicit agent interruption plus process re-scan before
handoff.

- [ ] **Step 2: Read `AGENTS.md` back immediately**

Run a focused read of the appended section and verify each rule is present.

- [ ] **Step 3: Update the existing heartbeat without creating a duplicate**

Preserve id `audit-stale-acsolverx-processes`, heartbeat kind, target thread,
active status, and evidence-only termination policy. Change the recurrence from
thirty minutes to five minutes and teach it that a live guard lock identifies a
bounded active job.

- [ ] **Step 4: Verify automation uniqueness and settings**

Read the exact automation file and confirm one matching automation directory,
`FREQ=MINUTELY;INTERVAL=5`, and the updated prompt.

---

### Task 4: Verify, commit, and push

**Files:**
- Verify: all Task 1–3 files and automation state.

**Interfaces:**
- Consumes: completed guard and policy.
- Produces: pushed branch `codex/proofs` with a clean tracked worktree.

- [ ] **Step 1: Run the focused test and compile checks again**

Run the exact Task 2 verification commands. Confirm no proof/search child
appears in a targeted process scan afterward.

- [ ] **Step 2: Review the diff for unrelated edits**

Run: `git diff --check` and inspect the staged diff. Revert no user work; stage
only the plan, design, guard, tests, and `AGENTS.md` lesson.

- [ ] **Step 3: Commit and push**

Run: `git commit -m "Guard proof runs against CPU leaks"` and
`git push origin codex/proofs`.

- [ ] **Step 4: Resume theory work locally**

Continue the seven-family old-new cut proof without subagents. Use symbolic
reasoning first; run any bounded checker only through the new guard.
