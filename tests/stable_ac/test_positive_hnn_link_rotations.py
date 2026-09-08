"""Exact orientable rotation diagnostics for literal marked triples.

The qU comparison's triviality does not imply geometricity. A negative
rotation diagnostic is not an AC obstruction.
"""

from collections import Counter
from itertools import permutations, product
from math import factorial, prod


CASES = (
    (("uqUPQ", "upUQP", "PqpU"), 3456, {2: 2, 4: 164, 6: 1422, 8: 1868}, 1,
     "c924a606d1deab95fccedbefb95b37517a0aad522844c11e8694e8256912b3ad"),
    (("uqUPQ", "upUQP", "qU"), 288, {2: 6, 4: 98, 6: 184}, 1,
     "eec40396186fe9f0b4f46581d713863a8201394d85f479a9549f0b32c8a54a49"),
    (("p", "q", "u"), 1, {0: 1}, 3,
     "28a2826f6ed6d2c780db0a8479ba8c02f54771e61b388556dedb9c08cdf5d698"),
    (("uqUPQ", "QpQPu", "pUPq"), 3456, {4: 192, 6: 1478, 8: 1786}, 1,
     "70e9bd49da4da0502965d667dc1b42b8fd13e45d8d311855daa1f94122fbe051"),
)


def independent_rotations(words):
    germs = {}
    matching = {}
    positive = {}
    support = {}
    for row, word in enumerate(words):
        for index, letter in enumerate(word):
            arrival = (row, index, 0)
            departure = (row, (index - 1) % len(word), 1)
            germs[arrival] = letter.swapcase()
            germs[departure] = letter
            matching[arrival] = departure
            matching[departure] = arrival
            positive.setdefault(letter.lower(), []).append(
                departure if letter.islower() else arrival
            )

    for dart, germ in germs.items():
        row, index, side = dart
        opposite = (row, index, 1 - side)
        assert opposite in germs
        assert matching[matching[dart]] == dart
        assert matching[dart] != dart
        assert germs[matching[dart]] == germ.swapcase()
        support.setdefault(germ, set()).add(germs[opposite])
    for generator, darts in positive.items():
        assert all(germs[dart] == generator for dart in darts)
        assert {matching[dart] for dart in darts} == {
            dart for dart, germ in germs.items() if germ == generator.swapcase()
        }

    unseen = set(support)
    components = 0
    while unseen:
        pending = [unseen.pop()]
        components += 1
        while pending:
            for neighbor in support[pending.pop()]:
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    pending.append(neighbor)

    options = []
    for generator in sorted(positive):
        darts = tuple(sorted(positive[generator]))
        options.append(tuple((darts[0],) + tail for tail in permutations(darts[1:])))
    budget = prod(factorial(len(darts) - 1) for darts in positive.values())
    histogram = Counter()
    count = 0
    for orders in product(*options):
        rotation = {}
        for order in orders:
            negative = tuple(matching[dart] for dart in reversed(order))
            for cycle in (order, negative):
                for index, dart in enumerate(cycle):
                    assert dart not in rotation
                    rotation[dart] = cycle[(index + 1) % len(cycle)]
        assert set(rotation) == set(germs) == set(rotation.values())
        remaining = set(germs)
        faces = 0
        while remaining:
            start = next(iter(remaining))
            dart = start
            faces += 1
            while dart in remaining:
                remaining.remove(dart)
                row, index, side = rotation[dart]
                dart = (row, index, 1 - side)
            assert dart == start
        defect = sum(map(len, words)) - len(support) + 2 * components - faces
        histogram[defect] += 1
        count += 1
    assert count == budget
    return budget, count, dict(histogram), components


def test_independent_exact_orientable_rotation_histograms():
    for words, cases, histogram, components, _ in CASES:
        assert independent_rotations(words) == (cases, cases, histogram, components)


def test_production_rotation_histograms_and_exact_trace_hashes():
    from experiments.stable_ac.thickenable.neuwirth_permutation_certificate import enumerate_trace

    for words, cases, histogram, components, trace_sha256 in CASES:
        census = enumerate_trace(words)
        assert census.expected_cases == census.enumerated_cases == cases
        assert census.defect_histogram == histogram
        assert census.link_components == {components}
        assert census.trace_sha256 == trace_sha256


def test_pu_ribbon_cut_is_not_a_word_move():
    """Ribbon deletion only, not a compatible word rotation or legal balanced move."""
    from experiments.stable_ac.thickenable.neuwirth_permutation_certificate import (
        OccurrenceData, _build_C, compose, cycle_count, orbit_count,
    )

    words = ("uqUPQ", "upUQP", "PqpU")
    letters = "".join(words)
    data = OccurrenceData.from_words(words)
    occurrence_orders = {"p": (3, 9, 10, 6, 12), "q": (1, 11, 4, 8),
                         "u": (0, 5, 7, 13, 2)}
    positive_orders = tuple(
        tuple(2 * index + int(letters[index].isupper())
              for index in occurrence_orders[generator])
        for generator in data.positive_ends
    )
    A = data.A
    C = _build_C(data, positive_orders)
    assert (cycle_count(A), cycle_count(C), orbit_count((A, C)),
            cycle_count(compose(A, C))) == (14, 6, 1, 8)
    deleted = {13, 14, 25, 26}
    assert A[13] == 14 and A[25] == 26
    assert letters[6:8] == letters[12:14] == "pU"
    remaining = tuple(dart for dart in range(len(A)) if dart not in deleted)
    reindex = {dart: index for index, dart in enumerate(remaining)}
    restricted_A = tuple(reindex[A[dart]] for dart in remaining)
    successors = []
    for dart in remaining:
        following = C[dart]
        while following in deleted:
            following = C[following]
        successors.append(reindex[following])
    restricted_C = tuple(successors)
    E, V, L, F = (cycle_count(restricted_A), cycle_count(restricted_C),
                  orbit_count((restricted_A, restricted_C)),
                  cycle_count(compose(restricted_A, restricted_C)))
    assert (E, V, L, F) == (12, 6, 1, 8)
    assert E - V + 2 * L - F == 0
