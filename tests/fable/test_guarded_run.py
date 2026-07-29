"""Tests for the fable line's guarded foreground experiment runner.

Every session process-safety rule that can be tested in seconds is tested here. The
tests use tiny timeouts and isolated lock/ledger/log paths under tmp_path, so they never
touch the real guard state and never leave a process behind.
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

from experiments.stable_ac.fable import guarded_run as G

REPO_ROOT = Path(G.__file__).resolve().parents[3]


@pytest.fixture()
def paths(tmp_path):
    """Isolated lock / ledger / log / code-dir so tests never touch real guard state."""
    code_dir = tmp_path / "code"
    code_dir.mkdir()
    (code_dir / "mod.py").write_text("x = 1\n")
    return {
        "lock_path": tmp_path / ".guard.lock",
        "ledger_path": tmp_path / "ledger.jsonl",
        "log_dir": tmp_path / "logs",
        "code_dir": code_dir,
    }


def _run(argv, paths, **kw):
    kw.setdefault("enforce_preflight", False)
    kw.setdefault("heartbeat_s", 1.0)
    return G.run_guarded(argv, log_dir=paths["log_dir"], lock_path=paths["lock_path"],
                         ledger_path=paths["ledger_path"], code_dir=paths["code_dir"],
                         **kw)


def _py(code: str) -> list[str]:
    return [sys.executable, "-c", code]


# ---------------------------------------------------------------------------------
# Hard ceilings
# ---------------------------------------------------------------------------------

def test_runtime_ceiling_is_ten_minutes():
    assert G.HARD_MAX_RUNTIME_S == 600
    assert G.HARD_MAX_PREFLIGHT_S == 60
    assert G.MAX_HEARTBEAT_S == 60


def test_refuses_timeout_above_hard_ceiling(paths):
    with pytest.raises(SystemExit, match="exceeds the hard"):
        _run(_py("pass"), paths, timeout_s=G.HARD_MAX_RUNTIME_S + 1)


def test_refuses_preflight_above_preflight_ceiling(paths):
    with pytest.raises(SystemExit, match="preflight ceiling"):
        _run(_py("pass"), paths, timeout_s=G.HARD_MAX_PREFLIGHT_S + 1, preflight=True)


def test_refuses_heartbeat_slower_than_sixty_seconds(paths):
    with pytest.raises(SystemExit, match="progress-reporting"):
        _run(_py("pass"), paths, timeout_s=5, heartbeat_s=61)


# ---------------------------------------------------------------------------------
# Happy path, single-thread env, logging
# ---------------------------------------------------------------------------------

def test_successful_run_is_ok_and_logged(paths):
    rec = _run(_py("print('hello')"), paths, timeout_s=30)
    assert rec["verdict"] == "ok"
    assert rec["returncode"] == 0
    assert rec["cleanup_verified"]["children_exited"] is True
    assert rec["cleanup_verified"]["lock_removed"] is True
    log = REPO_ROOT / rec["log"]
    assert "hello" in log.read_text()


def test_nonzero_exit_is_reported_not_masked(paths):
    rec = _run(_py("import sys; sys.exit(3)"), paths, timeout_s=30)
    assert rec["verdict"] == "nonzero_exit"
    assert rec["returncode"] == 3


def test_child_gets_single_thread_environment(paths):
    code = (
        "import os,json;"
        "print(json.dumps({k: os.environ.get(k) for k in "
        "('OMP_NUM_THREADS','NUMBA_NUM_THREADS','MKL_NUM_THREADS',"
        "'OPENBLAS_NUM_THREADS')}))"
    )
    rec = _run(_py(code), paths, timeout_s=30)
    payload = json.loads((REPO_ROOT / rec["log"]).read_text().strip().splitlines()[-1])
    assert payload == {
        "OMP_NUM_THREADS": "1", "NUMBA_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
    }


def test_verdict_note_refuses_mathematical_interpretation(paths):
    rec = _run(_py("pass"), paths, timeout_s=30)
    assert "not evidence for or against AC" in rec["note"]


# ---------------------------------------------------------------------------------
# Timeout, SIGTERM-first, SIGKILL escalation
# ---------------------------------------------------------------------------------

def test_timeout_terminates_child_with_sigterm_first(paths):
    rec = _run(_py("import time; time.sleep(120)"), paths, timeout_s=2)
    assert rec["verdict"] == "timeout"
    assert rec["termination"]["sigterm_sent"] is True
    assert rec["termination"].get("sigkill_sent") is False
    assert rec["cleanup_verified"]["children_exited"] is True
    assert rec["cleanup_verified"]["lock_removed"] is True


def test_sigkill_escalation_only_when_sigterm_ignored(paths):
    code = (
        "import signal,time;"
        "signal.signal(signal.SIGTERM, signal.SIG_IGN);"
        "print('ignoring', flush=True);"
        "time.sleep(120)"
    )
    rec = _run(_py(code), paths, timeout_s=2)
    assert rec["verdict"] == "timeout"
    assert rec["termination"]["sigterm_sent"] is True
    assert rec["termination"]["sigkill_sent"] is True
    assert rec["cleanup_verified"]["children_exited"] is True
    assert rec["cleanup_verified"]["surviving_pids"] == []


def test_child_runs_in_its_own_process_group(paths):
    rec = _run(_py("import os; print(os.getpgrp())"), paths, timeout_s=30)
    child_pgid = int((REPO_ROOT / rec["log"]).read_text().strip().splitlines()[-1])
    assert child_pgid == rec["child_pgid"]
    assert child_pgid != os.getpgrp(), "child must not share the guard's process group"


# ---------------------------------------------------------------------------------
# The rule that protects the controlling shell and infrastructure
# ---------------------------------------------------------------------------------

def test_refuses_to_signal_the_guards_own_process_group():
    with pytest.raises(RuntimeError, match="REFUSING to signal"):
        G.terminate_group(os.getpgrp())


@pytest.mark.parametrize("pgid", [0, 1, -1])
def test_refuses_to_signal_init_adjacent_groups(pgid):
    with pytest.raises(RuntimeError, match="REFUSING to signal"):
        G.terminate_group(pgid)


# ---------------------------------------------------------------------------------
# Exactly one experiment at a time
# ---------------------------------------------------------------------------------

def test_lock_refuses_a_second_concurrent_experiment(paths):
    lock = G.GuardLock(paths["lock_path"])
    lock.acquire()
    try:
        with pytest.raises(SystemExit, match="one experiment at a time"):
            _run(_py("pass"), paths, timeout_s=5)
    finally:
        lock.release()


def test_stale_lock_from_dead_guard_is_reclaimed(paths):
    paths["lock_path"].parent.mkdir(parents=True, exist_ok=True)
    # A pid that cannot be alive: allocate one and reap it.
    dead = subprocess.Popen([sys.executable, "-c", "pass"])
    dead.wait()
    paths["lock_path"].write_text(json.dumps({"pid": dead.pid, "started": time.time()}))
    rec = _run(_py("pass"), paths, timeout_s=30)
    assert rec["verdict"] == "ok"
    assert rec["cleanup_verified"]["lock_removed"] is True


def test_lock_released_even_when_child_times_out(paths):
    _run(_py("import time; time.sleep(60)"), paths, timeout_s=2)
    assert not paths["lock_path"].exists()


# ---------------------------------------------------------------------------------
# Never rerun an unchanged timed-out experiment
# ---------------------------------------------------------------------------------

def test_refuses_rerun_of_unchanged_timed_out_experiment(paths):
    argv = _py("import time; time.sleep(60)")
    first = _run(argv, paths, timeout_s=2)
    assert first["verdict"] == "timeout"
    with pytest.raises(SystemExit, match="already timed out"):
        _run(argv, paths, timeout_s=2)


def test_rerun_allowed_after_the_code_path_changes(paths):
    argv = _py("import time; time.sleep(60)")
    assert _run(argv, paths, timeout_s=2)["verdict"] == "timeout"
    (paths["code_dir"] / "mod.py").write_text("x = 2  # changed\n")
    rec = _run(argv, paths, timeout_s=2)  # refused only if fingerprint unchanged
    assert rec["verdict"] == "timeout"


def test_a_different_command_is_not_blocked_by_anothers_timeout(paths):
    assert _run(_py("import time; time.sleep(60)"), paths,
                timeout_s=2)["verdict"] == "timeout"
    assert _run(_py("print('unrelated')"), paths, timeout_s=30)["verdict"] == "ok"


def test_code_fingerprint_tracks_content_not_mtime(paths):
    before = G.code_fingerprint(paths["code_dir"])
    (paths["code_dir"] / "mod.py").write_text("x = 1\n")  # same content, new mtime
    assert G.code_fingerprint(paths["code_dir"]) == before
    (paths["code_dir"] / "mod.py").write_text("x = 99\n")
    assert G.code_fingerprint(paths["code_dir"]) != before


# ---------------------------------------------------------------------------------
# Preflight is mandatory before a long run
# ---------------------------------------------------------------------------------

def test_long_run_refused_without_a_successful_preflight(paths):
    with pytest.raises(SystemExit, match="no successful preflight"):
        G.run_guarded(_py("pass"), timeout_s=30, heartbeat_s=1.0,
                      enforce_preflight=True, log_dir=paths["log_dir"],
                      lock_path=paths["lock_path"], ledger_path=paths["ledger_path"],
                      code_dir=paths["code_dir"])


def test_successful_preflight_unlocks_the_long_run_for_same_module(paths):
    argv = [sys.executable, "-m", "json.tool", "--help"]
    pre = G.run_guarded(argv, timeout_s=30, heartbeat_s=1.0, preflight=True,
                        enforce_preflight=True, log_dir=paths["log_dir"],
                        lock_path=paths["lock_path"], ledger_path=paths["ledger_path"],
                        code_dir=paths["code_dir"])
    assert pre["verdict"] == "ok" and pre["kind"] == "preflight"
    rec = G.run_guarded(argv, timeout_s=30, heartbeat_s=1.0, enforce_preflight=True,
                        log_dir=paths["log_dir"], lock_path=paths["lock_path"],
                        ledger_path=paths["ledger_path"], code_dir=paths["code_dir"])
    assert rec["verdict"] == "ok" and rec["kind"] == "run"


def test_failed_preflight_does_not_unlock_the_long_run(paths):
    argv = _py("import sys; sys.exit(1)")
    G.run_guarded(argv, timeout_s=10, heartbeat_s=1.0, preflight=True,
                  enforce_preflight=True, log_dir=paths["log_dir"],
                  lock_path=paths["lock_path"], ledger_path=paths["ledger_path"],
                  code_dir=paths["code_dir"])
    with pytest.raises(SystemExit, match="no successful preflight"):
        G.run_guarded(argv, timeout_s=30, heartbeat_s=1.0, enforce_preflight=True,
                      log_dir=paths["log_dir"], lock_path=paths["lock_path"],
                      ledger_path=paths["ledger_path"], code_dir=paths["code_dir"])


def test_preflight_does_not_carry_across_a_code_change(paths):
    argv = [sys.executable, "-m", "json.tool", "--help"]
    G.run_guarded(argv, timeout_s=30, heartbeat_s=1.0, preflight=True,
                  enforce_preflight=True, log_dir=paths["log_dir"],
                  lock_path=paths["lock_path"], ledger_path=paths["ledger_path"],
                  code_dir=paths["code_dir"])
    (paths["code_dir"] / "mod.py").write_text("x = 'edited'\n")
    with pytest.raises(SystemExit, match="no successful preflight"):
        G.run_guarded(argv, timeout_s=30, heartbeat_s=1.0, enforce_preflight=True,
                      log_dir=paths["log_dir"], lock_path=paths["lock_path"],
                      ledger_path=paths["ledger_path"], code_dir=paths["code_dir"])


# ---------------------------------------------------------------------------------
# Early stop on unexpected children
# ---------------------------------------------------------------------------------

def test_stops_early_on_unexpected_child_processes(paths):
    code = (
        "import subprocess,sys,time;"
        "kids=[subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)'])"
        " for _ in range(6)];"
        "time.sleep(60)"
    )
    rec = G.run_guarded(_py(code), timeout_s=30, heartbeat_s=1.0, max_children=3,
                        enforce_preflight=False, log_dir=paths["log_dir"],
                        lock_path=paths["lock_path"], ledger_path=paths["ledger_path"],
                        code_dir=paths["code_dir"])
    assert rec["verdict"] == "stopped_early"
    assert "unexpected child processes" in rec["stop_reason"]
    assert rec["cleanup_verified"]["children_exited"] is True
    assert rec["cleanup_verified"]["surviving_pids"] == []


# ---------------------------------------------------------------------------------
# Ledger integrity
# ---------------------------------------------------------------------------------

def test_every_run_appends_exactly_one_ledger_row(paths):
    _run(_py("pass"), paths, timeout_s=10)
    _run(_py("print(1)"), paths, timeout_s=10)
    rows = G.read_ledger(paths["ledger_path"])
    assert len(rows) == 2
    assert all("verdict" in r and "code_fingerprint" in r for r in rows)


def test_ledger_survives_a_corrupt_line(paths):
    _run(_py("pass"), paths, timeout_s=10)
    with paths["ledger_path"].open("a") as fh:
        fh.write("{not json\n")
    assert len(G.read_ledger(paths["ledger_path"])) == 1


def test_target_module_extraction():
    assert G.target_module([sys.executable, "-m", "pkg.mod", "--flag"]) == "pkg.mod"
    assert G.target_module(["./script.sh", "-m"]) == "./script.sh"


def test_cli_rejects_empty_command():
    with pytest.raises(SystemExit):
        G.main(["--timeout", "5"])
