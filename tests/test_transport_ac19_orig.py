"""Transporting an original's certificate onto its representative.

The claim is algebraic -- AC moves are ``Aut(F2)``-equivariant, so the
original's path carries over move for move and a Nielsen tail finishes it --
and every certificate is replayed from the representative's own words by
``replay_elementary``, which trusts nothing. These tests hold the shipped
rows to that, and the module to its own conventions.
"""
import json
import os

import pytest

from experiments.equivalence_classes.lib.autcanon import aut_canon
from experiments.equivalence_classes.lib.words import canon_pair
from experiments.search import transport_ac19_orig as tr
from experiments.search.ac_decode import decode_elementary, replay_elementary
from experiments.search.decode_ac_jsonl import replay_packed
from experiments.search.run_leftovers_1m import read_rows


def _source(arm):
    rows = read_rows(os.path.join(tr.OUT_DIR, tr.SOURCE[arm]))
    if not rows:
        pytest.skip(f"no {arm} records on disk")
    return rows


def _shipped(arm):
    rows = read_rows(os.path.join(tr.OUT_DIR, tr.OUT[arm]))
    if not rows:
        pytest.skip(f"no transported {arm} rows on disk")
    return rows


def test_identity_transport_is_the_plain_decode():
    r = _source("greedy")[0]
    steps = [{"kind": "substitution", "move": m} for m in r["path_moves"]]
    plain = decode_elementary((r["r1"], r["r2"]), r["path"], steps)
    moved, info = tr.transport((r["r1"], r["r2"]), r["path"], r["path_moves"],
                               {"x": "x", "y": "y"})
    assert info["rep"] == list(canon_pair(r["r1"], r["r2"]))
    assert info["tail_moves"] == 0 and info["rep_moves"] == r["path_length"]
    assert replay_elementary((r["r1"], r["r2"]), moved) == ["x", "y"]
    assert len(moved) == len(plain)


def test_transport_lands_on_the_orbit_representative_and_replays():
    r = _source("greedy")[0]
    _, rep, phi = aut_canon((r["r1"], r["r2"]))
    moves, info = tr.transport((r["r1"], r["r2"]), r["path"], r["path_moves"], phi)
    assert tuple(info["rep"]) == tuple(rep)
    assert info["rep_moves"] == r["path_length"] + info["tail_moves"]
    assert info["elementary"] == len(moves)
    assert replay_elementary(rep, moves) == ["x", "y"]


@pytest.mark.parametrize("arm", sorted(tr.SOURCE))
def test_every_shipped_certificate_replays_from_the_representative(arm):
    rows = _shipped(arm)
    for r in rows:
        assert r["replayed"] is True
        assert r["rep_moves"] == r["orig_moves"] + r["tail_moves"]
        assert len(r["certificate"]) == r["elementary"]
        assert replay_packed((r["rep_r1"], r["rep_r2"]), r["certificate"]) == ["x", "y"]


def test_shipped_rows_cover_every_original_once():
    for arm, n in (("greedy", 40), ("s20_mk2", 18)):
        rows = _shipped(arm)
        assert len(rows) == n
        assert len({r["name"] for r in rows}) == n
        assert all(r["orig_moves"] == s["path_length"]
                   for r, s in zip(sorted(rows, key=lambda r: r["name"]),
                                   sorted(_source(arm), key=lambda r: r["name"])))


def test_per_orbit_picks_the_shortest_over_arms_and_originals():
    rows = {"a": [{"orbit": "ac19_2", "rep_r1": "x", "rep_r2": "y", "name": "p",
                   "rep_moves": 5, "elementary": 50, "orig_moves": 4, "tail_moves": 1},
                  {"orbit": "ac19_1", "rep_r1": "x", "rep_r2": "y", "name": "q",
                   "rep_moves": 9, "elementary": 90, "orig_moves": 8, "tail_moves": 1}],
            "b": [{"orbit": "ac19_2", "rep_r1": "x", "rep_r2": "y", "name": "r",
                   "rep_moves": 5, "elementary": 40, "orig_moves": 3, "tail_moves": 2}]}
    best = tr.per_orbit(rows)
    assert [b["orbit"] for b in best] == ["ac19_1", "ac19_2"]
    assert best[1]["via"] == "r" and best[1]["arm"] == "b"


def test_twenty_eight_orbits_all_carry_a_certificate():
    best = tr.per_orbit({arm: _shipped(arm) for arm in tr.SOURCE})
    assert len(best) == 28
    assert all(1 <= b["tail_moves"] <= 4 for b in best)
