"""Exact pair-of-pants gates for one MMS02 two-multiplication skeleton."""

from __future__ import annotations

import hashlib
from collections import Counter
from dataclasses import dataclass

P0 = "xYxYXyyXYxyXy"
P1 = "XyyXYXyxYYxy"
Q0 = "XXyxYxy"
Q1 = "YxYXyxYxxYXyXYxyX"

SOURCE_MATRIX = ((0, 1), (-1, 1))
TARGET_MATRIX = ((0, 1), (1, -2))
MULTIPLICATION_MATRIX = ((1, 1), (1, 2))
FORCED_AMBIENT_MATRIX = ((-2, 7), (-1, 4))

THETA = {
    "x": "XyyyXyyyy",
    "y": "Xyyyy",
}

EXPECTED_FIRST_HISTOGRAM = (
    (13, 12),
    (19, 9),
    (25, 18),
    (27, 15),
    (29, 20),
    (31, 24),
    (33, 40),
    (35, 168),
)
EXPECTED_SECOND_HISTOGRAM = ((21, 24), (23, 30), (25, 72))
EXPECTED_FIRST_DIGEST = (
    "93cadbc49466bc0091a3f5d2d88deae524e4149f20c0425e0154595d5b13ab55"
)
EXPECTED_SECOND_DIGEST = (
    "8b35ce966c670e3e4c1aee8fef799d1bace35d14162fb5c923e87cb60b1278e4"
)


def inverse(word: str) -> str:
    return word[::-1].swapcase()


def free_reduce(word: str) -> str:
    reduced: list[str] = []
    for letter in word:
        if reduced and reduced[-1] == letter.swapcase():
            reduced.pop()
        else:
            reduced.append(letter)
    return "".join(reduced)


def cyclic_reduce(word: str) -> str:
    reduced = free_reduce(word)
    while len(reduced) >= 2 and reduced[0] == reduced[-1].swapcase():
        reduced = free_reduce(reduced[1:-1])
    return reduced


def rotations(word: str) -> tuple[str, ...]:
    if not word:
        return ("",)
    return tuple(word[index:] + word[:index] for index in range(len(word)))


def cyclic_key(word: str) -> str:
    return min(rotations(cyclic_reduce(word)))


def apply_homomorphism(word: str, images: dict[str, str]) -> str:
    pieces = []
    for letter in word:
        image = images[letter.lower()]
        pieces.append(image if letter.islower() else inverse(image))
    return free_reduce("".join(pieces))


Matrix = tuple[tuple[int, int], tuple[int, int]]


def matrix_multiply(left: Matrix, right: Matrix) -> Matrix:
    return (
        (
            left[0][0] * right[0][0] + left[0][1] * right[1][0],
            left[0][0] * right[0][1] + left[0][1] * right[1][1],
        ),
        (
            left[1][0] * right[0][0] + left[1][1] * right[1][0],
            left[1][0] * right[0][1] + left[1][1] * right[1][1],
        ),
    )


@dataclass(frozen=True)
class RotationGate:
    factor_lengths: tuple[int, int]
    disjoint_axis_floor: int
    table_size: int
    length_histogram: tuple[tuple[int, int], ...]
    minimum: tuple[int, int, int, str]
    exact_target_matches: int
    table_digest: str


@dataclass(frozen=True)
class TwoMultiplicationDecision:
    transformed_first: str
    transformed_second: str
    first_gate: RotationGate
    second_gate: RotationGate
    verdict: str


def evaluate_rotation_gate(left: str, right: str, target: str) -> RotationGate:
    table = tuple(
        (left_index, right_index, cyclic_reduce(left_rotation + right_rotation))
        for left_index, left_rotation in enumerate(rotations(left))
        for right_index, right_rotation in enumerate(rotations(right))
    )
    histogram = tuple(sorted(Counter(len(product) for _, _, product in table).items()))
    minimum = min(
        (len(product), left_index, right_index, product)
        for left_index, right_index, product in table
    )
    exact_target_matches = sum(
        cyclic_key(product) == cyclic_key(target) for _, _, product in table
    )
    serialization = "\n".join(
        f"{left_index}:{right_index}:{product}"
        for left_index, right_index, product in table
    )
    return RotationGate(
        factor_lengths=(len(left), len(right)),
        disjoint_axis_floor=len(left) + len(right),
        table_size=len(table),
        length_histogram=histogram,
        minimum=minimum,
        exact_target_matches=exact_target_matches,
        table_digest=hashlib.sha256(serialization.encode()).hexdigest(),
    )


def decide_two_multiplication_skeleton() -> TwoMultiplicationDecision:
    post_multiplication = matrix_multiply(MULTIPLICATION_MATRIX, SOURCE_MATRIX)
    if post_multiplication != ((-1, 2), (-2, 3)):
        raise AssertionError("the two-multiplication exponent matrix drifted")
    if matrix_multiply(post_multiplication, FORCED_AMBIENT_MATRIX) != TARGET_MATRIX:
        raise AssertionError("the forced ambient matrix no longer reaches the target")
    determinant = (
        FORCED_AMBIENT_MATRIX[0][0] * FORCED_AMBIENT_MATRIX[1][1]
        - FORCED_AMBIENT_MATRIX[0][1] * FORCED_AMBIENT_MATRIX[1][0]
    )
    if determinant != -1:
        raise AssertionError("the forced ambient matrix is not unimodular")

    basis_u = "Xyyy"
    basis_v = "Xyyyy"
    if free_reduce(inverse(basis_u) + basis_v) != "y":
        raise AssertionError("the displayed lift no longer recovers y")
    if free_reduce("yyyy" + inverse(basis_v)) != "x":
        raise AssertionError("the displayed lift no longer recovers x")
    if free_reduce(basis_u + basis_v) != THETA["x"] or basis_v != THETA["y"]:
        raise AssertionError("the explicit Nielsen lift drifted")

    transformed_first = cyclic_reduce(apply_homomorphism(P0, THETA))
    transformed_second = cyclic_reduce(apply_homomorphism(P1, THETA))
    if transformed_first != "XyyyXYxYYxYXyyyyy":
        raise AssertionError("the first transformed row drifted")
    if transformed_second != "xYYYYxYYYYxyXyyXyy":
        raise AssertionError("the second transformed row drifted")

    first_gate = evaluate_rotation_gate(transformed_first, transformed_second, Q0)
    second_gate = evaluate_rotation_gate(transformed_second, Q0, Q1)
    if first_gate.length_histogram != EXPECTED_FIRST_HISTOGRAM:
        raise AssertionError("the first complete rotation histogram drifted")
    if second_gate.length_histogram != EXPECTED_SECOND_HISTOGRAM:
        raise AssertionError("the second complete rotation histogram drifted")
    if first_gate.table_digest != EXPECTED_FIRST_DIGEST:
        raise AssertionError("the first complete rotation table drifted")
    if second_gate.table_digest != EXPECTED_SECOND_DIGEST:
        raise AssertionError("the second complete rotation table drifted")
    if first_gate.minimum != (13, 5, 17, "yXyyyXyxYYYYx"):
        raise AssertionError("the first pair-of-pants minimum drifted")
    if second_gate.minimum != (21, 0, 1, "YYYxYYYYxyXyyXyyXyxYx"):
        raise AssertionError("the second pair-of-pants minimum drifted")
    if first_gate.exact_target_matches or second_gate.exact_target_matches:
        raise AssertionError("a target conjugacy class entered a rotation table")

    return TwoMultiplicationDecision(
        transformed_first=transformed_first,
        transformed_second=transformed_second,
        first_gate=first_gate,
        second_gate=second_gate,
        verdict="ALTERNATING_POSITIVE_TWO_MULTIPLICATION_SKELETON_CLOSED",
    )


if __name__ == "__main__":
    print(decide_two_multiplication_skeleton())
