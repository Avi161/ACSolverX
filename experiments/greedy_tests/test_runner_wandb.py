"""The seam between ``run_dataset`` and ``experiments/wandb_tracking.py``.

Scope. `wandb_tracking`'s own behaviour -- the identity scheme, the anytime
profile, the panels, the resume semantics -- is covered by `tests/wandb_tracking_test.py`
and `tests/wandb_offline_integration.py`. Duplicating that here would mean two
places to update. What is *not* covered there, and is covered here, is the wiring:
that `run_dataset` reaches `wandb_tracking` with the right arguments, that the
jsonl is written regardless, and above all that `USE_WANDB=False` never imports
`wandb` at all -- which is what lets this suite run in an environment without it.

Everything runs under ``WANDB_MODE="disabled"``: a real ``Run`` object, no network.
"""

import json

import pytest

import experiments.run_baseline as rb
from experiments.run_baseline import DEFAULT_CONFIG, run_dataset
from experiments.greedy_tests.fixtures.presentations import MS640, load_flat_lines

pytestmark = pytest.mark.wandb

STATS = {
    "solved": True, "nodes_explored": 42, "path_length": 1,
    "min_relator_length": 2, "min_relator": ["Y", "X"],
    "max_relator_length": 9, "max_relator": ["YYXyx", "Yxyx"],
    "max_relator_length_expanded": 7, "max_relator_expanded": ["YYXyx", "Yx"],
    "path": [["YYXyx", "Yx"], ["Y", "X"]], "path_moves": ["1_1_0_0"],
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


def _rows(path):
    with open(path) as f:
        return [json.loads(ln) for ln in f if ln.strip()]


def test_wandb_is_never_touched_when_disabled(cfg, monkeypatch):
    """``USE_WANDB=False`` must not reach ``wandb_tracking`` at all.

    Any call becomes an ImportError-shaped failure here, standing in for an
    environment where wandb is not installed.
    """
    monkeypatch.setattr(rb, "greedy_search", lambda *a, **k: dict(STATS))

    def explode(*a, **k):
        raise AssertionError("wandb_tracking must not be called with USE_WANDB=False")

    monkeypatch.setattr(rb.wandb_tracking, "init_run", explode)
    monkeypatch.setattr(rb.wandb_tracking, "finish_run", explode)

    out = run_dataset({**cfg, "USE_WANDB": False}, 500)
    assert len(_rows(out)) == 3


def test_a_disabled_run_still_writes_the_jsonl(cfg, monkeypatch):
    """W&B is a mirror; the jsonl stays the source of truth."""
    monkeypatch.setattr(rb, "greedy_search", lambda *a, **k: dict(STATS))
    out = run_dataset(cfg, 500)
    assert [r["pres_id"] for r in _rows(out)] == [0, 1, 2]


def test_init_run_receives_the_jsonl_stem_as_the_run_id(cfg, monkeypatch):
    """One identity for the file and the run, so both collide in the same class."""
    import os

    monkeypatch.setattr(rb, "greedy_search", lambda *a, **k: dict(STATS))
    seen = {}
    real = rb.wandb_tracking.init_run

    def spy(cfg_, budget, n_pres, run_id, run_prefix, subset_tag):
        seen.update(budget=budget, n_pres=n_pres, run_id=run_id,
                    run_prefix=run_prefix, subset_tag=subset_tag)
        return real(cfg_, budget, n_pres, run_id, run_prefix, subset_tag)

    monkeypatch.setattr(rb.wandb_tracking, "init_run", spy)
    out = run_dataset(cfg, 500)

    stem = os.path.basename(out)[: -len(".jsonl")]
    assert seen["run_id"] == stem
    assert seen["budget"] == 500 and seen["n_pres"] == 3
    assert seen["run_prefix"] == rb._run_prefix(
        {**DEFAULT_CONFIG, **cfg}, 500, 3)
    assert seen["subset_tag"] == "all"


def test_the_live_logger_is_seeded_from_the_rows_already_on_disk(cfg, monkeypatch):
    """A resumed run's cumulative curves must continue, not restart at zero."""
    monkeypatch.setattr(rb, "greedy_search", lambda *a, **k: dict(STATS))
    run_dataset(cfg, 500)                       # writes 3 rows, 42 nodes each

    captured = {}
    real = rb.wandb_tracking.LiveLogger

    class Spy(real):
        def __init__(self, run, cfg_, node_budget, **kw):
            captured.update(kw)
            super().__init__(run, cfg_, node_budget, **kw)

    monkeypatch.setattr(rb.wandb_tracking, "LiveLogger", Spy)
    run_dataset(cfg, 500)                       # everything already done

    assert captured["n_seen"] == 3
    assert captured["n_solved"] == 3
    assert captured["cum_nodes"] == 3 * 42, "cum_nodes must be seeded from the jsonl"
    assert captured["n_todo"] == 0


def test_finish_run_is_called_with_the_output_paths(cfg, monkeypatch):
    monkeypatch.setattr(rb, "greedy_search", lambda *a, **k: dict(STATS))
    seen = {}
    real = rb.wandb_tracking.finish_run

    def spy(run, logger, out_path, paths_path, run_id, *a, **k):
        seen.update(out_path=out_path, paths_path=paths_path, run_id=run_id)
        return real(run, logger, out_path, paths_path, run_id, *a, **k)

    monkeypatch.setattr(rb.wandb_tracking, "finish_run", spy)
    out = run_dataset(cfg, 500)

    assert seen["out_path"] == out
    assert seen["paths_path"] == out[: -len(".jsonl")] + "_paths.jsonl"
    assert seen["run_id"] in out


def test_the_wandb_toggles_stay_out_of_the_run_identity():
    """Changing where results are mirrored must not start a new jsonl."""
    base = rb._run_prefix(dict(DEFAULT_CONFIG), 1000, 640)
    for key, value in (("USE_WANDB", True), ("WANDB_PROJECT", "other"),
                       ("WANDB_ENTITY", "someone-else"), ("WANDB_MODE", "offline"),
                       ("WANDB_GROUP", "custom")):
        assert rb._run_prefix({**DEFAULT_CONFIG, key: value}, 1000, 640) == base
