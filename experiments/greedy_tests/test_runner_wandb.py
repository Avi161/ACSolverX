"""W&B wiring, exercised offline.

``USE_WANDB=False`` must not even import ``wandb`` -- the import is inside the
``if``, which is what lets this suite run in an environment without it. When it
is enabled, ``WANDB_MODE="disabled"`` gives a real ``Run`` object with no network,
so the calls are checked for real rather than against a mock.

The ``define_metric`` assertions matter: logging ``solve_rate`` at ``step=pres_id``
on a resumable run is rejected as non-monotonic once the finish-time panel logs
have pushed the global step past the last ``pres_id``.
"""

import json

import pytest

import experiments.run_baseline as rb
from experiments.run_baseline import DEFAULT_CONFIG, run_dataset
from experiments.greedy_tests.fixtures.presentations import MS640, load_flat_lines

wandb = pytest.importorskip("wandb")
pytestmark = pytest.mark.wandb

STATS = {
    "solved": True, "nodes_explored": 42, "path_length": 2,
    "min_relator_length": 2, "min_relator": ["Y", "X"],
    "max_relator_length": 9, "max_relator": ["YYXyx", "Yxyx"],
    "max_relator_length_expanded": 7, "max_relator_expanded": ["YYXyx", "Yx"],
    "path": [["YYXyx", "Yx"], ["Y", "X"]], "path_moves": ["1_1_0_0", "2_-1_1_0"],
}


@pytest.fixture
def tiny_dataset(tmp_path):
    lines = load_flat_lines(MS640)[:3]
    p = tmp_path / "tiny.txt"
    p.write_text("".join(repr(list(ln)) + "\n" for ln in lines))
    return str(p)


@pytest.fixture
def cfg(tmp_path, tiny_dataset):
    return {**DEFAULT_CONFIG, "DATASET": tiny_dataset,
            "LOCAL_OUT_DIR": str(tmp_path / "out"), "PROGRESS_EVERY": 100,
            "USE_WANDB": True, "WANDB_MODE": "disabled", "WANDB_ENTITY": None}


def test_wandb_is_not_imported_when_disabled(cfg, monkeypatch):
    """The lazy import is what lets the rest of the suite run without wandb."""
    monkeypatch.setattr(rb, "greedy_search", lambda *a, **k: dict(STATS))
    monkeypatch.setitem(__import__("sys").modules, "wandb", None)
    out = run_dataset({**cfg, "USE_WANDB": False}, 500)
    assert len(open(out).readlines()) == 3


def test_a_disabled_run_still_writes_the_jsonl(cfg, monkeypatch):
    monkeypatch.setattr(rb, "greedy_search", lambda *a, **k: dict(STATS))
    out = run_dataset(cfg, 500)
    rows = [json.loads(ln) for ln in open(out) if ln.strip()]
    assert [r["pres_id"] for r in rows] == [0, 1, 2]


def test_solve_rate_is_logged_against_pres_id_and_never_as_a_step(cfg, monkeypatch):
    """Regression for "steps must be monotonically increasing" on a resumed run."""
    monkeypatch.setattr(rb, "greedy_search", lambda *a, **k: dict(STATS))
    logged, metrics = [], []

    real_init = wandb.init

    def fake_init(**kw):
        run = real_init(**kw)
        run.define_metric = lambda name, **k: metrics.append((name, k))
        run.log = lambda data, **k: logged.append((data, k))
        return run

    monkeypatch.setattr(wandb, "init", fake_init)
    run_dataset(cfg, 500)

    assert ("pres_id", {}) in metrics
    assert ("solve_rate", {"step_metric": "pres_id"}) in metrics
    per_row = [d for d, k in logged if "solve_rate" in d]
    assert len(per_row) == 3
    assert all("pres_id" in d for d in per_row)
    assert all(k == {} for d, k in logged if "solve_rate" in d), \
        "solve_rate must never be pinned to an explicit step="


def test_the_run_id_is_the_jsonl_stem(cfg, monkeypatch):
    """One identity for the file and the run, so both collide in the same class."""
    monkeypatch.setattr(rb, "greedy_search", lambda *a, **k: dict(STATS))
    seen = {}
    real_init = wandb.init

    def fake_init(**kw):
        seen.update(kw)
        return real_init(**kw)

    monkeypatch.setattr(wandb, "init", fake_init)
    out = run_dataset(cfg, 500)

    import os
    stem = os.path.basename(out)[: -len(".jsonl")]
    assert seen["id"] == stem and seen["name"] == stem
    assert seen["resume"] == "allow"
    assert seen["config"]["node_budget"] == 500
    assert seen["config"]["max_relator_length"] == 24


def test_the_table_is_rebuilt_from_existing_rows_on_resume(cfg, monkeypatch):
    monkeypatch.setattr(rb, "greedy_search", lambda *a, **k: dict(STATS))
    run_dataset(cfg, 500)

    created = []

    class RecordingTable(wandb.Table):
        # A subclass, not a lambda: _finish_wandb builds a second Table for the
        # scatter panel and wandb.plot.scatter type-checks it with isinstance.
        def __init__(self, *a, **kw):
            super().__init__(*a, **kw)
            created.append(self)

    monkeypatch.setattr(wandb, "Table", RecordingTable)
    run_dataset(cfg, 500)          # everything already done
    assert created, "a Table must be constructed"
    assert len(created[0].data) == 3, "the three prior rows must be replayed into it"


def test_add_table_row_tolerates_missing_gated_columns():
    from experiments.run_baseline import _add_table_row

    table = wandb.Table(columns=[
        "pres_id", "r1", "r2", "node_budget", "max_relator_length_cap",
        "cyclic_reduce", "nodes_explored", "solved", "path_length",
        "min_relator_length", "max_relator_length"])
    _add_table_row(table, {"pres_id": 0, "r1": "x", "r2": "y", "node_budget": 1,
                           "nodes_explored": 2, "solved": True, "path_length": 1})
    assert len(table.data) == 1
    assert table.data[0][4] is None      # max_relator_length_cap was gated off
