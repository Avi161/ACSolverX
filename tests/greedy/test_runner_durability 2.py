"""A written row must reach the disk, and must not be written twice over.

Three guarantees, each of which failed once in production:

1. ``_emit`` fsyncs. ``flush()`` only hands bytes to the OS; on Colab's Google
   Drive FUSE mount a flushed row could still be dropped, and a 1M pooled run
   silently lost two presentations that way. Because the lost ids never entered
   ``done``, every resume re-searched them and lost them again.
2. ``_report_lost_rows`` notices. A filesystem that drops an fsynced write is
   beyond the runner's control, but discovering it by reading a jsonl by hand,
   hours later, is not acceptable. Say so at the end of the run.
3. ``use_path=False`` skips the path-recovery re-solve entirely. That re-solve
   runs the NORMAL solver at the full node budget with no memory guard (~20 GB
   at 1M/mrl48) to produce a path that ``_write_path`` then discards.

``N_WORKERS=1`` throughout, so no pool is built and ``greedy_search`` can be
monkeypatched in-process. The pool path is covered by ``test_runner_parallel``.
"""

import json
import os

import pytest

from experiments.run_baseline import DEFAULT_CONFIG, run_dataset, _report_lost_rows
import experiments.run_baseline as rb
from experiments.greedy_tests.fixtures.presentations import MS640, load_flat_lines

BUDGET = 500        # every fixture below solves in <5 nodes; see MAX_BUDGET = 1_000


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
            "HIGH_SPEEDUP": True,
            "N_WORKERS": 1,
            **over}


def _rows(path):
    with open(path) as f:
        return [json.loads(ln) for ln in f if ln.strip()]


def _count_solver_calls(monkeypatch):
    """Record every greedy_search call's high_speedup flag."""
    real = rb.greedy_search
    calls = []

    def fake(r1, r2, budget, **kw):
        calls.append(kw.get("high_speedup", False))
        return real(r1, r2, budget, **kw)

    monkeypatch.setattr(rb, "greedy_search", fake)
    return calls


# --- 1. every row is fsynced, not merely flushed ---------------------------

def test_emit_fsyncs_every_row(tmp_path, tiny_dataset, monkeypatch):
    synced = []
    real_fsync = os.fsync
    monkeypatch.setattr(os, "fsync", lambda fd: (synced.append(fd), real_fsync(fd))[1])

    out = run_dataset(_cfg(tmp_path, tiny_dataset), node_budget=BUDGET)

    assert len(_rows(out)) == 4
    # one per row at minimum; paths file adds more when use_path is on
    assert len(synced) >= 4, f"expected >=4 fsync calls, got {len(synced)}"


def test_persist_survives_a_filesystem_that_refuses_fsync(tmp_path, tiny_dataset,
                                                          monkeypatch):
    """An OSError from fsync must not abort a 30-hour run."""
    def refuse(fd):
        raise OSError("this filesystem does not support fsync")

    monkeypatch.setattr(os, "fsync", refuse)
    out = run_dataset(_cfg(tmp_path, tiny_dataset), node_budget=BUDGET)
    assert len(_rows(out)) == 4


# --- 2. a dropped row is reported, not silently tolerated -------------------

def test_report_lost_rows_names_the_missing_ids(tmp_path, capsys):
    p = tmp_path / "out.jsonl"
    with open(p, "w") as f:                      # id 2 never reached the disk
        for i in (0, 1, 3):
            f.write(json.dumps({"pres_id": i, "solved": False}) + "\n")

    lost = _report_lost_rows(str(p), done_before={0, 1}, todo_ids=[2, 3])

    assert lost == [2]
    out = capsys.readouterr().out
    assert "NOT on disk" in out and "[2]" in out


def test_report_lost_rows_silent_when_complete(tmp_path, capsys):
    p = tmp_path / "out.jsonl"
    with open(p, "w") as f:
        for i in range(4):
            f.write(json.dumps({"pres_id": i, "solved": False}) + "\n")

    assert _report_lost_rows(str(p), done_before={0, 1}, todo_ids=[2, 3]) == []
    assert "NOT on disk" not in capsys.readouterr().out


def test_a_clean_run_reports_nothing_lost(tmp_path, tiny_dataset, capsys):
    run_dataset(_cfg(tmp_path, tiny_dataset), node_budget=BUDGET)
    assert "NOT on disk" not in capsys.readouterr().out


# --- 3. use_path=False must not trigger the recovery re-solve ---------------

def test_use_path_false_skips_the_recovery_resolve(tmp_path, tiny_dataset,
                                                   monkeypatch):
    calls = _count_solver_calls(monkeypatch)
    out = run_dataset(_cfg(tmp_path, tiny_dataset, use_path=False),
                      node_budget=BUDGET)

    rows = _rows(out)
    assert len(rows) == 4 and all(r["solved"] for r in rows)
    assert not any(r.get("path_pending") for r in rows), \
        "a row was parked as path_pending even though use_path is off"
    assert not any(r.get("path_recovered") for r in rows)
    # every solve ran in heavy mode; the normal solver was never invoked
    assert calls and all(calls), \
        f"the unguarded normal solver ran {calls.count(False)} time(s)"
    assert not os.path.exists(out[: -len(".jsonl")] + "_paths.jsonl") or \
        _rows(out[: -len(".jsonl")] + "_paths.jsonl") == []


def test_use_path_true_still_recovers_each_path(tmp_path, tiny_dataset,
                                                monkeypatch):
    """Control: the recovery re-solve is exactly what use_path=True buys."""
    calls = _count_solver_calls(monkeypatch)
    out = run_dataset(_cfg(tmp_path, tiny_dataset, use_path=True),
                      node_budget=BUDGET)

    rows = _rows(out)
    assert len(rows) == 4 and all(r["solved"] for r in rows)
    assert all(r.get("path_recovered") for r in rows)
    assert not any(r.get("path_pending") for r in rows), \
        "path_pending must be cleared once the path is recovered"
    assert calls.count(False) == 4, "each solved row needs one normal-mode re-solve"
    assert len(_rows(out[: -len(".jsonl")] + "_paths.jsonl")) == 4
