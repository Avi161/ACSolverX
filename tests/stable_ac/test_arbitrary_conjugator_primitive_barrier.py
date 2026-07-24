from experiments.stable_ac.rank3_compression.one_edge import (
    cyclic_reduce,
    rotations,
)
from experiments.stable_ac.rank3_compression.two_stabilization import inverse


A = "xxxzXXXXZ"
B = "ZxzxZ"


def _minimum_rotation_product(left: str, right: str) -> int:
    return min(
        len(cyclic_reduce(left_rotation + right_rotation))
        for left_rotation in rotations(left)
        for right_rotation in rotations(right)
    )


def _abelianization(word: str) -> tuple[int, int]:
    return (
        word.count("x") - word.count("X"),
        word.count("z") - word.count("Z"),
    )


def test_exact_rotation_minima_and_primitive_length_gap():
    cases = (
        (A, B, (1, -1), 2),
        (A, inverse(B), (-3, 1), 4),
        (B, A, (1, -1), 2),
        (B, inverse(A), (3, -1), 4),
    )
    for left, right, expected_vector, primitive_length in cases:
        assert _abelianization(left + right) == expected_vector
        minimum = _minimum_rotation_product(left, right)
        assert minimum == 10
        assert minimum > primitive_length
