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

from scripts.run_proof_guarded import parse_args, run_long_guarded

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


def long_runner_command(
    *command: str,
    preflight: float = 0.5,
    timeout: float = 61.0,
    grace: float = 0.1,
) -> list[str]:
    return [
        sys.executable,
        str(RUNNER),
        "--long-run",
        "--preflight-seconds",
        str(preflight),
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
@pytest.mark.parametrize("value", ("0", "-1", "nan", "inf", "61"))
def test_long_run_invalid_preflight_or_progress_is_rejected_without_disclosure(
    tmp_path: Path, option: str, value: str
) -> None:
    marker = tmp_path / f"invalid-{option[2:]}-{value}"
    sentinel = "proof-guard-secret-sentinel"
    result = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--long-run",
            "--timeout-seconds",
            "61",
            option,
            value,
            "--",
            sys.executable,
            "-c",
            f"from pathlib import Path; Path({str(marker)!r}).write_text({sentinel!r})",
        ],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=2,
    )
    assert result.returncode == 2
    assert not marker.exists()
    assert sentinel not in result.stdout
    assert sentinel not in result.stderr


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


def test_long_run_replays_exact_command_in_two_phases_under_one_lock(
    tmp_path: Path,
) -> None:
    records_file = tmp_path / "phase-records.jsonl"
    child_program = "\n".join(
        (
            "import json, os, pathlib, sys",
            f"lock_path = pathlib.Path({str(LOCK)!r})",
            f"records_path = pathlib.Path({str(records_file)!r})",
            f"thread_names = {THREAD_ENV!r}",
            "lock = json.loads(lock_path.read_text())",
            "lock_stat = lock_path.stat()",
            "record = {",
            "    'phase': os.environ.get('ACSOLVERX_PROOF_PHASE'),",
            "    'threads': {name: os.environ.get(name) for name in thread_names},",
            "    'arguments': sys.argv[1:],",
            "    'lock_owner': lock['pid'],",
            "    'lock_identity': [lock_stat.st_dev, lock_stat.st_ino],",
            "    'parent_pid': os.getppid(),",
            "}",
            "with records_path.open('a', encoding='utf-8') as stream:",
            "    stream.write(json.dumps(record) + '\\n')",
        )
    )
    result = subprocess.run(
        long_runner_command(
            sys.executable, "-c", child_program, "same-command-argument"
        ),
        cwd=PROJECT_ROOT,
        check=False,
        timeout=3,
    )

    assert result.returncode == 0
    records = [json.loads(line) for line in records_file.read_text().splitlines()]
    assert [record["phase"] for record in records] == ["preflight", "experiment"]
    assert [record["arguments"] for record in records] == [
        ["same-command-argument"],
        ["same-command-argument"],
    ]
    assert [record["threads"] for record in records] == [
        {name: "1" for name in THREAD_ENV},
        {name: "1" for name in THREAD_ENV},
    ]
    assert all(record["lock_owner"] == record["parent_pid"] for record in records)
    assert records[0]["lock_owner"] == records[1]["lock_owner"]
    assert records[0]["lock_identity"] == records[1]["lock_identity"]


def test_nonzero_preflight_returns_125_without_starting_experiment(
    tmp_path: Path,
) -> None:
    records_file = tmp_path / "failed-preflight.jsonl"
    child_program = "\n".join(
        (
            "import json, os, pathlib",
            f"records_path = pathlib.Path({str(records_file)!r})",
            "phase = os.environ.get('ACSOLVERX_PROOF_PHASE')",
            "records_path.write_text(json.dumps({'phase': phase, 'pid': os.getpid()}) + '\\n')",
            "if phase == 'preflight':",
            "    raise SystemExit(9)",
        )
    )
    result = subprocess.run(
        long_runner_command(sys.executable, "-c", child_program),
        cwd=PROJECT_ROOT,
        check=False,
        timeout=3,
    )

    assert result.returncode == 125
    records = [json.loads(line) for line in records_file.read_text().splitlines()]
    assert [record["phase"] for record in records] == ["preflight"]
    wait_for_pid_exit(records[0]["pid"])


def test_timed_out_preflight_returns_125_and_cleans_its_exact_group(
    tmp_path: Path,
) -> None:
    records_file = tmp_path / "timed-out-preflight.jsonl"
    child_program = "\n".join(
        (
            "import json, os, pathlib, time",
            f"records_path = pathlib.Path({str(records_file)!r})",
            "phase = os.environ.get('ACSOLVERX_PROOF_PHASE')",
            "records_path.write_text(json.dumps({'phase': phase, 'pid': os.getpid()}) + '\\n')",
            "if phase == 'preflight':",
            "    time.sleep(10)",
        )
    )
    result = subprocess.run(
        long_runner_command(
            sys.executable, "-c", child_program, preflight=0.2, grace=0.1
        ),
        cwd=PROJECT_ROOT,
        check=False,
        timeout=3,
    )

    assert result.returncode == 125
    records = [json.loads(line) for line in records_file.read_text().splitlines()]
    assert [record["phase"] for record in records] == ["preflight"]
    wait_for_pid_exit(records[0]["pid"])


def test_long_run_returns_experiment_nonzero_status(tmp_path: Path) -> None:
    records_file = tmp_path / "nonzero-experiment.jsonl"
    child_program = "\n".join(
        (
            "import json, os, pathlib",
            f"records_path = pathlib.Path({str(records_file)!r})",
            "phase = os.environ.get('ACSOLVERX_PROOF_PHASE')",
            "with records_path.open('a', encoding='utf-8') as stream:",
            "    stream.write(json.dumps({'phase': phase}) + '\\n')",
            "if phase == 'experiment':",
            "    raise SystemExit(17)",
        )
    )
    result = subprocess.run(
        long_runner_command(sys.executable, "-c", child_program),
        cwd=PROJECT_ROOT,
        check=False,
        timeout=3,
    )

    assert result.returncode == 17
    records = [json.loads(line) for line in records_file.read_text().splitlines()]
    assert [record["phase"] for record in records] == ["preflight", "experiment"]


def test_timed_out_experiment_returns_124_and_cleans_its_exact_group(
    tmp_path: Path,
) -> None:
    records_file = tmp_path / "timed-out-experiment.jsonl"
    child_program = "\n".join(
        (
            "import json, os, pathlib, time",
            f"records_path = pathlib.Path({str(records_file)!r})",
            "phase = os.environ.get('ACSOLVERX_PROOF_PHASE')",
            "with records_path.open('a', encoding='utf-8') as stream:",
            "    stream.write(json.dumps({'phase': phase, 'pid': os.getpid()}) + '\\n')",
            "if phase == 'experiment':",
            "    time.sleep(10)",
        )
    )
    status = run_long_guarded(
        [sys.executable, "-c", child_program],
        preflight_seconds=0.5,
        experiment_seconds=0.2,
        progress_seconds=0.1,
        grace_seconds=0.1,
        monitor=None,
    )

    assert status == 124
    records = [json.loads(line) for line in records_file.read_text().splitlines()]
    assert [record["phase"] for record in records] == ["preflight", "experiment"]
    wait_for_pid_exit(records[1]["pid"])


def test_lingering_preflight_group_returns_126_without_starting_experiment(
    tmp_path: Path,
) -> None:
    records_file = tmp_path / "lingering-preflight.jsonl"
    child_program = "\n".join(
        (
            "import json, os, pathlib, subprocess, sys",
            f"records_path = pathlib.Path({str(records_file)!r})",
            "phase = os.environ.get('ACSOLVERX_PROOF_PHASE')",
            "grandchild = None",
            "if phase == 'preflight':",
            "    grandchild = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(10)'])",
            "record = {'phase': phase, 'pid': os.getpid(), 'grandchild_pid': grandchild.pid if grandchild else None}",
            "records_path.write_text(json.dumps(record) + '\\n')",
        )
    )
    result = subprocess.run(
        long_runner_command(sys.executable, "-c", child_program),
        cwd=PROJECT_ROOT,
        check=False,
        timeout=3,
    )

    assert result.returncode == 126
    records = [json.loads(line) for line in records_file.read_text().splitlines()]
    assert [record["phase"] for record in records] == ["preflight"]
    wait_for_pid_exit(records[0]["grandchild_pid"])


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
