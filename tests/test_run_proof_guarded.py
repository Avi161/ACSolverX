from __future__ import annotations

import errno
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

from scripts.run_proof_guarded import parse_args

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNNER = PROJECT_ROOT / "scripts" / "run_proof_guarded.py"
LOCK = PROJECT_ROOT / ".scratch" / "process-guard" / "active.json"
THREAD_ENV = (
    "NUMBA_NUM_THREADS",
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
)


def runner_command(*command: str, timeout: float = 2.0, grace: float = 0.1) -> list[str]:
    return [
        sys.executable,
        str(RUNNER),
        "--timeout-seconds",
        str(timeout),
        "--grace-seconds",
        str(grace),
        "--",
        *command,
    ]


def wait_for_path(path: Path, timeout: float = 1.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if path.exists():
            return
        time.sleep(0.01)
    pytest.fail(f"timed out waiting for {path}")


def pid_exists(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError as exc:
        return exc.errno == errno.EPERM
    return True


def wait_for_pid_exit(pid: int, timeout: float = 1.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if not pid_exists(pid):
            return
        time.sleep(0.01)
    pytest.fail(f"PID {pid} survived process-group cleanup")


def stop_fixture_pid(pid: int) -> None:
    if not pid_exists(pid):
        return
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    deadline = time.monotonic() + 0.2
    while time.monotonic() < deadline:
        if not pid_exists(pid):
            return
        time.sleep(0.01)
    try:
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


@pytest.fixture(autouse=True)
def no_guard_leak() -> None:
    if LOCK.exists():
        pytest.fail(f"proof-process guard already active at {LOCK}")
    yield
    assert not LOCK.exists(), f"proof-process guard leaked at {LOCK}"


def test_second_runner_never_starts_its_child(tmp_path: Path) -> None:
    marker = tmp_path / "second-started"
    first = subprocess.Popen(
        runner_command(sys.executable, "-c", "import time; time.sleep(0.8)"),
        cwd=PROJECT_ROOT,
    )
    try:
        wait_for_path(LOCK)
        second = subprocess.run(
            runner_command(
                sys.executable,
                "-c",
                f"from pathlib import Path; Path({str(marker)!r}).write_text('bad')",
            ),
            cwd=PROJECT_ROOT,
            check=False,
            timeout=2,
        )
        assert second.returncode == 73
        assert not marker.exists()
    finally:
        first.wait(timeout=2)
    assert first.returncode == 0


def test_timeout_kills_child_and_grandchild_process_group(tmp_path: Path) -> None:
    pids_file = tmp_path / "pids.json"
    child_program = (
        "import json, os, pathlib, subprocess, sys, time; "
        "grandchild=subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(10)']); "
        f"pathlib.Path({str(pids_file)!r}).write_text(json.dumps([os.getpid(), grandchild.pid])); "
        "time.sleep(10)"
    )
    result = subprocess.run(
        runner_command(sys.executable, "-c", child_program, timeout=0.3),
        cwd=PROJECT_ROOT,
        check=False,
        timeout=2,
    )
    assert result.returncode == 124
    child_pid, grandchild_pid = json.loads(pids_file.read_text())
    wait_for_pid_exit(child_pid)
    wait_for_pid_exit(grandchild_pid)


def test_sigterm_cleans_up_child_group_and_lock(tmp_path: Path) -> None:
    pids_file = tmp_path / "signal-pids.json"
    child_program = (
        "import json, os, pathlib, subprocess, sys, time; "
        "grandchild=subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(10)']); "
        f"pathlib.Path({str(pids_file)!r}).write_text(json.dumps([os.getpid(), grandchild.pid])); "
        "time.sleep(10)"
    )
    runner = subprocess.Popen(
        runner_command(sys.executable, "-c", child_program, timeout=5),
        cwd=PROJECT_ROOT,
    )
    wait_for_path(pids_file)
    child_pid, grandchild_pid = json.loads(pids_file.read_text())
    runner.send_signal(signal.SIGTERM)
    assert runner.wait(timeout=2) == 128 + signal.SIGTERM
    wait_for_pid_exit(child_pid)
    wait_for_pid_exit(grandchild_pid)


def test_normal_parent_exit_does_not_leak_its_grandchild(tmp_path: Path) -> None:
    grandchild_file = tmp_path / "normal-exit-grandchild.txt"
    child_program = (
        "import pathlib, subprocess, sys; "
        "grandchild=subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(10)']); "
        f"pathlib.Path({str(grandchild_file)!r}).write_text(str(grandchild.pid))"
    )
    result = subprocess.run(
        runner_command(sys.executable, "-c", child_program),
        cwd=PROJECT_ROOT,
        check=False,
        timeout=2,
    )
    assert result.returncode == 0
    grandchild_pid = int(grandchild_file.read_text())
    try:
        wait_for_pid_exit(grandchild_pid)
    finally:
        stop_fixture_pid(grandchild_pid)


def test_child_receives_one_thread_numerical_environment(tmp_path: Path) -> None:
    env_file = tmp_path / "threads.json"
    child_program = (
        "import json, os, pathlib; "
        f"keys={THREAD_ENV!r}; "
        f"pathlib.Path({str(env_file)!r}).write_text(json.dumps({{key: os.environ.get(key) for key in keys}}))"
    )
    result = subprocess.run(
        runner_command(sys.executable, "-c", child_program),
        cwd=PROJECT_ROOT,
        check=False,
        timeout=2,
    )
    assert result.returncode == 0
    assert json.loads(env_file.read_text()) == {key: "1" for key in THREAD_ENV}


def test_dead_owner_lock_is_reclaimed() -> None:
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    LOCK.write_text(json.dumps({"pid": 999_999, "started_at": "old", "worktree": "old"}))
    result = subprocess.run(
        runner_command(sys.executable, "-c", "raise SystemExit(0)"),
        cwd=PROJECT_ROOT,
        check=False,
        timeout=2,
    )
    assert result.returncode == 0


def test_timeout_61_without_long_run_is_rejected_before_launch(tmp_path: Path) -> None:
    marker = tmp_path / "too-long-started"
    result = subprocess.run(
        runner_command(
            sys.executable,
            "-c",
            f"from pathlib import Path; Path({str(marker)!r}).write_text('bad')",
            timeout=61,
        ),
        cwd=PROJECT_ROOT,
        check=False,
        timeout=2,
    )
    assert result.returncode == 2
    assert not marker.exists()


@pytest.mark.parametrize("timeout", (60, 601))
def test_long_run_timeout_outside_bounds_is_rejected_before_launch(
    tmp_path: Path, timeout: int
) -> None:
    marker = tmp_path / f"invalid-long-run-timeout-{timeout}"
    result = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--long-run",
            "--timeout-seconds",
            str(timeout),
            "--",
            sys.executable,
            "-c",
            f"from pathlib import Path; Path({str(marker)!r}).write_text('bad')",
        ],
        cwd=PROJECT_ROOT,
        check=False,
        timeout=2,
    )
    assert result.returncode == 2
    assert not marker.exists()


@pytest.mark.parametrize("option", ("--preflight-seconds", "--progress-seconds"))
def test_long_run_preflight_or_progress_above_maximum_is_rejected_before_launch(
    tmp_path: Path, option: str
) -> None:
    marker = tmp_path / f"invalid-{option[2:]}"
    result = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--long-run",
            "--timeout-seconds",
            "61",
            option,
            "61",
            "--",
            sys.executable,
            "-c",
            f"from pathlib import Path; Path({str(marker)!r}).write_text('bad')",
        ],
        cwd=PROJECT_ROOT,
        check=False,
        timeout=2,
    )
    assert result.returncode == 2
    assert not marker.exists()


def test_long_run_parser_preserves_finite_positive_phase_values() -> None:
    args = parse_args(
        [
            "--long-run",
            "--timeout-seconds",
            "61",
            "--preflight-seconds",
            "0.25",
            "--progress-seconds",
            "1.5",
            "--",
            "proof-command",
        ]
    )

    assert args.long_run is True
    assert args.preflight_seconds == 0.25
    assert args.progress_seconds == 1.5


@pytest.mark.parametrize(
    ("option", "value"),
    (
        ("--timeout-seconds", "nan"),
        ("--grace-seconds", "nan"),
        ("--grace-seconds", "6"),
    ),
)
def test_nonfinite_or_excessive_limits_are_rejected_before_launch(
    tmp_path: Path, option: str, value: str
) -> None:
    marker = tmp_path / f"invalid-{option[2:]}-{value}"
    result = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            option,
            value,
            "--",
            sys.executable,
            "-c",
            f"from pathlib import Path; Path({str(marker)!r}).write_text('bad')",
        ],
        cwd=PROJECT_ROOT,
        check=False,
        timeout=2,
    )
    assert result.returncode == 2
    assert not marker.exists()
