import csv
import os

import numpy as np

from experiments.heuristic_search.core.hcompact import HCompactSolver, _decode_stored_move
from experiments.heuristic_search.core.hcompact import greedy_search_hcompact
from experiments.search.greedy_baseline import moves_to_states, str_to_move
from experiments.search.heuristics import S20_MK2
from experiments.search.hybrid_10m import (
    MACRO_CAP, PREFIX_BUDGET, SEARCH_CAP, run_hybrid_10m,
)
from experiments.search.run_ac19_hybrid_10m import (
    ARM, BUDGET, CAMPAIGN, CAP, STATES_PER_NODE,
)
from experiments.search.run_leftovers_5m import (
    ENGINE_MEM_GEN, campaign_spec, plan_memory, resolve_campaign,
)


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(
    ROOT, "results", "heuristic_search", "ac19_hybrid_10m",
    "joint_survivors.csv")


def test_campaign_is_the_exact_three_joint_survivors():
    rows = list(csv.DictReader(open(CSV)))
    assert [r["name"] for r in rows] == [
        "ac19_44381", "ac19_51034", "ac19_65753"]
    prior = os.path.join(
        ROOT, "results", "heuristic_search", "ac19_10m",
        "ac19_10m_s20_mk2_b10000000_mrl64.jsonl")
    failed = {r.split('"name": "', 1)[1].split('"', 1)[0]
              for r in open(prior) if '"solved": false' in r}
    assert {r["name"] for r in rows} <= failed


def test_campaign_parameters_are_pinned():
    _, c = resolve_campaign(CAMPAIGN)
    spec = campaign_spec(CAMPAIGN, ARM)
    assert (BUDGET, CAP, STATES_PER_NODE) == (10_000_000, 255, 214)
    assert c["budget"] == BUDGET and c["mrl"] == CAP
    assert c["states_per_node"] == STATES_PER_NODE
    assert c["track_path"] is True and c["floor"] is None
    assert spec["n_rows"] == 3 and spec["chunks"] == 1
    assert SEARCH_CAP == CAP and MACRO_CAP is None
    assert ENGINE_MEM_GEN == 6


def test_wrapper_charges_prefix_and_restarts_compact_fallback():
    row = next(csv.DictReader(open(CSV)))
    got = run_hybrid_10m(
        row["r1"], row["r2"], PREFIX_BUDGET + 1, CAP,
        reserve_states=300_000, track_path=False)
    assert got["nodes_explored"] == PREFIX_BUDGET + 1
    assert got["hybrid_prefix_nodes"] == PREFIX_BUDGET
    assert got["hybrid_fallback_nodes"] == 1
    assert [a["component"] for a in got["hybrid_prefix_attempts"]] == [
        "normalization", "rewrite", "s40_gen"]


def test_explicit_reservation_is_exact_and_int32_guarded(monkeypatch):
    seen = []
    monkeypatch.setattr(HCompactSolver, "_alloc", lambda self, n, old=None: seen.append(n))
    HCompactSolver("x", "y", reserve_states=12_345)
    assert seen == [12_345]
    with np.testing.assert_raises_regex(MemoryError, "signed int32"):
        HCompactSolver("x", "y", reserve_states=2**31)


def test_compact_solver_refuses_an_input_beyond_its_semantic_cap():
    with np.testing.assert_raises_regex(ValueError, "exceeds"):
        HCompactSolver("x" * 256, "y", max_relator_length=255,
                       reserve_states=300_000)


def test_planner_never_returns_an_unrepresentable_state_count():
    _, reserve = plan_memory(
        BUDGET, CAP, available_gb=10_000, states_per_node=10_000,
        track_path=False, log=lambda _: None)
    assert reserve == 2**31 - 1


def test_cap_255_cut_positions_round_trip_through_path_storage():
    stored = np.array([1, -1, -128, -1], dtype=np.int8)
    assert _decode_stored_move(stored) == (1, -1, 128, 255)


def test_cap_255_capture_produces_a_replayable_path():
    pair = ("YYXyx", "Yx")
    got = greedy_search_hcompact(
        *pair, 30, max_relator_length=CAP, config=S20_MK2,
        track_path=True, reserve_states=300_000)
    replay = moves_to_states(
        *pair, [str_to_move(m) for m in got["path_moves"]])
    assert got["solved"] and replay == got["path"]


def test_worker_fails_closed_when_address_limit_cannot_be_installed(monkeypatch):
    import resource
    from experiments.search.run_leftovers_5m import _child_run_row

    monkeypatch.setattr(resource, "setrlimit", lambda *args: (_ for _ in ()).throw(
        ValueError("unsupported")))

    class Queue:
        messages = []

        def put(self, value):
            self.messages.append(value)

    q = Queue()
    _child_run_row(q, ARM, {"name": "row", "r1": "x", "r2": "y"},
                   2_000, CAP, 60, 1, 300_000, False)
    assert q.messages == [("err", "cannot enforce worker address-space limit: unsupported")]


def test_certificate_sizing_honors_the_campaign_override(monkeypatch, tmp_path):
    import experiments.search.run_ac19_hybrid_10m as runner

    monkeypatch.setenv("STATES_PER_NODE", "236")
    monkeypatch.setattr(runner, "read_rows", lambda path: [])
    seen = []
    monkeypatch.setattr(runner, "_floor_for", lambda campaign, log=print: seen.append(
        int(os.environ["STATES_PER_NODE"])) or int(os.environ["STATES_PER_NODE"]))
    runner.certify(str(tmp_path), log=lambda _: None)
    assert seen == [236]


def test_run_command_finishes_with_certificate_recovery(monkeypatch, tmp_path):
    import experiments.search.run_ac19_hybrid_10m as runner

    calls = []
    monkeypatch.setattr(runner, "run", lambda *a, **k: calls.append("run"))
    monkeypatch.setattr(runner, "report", lambda *a, **k: calls.append("report"))
    monkeypatch.setattr(runner, "certify", lambda *a, **k: calls.append("certify") or "certs")
    runner.main(["run", "--out-dir", str(tmp_path), "--workers", "1"])
    assert calls == ["run", "report", "certify"]


def test_captured_solution_is_verified_without_a_search_rerun(monkeypatch, tmp_path):
    import json
    import experiments.search.run_ac19_hybrid_10m as runner

    source = {"name": "toy", "r1": "x", "r2": "y", "solved": True,
              "nodes_explored": 1, "path": [["Y", "X"]], "path_moves": []}
    monkeypatch.setattr(runner, "read_rows", lambda path: [source] if
                        path.endswith("_b10000000_mrl255.jsonl") else [])
    monkeypatch.setattr(runner, "load_rows_5m", lambda *a, **k: ([{
        "name": "toy", "r1": "x", "r2": "y"}], "toy.csv"))
    monkeypatch.setattr(runner, "_run_row_isolated", lambda *a, **k: (_ for _ in ()).throw(
        AssertionError("captured paths must not rerun the search")))
    target = runner.certify(str(tmp_path), log=lambda _: None)
    saved = json.loads(open(target).read())
    assert saved["certified"] is True and saved["path"] == [["Y", "X"]]
