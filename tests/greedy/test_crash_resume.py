"""Resume survives the two ways a run really dies: a torn write and a full sweep.

Both defects covered here were once pinned in ``test_known_gaps.py`` as
``xfail(strict=True)`` under the repo's "do not modify existing code" rule. They
are now fixed in ``run_baseline.py``, so the markers are gone and these are
ordinary regression tests. See ``experiments/lessons/run-baseline-two-known-bugs.md``.

The load-bearing test is ``test_appending_after_a_torn_write_keeps_the_file_parseable``.
The reader-level tests further down pass whether or not ``_repair_jsonl`` exists
-- only driving a real append over a damaged file proves the bug is gone, because
the damage is done by the *writer*, not the reader.
"""

import json
import os

import pytest

import experiments.run_baseline as rb
from experiments.run_baseline import (
    DEFAULT_CONFIG, _read_done, _repair_jsonl, _resolve_paths, _run_prefix,
    run_dataset,
)
from experiments.greedy_tests.fixtures.presentations import MS640, load_flat_lines

STATS = {
    "solved": True, "nodes_explored": 42, "path_length": 1,
    "min_relator_length": 2, "min_relator": ["Y", "X"],
    "max_relator_length": 9, "max_relator": ["YYXyx", "Yxyx"],
    "max_relator_length_expanded": 7, "max_relator_expanded": ["YYXyx", "Yx"],
    "path": [["YYXyx", "Yx"], ["Y", "X"]], "path_moves": ["1_1_0_0"],
}

# A crash mid-write leaves exactly this: whole rows, then a half-written one
# with no trailing newline.
TORN = ('{"pres_id": 0, "solved": true}\n'
        '{"pres_id": 1, "solved": false}\n'
        '{"pres_id": 2, "solv')


@pytest.fixture
def tiny_dataset(tmp_path):
    lines = load_flat_lines(MS640)[:4]
    p = tmp_path / "tiny.txt"
    p.write_text("".join(repr(list(ln)) + "\n" for ln in lines))
    return str(p)


@pytest.fixture
def cfg(tmp_path, tiny_dataset):
    return {**DEFAULT_CONFIG, "DATASET": tiny_dataset,
            "LOCAL_OUT_DIR": str(tmp_path / "out"), "USE_WANDB": False}


def _seed(cfg_, budget, n_pres, text, suffix=".jsonl"):
    """Write `text` where `_resolve_paths` will look, and return that path."""
    out_dir = cfg_["LOCAL_OUT_DIR"]
    os.makedirs(out_dir, exist_ok=True)
    p = os.path.join(out_dir,
                     _run_prefix(cfg_, budget, n_pres) + "01_01_20" + suffix)
    with open(p, "w") as f:
        f.write(text)
    return p


# -- _repair_jsonl -----------------------------------------------------------


def test_an_intact_file_is_left_byte_for_byte_alone(tmp_path):
    p = tmp_path / "out.jsonl"
    text = '{"pres_id": 0}\n{"pres_id": 1}\n'
    p.write_text(text)
    assert _repair_jsonl(str(p)) == 0
    assert p.read_text() == text


def test_a_torn_final_line_is_truncated_away(tmp_path, capsys):
    p = tmp_path / "out.jsonl"
    p.write_text(TORN)
    assert _repair_jsonl(str(p)) == len('{"pres_id": 2, "solv')
    assert p.read_text() == ('{"pres_id": 0, "solved": true}\n'
                             '{"pres_id": 1, "solved": false}\n')
    assert "truncated final line" in capsys.readouterr().out


def test_a_file_that_is_one_partial_line_is_emptied(tmp_path):
    """No newline anywhere: nothing in it was ever completed."""
    p = tmp_path / "out.jsonl"
    p.write_text('{"pres_id": 0, "sol')
    _repair_jsonl(str(p))
    assert p.read_text() == ""


def test_repairing_a_missing_or_empty_file_is_a_no_op(tmp_path):
    assert _repair_jsonl(str(tmp_path / "nope.jsonl")) == 0
    p = tmp_path / "empty.jsonl"
    p.write_text("")
    assert _repair_jsonl(str(p)) == 0


def test_repair_is_idempotent(tmp_path):
    p = tmp_path / "out.jsonl"
    p.write_text(TORN)
    _repair_jsonl(str(p))
    once = p.read_text()
    assert _repair_jsonl(str(p)) == 0
    assert p.read_text() == once


# -- the actual bug: the writer, not the reader ------------------------------


def test_appending_after_a_torn_write_keeps_the_file_parseable(cfg, monkeypatch):
    """The load-bearing regression.

    A stub with no trailing newline plus ``open(path, "a")`` concatenates the
    next row onto it: ``{"pres_id": 2, "solv{"pres_id": 2, ...}``. That line is
    now in the *middle* of the file, so no amount of trailing-line tolerance in
    a reader can ever recover it. Guarding only ``_read_done`` would leave this
    green-looking and still broken.
    """
    monkeypatch.setattr(rb, "greedy_search", lambda *a, **k: dict(STATS))
    seeded = _seed(cfg, 500, 4, TORN)

    out = run_dataset(cfg, 500)
    assert out == seeded, "must resume into the seeded file, not start a new one"

    with open(out) as f:
        raw = [ln for ln in f if ln.strip()]
    rows = [json.loads(ln) for ln in raw]          # raises if a line got corrupted

    ids = [r["pres_id"] for r in rows]
    assert len(ids) == len(set(ids)), f"duplicate rows: {ids}"
    assert set(ids) == {0, 1, 2, 3}, "the torn presentation must be re-run"
    assert raw[-1].endswith("\n")


def test_the_torn_row_is_re_run_rather_than_trusted(cfg, monkeypatch):
    """pres 2's row was never completed, so it must be searched again."""
    searched = []

    def spy(r1, r2, *a, **k):
        searched.append((r1, r2))
        return dict(STATS)

    monkeypatch.setattr(rb, "greedy_search", spy)
    _seed(cfg, 500, 4, TORN)
    run_dataset(cfg, 500)

    assert len(searched) == 2, "pres 0 and 1 are done; 2 and 3 are not"


def test_a_paths_file_is_repaired_too(cfg, monkeypatch):
    """`paths_path` is appended to just like `out_path`, so it tears the same way."""
    monkeypatch.setattr(rb, "greedy_search", lambda *a, **k: dict(STATS))
    _seed(cfg, 500, 4, TORN)
    paths = _seed(cfg, 500, 4, '{"pres_id": 0, "r1": "x"}\n{"pres_id": 1, "r',
                  suffix="_paths.jsonl")

    run_dataset(cfg, 500)

    with open(paths) as f:
        for ln in f:
            if ln.strip():
                json.loads(ln)


# -- readers -----------------------------------------------------------------


def test_read_done_tolerates_a_truncated_trailing_line(tmp_path):
    """Reading an unrepaired file must resume, not crash."""
    p = tmp_path / "out.jsonl"
    p.write_text(TORN)
    done, seen, solved = _read_done(str(p))
    assert done == {0, 1}
    assert (seen, solved) == (2, 1)


def test_read_done_refuses_to_silently_skip_a_corrupt_interior_line(tmp_path):
    """Only a torn *final* line is a crash artefact.

    A bad line in the middle means something else went wrong. Skipping it would
    drop that pres_id from `done` and silently re-run it, hiding the corruption.
    """
    p = tmp_path / "out.jsonl"
    p.write_text('{"pres_id": 0, "solved": true}\n'
                 'garbage\n'
                 '{"pres_id": 2, "solved": true}\n')
    with pytest.raises(ValueError):
        _read_done(str(p))


def test_read_done_on_a_missing_file_is_empty(tmp_path):
    assert _read_done(str(tmp_path / "nope.jsonl")) == (set(), 0, 0)


# -- a fully-resumed heavy run -----------------------------------------------


def test_a_fully_resumed_heavy_run_does_not_crash(cfg):
    """``HIGH_SPEEDUP`` + >1 worker + nothing left to do.

    The numba warm-up used to read ``todo[0]`` unconditionally inside
    ``if high and n_workers > 1``, before the pool was created, so re-running a
    finished heavy sweep to confirm it was complete raised ``IndexError``. No
    worker is ever spawned on this path, so the test stays fast.
    """
    hcfg = {**cfg, "HIGH_SPEEDUP": True, "N_WORKERS": 2}
    seeded = _seed(hcfg, 500, 4,
                   "".join(json.dumps({"pres_id": i, "solved": True}) + "\n"
                           for i in range(4)))

    resolved, _, _, _ = _resolve_paths(hcfg, 500, 4)
    assert resolved == seeded
    assert _read_done(resolved)[1] == 4, "the fixture must leave nothing to do"

    assert run_dataset(hcfg, 500) == resolved


def test_a_fully_resumed_heavy_run_spawns_no_pool(cfg, monkeypatch):
    """Nothing to do must mean no fork, not merely no crash."""
    hcfg = {**cfg, "HIGH_SPEEDUP": True, "N_WORKERS": 2}
    _seed(hcfg, 500, 4,
          "".join(json.dumps({"pres_id": i, "solved": True}) + "\n"
                  for i in range(4)))

    def explode(*a, **k):
        raise AssertionError("no presentation is left to search; pool must not start")

    monkeypatch.setattr(rb, "greedy_search", explode)
    run_dataset(hcfg, 500)
