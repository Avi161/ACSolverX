import itertools
import math
from collections import Counter

import numpy as np
import pytest
from numba import njit

from experiments.stable_ac.cov.ak_3_universal_test.certify_classical import (
    AK3,
    CEILING,
    component,
)
from experiments.stable_ac.thickenable.neuwirth_permutation_certificate import (
    OccurrenceData,
    enumerate_trace,
)
from experiments.stable_ac.thickenable.neuwirth_rank_solver import (
    classify_support,
    embedding_schemes,
    solve_spherical,
)


@pytest.mark.parametrize(
    ("words", "kind", "scheme_count"),
    [
        (("xxxYYYY", "xyxYXY"), "K4", 1),
        (("X", "XYXy"), "K4-e", 2),
        (("XYXy", "Y"), "K4-e", 2),
        (("X", "XYY"), "C4", 1),
    ],
)
def test_supported_exact_word_links_have_complete_scheme_families(
    words, kind, scheme_count
):
    support = classify_support(words)
    assert support.kind == kind
    schemes = embedding_schemes(support.data)
    assert len(schemes) == scheme_count
    assert all(scheme.slot_partition_verified for scheme in schemes)


@pytest.mark.parametrize(
    "words",
    [
        ("x", "y"),
        ("xx", "yy"),
        ("xxx", "yyy"),
        ("xx", "x"),
    ],
)
def test_out_of_scope_supports_fail_closed(words):
    support = classify_support(words)
    assert support.kind == "UNSUPPORTED"
    assert embedding_schemes(support.data) == ()


@pytest.mark.parametrize(
    "words",
    [
        ("X", "XYXy"),
        ("X", "XYY"),
        ("xyXY",),
    ],
)
def test_positive_decisions_carry_replayed_spherical_rotations(words):
    decision = solve_spherical(words)
    assert decision.verdict == "SPHERICAL"
    assert decision.spherical is True
    assert decision.witness is not None
    assert decision.witness.euler_characteristic == 2
    assert decision.witness.genus == 0
    assert decision.witness.face_count == len(decision.witness.faces)
    assert decision.witness.b_reversal_verified
    assert decision.witness.rank_partition_verified
    assert decision.witness.phase_equations_verified
    assert sorted(map(len, decision.witness.rotations)) == sorted(
        len(decision.support.data.vertex_darts[vertex]) for vertex in range(4)
    )


@pytest.mark.parametrize(
    "words",
    [
        ("XYXy", "Y"),
        ("xxxYYYY", "xyxYXY"),
        ("YYXXyx", "YYYxyXX"),
    ],
)
def test_negative_decisions_exhaust_all_schemes_phases_seeds_and_combinations(words):
    decision = solve_spherical(words)
    nx = len(decision.support.data.vertex_darts[0])
    ny = len(decision.support.data.vertex_darts[2])
    scheme_count = len(embedding_schemes(decision.support.data))

    assert decision.verdict == "NOT_SPHERICAL"
    assert decision.spherical is False
    assert decision.witness is None
    assert decision.counters.exhaustive
    assert (
        decision.counters.schemes_considered
        == decision.counters.scheme_budget
        == scheme_count
    )
    assert (
        decision.counters.phase_pairs_considered
        == decision.counters.phase_pair_budget
        == scheme_count * nx * ny
    )
    assert (
        decision.counters.component_seed_attempts
        == decision.counters.component_seed_budget
        > 0
    )
    assert (
        decision.counters.component_combinations_considered
        == decision.counters.component_combination_budget
        >= 0
    )


def test_unsupported_solver_decision_is_neither_yes_nor_no():
    decision = solve_spherical(("x", "y"))
    assert decision.verdict == "UNSUPPORTED"
    assert decision.spherical is None
    assert decision.witness is None
    assert not decision.counters.exhaustive


def test_split_central_class_and_both_collision_filters_are_exercised():
    split = solve_spherical(("XX", "XYxY"))
    assert split.spherical is True
    assert split.witness is not None
    assert split.support.kind == "K4-e"
    assert split.witness.cut == 1
    poles = tuple(
        vertex
        for vertex in range(4)
        if vertex not in split.support.missing_edge
    )
    central = tuple(sorted(poles))
    assert len(split.support.data.class_edges[central]) == 2
    assert split.counters.within_cycle_collision_rejections > 0

    cross_cycle = solve_spherical(("xyyxx", "YYXXX"))
    assert cross_cycle.spherical is True
    assert cross_cycle.counters.cross_cycle_collision_rejections > 0
    assert cross_cycle.counters.union_cardinality_checks > 0
    assert cross_cycle.witness is not None
    assert cross_cycle.witness.rank_partition_verified


_INVERSE = {"x": "X", "X": "x", "y": "Y", "Y": "y"}
_LETTERS = "xXyY"


def _cyclically_reduced(word):
    return all(
        word[(index + 1) % len(word)] != _INVERSE[letter]
        for index, letter in enumerate(word)
    )


def _least_rotation(word):
    return min(word[index:] + word[:index] for index in range(len(word)))


def _canonical_small_word_pairs():
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
                    pairs.add(tuple(sorted((first, second))))
    return tuple(
        pair
        for pair in sorted(pairs)
        if classify_support(pair).kind != "UNSUPPORTED"
    )


def test_exhaustive_canonical_small_word_pairs_match_factorial_census():
    pairs = _canonical_small_word_pairs()
    support_counts = Counter(classify_support(pair).kind for pair in pairs)
    assert len(pairs) == 1_412
    assert support_counts == {"K4": 328, "K4-e": 568, "C4": 516}

    decision_counts = Counter()
    within_collision_cases = 0
    split_cuts_seen = set()
    for pair in pairs:
        rank = solve_spherical(pair)
        factorial = enumerate_trace(pair)
        assert rank.spherical is bool(factorial.accepting_orders), pair
        decision_counts[(rank.support.kind, rank.spherical)] += 1
        within_collision_cases += bool(
            rank.counters.within_cycle_collision_rejections
        )
        if rank.witness is not None and rank.witness.cut not in (None, 0):
            split_cuts_seen.add(rank.witness.cut)

    assert decision_counts == {
        ("K4", True): 88,
        ("K4", False): 240,
        ("K4-e", True): 192,
        ("K4-e", False): 376,
        ("C4", True): 188,
        ("C4", False): 328,
    }
    assert within_collision_cases > 0
    assert split_cuts_seen == {1}


@njit
def _compiled_factorial_has_spherical_rotation(A, x_next, y_next, target_faces):
    dart_count = len(A)
    for x_index in range(x_next.shape[0]):
        for y_index in range(y_next.shape[0]):
            visited = np.zeros(dart_count, dtype=np.uint8)
            face_count = 0
            for start in range(dart_count):
                if visited[start]:
                    continue
                face_count += 1
                if face_count > target_faces:
                    break
                dart = start
                while not visited[dart]:
                    visited[dart] = 1
                    successor = x_next[x_index, dart]
                    if successor < 0:
                        successor = y_next[y_index, dart]
                    dart = successor
            if face_count == target_faces and visited.sum() == dart_count:
                return True
    return False


def _generator_face_successors(data, generator):
    endpoints = data.positive_ends[generator]
    positive_orders = (
        (endpoints[0],) + tail
        for tail in itertools.permutations(endpoints[1:])
    )
    rows = []
    for positive_order in positive_orders:
        C = [-1] * len(data.A)
        negative_order = tuple(
            data.B[dart] for dart in reversed(positive_order)
        )
        for rotation in (positive_order, negative_order):
            for index, dart in enumerate(rotation):
                C[dart] = rotation[(index + 1) % len(rotation)]
        rows.append(
            tuple(
                data.A[C[dart]] if C[dart] >= 0 else -1
                for dart in range(len(data.A))
            )
        )
    return np.asarray(rows, dtype=np.int64)


def _factorial_has_spherical_rotation(words):
    data = OccurrenceData.from_words(words)
    assert tuple(data.positive_ends) == ("x", "y")
    x_next = _generator_face_successors(data, "x")
    y_next = _generator_face_successors(data, "y")
    target_faces = len(data.A) // 2 - 2
    return bool(
        _compiled_factorial_has_spherical_rotation(
            np.asarray(data.A, dtype=np.int64),
            x_next,
            y_next,
            target_faces,
        )
    )


def _factorial_cost(words):
    degrees = Counter(letter.lower() for word in words for letter in word)
    return math.factorial(degrees["x"] - 1) * math.factorial(
        degrees["y"] - 1
    )


def test_all_18_affordable_height_17_states_match_optimized_factorial_census():
    states = component(AK3, CEILING)
    affordable = tuple(
        sorted(
            state
            for state in states
            if _factorial_cost(state) <= 2_000_000
        )
    )
    assert len(states) == 1_000
    assert len(affordable) == 18
    assert Counter(map(_factorial_cost, affordable)) == {
        86_400: 6,
        518_400: 12,
    }
    assert Counter(classify_support(state).kind for state in affordable) == {
        "K4": 18
    }

    for state in affordable:
        assert (
            solve_spherical(state).spherical
            is _factorial_has_spherical_rotation(state)
        ), state
