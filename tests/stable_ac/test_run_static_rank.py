"""run_static_rank (Track T2) harness tests: pluralized row schema at rank 4 and
5, resume, torn-line repair, filename identity (rank + cap in, limits out), the
paths file, the config yaml, the big-budget guard, HIGH_SPEEDUP dispatch — plus
ONE real end-to-end micro-run (rank 4, budget 500) closed through the INDEPENDENT
``verify_static_rank`` certificate verifier (structural stabilization check +
spec replay to the trivial presentation), and a tamper test proving the verifier
is not vacuous.

Every stubbed test monkeypatches the search seam
(``run_static_rank.search_n`` / ``search_n_fast``): the presentation is still
built for real, so ``n_gen``/``n_rel`` and the adjoined ``z_relators`` are real;
only the search is replaced.
"""

import json
import os

import pytest
import yaml

import experiments.stable_ac.nocov.run_static_rank as rs
import experiments.stable_ac.verify_static_rank as V
from experiments.stable_ac.nocov.run_static_rank import (
    DEFAULT_CONFIG, _require_budget_allowed, _run_prefix, _z_key, main,
    run_static_rank,
)

YAML_PATH = os.path.join(os.path.dirname(rs.__file__), "config_static_rank.yaml")

# A valid search_n stats dict (n_rel=4 shapes; the harness only reads the dict).
STATS = {
    "solved": True, "nodes_explored": 8, "path_length": 7,
    "min_relator_length": 4, "min_relator": ["Z", "A", "Y", "X"],
    "max_relator_length": 30,
    "max_relator": ["YYYYx", "ZyyyxYYY", "Axyy", "YYYYYYYXyyyyyyx"],
    "max_relator_length_expanded": 20,
    "max_relator_expanded": ["YYYYx", "Zx", "Ay", "YYYYYYYXyyyyyyx"],
    "path": [], "path_words": [],
    "path_moves": ["3_2_-1_0_0", "3_0_-1_1_0"],
}

BASE_KEYS = {
    "name", "source", "pres_id", "r1", "r2", "base_total_length", "z_words",
    "z_relators", "rank", "w_family", "allow_chained", "mode", "n_gen", "n_rel",
    "benchmark", "node_budget", "max_relator_length_cap", "cyclic_reduce",
    "nodes_explored", "solved", "path_length", "min_relator_length",
    "min_relator", "max_relator_length", "max_relator",
    "max_relator_length_expanded", "max_relator_expanded", "time_seconds",
    "git_commit",
}
LADDER_KEYS = {"baseline_nodes_at_50k", "baseline_path_at_50k",
               "baseline_solved_at_50k", "nodes_1M", "path_1M"}


@pytest.fixture
def cfg(tmp_path):
    # NAMES=[ms499] selects one ladder row; WORDSET_LIMIT=2 -> 2 word-sets = 2 jobs.
    return {**DEFAULT_CONFIG, "LOCAL_OUT_DIR": str(tmp_path / "out"),
            "NAMES": ["ms499"], "WORDSET_LIMIT": 2, "USE_WANDB": False}


def _rows(path):
    with open(path) as f:
        return [json.loads(ln) for ln in f if ln.strip()]


def _stub(monkeypatch, stats=STATS):
    calls = []

    def spy(*a, **k):
        calls.append(a)
        return dict(stats)

    monkeypatch.setattr(rs, "search_n", spy)
    return calls


def _fast_stub(monkeypatch, stats=STATS):
    calls = []

    def spy(*a, **k):
        calls.append(a)
        return dict(stats)

    monkeypatch.setattr(rs, "search_n_fast", spy)
    return calls


# -- row schema ---------------------------------------------------------------


def test_rank4_rows_carry_the_full_schema(cfg, monkeypatch):
    _stub(monkeypatch)
    out = run_static_rank(cfg, 100, "A1", 4)
    rows = _rows(out)
    assert len(rows) == 2
    for r in rows:
        assert BASE_KEYS <= set(r), BASE_KEYS - set(r)
        assert r["mode"] == "static_rank"
        assert r["rank"] == 4
        assert (r["n_gen"], r["n_rel"]) == (4, 4)
        # rank 4 adjoins z then a (GEN_CHARS "xyz"+"abc..."): Z. then A.
        assert len(r["z_words"]) == 2 and len(r["z_relators"]) == 2
        assert r["z_relators"][0] == "Z" + r["z_words"][0]
        assert r["z_relators"][1] == "A" + r["z_words"][1]
        assert r["allow_chained"] is False
        assert r["benchmark"] == "combined_11"
        assert r["node_budget"] == 100
        assert r["max_relator_length_cap"] == 64
        assert r["cyclic_reduce"] is True
        assert r["git_commit"] is None or (
            len(r["git_commit"]) == 40
            and all(c in "0123456789abcdef" for c in r["git_commit"]))
        assert isinstance(r["time_seconds"], float)
    # ms499 is a ladder row -> baseline passthrough + a pres_id
    for r in rows:
        assert r["source"] == "ladder"
        assert LADDER_KEYS <= set(r), LADDER_KEYS - set(r)
        assert r["pres_id"] is not None


def test_rank5_adjoins_z_a_b(cfg, monkeypatch):
    _stub(monkeypatch)
    out = run_static_rank({**cfg, "WORDSET_LIMIT": 1}, 100, "A1", 5)
    rows = _rows(out)
    assert len(rows) == 1
    r = rows[0]
    assert r["rank"] == 5
    assert (r["n_gen"], r["n_rel"]) == (5, 5)
    assert len(r["z_words"]) == 3 and len(r["z_relators"]) == 3
    for ch, w, zrel in zip("ZAB", r["z_words"], r["z_relators"]):
        assert zrel == ch + w         # z->Z, a->A, b->B, per GEN_CHARS


# -- resume -------------------------------------------------------------------


def test_resume_skips_done_jobs(cfg, monkeypatch):
    calls = _stub(monkeypatch)
    out1 = run_static_rank(cfg, 100, "A1", 4)
    assert len(calls) == 2
    out2 = run_static_rank(cfg, 100, "A1", 4)
    assert out2 == out1, "must resume into the same file, not start a new one"
    assert len(calls) == 2, "the second run must search nothing"
    assert len(_rows(out1)) == 2


def test_a_torn_trailing_line_is_repaired_and_re_run(cfg, monkeypatch):
    calls = _stub(monkeypatch)
    out = run_static_rank(cfg, 100, "A1", 4)
    with open(out) as f:
        lines = f.readlines()
    torn = json.loads(lines[-1])
    torn_key = (torn["name"], _z_key(torn["z_words"]))
    with open(out, "w") as f:
        f.writelines(lines[:-1])
        f.write(lines[-1][: len(lines[-1]) // 2])
    calls.clear()

    run_static_rank(cfg, 100, "A1", 4)

    rows = _rows(out)                # raises if any line was left corrupted
    keys = [(r["name"], _z_key(r["z_words"])) for r in rows]
    assert len(keys) == len(set(keys)), f"duplicate rows: {keys}"
    assert len(rows) == 2
    assert len(calls) == 1, "exactly the torn job re-runs"
    assert torn_key in keys
    with open(out) as f:
        assert f.readlines()[-1].endswith("\n")


def test_resume_reattaches_to_an_old_dated_file(cfg, monkeypatch):
    """The date suffix must never gate resume (date-in-filename-broke-resume)."""
    calls = _stub(monkeypatch)
    out = run_static_rank(cfg, 100, "A1", 4)
    prefix = _run_prefix(cfg, 100, "A1", 4)
    old = os.path.join(os.path.dirname(out), prefix + "01_01_20.jsonl")
    os.rename(out, old)
    paths = out[:-len(".jsonl")] + "_paths.jsonl"
    os.rename(paths, old[:-len(".jsonl")] + "_paths.jsonl")
    calls.clear()

    out2 = run_static_rank(cfg, 100, "A1", 4)

    assert out2 == old, "must continue the old-dated file, not start a new one"
    assert not calls
    assert len(_rows(old)) == 2


# -- filename identity --------------------------------------------------------


def test_prefix_encodes_identity_not_date():
    c = dict(DEFAULT_CONFIG)
    p = _run_prefix(c, 100, "A1", 4)
    assert p == "staticrank_combined_11_A1_r4_100_mrl64_cyc_"
    # every search-identity knob changes the prefix (rank + cap included)...
    assert _run_prefix(c, 200, "A1", 4) != p
    assert _run_prefix(c, 100, "A2", 4) != p
    assert _run_prefix(c, 100, "A1", 5) != p            # rank in
    assert _run_prefix({**c, "MAX_RELATOR_LENGTH": 32}, 100, "A1", 4) != p  # cap in
    assert _run_prefix({**c, "BENCHMARK": "combined_22"}, 100, "A1", 4) != p
    assert _run_prefix({**c, "CYCLIC_REDUCE": False}, 100, "A1", 4) != p
    # ...and job-selection / limit / result-neutral knobs do NOT (resume is
    # row-keyed; HIGH_SPEEDUP and ALLOW_CHAINED are result-neutral with A1/A2)
    assert _run_prefix({**c, "ROW_LIMIT": 3, "WORDSET_LIMIT": 1, "PAIR_LIMIT": 5,
                        "TRIPLE_LIMIT": 5, "ALLOW_CHAINED_WORDS": True,
                        "HIGH_SPEEDUP": True, "USE_WANDB": True,
                        "NAMES": ["ms499"], "PROGRESS_EVERY": 1},
                       100, "A1", 4) == p


# -- paths file ---------------------------------------------------------------


def test_solved_paths_land_in_the_paths_file_moves_only(cfg, monkeypatch):
    _stub(monkeypatch)
    out = run_static_rank(cfg, 100, "A1", 4)
    prows = _rows(out[:-len(".jsonl")] + "_paths.jsonl")
    assert len(prows) == 2
    for p in prows:
        assert set(p) == {"name", "z_words", "r1", "r2", "z_relators",
                          "path_moves"}, "moves only — replay is the decoder"
        assert p["path_moves"] == STATS["path_moves"]
        assert isinstance(p["z_words"], list) and isinstance(p["z_relators"], list)
    keys = [(p["name"], _z_key(p["z_words"])) for p in prows]
    assert len(keys) == len(set(keys))


def test_unsolved_jobs_write_no_path_row(cfg, monkeypatch):
    unsolved = {**STATS, "solved": False, "path_length": None,
                "path_moves": [], "path": [], "path_words": []}
    _stub(monkeypatch, unsolved)
    out = run_static_rank(cfg, 100, "A1", 4)
    assert _rows(out[:-len(".jsonl")] + "_paths.jsonl") == []


# -- config yaml --------------------------------------------------------------


def test_config_yaml_round_trips_with_default_config():
    with open(YAML_PATH) as f:
        y = yaml.safe_load(f)
    assert set(DEFAULT_CONFIG) | {"BUDGET"} <= set(y)
    assert y["MODE"] == "static_rank"
    assert y["MAX_RELATOR_LENGTH"] == 64
    assert set(y["FAMILIES"]) <= {"A1", "A2"}
    assert y["RANKS"] == [4, 5]
    assert isinstance(y["BUDGET"], list)
    assert all(isinstance(b, int) for b in y["BUDGET"])
    # values match DEFAULT_CONFIG except the documented production deltas
    deltas = ("MOUNT_DRIVE", "USE_WANDB", "HIGH_SPEEDUP")
    for k in DEFAULT_CONFIG:
        if k in deltas:
            continue
        assert y[k] == DEFAULT_CONFIG[k], f"{k}: yaml {y[k]!r} != default"
    assert y["MOUNT_DRIVE"] is True
    assert y["USE_WANDB"] is True
    assert y["HIGH_SPEEDUP"] is True
    assert y["BUDGET"] == [10000]


# -- HIGH_SPEEDUP dispatch ----------------------------------------------------


def test_high_speedup_dispatches_to_the_fast_solver(cfg, monkeypatch):
    slow_calls = _stub(monkeypatch)
    fast_calls = _fast_stub(monkeypatch)
    run_static_rank({**cfg, "HIGH_SPEEDUP": True}, 100, "A1", 4)
    assert len(fast_calls) == 2
    assert not slow_calls, "fast mode must never fall through to search_n"


def test_high_speedup_off_never_calls_the_fast_solver(cfg, monkeypatch):
    slow_calls = _stub(monkeypatch)
    fast_calls = _fast_stub(monkeypatch)
    run_static_rank(cfg, 100, "A1", 4)
    assert len(slow_calls) == 2 and not fast_calls


# -- big-budget guard ---------------------------------------------------------


def test_main_refuses_big_budgets_without_the_env(monkeypatch):
    monkeypatch.delenv("ACSOLVERX_ALLOW_BIG", raising=False)

    def explode(*a, **k):
        raise AssertionError("no sweep may start under a refused budget")

    monkeypatch.setattr(rs, "run_static_rank", explode)
    with pytest.raises(SystemExit):
        main()                       # the real yaml carries BUDGET [10000]


def test_run_static_rank_itself_refuses_a_big_budget(cfg, monkeypatch):
    """The notebook calls run_static_rank directly, so the guard lives there too."""
    monkeypatch.delenv("ACSOLVERX_ALLOW_BIG", raising=False)
    _stub(monkeypatch)
    with pytest.raises(SystemExit):
        run_static_rank(cfg, 5000, "A1", 4)


def test_small_budgets_need_no_env(monkeypatch):
    monkeypatch.delenv("ACSOLVERX_ALLOW_BIG", raising=False)
    _require_budget_allowed([100, 1000])     # must not raise


# -- the one real end-to-end micro-run, closed through the verifier -----------


def test_end_to_end_micro_run_verifies(tmp_path):
    """No monkeypatch: real rank-4 searches on ms499 (two A1 words) at budget 500,
    then EVERY solved row's certificate is checked by the independent
    verify_static_rank (structural stabilization + spec replay to trivial)."""
    cfg = {**DEFAULT_CONFIG, "LOCAL_OUT_DIR": str(tmp_path / "out"),
           "NAMES": ["ms499"], "WORDSET_LIMIT": 3, "USE_WANDB": False}
    out = run_static_rank(cfg, 500, "A1", 4)
    rows = _rows(out)
    assert len(rows) == 3
    assert any(r["solved"] for r in rows), "ms499 rank-4 solves cheaply"
    for r in rows:
        assert r["nodes_explored"] <= 500
        assert (r["n_gen"], r["n_rel"]) == (4, 4)

    n_rows, n_solved, failures = V.verify_file(out)
    assert n_rows == 3
    assert n_solved >= 1
    assert failures == [], failures


def test_verifier_rejects_a_tampered_certificate(tmp_path):
    """Non-vacuity: a real solved row whose path is truncated (so the replay no
    longer reaches the trivial presentation) MUST fail the verifier, and a wrong
    z_relator MUST fail the structural check."""
    cfg = {**DEFAULT_CONFIG, "LOCAL_OUT_DIR": str(tmp_path / "out"),
           "NAMES": ["ms499"], "WORDSET_LIMIT": 1, "USE_WANDB": False}
    out = run_static_rank(cfg, 500, "A1", 4)
    row = next(r for r in _rows(out) if r["solved"])
    prow = _rows(out[:-len(".jsonl")] + "_paths.jsonl")[0]
    # sanity: the untampered certificate verifies
    V.verify_solved_row(row, prow["path_moves"], prow)

    # (b) truncate the path: the replay no longer reaches trivial
    short = prow["path_moves"][:-1]
    bad = {**row, "path_length": len(short)}
    with pytest.raises(V.CertificateError):
        V.verify_solved_row(bad, short, {**prow, "path_moves": short})

    # (a) corrupt the coupled relator so it no longer encodes z_words
    bad_struct = {**row, "z_relators": ["Zy"] + row["z_relators"][1:]}
    with pytest.raises(V.CertificateError):
        V.verify_solved_row(bad_struct, prow["path_moves"],
                            {**prow, "z_relators": ["Zy"] + prow["z_relators"][1:]})
