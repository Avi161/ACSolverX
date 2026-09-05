"""Free and cyclic reduction.

``reduce_relator_nj`` was rewritten as a stack after the prototype's boundary
branch (``rel[add_index + 1]``) read out of bounds whenever the cancelling
partner was the last symbol. numba does not bounds-check, so it silently
returned a garbage length-1 relator instead of the empty word. The empty-word
cases below are that regression.
"""

import numpy as np
import pytest

from experiments.search.greedy_baseline import arr_to_str, reduce_relator_nj, str_to_arr
from experiments.greedy_tests.fixtures.presentations import all_words
from experiments.greedy_tests.spec.words import (
    is_cyclically_reduced, is_freely_reduced, reduce_word, str_to_word, word_to_str,
)


def _reduce(s, cyclic):
    return arr_to_str(reduce_relator_nj(str_to_arr(s), cyclic))


@pytest.mark.parametrize("cyclic", [True, False])
def test_matches_spec_exhaustively_to_length_six(cyclic):
    """4^0 + ... + 4^6 = 5461 words, both modes, against a from-definition spec."""
    for w in all_words(2, 6):
        assert _reduce(word_to_str(w), cyclic) == word_to_str(reduce_word(w, cyclic))


@pytest.mark.parametrize("word", ["xX", "Xx", "yY", "Yy", "xXyY", "xyYX", "xyYXxX"])
def test_full_cancellation_returns_the_empty_word(word):
    for cyclic in (True, False):
        out = reduce_relator_nj(str_to_arr(word), cyclic)
        assert out.shape == (0, 2), f"{word!r} -> {arr_to_str(out)!r}"


def test_cancelling_partner_at_the_last_symbol_is_the_old_oob_bug():
    # 'xyYX': the y/Y pair cancels, then x/X cancel with X the final symbol.
    assert _reduce("xyYX", True) == ""
    assert _reduce("xyYX", False) == ""


def test_empty_input_is_passed_through_well_formed():
    for cyclic in (True, False):
        out = reduce_relator_nj(str_to_arr(""), cyclic)
        assert out.shape == (0, 2)


@pytest.mark.parametrize("cyclic", [True, False])
def test_output_is_freely_reduced(cyclic):
    for w in all_words(2, 6):
        assert is_freely_reduced(str_to_word(_reduce(word_to_str(w), cyclic)))


def test_cyclic_mode_output_is_cyclically_reduced():
    for w in all_words(2, 6):
        assert is_cyclically_reduced(str_to_word(_reduce(word_to_str(w), True)))


def test_noncyclic_mode_leaves_the_wraparound_alone():
    # 'xyX' is freely reduced but not cyclically reduced.
    assert _reduce("xyX", False) == "xyX"
    assert _reduce("xyX", True) == "y"


@pytest.mark.parametrize("cyclic", [True, False])
def test_idempotent(cyclic):
    for w in all_words(2, 6):
        once = _reduce(word_to_str(w), cyclic)
        assert _reduce(once, cyclic) == once


@pytest.mark.parametrize("cyclic", [True, False])
def test_length_parity_is_preserved(cyclic):
    """Every cancellation removes exactly two symbols."""
    for w in all_words(2, 6):
        assert len(_reduce(word_to_str(w), cyclic)) % 2 == len(w) % 2


def test_does_not_mutate_its_input():
    a = str_to_arr("xyYX")
    before = a.copy()
    reduce_relator_nj(a, True)
    assert np.array_equal(a, before)


def test_only_the_stack_can_produce_the_empty_word():
    """The cyclic tail never empties an already free-reduced word.

    Its bound is a strict ``i < length / 2``, and a free-reduced word of length 2
    cannot satisfy ``w[0] == -w[-1]`` in the first place. So an empty result
    always comes from the free-reduction stack, never from the wrap-around.
    """
    for w in all_words(2, 6):
        free = reduce_word(w, cyclic=False)
        if free:
            assert _reduce(word_to_str(free), True) != ""
