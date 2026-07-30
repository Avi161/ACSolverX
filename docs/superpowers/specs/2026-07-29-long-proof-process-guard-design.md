# Long Proof Process Guard Design

## Problem

The existing proof guard safely limits ordinary computations to sixty seconds,
but the independent AK(3) certificate replay now has a theoretically justified
need for a longer bounded run. Raising the ordinary limit would weaken the safe
default and would not prove that the long command passed a short rehearsal,
remained single-threaded, preserved its direct launcher/coordinator/phase-leader
chain, or stopped under thermal or process-tree anomalies.

## Chosen design

Extend `scripts/run_proof_guarded.py` with an explicit `--long-run` mode. Short
mode remains unchanged: every computational proof, checker, census, test, or
search runs as the single foreground guarded computation, with a thirty-second
default and sixty-second maximum. An unchanged timed-out command may not be
rerun. The focused guard suite is the sole direct-run exception because it must
acquire and contest the singleton itself.
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

Every preflight and experiment child is launched in the foreground with
inherited I/O, `shell=False`, one new session/process group, and all supported
numerical thread variables set to `1`. The runner never starts a detached or
background job. It records no command arguments in the lock or progress output.

Four actors must remain distinct. The procedural root Codex launcher is the only
actor authorized to start long mode. The guard captures the PID of its direct OS
launcher before argument parsing, the guard process itself is the coordinator,
and each preflight or experiment session leader is a phase leader. Before
preflight and during each phase, the guard checks that the captured launcher is
alive and directly parents the coordinator, and that the coordinator is alive
and directly parents the current phase leader. This verifies the observed OS
parent chain but cannot cryptographically prove that the captured direct
launcher belongs to root Codex. Subagents may prepare or review the command and
proof code, but they may not start either phase. Exactly one foreground
invocation and one numerical CPU thread are allowed.

## Live safety monitor

Long mode samples the process table once per second without reading command
arguments or environments. `ps` is requested only for PID, PPID, process-group
ID, CPU percentage, state, and executable name. It fails closed if that bounded
process-table read cannot be inspected or parsed.

The guard coordinator aborts the exact active preflight or experiment process
group when any of these occurs:

- the captured direct OS launcher or guard coordinator disappears or becomes a
  zombie, the coordinator is reparented away from that launcher, or the phase
  leader disappears or is reparented away from the coordinator;
- a descendant escapes the active phase's process group;
- the whole exact process group exceeds 125 percent aggregate CPU for three
  consecutive samples, which is incompatible with sustained one-thread work;
- macOS `NSProcessInfo.thermalState` is anything other than nominal, or the
  thermal state cannot be read; or
- the runner receives `SIGHUP`, `SIGTERM`, or an interactive interrupt.

The guard coordinator does not call Foundation in-process. For each sample it
launches the guard itself in a bounded internal thermal-helper mode, using only
the fixed argument vector of the current Python executable, the guard's absolute
path, and `--internal-thermal-probe`. The helper runs in its own process group
with the same one-thread environment, bypasses the proof lock and long-run
recursion, and alone calls `NSProcessInfo.thermalState` through Foundation and
`ctypes`.
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
the exact child group. The guard coordinator stops the known group, returns a
safety failure, and the mandatory post-run OS audit resolves the escaped PID
before any further computation. This preserves the prohibition on killing an
ambiguous shell, application, or unrelated process.

At each phase start and at every configured one-to-sixty-second boundary during
the experiment, the runner prints and flushes phase, elapsed time, exact-group
process count, aggregate CPU, and thermal state. It never prints the command or
environment. The procedural root Codex launcher also polls the foreground
command often enough to give the user a progress update within every
sixty-second window.

## Cleanup and outcomes

Every phase stop path sends `SIGTERM` to `os.killpg(child.pid, ...)`, waits the
bounded grace period, verifies the exact group is gone, and uses `SIGKILL` only
if that same group ignored `SIGTERM`. Apart from separately cleaning the exact
internal helper group, the active phase PGID is the only authorized signal
target. The guard never signals its parent, its own group, an escaped PID, the
controlling shell, Codex/ChatGPT, a terminal, or application infrastructure.

Long-mode exit statuses transport these ordinary outcomes:

- `0` (or the experiment's nonzero status): completed experiment;
- `73`: singleton lock already held;
- `124`: experiment timeout;
- `125`: preflight failed or timed out, so the experiment did not start;
- `126`: safety monitor or cleanup invariant failed;
- `2`: invalid command-line limits.

An unavailable experiment executable returns `127`; an unavailable or otherwise
nonzero preflight maps to `125`. Interruption returns the conventional
`128 + signal` status after exact-group cleanup. These numbers are not
semantically authoritative: the guard preserves a completed experiment child's
exit status, so a child may collide with `73`, `124`, `125`, or `126`.

After acquiring the singleton, long mode atomically replaces stale audit state
with a fresh mode-`0600` `.scratch/process-guard/last-run.json` whose `run_id`
matches the active lock. The in-progress record contains fresh start time and
captured launcher/coordinator provenance. While still holding the singleton,
the guard rechecks every observed preflight and experiment PGID, changes the
record to `state=finalized`, and atomically writes the semantic `classification`,
top-level `guard_status` and `return_status`, and each phase's `outcome`, PGID,
`guard_status`, `child_exit_status`, and `exact_group_absent`. It records
`lock_release_pending: true`, then releases the singleton and never rewrites the
shared audit after release. A duplicate attempt returning `73` never creates or
changes an audit, so its caller must not mistake the active owner's record for a
result of the duplicate attempt.

For each completed long invocation, the procedural root Codex launcher snapshots
the prior audit provenance and invocation start, then requires the resulting
mode-`0600` record to be fresh, `finalized`, and matched to that invocation by
its new `run_id`, timestamps, and captured launcher/coordinator provenance. It
derives the outcome from `classification` and the top-level and per-phase fields,
not from numeric return status alone. It independently requires
`.scratch/process-guard/active.json` to be absent after return and performs an
external safe-field scan for stale project Python, pytest, uv, or Numba
processes. The exact audit covers all observed phase PGIDs, but one-second
sampling cannot exclude an unobserved double fork; the external scan is
therefore mandatory.

An absent, stale, still-`in_progress`, provenance-mismatched, non-private,
incomplete, or unwritable final audit is an unsuccessful bounded audit/write
stop. Every failed or timed-out preflight, experiment timeout, nonzero child
exit, interruption, thermal or process stop, safety or cleanup failure, audit or
write stop, and every other unsuccessful bounded result is only a bounded
failure and is never evidence against AC or stable AC. Project policy forbids
rerunning an unchanged timed-out experiment. The procedural root Codex launcher
immediately commits the bounded result, binds the mandatory push log, and pushes
it before any further proof computation.

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
environments, timeout mappings, progress output, thermal/CPU/ancestry/escaped
descendant safety aborts, direct launcher/coordinator/phase-leader ancestry,
exact-group cleanup, singleton locking across phases, private audit provenance
and finalization, colliding child-status disambiguation, duplicate audit
isolation, and lock removal. The suite itself must remain a short foreground
run.
