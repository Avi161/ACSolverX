"""Pins for rung-local nonsym CoV beam (user algorithm)."""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from experiments.stable_ac.cov.ladder.mu_ladder_nonsym_beam import (  # noqa: E402
    climb_beam,
)
from experiments.stable_ac.cov.ladder.mu_ladder_nonsym import orbit_fast  # noqa: E402


def test_beam_keeps_at_most_k_and_autmin():
    out = climb_beam("YYXyx", "Yx", beam_k=2, rungs=4, cap=24, stop_mu=2)
    assert out["beam_k"] == 2
    assert out["best_mu"] <= out["mu_in"]
    mu, rep = orbit_fast(tuple(out["best_rep"]))
    assert list(rep) == out["best_rep"] and mu == out["best_mu"]
    for h in out["best_chain_hops"]:
        assert h["n_subs"] > 1


def test_beam_k1_runs():
    out = climb_beam("YYXyx", "YXyXXyxx", beam_k=1, rungs=3, cap=24,
                     stop_mu=12, max_aut_canon=200)
    assert out["n_orbits_seen"] >= 1
    assert out["cost"]["n_aut_canon"] <= 200 or out["stopped_reason"] == "max_aut_canon"


def test_already_below_stop():
    # Short presentation: Aut-min μ often small.
    out = climb_beam("Yx", "Xy", beam_k=4, rungs=2, stop_mu=12)
    assert out["best_mu"] <= 12
    assert out["hits_stop"] is True


def test_global_visited_blocks_return_to_start():
    """Aut-min start stays in ``seen`` for the whole climb — multi-hop
    cannot re-admit the initial orbit (not just one-hop parent≠child)."""
    out = climb_beam("YYYXyyx", "YYXyyXyx", beam_k=4, rungs=8, cap=24,
                     stop_mu=12, max_aut_canon=400)
    start = tuple(out["start_autmin"])
    # Every hop in every recorded chain lands on a *new* Aut-min vs parent,
    # and the start orbit itself is never a later hop target.
    for h in out["best_chain_hops"]:
        assert tuple(h["rep"]) != start
        assert tuple(h["rep"]) != tuple(h["parent_pair"])
    # n_orbits_seen counts start + every newly admitted Aut-min.
    assert out["n_orbits_seen"] >= 1 + len(out["best_chain_hops"])
