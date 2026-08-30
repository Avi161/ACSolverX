import hashlib
from collections import Counter

from experiments.equivalence_classes.lib.words import (
    apply_hom,
    cyc_reduce,
)
from experiments.stable_ac.mms02_two_multiplication_pair_of_pants_certificate import (
    EXPECTED_FIRST_DIGEST,
    EXPECTED_FIRST_HISTOGRAM,
    EXPECTED_SECOND_DIGEST,
    EXPECTED_SECOND_HISTOGRAM,
    P0,
    P1,
    Q0,
    Q1,
    THETA,
    decide_two_multiplication_skeleton,
)


def _rotations(word: str) -> tuple[str, ...]:
    return tuple(word[index:] + word[:index] for index in range(len(word)))


def _rotation_table(left: str, right: str) -> tuple[tuple[int, int, str], ...]:
    return tuple(
        (left_index, right_index, cyc_reduce(left_rotation + right_rotation))
        for left_index, left_rotation in enumerate(_rotations(left))
        for right_index, right_rotation in enumerate(_rotations(right))
    )


def _digest(table: tuple[tuple[int, int, str], ...]) -> str:
    serialization = "\n".join(
        f"{left_index}:{right_index}:{product}"
        for left_index, right_index, product in table
    )
    return hashlib.sha256(serialization.encode()).hexdigest()


def test_two_multiplication_forced_lift_and_rows():
    decision = decide_two_multiplication_skeleton()
    assert cyc_reduce(apply_hom(P0, THETA)) == decision.transformed_first
    assert cyc_reduce(apply_hom(P1, THETA)) == decision.transformed_second
    assert decision.transformed_first == "XyyyXYxYYxYXyyyyy"
    assert decision.transformed_second == "xYYYYxYYYYxyXyyXyy"


def test_first_pair_of_pants_table_is_complete_and_misses_q0():
    decision = decide_two_multiplication_skeleton()
    gate = decision.first_gate
    table = _rotation_table(decision.transformed_first, decision.transformed_second)
    histogram = tuple(sorted(Counter(len(product) for _, _, product in table).items()))
    assert len(table) == 17 * 18 == gate.table_size
    assert histogram == EXPECTED_FIRST_HISTOGRAM == gate.length_histogram
    assert _digest(table) == EXPECTED_FIRST_DIGEST == gate.table_digest
    assert gate.disjoint_axis_floor == 35
    assert gate.minimum == (13, 5, 17, "yXyyyXyxYYYYx")
    assert gate.minimum[0] > len(cyc_reduce(Q0))
    assert gate.exact_target_matches == 0


def test_second_pair_of_pants_table_is_complete_and_misses_q1():
    decision = decide_two_multiplication_skeleton()
    gate = decision.second_gate
    table = _rotation_table(decision.transformed_second, Q0)
    histogram = tuple(sorted(Counter(len(product) for _, _, product in table).items()))
    assert len(table) == 18 * 7 == gate.table_size
    assert histogram == EXPECTED_SECOND_HISTOGRAM == gate.length_histogram
    assert _digest(table) == EXPECTED_SECOND_DIGEST == gate.table_digest
    assert gate.disjoint_axis_floor == 25
    assert gate.minimum == (21, 0, 1, "YYYxYYYYxyXyyXyyXyxYx")
    assert gate.minimum[0] > len(cyc_reduce(Q1))
    assert gate.exact_target_matches == 0


def test_two_multiplication_scope_verdict_is_pinned():
    decision = decide_two_multiplication_skeleton()
    assert decision.verdict == (
        "ALTERNATING_POSITIVE_TWO_MULTIPLICATION_SKELETON_CLOSED"
    )
