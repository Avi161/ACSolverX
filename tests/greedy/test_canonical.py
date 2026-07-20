"""Canonicalisation: Booth's minimal rotation, orbit representative, pair order.

A relator is an unoriented cyclic word, so the stored representative must be
invariant under rotation and under whole-relator inversion. The solver reaches
it with Booth's algorithm; the spec brute-forces the orbit, so agreement is
independent evidence rather than a restatement.
"""

import pytest

from experiments.search.greedy_baseline import (
    arr_to_str, canonical_pair_nj, canonical_relator_nj, find_minimal_rotation,
    inverse_relator_nj, lex_cmp_array, str_to_arr,
)
from experiments.greedy_tests.fixtures.presentations import all_words
from experiments.greedy_tests.spec.words import (
    booth_order_key, canonical_word, inverse, lex_key, min_rotation, orbit,
    reduce_word, rotate, str_to_word, word_to_str,
)

_WORDS = [w for w in all_words(2, 6) if w]


def _canon(w):
    return str_to_word(arr_to_str(canonical_relator_nj(str_to_arr(word_to_str(w)))))


def _min_rot(w):
    return str_to_word(arr_to_str(find_minimal_rotation(str_to_arr(word_to_str(w)))))


def test_booth_equals_brute_force_minimal_rotation():
    for w in _WORDS:
        assert _min_rot(w) == min_rotation(w)


def test_minimal_rotation_is_a_rotation_of_the_input():
    for w in _WORDS:
        assert _min_rot(w) in {rotate(w, k) for k in range(len(w))}


def test_canonical_relator_matches_spec_exhaustively():
    for w in _WORDS:
        assert _canon(w) == canonical_word(w)


def test_canonical_relator_is_the_orbit_minimum():
    for w in _WORDS:
        best = min(orbit(w), key=lambda r: lex_key(r, booth_order_key))
        assert _canon(w) == best


def test_canonical_is_invariant_under_rotation_and_inversion():
    for w in _WORDS:
        c = _canon(w)
        for k in range(len(w)):
            assert _canon(rotate(w, k)) == c
        assert _canon(inverse(w)) == c


def test_canonical_is_idempotent():
    for w in _WORDS:
        assert _canon(_canon(w)) == _canon(w)


def test_canonical_preserves_length():
    for w in _WORDS:
        assert len(_canon(w)) == len(w)


def test_a_single_letter_canonicalises_to_its_inverse():
    """Why a solved state prints as ``['Y', 'X']`` rather than ``['x', 'y']``."""
    assert arr_to_str(canonical_relator_nj(str_to_arr("x"))) == "X"
    assert arr_to_str(canonical_relator_nj(str_to_arr("y"))) == "Y"


# -- canonical_pair_nj ------------------------------------------------------


def _pair(a, b):
    ca, cb = canonical_pair_nj(str_to_arr(a), str_to_arr(b))
    return arr_to_str(ca), arr_to_str(cb)


_PAIRS = [(word_to_str(a), word_to_str(b))
          for a in all_words(2, 3) if a
          for b in all_words(2, 3) if b]


def test_pair_is_symmetric_under_swap():
    for a, b in _PAIRS:
        assert _pair(a, b) == _pair(b, a)


def test_pair_is_idempotent():
    for a, b in _PAIRS:
        p = _pair(a, b)
        assert _pair(*p) == p


def test_pair_is_ordered_by_length_then_lex():
    for a, b in _PAIRS:
        x, y = _pair(a, b)
        kx = (len(x), lex_key(str_to_word(x), booth_order_key))
        ky = (len(y), lex_key(str_to_word(y), booth_order_key))
        assert kx <= ky


def test_pair_equals_spec_sort_of_canonical_words():
    for a, b in _PAIRS:
        want = sorted((canonical_word(str_to_word(a)), canonical_word(str_to_word(b))),
                      key=lambda r: (len(r), lex_key(r, booth_order_key)))
        assert _pair(a, b) == tuple(word_to_str(w) for w in want)


def test_trivial_state_canonicalises_to_Y_X():
    assert _pair("x", "y") == ("Y", "X")


# -- lex_cmp_array ----------------------------------------------------------


def test_lex_cmp_array_is_correct_for_equal_lengths():
    """``lex_cmp_array(a, b)`` means ``a >= b`` under Y < y < X < x."""
    for n in (1, 2, 3):
        words = [w for w in all_words(2, n) if len(w) == n]
        arrs = {w: str_to_arr(word_to_str(w)) for w in words}
        for a in words:
            for b in words:
                want = lex_key(a, booth_order_key) >= lex_key(b, booth_order_key)
                assert bool(lex_cmp_array(arrs[a], arrs[b])) is want, (a, b)


def test_lex_cmp_array_is_only_meaningful_for_equal_lengths():
    """Characterization: it ``zip``s, so a prefix compares equal and returns True.

    This is not a bug because both call sites guarantee equal lengths --
    ``canonical_relator_nj`` compares a word's minimal rotation against its
    inverse's (same length), and ``canonical_pair_nj`` short-circuits on
    ``len(cr1) == len(cr2)``. The next caller must preserve that.
    """
    assert bool(lex_cmp_array(str_to_arr("Y"), str_to_arr("Yy"))) is True
    assert bool(lex_cmp_array(str_to_arr("Yy"), str_to_arr("Y"))) is True


def test_every_lex_cmp_call_site_passes_equal_lengths():
    for w in _WORDS:
        a = find_minimal_rotation(str_to_arr(word_to_str(w)))
        b = find_minimal_rotation(inverse_relator_nj(str_to_arr(word_to_str(w))))
        assert len(a) == len(b)
