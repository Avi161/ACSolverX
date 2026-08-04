"""Budget-capped pins for non-automorphic CoV beam (Aut-min after every hop)."""
from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from experiments.stable_ac.cov.ladder import mu_ladder_nonsym as ml  # noqa: E402


def test_hop_returns_autmin_pairs_only():
    # AK(2)-ish short pair from ms640 easy end
    hops = ml.hop_nonsym("YYXyx", "Yx", cap=24)
    for rep, (mu, pair, z, ig, ii, ns) in hops.items():
        assert ns > 1
        assert pair == rep
        mu2, rep2 = ml.orbit(pair)
        assert rep2 == rep and mu2 == mu


def test_climb_start_is_autmin_and_seen_grows():
    out = ml.climb_nonsym("YYXyx", "Yx", rungs=3, beam_k=4, cap=24,
                          stop_mu=2, cost_budget_ms=60_000)
    assert out["start_autmin"] == list(ml.orbit(("YYXyx", "Yx"))[1])
    assert out["n_orbits_seen"] >= 1
    assert out["best_mu"] <= out["mu_in"]
    # best_rep is Aut-min
    mu, rep = ml.orbit(tuple(out["best_rep"]))
    assert list(rep) == out["best_rep"] and mu == out["best_mu"]


def test_remaining_budget():
    rem, spent = ml.remaining_budget(500.0, 1.0, total_nodes=1000)
    assert rem == 500 and spent == 500
    rem, spent = ml.remaining_budget(5000.0, 1.0, total_nodes=1000)
    assert rem == 0 and spent == 1000


def test_control_csv_exists():
    from experiments.heuristic_search.runners import run_bench60_covbeam_b1k as rb
    ctrl = rb.load_control()
    assert len(ctrl) == 60
    assert "0" in ctrl and ctrl["0"]["b1k_greedy_nodes"] is not None
