"""Data loading, row construction, the jsonl schema, and resume.

``run_dataset`` is exercised with a stubbed ``greedy_search`` wherever the point
is harness behaviour rather than search behaviour -- the real solver is slow and
its correctness is covered elsewhere. The integration tests at the bottom use
the real one on a handful of easy presentations.
"""

import json
import os

import pytest

import experiments.run_baseline as rb
from experiments.run_baseline import (
    DEFAULT_CONFIG, _build_row, _path_payload, _read_done, int_line_to_relators,
    load_dataset, run_dataset,
)
from experiments.greedy_tests.fixtures.presentations import MS640, load_flat_lines, repo_root

STATS = {
    "solved": True, "nodes_explored": 42, "path_length": 2,
    "min_relator_length": 2, "min_relator": ["Y", "X"],
    "max_relator_length": 9, "max_relator": ["YYXyx", "Yxyx"],
    "max_relator_length_expanded": 7, "max_relator_expanded": ["YYXyx", "Yx"],
    "path": [["YYXyx", "Yx"], ["Yx", "Xy"], ["Y", "X"]],
    "path_moves": ["1_1_0_0", "2_-1_1_0"],
}
UNSOLVED = {**STATS, "solved": False, "path_length": None, "path": [], "path_moves": []}


@pytest.fixture
def tiny_dataset(tmp_path):
    """Six real ms640 lines, written to a standalone file with an absolute path."""
    lines = load_flat_lines(MS640)[:6]
    p = tmp_path / "tiny.txt"
    p.write_text("".join(repr(list(ln)) + "\n" for ln in lines))
    return str(p)


@pytest.fixture
def cfg(tmp_path, tiny_dataset):
    return {**DEFAULT_CONFIG,
            "DATASET": tiny_dataset,
            "LOCAL_OUT_DIR": str(tmp_path / "out"),
            "USE_WANDB": False,
            "PROGRESS_EVERY": 100}


def _rows(path):
    with open(path) as f:
        return [json.loads(ln) for ln in f if ln.strip()]


# -- the flat-int codec ------------------------------------------------------


def test_int_line_to_relators_decodes_the_documented_alphabet():
    assert int_line_to_relators([1, -1, 0, 0, 2, -2, 0, 0]) == ("xX", "yY")


def test_int_line_to_relators_splits_in_half_and_strips_padding():
    line = [1, 2, 0, 0] + [-1, 0, 0, 0]
    assert int_line_to_relators(line) == ("xy", "X")


def test_int_line_to_relators_is_hardcoded_to_two_relators():
    """``len // 2``. A three-relator line would be silently mis-split, not rejected.

    Pinned so that generalising the layout for stable AC is a visible change.
    Feeding it a 3-slot line yields two bogus relators and no error.
    """
    three_slots = [1, 0] + [2, 0] + [3, 0]      # r1 | r2 | r3, 2 ints each
    with pytest.raises(KeyError):
        # 3 is not in the 2-generator alphabet; the split is 3|3 regardless
        int_line_to_relators(three_slots)
    both = int_line_to_relators([1, 0, 2, 0, -1, 0])
    assert both == ("xy", "X"), "silently split 3 slots into 2 -- not an error"


def test_load_dataset_yields_pres_id_and_relator_strings():
    got = list(load_dataset(os.path.join(repo_root(), MS640), subset=(0, 3)))
    assert [pid for pid, _, _ in got] == [0, 1, 2]
    assert got[0][1:] == ("YYXyx", "Yx")


def test_load_dataset_subset_none_is_everything():
    assert len(list(load_dataset(os.path.join(repo_root(), MS640)))) == 640


def test_load_dataset_accepts_an_explicit_id_list():
    got = list(load_dataset(os.path.join(repo_root(), MS640), subset=[5, 2]))
    assert [pid for pid, _, _ in got] == [5, 2]


def test_load_dataset_raises_on_an_out_of_range_subset():
    with pytest.raises(IndexError):
        list(load_dataset(os.path.join(repo_root(), MS640), subset=(638, 645)))


# -- _build_row / _path_payload ---------------------------------------------


def _base_cfg(**over):
    return {**DEFAULT_CONFIG, **over}


def test_always_present_columns():
    row = _build_row(_base_cfg(), 7, "xy", "xY", 1000, STATS, 1.5)
    for k in ("pres_id", "r1", "r2", "node_budget", "max_relator_length_cap",
              "cyclic_reduce", "nodes_explored", "solved", "path_length"):
        assert k in row
    assert row["pres_id"] == 7 and row["node_budget"] == 1000
    assert "path_recovered" not in row


@pytest.mark.parametrize("toggle,keys", [
    ("use_min_relator", ("min_relator_length", "min_relator")),
    ("use_max_relator", ("max_relator_length", "max_relator")),
    ("use_max_relator_expanded", ("max_relator_length_expanded", "max_relator_expanded")),
])
def test_each_use_toggle_gates_exactly_its_own_columns(toggle, keys):
    on = _build_row(_base_cfg(**{toggle: True}), 0, "x", "y", 10, STATS, 0.1)
    off = _build_row(_base_cfg(**{toggle: False}), 0, "x", "y", 10, STATS, 0.1)
    assert all(k in on for k in keys)
    assert all(k not in off for k in keys)
    assert set(on) - set(off) == set(keys)


def test_use_time_gates_the_timing_column():
    assert "time_seconds" in _build_row(_base_cfg(use_time=True), 0, "x", "y", 1, STATS, 1.23456)
    assert _build_row(_base_cfg(use_time=True), 0, "x", "y", 1, STATS, 1.23456)["time_seconds"] == 1.2346
    assert "time_seconds" not in _build_row(_base_cfg(use_time=False), 0, "x", "y", 1, STATS, 1.0)


def test_the_path_is_inlined_only_when_not_written_to_a_sidecar():
    inline = _base_cfg(use_path=True, PATH_IN_SEPARATE_FILE=False)
    assert "path_moves" in _build_row(inline, 0, "x", "y", 1, STATS, 0.1)
    sidecar = _base_cfg(use_path=True, PATH_IN_SEPARATE_FILE=True)
    assert "path_moves" not in _build_row(sidecar, 0, "x", "y", 1, STATS, 0.1)


def test_an_unsolved_row_never_carries_a_path():
    cfg = _base_cfg(use_path=True, PATH_IN_SEPARATE_FILE=False)
    row = _build_row(cfg, 0, "x", "y", 1, UNSOLVED, 0.1)
    assert "path_moves" not in row and "path" not in row
    assert row["path_length"] is None


@pytest.mark.parametrize("fmt,keys", [
    ("moves", {"path_moves"}), ("strings", {"path"}), ("both", {"path_moves", "path"}),
])
def test_path_format_selects_the_payload(fmt, keys):
    assert set(_path_payload(_base_cfg(PATH_FORMAT=fmt), STATS)) == keys


# -- _read_done --------------------------------------------------------------


def test_read_done_on_a_missing_file(tmp_path):
    assert _read_done(str(tmp_path / "nope.jsonl")) == (set(), 0, 0)


def test_read_done_counts_seen_and_solved_and_skips_blank_lines(tmp_path):
    p = tmp_path / "a.jsonl"
    p.write_text('{"pres_id": 1, "solved": true}\n\n{"pres_id": 2, "solved": false}\n\n')
    done, seen, solved = _read_done(str(p))
    assert done == {1, 2} and seen == 2 and solved == 1


# -- run_dataset -------------------------------------------------------------


def test_run_dataset_writes_one_row_per_presentation(cfg, monkeypatch):
    monkeypatch.setattr(rb, "greedy_search", lambda *a, **k: dict(STATS))
    out = run_dataset(cfg, 500)
    rows = _rows(out)
    assert [r["pres_id"] for r in rows] == list(range(6))
    assert all(r["node_budget"] == 500 for r in rows)


def test_run_dataset_writes_the_paths_sidecar_for_solved_rows_only(cfg, monkeypatch):
    calls = {"n": 0}

    def fake(*a, **k):
        calls["n"] += 1
        return dict(STATS) if calls["n"] % 2 else dict(UNSOLVED)

    monkeypatch.setattr(rb, "greedy_search", fake)
    out = run_dataset(cfg, 500)
    paths = out[: -len(".jsonl")] + "_paths.jsonl"
    assert len(_rows(out)) == 6
    assert len(_rows(paths)) == 3
    assert set(_rows(paths)[0]) == {"pres_id", "r1", "r2", "path_moves"}


def test_resume_skips_presentations_already_present(cfg, monkeypatch):
    monkeypatch.setattr(rb, "greedy_search", lambda *a, **k: dict(STATS))
    out = run_dataset(cfg, 500)
    assert len(_rows(out)) == 6

    seen = []
    monkeypatch.setattr(rb, "greedy_search",
                        lambda *a, **k: seen.append(1) or dict(STATS))
    out2 = run_dataset(cfg, 500)
    assert out2 == out
    assert seen == [], "a resumed run must not re-solve anything"
    assert len(_rows(out)) == 6


def test_resume_off_appends_duplicate_pres_ids(cfg, monkeypatch):
    """Characterization: there is no write-time dedup, only the resume filter."""
    monkeypatch.setattr(rb, "greedy_search", lambda *a, **k: dict(STATS))
    out = run_dataset(cfg, 500)
    run_dataset({**cfg, "RESUME": False}, 500)
    ids = [r["pres_id"] for r in _rows(out)]
    assert len(ids) == 12 and len(set(ids)) == 6


def test_two_budgets_write_two_files(cfg, monkeypatch):
    monkeypatch.setattr(rb, "greedy_search", lambda *a, **k: dict(STATS))
    a = run_dataset(cfg, 500)
    b = run_dataset(cfg, 900)
    assert a != b
    assert len(_rows(a)) == len(_rows(b)) == 6
    assert {r["node_budget"] for r in _rows(b)} == {900}


def test_subset_selects_presentations_and_names_the_file(cfg, monkeypatch):
    monkeypatch.setattr(rb, "greedy_search", lambda *a, **k: dict(STATS))
    out = run_dataset({**cfg, "SUBSET": (1, 4)}, 500)
    assert [r["pres_id"] for r in _rows(out)] == [1, 2, 3]
    assert "_1-4_" in os.path.basename(out)


def test_run_dataset_end_to_end_with_the_real_solver(cfg):
    """No stub: the rows must actually describe solved searches."""
    out = run_dataset({**cfg, "SUBSET": (0, 3)}, 3000)
    rows = _rows(out)
    paths = {p["pres_id"]: p for p in _rows(out[: -len(".jsonl")] + "_paths.jsonl")}
    assert len(rows) == 3 and all(r["solved"] for r in rows)
    for r in rows:
        assert 1 <= r["nodes_explored"] <= 3000
        assert r["max_relator_length_cap"] == 24 and r["cyclic_reduce"] is True
        assert r["path_length"] == len(paths[r["pres_id"]]["path_moves"])


def test_recovered_rows_are_flagged_and_replay_to_a_trivial_state(cfg):
    """The heavy path defers the row until the normal solver has recovered its path."""
    from experiments.search.greedy_baseline import moves_to_states, str_to_move

    out = run_dataset({**cfg, "SUBSET": (0, 3), "HIGH_SPEEDUP": True,
                       "N_WORKERS": 1}, 3000)
    rows = _rows(out)
    assert all(r["solved"] for r in rows)
    assert all(r.get("path_recovered") is True for r in rows), \
        "a solved heavy row must be re-solved and marked"

    paths = _rows(out[: -len(".jsonl")] + "_paths.jsonl")
    for pr in paths:
        states = moves_to_states(pr["r1"], pr["r2"],
                                 [str_to_move(m) for m in pr["path_moves"]])
        assert [len(s) for s in states[-1]] == [1, 1]


def test_unsolved_heavy_rows_are_not_marked_recovered(cfg, monkeypatch):
    monkeypatch.setattr(rb, "greedy_search", lambda *a, **k: dict(UNSOLVED))
    out = run_dataset({**cfg, "HIGH_SPEEDUP": True, "N_WORKERS": 1}, 500)
    assert all("path_recovered" not in r for r in _rows(out))
