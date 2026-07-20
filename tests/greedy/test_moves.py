"""The substitution move: does it enumerate Definition 2.1, and is the tuple honest?

Two different things are checked, and the difference matters:

* the canonical neighbour **set** equals a from-definition generator, and
* the stored ``(target, jsign, k1, k2)`` decodes to the definition's exact
  operation ``r_i <- rot_{k1}(r_i) . rot_{k2}(r_{3-i}^j)``.

Only the second catches a mislabelled move. Canonicalisation quotients out
rotation and inversion, so a generator that inverts the *target* rather than the
other relator produces an identical neighbour set while writing tuples that mean
something else. Round-tripping through replay proves internal consistency, not
agreement with the paper.
"""

import pytest

from experiments.search.greedy_baseline import (
    arr_to_str, canonical_pair_nj, get_neighbors_nj, get_neighbors_with_moves_nj,
    move_to_str, reduce_relator_nj, replay_move_nj, str_to_arr, str_to_move,
)
from experiments.greedy_tests.fixtures.presentations import (
    MMS02_LEN14, ak, ms640, ms_unsolved, random_presentations,
)
from experiments.greedy_tests.spec import moves as spec_moves
from experiments.greedy_tests.spec.moves import apply_move, legacy_to_move
from experiments.greedy_tests.spec.presentation import Presentation
from experiments.greedy_tests.spec.words import inverse as spec_words_inverse
from experiments.greedy_tests.spec.words import rotate as spec_rotate
from experiments.greedy_tests.spec.words import str_to_word

CASES = (
    ms640(range(0, 25))
    + ms_unsolved(range(0, 3))
    + [ak(2), ak(3), MMS02_LEN14]
    + random_presentations(seed=1234, count=10, max_len=6)
)
CYCLIC = [True, False]


def _arrs(pres):
    return tuple(str_to_arr(s) for s in pres.to_strs())


def _raw_children(pres):
    r1, r2 = _arrs(pres)
    return list(get_neighbors_with_moves_nj(r1, r2))


def _canonical_set(pres, cap, cyclic):
    out = set()
    for nr1, nr2, *_ in _raw_children(pres):
        a = reduce_relator_nj(nr1, cyclic)
        b = reduce_relator_nj(nr2, cyclic)
        if len(a) > cap or len(b) > cap:
            continue
        ca, cb = canonical_pair_nj(a, b)
        out.add((str_to_word(arr_to_str(ca)), str_to_word(arr_to_str(cb))))
    return out


@pytest.mark.parametrize("cyclic", CYCLIC)
def test_canonical_neighbour_set_equals_definition_2_1(cyclic):
    for pres in CASES:
        assert _canonical_set(pres, 24, cyclic) == spec_moves.neighbour_set(
            pres, 24, cyclic)


def test_the_stored_tuple_decodes_to_the_definition_2_1_operation():
    """The OTHER relator carries the sign ``j``; the target is only rotated."""
    for pres in CASES[:20]:
        for nr1, nr2, target, jsign, k1, k2 in _raw_children(pres):
            mv = legacy_to_move(int(target), int(jsign), int(k1), int(k2))
            want = apply_move(pres.relators, mv)
            got = (str_to_word(arr_to_str(nr1)), str_to_word(arr_to_str(nr2)))
            assert got == want, (pres.to_strs(), target, jsign, k1, k2)


def test_target_is_rotated_but_never_inverted():
    """A move labelled ``target=2`` must invert r1, not r2 (Def 2.1's ``r_{3-i}``).

    Built straight from the definition, without going through the spec's move
    type -- so a matching bug in ``legacy_to_move`` cannot hide this.
    """
    for pres in CASES[:10]:
        rels = pres.relators
        for nr1, nr2, target, jsign, k1, k2 in _raw_children(pres):
            i, j = int(target) - 1, 2 - int(target)
            source = rels[j] if int(jsign) == 1 else spec_words_inverse(rels[j])
            piece = spec_rotate(rels[i], int(k1)) + spec_rotate(source, int(k2))
            expected = list(rels)
            expected[i] = piece
            got = (str_to_word(arr_to_str(nr1)), str_to_word(arr_to_str(nr2)))
            assert got == tuple(expected), (pres.to_strs(), target, jsign, k1, k2)


def test_enumeration_order_is_target_then_jsign_then_k1_then_k2():
    """The heap tie-breaks on ``depth``, fixed by first-visit order, so this is load-bearing."""
    for pres in CASES[:15]:
        got = [(int(t), int(js), int(k1), int(k2))
               for _, _, t, js, k1, k2 in _raw_children(pres)]
        want = [spec_moves.move_to_legacy(mv, 2)
                for mv in spec_moves.enumerate_moves(pres)]
        assert got == want


def test_only_cancelling_seams_are_emitted():
    for pres in CASES[:15]:
        for nr1, nr2, target, jsign, k1, k2 in _raw_children(pres):
            mv = legacy_to_move(int(target), int(jsign), int(k1), int(k2))
            assert spec_moves.seam_cancels(pres.relators, mv)


def test_replay_move_reproduces_the_enumerated_raw_child():
    for pres in CASES[:15]:
        r1, r2 = _arrs(pres)
        for nr1, nr2, target, jsign, k1, k2 in _raw_children(pres):
            br1, br2 = replay_move_nj(r1, r2, target, jsign, k1, k2)
            assert (arr_to_str(br1), arr_to_str(br2)) == (arr_to_str(nr1), arr_to_str(nr2))


def test_unused_notebook_generator_yields_the_same_canonical_set():
    """``get_neighbors_nj``'s docstring claims this; nothing else checks it."""
    for pres in CASES[:15]:
        r1, r2 = _arrs(pres)
        old = set()
        for nr1, nr2 in get_neighbors_nj(r1, r2):
            a = reduce_relator_nj(nr1, True)
            b = reduce_relator_nj(nr2, True)
            if len(a) > 24 or len(b) > 24:
                continue
            ca, cb = canonical_pair_nj(a, b)
            old.add((str_to_word(arr_to_str(ca)), str_to_word(arr_to_str(cb))))
        assert old == _canonical_set(pres, 24, True)


def test_a_zero_length_relator_yields_no_moves_from_it():
    """An empty relator is a safe dead end, never a trivial state."""
    pres = Presentation(2, ((), (1, 2)))
    assert list(spec_moves.enumerate_moves(pres)) == []


# -- move string codec ------------------------------------------------------


@pytest.mark.parametrize("mv", [(1, 1, 0, 0), (2, -1, 3, 7), (1, -1, 0, 12)])
def test_move_string_round_trip_including_negative_sign(mv):
    s = move_to_str(mv)
    assert s == "_".join(str(v) for v in mv)
    assert str_to_move(s) == mv


def test_move_string_is_human_readable_as_definition_2_1():
    """``2_-1_0_0`` reads as ``r2 <- r2 . r1^-1``."""
    mv = legacy_to_move(*str_to_move("2_-1_0_0"))
    assert (mv.i, mv.j, mv.s, mv.k1, mv.k2) == (1, 0, -1, 0, 0)
