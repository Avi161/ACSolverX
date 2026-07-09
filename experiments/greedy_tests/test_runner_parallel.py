"""The HIGH_SPEEDUP multiprocessing path.

``N_WORKERS`` is forced to 2 in every test here. On a 16 GB machine
``_auto_workers`` returns 1 with the default ``GB_PER_PRES=9.0``, so
``high and n_workers > 1`` is false and the entire pool / queue / heartbeat-drain
path would never execute -- the tests would pass while covering nothing.

Both start methods are exercised. macOS defaults to ``spawn`` and Colab to
``fork``, and they differ in ways that matter: a spawned child re-imports the
module (so a monkeypatched ``greedy_search`` does not reach it, and the real
solver runs), while a forked child inherits the parent's memory.
"""

import json
import multiprocessing as mp
import os
import sys

import pytest

from experiments.run_baseline import DEFAULT_CONFIG, _resolve_paths, run_dataset
from experiments.search.greedy_baseline import moves_to_states, str_to_move
from experiments.greedy_tests.fixtures.presentations import MS640, load_flat_lines

pytestmark = [pytest.mark.slow, pytest.mark.mp]

#: ``fork`` is only exercised on Linux, which is what Colab runs. Forking a
#: multi-threaded process is unsafe on macOS (and warns from Python 3.12), so
#: testing it here would risk hanging the suite on the developer's machine
#: rather than proving anything about the deployment target.
_WANTED = ["spawn"] + (["fork"] if sys.platform.startswith("linux") else [])
START_METHODS = [m for m in _WANTED if m in mp.get_all_start_methods()]


@pytest.fixture
def tiny_dataset(tmp_path):
    lines = load_flat_lines(MS640)[:4]
    p = tmp_path / "tiny.txt"
    p.write_text("".join(repr(list(ln)) + "\n" for ln in lines))
    return str(p)


def _cfg(tmp_path, tiny_dataset, **over):
    return {**DEFAULT_CONFIG,
            "DATASET": tiny_dataset,
            "LOCAL_OUT_DIR": str(tmp_path / "out"),
            "USE_WANDB": False,
            "PROGRESS_EVERY": 100,
            **over}


def _rows(path):
    with open(path) as f:
        return [json.loads(ln) for ln in f if ln.strip()]


@pytest.mark.parametrize("start_method", START_METHODS)
def test_the_pool_path_produces_the_same_rows_as_the_serial_path(
        tmp_path, tiny_dataset, start_method):
    serial = run_dataset(_cfg(tmp_path / "a", tiny_dataset,
                              HIGH_SPEEDUP=False), 1000)
    parallel = run_dataset(_cfg(tmp_path / "b", tiny_dataset,
                                HIGH_SPEEDUP=True, N_WORKERS=2,
                                MP_START_METHOD=start_method), 1000)

    a = {r["pres_id"]: r for r in _rows(serial)}
    b = {r["pres_id"]: r for r in _rows(parallel)}
    assert set(a) == set(b) == {0, 1, 2, 3}
    for pid in a:
        for field in ("solved", "nodes_explored", "path_length",
                      "min_relator_length", "max_relator_length",
                      "max_relator_length_expanded"):
            assert a[pid][field] == b[pid][field], (pid, field)


@pytest.mark.parametrize("start_method", START_METHODS)
def test_solved_rows_from_the_pool_are_recovered_and_replay_to_trivial(
        tmp_path, tiny_dataset, start_method):
    out = run_dataset(_cfg(tmp_path, tiny_dataset, HIGH_SPEEDUP=True,
                           N_WORKERS=2, MP_START_METHOD=start_method), 1000)
    rows = _rows(out)
    assert rows and all(r["solved"] for r in rows)
    assert all(r["path_recovered"] is True for r in rows)

    paths = _rows(out[: -len(".jsonl")] + "_paths.jsonl")
    assert len(paths) == len(rows)
    for pr in paths:
        states = moves_to_states(pr["r1"], pr["r2"],
                                 [str_to_move(m) for m in pr["path_moves"]])
        assert [len(s) for s in states[-1]] == [1, 1]


def test_workers_never_open_the_output_files(tmp_path, tiny_dataset):
    """Parent-as-sole-writer: there is no lock, so this is the whole safety argument.

    Rows arrive out of order (``imap_unordered``) but each appears exactly once,
    and the file is never interleaved mid-line.
    """
    out = run_dataset(_cfg(tmp_path, tiny_dataset, HIGH_SPEEDUP=True,
                           N_WORKERS=2), 1000)
    with open(out) as f:
        raw = f.read()
    assert raw.endswith("\n")
    for ln in raw.splitlines():
        json.loads(ln)          # every line is a complete JSON object
    ids = [r["pres_id"] for r in _rows(out)]
    assert sorted(ids) == [0, 1, 2, 3] and len(ids) == len(set(ids))


def test_resume_works_across_a_pool_run(tmp_path, tiny_dataset):
    """A partially-done pool run resumes and completes only what is left.

    The dataset is deliberately *not* finished first: that is the case this test
    is about. The *fully*-resumed pool sweep (nothing left to do, which once
    raised ``IndexError`` on ``todo[0]``) is covered by ``test_crash_resume.py``.
    """
    cfg = _cfg(tmp_path, tiny_dataset, HIGH_SPEEDUP=True, N_WORKERS=2)
    partial = run_dataset({**cfg, "SUBSET": (0, 2)}, 1000)
    assert len(_rows(partial)) == 2

    # Same budget and cap, wider subset -> a different run identity, so seed the
    # full run's file with the two rows we already have.
    full, *_ = _resolve_paths(cfg, 1000, 4)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        for r in _rows(partial):
            f.write(json.dumps(r) + "\n")

    out = run_dataset(cfg, 1000)
    assert out == full
    rows = _rows(out)
    assert sorted(r["pres_id"] for r in rows) == [0, 1, 2, 3]
    assert len(rows) == 4, "resume must add exactly the two missing presentations"


def test_heartbeat_queue_survives_the_pool(tmp_path, tiny_dataset, capsys):
    """``HEARTBEAT_EVERY_S`` is result-neutral, but the queue must still be wired."""
    out = run_dataset(_cfg(tmp_path, tiny_dataset, HIGH_SPEEDUP=True,
                           N_WORKERS=2, HEARTBEAT_EVERY_S=1), 1000)
    printed = capsys.readouterr().out
    assert "[hb] armed: 2 worker(s)" in printed
    assert len(_rows(out)) == 4


def test_heartbeat_debug_writes_stack_dumps_into_the_cwd(tmp_path, tiny_dataset,
                                                         in_tmp_cwd):
    """A worker's stderr is invisible in a notebook, so the dump goes to a file.

    A healthy worker cancels the watchdog on its first tick, so the files stay
    empty -- their presence, not their content, is what is asserted.
    """
    out = run_dataset(_cfg(tmp_path, tiny_dataset, HIGH_SPEEDUP=True,
                           N_WORKERS=2, HEARTBEAT_EVERY_S=1,
                           HEARTBEAT_DEBUG=True), 1000)
    assert len(_rows(out)) == 4
    dumps = [p for p in os.listdir(in_tmp_cwd) if p.startswith("hb_stack_")]
    assert dumps, "HEARTBEAT_DEBUG must arm the faulthandler watchdog per worker"
    for d in dumps:
        assert os.path.getsize(os.path.join(in_tmp_cwd, d)) == 0, \
            "a healthy worker cancels the watchdog before it ever fires"


def test_n_workers_one_takes_the_serial_path_and_still_uses_the_heavy_solver(
        tmp_path, tiny_dataset, capsys):
    out = run_dataset(_cfg(tmp_path, tiny_dataset, HIGH_SPEEDUP=True,
                           N_WORKERS=1), 1000)
    printed = capsys.readouterr().out
    assert "HIGH_SPEEDUP: 1 worker(s)" in printed
    assert "warming numba in the parent" not in printed, "no pool, so no pre-fork warm-up"
    assert all(r["path_recovered"] is True for r in _rows(out))
