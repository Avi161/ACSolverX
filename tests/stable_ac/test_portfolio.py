"""Harness tests for the production portfolio runner (idea 12) and the
same-orbit re-seed strategy (idea 11). No real search above budget 100; the
search seam (``harness._search``) is stubbed everywhere except the strategy
enumeration itself, which runs no search by contract."""

import json
import os

import pytest

from experiments.equivalence_classes.lib.autcanon import aut_canon
from experiments.stable_ac.idea_bench import harness, run_portfolio
from experiments.stable_ac.idea_bench.strategies import reseed_orbit

AK3 = ("xxxYYYY", "xyxYXY")


def test_load_bench_aca_124_loads_all_rows():
    rows = harness.load_bench("aca_124")
    assert len(rows) == 124
    assert rows[0]["pres_id"] == "aca_0"
    assert all(r["r1"] and r["r2"] for r in rows)
    assert all(r["nodes_1M"] is None for r in rows)   # no known optimum: pure coverage


def test_reseed_orbit_candidates_are_same_orbit_deduped_ranked():
    cands = reseed_orbit.candidates(*AK3, 24)
    assert 0 < len(cands) <= 60
    # no identity, no duplicates
    from experiments.equivalence_classes.lib.words import canon_pair
    start = canon_pair(*AK3)
    pairs = [(a, b) for a, b, _ in cands]
    assert start not in pairs
    assert len(set(pairs)) == len(pairs)
    # per-candidate cap is at least the run cap
    assert all(c >= 24 for _, _, c in cands)
    # same Aut(F2)-orbit by construction — verify on a sample through aut_canon
    _, rep0, _ = aut_canon(start)
    for a, b in pairs[:4] + pairs[-2:]:
        _, rep, _ = aut_canon((a, b))
        assert rep == rep0, f"{(a, b)} left the orbit"
    # deterministic
    assert cands == reseed_orbit.candidates(*AK3, 24)


def test_budget_gate_refuses_big_budgets(monkeypatch, tmp_path):
    monkeypatch.delenv("ACSOLVERX_ALLOW_BIG", raising=False)
    with pytest.raises(SystemExit):
        run_portfolio.run_portfolio(budgets=(5000,), out_dir=str(tmp_path))


def test_unknown_strategy_refused(tmp_path):
    with pytest.raises(SystemExit):
        run_portfolio.run_portfolio(strategies=("no_such_strategy",),
                                    budgets=(50,), out_dir=str(tmp_path))


def _stub_search(monkeypatch):
    calls = []

    def fake(r1, r2, budget, cap):
        calls.append((r1, r2, budget, cap))
        return {"solved": False, "nodes_explored": 7, "path_length": None}

    monkeypatch.setattr(harness, "_search", fake)
    return calls


def test_per_budget_files_schema_resume_and_identity(monkeypatch, tmp_path):
    _stub_search(monkeypatch)
    written = run_portfolio.run_portfolio(
        bench="aca_124", strategies=("baseline",), group="g1",
        budgets=(50, 100), cap=24, jobs=1, row_limit=2, out_dir=str(tmp_path))
    # one file per budget, dateless identity names
    names = sorted(os.path.basename(p) for p in written)
    assert names == ["portfolio_aca_124_g1_100_mrl24.jsonl",
                     "portfolio_aca_124_g1_50_mrl24.jsonl"]
    rows = [json.loads(ln) for ln in open(written[0])]
    assert len(rows) == 2                        # 2 presentations x baseline
    r = rows[0]
    assert r["strategy"] == "baseline" and r["budget"] == 50
    assert r["cap"] == 24 and r["bench"] == "aca_124"
    assert r["pres_id"].startswith("aca_")
    assert r["solved"] is False and r["total_nodes"] == 7
    # resume: a second run adds nothing
    run_portfolio.run_portfolio(
        bench="aca_124", strategies=("baseline",), group="g1",
        budgets=(50, 100), cap=24, jobs=1, row_limit=2, out_dir=str(tmp_path))
    assert len(open(written[0]).readlines()) == 2
    assert len(open(written[1]).readlines()) == 2


def test_baseline_control_is_always_included(monkeypatch, tmp_path):
    _stub_search(monkeypatch)
    written = run_portfolio.run_portfolio(
        bench="aca_124", strategies=("reseed_orbit",), group="g2",
        budgets=(50,), cap=24, jobs=1, row_limit=1, out_dir=str(tmp_path))
    strategies = {json.loads(ln)["strategy"] for ln in open(written[0])}
    assert strategies == {"baseline", "reseed_orbit"}
