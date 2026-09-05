from __future__ import annotations

import errno
import io
import json
import os
import signal
import subprocess
import sys
import time
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import FrozenInstanceError
from datetime import datetime
from pathlib import Path

import pytest

import scripts.run_proof_guarded as proof_guard
from scripts.run_proof_guarded import parse_args, run_long_guarded

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNNER = PROJECT_ROOT / "scripts" / "run_proof_guarded.py"
LOCK = PROJECT_ROOT / ".scratch" / "process-guard" / "active.json"
LAST_RUN = LOCK.with_name("last-run.json")
THREAD_ENV = (
    "NUMBA_NUM_THREADS",
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
)


class _FlushRecordingStream(io.StringIO):
    def __init__(self) -> None:
        super().__init__()
        self.flush_count = 0

    def flush(self) -> None:
        self.flush_count += 1
        super().flush()


def _exception_chain(exception: BaseException) -> tuple[BaseException, ...]:
    seen: set[int] = set()

    def visit(current: BaseException | None) -> tuple[BaseException, ...]:
        if current is None or id(current) in seen:
            return ()
        seen.add(id(current))
        return (
            current,
            *visit(current.__cause__),
            *visit(current.__context__),
        )

    return visit(exception)


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


def run_immediate_synthetic_long_main(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    phase_statuses: tuple[int, ...],
    *,
    command_sentinel: str = "audit-command-secret-sentinel",
    environment_sentinel: str = "audit-environment-secret-sentinel",
) -> tuple[int, Path, Path, list[tuple[int, bool]]]:
    process_guard_dir = tmp_path / "process-guard"
    lock_path = process_guard_dir / "active.json"
    last_run_path = process_guard_dir / "last-run.json"
    phase_pids = iter(720_000 + index for index in range(len(phase_statuses)))
    statuses = iter(phase_statuses)
    group_checks: list[tuple[int, bool]] = []

    class SyntheticChild:
        def __init__(self, pid: int, status: int) -> None:
            self.pid = pid
            self.status = status

        def poll(self) -> int:
            return self.status

    monkeypatch.setattr(proof_guard, "LOCK_PATH", lock_path)
    monkeypatch.setattr(
        proof_guard,
        "LAST_RUN_PATH",
        last_run_path,
        raising=False,
    )
    monkeypatch.setattr(proof_guard, "SafetyMonitor", lambda: None)
    monkeypatch.setattr(
        proof_guard.subprocess,
        "Popen",
        lambda *_args, **_kwargs: SyntheticChild(next(phase_pids), next(statuses)),
    )
    monkeypatch.setattr(proof_guard.os, "getppid", lambda: 620_000)
    monkeypatch.setenv("PROOF_GUARD_AUDIT_SECRET", environment_sentinel)

    def group_absent(process_group_id: int) -> bool:
        group_checks.append((process_group_id, lock_path.exists()))
        return False

    monkeypatch.setattr(proof_guard, "group_exists", group_absent)
    status = proof_guard.main(
        [
            "--long-run",
            "--preflight-seconds",
            "0.1",
            "--timeout-seconds",
            "61",
            "--",
            "synthetic-command",
            command_sentinel,
        ]
    )
    return status, lock_path, last_run_path, group_checks


def run_mode_synthetic_long_main(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    phase_modes: tuple[str, ...],
    *,
    samples: tuple[object, ...] = (),
    fail_final_recheck: tuple[int, ...] = (),
) -> tuple[int, Path, Path, list[tuple[int, int]], list[tuple[int, bool]]]:
    process_guard_dir = tmp_path / "process-guard"
    lock_path = process_guard_dir / "active.json"
    last_run_path = process_guard_dir / "last-run.json"
    clock = _FakeClock()
    pending_modes = list(phase_modes)
    pending_samples = list(samples)
    alive: dict[int, bool] = {}
    killpg_calls: list[tuple[int, int]] = []
    group_checks: list[tuple[int, bool]] = []
    next_pid = 730_000

    class SyntheticChild:
        def __init__(self, pid: int, mode: str) -> None:
            self.pid = pid
            self.mode = mode

        def poll(self) -> int | None:
            if self.mode == "complete":
                alive[self.pid] = False
                return 0
            return None

        def wait(self, timeout: float | None = None) -> int:
            if self.mode == "timeout":
                assert timeout is not None
                clock.now += timeout
                raise subprocess.TimeoutExpired("synthetic phase", timeout)
            raise AssertionError(f"unexpected wait for synthetic mode {self.mode}")

    class SyntheticMonitor:
        def verify_launcher_coordinator(
            self,
            launcher_pid: int,
            coordinator_pid: int,
            sample_deadline: float | None = None,
        ) -> None:
            del launcher_pid, coordinator_pid, sample_deadline
            return None

        def sample(self, **_kwargs: object) -> object:
            if not pending_samples:
                raise AssertionError("synthetic monitor sampled too often")
            sample = pending_samples.pop(0)
            if isinstance(sample, BaseException):
                raise sample
            return sample

    def popen(*_args: object, **_kwargs: object) -> object:
        nonlocal next_pid
        mode = pending_modes.pop(0)
        if mode == "start_error":
            raise OSError(errno.ENOENT, "synthetic start failure")
        child = SyntheticChild(next_pid, mode)
        next_pid += 1
        alive[child.pid] = True
        return child

    def group_exists(process_group_id: int) -> bool:
        lock_present = lock_path.exists()
        prior_checks = sum(
            checked_pgid == process_group_id
            for checked_pgid, _lock_present in group_checks
        )
        group_checks.append((process_group_id, lock_present))
        if (
            lock_present
            and process_group_id in fail_final_recheck
            and prior_checks >= 1
        ):
            return True
        return alive.get(process_group_id, False)

    def killpg(process_group_id: int, signum: int) -> None:
        killpg_calls.append((process_group_id, signum))
        if not alive.get(process_group_id, False):
            raise ProcessLookupError
        alive[process_group_id] = False

    monkeypatch.setattr(proof_guard, "LOCK_PATH", lock_path)
    monkeypatch.setattr(proof_guard, "LAST_RUN_PATH", last_run_path)
    monkeypatch.setattr(
        proof_guard,
        "SafetyMonitor",
        (lambda: SyntheticMonitor()) if samples else (lambda: None),
    )
    monkeypatch.setattr(proof_guard.subprocess, "Popen", popen)
    monkeypatch.setattr(proof_guard, "group_exists", group_exists)
    monkeypatch.setattr(proof_guard.os, "killpg", killpg)
    monkeypatch.setattr(proof_guard.os, "getppid", lambda: 630_000)
    monkeypatch.setattr(proof_guard.time, "monotonic", clock.monotonic)
    monkeypatch.setattr(
        proof_guard.time,
        "sleep",
        lambda seconds: setattr(clock, "now", clock.now + seconds),
    )

    status = proof_guard.main(
        [
            "--long-run",
            "--preflight-seconds",
            "0.1",
            "--timeout-seconds",
            "61",
            "--",
            "synthetic-command",
        ]
    )
    return status, lock_path, last_run_path, killpg_calls, group_checks


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


def exact_group_exists(process_group_id: int) -> bool:
    try:
        os.killpg(process_group_id, 0)
    except OSError as exc:
        if exc.errno == errno.ESRCH:
            return False
        if exc.errno == errno.EPERM:
            return True
        raise
    return True


def stop_fixture_group(child: subprocess.Popen[object]) -> None:
    child.poll()
    if not exact_group_exists(child.pid):
        return
    try:
        os.killpg(child.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    try:
        child.wait(timeout=1.0)
    except subprocess.TimeoutExpired:
        pass


@pytest.fixture(autouse=True)
def no_guard_leak() -> None:
    if LOCK.exists():
        pytest.fail(f"proof-process guard already active at {LOCK}")
    if LAST_RUN.exists():
        pytest.fail(f"unexpected proof-process audit already present at {LAST_RUN}")
    yield
    assert not LOCK.exists(), f"proof-process guard leaked at {LOCK}"
    LAST_RUN.unlink(missing_ok=True)


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


@pytest.mark.parametrize(
    "signum",
    (signal.SIGHUP, signal.SIGTERM, signal.SIGINT),
)
def test_guard_signals_clean_up_child_group_and_lock(
    tmp_path: Path,
    signum: int,
) -> None:
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
    runner.send_signal(signum)
    assert runner.wait(timeout=2) == 128 + signum
    wait_for_pid_exit(child_pid)
    wait_for_pid_exit(grandchild_pid)


@pytest.mark.parametrize(
    "signum",
    (signal.SIGHUP, signal.SIGTERM, signal.SIGINT),
)
@pytest.mark.parametrize("launch_role", ("short", "phase", "helper"))
def test_signal_at_post_spawn_boundary_cleans_registered_exact_group(
    monkeypatch: pytest.MonkeyPatch,
    signum: int,
    launch_role: str,
) -> None:
    real_popen = proof_guard.subprocess.Popen
    launched: list[subprocess.Popen[object]] = []
    audit = proof_guard.PhaseAudit()
    delivered_audit_states: list[tuple[int | None, str]] = []

    def spawn_then_signal(
        _command: object,
        **kwargs: object,
    ) -> subprocess.Popen[object]:
        child = real_popen(
            [sys.executable, "-c", "import time; time.sleep(10)"],
            **kwargs,
        )
        launched.append(child)
        os.kill(os.getpid(), signum)
        return child

    def interrupt(delivered_signum: int, _frame: object) -> None:
        delivered_audit_states.append((audit.pgid, audit.outcome))
        if delivered_signum == signal.SIGINT:
            raise KeyboardInterrupt
        raise proof_guard.GuardSignal(delivered_signum)

    monkeypatch.setattr(proof_guard.subprocess, "Popen", spawn_then_signal)
    previous_handler = signal.signal(signum, interrupt)
    expected_exception = (
        KeyboardInterrupt if signum == signal.SIGINT else proof_guard.GuardSignal
    )
    try:
        with pytest.raises(expected_exception) as exc_info:
            if launch_role == "short":
                proof_guard.run_guarded(
                    ("synthetic-command",),
                    timeout_seconds=5.0,
                    grace_seconds=0.05,
                )
            elif launch_role == "phase":
                proof_guard._run_long_phase(
                    ("synthetic-command",),
                    "preflight",
                    timeout_seconds=5.0,
                    progress_seconds=1.0,
                    grace_seconds=0.05,
                    monitor=None,
                    clock=time.monotonic,
                    launcher_pid=os.getppid(),
                    coordinator_pid=os.getpid(),
                    phase_audit=audit,
                )
            else:
                proof_guard.read_bounded_macos_thermal_state(
                    deadline=time.monotonic() + 5.0,
                )
    finally:
        signal.signal(signum, previous_handler)

    assert len(launched) == 1
    child = launched[0]
    child.poll()
    group_absent_before_fixture_cleanup = not exact_group_exists(child.pid)
    stop_fixture_group(child)
    assert group_absent_before_fixture_cleanup is True
    if signum != signal.SIGINT:
        assert exc_info.value.signum == signum
    if launch_role == "phase":
        assert delivered_audit_states == [(child.pid, "running")]
        assert audit == proof_guard.PhaseAudit(
            pgid=child.pid,
            outcome="interrupted",
            guard_status=None,
            child_exit_status=None,
            exact_group_absent=True,
        )


@pytest.mark.parametrize("launch_role", ("short", "phase", "helper"))
def test_launch_cleanup_failure_supersedes_pending_signal_with_fixed_error(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    launch_role: str,
) -> None:
    clock = _FakeClock()
    process_group_id = 988_200_001
    secret = "launch-cleanup-secret-sentinel"
    audit = proof_guard.PhaseAudit()
    killpg_calls: list[tuple[int, int]] = []

    class SyntheticChild:
        pid = process_group_id
        returncode: int | None = None

        def poll(self) -> None:
            return None

        def wait(self, timeout: float | None = None) -> int:
            raise subprocess.TimeoutExpired(
                f"{secret}-{process_group_id}",
                timeout,
            )

    def spawn_then_signal(*_args: object, **_kwargs: object) -> SyntheticChild:
        os.kill(os.getpid(), signal.SIGTERM)
        return SyntheticChild()

    def interrupt(delivered_signum: int, _frame: object) -> None:
        raise proof_guard.GuardSignal(delivered_signum)

    monkeypatch.setattr(proof_guard.subprocess, "Popen", spawn_then_signal)
    monkeypatch.setattr(proof_guard, "group_exists", lambda _pgid: True)
    monkeypatch.setattr(
        proof_guard.os,
        "killpg",
        lambda pgid, signum: killpg_calls.append((pgid, signum)),
    )
    monkeypatch.setattr(proof_guard.time, "monotonic", clock.monotonic)
    monkeypatch.setattr(
        proof_guard.time,
        "sleep",
        lambda seconds: setattr(clock, "now", clock.now + seconds),
    )
    previous_handler = signal.signal(signal.SIGTERM, interrupt)
    try:
        with pytest.raises(
            RuntimeError,
            match="^proof guard safety cleanup failed$",
        ) as exc_info:
            if launch_role == "short":
                proof_guard.run_guarded(
                    ("synthetic-command", secret),
                    timeout_seconds=5.0,
                    grace_seconds=0.05,
                )
            elif launch_role == "phase":
                proof_guard._run_long_phase(
                    ("synthetic-command", secret),
                    "preflight",
                    timeout_seconds=5.0,
                    progress_seconds=1.0,
                    grace_seconds=0.05,
                    monitor=None,
                    clock=clock.monotonic,
                    launcher_pid=os.getppid(),
                    coordinator_pid=os.getpid(),
                    phase_audit=audit,
                )
            else:
                proof_guard.read_bounded_macos_thermal_state(
                    deadline=1.0,
                    clock=clock.monotonic,
                )
    finally:
        signal.signal(signal.SIGTERM, previous_handler)

    captured = capsys.readouterr()
    exception_chain = _exception_chain(exc_info.value)
    exception_chain_text = " ".join(
        f"{current!r} {current.args!r} {vars(current)!r}"
        for current in exception_chain
    )
    assert exception_chain == (exc_info.value,)
    assert killpg_calls == [
        (process_group_id, signal.SIGTERM),
        (process_group_id, signal.SIGKILL),
    ]
    combined_text = captured.out + captured.err + exception_chain_text
    assert str(process_group_id) not in combined_text
    assert secret not in combined_text
    if launch_role == "phase":
        assert audit == proof_guard.PhaseAudit(
            pgid=process_group_id,
            outcome="cleanup_stop",
            guard_status=proof_guard.SAFETY_EXIT,
            child_exit_status=None,
            exact_group_absent=False,
        )


def test_cleanup_sends_sigterm_before_sigkill_to_surviving_exact_group(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    process_group_id = 900_000
    clock = _FakeClock()
    group_alive = True
    killpg_calls: list[tuple[int, int]] = []

    class SyntheticChild:
        pid = process_group_id

        def poll(self) -> None:
            return None

        def wait(self, timeout: float | None = None) -> int:
            assert timeout == 0.1
            return 0

    def killpg(target_group_id: int, signum: int) -> None:
        nonlocal group_alive
        killpg_calls.append((target_group_id, signum))
        if signum == signal.SIGKILL:
            group_alive = False

    monkeypatch.setattr(proof_guard.time, "monotonic", clock.monotonic)
    monkeypatch.setattr(
        proof_guard.time,
        "sleep",
        lambda seconds: setattr(clock, "now", clock.now + seconds),
    )
    monkeypatch.setattr(proof_guard.os, "killpg", killpg)
    monkeypatch.setattr(proof_guard, "group_exists", lambda _pgid: group_alive)

    proof_guard.terminate_group(SyntheticChild(), grace_seconds=0.02)

    assert killpg_calls == [
        (process_group_id, signal.SIGTERM),
        (process_group_id, signal.SIGKILL),
    ]
    assert group_alive is False


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


def test_exec_trampoline_unblocks_all_guard_signals_before_target(
    tmp_path: Path,
) -> None:
    mask_file = tmp_path / "target-signal-mask.json"
    child_program = "\n".join(
        (
            "import json, pathlib, signal",
            "blocked = signal.pthread_sigmask(signal.SIG_BLOCK, set())",
            f"guarded = {tuple(int(item) for item in (signal.SIGHUP, signal.SIGTERM, signal.SIGINT))!r}",
            f"pathlib.Path({str(mask_file)!r}).write_text(json.dumps(sorted(int(item) for item in blocked if int(item) in guarded)))",
        )
    )
    guarded_signals = {signal.SIGHUP, signal.SIGTERM, signal.SIGINT}
    previous_mask = signal.pthread_sigmask(signal.SIG_BLOCK, guarded_signals)
    try:
        status = proof_guard.run_guarded(
            (sys.executable, "-c", child_program),
            timeout_seconds=2.0,
            grace_seconds=0.1,
        )
    finally:
        signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)

    assert status == 0
    assert json.loads(mask_file.read_text()) == []


def test_exec_trampoline_roundtrips_surrogate_escaped_posix_argv(
    tmp_path: Path,
) -> None:
    argv_file = tmp_path / "surrogate-argv.bin"
    raw_argument = b"\xffpipe-argv-byte-sentinel"
    surrogate_argument = os.fsdecode(raw_argument)
    child_program = "\n".join(
        (
            "import os, pathlib, sys",
            f"pathlib.Path({str(argv_file)!r}).write_bytes(os.fsencode(sys.argv[1]))",
        )
    )

    status = proof_guard.run_guarded(
        (sys.executable, "-c", child_program, surrogate_argument),
        timeout_seconds=2.0,
        grace_seconds=0.1,
    )

    assert status == 0
    assert argv_file.read_bytes() == raw_argument


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


def test_lock_creation_base_exception_closes_fd_and_unlinks_exact_inode(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    lock_path = tmp_path / "process-guard" / "active.json"
    opened_fds: list[int] = []
    real_open = proof_guard.os.open
    real_fstat = proof_guard.os.fstat
    fstat_calls = 0

    def record_open(*args: object, **kwargs: object) -> int:
        fd = real_open(*args, **kwargs)
        opened_fds.append(fd)
        return fd

    def interrupt_first_fstat(fd: int) -> os.stat_result:
        nonlocal fstat_calls
        fstat_calls += 1
        if fstat_calls == 1:
            raise KeyboardInterrupt
        return real_fstat(fd)

    monkeypatch.setattr(proof_guard.os, "open", record_open)
    monkeypatch.setattr(proof_guard.os, "fstat", interrupt_first_fstat)

    with pytest.raises(KeyboardInterrupt):
        proof_guard.ProcessLock(lock_path, run_id="d" * 32).acquire()

    assert not lock_path.exists()
    assert len(opened_fds) == 1
    with pytest.raises(OSError) as exc_info:
        real_fstat(opened_fds[0])
    assert exc_info.value.errno == errno.EBADF


def test_signal_after_exclusive_open_is_deferred_until_exact_inode_cleanup(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    lock_path = tmp_path / "process-guard" / "active.json"
    opened_fds: list[int] = []
    real_open = proof_guard.os.open
    real_fstat = proof_guard.os.fstat
    previous_handler = signal.signal(
        signal.SIGTERM,
        lambda signum, _frame: (_ for _ in ()).throw(
            proof_guard.GuardSignal(signum)
        ),
    )

    def signal_after_open(*args: object, **kwargs: object) -> int:
        fd = real_open(*args, **kwargs)
        opened_fds.append(fd)
        os.kill(os.getpid(), signal.SIGTERM)
        return fd

    monkeypatch.setattr(proof_guard.os, "open", signal_after_open)
    try:
        with pytest.raises(proof_guard.GuardSignal):
            proof_guard.ProcessLock(lock_path, run_id="d" * 32).acquire()
    finally:
        signal.signal(signal.SIGTERM, previous_handler)

    assert not lock_path.exists()
    assert len(opened_fds) == 1
    with pytest.raises(OSError) as exc_info:
        real_fstat(opened_fds[0])
    assert exc_info.value.errno == errno.EBADF


def test_lock_cleanup_never_unlinks_replacement_inode(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    lock_path = tmp_path / "process-guard" / "active.json"
    replacement = b"replacement-lock\n"

    def replace_then_interrupt(*_args: object, **_kwargs: object) -> None:
        lock_path.unlink()
        lock_path.write_bytes(replacement)
        raise proof_guard.GuardSignal(signal.SIGTERM)

    monkeypatch.setattr(proof_guard.json, "dump", replace_then_interrupt)

    with pytest.raises(proof_guard.GuardSignal):
        proof_guard.ProcessLock(lock_path, run_id="e" * 32).acquire()

    assert lock_path.read_bytes() == replacement


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


def test_subsecond_progress_is_rejected_without_launch_or_disclosure(
    tmp_path: Path,
) -> None:
    marker = tmp_path / "subsecond-progress-started"
    sentinel = "subsecond-progress-secret"
    result = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--long-run",
            "--timeout-seconds",
            "61",
            "--progress-seconds",
            "0.999999",
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


def test_long_run_parser_accepts_smallest_progress_interval() -> None:
    args = parse_args(
        [
            "--long-run",
            "--timeout-seconds",
            "61",
            "--preflight-seconds",
            "0.25",
            "--progress-seconds",
            "1",
            "--",
            "proof-command",
        ]
    )

    assert args.long_run is True
    assert args.preflight_seconds == 0.25
    assert args.progress_seconds == 1.0


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


def test_real_argv_roundtrip_is_absent_from_wrapper_argv_audit_and_errors(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    process_guard_dir = tmp_path / "process-guard"
    lock_path = process_guard_dir / "active.json"
    last_run_path = process_guard_dir / "last-run.json"
    records_path = tmp_path / "argv-roundtrip.jsonl"
    sentinel = "pipe-only-real-argv-secret-sentinel"
    wrapper_calls: list[tuple[object, dict[str, object]]] = []
    real_popen = proof_guard.subprocess.Popen
    child_program = "\n".join(
        (
            "import json, pathlib, sys",
            f"path = pathlib.Path({str(records_path)!r})",
            "with path.open('a', encoding='utf-8') as stream:",
            "    stream.write(json.dumps(sys.argv[1:]) + '\\n')",
        )
    )

    def record_wrapper(
        command: object,
        **kwargs: object,
    ) -> subprocess.Popen[object]:
        wrapper_calls.append((command, kwargs))
        return real_popen(command, **kwargs)

    monkeypatch.setattr(proof_guard, "LOCK_PATH", lock_path)
    monkeypatch.setattr(proof_guard, "LAST_RUN_PATH", last_run_path)
    monkeypatch.setattr(proof_guard, "SafetyMonitor", lambda: None)
    monkeypatch.setattr(proof_guard.subprocess, "Popen", record_wrapper)

    status = proof_guard.main(
        [
            "--long-run",
            "--preflight-seconds",
            "0.5",
            "--timeout-seconds",
            "61",
            "--",
            sys.executable,
            "-c",
            child_program,
            sentinel,
        ]
    )

    captured = capsys.readouterr()
    audit_text = last_run_path.read_text(encoding="utf-8")
    records = [json.loads(line) for line in records_path.read_text().splitlines()]
    assert status == 0
    assert records == [[sentinel], [sentinel]]
    assert len(wrapper_calls) == 2
    for wrapper_argv, wrapper_kwargs in wrapper_calls:
        wrapper_text = repr((wrapper_argv, wrapper_kwargs))
        assert sentinel not in wrapper_text
        assert wrapper_kwargs["shell"] is False
        assert wrapper_kwargs["start_new_session"] is True
        assert wrapper_kwargs["cwd"] == PROJECT_ROOT
        assert "pass_fds" in wrapper_kwargs
    assert sentinel not in audit_text
    assert sentinel not in captured.out
    assert sentinel not in captured.err


def test_start_failure_keeps_real_argv_out_of_wrapper_audit_and_error(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    process_guard_dir = tmp_path / "process-guard"
    lock_path = process_guard_dir / "active.json"
    last_run_path = process_guard_dir / "last-run.json"
    sentinel = "failed-launch-real-argv-secret-sentinel"
    wrapper_calls: list[tuple[object, dict[str, object]]] = []

    def fail_wrapper(command: object, **kwargs: object) -> None:
        wrapper_calls.append((command, kwargs))
        raise OSError(errno.ENOENT, "synthetic fixed launch failure")

    monkeypatch.setattr(proof_guard, "LOCK_PATH", lock_path)
    monkeypatch.setattr(proof_guard, "LAST_RUN_PATH", last_run_path)
    monkeypatch.setattr(proof_guard, "SafetyMonitor", lambda: None)
    monkeypatch.setattr(proof_guard.subprocess, "Popen", fail_wrapper)

    status = proof_guard.main(
        [
            "--long-run",
            "--preflight-seconds",
            "0.5",
            "--timeout-seconds",
            "61",
            "--",
            "synthetic-command",
            sentinel,
        ]
    )

    captured = capsys.readouterr()
    audit_text = last_run_path.read_text(encoding="utf-8")
    audit = json.loads(audit_text)
    assert status == proof_guard.PREFLIGHT_EXIT
    assert audit["classification"] == "start_guard_error"
    assert audit["phases"]["preflight"]["outcome"] == "start_error"
    assert len(wrapper_calls) == 1
    assert sentinel not in repr(wrapper_calls[0])
    assert sentinel not in audit_text
    assert sentinel not in captured.out
    assert sentinel not in captured.err


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


def test_clean_long_run_writes_private_locked_audit_and_rechecks_both_groups(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    command_sentinel = "clean-audit-command-secret"
    environment_sentinel = "clean-audit-environment-secret"
    status, lock_path, last_run_path, group_checks = (
        run_immediate_synthetic_long_main(
            monkeypatch,
            tmp_path,
            (0, 0),
            command_sentinel=command_sentinel,
            environment_sentinel=environment_sentinel,
        )
    )

    raw_record = last_run_path.read_text(encoding="utf-8")
    record = json.loads(raw_record)
    assert status == 0
    assert not lock_path.exists()
    assert last_run_path.stat().st_mode & 0o777 == 0o600
    assert command_sentinel not in raw_record
    assert environment_sentinel not in raw_record
    assert set(record) == {
        "schema",
        "version",
        "run_id",
        "state",
        "started_at",
        "finished_at",
        "launcher_pid",
        "coordinator_pid",
        "phases",
        "classification",
        "guard_status",
        "return_status",
        "lock_release_pending",
    }
    assert record["schema"] == "acsolverx.proof-process-guard.last-run"
    assert record["version"] == 1
    assert record["state"] == "finalized"
    assert len(record["run_id"]) == 32
    assert datetime.fromisoformat(record["started_at"]).tzinfo is not None
    assert datetime.fromisoformat(record["finished_at"]).tzinfo is not None
    assert record["launcher_pid"] == 620_000
    assert record["coordinator_pid"] == os.getpid()
    assert record["phases"] == {
        "preflight": {
            "pgid": 720_000,
            "outcome": "child_exit",
            "guard_status": 0,
            "child_exit_status": 0,
            "exact_group_absent": True,
        },
        "experiment": {
            "pgid": 720_001,
            "outcome": "child_exit",
            "guard_status": 0,
            "child_exit_status": 0,
            "exact_group_absent": True,
        },
    }
    assert record["classification"] == "experiment_child_exit"
    assert record["guard_status"] == 0
    assert record["return_status"] == 0
    assert record["lock_release_pending"] is True
    assert group_checks.count((720_000, True)) == 2
    assert group_checks.count((720_001, True)) == 2


def test_audit_write_precedes_release_and_blocks_another_guard_acquisition(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    events: list[str] = []
    blocked_acquisitions: list[bool] = []
    atomic_write = proof_guard._atomic_write_long_run_audit
    release = proof_guard.ProcessLock.release

    def observed_atomic_write(audit: object) -> None:
        events.append("write")
        competing_lock = proof_guard.ProcessLock(proof_guard.LOCK_PATH)
        try:
            competing_lock.acquire()
        except proof_guard.LockHeldError:
            blocked_acquisitions.append(True)
        else:
            blocked_acquisitions.append(False)
            release(competing_lock)
        atomic_write(audit)

    def observed_release(process_lock: object) -> None:
        events.append("release")
        release(process_lock)

    monkeypatch.setattr(
        proof_guard,
        "_atomic_write_long_run_audit",
        observed_atomic_write,
    )
    monkeypatch.setattr(proof_guard.ProcessLock, "release", observed_release)

    status, lock_path, _last_run_path, _group_checks = (
        run_immediate_synthetic_long_main(monkeypatch, tmp_path, (0, 0))
    )

    assert status == 0
    assert blocked_acquisitions == [True, True]
    assert events == ["write", "write", "release"]
    assert not lock_path.exists()


def test_run_id_binds_active_lock_in_progress_and_finalized_audit(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    process_guard_dir = tmp_path / "process-guard"
    lock_path = process_guard_dir / "active.json"
    last_run_path = process_guard_dir / "last-run.json"
    run_id = "a" * 32
    observations: list[tuple[dict[str, object], dict[str, object]]] = []
    phase_pids = iter((740_000, 740_001))

    class SyntheticChild:
        def __init__(self, pid: int) -> None:
            self.pid = pid

        def poll(self) -> int:
            return 0

    def popen(*_args: object, **_kwargs: object) -> object:
        observations.append(
            (
                json.loads(lock_path.read_text(encoding="utf-8")),
                json.loads(last_run_path.read_text(encoding="utf-8")),
            )
        )
        return SyntheticChild(next(phase_pids))

    monkeypatch.setattr(proof_guard, "LOCK_PATH", lock_path)
    monkeypatch.setattr(proof_guard, "LAST_RUN_PATH", last_run_path)
    monkeypatch.setattr(proof_guard, "_new_run_id", lambda: run_id, raising=False)
    monkeypatch.setattr(proof_guard, "SafetyMonitor", lambda: None)
    monkeypatch.setattr(proof_guard.subprocess, "Popen", popen)
    monkeypatch.setattr(proof_guard, "group_exists", lambda _pgid: False)

    status = proof_guard.main(
        [
            "--long-run",
            "--preflight-seconds",
            "0.1",
            "--timeout-seconds",
            "61",
            "--",
            "synthetic-command",
        ]
    )

    final_record = json.loads(last_run_path.read_text(encoding="utf-8"))
    assert status == 0
    assert len(observations) == 2
    assert all(lock["run_id"] == run_id for lock, _audit in observations)
    assert all(audit["run_id"] == run_id for _lock, audit in observations)
    assert all(audit["state"] == "in_progress" for _lock, audit in observations)
    assert final_record["run_id"] == run_id
    assert final_record["state"] == "finalized"


def test_permanent_final_replace_failure_preserves_fresh_in_progress_audit(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    process_guard_dir = tmp_path / "process-guard"
    process_guard_dir.mkdir(parents=True)
    last_run_path = process_guard_dir / "last-run.json"
    stale_sentinel = "stale-audit-sensitive-sentinel"
    last_run_path.write_text(
        json.dumps(
            {
                "run_id": "stale-run",
                "state": "finalized",
                "forbidden": stale_sentinel,
            }
        ),
        encoding="utf-8",
    )
    run_id = "b" * 32
    real_replace = proof_guard.os.replace
    replace_calls = 0

    def fail_final_replace(source: object, destination: object) -> None:
        nonlocal replace_calls
        replace_calls += 1
        if replace_calls == 1:
            real_replace(source, destination)
            return
        raise OSError("synthetic permanent final replace failure")

    monkeypatch.setattr(proof_guard, "_new_run_id", lambda: run_id, raising=False)
    monkeypatch.setattr(proof_guard.os, "replace", fail_final_replace)
    status, lock_path, observed_last_run_path, _group_checks = (
        run_immediate_synthetic_long_main(monkeypatch, tmp_path, (0, 0))
    )

    record = json.loads(observed_last_run_path.read_text(encoding="utf-8"))
    assert status == proof_guard.SAFETY_EXIT
    assert not lock_path.exists()
    assert replace_calls == 2
    assert record["run_id"] == run_id
    assert record["state"] == "in_progress"
    assert stale_sentinel not in observed_last_run_path.read_text(encoding="utf-8")
    assert observed_last_run_path.stat().st_mode & 0o777 == 0o600


def test_duplicate_long_run_never_touches_active_run_audit(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    process_guard_dir = tmp_path / "process-guard"
    process_guard_dir.mkdir(parents=True)
    lock_path = process_guard_dir / "active.json"
    last_run_path = process_guard_dir / "last-run.json"
    active_run_id = "c" * 32
    lock_path.write_text(
        json.dumps(
            {
                "pid": os.getpid(),
                "started_at": "active",
                "worktree": "synthetic",
                "run_id": active_run_id,
            }
        ),
        encoding="utf-8",
    )
    original_audit = (
        json.dumps({"run_id": active_run_id, "state": "in_progress"}) + "\n"
    ).encode()
    last_run_path.write_bytes(original_audit)
    launches: list[bool] = []

    monkeypatch.setattr(proof_guard, "LOCK_PATH", lock_path)
    monkeypatch.setattr(proof_guard, "LAST_RUN_PATH", last_run_path)
    monkeypatch.setattr(
        proof_guard.subprocess,
        "Popen",
        lambda *_args, **_kwargs: launches.append(True),
    )

    status = proof_guard.main(
        [
            "--long-run",
            "--timeout-seconds",
            "61",
            "--",
            "synthetic-command",
        ]
    )

    assert status == proof_guard.DUPLICATE_EXIT
    assert launches == []
    assert last_run_path.read_bytes() == original_audit


def test_signal_raised_after_lock_acquisition_still_releases_owned_inode(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    process_guard_dir = tmp_path / "process-guard"
    lock_path = process_guard_dir / "active.json"
    last_run_path = process_guard_dir / "last-run.json"
    acquire = proof_guard.ProcessLock.acquire

    def acquire_then_interrupt(process_lock: object) -> None:
        acquire(process_lock)
        raise proof_guard.GuardSignal(signal.SIGTERM)

    monkeypatch.setattr(proof_guard, "LOCK_PATH", lock_path)
    monkeypatch.setattr(proof_guard, "LAST_RUN_PATH", last_run_path)
    monkeypatch.setattr(proof_guard.ProcessLock, "acquire", acquire_then_interrupt)

    status = proof_guard.main(
        [
            "--long-run",
            "--timeout-seconds",
            "61",
            "--",
            "synthetic-command",
        ]
    )

    assert status == proof_guard.SAFETY_EXIT
    assert not lock_path.exists()


def test_signal_during_finalization_is_mapped_before_lock_release(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    finalize = proof_guard._finalize_long_run_audit
    finalize_calls = 0

    def interrupt_first_finalization(*args: object, **kwargs: object) -> int:
        nonlocal finalize_calls
        finalize_calls += 1
        if finalize_calls == 1:
            raise proof_guard.GuardSignal(signal.SIGTERM)
        return finalize(*args, **kwargs)

    monkeypatch.setattr(
        proof_guard,
        "_finalize_long_run_audit",
        interrupt_first_finalization,
    )
    status, lock_path, last_run_path, _group_checks = (
        run_immediate_synthetic_long_main(monkeypatch, tmp_path, (0, 0))
    )

    record = json.loads(last_run_path.read_text(encoding="utf-8"))
    expected_status = 128 + signal.SIGTERM
    assert status == expected_status
    assert finalize_calls == 2
    assert not lock_path.exists()
    assert record["classification"] == "interruption"
    assert record["guard_status"] == expected_status
    assert record["return_status"] == expected_status


def test_launcher_pid_is_captured_before_argument_parsing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    process_guard_dir = tmp_path / "process-guard"
    lock_path = process_guard_dir / "active.json"
    last_run_path = process_guard_dir / "last-run.json"
    parent_pid = [660_000]
    parse_args = proof_guard.parse_args
    phase_pids = iter((760_000, 760_001))

    class SyntheticChild:
        def __init__(self, pid: int) -> None:
            self.pid = pid

        def poll(self) -> int:
            return 0

    def parse_then_reparent(argv: object) -> object:
        parsed = parse_args(argv)
        parent_pid[0] = 660_001
        return parsed

    monkeypatch.setattr(proof_guard, "LOCK_PATH", lock_path)
    monkeypatch.setattr(proof_guard, "LAST_RUN_PATH", last_run_path)
    monkeypatch.setattr(proof_guard, "parse_args", parse_then_reparent)
    monkeypatch.setattr(proof_guard.os, "getppid", lambda: parent_pid[0])
    monkeypatch.setattr(proof_guard, "SafetyMonitor", lambda: None)
    monkeypatch.setattr(
        proof_guard.subprocess,
        "Popen",
        lambda *_args, **_kwargs: SyntheticChild(next(phase_pids)),
    )
    monkeypatch.setattr(proof_guard, "group_exists", lambda _pgid: False)

    status = proof_guard.main(
        [
            "--long-run",
            "--preflight-seconds",
            "0.1",
            "--timeout-seconds",
            "61",
            "--",
            "synthetic-command",
        ]
    )

    record = json.loads(last_run_path.read_text(encoding="utf-8"))
    assert status == 0
    assert record["launcher_pid"] == 660_000


def test_failed_preflight_audit_has_no_experiment_pgid(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    status, _lock_path, last_run_path, _group_checks = (
        run_immediate_synthetic_long_main(monkeypatch, tmp_path, (9,))
    )

    record = json.loads(last_run_path.read_text(encoding="utf-8"))
    assert status == proof_guard.PREFLIGHT_EXIT
    assert record["classification"] == "preflight_child_exit"
    assert record["guard_status"] == proof_guard.PREFLIGHT_EXIT
    assert record["return_status"] == proof_guard.PREFLIGHT_EXIT
    assert record["phases"]["preflight"] == {
        "pgid": 720_000,
        "outcome": "child_exit",
        "guard_status": 0,
        "child_exit_status": 9,
        "exact_group_absent": True,
    }
    assert record["phases"]["experiment"] == {
        "pgid": None,
        "outcome": "not_started",
        "guard_status": None,
        "child_exit_status": None,
        "exact_group_absent": None,
    }


@pytest.mark.parametrize(
    "experiment_status",
    (
        proof_guard.DUPLICATE_EXIT,
        proof_guard.TIMEOUT_EXIT,
        proof_guard.PREFLIGHT_EXIT,
        proof_guard.SAFETY_EXIT,
    ),
)
def test_reserved_experiment_status_is_classified_as_completion(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    experiment_status: int,
) -> None:
    status, _lock_path, last_run_path, _group_checks = (
        run_immediate_synthetic_long_main(
            monkeypatch,
            tmp_path,
            (0, experiment_status),
        )
    )

    record = json.loads(last_run_path.read_text(encoding="utf-8"))
    assert status == experiment_status
    assert record["classification"] == "experiment_child_exit"
    assert record["guard_status"] == 0
    assert record["return_status"] == experiment_status
    assert record["phases"]["experiment"]["outcome"] == "child_exit"
    assert (
        record["phases"]["experiment"]["child_exit_status"]
        == experiment_status
    )


def test_atomic_audit_replace_failure_changes_final_status_to_safety(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    replace_calls: list[tuple[object, object]] = []

    def fail_replace(source: object, destination: object) -> None:
        replace_calls.append((source, destination))
        raise OSError("synthetic atomic replace failure")

    monkeypatch.setattr(proof_guard.os, "replace", fail_replace)
    status, _lock_path, last_run_path, _group_checks = (
        run_immediate_synthetic_long_main(monkeypatch, tmp_path, (0, 0))
    )

    assert status == proof_guard.SAFETY_EXIT
    assert replace_calls
    assert not last_run_path.exists()


@pytest.mark.parametrize(
    ("phase_modes", "expected_status", "expected_classification", "phase"),
    (
        (("timeout",), 125, "preflight_timeout", "preflight"),
        (("complete", "timeout"), 124, "experiment_timeout", "experiment"),
    ),
)
def test_phase_timeout_audit_is_not_confused_with_completed_status_124(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    phase_modes: tuple[str, ...],
    expected_status: int,
    expected_classification: str,
    phase: str,
) -> None:
    status, _lock_path, last_run_path, killpg_calls, _group_checks = (
        run_mode_synthetic_long_main(monkeypatch, tmp_path, phase_modes)
    )

    record = json.loads(last_run_path.read_text(encoding="utf-8"))
    expected_pgid = 730_000 if phase == "preflight" else 730_001
    assert status == expected_status
    assert record["classification"] == expected_classification
    assert record["guard_status"] == expected_status
    assert record["return_status"] == expected_status
    assert record["phases"][phase] == {
        "pgid": expected_pgid,
        "outcome": "timeout",
        "guard_status": proof_guard.TIMEOUT_EXIT,
        "child_exit_status": None,
        "exact_group_absent": True,
    }
    assert killpg_calls == [(expected_pgid, signal.SIGTERM)]


def test_safety_stop_audit_records_exact_group_cleanup(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    status, _lock_path, last_run_path, killpg_calls, _group_checks = (
        run_mode_synthetic_long_main(
            monkeypatch,
            tmp_path,
            ("complete", "running"),
            samples=(_safety_sample(), _safety_sample(thermal_state=1)),
        )
    )

    record = json.loads(last_run_path.read_text(encoding="utf-8"))
    assert status == proof_guard.SAFETY_EXIT
    assert record["classification"] == "safety_cleanup_stop"
    assert record["phases"]["experiment"] == {
        "pgid": 730_001,
        "outcome": "safety_stop",
        "guard_status": proof_guard.SAFETY_EXIT,
        "child_exit_status": None,
        "exact_group_absent": True,
    }
    assert killpg_calls == [(730_001, signal.SIGTERM)]


def test_safety_stop_preserves_already_observed_child_exit_status(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    status, _lock_path, last_run_path, killpg_calls, _group_checks = (
        run_mode_synthetic_long_main(
            monkeypatch,
            tmp_path,
            ("complete",),
            samples=(_safety_sample(thermal_state=1),),
        )
    )

    record = json.loads(last_run_path.read_text(encoding="utf-8"))
    assert status == proof_guard.SAFETY_EXIT
    assert record["classification"] == "safety_cleanup_stop"
    assert record["phases"]["preflight"] == {
        "pgid": 730_000,
        "outcome": "safety_stop",
        "guard_status": proof_guard.SAFETY_EXIT,
        "child_exit_status": 0,
        "exact_group_absent": True,
    }
    assert killpg_calls == []


def test_sample_deadline_preserves_already_observed_child_exit_status(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = _FakeClock()
    process_group_id = 731_000

    class FastExitChild:
        pid = process_group_id

        def poll(self) -> int:
            return 0

    monkeypatch.setattr(
        proof_guard.subprocess,
        "Popen",
        lambda *_args, **_kwargs: FastExitChild(),
    )
    monkeypatch.setattr(proof_guard, "group_exists", lambda _pgid: False)
    monkeypatch.setattr(
        proof_guard.os,
        "killpg",
        lambda _pgid, _signum: (_ for _ in ()).throw(ProcessLookupError),
    )
    monitor = _SequenceMonitor(
        [_safety_sample()],
        clock,
        sample_advances=[1.1],
    )
    audit = proof_guard.LongRunAudit(
        run_id="f" * 32,
        started_at="synthetic",
        launcher_pid=670_000,
        coordinator_pid=os.getpid(),
    )

    status = run_long_guarded(
        ("synthetic-command",),
        preflight_seconds=1.0,
        experiment_seconds=1.0,
        progress_seconds=1.0,
        grace_seconds=0.1,
        monitor=monitor,
        clock=clock.monotonic,
        launcher_pid=670_000,
        audit=audit,
    )

    assert status == proof_guard.PREFLIGHT_EXIT
    assert audit.phases["preflight"].outcome == "timeout"
    assert audit.phases["preflight"].guard_status == proof_guard.TIMEOUT_EXIT
    assert audit.phases["preflight"].child_exit_status == 0


def test_interruption_audit_records_status_and_exact_group_cleanup(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    status, _lock_path, last_run_path, killpg_calls, _group_checks = (
        run_mode_synthetic_long_main(
            monkeypatch,
            tmp_path,
            ("complete", "running"),
            samples=(
                _safety_sample(),
                proof_guard.GuardSignal(signal.SIGTERM),
            ),
        )
    )

    record = json.loads(last_run_path.read_text(encoding="utf-8"))
    expected_status = 128 + signal.SIGTERM
    assert status == expected_status
    assert record["classification"] == "interruption"
    assert record["guard_status"] == expected_status
    assert record["return_status"] == expected_status
    assert record["phases"]["experiment"] == {
        "pgid": 730_001,
        "outcome": "interrupted",
        "guard_status": expected_status,
        "child_exit_status": None,
        "exact_group_absent": True,
    }
    assert killpg_calls == [(730_001, signal.SIGTERM)]


def test_helper_cleanup_failure_is_a_sanitized_safety_cleanup_stop(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    process_guard_dir = tmp_path / "process-guard"
    lock_path = process_guard_dir / "active.json"
    last_run_path = process_guard_dir / "last-run.json"
    clock = _FakeClock()
    phase_group_id = 988_100_001
    helper_group_id = 988_100_002
    helper_secret = "helper-audit-cleanup-secret-sentinel"
    phase_alive = True
    popen_calls = 0
    killpg_calls: list[tuple[int, int]] = []
    real_safety_monitor = proof_guard.SafetyMonitor

    class SyntheticPhase:
        pid = phase_group_id

        def poll(self) -> None:
            return None

        def wait(self, timeout: float | None = None) -> int:
            raise AssertionError("phase wait ran after immediate helper failure")

    class SyntheticProbe:
        pid = helper_group_id
        returncode: int | None = None

        def communicate(self, timeout: float) -> tuple[str, str]:
            assert timeout > 0
            raise proof_guard.GuardSignal(signal.SIGTERM)

        def poll(self) -> None:
            return None

        def wait(self, timeout: float | None = None) -> int:
            raise subprocess.TimeoutExpired(
                f"{helper_secret}-{helper_group_id}",
                timeout,
            )

    def popen(*_args: object, **_kwargs: object) -> object:
        nonlocal popen_calls
        popen_calls += 1
        return SyntheticPhase() if popen_calls == 1 else SyntheticProbe()

    def group_exists(process_group_id: int) -> bool:
        if process_group_id == helper_group_id:
            return True
        if process_group_id == phase_group_id:
            return phase_alive
        return False

    def killpg(process_group_id: int, signum: int) -> None:
        nonlocal phase_alive
        killpg_calls.append((process_group_id, signum))
        if process_group_id == phase_group_id:
            phase_alive = False

    class HelperFailureMonitor:
        def verify_launcher_coordinator(
            self,
            launcher_pid: int,
            coordinator_pid: int,
            sample_deadline: float | None = None,
        ) -> None:
            del launcher_pid, coordinator_pid, sample_deadline
            return None

        def sample(self, **kwargs: object) -> object:
            return real_safety_monitor(
                process_reader=lambda _timeout: (),
                thermal_reader=lambda deadline: (
                    proof_guard.read_bounded_macos_thermal_state(
                        deadline,
                        clock=clock.monotonic,
                    )
                ),
                clock=clock.monotonic,
            ).sample(**kwargs)

    monkeypatch.setattr(proof_guard, "LOCK_PATH", lock_path)
    monkeypatch.setattr(proof_guard, "LAST_RUN_PATH", last_run_path)
    monkeypatch.setattr(proof_guard, "SafetyMonitor", HelperFailureMonitor)
    monkeypatch.setattr(proof_guard.subprocess, "Popen", popen)
    monkeypatch.setattr(proof_guard, "group_exists", group_exists)
    monkeypatch.setattr(proof_guard.os, "killpg", killpg)
    monkeypatch.setattr(proof_guard.time, "monotonic", clock.monotonic)
    monkeypatch.setattr(
        proof_guard.time,
        "sleep",
        lambda seconds: setattr(clock, "now", clock.now + seconds),
    )

    status = proof_guard.main(
        [
            "--long-run",
            "--preflight-seconds",
            "1",
            "--timeout-seconds",
            "61",
            "--",
            "synthetic-command",
            helper_secret,
        ]
    )

    captured = capsys.readouterr()
    audit_text = last_run_path.read_text(encoding="utf-8")
    audit = json.loads(audit_text)
    assert status == proof_guard.SAFETY_EXIT
    assert audit["classification"] == "safety_cleanup_stop"
    assert audit["guard_status"] == proof_guard.SAFETY_EXIT
    assert audit["return_status"] == proof_guard.SAFETY_EXIT
    assert audit["phases"]["preflight"] == {
        "pgid": phase_group_id,
        "outcome": "safety_stop",
        "guard_status": proof_guard.SAFETY_EXIT,
        "child_exit_status": None,
        "exact_group_absent": True,
    }
    assert killpg_calls == [
        (helper_group_id, signal.SIGTERM),
        (helper_group_id, signal.SIGKILL),
        (phase_group_id, signal.SIGTERM),
    ]
    combined_text = captured.out + captured.err + audit_text
    assert str(helper_group_id) not in combined_text
    assert helper_secret not in combined_text


def test_start_error_audit_has_no_phase_pgid_and_stays_distinguishable(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    status, _lock_path, last_run_path, killpg_calls, _group_checks = (
        run_mode_synthetic_long_main(monkeypatch, tmp_path, ("start_error",))
    )

    record = json.loads(last_run_path.read_text(encoding="utf-8"))
    assert status == proof_guard.PREFLIGHT_EXIT
    assert record["classification"] == "start_guard_error"
    assert record["phases"]["preflight"] == {
        "pgid": None,
        "outcome": "start_error",
        "guard_status": 127,
        "child_exit_status": None,
        "exact_group_absent": None,
    }
    assert killpg_calls == []


def test_failed_final_group_recheck_changes_status_and_is_recorded(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    status, _lock_path, last_run_path, _killpg_calls, group_checks = (
        run_mode_synthetic_long_main(
            monkeypatch,
            tmp_path,
            ("complete", "complete"),
            fail_final_recheck=(730_001,),
        )
    )

    record = json.loads(last_run_path.read_text(encoding="utf-8"))
    assert status == proof_guard.SAFETY_EXIT
    assert record["classification"] == "safety_cleanup_stop"
    assert record["phases"]["preflight"]["exact_group_absent"] is True
    assert record["phases"]["experiment"]["exact_group_absent"] is False
    assert group_checks.count((730_000, True)) == 2
    assert group_checks.count((730_001, True)) == 2


def test_failed_lock_absence_recheck_changes_status_and_is_recorded(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(proof_guard.ProcessLock, "release", lambda _self: None)
    status, lock_path, last_run_path, _group_checks = (
        run_immediate_synthetic_long_main(monkeypatch, tmp_path, (0, 0))
    )

    record = json.loads(last_run_path.read_text(encoding="utf-8"))
    assert status == proof_guard.SAFETY_EXIT
    assert lock_path.exists()
    assert record["classification"] == "experiment_child_exit"
    assert record["guard_status"] == 0
    assert record["return_status"] == 0
    assert record["lock_release_pending"] is True


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
        progress_seconds=1.0,
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
        progress_seconds=1.0,
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
        _process_info(50, 1, 50, 0.0, ucomm="launcher"),
        _process_info(100, 50, 100, 0.0, ucomm="guard"),
        _process_info(200, 100, 200, 50.0, ucomm="phase"),
        _process_info(201, 200, 200, child_cpu, ucomm="worker"),
        _process_info(202, 201, 202, 99.0, ucomm="escaped"),
        _process_info(203, 1, 200, 10.0, ucomm="reparented-worker"),
        _process_info(300, 100, 300, 88.0, ucomm="unrelated"),
    )
    monitor = proof_guard.SafetyMonitor(
        process_reader=lambda _timeout: processes,
        thermal_reader=lambda _deadline: 0,
    )

    sample = monitor.sample(
        child_pid=200,
        process_group_id=200,
        launcher_pid=50,
        coordinator_pid=100,
    )

    assert sample.coordinator_alive is True
    assert sample.phase_leader_reparented is False
    assert sample.group_process_count == 3
    assert sample.group_cpu_percent == pytest.approx(expected_cpu)
    assert sample.escaped_pids == (202,)
    with pytest.raises(FrozenInstanceError):
        sample.group_cpu_percent = 0.0
    with pytest.raises(FrozenInstanceError):
        processes[0].pid = 0


def test_monitor_shares_one_deadline_across_thermal_and_process_sampling() -> None:
    clock = _FakeClock()
    observed_thermal_deadlines: list[float] = []
    observed_timeouts: list[float] = []
    processes = (
        _process_info(50, 1, 50, 0.0),
        _process_info(100, 50, 100, 0.0),
        _process_info(200, 100, 200, 1.0),
    )

    def read_processes(timeout_seconds: float) -> tuple[object, ...]:
        observed_timeouts.append(timeout_seconds)
        clock.now += timeout_seconds
        return processes

    def read_thermal(deadline: float) -> int:
        observed_thermal_deadlines.append(deadline)
        clock.now += 0.6
        return 0

    sample = proof_guard.SafetyMonitor(
        process_reader=read_processes,
        thermal_reader=read_thermal,
        clock=clock.monotonic,
    ).sample(
        child_pid=200,
        process_group_id=200,
        launcher_pid=50,
        coordinator_pid=100,
        sample_deadline=1.0,
    )

    assert sample.failure_reason is None
    assert observed_thermal_deadlines == [1.0]
    assert observed_timeouts == [pytest.approx(0.4)]
    assert clock.now == pytest.approx(1.0)


def test_monitor_skips_process_sampling_when_thermal_consumes_deadline() -> None:
    clock = _FakeClock()
    process_calls: list[float] = []

    def read_thermal(deadline: float) -> int:
        clock.now = deadline
        return 0

    monitor = proof_guard.SafetyMonitor(
        process_reader=lambda timeout: process_calls.append(timeout) or (),
        thermal_reader=read_thermal,
        clock=clock.monotonic,
    )

    sample = monitor.sample(
        child_pid=200,
        process_group_id=200,
        launcher_pid=50,
        coordinator_pid=100,
        sample_deadline=1.0,
    )

    assert sample.failure_reason is not None
    assert "no time remains" in sample.failure_reason
    assert process_calls == []


@pytest.mark.parametrize(
    ("processes", "failure_fragment"),
    (
        (
            (
                _process_info(200, 100, 200, 0.0),
                _process_info(300, 200, 300, 1.0),
            ),
            "launcher process is no longer alive",
        ),
        (
            (
                _process_info(100, 1, 100, 0.0, state="Z"),
                _process_info(200, 100, 200, 0.0),
                _process_info(300, 200, 300, 1.0),
            ),
            "launcher process is no longer alive",
        ),
        (
            (
                _process_info(100, 1, 100, 0.0),
                _process_info(300, 200, 300, 1.0),
            ),
            "guard coordinator process is no longer alive",
        ),
        (
            (
                _process_info(100, 1, 100, 0.0),
                _process_info(200, 100, 200, 0.0, state="Z"),
                _process_info(300, 200, 300, 1.0),
            ),
            "guard coordinator process is no longer alive",
        ),
        (
            (
                _process_info(100, 1, 100, 0.0),
                _process_info(200, 1, 200, 0.0),
                _process_info(300, 200, 300, 1.0),
            ),
            "guard coordinator was reparented away from the launcher",
        ),
        (
            (
                _process_info(100, 1, 100, 0.0),
                _process_info(200, 100, 200, 0.0),
                _process_info(300, 1, 300, 1.0),
            ),
            "phase leader was reparented away from the guard coordinator",
        ),
    ),
)
def test_monitor_fails_closed_for_launcher_coordinator_and_leader_ancestry(
    processes: tuple[object, ...],
    failure_fragment: str,
) -> None:
    sample = proof_guard.SafetyMonitor(
        process_reader=lambda _timeout: processes,
        thermal_reader=lambda _deadline: 0,
    ).sample(
        child_pid=300,
        process_group_id=300,
        launcher_pid=100,
        coordinator_pid=200,
    )

    assert sample.failure_reason is not None
    assert failure_fragment in sample.failure_reason


@pytest.mark.parametrize(
    ("processes", "expected_failure"),
    (
        (
            (
                _process_info(100, 1, 100, 0.0),
                _process_info(200, 100, 200, 0.0),
            ),
            None,
        ),
        (
            (_process_info(200, 100, 200, 0.0),),
            "launcher process is no longer alive",
        ),
        (
            (
                _process_info(100, 1, 100, 0.0, state="Z"),
                _process_info(200, 100, 200, 0.0),
            ),
            "launcher process is no longer alive",
        ),
        (
            (_process_info(100, 1, 100, 0.0),),
            "guard coordinator process is no longer alive",
        ),
        (
            (
                _process_info(100, 1, 100, 0.0),
                _process_info(200, 100, 200, 0.0, state="Z"),
            ),
            "guard coordinator process is no longer alive",
        ),
        (
            (
                _process_info(100, 1, 100, 0.0),
                _process_info(200, 1, 200, 0.0),
            ),
            "guard coordinator was reparented away from the launcher",
        ),
    ),
)
def test_preflight_verifies_launcher_to_coordinator_chain(
    processes: tuple[object, ...],
    expected_failure: str | None,
) -> None:
    monitor = proof_guard.SafetyMonitor(
        process_reader=lambda _timeout: processes,
        thermal_reader=lambda _deadline: 0,
    )

    failure = monitor.verify_launcher_coordinator(
        launcher_pid=100,
        coordinator_pid=200,
        sample_deadline=time.monotonic() + 1.0,
    )

    assert failure == expected_failure


def test_failed_preflight_chain_check_never_launches_a_phase(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    process_guard_dir = tmp_path / "process-guard"
    lock_path = process_guard_dir / "active.json"
    last_run_path = process_guard_dir / "last-run.json"
    chain_calls: list[tuple[int, int]] = []
    launches: list[bool] = []

    class FailingChainMonitor:
        def verify_launcher_coordinator(
            self,
            launcher_pid: int,
            coordinator_pid: int,
            sample_deadline: float | None = None,
        ) -> str:
            assert sample_deadline is not None
            chain_calls.append((launcher_pid, coordinator_pid))
            return "launcher process is no longer alive"

        def sample(self, **_kwargs: object) -> object:
            raise AssertionError("phase monitor ran after failed chain check")

    monkeypatch.setattr(proof_guard, "LOCK_PATH", lock_path)
    monkeypatch.setattr(proof_guard, "LAST_RUN_PATH", last_run_path)
    monkeypatch.setattr(proof_guard.os, "getppid", lambda: 640_000)
    monkeypatch.setattr(proof_guard, "SafetyMonitor", FailingChainMonitor)
    monkeypatch.setattr(
        proof_guard.subprocess,
        "Popen",
        lambda *_args, **_kwargs: launches.append(True),
    )

    status = proof_guard.main(
        [
            "--long-run",
            "--timeout-seconds",
            "61",
            "--",
            "synthetic-command",
        ]
    )

    record = json.loads(last_run_path.read_text(encoding="utf-8"))
    assert status == proof_guard.SAFETY_EXIT
    assert chain_calls == [(640_000, os.getpid())]
    assert launches == []
    assert record["state"] == "finalized"
    assert record["classification"] == "start_guard_error"
    assert record["phases"]["preflight"]["outcome"] == "not_started"


def test_long_phase_monitor_receives_launcher_and_guard_coordinator(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    children = iter((710_000, 710_001))
    calls: list[dict[str, object]] = []

    class SyntheticChild:
        def __init__(self, pid: int) -> None:
            self.pid = pid

        def poll(self) -> int:
            return 0

    class RecordingMonitor:
        def sample(self, **kwargs: object) -> object:
            calls.append(kwargs)
            return _safety_sample()

    monkeypatch.setattr(
        proof_guard.subprocess,
        "Popen",
        lambda *_args, **_kwargs: SyntheticChild(next(children)),
    )
    monkeypatch.setattr(proof_guard, "group_exists", lambda _pgid: False)

    status = run_long_guarded(
        ["synthetic-command"],
        preflight_seconds=1.0,
        experiment_seconds=1.0,
        progress_seconds=1.0,
        grace_seconds=0.1,
        monitor=RecordingMonitor(),
        launcher_pid=610_000,
    )

    assert status == 0
    assert [call["launcher_pid"] for call in calls] == [610_000, 610_000]
    assert [call["coordinator_pid"] for call in calls] == [
        os.getpid(),
        os.getpid(),
    ]


def test_fast_clean_exit_allows_missing_leader_but_still_samples_safety(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    command_sentinel = "fast-exit-command-secret"
    launcher_pid = 650_000
    coordinator_pid = os.getpid()
    processes = (
        _process_info(launcher_pid, 1, launcher_pid, 0.0),
        _process_info(coordinator_pid, launcher_pid, coordinator_pid, 0.0),
    )
    phase_pids = iter((750_000, 750_001))
    killpg_calls: list[tuple[int, int]] = []

    class FastExitChild:
        def __init__(self, pid: int) -> None:
            self.pid = pid

        def poll(self) -> int:
            return 0

    monkeypatch.setattr(
        proof_guard.subprocess,
        "Popen",
        lambda *_args, **_kwargs: FastExitChild(next(phase_pids)),
    )
    monkeypatch.setattr(proof_guard, "group_exists", lambda _pgid: False)
    monkeypatch.setattr(
        proof_guard.os,
        "killpg",
        lambda pgid, signum: killpg_calls.append((pgid, signum)),
    )
    monitor = proof_guard.SafetyMonitor(
        process_reader=lambda _timeout: processes,
        thermal_reader=lambda _deadline: 0,
    )

    status = run_long_guarded(
        ("synthetic-command", command_sentinel),
        preflight_seconds=1.0,
        experiment_seconds=1.0,
        progress_seconds=1.0,
        grace_seconds=0.1,
        monitor=monitor,
        launcher_pid=launcher_pid,
    )

    captured = capsys.readouterr()
    assert status == 0
    assert killpg_calls == []
    assert captured.out.splitlines() == [
        "proof guard progress phase=preflight elapsed=0s "
        "exact_group_process_count=0 aggregate_cpu=0% thermal=nominal",
        "proof guard progress phase=experiment elapsed=0s "
        "exact_group_process_count=0 aggregate_cpu=0% thermal=nominal",
    ]
    assert command_sentinel not in captured.out
    assert command_sentinel not in captured.err


def test_exit_during_sampling_repolls_before_missing_leader_abort(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    launcher_pid = 650_100
    coordinator_pid = os.getpid()
    processes = (
        _process_info(launcher_pid, 1, launcher_pid, 0.0),
        _process_info(coordinator_pid, launcher_pid, coordinator_pid, 0.0),
    )
    phase_pids = iter((750_100, 750_101))
    children: list[object] = []
    killpg_calls: list[tuple[int, int]] = []

    class ExitDuringSampleChild:
        def __init__(self, pid: int) -> None:
            self.pid = pid
            self.poll_calls = 0

        def poll(self) -> int | None:
            self.poll_calls += 1
            return None if self.poll_calls == 1 else 0

    def popen(*_args: object, **_kwargs: object) -> object:
        child = ExitDuringSampleChild(next(phase_pids))
        children.append(child)
        return child

    monkeypatch.setattr(proof_guard.subprocess, "Popen", popen)
    monkeypatch.setattr(proof_guard, "group_exists", lambda _pgid: False)
    monkeypatch.setattr(
        proof_guard.os,
        "killpg",
        lambda pgid, signum: (
            killpg_calls.append((pgid, signum)),
            (_ for _ in ()).throw(ProcessLookupError),
        )[-1],
    )
    monitor = proof_guard.SafetyMonitor(
        process_reader=lambda _timeout: processes,
        thermal_reader=lambda _deadline: 0,
    )

    status = run_long_guarded(
        ("synthetic-command",),
        preflight_seconds=1.0,
        experiment_seconds=1.0,
        progress_seconds=1.0,
        grace_seconds=0.1,
        monitor=monitor,
        launcher_pid=launcher_pid,
    )

    assert status == 0
    assert [child.poll_calls for child in children] == [2, 2]
    assert killpg_calls == []


def test_live_child_with_missing_leader_aborts_its_exact_group(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    launcher_pid = 651_000
    coordinator_pid = os.getpid()
    process_group_id = 751_000
    processes = (
        _process_info(launcher_pid, 1, launcher_pid, 0.0),
        _process_info(coordinator_pid, launcher_pid, coordinator_pid, 0.0),
    )
    group_alive = True
    killpg_calls: list[tuple[int, int]] = []

    class LiveChild:
        pid = process_group_id

        def poll(self) -> None:
            return None

    def killpg(target_group_id: int, signum: int) -> None:
        nonlocal group_alive
        killpg_calls.append((target_group_id, signum))
        group_alive = False

    monkeypatch.setattr(
        proof_guard.subprocess,
        "Popen",
        lambda *_args, **_kwargs: LiveChild(),
    )
    monkeypatch.setattr(
        proof_guard,
        "group_exists",
        lambda _pgid: group_alive,
    )
    monkeypatch.setattr(proof_guard.os, "killpg", killpg)
    monitor = proof_guard.SafetyMonitor(
        process_reader=lambda _timeout: processes,
        thermal_reader=lambda _deadline: 0,
    )

    status = run_long_guarded(
        ("synthetic-command",),
        preflight_seconds=1.0,
        experiment_seconds=1.0,
        progress_seconds=1.0,
        grace_seconds=0.1,
        monitor=monitor,
        launcher_pid=launcher_pid,
    )

    assert status == proof_guard.SAFETY_EXIT
    assert killpg_calls == [(process_group_id, signal.SIGTERM)]
    assert (
        "phase leader is missing from the process table"
        in capsys.readouterr().err
    )


@pytest.mark.parametrize("thermal_state", (0, 1, 2, 3))
def test_monitor_accepts_only_nominal_thermal_state(thermal_state: int) -> None:
    monitor = proof_guard.SafetyMonitor(
        process_reader=lambda _timeout: (
            _process_info(50, 1, 50, 0.0),
            _process_info(100, 50, 100, 0.0),
            _process_info(200, 100, 200, 1.0),
        ),
        thermal_reader=lambda _deadline: thermal_state,
    )

    sample = monitor.sample(
        child_pid=200,
        process_group_id=200,
        launcher_pid=50,
        coordinator_pid=100,
    )

    assert (sample.failure_reason is None) is (thermal_state == 0)


def test_monitor_fails_closed_when_thermal_state_is_unreadable() -> None:
    def unreadable(_deadline: float) -> int:
        raise RuntimeError("thermal API unavailable")

    monitor = proof_guard.SafetyMonitor(
        process_reader=lambda _timeout: (),
        thermal_reader=unreadable,
    )

    sample = monitor.sample(
        child_pid=200,
        process_group_id=200,
        launcher_pid=50,
        coordinator_pid=100,
    )

    assert sample.failure_reason is not None
    assert "thermal API unavailable" in sample.failure_reason


def _install_fake_macos_thermal_api(
    monkeypatch: pytest.MonkeyPatch,
    thermal_state: int,
    missing_method: bytes | None = None,
) -> dict[str, list[object]]:
    import ctypes

    selectors = {b"processInfo": 11, b"thermalState": 12}
    calls: dict[str, list[object]] = {
        "loaded": [],
        "method_lookups": [],
        "implementation_lookups": [],
        "raw_messages": [],
        "imp_messages": [],
    }
    objc_get_class = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_char_p)(
        lambda name: 10 if name == b"NSProcessInfo" else 0
    )
    selector_register = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_char_p)(
        lambda name: selectors.get(name, 0)
    )

    def look_up_class_method(receiver: int, selector: int) -> int:
        calls["method_lookups"].append(("class", receiver, selector))
        if missing_method == b"processInfo":
            return 0
        return 101

    def look_up_instance_method(receiver: int, selector: int) -> int:
        calls["method_lookups"].append(("instance", receiver, selector))
        if missing_method == b"thermalState":
            return 0
        return 102

    class_get_class_method = ctypes.CFUNCTYPE(
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p
    )(look_up_class_method)
    class_get_instance_method = ctypes.CFUNCTYPE(
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p
    )(look_up_instance_method)

    def call_process_info(receiver: int, selector: int) -> int:
        calls["imp_messages"].append((receiver, selector))
        return 20

    def call_thermal_state(receiver: int, selector: int) -> int:
        calls["imp_messages"].append((receiver, selector))
        return thermal_state

    process_info_imp = ctypes.CFUNCTYPE(
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p
    )(call_process_info)
    thermal_state_imp = ctypes.CFUNCTYPE(
        ctypes.c_long, ctypes.c_void_p, ctypes.c_void_p
    )(call_thermal_state)

    def get_implementation(method: int) -> int:
        calls["implementation_lookups"].append(method)
        implementation = process_info_imp if method == 101 else thermal_state_imp
        return ctypes.cast(implementation, ctypes.c_void_p).value or 0

    method_get_implementation = ctypes.CFUNCTYPE(
        ctypes.c_void_p, ctypes.c_void_p
    )(get_implementation)

    def send_raw_message(receiver: int, selector: int) -> int:
        calls["raw_messages"].append((receiver, selector))
        return 20 if (receiver, selector) == (10, 11) else thermal_state

    message_send = ctypes.CFUNCTYPE(
        ctypes.c_long, ctypes.c_void_p, ctypes.c_void_p
    )(send_raw_message)

    class ObjCLibrary:
        objc_getClass = objc_get_class
        sel_registerName = selector_register
        class_getClassMethod = class_get_class_method
        class_getInstanceMethod = class_get_instance_method
        method_getImplementation = method_get_implementation
        objc_msgSend = message_send

    def load_library(path: str) -> object:
        calls["loaded"].append(path)
        if path == "/usr/lib/libobjc.A.dylib":
            return ObjCLibrary()
        if path == "/System/Library/Frameworks/Foundation.framework/Foundation":
            return object()
        raise OSError(path)

    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.setattr(ctypes, "CDLL", load_library)
    return calls


def test_macos_thermal_reader_uses_foundation_and_libobjc(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = _install_fake_macos_thermal_api(monkeypatch, thermal_state=0)

    assert proof_guard.read_macos_thermal_state() == 0
    assert calls["loaded"] == [
        "/System/Library/Frameworks/Foundation.framework/Foundation",
        "/usr/lib/libobjc.A.dylib",
    ]
    assert calls["raw_messages"] == []
    assert calls["imp_messages"] == [(10, 11), (20, 12)]


@pytest.mark.parametrize("missing_method", (b"processInfo", b"thermalState"))
def test_macos_thermal_reader_rejects_missing_method_before_invocation(
    monkeypatch: pytest.MonkeyPatch,
    missing_method: bytes,
) -> None:
    calls = _install_fake_macos_thermal_api(
        monkeypatch,
        thermal_state=0,
        missing_method=missing_method,
    )

    with pytest.raises(RuntimeError, match=missing_method.decode()):
        proof_guard.read_macos_thermal_state()
    assert calls["raw_messages"] == []
    assert calls["imp_messages"] == []


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


def test_internal_thermal_probe_bypasses_proof_lock_and_recursion(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def forbidden(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("internal thermal probe entered guarded execution")

    monkeypatch.setattr(proof_guard, "_read_macos_thermal_state_enum", lambda: 0)
    monkeypatch.setattr(proof_guard.ProcessLock, "acquire", forbidden)
    monkeypatch.setattr(proof_guard.subprocess, "Popen", forbidden)

    status = proof_guard.main(["--internal-thermal-probe"])

    assert status == 0
    assert capsys.readouterr().out == "0\n"


def test_internal_thermal_probe_emits_valid_pressure_enum(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _install_fake_macos_thermal_api(monkeypatch, thermal_state=2)

    status = proof_guard.main(["--internal-thermal-probe"])

    assert status == 0
    assert capsys.readouterr().out == "2\n"


def test_bounded_thermal_probe_uses_fixed_internal_mode_and_parses_enum(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = _FakeClock()
    clock.now = 3.0
    popen_calls: list[tuple[object, object]] = []
    communicate_timeouts: list[float] = []
    pipe_payloads: list[object] = []

    class SyntheticProbe:
        pid = 910_000
        returncode = 0

        def __init__(self, argv_read_fd: int) -> None:
            self.argv_read_fd = argv_read_fd

        def communicate(self, timeout: float) -> tuple[str, str]:
            communicate_timeouts.append(timeout)
            with os.fdopen(self.argv_read_fd, "rb", closefd=True) as stream:
                pipe_payloads.append(json.loads(stream.read().decode("utf-8")))
            return "0\n", ""

    def popen(command: object, **kwargs: object) -> SyntheticProbe:
        popen_calls.append((command, kwargs))
        clock.now += 0.5
        pass_fds = kwargs["pass_fds"]
        assert isinstance(pass_fds, tuple) and len(pass_fds) == 1
        return SyntheticProbe(os.dup(pass_fds[0]))

    monkeypatch.setattr(proof_guard.subprocess, "Popen", popen)
    monkeypatch.setattr(proof_guard, "group_exists", lambda _pgid: False)

    thermal_state = proof_guard.read_bounded_macos_thermal_state(
        deadline=5.0,
        clock=clock.monotonic,
    )

    assert thermal_state == 0
    assert communicate_timeouts == [1.5]
    assert pipe_payloads == [
        [sys.executable, str(RUNNER), "--internal-thermal-probe"]
    ]
    assert len(popen_calls) == 1
    wrapper_argv, wrapper_kwargs = popen_calls[0]
    assert isinstance(wrapper_argv, list)
    assert wrapper_argv[:3] == [
        sys.executable,
        str(RUNNER),
        "--internal-exec-trampoline",
    ]
    assert len(wrapper_argv) == 4
    read_fd = int(wrapper_argv[3])
    assert wrapper_kwargs == {
        "cwd": PROJECT_ROOT,
        "env": proof_guard.limited_environment(),
        "shell": False,
        "start_new_session": True,
        "pass_fds": (read_fd,),
        "stdout": subprocess.PIPE,
        "stderr": subprocess.DEVNULL,
        "text": True,
    }


def test_thermal_probe_rejects_success_exactly_at_deadline(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = _FakeClock()
    standard_output = io.StringIO()
    standard_error = _FlushRecordingStream()
    communicate_timeouts: list[float] = []

    class SyntheticProbe:
        pid = 910_001
        returncode = 0

        def communicate(self, timeout: float) -> tuple[str, str]:
            communicate_timeouts.append(timeout)
            clock.now += timeout
            return "0\n", ""

        def poll(self) -> int:
            return 0

    monkeypatch.setattr(
        proof_guard.subprocess,
        "Popen",
        lambda *_args, **_kwargs: SyntheticProbe(),
    )
    monkeypatch.setattr(proof_guard, "group_exists", lambda _pgid: False)

    with redirect_stdout(standard_output), redirect_stderr(standard_error):
        with pytest.raises(RuntimeError, match="thermal probe deadline exceeded"):
            proof_guard.read_bounded_macos_thermal_state(
                deadline=0.5,
                clock=clock.monotonic,
            )

    assert communicate_timeouts == [0.5]
    assert clock.now == 0.5
    assert standard_output.getvalue() == ""
    assert standard_error.getvalue() == (
        "proof guard safety transition: thermal probe deadline reached\n"
    )
    assert standard_error.flush_count == 1


def test_thermal_probe_timeout_terminates_then_kills_exact_helper_group(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = _FakeClock()
    process_group_id = 910_002
    command_sentinel = "thermal-probe-command-secret"
    group_alive = True
    killpg_calls: list[tuple[int, int]] = []
    transition_before_cleanup: list[tuple[str, int]] = []
    standard_output = io.StringIO()
    standard_error = _FlushRecordingStream()

    class SyntheticProbe:
        pid = process_group_id
        returncode: int | None = None

        def communicate(self, timeout: float) -> tuple[str, str]:
            clock.now += timeout
            raise subprocess.TimeoutExpired(
                f"{command_sentinel}-{process_group_id}",
                timeout,
            )

        def poll(self) -> None:
            return None

        def wait(self, timeout: float | None = None) -> int:
            self.returncode = -signal.SIGKILL
            return self.returncode

    def killpg(target_group_id: int, signum: int) -> None:
        nonlocal group_alive
        killpg_calls.append((target_group_id, signum))
        transition_before_cleanup.append(
            (standard_error.getvalue(), standard_error.flush_count)
        )
        if signum == signal.SIGKILL:
            group_alive = False

    monkeypatch.setattr(
        proof_guard.subprocess,
        "Popen",
        lambda *_args, **_kwargs: SyntheticProbe(),
    )
    monkeypatch.setattr(proof_guard.os, "killpg", killpg)
    monkeypatch.setattr(proof_guard, "group_exists", lambda _pgid: group_alive)
    monkeypatch.setattr(proof_guard.time, "monotonic", clock.monotonic)
    monkeypatch.setattr(
        proof_guard.time,
        "sleep",
        lambda seconds: setattr(clock, "now", clock.now + seconds),
    )

    with redirect_stdout(standard_output), redirect_stderr(standard_error):
        with pytest.raises(RuntimeError, match="thermal probe timed out") as exc_info:
            proof_guard.read_bounded_macos_thermal_state(
                deadline=0.5,
                clock=clock.monotonic,
            )

    transition = "proof guard safety transition: thermal probe deadline reached\n"
    assert killpg_calls == [
        (process_group_id, signal.SIGTERM),
        (process_group_id, signal.SIGKILL),
    ]
    assert transition_before_cleanup == [(transition, 1), (transition, 1)]
    assert clock.now >= 0.5
    assert group_alive is False
    assert standard_output.getvalue() == ""
    assert standard_error.getvalue() == transition
    assert str(process_group_id) not in standard_output.getvalue()
    assert str(process_group_id) not in standard_error.getvalue()
    exception_chain = _exception_chain(exc_info.value)
    exception_chain_text = " ".join(
        f"{current!r} {current.args!r} {vars(current)!r}"
        for current in exception_chain
    )
    assert exception_chain == (exc_info.value,)
    assert exc_info.value.__context__ is None
    assert exc_info.value.__cause__ is None
    assert str(process_group_id) not in exception_chain_text
    assert command_sentinel not in exception_chain_text


@pytest.mark.parametrize(
    ("failure_point", "survives_sigterm", "expected_signals"),
    (
        ("write", False, (signal.SIGTERM,)),
        ("flush", True, (signal.SIGTERM, signal.SIGKILL)),
    ),
)
def test_thermal_probe_transition_io_failure_still_cleans_exact_helper_group(
    monkeypatch: pytest.MonkeyPatch,
    failure_point: str,
    survives_sigterm: bool,
    expected_signals: tuple[int, ...],
) -> None:
    clock = _FakeClock()
    process_group_id = 987_654_320
    command_sentinel = "thermal-probe-timeout-command-secret"
    io_sentinel = "thermal-probe-transition-io-secret"
    events: list[str] = []
    group_checks: list[bool] = []
    group_alive = True
    standard_output = io.StringIO()

    class FailingTransitionStream:
        def __init__(self) -> None:
            self.parts: list[str] = []
            self.transition_attempted = False

        def write(self, value: str) -> int:
            if not self.transition_attempted:
                self.transition_attempted = True
                events.append("transition-attempt")
            if failure_point == "write":
                raise OSError(f"{io_sentinel}-{process_group_id}")
            self.parts.append(value)
            return len(value)

        def flush(self) -> None:
            events.append("transition-flush")
            if failure_point == "flush":
                raise OSError(f"{io_sentinel}-{process_group_id}")

        def getvalue(self) -> str:
            return "".join(self.parts)

    standard_error = FailingTransitionStream()

    class SyntheticProbe:
        pid = process_group_id
        returncode: int | None = None

        def communicate(self, timeout: float) -> tuple[str, str]:
            clock.now += timeout
            raise subprocess.TimeoutExpired(
                f"{command_sentinel}-{process_group_id}",
                timeout,
            )

        def poll(self) -> None:
            return None

        def wait(self, timeout: float | None = None) -> int:
            self.returncode = -signal.SIGKILL
            return self.returncode

    def group_exists(_process_group_id: int) -> bool:
        group_checks.append(group_alive)
        return group_alive

    def killpg(target_group_id: int, signum: int) -> None:
        nonlocal group_alive
        assert target_group_id == process_group_id
        events.append(signal.Signals(signum).name)
        if signum == signal.SIGTERM and not survives_sigterm:
            group_alive = False
        if signum == signal.SIGKILL:
            group_alive = False

    monkeypatch.setattr(
        proof_guard.subprocess,
        "Popen",
        lambda *_args, **_kwargs: SyntheticProbe(),
    )
    monkeypatch.setattr(proof_guard.os, "killpg", killpg)
    monkeypatch.setattr(proof_guard, "group_exists", group_exists)
    monkeypatch.setattr(proof_guard.time, "monotonic", clock.monotonic)
    monkeypatch.setattr(
        proof_guard.time,
        "sleep",
        lambda seconds: setattr(clock, "now", clock.now + seconds),
    )

    with redirect_stdout(standard_output), redirect_stderr(standard_error):
        with pytest.raises(
            RuntimeError,
            match="^thermal probe safety transition failed$",
        ) as exc_info:
            proof_guard.read_bounded_macos_thermal_state(
                deadline=0.5,
                clock=clock.monotonic,
            )

    signal_events = [
        signal.Signals(signum).name
        for signum in expected_signals
    ]
    assert events[0] == "transition-attempt"
    assert events.index("SIGTERM") > events.index("transition-attempt")
    if failure_point == "flush":
        assert events.index("SIGTERM") > events.index("transition-flush")
    assert [event for event in events if event.startswith("SIG")] == signal_events
    assert group_alive is False
    assert group_checks[-1] is False
    assert standard_output.getvalue() == ""
    stream_text = standard_output.getvalue() + standard_error.getvalue()
    exception_chain = _exception_chain(exc_info.value)
    exception_chain_text = " ".join(
        f"{current!r} {current.args!r} {vars(current)!r}"
        for current in exception_chain
    )
    assert exception_chain == (exc_info.value,)
    assert exc_info.value.__context__ is None
    assert exc_info.value.__cause__ is None
    for sentinel in (str(process_group_id), command_sentinel, io_sentinel):
        assert sentinel not in stream_text
        assert sentinel not in exception_chain_text


def test_thermal_probe_cleanup_failure_is_silent_and_pid_free(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = _FakeClock()
    process_group_id = 987_654_321
    killpg_calls: list[tuple[int, int]] = []
    transition_before_cleanup: list[tuple[str, int]] = []
    standard_output = io.StringIO()
    standard_error = _FlushRecordingStream()

    class SyntheticProbe:
        pid = process_group_id
        returncode: int | None = None

        def communicate(self, timeout: float) -> tuple[str, str]:
            clock.now += timeout
            raise subprocess.TimeoutExpired(
                f"thermal-probe-{process_group_id}",
                timeout,
            )

        def poll(self) -> None:
            return None

        def wait(self, timeout: float | None = None) -> int:
            raise subprocess.TimeoutExpired(
                f"thermal-cleanup-{process_group_id}",
                timeout,
            )

    def killpg(target_group_id: int, signum: int) -> None:
        killpg_calls.append((target_group_id, signum))
        transition_before_cleanup.append(
            (standard_error.getvalue(), standard_error.flush_count)
        )

    monkeypatch.setattr(
        proof_guard.subprocess,
        "Popen",
        lambda *_args, **_kwargs: SyntheticProbe(),
    )
    monkeypatch.setattr(proof_guard.os, "killpg", killpg)
    monkeypatch.setattr(proof_guard, "group_exists", lambda _pgid: True)
    monkeypatch.setattr(proof_guard.time, "monotonic", clock.monotonic)
    monkeypatch.setattr(
        proof_guard.time,
        "sleep",
        lambda seconds: setattr(clock, "now", clock.now + seconds),
    )

    with redirect_stdout(standard_output), redirect_stderr(standard_error):
        with pytest.raises(RuntimeError, match="thermal probe cleanup failed") as exc_info:
            proof_guard.read_bounded_macos_thermal_state(
                deadline=0.5,
                clock=clock.monotonic,
            )

    transition = "proof guard safety transition: thermal probe deadline reached\n"
    assert killpg_calls == [
        (process_group_id, signal.SIGTERM),
        (process_group_id, signal.SIGKILL),
    ]
    assert transition_before_cleanup == [(transition, 1), (transition, 1)]
    assert standard_output.getvalue() == ""
    assert standard_error.getvalue() == transition
    assert str(process_group_id) not in standard_output.getvalue()
    assert str(process_group_id) not in standard_error.getvalue()
    assert str(process_group_id) not in str(exc_info.value)


@pytest.mark.parametrize("interruption_site", ("communicate", "group_probe"))
@pytest.mark.parametrize("interruption_kind", ("guard_signal", "keyboard"))
def test_helper_cleanup_success_preserves_original_interruption(
    monkeypatch: pytest.MonkeyPatch,
    interruption_site: str,
    interruption_kind: str,
) -> None:
    clock = _FakeClock()
    process_group_id = 988_000_001
    group_alive = True
    group_probe_calls = 0
    killpg_calls: list[tuple[int, int]] = []
    interruption: BaseException = (
        proof_guard.GuardSignal(signal.SIGTERM)
        if interruption_kind == "guard_signal"
        else KeyboardInterrupt()
    )

    class SyntheticProbe:
        pid = process_group_id
        returncode = 0

        def communicate(self, timeout: float) -> tuple[str, str]:
            assert timeout > 0
            if interruption_site == "communicate":
                raise interruption
            return "0\n", ""

        def poll(self) -> None:
            return None

        def wait(self, timeout: float | None = None) -> int:
            return 0

    def group_exists(_process_group_id: int) -> bool:
        nonlocal group_probe_calls
        group_probe_calls += 1
        if interruption_site == "group_probe" and group_probe_calls == 1:
            raise interruption
        return group_alive

    def killpg(target_group_id: int, signum: int) -> None:
        nonlocal group_alive
        killpg_calls.append((target_group_id, signum))
        group_alive = False

    monkeypatch.setattr(
        proof_guard.subprocess,
        "Popen",
        lambda *_args, **_kwargs: SyntheticProbe(),
    )
    monkeypatch.setattr(proof_guard, "group_exists", group_exists)
    monkeypatch.setattr(proof_guard.os, "killpg", killpg)
    monkeypatch.setattr(proof_guard.time, "monotonic", clock.monotonic)
    monkeypatch.setattr(
        proof_guard.time,
        "sleep",
        lambda seconds: setattr(clock, "now", clock.now + seconds),
    )

    with pytest.raises(type(interruption)) as exc_info:
        proof_guard.read_bounded_macos_thermal_state(
            deadline=1.0,
            clock=clock.monotonic,
        )

    assert exc_info.value is interruption
    assert killpg_calls == [(process_group_id, signal.SIGTERM)]
    assert group_alive is False


def test_helper_cleanup_defers_second_signal_until_final_absence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = _FakeClock()
    process_group_id = 988_000_003
    group_alive = True
    events: list[str] = []
    original_interruption = proof_guard.GuardSignal(signal.SIGHUP)

    class SyntheticProbe:
        pid = process_group_id
        returncode: int | None = None

        def communicate(self, timeout: float) -> tuple[str, str]:
            assert timeout > 0
            raise original_interruption

        def poll(self) -> None:
            return None

        def wait(self, timeout: float | None = None) -> int:
            return 0

    def group_exists(_process_group_id: int) -> bool:
        events.append("final-absence" if not group_alive else "group-alive")
        return group_alive

    def killpg(target_group_id: int, signum: int) -> None:
        nonlocal group_alive
        assert target_group_id == process_group_id
        assert signum == signal.SIGTERM
        events.append("term")
        os.kill(os.getpid(), signal.SIGINT)
        events.append("second-signal-pending")
        group_alive = False

    def second_signal_handler(_signum: int, _frame: object) -> None:
        events.append("second-signal-delivered")
        raise KeyboardInterrupt

    monkeypatch.setattr(
        proof_guard.subprocess,
        "Popen",
        lambda *_args, **_kwargs: SyntheticProbe(),
    )
    monkeypatch.setattr(proof_guard, "group_exists", group_exists)
    monkeypatch.setattr(proof_guard.os, "killpg", killpg)
    monkeypatch.setattr(proof_guard.time, "monotonic", clock.monotonic)
    monkeypatch.setattr(
        proof_guard.time,
        "sleep",
        lambda seconds: setattr(clock, "now", clock.now + seconds),
    )
    previous_handler = signal.signal(signal.SIGINT, second_signal_handler)
    try:
        with pytest.raises(proof_guard.GuardSignal) as exc_info:
            proof_guard.read_bounded_macos_thermal_state(
                deadline=1.0,
                clock=clock.monotonic,
            )
    finally:
        signal.signal(signal.SIGINT, previous_handler)

    assert exc_info.value is original_interruption
    assert events == [
        "term",
        "second-signal-pending",
        "final-absence",
        "second-signal-delivered",
    ]


@pytest.mark.parametrize("interruption_site", ("communicate", "group_probe"))
def test_helper_cleanup_failure_supersedes_interruption_without_chain_or_pid(
    monkeypatch: pytest.MonkeyPatch,
    interruption_site: str,
) -> None:
    clock = _FakeClock()
    process_group_id = 988_000_002
    secret = "helper-cleanup-secret-sentinel"
    killpg_calls: list[tuple[int, int]] = []
    group_probe_calls = 0

    class SyntheticProbe:
        pid = process_group_id
        returncode: int | None = None

        def communicate(self, timeout: float) -> tuple[str, str]:
            assert timeout > 0
            if interruption_site == "communicate":
                raise proof_guard.GuardSignal(signal.SIGTERM)
            return "0\n", ""

        def poll(self) -> None:
            return None

        def wait(self, timeout: float | None = None) -> int:
            raise subprocess.TimeoutExpired(
                f"{secret}-{process_group_id}",
                timeout,
            )

    monkeypatch.setattr(
        proof_guard.subprocess,
        "Popen",
        lambda *_args, **_kwargs: SyntheticProbe(),
    )
    def group_exists(_process_group_id: int) -> bool:
        nonlocal group_probe_calls
        group_probe_calls += 1
        if interruption_site == "group_probe" and group_probe_calls == 1:
            raise proof_guard.GuardSignal(signal.SIGTERM)
        return True

    monkeypatch.setattr(proof_guard, "group_exists", group_exists)
    monkeypatch.setattr(
        proof_guard.os,
        "killpg",
        lambda pgid, signum: killpg_calls.append((pgid, signum)),
    )
    monkeypatch.setattr(proof_guard.time, "monotonic", clock.monotonic)
    monkeypatch.setattr(
        proof_guard.time,
        "sleep",
        lambda seconds: setattr(clock, "now", clock.now + seconds),
    )

    with pytest.raises(
        RuntimeError,
        match="^proof guard safety cleanup failed$",
    ) as exc_info:
        proof_guard.read_bounded_macos_thermal_state(
            deadline=1.0,
            clock=clock.monotonic,
        )

    exception_chain = _exception_chain(exc_info.value)
    exception_chain_text = " ".join(
        f"{current!r} {current.args!r} {vars(current)!r}"
        for current in exception_chain
    )
    assert exception_chain == (exc_info.value,)
    assert killpg_calls == [
        (process_group_id, signal.SIGTERM),
        (process_group_id, signal.SIGKILL),
    ]
    assert str(process_group_id) not in exception_chain_text
    assert secret not in exception_chain_text


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

    processes = proof_guard._read_process_table(0.75)

    assert processes == (_process_info(200, 100, 200, 12.5),)
    assert calls == [
        (
            ["ps", "-axo", "pid=,ppid=,pgid=,%cpu=,state=,ucomm="],
            {
                "check": True,
                "capture_output": True,
                "text": True,
                "timeout": 0.75,
            },
        )
    ]


class _FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def monotonic(self) -> float:
        return self.now


class _SequenceMonitor:
    def __init__(
        self,
        samples: list[object],
        clock: _FakeClock,
        *,
        sample_advances: list[float] | None = None,
        output_stream: io.StringIO | None = None,
        honor_sample_timeout: bool = False,
    ) -> None:
        self.samples = samples
        self.clock = clock
        self.sample_advances = sample_advances
        self.output_stream = output_stream
        self.honor_sample_timeout = honor_sample_timeout
        self.calls: list[tuple[int, int, int, int]] = []
        self.sample_times: list[float] = []
        self.sample_deadlines: list[float] = []
        self.sample_budgets: list[float] = []
        self.output_before_samples: list[list[str]] = []

    def sample(
        self,
        child_pid: int,
        process_group_id: int,
        launcher_pid: int,
        coordinator_pid: int,
        sample_deadline: float | None = None,
        allow_missing_leader: bool = False,
    ) -> object:
        del allow_missing_leader
        if sample_deadline is None:
            sample_deadline = self.clock.monotonic() + 2.0
        sample_budget = sample_deadline - self.clock.monotonic()
        self.calls.append(
            (child_pid, process_group_id, launcher_pid, coordinator_pid)
        )
        self.sample_times.append(self.clock.monotonic())
        self.sample_deadlines.append(sample_deadline)
        self.sample_budgets.append(sample_budget)
        if self.output_stream is not None:
            self.output_before_samples.append(
                self.output_stream.getvalue().splitlines()
            )
        if not self.samples:
            raise AssertionError("monitor sampled more often than expected")
        sample = self.samples.pop(0)
        if isinstance(sample, BaseException):
            raise sample
        if self.sample_advances is not None:
            if not self.sample_advances:
                raise AssertionError("monitor advanced more often than expected")
            sample_advance = self.sample_advances.pop(0)
            if (
                self.honor_sample_timeout
                and sample_advance > sample_budget
            ):
                self.clock.now += sample_budget
                raise subprocess.TimeoutExpired(
                    "synthetic process sample",
                    sample_budget,
                )
            self.clock.now += sample_advance
        return sample


def _safety_sample(
    *,
    cpu_percent: float = 0.0,
    group_process_count: int = 1,
    thermal_state: int | None = 0,
    coordinator_alive: bool = True,
    phase_leader_reparented: bool = False,
    escaped_pids: tuple[int, ...] = (),
    error: str | None = None,
) -> object:
    return proof_guard.SafetySample(
        thermal_state=thermal_state,
        launcher_alive=True,
        coordinator_alive=coordinator_alive,
        coordinator_reparented=False,
        phase_leader_missing=False,
        phase_leader_reparented=phase_leader_reparented,
        group_process_count=group_process_count,
        group_cpu_percent=cpu_percent,
        escaped_pids=escaped_pids,
        error=error,
    )


def _run_synthetic_monitored_phases(
    monkeypatch: pytest.MonkeyPatch,
    samples: list[object],
    completion_times: tuple[float, ...],
    *,
    command: tuple[str, ...] = ("synthetic-command",),
    progress_seconds: float = 10.0,
    sample_advances: list[float] | None = None,
    output_stream: io.StringIO | None = None,
    honor_sample_timeout: bool = False,
    preflight_seconds: float = 10.0,
    experiment_seconds: float = 10.0,
    events: list[tuple[str, int, float]] | None = None,
) -> tuple[int, list[tuple[int, int]], _SequenceMonitor]:
    clock = _FakeClock()
    alive: dict[int, bool] = {}
    children: list[object] = []

    class SyntheticChild:
        def __init__(self, pid: int, complete_after: float) -> None:
            self.pid = pid
            self.complete_after = complete_after
            self.deadline: float | None = None

        def start(self) -> None:
            self.deadline = clock.now + self.complete_after
            alive[self.pid] = True

        def poll(self) -> int | None:
            assert self.deadline is not None
            if events is not None:
                events.append(("poll", self.pid, clock.now))
            if clock.now >= self.deadline:
                alive[self.pid] = False
                return 0
            return None

        def wait(self, timeout: float | None = None) -> int:
            assert self.deadline is not None
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
    children_by_pid = {child.pid: child for child in children}
    killpg_calls: list[tuple[int, int]] = []

    def popen(*_args: object, **_kwargs: object) -> object:
        child = children.pop(0)
        child.start()
        return child

    def killpg(process_group_id: int, signum: int) -> None:
        killpg_calls.append((process_group_id, signum))
        if events is not None:
            events.append(("killpg", process_group_id, clock.now))
        if not process_group_alive(process_group_id):
            raise ProcessLookupError
        if signum in (signal.SIGTERM, signal.SIGKILL):
            alive[process_group_id] = False

    def process_group_alive(process_group_id: int) -> bool:
        child = children_by_pid.get(process_group_id)
        if child is None or not alive.get(process_group_id, False):
            return False
        assert child.deadline is not None
        if clock.now >= child.deadline:
            alive[process_group_id] = False
            return False
        return True

    monitor = _SequenceMonitor(
        samples,
        clock,
        sample_advances=sample_advances,
        output_stream=output_stream,
        honor_sample_timeout=honor_sample_timeout,
    )
    monkeypatch.setattr(proof_guard.subprocess, "Popen", popen)
    monkeypatch.setattr(
        proof_guard,
        "group_exists",
        process_group_alive,
    )
    monkeypatch.setattr(proof_guard.os, "killpg", killpg)

    status = run_long_guarded(
        command,
        preflight_seconds=preflight_seconds,
        experiment_seconds=experiment_seconds,
        progress_seconds=progress_seconds,
        grace_seconds=0.1,
        monitor=monitor,
        clock=clock.monotonic,
    )
    return status, killpg_calls, monitor


def test_progress_reports_sanitized_phase_starts_and_two_experiment_boundaries(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    command_sentinel = "proof-command-secret-sentinel"
    environment_sentinel = "proof-environment-secret-sentinel"
    monkeypatch.setenv("PROOF_GUARD_TEST_SECRET", environment_sentinel)

    status, killpg_calls, monitor = _run_synthetic_monitored_phases(
        monkeypatch,
        [
            _safety_sample(cpu_percent=10.0, group_process_count=1),
            _safety_sample(cpu_percent=20.0, group_process_count=2),
            _safety_sample(cpu_percent=30.0, group_process_count=3),
            _safety_sample(cpu_percent=40.0, group_process_count=4),
        ],
        completion_times=(0.5, 2.5),
        command=("synthetic-command", command_sentinel),
        progress_seconds=1.0,
    )

    captured = capsys.readouterr()
    assert status == 0
    assert killpg_calls == []
    assert monitor.sample_times == [0.0, 0.5, 1.5, 2.5]
    assert captured.out.splitlines() == [
        "proof guard progress phase=preflight elapsed=0s "
        "exact_group_process_count=1 aggregate_cpu=10% thermal=nominal",
        "proof guard progress phase=experiment elapsed=0s "
        "exact_group_process_count=2 aggregate_cpu=20% thermal=nominal",
        "proof guard progress phase=experiment elapsed=1s "
        "exact_group_process_count=2 aggregate_cpu=20% thermal=nominal",
        "proof guard progress phase=experiment elapsed=2s "
        "exact_group_process_count=3 aggregate_cpu=30% thermal=nominal",
    ]
    assert command_sentinel not in captured.out
    assert command_sentinel not in captured.err
    assert environment_sentinel not in captured.out
    assert environment_sentinel not in captured.err


def test_immediate_success_still_reports_both_phase_starts(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    status, killpg_calls, monitor = _run_synthetic_monitored_phases(
        monkeypatch,
        [
            _safety_sample(cpu_percent=10.0, group_process_count=1),
            _safety_sample(cpu_percent=20.0, group_process_count=2),
        ],
        completion_times=(0.0, 0.0),
    )

    assert status == 0
    assert killpg_calls == []
    assert monitor.sample_times == [0.0, 0.0]
    assert capsys.readouterr().out.splitlines() == [
        "proof guard progress phase=preflight elapsed=0s "
        "exact_group_process_count=1 aggregate_cpu=10% thermal=nominal",
        "proof guard progress phase=experiment elapsed=0s "
        "exact_group_process_count=2 aggregate_cpu=20% thermal=nominal",
    ]


def test_slow_sample_honors_progress_budget_and_aborts_without_late_write(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    command_sentinel = "blocking-sample-command-secret"
    environment_sentinel = "blocking-sample-environment-secret"
    monkeypatch.setenv("PROOF_GUARD_BLOCKING_SAMPLE_SECRET", environment_sentinel)
    output = io.StringIO()

    with redirect_stdout(output):
        status, killpg_calls, monitor = _run_synthetic_monitored_phases(
            monkeypatch,
            [
                _safety_sample(cpu_percent=10.0, group_process_count=1),
                _safety_sample(cpu_percent=20.0, group_process_count=2),
                _safety_sample(cpu_percent=30.0, group_process_count=3),
            ],
            completion_times=(0.0, 3.5),
            command=("synthetic-command", command_sentinel),
            progress_seconds=1.0,
            sample_advances=[0.0, 0.0, 2.2],
            output_stream=output,
            honor_sample_timeout=True,
        )

    captured = capsys.readouterr()
    lines = output.getvalue().splitlines()
    assert status == 126
    assert killpg_calls == [(700_001, signal.SIGTERM)]
    assert monitor.sample_times == [0.0, 0.0, 1.0]
    assert monitor.sample_budgets == [2.0, 1.0, 1.0]
    assert monitor.clock.now == 2.0
    expected_lines = [
        "proof guard progress phase=preflight elapsed=0s "
        "exact_group_process_count=1 aggregate_cpu=10% thermal=nominal",
        "proof guard progress phase=experiment elapsed=0s "
        "exact_group_process_count=2 aggregate_cpu=20% thermal=nominal",
        "proof guard progress phase=experiment elapsed=1s "
        "exact_group_process_count=2 aggregate_cpu=20% thermal=nominal",
    ]
    assert monitor.output_before_samples[2] == expected_lines
    assert lines == expected_lines
    assert command_sentinel not in output.getvalue()
    assert command_sentinel not in captured.err
    assert environment_sentinel not in output.getvalue()
    assert environment_sentinel not in captured.err


@pytest.mark.parametrize("phase", ("preflight", "experiment"))
@pytest.mark.parametrize("child_state", ("completed", "running"))
def test_post_sample_timeout_precedes_progress_and_child_state(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    phase: str,
    child_state: str,
) -> None:
    child_duration = 0.5 if child_state == "completed" else 2.0
    events: list[tuple[str, int, float]] = []
    if phase == "preflight":
        samples = [_safety_sample(), _safety_sample()]
        sample_advances = [1.1, 0.0]
        completion_times = (child_duration, 0.0)
        target_pid = 700_000
        expected_status = 125
        expected_lines: list[str] = []
    else:
        samples = [_safety_sample(), _safety_sample()]
        sample_advances = [0.0, 1.1]
        completion_times = (0.0, child_duration)
        target_pid = 700_001
        expected_status = 124
        expected_lines = [
            "proof guard progress phase=preflight elapsed=0s "
            "exact_group_process_count=1 aggregate_cpu=0% thermal=nominal"
        ]

    status, killpg_calls, _monitor = _run_synthetic_monitored_phases(
        monkeypatch,
        samples,
        completion_times=completion_times,
        progress_seconds=1.0,
        sample_advances=sample_advances,
        preflight_seconds=1.0,
        experiment_seconds=1.0,
        events=events,
    )

    assert status == expected_status
    assert killpg_calls == [(target_pid, signal.SIGTERM)]
    target_events = [event for event in events if event[1] == target_pid]
    assert target_events[:2] == [
        ("poll", target_pid, 0.0),
        ("killpg", target_pid, 1.1),
    ]
    assert capsys.readouterr().out.splitlines() == expected_lines


def test_progress_flushes_each_line() -> None:
    class FlushRecordingStream(io.StringIO):
        def __init__(self) -> None:
            super().__init__()
            self.flush_count = 0

        def flush(self) -> None:
            self.flush_count += 1
            super().flush()

    stream = FlushRecordingStream()
    with redirect_stdout(stream):
        proof_guard._print_progress(
            "experiment",
            1.0,
            _safety_sample(cpu_percent=25.0, group_process_count=2),
        )

    assert stream.flush_count == 1


def test_progress_catch_up_has_a_finite_per_loop_line_bound() -> None:
    output = io.StringIO()
    with redirect_stdout(output):
        next_progress_index = proof_guard._print_due_progress(
            "experiment",
            0.0,
            10_000.0,
            1,
            1.0,
            _safety_sample(),
        )

    assert len(output.getvalue().splitlines()) == 600
    assert next_progress_index == 601


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


def test_safety_samples_immediately_each_phase_then_once_per_second(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    status, killpg_calls, monitor = _run_synthetic_monitored_phases(
        monkeypatch,
        [_safety_sample() for _ in range(5)],
        completion_times=(2.5, 1.5),
    )

    assert status == 0
    assert killpg_calls == []
    assert monitor.sample_times == [0.0, 1.0, 2.0, 2.5, 3.5]
    assert [
        child_pid
        for child_pid, _pgid, _launcher, _coordinator in monitor.calls
    ] == [
        700_000,
        700_000,
        700_000,
        700_001,
        700_001,
    ]


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
        "controller": lambda: _safety_sample(coordinator_alive=False),
        "reparented": lambda: _safety_sample(phase_leader_reparented=True),
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
