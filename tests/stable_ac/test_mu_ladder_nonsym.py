"""Budget-capped pins for non-automorphic best-first CoV ladder (REVISE form)."""
from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from experiments.stable_ac.cov.ladder import mu_ladder_nonsym as ml  # noqa: E402


def test_hop_nonsym_provenance_and_autmin():
    # Parent must already be Aut-min for hop_nonsym contract.
    mu, parent = ml.orbit_fast(("YYXyx", "Yx"))
    hops = ml.hop_nonsym(parent[0], parent[1], cap=24)
    for h in hops:
        assert h["n_subs"] > 1
        assert h["rep"] == list(ml.orbit_fast(h["concrete_pair"])[1])
        assert set(h) >= {
            "parent_pair", "z", "iso_gen", "iso_index", "n_subs",
            "concrete_pair", "mu", "rep"}
        assert h["parent_pair"] == list(parent)


def test_climb_best_first_autmin_visited():
    out = ml.climb_nonsym("YYXyx", "Yx", max_expand=8, cap=24, stop_mu=2)
    assert out["start_autmin"] == list(ml.orbit_fast(("YYXyx", "Yx"))[1])
    assert out["best_mu"] <= out["mu_in"]
    mu, rep = ml.orbit_fast(tuple(out["best_rep"]))
    assert list(rep) == out["best_rep"] and mu == out["best_mu"]
    # provenance present on every hop in the best chain
    for h in out["best_chain_hops"]:
        assert h["n_subs"] > 1
        assert set(h) >= {
            "parent_pair", "z", "iso_gen", "iso_index", "n_subs",
            "concrete_pair", "mu", "rep"}


def test_alpha_rescore():
    # solved at 100 nodes, 20 aut_canon calls
    ok0, rem0, _ = ml.solved_at_alpha(True, 100, 20, alpha=0)
    assert ok0 and rem0 == 1000
    ok33, rem33, spent = ml.solved_at_alpha(True, 100, 20, alpha=33)
    # spent = 660, B_rem = 340 ≥ 100 → still solved
    assert ok33 and rem33 == 340
    ok_big, rem_big, _ = ml.solved_at_alpha(True, 100, 20, alpha=50)
    # spent = 1000, B_rem = 0 < 100 → fail
    assert not ok_big and rem_big == 0


def test_control_csv_and_heur_arm():
    from experiments.heuristic_search.runners import run_bench60_covbeam_b1k as rb
    ctrl = rb.load_control()
    assert len(ctrl) == 60
    n_g = sum(1 for r in ctrl.values() if r["b1k_greedy_solved"])
    n_h = sum(1 for r in ctrl.values() if r["b1k_heur_solved"])
    assert n_g == 29 and n_h == 43
