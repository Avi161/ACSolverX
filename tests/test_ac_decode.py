"""The decoder that turns an automorphism-assisted path into AC moves.

The claim under test is the one that makes the whole cascade result an AC
result: a path that changes basis is still an AC solve, and the moves can be
recovered. Everything here ends at the same place -- a move sequence replayed
from the original input through `moves_to_states`, landing on a terminal pair.
"""
import json
import os

import pytest

from experiments.equivalence_classes.lib.words import (
    apply_pair, canon_pair, SIGNED_PERMS,
)
from experiments.search import ac_decode
from experiments.search.ac_decode import (
    bridge, decode, elementary_inverse, find_move, is_terminal, push_back,
    reduce_basis,
)
from experiments.search.cascade_heuristics import search as cascade
from experiments.search.greedy_baseline import moves_to_states
from experiments.search.heuristic_1k import NIELSEN

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MS640 = os.path.join(ROOT, "data", "ms640_solved.txt")
SYM = {1: "x", -1: "X", 2: "y", -2: "Y"}


def _rows(limit=None):
    out = []
    with open(MS640) as fh:
        for line in fh:
            if not line.strip():
                continue
            v = json.loads(line)
            h = len(v) // 2
            out.append(("".join(SYM[t] for t in v[:h] if t),
                        "".join(SYM[t] for t in v[h:] if t)))
            if limit and len(out) >= limit:
                break
    return out


def _run(pair):
    return cascade(pair, budget=1000, cap=255, starter_budget=500,
                   rewrite_budget=1000, intermediate_cap=None)


# --- the algebra the decoder rests on --------------------------------------
def test_every_elementary_image_has_an_inverse_that_undoes_it():
    for image in ac_decode.ELEMENTARY:
        back = elementary_inverse(image)
        for pair in (("xyX", "yyx"), ("YYXyx", "Yx"), ("YXXyx", "YYYYYXyyyxyxxx")):
            moved = apply_pair(list(canon_pair(*pair)), image)
            assert list(apply_pair(list(moved), back)) == list(canon_pair(*pair))


def test_a_non_elementary_map_is_refused_rather_than_guessed():
    with pytest.raises(ValueError, match="not an elementary"):
        elementary_inverse({"x": "xyx", "y": "y"})


def test_the_elementary_set_is_the_four_nielsen_images_and_eight_signed_perms():
    assert len(ac_decode.ELEMENTARY) == 12
    assert set(map(str, NIELSEN)) <= set(map(str, ac_decode.ELEMENTARY))
    assert len(SIGNED_PERMS) == 8


# --- the move matcher ------------------------------------------------------
def test_find_move_recovers_a_move_the_search_enumeration_prunes():
    """r2 -> r1.r2 on ('Y','YX'). The seam does not cancel, so
    `get_neighbors_with_moves_nj` never emits it -- but it is an AC move."""
    move = find_move(("Y", "YX"), ("Y", "YYX"))
    assert move == (2, 1, 0, 0)
    assert list(moves_to_states("Y", "YX", [move])[-1]) == ["Y", "YYX"]


def test_find_move_returns_none_when_no_single_move_connects():
    assert find_move(("Y", "X"), ("YYYYYYY", "XXXXXXX")) is None


def test_every_move_find_move_returns_actually_replays():
    for source in (("Y", "YX"), ("YYXyx", "Yx"), ("xyX", "yyx")):
        for target in (("Y", "X"), ("X", "YX"), ("Y", "YYX")):
            move = find_move(source, target)
            if move is None:
                continue
            assert list(moves_to_states(source[0], source[1], [move])[-1]) \
                == list(target)


# --- the basis tail --------------------------------------------------------
def test_a_basis_reduces_to_a_terminal_pair_by_ac_moves():
    for basis in (("Y", "Yx"), ("Y", "YYX"), ("Y", "YYYYx"), ("X", "YX")):
        moves = reduce_basis(basis)
        assert moves is not None, basis
        assert is_terminal(tuple(moves_to_states(basis[0], basis[1], moves)[-1]))


def test_a_terminal_pair_needs_no_tail_at_all():
    assert reduce_basis(("Y", "X")) == []
    assert reduce_basis(("x", "y")) == []


def test_is_terminal_rejects_a_repeated_generator():
    assert not is_terminal(("x", "X"))
    assert not is_terminal(("x", "x"))
    assert is_terminal(("x", "Y")) and is_terminal(("Y", "x"))


# --- the bridge ------------------------------------------------------------
def test_bridge_is_empty_between_a_state_and_itself():
    assert bridge(("Y", "X"), ("Y", "X")) == []


def test_bridge_finds_a_two_step_route_and_it_replays():
    source = ("Y", "YX")
    target = tuple(moves_to_states("Y", "YX", [(2, 1, 0, 0), (1, 1, 0, 0)])[-1])
    span = bridge(source, target, max_depth=3)
    assert span is not None
    assert tuple(moves_to_states(source[0], source[1], span)[-1]) == target


def test_bridge_gives_up_rather_than_search_forever():
    assert bridge(("Y", "X"), ("YXYXYXYXYX", "YXYXYXYXYXYX"), max_depth=2) is None


# --- push-back -------------------------------------------------------------
def test_push_back_drops_the_automorphism_steps_and_keeps_the_input():
    pair = next(p for p in _rows(80)
                if _run(p)["solved"]
                and any(s.get("kind") == "automorphism" for s in _run(p)["steps"]))
    got = _run(pair)
    path = push_back(pair, got["states"], got["steps"])
    assert path[0] == tuple(canon_pair(*pair))
    assert len(path) <= len(got["states"])
    assert len(set(path)) == len(path), "no state should repeat"


# --- end to end ------------------------------------------------------------
def test_an_aut_assisted_solve_decodes_to_a_replayable_ac_certificate():
    checked = 0
    for pair in _rows(120):
        got = _run(pair)
        if not got["solved"]:
            continue
        if not any(s.get("kind") == "automorphism" for s in got["steps"]):
            continue
        moves, info = decode(pair, got["states"], got["steps"])
        assert moves is not None, (pair, info["reason"])
        assert all(len(m) == 4 for m in moves), "moves stay in the repo's format"
        replay = moves_to_states(pair[0], pair[1], moves)
        assert is_terminal(tuple(replay[-1])), (pair, replay[-1])
        assert info["final"] == list(replay[-1])
        checked += 1
        if checked >= 25:
            break
    assert checked >= 25


def test_decode_reports_why_it_failed_instead_of_returning_junk():
    moves, info = decode(("Y", "X"), [["Y", "X"], ["YYYYYYYY", "XXXXXXXX"]],
                         [{"kind": "substitution", "move": "1_1_0_0"}],
                         bridge_depth=1)
    assert moves is None
    assert "no AC move sequence" in info["reason"]


def test_the_bridge_closes_with_the_matcher_rather_than_walking_in():
    """A blind BFS branches ~400 per node here, so depth 3 is ~35 minutes.
    Closing the last step with `find_move` makes depth d cost d-1 expansions.
    The guard is a time bound: the rows that need a bridge must stay usable."""
    import time
    source = ("Y", "YX")
    target = tuple(moves_to_states("Y", "YX", [(2, 1, 0, 0), (1, 1, 0, 0)])[-1])
    started = time.time()
    span = bridge(source, target, max_depth=3)
    assert span is not None
    assert time.time() - started < 20, "the bridge must not search blind"
    assert tuple(moves_to_states(source[0], source[1], span)[-1]) == target


def test_a_row_that_needs_a_conjugated_step_decodes_in_seconds():
    """MS640 row 571 is one of the eleven whose pushed-back path contains a
    step the four-integer encoding cannot say in one move."""
    import time
    pair = _rows(572)[571]
    got = _run(pair)
    assert got["solved"]
    started = time.time()
    moves, info = decode(pair, got["states"], got["steps"])
    elapsed = time.time() - started
    assert moves is not None, info["reason"]
    assert info["bridged"] == 1
    assert is_terminal(tuple(moves_to_states(pair[0], pair[1], moves)[-1]))
    assert elapsed < 60, f"took {elapsed:.0f}s; the bridge has regressed"
