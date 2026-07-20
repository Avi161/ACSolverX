"""The character <-> (n, 2) bool encoding, and the two symbol orders.

The state array carries one bit for "which generator" and one for the sign,
which is precisely why a third generator cannot be represented without widening
the encoding. These tests pin the current mapping so that a widening is a
deliberate, visible change.
"""

import numpy as np
import pytest

from experiments.search.greedy_baseline import (
    arr_to_str, array_to_char, char_to_array, inverse_relator_nj, is_equal_nj,
    is_inverse_nj, is_less_than, state_to_key, str_to_arr,
)
from experiments.greedy_tests.fixtures.presentations import all_words
from experiments.greedy_tests.spec.words import (
    ascii_order_key, booth_order_key, inverse, str_to_word, symbol_to_char,
    word_to_str,
)

ALPHABET = "xXyY"


def _row(c):
    return np.array(char_to_array[c], dtype=bool)


def test_char_table_is_exactly_two_generators():
    assert set(char_to_array) == set(ALPHABET)
    assert len(char_to_array) == 4


@pytest.mark.parametrize("c", ALPHABET)
def test_array_to_char_inverts_char_to_array(c):
    b0, b1 = char_to_array[c]
    assert array_to_char(b0, b1) == c


def test_empty_string_gives_well_formed_2d_array():
    # A (0,) array here crashes numba's (n, 2) signature; regression for that.
    a = str_to_arr("")
    assert a.shape == (0, 2)
    assert a.dtype == np.bool_


def test_str_arr_round_trip_exhaustive():
    for w in all_words(2, 5):
        s = word_to_str(w)
        assert arr_to_str(str_to_arr(s)) == s


def test_is_inverse_and_is_equal_truth_table():
    for a in ALPHABET:
        for b in ALPHABET:
            ra, rb = _row(a), _row(b)
            assert bool(is_equal_nj(ra, rb)) == (a == b)
            assert bool(is_inverse_nj(ra, rb)) == (a.swapcase() == b)


def test_is_less_than_is_the_booth_order_Y_y_X_x():
    expected = sorted(ALPHABET, key=lambda c: booth_order_key(str_to_word(c)[0]))
    assert expected == ["Y", "y", "X", "x"]
    for a in ALPHABET:
        for b in ALPHABET:
            want = booth_order_key(str_to_word(a)[0]) < booth_order_key(str_to_word(b)[0])
            assert bool(is_less_than(_row(a), _row(b))) is want


def test_ascii_order_key_matches_real_character_order():
    """The packed key must sort like the rendered string, so this must hold."""
    for n_gen in (2, 3):
        syms = [g for g in range(-n_gen, n_gen + 1) if g != 0]
        by_key = sorted(syms, key=ascii_order_key)
        by_char = sorted(syms, key=symbol_to_char)
        assert by_key == by_char
    assert [symbol_to_char(g) for g in sorted([-1, -2, 1, 2], key=ascii_order_key)] \
        == ["X", "Y", "x", "y"]


def test_inverse_relator_reverses_and_flips_sign():
    for w in all_words(2, 4):
        got = str_to_word(arr_to_str(inverse_relator_nj(str_to_arr(word_to_str(w)))))
        assert got == inverse(w)


def test_inverse_relator_is_an_involution_and_does_not_mutate():
    a = str_to_arr("xxyXY")
    before = a.copy()
    twice = inverse_relator_nj(inverse_relator_nj(a))
    assert np.array_equal(a, before)
    assert np.array_equal(twice, a)


def test_state_to_key_is_the_string_pair():
    a, b = str_to_arr("xy"), str_to_arr("XY")
    assert state_to_key((a, b)) == ("xy", "XY")
