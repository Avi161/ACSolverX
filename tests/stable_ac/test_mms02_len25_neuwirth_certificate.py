from collections import Counter

from experiments.stable_ac.thickenable.mms02_len25_neuwirth_certificate import (
    PUBLISHED_WORDS,
    decide_mms02_length25_neuwirth,
)


GERMS = {
    "x": (0, 1),
    "X": (1, 0),
    "y": (2, 3),
    "Y": (3, 2),
}
EXPECTED_MULTIPLICITIES = {
    (0, 2): 7,
    (0, 3): 4,
    (1, 2): 4,
    (1, 3): 7,
    (2, 3): 3,
}


def _independent_corner_multiplicities(words):
    counts = Counter()
    for word in words:
        for index, letter in enumerate(word):
            following = word[(index + 1) % len(word)]
            edge = tuple(sorted((GERMS[letter][1], GERMS[following][0])))
            counts[edge] += 1
    return dict(counts)


def test_mms02_length25_words_and_support_are_exact():
    assert PUBLISHED_WORDS == (
        "XYxYXyxYYxyXy",
        "YXyyXYxyxYYx",
    )
    assert tuple(map(len, PUBLISHED_WORDS)) == (13, 12)
    assert _independent_corner_multiplicities(PUBLISHED_WORDS) == (
        EXPECTED_MULTIPLICITIES
    )

    decision = decide_mms02_length25_neuwirth()
    assert decision.occurrence_count == 25
    assert decision.support_kind == "K4-e"
    assert decision.missing_edge == (0, 1)
    assert decision.simple_edges == frozenset(EXPECTED_MULTIPLICITIES)
    assert dict(decision.parallel_multiplicities) == EXPECTED_MULTIPLICITIES
    assert decision.vertex_degrees == (11, 11, 14, 14)
    assert decision.scheme_cuts == (0, 1, 2, 3)
    assert len(decision.scheme_names) == 4


def test_mms02_length25_signed_rank_search_is_exhaustive_and_negative():
    decision = decide_mms02_length25_neuwirth()
    counters = decision.counters

    assert decision.verdict == "NOT_SPHERICAL_EXACT_COMPLEX"
    assert decision.witness is None
    assert counters.scheme_budget == counters.schemes_considered == 4
    assert counters.phase_pair_budget == counters.phase_pairs_considered == 616
    assert (
        counters.component_seed_budget
        == counters.component_seed_attempts
        == 8_624
    )
    assert counters.closed_component_assignments == 0
    assert counters.component_combination_budget == 0
    assert counters.component_combinations_considered == 0
    assert counters.exhaustive
