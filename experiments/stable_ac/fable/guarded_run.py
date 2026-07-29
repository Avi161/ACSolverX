"""Guarded foreground runner for long CPU proof experiments (fable line).

Session policy this implements, verbatim in intent:

  * Maximum runtime: 10 minutes per experiment.
  * First require a successful <=60-second preflight on the same code path.
  * Exactly one experiment at a time, foreground only, through the guarded runner.
  * Use one CPU thread; prohibit detached/background processes.
  * Do not kill the controlling shell, the agent harness, terminal, or application
    infrastructure. Terminate only the experiment's exact child process group.
  * Report progress at least every 60 seconds while it runs.
  * Send SIGTERM first; use SIGKILL only if the exact process group ignores SIGTERM.
  * Never rerun an unchanged timed-out experiment.
  * Stop early on thermal pressure, abnormal CPU behavior, unexpected child
    processes, or loss of the controlling task.
  * After completion or interruption, verify that every child exited, the guard lock
    is gone, and no stale Python/pytest/uv/Numba process remains.

A timeout or an unsuccessful experiment is a bounded engineering outcome. It is NEVER
evidence for or against AC or stable AC, and this module refuses to characterise it as
such: `verdict` is always one of the process-level strings below, never a mathematical
claim.

Deliberately NOT placed at scripts/run_proof_guarded.py: the codex line added a guard at
that exact path, and colliding on it would create a merge conflict for the user. This is
the fable line's own guard, in the fable namespace.

Usage
-----
    # preflight (hard-capped at 60s), on the same code path as the real run
    python3 -m experiments.stable_ac.fable.guarded_run --preflight \
        -- python3 -m experiments.stable_ac.fable.drop_floor_check --max-length 6

    # the real run (hard-capped at 600s); refuses without a matching preflight
    python3 -m experiments.stable_ac.fable.guarded_run --timeout 600 \
        -- python3 -m experiments.stable_ac.fable.drop_floor_check --max-length 8
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------------
# Hard limits. These are ceilings, not defaults, and are not overridable by flags.
# ---------------------------------------------------------------------------------

HARD_MAX_RUNTIME_S = 600          # 10 minutes, per session policy
HARD_MAX_PREFLIGHT_S = 60         # preflight ceiling, per session policy
MAX_HEARTBEAT_S = 60              # progress must be reported at least this often
SIGTERM_GRACE_S = 10              # wait after SIGTERM before considering SIGKILL
STALL_LIMIT_S = 180               # child CPU time frozen this long => hung
THERMAL_LIMIT_C = 95.0            # stop early above this, when readable

REPO_ROOT = Path(__file__).resolve().parents[3]
LOCK_PATH = REPO_ROOT / "results" / "stable_ac" / "fable" / ".guard.lock"
LEDGER_PATH = REPO_ROOT / "results" / "stable_ac" / "fable" / "guard_ledger.jsonl"
LOG_DIR = REPO_ROOT / "results" / "stable_ac" / "fable" / "guard_logs"

# The code path whose contents define "the same code path" for preflight matching and
# for "unchanged" in the never-rerun-a-timeout rule.
CODE_DIR = REPO_ROOT / "experiments" / "stable_ac" / "fable"

SINGLE_THREAD_ENV = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "NUMBA_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
    "JAX_PLATFORMS": "cpu",  # belt and braces; this line never imports JAX
}


# ---------------------------------------------------------------------------------
# Fingerprinting
# ---------------------------------------------------------------------------------

def code_fingerprint(code_dir: Path = CODE_DIR) -> str:
    """SHA-256 over every .py file in the experiment code path.

    Any edit anywhere in the code path changes this. That is intentional: it makes
    "unchanged" conservative in the safe direction — after any code change a timed-out
    experiment may be retried, and a stale preflight stops counting.
    """
    h = hashlib.sha256()
    if code_dir.is_dir():
        for path in sorted(code_dir.rglob("*.py")):
            h.update(path.relative_to(code_dir).as_posix().encode())
            h.update(hashlib.sha256(path.read_bytes()).digest())
    return h.hexdigest()


def command_key(argv: list[str]) -> str:
    return hashlib.sha256("\x00".join(argv).encode()).hexdigest()


def target_module(argv: list[str]) -> str:
    """The experiment's identity for preflight matching: the -m module, else argv[0]."""
    for i, tok in enumerate(argv):
        if tok == "-m" and i + 1 < len(argv):
            return argv[i + 1]
    return argv[0] if argv else ""


# ---------------------------------------------------------------------------------
# Ledger
# ---------------------------------------------------------------------------------

def read_ledger(path: Path = LEDGER_PATH) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def append_ledger(row: dict, path: Path = LEDGER_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as fh:
        fh.write(json.dumps(row, sort_keys=True) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


def timed_out_unchanged(argv: list[str], fp: str, ledger: list[dict]) -> bool:
    """True if this exact command timed out under this exact code fingerprint."""
    key = command_key(argv)
    return any(
        r.get("verdict") == "timeout"
        and r.get("command_key") == key
        and r.get("code_fingerprint") == fp
        for r in ledger
    )


def preflight_ok(argv: list[str], fp: str, ledger: list[dict]) -> bool:
    """True if a preflight for the same module succeeded on this same code path."""
    module = target_module(argv)
    return any(
        r.get("kind") == "preflight"
        and r.get("verdict") == "ok"
        and r.get("code_fingerprint") == fp
        and r.get("target_module") == module
        for r in ledger
    )


# ---------------------------------------------------------------------------------
# Lock: exactly one experiment at a time
# ---------------------------------------------------------------------------------

class GuardLock:
    def __init__(self, path: Path = LOCK_PATH):
        self.path = path
        self.acquired = False

    def acquire(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            holder = self._holder()
            if holder is not None and not _pid_alive(holder):
                # Stale lock from a killed guard: reclaim it, but say so.
                print(f"[guard] reclaiming stale lock from dead pid {holder}", flush=True)
                self.path.unlink(missing_ok=True)
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            else:
                raise SystemExit(
                    f"[guard] REFUSED: another experiment holds {self.path} "
                    f"(pid {holder}). Exactly one experiment at a time."
                )
        with os.fdopen(fd, "w") as fh:
            json.dump({"pid": os.getpid(), "started": time.time()}, fh)
        self.acquired = True

    def _holder(self) -> int | None:
        try:
            return int(json.loads(self.path.read_text())["pid"])
        except Exception:
            return None

    def release(self) -> None:
        if self.acquired:
            self.path.unlink(missing_ok=True)
            self.acquired = False


def _display_path(path: Path) -> str:
    """Repo-relative when inside the repo, absolute otherwise (e.g. tmp dirs in tests)."""
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


# ---------------------------------------------------------------------------------
# Process inspection helpers (no third-party deps)
# ---------------------------------------------------------------------------------

def pgid_members(pgid: int, include_zombies: bool = False) -> list[int]:
    """Live pids in process group `pgid`.

    Zombies are excluded by default. A zombie has already died — it lingers in /proc
    only until its parent reaps it — so counting one as a survivor would escalate a
    clean SIGTERM exit to a needless SIGKILL, and would report `children_exited=False`
    for a child that did exit.
    """
    members = []
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        try:
            stat = (entry / "stat").read_text()
        except (OSError, ValueError):
            continue
        # After the comm field (which may contain spaces and parens) come:
        # tail[0]=state, tail[1]=ppid, tail[2]=pgrp, ..., tail[11]=utime, tail[12]=stime
        try:
            tail = stat[stat.rindex(")") + 2:].split()
            if int(tail[2]) != pgid:
                continue
            if tail[0] == "Z" and not include_zombies:
                continue
            members.append(int(entry.name))
        except (ValueError, IndexError):
            continue
    return members


def child_cpu_seconds(pgid: int) -> float:
    total = 0.0
    ticks = os.sysconf("SC_CLK_TCK")
    for pid in pgid_members(pgid):
        try:
            stat = (Path("/proc") / str(pid) / "stat").read_text()
            tail = stat[stat.rindex(")") + 2:].split()
            total += (int(tail[11]) + int(tail[12])) / ticks  # utime + stime
        except (OSError, ValueError, IndexError):
            continue
    return total


def max_thermal_c() -> float | None:
    temps = []
    for zone in Path("/sys/class/thermal").glob("thermal_zone*/temp"):
        try:
            temps.append(int(zone.read_text().strip()) / 1000.0)
        except (OSError, ValueError):
            continue
    return max(temps) if temps else None


def stale_interpreter_processes(exclude_pgid: int) -> list[str]:
    """Python/pytest/uv/numba processes outside our own tree. REPORTED, never killed."""
    ours = {os.getpid(), os.getppid()}
    out = []
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        pid = int(entry.name)
        if pid in ours:
            continue
        try:
            cmdline = (entry / "cmdline").read_bytes().replace(b"\x00", b" ").decode(
                errors="replace").strip()
            stat = (entry / "stat").read_text()
            pgrp = int(stat[stat.rindex(")") + 2:].split()[2])
        except (OSError, ValueError, IndexError):
            continue
        if pgrp == exclude_pgid or not cmdline:
            continue
        low = cmdline.lower()
        if any(tok in low for tok in ("python", "pytest", "uv ", "numba")):
            out.append(f"pid={pid} pgid={pgrp} {cmdline[:120]}")
    return out


# ---------------------------------------------------------------------------------
# Termination: SIGTERM to the exact child process group, SIGKILL only if ignored
# ---------------------------------------------------------------------------------

def terminate_group(pgid: int, grace_s: float = SIGTERM_GRACE_S) -> dict:
    """Signal ONLY the experiment's process group. Never our own, never the session."""
    own_pgid = os.getpgrp()
    if pgid == own_pgid or pgid <= 1:
        raise RuntimeError(
            f"[guard] REFUSING to signal pgid {pgid}: it is the guard's own group "
            f"({own_pgid}) or an init-adjacent group. This is the check that keeps the "
            f"controlling shell and harness alive."
        )
    report = {"pgid": pgid, "sigterm_sent": False, "sigkill_sent": False}
    try:
        os.killpg(pgid, signal.SIGTERM)
        report["sigterm_sent"] = True
    except ProcessLookupError:
        report["already_gone"] = True
        return report
    deadline = time.monotonic() + grace_s
    while time.monotonic() < deadline:
        if not pgid_members(pgid):
            report["exited_on_sigterm"] = True
            return report
        time.sleep(0.25)
    if pgid_members(pgid):
        try:
            os.killpg(pgid, signal.SIGKILL)
            report["sigkill_sent"] = True
        except ProcessLookupError:
            report["already_gone"] = True
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline and pgid_members(pgid):
            time.sleep(0.25)
    report["survivors"] = pgid_members(pgid)
    return report


# ---------------------------------------------------------------------------------
# The run
# ---------------------------------------------------------------------------------

def run_guarded(
    argv: list[str],
    timeout_s: float,
    heartbeat_s: float = 30.0,
    preflight: bool = False,
    max_children: int = 16,
    log_dir: Path = LOG_DIR,
    lock_path: Path = LOCK_PATH,
    ledger_path: Path = LEDGER_PATH,
    code_dir: Path = CODE_DIR,
    enforce_preflight: bool = True,
) -> dict:
    if not argv:
        raise SystemExit("[guard] nothing to run")

    ceiling = HARD_MAX_PREFLIGHT_S if preflight else HARD_MAX_RUNTIME_S
    if timeout_s > ceiling:
        raise SystemExit(
            f"[guard] REFUSED: requested timeout {timeout_s}s exceeds the hard "
            f"{'preflight ' if preflight else ''}ceiling of {ceiling}s."
        )
    if heartbeat_s > MAX_HEARTBEAT_S:
        raise SystemExit(
            f"[guard] REFUSED: heartbeat {heartbeat_s}s exceeds the {MAX_HEARTBEAT_S}s "
            f"progress-reporting requirement."
        )

    fp = code_fingerprint(code_dir)
    ledger = read_ledger(ledger_path)

    if timed_out_unchanged(argv, fp, ledger):
        raise SystemExit(
            "[guard] REFUSED: this exact command already timed out on this exact code "
            "path. Policy forbids rerunning an unchanged timed-out experiment — change "
            "the code, shrink the corpus, or run a different experiment."
        )
    if not preflight and enforce_preflight and not preflight_ok(argv, fp, ledger):
        raise SystemExit(
            f"[guard] REFUSED: no successful preflight recorded for module "
            f"'{target_module(argv)}' on this code path (fingerprint {fp[:12]}). "
            f"Run with --preflight and a smaller corpus first."
        )

    env = dict(os.environ)
    env.update(SINGLE_THREAD_ENV)

    log_dir.mkdir(parents=True, exist_ok=True)
    started_wall = time.time()
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime(started_wall))
    tag = "preflight" if preflight else "run"
    out_path = log_dir / f"{tag}-{stamp}-{command_key(argv)[:8]}.log"

    print(f"[guard] {tag}: {' '.join(argv)}", flush=True)
    print(f"[guard] timeout={timeout_s}s heartbeat={heartbeat_s}s "
          f"code_fingerprint={fp[:12]} single-thread=on", flush=True)
    print(f"[guard] child stdout+stderr -> {out_path}", flush=True)

    lock = GuardLock(lock_path)
    lock.acquire()

    verdict = "error"
    stop_reason = None
    proc = None
    pgid = None
    term_report: dict = {}
    peak_children = 0
    thermal_peak = max_thermal_c()

    try:
        with out_path.open("wb") as sink:
            # start_new_session=True => the child is its own session and group leader,
            # so pgid == proc.pid and we can signal exactly that group and nothing else.
            proc = subprocess.Popen(
                argv, cwd=str(REPO_ROOT), env=env, stdout=sink,
                stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                start_new_session=True,
            )
            pgid = proc.pid
            begin = time.monotonic()
            last_beat = begin
            last_cpu = 0.0
            last_cpu_change = begin

            while True:
                rc = proc.poll()
                if rc is not None:
                    verdict = "ok" if rc == 0 else "nonzero_exit"
                    break

                now = time.monotonic()
                elapsed = now - begin

                if elapsed > timeout_s:
                    verdict, stop_reason = "timeout", f"exceeded {timeout_s}s"
                    break

                members = pgid_members(pgid)
                peak_children = max(peak_children, len(members))
                if len(members) > max_children:
                    verdict, stop_reason = "stopped_early", (
                        f"unexpected child processes: {len(members)} in the experiment "
                        f"group exceeds max_children={max_children}")
                    break

                cpu = child_cpu_seconds(pgid)
                if cpu > last_cpu + 0.05:
                    last_cpu, last_cpu_change = cpu, now
                elif now - last_cpu_change > STALL_LIMIT_S:
                    verdict, stop_reason = "stopped_early", (
                        f"abnormal CPU behaviour: child CPU time frozen at {cpu:.1f}s "
                        f"for {STALL_LIMIT_S}s while wall clock advanced")
                    break

                temp = max_thermal_c()
                if temp is not None:
                    thermal_peak = max(thermal_peak or temp, temp)
                    if temp >= THERMAL_LIMIT_C:
                        verdict, stop_reason = "stopped_early", (
                            f"thermal pressure: {temp:.1f}C >= {THERMAL_LIMIT_C}C")
                        break

                if os.getppid() == 1:
                    verdict, stop_reason = "stopped_early", (
                        "lost the controlling task (guard was reparented to init)")
                    break

                if now - last_beat >= heartbeat_s:
                    last_beat = now
                    tail = ""
                    try:
                        data = out_path.read_bytes()[-200:].decode(errors="replace")
                        tail = data.strip().splitlines()[-1][:100] if data.strip() else ""
                    except OSError:
                        pass
                    print(f"[guard] +{elapsed:6.1f}s cpu={cpu:7.1f}s "
                          f"procs={len(members)}"
                          + (f" temp={temp:.1f}C" if temp is not None else "")
                          + (f" | {tail}" if tail else ""), flush=True)

                time.sleep(0.5)

        if verdict in ("timeout", "stopped_early"):
            print(f"[guard] STOPPING: {stop_reason}", flush=True)
            term_report = terminate_group(pgid)
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass

    except KeyboardInterrupt:
        verdict, stop_reason = "interrupted", "KeyboardInterrupt"
        if pgid:
            term_report = terminate_group(pgid)
    finally:
        # Post-run verification, per policy: children gone, lock gone, no stale
        # interpreters. Runs on every path, including exceptions.
        survivors = pgid_members(pgid) if pgid else []
        lock.release()
        lock_gone = not lock_path.exists()
        stale = stale_interpreter_processes(pgid or -1)

        elapsed_total = time.time() - started_wall
        record = {
            "kind": "preflight" if preflight else "run",
            "verdict": verdict,
            "stop_reason": stop_reason,
            "command": argv,
            "command_key": command_key(argv),
            "target_module": target_module(argv),
            "code_fingerprint": fp,
            "timeout_s": timeout_s,
            "elapsed_s": round(elapsed_total, 2),
            "returncode": proc.returncode if proc else None,
            "child_pgid": pgid,
            "peak_processes_in_group": peak_children,
            "termination": term_report,
            "cleanup_verified": {
                "children_exited": survivors == [],
                "surviving_pids": survivors,
                "lock_removed": lock_gone,
                "stale_interpreters": stale,
            },
            "thermal_peak_c": thermal_peak,
            "log": _display_path(out_path),
            "started_utc": stamp,
            "note": (
                "verdict is a PROCESS outcome. A timeout or nonzero exit is a bounded "
                "engineering result and is not evidence for or against AC or stable AC."
            ),
        }
        append_ledger(record, ledger_path)

        print(f"[guard] verdict={verdict} elapsed={elapsed_total:.1f}s "
              f"rc={record['returncode']}", flush=True)
        print(f"[guard] cleanup: children_exited={survivors == []} "
              f"lock_removed={lock_gone} stale_interpreters={len(stale)}", flush=True)
        for line in stale:
            print(f"[guard]   stale (reported, NOT killed): {line}", flush=True)
        if survivors:
            print(f"[guard] WARNING surviving pids in experiment group: {survivors}",
                  flush=True)

    return record


def main(cli: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Guarded foreground runner for long CPU proof experiments.")
    parser.add_argument("--timeout", type=float, default=None,
                        help=f"seconds; ceiling {HARD_MAX_RUNTIME_S} "
                             f"({HARD_MAX_PREFLIGHT_S} for --preflight)")
    parser.add_argument("--heartbeat", type=float, default=30.0,
                        help=f"progress interval, max {MAX_HEARTBEAT_S}s")
    parser.add_argument("--preflight", action="store_true",
                        help="short validation run on the same code path")
    parser.add_argument("--max-children", type=int, default=16)
    parser.add_argument("command", nargs=argparse.REMAINDER,
                        help="-- followed by the command to run")
    args = parser.parse_args(cli)

    argv = args.command
    if argv and argv[0] == "--":
        argv = argv[1:]
    if not argv:
        parser.error("no command given; use: guarded_run [opts] -- python3 -m module ...")

    timeout = args.timeout
    if timeout is None:
        timeout = HARD_MAX_PREFLIGHT_S if args.preflight else HARD_MAX_RUNTIME_S

    record = run_guarded(
        argv, timeout_s=timeout, heartbeat_s=args.heartbeat,
        preflight=args.preflight, max_children=args.max_children,
    )
    return 0 if record["verdict"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
