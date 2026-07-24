import itertools
from collections import Counter

from experiments.stable_ac.thickenable.neuwirth_p4_solver import (
    p4_embedding_schemes,
    solve_four_germ_spherical,
)
from experiments.stable_ac.thickenable.neuwirth_permutation_certificate import (
    enumerate_trace,
)
from experiments.stable_ac.thickenable.neuwirth_rank_solver import (
    classify_support,
)


def test_p4_support_has_one_scheme_per_central_bundle_gap():
    words = (
        "YXXYXXXXX",
        "YXXXYXXXYXXXYXXXYXXXXYXXXXYXXXX",
    )
    support = classify_support(words)
    assert support.kind == "UNSUPPORTED"
    schemes = p4_embedding_schemes(support)
    internal = tuple(
        vertex
        for vertex in range(4)
        if sum(vertex in edge for edge in support.simple_edges) == 2
    )
    central = tuple(sorted(internal))
    assert len(schemes) == len(support.data.class_edges[central])
    assert {scheme.cut for scheme in schemes} == set(range(len(schemes)))
    assert all(scheme.slot_partition_verified for scheme in schemes)


def test_p4_positive_and_negative_match_factorial_replay():
    for words in (("X", "XY"), ("X", "XXXYXY")):
        rank = solve_four_germ_spherical(words)
        factorial = enumerate_trace(words)
        assert rank.support.kind == "P4"
        assert rank.spherical is bool(factorial.accepting_orders)
        if rank.spherical:
            assert rank.witness is not None
            assert rank.witness.euler_characteristic == 2
            assert rank.witness.b_reversal_verified
        else:
            assert rank.witness is None
            assert rank.counters.exhaustive


_INVERSE = {"x": "X", "X": "x", "y": "Y", "Y": "y"}
_LETTERS = "xXyY"


def _cyclically_reduced(word):
    return all(
        word[(index + 1) % len(word)] != _INVERSE[letter]
        for index, letter in enumerate(word)
    )


def _least_rotation(word):
    return min(word[index:] + word[:index] for index in range(len(word)))


def _canonical_small_p4_pairs():
    words_by_length = {
        length: sorted(
            {
                _least_rotation("".join(letters))
                for letters in itertools.product(_LETTERS, repeat=length)
                if _cyclically_reduced("".join(letters))
            }
        )
        for length in range(1, 7)
    }
    pairs = set()
    for total_length in range(2, 8):
        for first_length in range(1, total_length):
            second_length = total_length - first_length
            for first in words_by_length[first_length]:
                for second in words_by_length[second_length]:
                    pair = tuple(sorted((first, second)))
                    support = classify_support(pair)
                    degrees = Counter()
                    for left, right in support.simple_edges:
                        degrees[left] += 1
                        degrees[right] += 1
                    if (
                        len(support.simple_edges) == 3
                        and sorted(degrees[vertex] for vertex in range(4))
                        == [1, 1, 2, 2]
                    ):
                        pairs.add(pair)
    return tuple(sorted(pairs))


def test_all_small_p4_pairs_match_factorial_census():
    pairs = _canonical_small_p4_pairs()
    assert len(pairs) == 476

    decision_counts = Counter()
    nonzero_central_shifts = 0
    for pair in pairs:
        rank = solve_four_germ_spherical(pair)
        factorial = enumerate_trace(pair)
        assert rank.spherical is bool(factorial.accepting_orders), pair
        decision_counts[rank.spherical] += 1
        if rank.witness is not None and rank.witness.cut:
            nonzero_central_shifts += 1

    assert decision_counts == {True: 444, False: 32}
    assert nonzero_central_shifts > 0
