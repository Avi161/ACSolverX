# Proof Process Guard Design

## Problem

Four redundant proof jobs survived their useful work and each consumed most of
a CPU core.  Interrupting their controlling agents did not terminate the
detached children.  The existing thirty-minute audit eventually detects this,
but it does not prevent duplicate jobs or bound their lifetime.

The guard must make the safe state the default without weakening the rule that
an audit may terminate only a process whose staleness is established.

## Chosen design

All computational proof commands launched by this task go through one
foreground Python runner, `scripts/run_proof_guarded.py`.

The runner has four independent controls:

1. It atomically acquires one worktree-local lock. A second runner exits before
   starting its command. A lock whose owner PID no longer exists is reclaimed.
2. It starts the command in a new process group and applies a hard wall-clock
   timeout. On timeout or interruption, it sends `SIGTERM` to the entire exact
   group, verifies exit, and uses `SIGKILL` only after a short grace period.
3. It defaults to thirty seconds and rejects limits above sixty seconds. A job
   that needs longer must be decomposed or optimized before it is run again.
4. It limits common numerical runtimes to one worker thread through their
   documented environment variables. The child stays attached to the runner's
   terminal; the runner never creates a detached or background job.

The existing heartbeat audit remains a backstop and is tightened from thirty
minutes to five minutes. It continues to require PID-, tree-, working-directory,
file-, and connection-level evidence before termination. It must also recognize
the guard lock as evidence of an active bounded job, not evidence of staleness.

## Alternatives rejected

- Audit only: detection remains reactive and leaves a multi-minute overheating
  window.
- Runner only: a command started outside the runner or a runner crash would
  have no independent cleanup path.
- Killing every old process by name: this could terminate an interactive shell,
  active service, editor, or unrelated user computation.

## Interfaces

The command-line interface is:

```text
python3 scripts/run_proof_guarded.py [--timeout-seconds N] [--grace-seconds N] -- COMMAND [ARG ...]
```

Success returns the child's status. Duplicate refusal returns 73. Timeout
returns 124. Invalid limits return 2. The lock lives at
`.scratch/process-guard/active.json` and records only the runner PID, start time,
and worktree path—never command arguments or secrets.

## Verification

Fast integration tests use only tiny Python children. They prove that:

- a concurrent second invocation never starts its child;
- a timed-out child and its grandchild are both gone;
- numerical thread limits reach the child;
- a dead-owner lock is reclaimed; and
- a timeout above sixty seconds is rejected before launch.

No expensive proof checker is used to test the guard.
