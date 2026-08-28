import itertools
import math
from collections import Counter

from experiments.stable_ac.thickenable.mms02_tpub_neuwirth_certificate import (
    INTERNAL_WORDS,
    ORIGINAL_WORDS,
    decide_tpub_neuwirth,
    relabel_words,
)
from experiments.stable_ac.thickenable.neuwirth_permutation_certificate import (
    enumerate_trace,
)
from experiments.stable_ac.thickenable.neuwirth_rank3_rigid_solver import (
    solve_rigid_spherical,
)


GERMS = {
    "x": (0, 1),
    "X": (1, 0),
    "y": (2, 3),
    "Y": (3, 2),
    "z": (4, 5),
    "Z": (5, 4),
}
EXPECTED_MULTIPLICITIES = {
    (0, 2): 6,
    (0, 3): 6,
    (0, 4): 1,
    (1, 2): 4,
    (1, 3): 1,
    (1, 4): 4,
    (1, 5): 4,
    (3, 4): 1,
    (3, 5): 2,
}
EXPECTED_MACRO_ROTATIONS = (
    (
        (2, 3, 4),
        (2, 4, 3, 5),
        (0, 1),
        (0, 5, 1, 4),
        (0, 3, 1),
        (1, 3),
    ),
    (
        (2, 3, 4),
        (2, 4, 5, 3),
        (0, 1),
        (0, 1, 5, 4),
        (0, 3, 1),
        (1, 3),
    ),
    (
        (2, 4, 3),
        (2, 3, 5, 4),
        (0, 1),
        (0, 4, 5, 1),
        (0, 1, 3),
        (1, 3),
    ),
    (
        (2, 4, 3),
        (2, 5, 3, 4),
        (0, 1),
        (0, 4, 1, 5),
        (0, 1, 3),
        (1, 3),
    ),
)


def _independent_multiplicities(words):
    counts = Counter()
    for word in words:
        for index, letter in enumerate(word):
            following = word[(index + 1) % len(word)]
            edge = tuple(sorted((GERMS[letter][1], GERMS[following][0])))
            counts[edge] += 1
    return dict(counts)


def _independent_face_count(rotation, edges):
    unseen = {
        dart
        for edge in edges
        for dart in (edge, tuple(reversed(edge)))
    }
    faces = 0
    while unseen:
        faces += 1
        dart = min(unseen)
        while dart in unseen:
            unseen.remove(dart)
            left, right = dart
            order = rotation[right]
            dart = (right, order[(order.index(left) + 1) % len(order)])
    return faces


def _independent_macro_rotations(edges):
    adjacency = {vertex: set() for vertex in range(6)}
    for left, right in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    choices = []
    for vertex in range(6):
        head, *tail = sorted(adjacency[vertex])
        choices.append(
            tuple((head, *order) for order in itertools.permutations(tail))
        )
    assert math.prod(map(len, choices)) == 144
    return tuple(
        sorted(
            rotation
            for rotation in itertools.product(*choices)
            if 6 - len(edges) + _independent_face_count(rotation, edges) == 2
        )
    )


def _connected_after_delete(edges, deleted):
    remaining = set(range(6)) - set(deleted)
    adjacency = {vertex: set() for vertex in remaining}
    for left, right in edges:
        if left in remaining and right in remaining:
            adjacency[left].add(right)
            adjacency[right].add(left)
    reached = {min(remaining)}
    stack = list(reached)
    while stack:
        vertex = stack.pop()
        for neighbor in adjacency[vertex] - reached:
            reached.add(neighbor)
            stack.append(neighbor)
    return reached == remaining


def test_tpub_exact_words_support_and_macro_rotations():
    assert relabel_words(ORIGINAL_WORDS) == INTERNAL_WORDS
    assert sum(map(len, ORIGINAL_WORDS)) == 29
    multiplicities = _independent_multiplicities(ORIGINAL_WORDS)
    assert multiplicities == EXPECTED_MULTIPLICITIES
    edges = frozenset(multiplicities)
    assert tuple(
        edge for edge in sorted(edges) if not _connected_after_delete(edges, edge)
    ) == ((1, 3),)
    assert multiplicities[(1, 3)] == 1
    assert _independent_macro_rotations(edges) == (
        EXPECTED_MACRO_ROTATIONS
    )


def test_tpub_signed_rank_search_is_exhaustive_and_negative():
    decision = decide_tpub_neuwirth()
    assert decision.occurrence_count == 29
    assert dict(decision.parallel_multiplicities) == EXPECTED_MULTIPLICITIES
    assert decision.degrees == (3, 4, 2, 4, 3, 2)
    assert decision.macro_rotation_budget == 144
    assert decision.macro_rotations == EXPECTED_MACRO_ROTATIONS
    assert decision.disconnecting_support_pairs == ((1, 3),)
    assert decision.verdict == "NOT_SPHERICAL_EXACT_COMPLEX"
    assert decision.witness is None
    assert decision.counters.scheme_budget == 4
    assert decision.counters.schemes_considered == 4
    assert decision.counters.phase_tuple_budget == 3_120
    assert decision.counters.phase_tuples_considered == 3_120
    assert decision.counters.component_seed_budget == 18_720
    assert decision.counters.component_seed_attempts == 18_720
    assert decision.counters.closed_component_assignments == 96
    assert decision.counters.component_combination_budget == 0
    assert decision.counters.exhaustive


def test_generalized_rank_solver_preserves_factorial_fixture():
    words = ("XZXTz", "ZTxZZ", "ttXzX")
    rank = solve_rigid_spherical(words)
    factorial = enumerate_trace(words)
    assert factorial.expected_cases == 17_280
    assert factorial.enumerated_cases == factorial.expected_cases
    assert rank.support.kind == "K6-P5"
    assert rank.spherical is bool(factorial.accepting_orders)
    assert rank.spherical is False
    assert rank.witness is None
    assert rank.counters.exhaustive
