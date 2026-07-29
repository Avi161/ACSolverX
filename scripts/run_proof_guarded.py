from __future__ import annotations

import argparse
import errno
import json
import math
import os
import signal
import subprocess
import sys
import time
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path
from types import FrameType

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = PROJECT_ROOT / ".scratch" / "process-guard" / "active.json"
DEFAULT_TIMEOUT_SECONDS = 30.0
MAX_TIMEOUT_SECONDS = 60.0
DEFAULT_GRACE_SECONDS = 2.0
MAX_GRACE_SECONDS = 5.0
DUPLICATE_EXIT = 73
TIMEOUT_EXIT = 124
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
        os.killpg(process_group_id, signal.SIGKILL)
    try:
        child.wait(timeout=max(grace_seconds, 0.1))
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"process group {process_group_id} survived SIGKILL") from exc


def limited_environment() -> dict[str, str]:
    environment = os.environ.copy()
    for name in THREAD_ENV:
        environment[name] = "1"
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


def parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run one foreground proof command with singleton and timeout guards."
    )
    parser.add_argument(
        "--timeout-seconds", type=float, default=DEFAULT_TIMEOUT_SECONDS
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
    if args.timeout_seconds > MAX_TIMEOUT_SECONDS:
        parser.error(
            f"--timeout-seconds cannot exceed {MAX_TIMEOUT_SECONDS:g} seconds"
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
