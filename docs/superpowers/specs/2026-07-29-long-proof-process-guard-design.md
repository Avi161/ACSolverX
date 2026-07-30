# Long Proof Process Guard Design

## Problem

The existing proof guard safely limits ordinary computations to sixty seconds,
but the independent AK(3) certificate replay now has a theoretically justified
need for a longer bounded run. Raising the ordinary limit would weaken the safe
default and would not prove that the long command passed a short rehearsal,
remained single-threaded, stayed attached to its controller, or stopped under
thermal or process-tree anomalies.

## Chosen design

Extend `scripts/run_proof_guarded.py` with an explicit `--long-run` mode. Short
mode remains unchanged: thirty seconds by default and sixty seconds maximum.
Long mode accepts an experiment timeout greater than sixty and at most six
hundred seconds, a positive preflight timeout at most sixty seconds, and a
progress interval from one through sixty seconds.

One invocation holds the existing singleton lock across two executions of the
exact same argument vector:

1. The preflight receives `ACSOLVERX_PROOF_PHASE=preflight`. It must exit zero
   within its limit and leave no member of its exact process group alive.
2. Only then does the experiment receive
   `ACSOLVERX_PROOF_PHASE=experiment`. It may run for at most six hundred
   seconds and must also leave no group member alive.

The phase variable lets one proof entry point choose a deterministic small
input for rehearsal and the full input for the experiment. The executable,
script path, and all command arguments remain byte-for-byte identical. The
singleton lock spans both phases, so another guarded command cannot enter
between them.

Every child is launched in the foreground with inherited I/O, `shell=False`,
one new session/process group, and all supported numerical thread variables set
to `1`. The runner never starts a detached or background job. It records no
command arguments in the lock or progress output.

Only the root Codex controller is authorized to launch long mode. Subagents may
prepare or review the command and proof code, but they may not start the
preflight or experiment. Exactly one foreground invocation and one numerical
CPU thread are allowed.

## Live safety monitor

Long mode samples the process table once per second without reading command
arguments or environments. `ps` is requested only for PID, PPID, process-group
ID, CPU percentage, state, and executable name. It fails closed if that bounded
process-table read cannot be inspected or parsed.

The runner aborts the exact active preflight or experiment process group when
any of these occurs:

- the original controller PID disappears or becomes a zombie, or the phase
  leader is reparented away from that controller;
- a descendant escapes the active phase's process group;
- the whole exact process group exceeds 125 percent aggregate CPU for three
  consecutive samples, which is incompatible with sustained one-thread work;
- macOS `NSProcessInfo.thermalState` is anything other than nominal, or the
  thermal state cannot be read; or
- the runner receives `SIGHUP`, `SIGTERM`, or an interactive interrupt.

The controller does not call Foundation in-process. For each sample it launches
the guard itself in a bounded internal thermal-helper mode, using only the fixed
argument vector of the current Python executable, the guard's absolute path,
and `--internal-thermal-probe`. The helper runs in its own process group with
the same one-thread environment, bypasses the proof lock and long-run recursion,
and alone calls `NSProcessInfo.thermalState` through Foundation and `ctypes`.
`pmset -g therm` is not used because it can return status zero while printing
only IOKit errors in the Codex execution environment.

Thermal probing and the following `ps` read share one absolute monotonic sample
deadline, itself bounded by the phase timeout, the next progress boundary, and
the monitor's two-second sample budget. The thermal helper receives only the
time remaining to that deadline. A helper deadline or timeout first emits the
fixed, PID-free safety transition and then cleans only the helper's exact group
with `SIGTERM`, using `SIGKILL` only if that group survives the fixed grace
period. Probe output, cleanup errors, and exception chains are sanitized so
they cannot disclose helper arguments, PIDs, or captured failure details.

An escaped descendant is reported but not signalled because it is no longer in
the exact child group. The controller stops the known group, returns a safety
failure, and the mandatory post-run OS audit resolves the escaped PID before any
further computation. This preserves the prohibition on killing an ambiguous
shell, application, or unrelated process.

At each phase start and at every configured one-to-sixty-second boundary during
the experiment, the runner prints and flushes phase, elapsed time, exact-group
process count, aggregate CPU, and thermal state. It never prints the command or
environment. The Codex controller also polls the foreground command often
enough to give the user a progress update within every sixty-second window.

## Cleanup and outcomes

Every phase stop path sends `SIGTERM` to `os.killpg(child.pid, ...)`, waits the
bounded grace period, verifies the exact group is gone, and uses `SIGKILL` only
if that same group ignored `SIGTERM`. Apart from separately cleaning the exact
internal helper group, the active phase PGID is the only authorized signal
target. The guard never signals its parent, its own group, an escaped PID, the
controlling shell, Codex/ChatGPT, a terminal, or application infrastructure.

Long-mode exit statuses are:

- `0` (or the experiment's nonzero status): completed experiment;
- `73`: singleton lock already held;
- `124`: experiment timeout;
- `125`: preflight failed or timed out, so the experiment did not start;
- `126`: safety monitor or cleanup invariant failed;
- `2`: invalid command-line limits.

An unavailable experiment executable returns `127`; an unavailable or otherwise
nonzero preflight maps to `125`. Controller interruption returns the conventional
`128 + signal` status after exact-group cleanup.

After every long invocation, the root controller independently verifies that the
exact child group is absent, the guard lock is absent, and no stale project
Python, pytest, uv, or Numba process remains. A timeout fingerprint is recorded
in the experiment memo, and project policy forbids rerunning that unchanged
experiment. Every timeout, nonzero completion, safety stop, or other unsuccessful
result is only a bounded failure and is never evidence against AC or stable AC.
The root controller immediately commits the bounded result, binds the mandatory
push log, and pushes it before any further proof computation.

## Alternatives rejected

- Raising the ordinary maximum to six hundred seconds: this would make an
  accidental long run easy and would omit the preflight gate.
- Separate preflight and experiment invocations: the command or code could
  change between them, and another computation could acquire the lock.
- A reusable preflight receipt: a stale receipt can be paired with a different
  working tree, dependency state, or command.
- Killing every descendant by PID: an escaped or reparented PID may be
  ambiguous. Only the exact active phase PGID, plus the internal helper's exact
  PGID while cleaning that helper, is an authorized signal target.

## Verification

The focused guard suite is the only computation allowed to invoke the guard
directly. Synthetic tests must prove argument validation, exact-command
two-phase execution, failed-preflight exclusion, phase and one-thread
environments, timeout mappings, progress output, thermal/CPU/controller/escaped
descendant safety aborts, exact-group cleanup, singleton locking across phases,
and lock removal. The suite itself must remain a short foreground run.
