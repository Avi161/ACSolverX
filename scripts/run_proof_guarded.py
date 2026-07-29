from __future__ import annotations

import argparse
import ctypes
import errno
import json
import math
import os
import signal
import subprocess
import sys
import time
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from types import FrameType
from typing import Callable

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = PROJECT_ROOT / ".scratch" / "process-guard" / "active.json"
DEFAULT_TIMEOUT_SECONDS = 30.0
MAX_TIMEOUT_SECONDS = 60.0
MAX_LONG_TIMEOUT_SECONDS = 600.0
DEFAULT_PREFLIGHT_SECONDS = 60.0
DEFAULT_PROGRESS_SECONDS = 60.0
DEFAULT_GRACE_SECONDS = 2.0
MAX_GRACE_SECONDS = 5.0
DUPLICATE_EXIT = 73
TIMEOUT_EXIT = 124
PREFLIGHT_EXIT = 125
SAFETY_EXIT = 126
SAFETY_SAMPLE_SECONDS = 1.0
MAX_GROUP_CPU_PERCENT = 125.0
MAX_CONSECUTIVE_HIGH_CPU_SAMPLES = 3
THREAD_ENV = (
    "NUMBA_NUM_THREADS",
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
)


class LockHeldError(RuntimeError):
    pass


class GuardSignal(Exception):
    def __init__(self, signum: int) -> None:
        super().__init__(signum)
        self.signum = signum


@dataclass(frozen=True)
class ProcessInfo:
    pid: int
    ppid: int
    pgid: int
    cpu_percent: float
    state: str
    ucomm: str


@dataclass(frozen=True)
class SafetySample:
    thermal_state: int | None
    controller_alive: bool
    child_reparented: bool
    group_process_count: int
    group_cpu_percent: float
    escaped_pids: tuple[int, ...]
    error: str | None = None

    @property
    def failure_reason(self) -> str | None:
        if self.error is not None:
            return f"sampling failed: {self.error}"
        if self.thermal_state != 0:
            return f"macOS thermal state {self.thermal_state!r} is not nominal"
        if not self.controller_alive:
            return "controller process is no longer alive"
        if self.child_reparented:
            return "phase leader was reparented away from the controller"
        if self.escaped_pids:
            escaped = ", ".join(str(pid) for pid in self.escaped_pids)
            return f"descendant escaped the phase process group: PID {escaped}"
        return None


def read_macos_thermal_state() -> int:
    if sys.platform != "darwin":
        raise RuntimeError("macOS thermal monitoring requires macOS")

    try:
        ctypes.CDLL(
            "/System/Library/Frameworks/Foundation.framework/Foundation"
        )
        objc = ctypes.CDLL("/usr/lib/libobjc.A.dylib")
        objc.objc_getClass.argtypes = [ctypes.c_char_p]
        objc.objc_getClass.restype = ctypes.c_void_p
        objc.sel_registerName.argtypes = [ctypes.c_char_p]
        objc.sel_registerName.restype = ctypes.c_void_p

        process_info_class = objc.objc_getClass(b"NSProcessInfo")
        process_info_selector = objc.sel_registerName(b"processInfo")
        thermal_state_selector = objc.sel_registerName(b"thermalState")
        message_send_address = ctypes.cast(
            objc.objc_msgSend, ctypes.c_void_p
        ).value
        if not all(
            (
                process_info_class,
                process_info_selector,
                thermal_state_selector,
                message_send_address,
            )
        ):
            raise RuntimeError("required Objective-C thermal symbols are unavailable")

        send_object = ctypes.CFUNCTYPE(
            ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p
        )(message_send_address)
        send_integer = ctypes.CFUNCTYPE(
            ctypes.c_long, ctypes.c_void_p, ctypes.c_void_p
        )(message_send_address)
        process_info = send_object(process_info_class, process_info_selector)
        if not process_info:
            raise RuntimeError("NSProcessInfo.processInfo returned nil")
        thermal_state = int(send_integer(process_info, thermal_state_selector))
    except (GuardSignal, KeyboardInterrupt):
        raise
    except RuntimeError:
        raise
    except Exception as exc:
        raise RuntimeError(f"macOS thermal API failure: {exc}") from exc

    if thermal_state not in (0, 1, 2, 3):
        raise RuntimeError(
            f"macOS thermal API returned unexpected state {thermal_state}"
        )
    if thermal_state != 0:
        raise RuntimeError(f"macOS thermal state {thermal_state} is not nominal")
    return thermal_state


def _read_process_table() -> tuple[ProcessInfo, ...]:
    try:
        result = subprocess.run(
            ["ps", "-axo", "pid=,ppid=,pgid=,%cpu=,state=,ucomm="],
            check=True,
            capture_output=True,
            text=True,
            timeout=2.0,
        )
        processes: list[ProcessInfo] = []
        seen_pids: set[int] = set()
        for line_number, line in enumerate(result.stdout.splitlines(), start=1):
            fields = line.split(None, 5)
            if len(fields) != 6:
                raise ValueError(f"malformed ps row {line_number}")
            pid = int(fields[0])
            ppid = int(fields[1])
            pgid = int(fields[2])
            cpu_percent = float(fields[3])
            if pid <= 0 or ppid < 0 or pgid <= 0:
                raise ValueError(f"invalid process identity in ps row {line_number}")
            if not math.isfinite(cpu_percent) or cpu_percent < 0:
                raise ValueError(f"invalid CPU value in ps row {line_number}")
            if pid in seen_pids:
                raise ValueError(f"duplicate PID in ps row {line_number}")
            seen_pids.add(pid)
            processes.append(
                ProcessInfo(
                    pid=pid,
                    ppid=ppid,
                    pgid=pgid,
                    cpu_percent=cpu_percent,
                    state=fields[4],
                    ucomm=fields[5],
                )
            )
        return tuple(processes)
    except (
        OSError,
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
        ValueError,
    ) as exc:
        raise RuntimeError(f"could not read the process table: {exc}") from exc


class SafetyMonitor:
    def __init__(
        self,
        process_reader: Callable[[], Sequence[ProcessInfo]] = _read_process_table,
        thermal_reader: Callable[[], int] = read_macos_thermal_state,
    ) -> None:
        self._process_reader = process_reader
        self._thermal_reader = thermal_reader

    def sample(
        self,
        child_pid: int,
        process_group_id: int,
        controller_pid: int,
    ) -> SafetySample:
        try:
            thermal_state = self._thermal_reader()
        except (GuardSignal, KeyboardInterrupt):
            raise
        except Exception as exc:
            return SafetySample(
                thermal_state=None,
                controller_alive=False,
                child_reparented=False,
                group_process_count=0,
                group_cpu_percent=0.0,
                escaped_pids=(),
                error=str(exc),
            )
        if thermal_state != 0:
            return SafetySample(
                thermal_state=thermal_state,
                controller_alive=False,
                child_reparented=False,
                group_process_count=0,
                group_cpu_percent=0.0,
                escaped_pids=(),
            )

        try:
            processes = tuple(self._process_reader())
            by_pid = {process.pid: process for process in processes}
            if len(by_pid) != len(processes):
                raise RuntimeError("process table contains duplicate PIDs")
            phase_leader = by_pid.get(child_pid)
            if phase_leader is None:
                raise RuntimeError(f"phase leader PID {child_pid} is missing")

            children_by_parent: dict[int, list[int]] = {}
            for process in processes:
                children_by_parent.setdefault(process.ppid, []).append(process.pid)
            descendants: set[int] = set()
            pending = [child_pid]
            while pending:
                pid = pending.pop()
                if pid in descendants:
                    continue
                descendants.add(pid)
                pending.extend(children_by_parent.get(pid, ()))

            group_processes = tuple(
                process
                for process in processes
                if process.pgid == process_group_id
            )
            escaped_pids = tuple(
                sorted(
                    pid
                    for pid in descendants
                    if by_pid[pid].pgid != process_group_id
                )
            )
            controller = by_pid.get(controller_pid)
            return SafetySample(
                thermal_state=thermal_state,
                controller_alive=(
                    controller is not None and "Z" not in controller.state
                ),
                child_reparented=phase_leader.ppid != controller_pid,
                group_process_count=len(group_processes),
                group_cpu_percent=sum(
                    process.cpu_percent for process in group_processes
                ),
                escaped_pids=escaped_pids,
            )
        except (GuardSignal, KeyboardInterrupt):
            raise
        except Exception as exc:
            return SafetySample(
                thermal_state=thermal_state,
                controller_alive=False,
                child_reparented=False,
                group_process_count=0,
                group_cpu_percent=0.0,
                escaped_pids=(),
                error=str(exc),
            )


def process_exists(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError as exc:
        if exc.errno == errno.ESRCH:
            return False
        if exc.errno == errno.EPERM:
            return True
        raise
    return True


class ProcessLock:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._identity: tuple[int, int] | None = None

    def acquire(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        for _ in range(2):
            try:
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            except FileExistsError:
                identity, owner_pid = self._read_owner()
                if process_exists(owner_pid):
                    raise LockHeldError(f"proof runner PID {owner_pid} already owns the guard")
                self._unlink_if_identity(identity)
                continue

            stat_result = os.fstat(fd)
            self._identity = (stat_result.st_dev, stat_result.st_ino)
            payload = {
                "pid": os.getpid(),
                "started_at": datetime.now(timezone.utc).isoformat(),
                "worktree": str(PROJECT_ROOT),
            }
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as stream:
                    json.dump(payload, stream, sort_keys=True)
                    stream.write("\n")
                    stream.flush()
                    os.fsync(stream.fileno())
            except BaseException:
                self.release()
                raise
            return
        raise LockHeldError("proof guard changed while reclaiming a dead-owner lock")

    def _read_owner(self) -> tuple[tuple[int, int], int]:
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        try:
            fd = os.open(self.path, flags)
        except FileNotFoundError:
            return self._read_owner()
        try:
            stat_result = os.fstat(fd)
            with os.fdopen(fd, encoding="utf-8") as stream:
                payload = json.load(stream)
            owner_pid = payload["pid"]
            if not isinstance(owner_pid, int) or owner_pid <= 0:
                raise ValueError("invalid lock owner")
            return (stat_result.st_dev, stat_result.st_ino), owner_pid
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise LockHeldError("existing proof guard is unreadable; refusing to start") from exc

    def _unlink_if_identity(self, identity: tuple[int, int]) -> None:
        try:
            stat_result = self.path.lstat()
        except FileNotFoundError:
            return
        if (stat_result.st_dev, stat_result.st_ino) == identity:
            self.path.unlink()

    def release(self) -> None:
        if self._identity is None:
            return
        self._unlink_if_identity(self._identity)
        self._identity = None


def group_exists(process_group_id: int) -> bool:
    try:
        os.killpg(process_group_id, 0)
    except OSError as exc:
        if exc.errno == errno.ESRCH:
            return False
        if exc.errno == errno.EPERM:
            return True
        raise
    return True


def terminate_group(child: subprocess.Popen[bytes], grace_seconds: float) -> None:
    process_group_id = child.pid
    try:
        os.killpg(process_group_id, signal.SIGTERM)
    except ProcessLookupError:
        child.poll()
        return

    deadline = time.monotonic() + grace_seconds
    while time.monotonic() < deadline:
        child.poll()
        if not group_exists(process_group_id):
            return
        time.sleep(0.01)

    if group_exists(process_group_id):
        try:
            os.killpg(process_group_id, signal.SIGKILL)
        except ProcessLookupError:
            child.poll()
            return
    try:
        child.wait(timeout=max(grace_seconds, 0.1))
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"process group {process_group_id} survived SIGKILL") from exc


def limited_environment(phase: str | None = None) -> dict[str, str]:
    environment = os.environ.copy()
    for name in THREAD_ENV:
        environment[name] = "1"
    if phase is not None:
        environment["ACSOLVERX_PROOF_PHASE"] = phase
    return environment


def run_guarded(
    command: Sequence[str], timeout_seconds: float, grace_seconds: float
) -> int:
    try:
        child = subprocess.Popen(
            list(command),
            cwd=PROJECT_ROOT,
            env=limited_environment(),
            shell=False,
            start_new_session=True,
        )
    except OSError as exc:
        print(f"proof guard could not start the command: {exc.strerror}", file=sys.stderr)
        return 127

    try:
        return_code = child.wait(timeout=timeout_seconds)
        if group_exists(child.pid):
            terminate_group(child, grace_seconds)
        return return_code
    except subprocess.TimeoutExpired:
        terminate_group(child, grace_seconds)
        print(
            f"proof guard stopped process group {child.pid} after {timeout_seconds:g} seconds",
            file=sys.stderr,
        )
        return TIMEOUT_EXIT
    except BaseException:
        terminate_group(child, grace_seconds)
        raise


def _clean_exact_group(
    child: subprocess.Popen[bytes], grace_seconds: float
) -> bool:
    try:
        terminate_group(child, grace_seconds)
    except RuntimeError as exc:
        print(f"proof guard cleanup failed: {exc}", file=sys.stderr)
        return False
    if group_exists(child.pid):
        print(
            f"proof guard cleanup left process group {child.pid} alive",
            file=sys.stderr,
        )
        return False
    return True


def _run_long_phase(
    command: Sequence[str],
    phase: str,
    timeout_seconds: float,
    progress_seconds: float,
    grace_seconds: float,
    monitor: object | None,
) -> tuple[int, bool]:
    del progress_seconds
    try:
        child = subprocess.Popen(
            list(command),
            cwd=PROJECT_ROOT,
            env=limited_environment(phase),
            shell=False,
            start_new_session=True,
        )
    except OSError as exc:
        print(f"proof guard could not start the command: {exc.strerror}", file=sys.stderr)
        return 127, False

    try:
        deadline = time.monotonic() + timeout_seconds
        next_sample_at = time.monotonic()
        consecutive_high_cpu_samples = 0
        while True:
            return_code = child.poll()
            if return_code is not None:
                if group_exists(child.pid):
                    _clean_exact_group(child, grace_seconds)
                    print(
                        f"proof guard found a lingering {phase} process group "
                        f"{child.pid}",
                        file=sys.stderr,
                    )
                    return SAFETY_EXIT, True
                return return_code, False

            now = time.monotonic()
            safety_failure: str | None = None
            if monitor is not None and now >= next_sample_at:
                try:
                    sample = monitor.sample(
                        child_pid=child.pid,
                        process_group_id=child.pid,
                        controller_pid=os.getpid(),
                    )
                    if not isinstance(sample, SafetySample):
                        raise RuntimeError("monitor returned an invalid safety sample")
                except (GuardSignal, KeyboardInterrupt):
                    raise
                except Exception as exc:
                    safety_failure = f"sampling failed: {exc}"
                else:
                    safety_failure = sample.failure_reason
                    if sample.group_cpu_percent > MAX_GROUP_CPU_PERCENT:
                        consecutive_high_cpu_samples += 1
                    else:
                        consecutive_high_cpu_samples = 0
                    if (
                        safety_failure is None
                        and consecutive_high_cpu_samples
                        >= MAX_CONSECUTIVE_HIGH_CPU_SAMPLES
                    ):
                        safety_failure = (
                            "exact process group exceeded "
                            f"{MAX_GROUP_CPU_PERCENT:g}% CPU for "
                            f"{consecutive_high_cpu_samples} consecutive samples"
                        )
                next_sample_at = now + SAFETY_SAMPLE_SECONDS

            if safety_failure is not None:
                print(
                    f"proof guard safety abort in {phase}: {safety_failure}",
                    file=sys.stderr,
                )
                _clean_exact_group(child, grace_seconds)
                return SAFETY_EXIT, True

            remaining_seconds = deadline - time.monotonic()
            if remaining_seconds <= 0:
                if not _clean_exact_group(child, grace_seconds):
                    return SAFETY_EXIT, True
                print(
                    f"proof guard stopped {phase} process group {child.pid} "
                    f"after {timeout_seconds:g} seconds",
                    file=sys.stderr,
                )
                return TIMEOUT_EXIT, False

            wait_seconds = remaining_seconds
            if monitor is not None:
                wait_seconds = min(
                    wait_seconds,
                    max(0.0, next_sample_at - time.monotonic()),
                )
            if wait_seconds <= 0:
                continue
            try:
                return_code = child.wait(timeout=wait_seconds)
            except subprocess.TimeoutExpired:
                continue
            if group_exists(child.pid):
                _clean_exact_group(child, grace_seconds)
                print(
                    f"proof guard found a lingering {phase} process group {child.pid}",
                    file=sys.stderr,
                )
                return SAFETY_EXIT, True
            return return_code, False
    except BaseException:
        _clean_exact_group(child, grace_seconds)
        raise


def run_long_guarded(
    command: Sequence[str],
    preflight_seconds: float,
    experiment_seconds: float,
    progress_seconds: float,
    grace_seconds: float,
    monitor: object | None,
) -> int:
    preflight_status, cleanup_failed = _run_long_phase(
        command,
        "preflight",
        preflight_seconds,
        progress_seconds,
        grace_seconds,
        monitor,
    )
    if cleanup_failed:
        return SAFETY_EXIT
    if preflight_status != 0:
        return PREFLIGHT_EXIT

    experiment_status, cleanup_failed = _run_long_phase(
        command,
        "experiment",
        experiment_seconds,
        progress_seconds,
        grace_seconds,
        monitor,
    )
    if cleanup_failed:
        return SAFETY_EXIT
    return experiment_status


def parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run one foreground proof command with singleton and timeout guards."
    )
    parser.add_argument(
        "--timeout-seconds", type=float, default=DEFAULT_TIMEOUT_SECONDS
    )
    parser.add_argument("--long-run", action="store_true")
    parser.add_argument(
        "--preflight-seconds", type=float, default=DEFAULT_PREFLIGHT_SECONDS
    )
    parser.add_argument(
        "--progress-seconds", type=float, default=DEFAULT_PROGRESS_SECONDS
    )
    parser.add_argument("--grace-seconds", type=float, default=DEFAULT_GRACE_SECONDS)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    if args.command and args.command[0] == "--":
        args.command = args.command[1:]
    if not args.command:
        parser.error("a command is required after --")
    if not math.isfinite(args.timeout_seconds) or args.timeout_seconds <= 0:
        parser.error("--timeout-seconds must be positive")
    if args.long_run and args.timeout_seconds <= MAX_TIMEOUT_SECONDS:
        parser.error(
            f"--timeout-seconds must exceed {MAX_TIMEOUT_SECONDS:g} seconds in long mode"
        )
    if args.long_run and args.timeout_seconds > MAX_LONG_TIMEOUT_SECONDS:
        parser.error(
            f"--timeout-seconds cannot exceed {MAX_LONG_TIMEOUT_SECONDS:g} seconds"
        )
    if not args.long_run and args.timeout_seconds > MAX_TIMEOUT_SECONDS:
        parser.error(
            f"--timeout-seconds cannot exceed {MAX_TIMEOUT_SECONDS:g} seconds"
        )
    if not math.isfinite(args.preflight_seconds) or args.preflight_seconds <= 0:
        parser.error("--preflight-seconds must be positive")
    if args.preflight_seconds > MAX_TIMEOUT_SECONDS:
        parser.error(
            f"--preflight-seconds cannot exceed {MAX_TIMEOUT_SECONDS:g} seconds"
        )
    if not math.isfinite(args.progress_seconds) or args.progress_seconds <= 0:
        parser.error("--progress-seconds must be positive")
    if args.progress_seconds > MAX_TIMEOUT_SECONDS:
        parser.error(
            f"--progress-seconds cannot exceed {MAX_TIMEOUT_SECONDS:g} seconds"
        )
    if not math.isfinite(args.grace_seconds) or args.grace_seconds <= 0:
        parser.error("--grace-seconds must be positive")
    if args.grace_seconds > MAX_GRACE_SECONDS:
        parser.error(f"--grace-seconds cannot exceed {MAX_GRACE_SECONDS:g} seconds")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    process_lock = ProcessLock(LOCK_PATH)
    previous_handlers: dict[int, signal.Handlers] = {}

    def handle_signal(signum: int, _frame: FrameType | None) -> None:
        raise GuardSignal(signum)

    for signum in (signal.SIGHUP, signal.SIGTERM):
        previous_handlers[signum] = signal.signal(signum, handle_signal)

    try:
        try:
            process_lock.acquire()
        except LockHeldError as exc:
            print(f"proof guard refused duplicate run: {exc}", file=sys.stderr)
            return DUPLICATE_EXIT
        try:
            if args.long_run:
                return run_long_guarded(
                    args.command,
                    args.preflight_seconds,
                    args.timeout_seconds,
                    args.progress_seconds,
                    args.grace_seconds,
                    SafetyMonitor(),
                )
            return run_guarded(
                args.command, args.timeout_seconds, args.grace_seconds
            )
        except GuardSignal as exc:
            return 128 + exc.signum
        except KeyboardInterrupt:
            return 128 + signal.SIGINT
        finally:
            process_lock.release()
    finally:
        for signum, handler in previous_handlers.items():
            signal.signal(signum, handler)


if __name__ == "__main__":
    raise SystemExit(main())
