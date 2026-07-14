"""run_nocov harness tests: row schema, resume, torn-line repair, filename
identity, the paths file, the config yaml, the big-budget guard — plus ONE
real end-to-end micro-run (budget 100) that closes the loop via replay.

Every other test monkeypatches the search seam
(``experiments.stable_ac.nocov.run_nocov.search_n``) so no real search runs; the
harness behaviour under test is identical either way because run_nocov only
ever sees the returned stats dict.
"""

import json
import os

import pytest
import yaml

import experiments.stable_ac.nocov.run_nocov as rn
from experiments.stable_ac.nocov.run_nocov import (
    DEFAULT_CONFIG, _require_budget_allowed, _run_prefix, main, run_nocov,
)
from experiments.stable_ac.solvern import moves_to_states, str_to_word

YAML_PATH = os.path.join(os.path.dirname(rn.__file__), "config_nocov.yaml")

# A valid search_n stats dict (shapes match a real n_rel=3 nocov solve).
STATS = {
    "solved": True, "nodes_explored": 7, "path_length": 6,
    "min_relator_length": 3, "min_relator": ["Z", "Y", "X"],
    "max_relator_length": 35,
    "max_relator": ["YYYYx", "ZyyyyyyxYYYYYYY", "YYYYYYYXyyyyyyx"],
    "max_relator_length_expanded": 22,
    "max_relator_expanded": ["YYYYx", "Zx", "YYYYYYYXyyyyyyx"],
    "path": [], "path_words": [],
    "path_moves": ["2_0_1_0_0", "1_2_1_0_0"],
}

BASE_KEYS = {
    "name", "source", "pres_id", "r1", "r2", "base_total_length", "z_word",
    "z_relator", "w_family", "mode", "n_gen", "n_rel", "benchmark",
    "node_budget", "max_relator_length_cap", "cyclic_reduce", "nodes_explored",
    "solved", "path_length", "min_relator_length", "min_relator",
    "max_relator_length", "max_relator", "max_relator_length_expanded",
    "max_relator_expanded", "time_seconds", "git_commit",
}
LADDER_KEYS = {"baseline_nodes_at_50k", "baseline_path_at_50k",
               "baseline_solved_at_50k", "nodes_1M", "path_1M"}
REACH_KEYS = {"bar_to_beat", "start_length", "aut_min_rep_r1",
              "aut_min_rep_r2"}


@pytest.fixture
def cfg(tmp_path):
    # ROW_LIMIT=2 selects combined_11's first two rows (ladder: ms499, ms165);
    # WORD_LIMIT=2 keeps A1 to ['x', 'y'] -> 4 jobs total.
    return {**DEFAULT_CONFIG, "LOCAL_OUT_DIR": str(tmp_path / "out"),
            "ROW_LIMIT": 2, "WORD_LIMIT": 2, "USE_WANDB": False}


def _rows(path):
    with open(path) as f:
        return [json.loads(ln) for ln in f if ln.strip()]


def _stub(monkeypatch, stats=STATS):
    calls = []

    def spy(*a, **k):
        calls.append(a)
        return dict(stats)

    monkeypatch.setattr(rn, "search_n", spy)
    return calls


# -- row schema ---------------------------------------------------------------


def test_rows_carry_the_full_schema(cfg, monkeypatch):
    _stub(monkeypatch)
    out = run_nocov(cfg, 100, "A1")
    rows = _rows(out)
    assert len(rows) == 4                       # 2 rows x 2 words
    for r in rows:
        assert BASE_KEYS <= set(r), BASE_KEYS - set(r)
        assert r["mode"] == "nocov"
        assert (r["n_gen"], r["n_rel"]) == (3, 3)
        assert r["z_relator"] == "Z" + r["z_word"]
        assert r["benchmark"] == "combined_11"
        assert r["node_budget"] == 100
        assert r["max_relator_length_cap"] == 64
        assert r["cyclic_reduce"] is True
        # provenance: a 40-hex commit in a checkout, None outside one
        assert r["git_commit"] is None or (
            len(r["git_commit"]) == 40
            and all(c in "0123456789abcdef" for c in r["git_commit"]))
        assert isinstance(r["time_seconds"], float)
    # combined_11's first two rows are ladder rows -> baseline passthrough
    assert all(r["source"] == "ladder" for r in rows)
    for r in rows:
        assert LADDER_KEYS <= set(r), LADDER_KEYS - set(r)
        assert r["pres_id"] is not None


def test_a_reach_row_carries_bar_to_beat(cfg, monkeypatch):
    _stub(monkeypatch)
    out = run_nocov({**cfg, "NAMES": ["AK(3)"], "ROW_LIMIT": None}, 100, "A1")
    rows = _rows(out)
    assert rows and all(r["source"] == "reach" for r in rows)
    for r in rows:
        assert REACH_KEYS <= set(r), REACH_KEYS - set(r)
        assert r["pres_id"] is None             # reach rows have no pres_id


# -- resume -------------------------------------------------------------------


def test_resume_skips_done_jobs(cfg, monkeypatch):
    calls = _stub(monkeypatch)
    out1 = run_nocov(cfg, 100, "A1")
    assert len(calls) == 4
    out2 = run_nocov(cfg, 100, "A1")
    assert out2 == out1, "must resume into the same file, not start a new one"
    assert len(calls) == 4, "the second run must search nothing"
    assert len(_rows(out1)) == 4, "row count unchanged by the re-run"


def test_a_torn_trailing_line_is_repaired_and_re_run(cfg, monkeypatch):
    calls = _stub(monkeypatch)
    out = run_nocov(cfg, 100, "A1")
    with open(out) as f:
        lines = f.readlines()
    torn = json.loads(lines[-1])
    torn_key = (torn["name"], torn["z_word"])
    # A crash mid-write leaves whole rows then a half-written one, no newline.
    with open(out, "w") as f:
        f.writelines(lines[:-1])
        f.write(lines[-1][: len(lines[-1]) // 2])
    calls.clear()

    run_nocov(cfg, 100, "A1")

    rows = _rows(out)                # raises if any line was left corrupted
    keys = [(r["name"], r["z_word"]) for r in rows]
    assert len(keys) == len(set(keys)), f"duplicate rows: {keys}"
    assert len(rows) == 4
    assert len(calls) == 1, "exactly the torn job re-runs"
    assert torn_key in keys
    with open(out) as f:
        assert f.readlines()[-1].endswith("\n")


def test_resume_reattaches_to_an_old_dated_file(cfg, monkeypatch):
    """The date suffix must never gate resume (date-in-filename-broke-resume)."""
    calls = _stub(monkeypatch)
    out = run_nocov(cfg, 100, "A1")
    prefix = _run_prefix(cfg, 100, "A1")
    old = os.path.join(os.path.dirname(out), prefix + "01_01_20.jsonl")
    os.rename(out, old)
    paths = out[:-len(".jsonl")] + "_paths.jsonl"
    os.rename(paths, old[:-len(".jsonl")] + "_paths.jsonl")
    calls.clear()

    out2 = run_nocov(cfg, 100, "A1")

    assert out2 == old, "must continue the old-dated file, not start a new one"
    assert not calls
    assert len(_rows(old)) == 4


# -- filename identity ----------------------------------------------------------


def test_prefix_encodes_identity_not_date():
    c = dict(DEFAULT_CONFIG)
    p = _run_prefix(c, 100, "A1")
    assert p == "nocov_combined_11_A1_100_mrl64_cyc_"
    # every search-identity knob changes the prefix...
    assert _run_prefix(c, 200, "A1") != p
    assert _run_prefix(c, 100, "A2") != p
    assert _run_prefix({**c, "MAX_RELATOR_LENGTH": 32}, 100, "A1") != p
    assert _run_prefix({**c, "BENCHMARK": "combined_22"}, 100, "A1") != p
    assert _run_prefix({**c, "CYCLIC_REDUCE": False}, 100, "A1") != p
    # ...and job-selection / result-neutral knobs do not (resume is row-keyed)
    assert _run_prefix({**c, "ROW_LIMIT": 3, "WORD_LIMIT": 1, "USE_WANDB": True,
                        "NAMES": ["ms499"], "PROGRESS_EVERY": 1}, 100, "A1") == p


# -- paths file -----------------------------------------------------------------


def test_solved_paths_land_in_the_paths_file_moves_only(cfg, monkeypatch):
    _stub(monkeypatch)
    out = run_nocov(cfg, 100, "A1")
    prows = _rows(out[:-len(".jsonl")] + "_paths.jsonl")
    assert len(prows) == 4
    for p in prows:
        assert set(p) == {"name", "z_word", "r1", "r2", "z_relator",
                          "path_moves"}, "moves only — replay is the decoder"
        assert p["path_moves"] == STATS["path_moves"]
    keys = [(p["name"], p["z_word"]) for p in prows]
    assert len(keys) == len(set(keys))


def test_unsolved_jobs_write_no_path_row(cfg, monkeypatch):
    unsolved = {**STATS, "solved": False, "path_length": None,
                "path_moves": [], "path": [], "path_words": []}
    _stub(monkeypatch, unsolved)
    out = run_nocov(cfg, 100, "A1")
    assert _rows(out[:-len(".jsonl")] + "_paths.jsonl") == []


# -- config yaml ------------------------------------------------------------


def test_config_yaml_round_trips_with_default_config():
    with open(YAML_PATH) as f:
        y = yaml.safe_load(f)
    assert set(DEFAULT_CONFIG) | {"BUDGET"} <= set(y)
    assert y["MAX_RELATOR_LENGTH"] == 64
    assert set(y["FAMILIES"]) <= {"A1", "A2", "A3"}
    assert y["MODE"] == "nocov"
    assert isinstance(y["BUDGET"], list)
    assert all(isinstance(b, int) for b in y["BUDGET"])
    # values match DEFAULT_CONFIG except the documented production deltas,
    # each pinned explicitly below so a yaml change stays a conscious act
    deltas = ("MOUNT_DRIVE", "USE_WANDB", "BENCHMARK", "FAMILIES",
              "A2_MAX_WORDS", "A2_DROP_LEN1")
    for k in DEFAULT_CONFIG:
        if k in deltas:
            continue
        assert y[k] == DEFAULT_CONFIG[k], f"{k}: yaml {y[k]!r} != default"
    assert y["MOUNT_DRIVE"] is True
    assert y["USE_WANDB"] is True
    assert y["BUDGET"] == [10000]
    # the combined_66 production run: full benchmark, A2 capped (11,648
    # uncapped words -> 13,744 jobs is ~2x the intended sweep), cheap
    # families ordered first so A1/A3 complete before A2 starts
    assert y["BENCHMARK"] == "combined_66"
    assert y["FAMILIES"] == ["A1", "A3", "A2"]
    assert y["A2_MAX_WORDS"] == 64
    # A1 runs the singles on every row; dropping them from A2 removes the
    # systematic cross-family duplicates and improves the capped selection
    assert y["A2_DROP_LEN1"] is True


# -- big-budget guard ---------------------------------------------------------


def test_main_refuses_big_budgets_without_the_env(monkeypatch):
    monkeypatch.delenv("ACSOLVERX_ALLOW_BIG", raising=False)

    def explode(*a, **k):
        raise AssertionError("no sweep may start under a refused budget")

    monkeypatch.setattr(rn, "run_nocov", explode)
    with pytest.raises(SystemExit):
        main()                       # the real yaml carries BUDGET [50000]


def test_run_nocov_itself_refuses_a_big_budget(cfg, monkeypatch):
    """The notebook calls run_nocov directly, so the guard must live there too."""
    monkeypatch.delenv("ACSOLVERX_ALLOW_BIG", raising=False)
    _stub(monkeypatch)
    with pytest.raises(SystemExit):
        run_nocov(cfg, 5000, "A1")


def test_small_budgets_need_no_env(monkeypatch):
    monkeypatch.delenv("ACSOLVERX_ALLOW_BIG", raising=False)
    _require_budget_allowed([100, 1000])     # must not raise


# -- the one real end-to-end micro-run ----------------------------------------


def test_end_to_end_micro_run_and_replay(tmp_path):
    """No monkeypatch: real searches at budget 100 on the easiest ladder row,
    then the stored moves are replayed to a state where every relator is a
    single generator (the trivial <x,y,z> presentation)."""
    cfg = {**DEFAULT_CONFIG, "LOCAL_OUT_DIR": str(tmp_path / "out"),
           "NAMES": ["ms499"], "WORD_LIMIT": 2, "USE_WANDB": False}
    out = run_nocov(cfg, 100, "A1")
    rows = _rows(out)
    assert len(rows) == 2
    prows = {(p["name"], p["z_word"]): p
             for p in _rows(out[:-len(".jsonl")] + "_paths.jsonl")}
    for r in rows:
        assert isinstance(r["solved"], bool)
        assert r["nodes_explored"] <= 100
        if r["solved"]:
            p = prows[(r["name"], r["z_word"])]
            start = [str_to_word(r["r1"]), str_to_word(r["r2"]),
                     str_to_word(p["z_relator"])]
            states = moves_to_states(start, p["path_moves"], cyclic=True)
            assert all(len(rel) == 1 for rel in states[-1])
    assert any(r["solved"] for r in rows), "ms499 z=x solves in ~7 nodes"
