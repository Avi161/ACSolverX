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
from experiments.equivalence_classes.lib.words import (
    apply_hom, canon_pair, free_reduce, inv,
)
from experiments.search import transport_ac19_orig as tr
from experiments.search.ac_decode import (
    decode_elementary, replay_elementary, to_conjugator,
)
from experiments.search.decode_ac_jsonl import replay_packed
from experiments.search.run_leftovers_1m import read_rows

# Step counts of the shipped paths. Asserted so a regression cannot pass by
# quietly checking fewer rows.
STEPS = {"greedy": 2_211, "s20_mk2": 1_069}


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


def _equivariant_steps(rec):
    """``(matching, total)`` steps of one path under its own ``aut_canon`` phi.

    The identity being checked is the content of the theorem: applying the SAME
    move -- same target, same sign, conjugator word carried through phi -- to
    phi of a state gives phi of the next state.

    The move must be applied in the pair's OWN order, with no canonicalization
    between steps. Canonicalizing mid-check can swap the two relators, after
    which ``target`` addresses the wrong one and a correct transport reads as a
    failure (it scored 7 of 23 on the first row that way).
    """
    _, _, phi = aut_canon((rec["r1"], rec["r2"]))
    states, moves = rec["path"], rec["path_moves"]
    ok = 0
    for index, move in enumerate(moves):
        current, nxt = tuple(states[index]), tuple(states[index + 1])
        target, sign, conjugator = to_conjugator(
            current, tuple(int(v) for v in move.split("_")))
        pair = [apply_hom(current[0], phi), apply_hom(current[1], phi)]
        other = pair[2 - target]
        oriented = other if sign == 1 else inv(other)
        moved = apply_hom(conjugator, phi)
        pair[target - 1] = free_reduce(
            pair[target - 1] + inv(moved) + oriented + moved)
        ok += canon_pair(*pair) == canon_pair(apply_hom(nxt[0], phi),
                                              apply_hom(nxt[1], phi))
    return ok, len(moves)


@pytest.mark.parametrize("arm", sorted(tr.SOURCE))
def test_every_step_is_equivariant(arm):
    """phi(move(S)) == move_phi(phi(S)) on every step of every shipped path."""
    ok = total = 0
    for rec in _source(arm):
        a, b = _equivariant_steps(rec)
        ok += a
        total += b
    assert total == STEPS[arm], f"{arm}: {total} steps, expected {STEPS[arm]}"
    assert ok == total, f"{arm}: only {ok} of {total} steps are equivariant"


def test_the_check_would_fail_on_an_untranslated_conjugator():
    """The equivariance test has to be able to fail, or it proves nothing.

    Leaving the conjugator in the ORIGINAL basis instead of carrying it through
    phi is the exact mistake the theorem rules out; it must not pass.
    """
    rec = _source("greedy")[0]
    _, _, phi = aut_canon((rec["r1"], rec["r2"]))
    states, moves = rec["path"], rec["path_moves"]
    ok = 0
    for index, move in enumerate(moves):
        current, nxt = tuple(states[index]), tuple(states[index + 1])
        target, sign, conjugator = to_conjugator(
            current, tuple(int(v) for v in move.split("_")))
        pair = [apply_hom(current[0], phi), apply_hom(current[1], phi)]
        other = pair[2 - target]
        oriented = other if sign == 1 else inv(other)
        pair[target - 1] = free_reduce(          # conjugator NOT transported
            pair[target - 1] + inv(conjugator) + oriented + conjugator)
        ok += canon_pair(*pair) == canon_pair(apply_hom(nxt[0], phi),
                                              apply_hom(nxt[1], phi))
    assert ok < len(moves), "untranslated conjugators must not reproduce the path"


def test_the_tail_is_never_empty_and_never_long():
    """phi of a terminal pair is a basis, so a tail is always needed."""
    tails = [r["tail_moves"] for arm in tr.SOURCE for r in _shipped(arm)]
    assert len(tails) == 58
    assert min(tails) >= 1 and max(tails) <= 4
