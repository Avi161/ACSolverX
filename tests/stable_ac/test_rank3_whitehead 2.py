from experiments.equivalence_classes.lib.autcanon import AUTOS
from experiments.stable_ac.rank3_compression.rank3_whitehead import (
    check_reduction,
    check_word_reduction,
    is_primitive_word,
    is_primitive_pair,
    reduce_pair,
    reduce_word,
    reduce_word_fast,
    second_kind_automorphisms,
)


def _map_key(phi):
    return tuple(sorted(phi.items()))


def test_rank_two_specialization_matches_existing_whitehead_set():
    generated = {
        _map_key(phi) for phi in second_kind_automorphisms(("x", "y"))
    }
    existing = {_map_key(phi) for phi in AUTOS[8:]}
    assert generated == existing


def test_rank_three_has_ninety_nonidentity_second_kind_maps():
    assert len(second_kind_automorphisms(("x", "z", "t"))) == 90


def test_primitive_pair_reduces_to_two_distinct_letters():
    result = reduce_pair(("xz", "t"))
    assert result.minimum_total == 2
    assert is_primitive_pair(result)
    check_reduction(("xz", "t"), result)


def test_nonprimitive_power_pair_has_certified_minimum_three():
    result = reduce_pair(("xx", "z"))
    assert result.minimum_total == 3
    assert not is_primitive_pair(result)
    check_reduction(("xx", "z"), result)


def test_primitive_single_word_reduces_to_one_letter():
    result = reduce_word("xz")
    assert result.minimum_total == 1
    assert is_primitive_word(result)
    check_word_reduction("xz", result)


def test_nonprimitive_power_word_stops_at_length_two():
    result = reduce_word("xx")
    assert result.minimum_total == 2
    assert not is_primitive_word(result)
    check_word_reduction("xx", result)


def test_fast_word_reducer_matches_certified_minima():
    for word in ("xz", "xx", "TTTXZtX", "TXZZxzz"):
        slow = reduce_word(word)
        fast = reduce_word_fast(word)
        assert fast.minimum_total == slow.minimum_total
        check_word_reduction(word, fast)
