from __future__ import annotations

import errno
import json
import os
import signal
import subprocess
import sys
import time
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

import scripts.run_proof_guarded as proof_guard
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
    ("phase_modes", "expected_status"),
    (
        (("timeout",), 125),
        (("complete", "timeout"), 124),
        (("complete", "linger"), 126),
    ),
)
def test_sigkill_disappearance_race_preserves_phase_status_without_group_leak(
    monkeypatch: pytest.MonkeyPatch,
    phase_modes: tuple[str, ...],
    expected_status: int,
) -> None:
    class SyntheticChild:
        def __init__(self, pid: int, mode: str) -> None:
            self.pid = pid
            self.mode = mode

        def wait(self, timeout: float | None = None) -> int:
            if self.mode == "timeout":
                raise subprocess.TimeoutExpired("synthetic phase", timeout)
            return 0

        def poll(self) -> None:
            return None

    children = [
        SyntheticChild(pid=800_000 + index, mode=mode)
        for index, mode in enumerate(phase_modes)
    ]
    group_alive: dict[int, bool] = {}

    def popen(*_args: object, **_kwargs: object) -> SyntheticChild:
        child = children.pop(0)
        group_alive[child.pid] = child.mode in {"timeout", "linger"}
        return child

    def killpg(process_group_id: int, signum: int) -> None:
        if not group_alive.get(process_group_id, False):
            raise ProcessLookupError
        if signum == signal.SIGKILL:
            group_alive[process_group_id] = False
            raise ProcessLookupError

    monkeypatch.setattr(proof_guard.subprocess, "Popen", popen)
    monkeypatch.setattr(
        proof_guard,
        "group_exists",
        lambda process_group_id: group_alive.get(process_group_id, False),
    )
    monkeypatch.setattr(proof_guard.os, "killpg", killpg)

    status = run_long_guarded(
        ["synthetic-command", "unchanged-argument"],
        preflight_seconds=0.1,
        experiment_seconds=0.1,
        progress_seconds=0.1,
        grace_seconds=0.0,
        monitor=None,
    )

    assert status == expected_status
    assert not any(group_alive.values())


def test_lingering_experiment_group_returns_126_and_cleans_exact_group(
    tmp_path: Path,
) -> None:
    records_file = tmp_path / "lingering-experiment.jsonl"
    child_program = "\n".join(
        (
            "import json, os, pathlib, subprocess, sys",
            f"records_path = pathlib.Path({str(records_file)!r})",
            "phase = os.environ.get('ACSOLVERX_PROOF_PHASE')",
            "grandchild = None",
            "if phase == 'experiment':",
            "    grandchild = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(10)'])",
            "record = {'phase': phase, 'pid': os.getpid(), 'grandchild_pid': grandchild.pid if grandchild else None}",
            "with records_path.open('a', encoding='utf-8') as stream:",
            "    stream.write(json.dumps(record) + '\\n')",
        )
    )
    result = subprocess.run(
        long_runner_command(sys.executable, "-c", child_program),
        cwd=PROJECT_ROOT,
        check=False,
        timeout=3,
    )

    records = [json.loads(line) for line in records_file.read_text().splitlines()]
    grandchild_pid = records[1]["grandchild_pid"]
    try:
        assert result.returncode == 126
        assert [record["phase"] for record in records] == [
            "preflight",
            "experiment",
        ]
        assert records[0]["grandchild_pid"] is None
        wait_for_pid_exit(grandchild_pid)
    finally:
        stop_fixture_pid(grandchild_pid)


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


def _process_info(
    pid: int,
    ppid: int,
    pgid: int,
    cpu_percent: float,
    state: str = "S",
    ucomm: str = "python3",
) -> object:
    return proof_guard.ProcessInfo(pid, ppid, pgid, cpu_percent, state, ucomm)


@pytest.mark.parametrize(
    ("child_cpu", "expected_cpu"),
    ((76.0, 136.0), (64.9, 124.9)),
)
def test_monitor_counts_only_exact_group_and_reports_escaped_descendants(
    child_cpu: float,
    expected_cpu: float,
) -> None:
    processes = (
        _process_info(100, 1, 100, 0.0, ucomm="guard"),
        _process_info(200, 100, 200, 50.0, ucomm="phase"),
        _process_info(201, 200, 200, child_cpu, ucomm="worker"),
        _process_info(202, 201, 202, 99.0, ucomm="escaped"),
        _process_info(203, 1, 200, 10.0, ucomm="reparented-worker"),
        _process_info(300, 100, 300, 88.0, ucomm="unrelated"),
    )
    monitor = proof_guard.SafetyMonitor(
        process_reader=lambda: processes,
        thermal_reader=lambda: 0,
    )

    sample = monitor.sample(child_pid=200, process_group_id=200, controller_pid=100)

    assert sample.controller_alive is True
    assert sample.child_reparented is False
    assert sample.group_process_count == 3
    assert sample.group_cpu_percent == pytest.approx(expected_cpu)
    assert sample.escaped_pids == (202,)
    with pytest.raises(FrozenInstanceError):
        sample.group_cpu_percent = 0.0
    with pytest.raises(FrozenInstanceError):
        processes[0].pid = 0


def test_monitor_reports_lost_controller_and_reparented_child() -> None:
    lost_controller = proof_guard.SafetyMonitor(
        process_reader=lambda: (_process_info(200, 100, 200, 1.0),),
        thermal_reader=lambda: 0,
    ).sample(child_pid=200, process_group_id=200, controller_pid=100)
    reparented_child = proof_guard.SafetyMonitor(
        process_reader=lambda: (
            _process_info(100, 1, 100, 0.0),
            _process_info(200, 1, 200, 1.0),
        ),
        thermal_reader=lambda: 0,
    ).sample(child_pid=200, process_group_id=200, controller_pid=100)

    assert lost_controller.controller_alive is False
    assert lost_controller.failure_reason is not None
    assert reparented_child.child_reparented is True
    assert reparented_child.failure_reason is not None


@pytest.mark.parametrize("thermal_state", (0, 1, 2, 3))
def test_monitor_accepts_only_nominal_thermal_state(thermal_state: int) -> None:
    monitor = proof_guard.SafetyMonitor(
        process_reader=lambda: (
            _process_info(100, 1, 100, 0.0),
            _process_info(200, 100, 200, 1.0),
        ),
        thermal_reader=lambda: thermal_state,
    )

    sample = monitor.sample(child_pid=200, process_group_id=200, controller_pid=100)

    assert (sample.failure_reason is None) is (thermal_state == 0)


def test_monitor_fails_closed_when_thermal_state_is_unreadable() -> None:
    def unreadable() -> int:
        raise RuntimeError("thermal API unavailable")

    monitor = proof_guard.SafetyMonitor(
        process_reader=lambda: (),
        thermal_reader=unreadable,
    )

    sample = monitor.sample(child_pid=200, process_group_id=200, controller_pid=100)

    assert sample.failure_reason is not None
    assert "thermal API unavailable" in sample.failure_reason


def _install_fake_macos_thermal_api(
    monkeypatch: pytest.MonkeyPatch,
    thermal_state: int,
) -> list[str]:
    import ctypes

    selectors = {b"processInfo": 11, b"thermalState": 12}
    objc_get_class = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_char_p)(
        lambda name: 10 if name == b"NSProcessInfo" else 0
    )
    selector_register = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_char_p)(
        lambda name: selectors.get(name, 0)
    )
    message_send = ctypes.CFUNCTYPE(
        ctypes.c_long, ctypes.c_void_p, ctypes.c_void_p
    )(
        lambda receiver, selector: (
            20 if (receiver, selector) == (10, 11) else thermal_state
        )
    )

    class ObjCLibrary:
        objc_getClass = objc_get_class
        sel_registerName = selector_register
        objc_msgSend = message_send

    loaded: list[str] = []

    def load_library(path: str) -> object:
        loaded.append(path)
        if path == "/usr/lib/libobjc.A.dylib":
            return ObjCLibrary()
        if path == "/System/Library/Frameworks/Foundation.framework/Foundation":
            return object()
        raise OSError(path)

    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.setattr(ctypes, "CDLL", load_library)
    return loaded


def test_macos_thermal_reader_uses_foundation_and_libobjc(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    loaded = _install_fake_macos_thermal_api(monkeypatch, thermal_state=0)

    assert proof_guard.read_macos_thermal_state() == 0
    assert loaded == [
        "/System/Library/Frameworks/Foundation.framework/Foundation",
        "/usr/lib/libobjc.A.dylib",
    ]


@pytest.mark.parametrize("thermal_state", (1, 2, 3))
def test_macos_thermal_reader_rejects_pressure_states(
    monkeypatch: pytest.MonkeyPatch,
    thermal_state: int,
) -> None:
    _install_fake_macos_thermal_api(monkeypatch, thermal_state)

    with pytest.raises(RuntimeError, match="not nominal"):
        proof_guard.read_macos_thermal_state()


def test_macos_thermal_reader_rejects_unsupported_platform(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(sys, "platform", "linux")

    with pytest.raises(RuntimeError, match="requires macOS"):
        proof_guard.read_macos_thermal_state()


def test_macos_thermal_reader_wraps_objective_c_api_failures(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import ctypes

    monkeypatch.setattr(sys, "platform", "darwin")

    def fail_to_load(_path: str) -> object:
        raise ctypes.ArgumentError("invalid Objective-C call")

    monkeypatch.setattr(ctypes, "CDLL", fail_to_load)

    with pytest.raises(RuntimeError, match="macOS thermal API failure"):
        proof_guard.read_macos_thermal_state()


def test_process_reader_requests_only_non_sensitive_fields(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[object, object]] = []

    def run(command: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(
            command,
            0,
            stdout="200 100 200 12.5 S python3\n",
            stderr="",
        )

    monkeypatch.setattr(proof_guard.subprocess, "run", run)

    processes = proof_guard._read_process_table()

    assert processes == (_process_info(200, 100, 200, 12.5),)
    assert calls == [
        (
            ["ps", "-axo", "pid=,ppid=,pgid=,%cpu=,state=,ucomm="],
            {
                "check": True,
                "capture_output": True,
                "text": True,
                "timeout": 2.0,
            },
        )
    ]


class _FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def monotonic(self) -> float:
        return self.now


class _SequenceMonitor:
    def __init__(self, samples: list[object]) -> None:
        self.samples = samples
        self.calls: list[tuple[int, int, int]] = []

    def sample(
        self,
        child_pid: int,
        process_group_id: int,
        controller_pid: int,
    ) -> object:
        self.calls.append((child_pid, process_group_id, controller_pid))
        if not self.samples:
            raise AssertionError("monitor sampled more often than expected")
        sample = self.samples.pop(0)
        if isinstance(sample, BaseException):
            raise sample
        return sample


def _safety_sample(
    *,
    cpu_percent: float = 0.0,
    thermal_state: int | None = 0,
    controller_alive: bool = True,
    child_reparented: bool = False,
    escaped_pids: tuple[int, ...] = (),
    error: str | None = None,
) -> object:
    return proof_guard.SafetySample(
        thermal_state=thermal_state,
        controller_alive=controller_alive,
        child_reparented=child_reparented,
        group_process_count=1,
        group_cpu_percent=cpu_percent,
        escaped_pids=escaped_pids,
        error=error,
    )


def _run_synthetic_monitored_phases(
    monkeypatch: pytest.MonkeyPatch,
    samples: list[object],
    completion_times: tuple[float, ...],
) -> tuple[int, list[tuple[int, int]], _SequenceMonitor]:
    clock = _FakeClock()
    alive: dict[int, bool] = {}
    children: list[object] = []

    class SyntheticChild:
        def __init__(self, pid: int, complete_after: float) -> None:
            self.pid = pid
            self.deadline = clock.now + complete_after
            alive[pid] = True

        def poll(self) -> int | None:
            if clock.now >= self.deadline:
                alive[self.pid] = False
                return 0
            return None

        def wait(self, timeout: float | None = None) -> int:
            if timeout is None:
                clock.now = self.deadline
                alive[self.pid] = False
                return 0
            if clock.now + timeout >= self.deadline:
                clock.now = self.deadline
                alive[self.pid] = False
                return 0
            clock.now += timeout
            raise subprocess.TimeoutExpired("synthetic phase", timeout)

    children.extend(
        SyntheticChild(700_000 + index, complete_after)
        for index, complete_after in enumerate(completion_times)
    )
    killpg_calls: list[tuple[int, int]] = []

    def popen(*_args: object, **_kwargs: object) -> object:
        return children.pop(0)

    def killpg(process_group_id: int, signum: int) -> None:
        killpg_calls.append((process_group_id, signum))
        if not alive.get(process_group_id, False):
            raise ProcessLookupError
        if signum in (signal.SIGTERM, signal.SIGKILL):
            alive[process_group_id] = False

    monitor = _SequenceMonitor(samples)
    monkeypatch.setattr(proof_guard.subprocess, "Popen", popen)
    monkeypatch.setattr(proof_guard.time, "monotonic", clock.monotonic)
    monkeypatch.setattr(
        proof_guard,
        "group_exists",
        lambda process_group_id: alive.get(process_group_id, False),
    )
    monkeypatch.setattr(proof_guard.os, "killpg", killpg)

    status = run_long_guarded(
        ["synthetic-command"],
        preflight_seconds=10.0,
        experiment_seconds=10.0,
        progress_seconds=10.0,
        grace_seconds=0.1,
        monitor=monitor,
    )
    return status, killpg_calls, monitor


def test_one_high_cpu_sample_does_not_abort(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    status, killpg_calls, _monitor = _run_synthetic_monitored_phases(
        monkeypatch,
        [_safety_sample(cpu_percent=126.0), _safety_sample()],
        completion_times=(0.5, 0.5),
    )

    assert status == 0
    assert killpg_calls == []


def test_three_consecutive_high_cpu_samples_abort_exact_group(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    status, killpg_calls, _monitor = _run_synthetic_monitored_phases(
        monkeypatch,
        [
            _safety_sample(cpu_percent=126.0),
            _safety_sample(cpu_percent=130.0),
            _safety_sample(cpu_percent=125.1),
        ],
        completion_times=(3.0,),
    )

    assert status == 126
    assert killpg_calls == [(700_000, signal.SIGTERM)]


def test_compliant_cpu_sample_resets_high_cpu_streak(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    status, killpg_calls, _monitor = _run_synthetic_monitored_phases(
        monkeypatch,
        [
            _safety_sample(cpu_percent=126.0),
            _safety_sample(cpu_percent=125.0),
            _safety_sample(cpu_percent=130.0),
            _safety_sample(cpu_percent=140.0),
            _safety_sample(),
        ],
        completion_times=(3.5, 0.5),
    )

    assert status == 0
    assert killpg_calls == []


@pytest.mark.parametrize(
    ("failure", "reported_pid"),
    (
        ("thermal", None),
        ("controller", None),
        ("reparented", None),
        ("escaped", 812_345),
        ("sampling", None),
    ),
)
def test_immediate_safety_failure_aborts_only_exact_group(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    failure: str,
    reported_pid: int | None,
) -> None:
    direct_kills: list[tuple[int, int]] = []
    monkeypatch.setattr(
        proof_guard.os,
        "kill",
        lambda pid, signum: direct_kills.append((pid, signum)),
    )
    samples = {
        "thermal": lambda: _safety_sample(thermal_state=1),
        "controller": lambda: _safety_sample(controller_alive=False),
        "reparented": lambda: _safety_sample(child_reparented=True),
        "escaped": lambda: _safety_sample(escaped_pids=(812_345,)),
        "sampling": lambda: RuntimeError("ps sampling failed"),
    }

    status, killpg_calls, _monitor = _run_synthetic_monitored_phases(
        monkeypatch,
        [samples[failure]()],
        completion_times=(3.0,),
    )

    assert status == 126
    assert killpg_calls == [(700_000, signal.SIGTERM)]
    assert direct_kills == []
    if reported_pid is not None:
        assert str(reported_pid) in capsys.readouterr().err
        assert all(process_group_id != reported_pid for process_group_id, _ in killpg_calls)
