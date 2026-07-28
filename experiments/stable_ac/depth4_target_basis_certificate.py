from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations


SOURCE_A_KERNEL = ((0, -1), (4, -1), (7, -1), (11, -1), (10, 1), (6, 1))
SOURCE_B_KERNEL = ((0, -1), (4, -1), (8, -1), (7, 1), (4, 1))
SOURCE_A_KERNEL_INVERSE = tuple(
    (index, -sign)
    for index, sign in reversed(SOURCE_A_KERNEL)
)


@dataclass(frozen=True)
class LinearCondition:
    coefficients: tuple[int, int, int, int]
    right_hand_side: int
    cancellation_pairs: int


CONDITIONS = (
    LinearCondition((1, 1, 0, 0), 1, 2),
    LinearCondition((1, 0, 0, 0), 0, 3),
    LinearCondition((1, -1, -1, 0), 0, 2),
    LinearCondition((0, 0, 0, 1), 0, 2),
    LinearCondition((0, -1, 1, -1), 0, 2),
)


def boundary_cancellation_rule(
    left: tuple[tuple[int, int], ...],
    right: tuple[tuple[int, int], ...],
) -> tuple[int, int] | None:
    left_index, left_sign = left[-1]
    right_index, right_sign = right[0]
    if left_sign != -right_sign:
        return None
    shift_difference = left_index - right_index
    pairs = 0
    for left_letter, right_letter in zip(reversed(left), right):
        if (
            left_letter[0] != right_letter[0] + shift_difference
            or left_letter[1] != -right_letter[1]
        ):
            break
        pairs += 1
    return shift_difference, pairs


def boundary_cancellation_rules() -> dict[tuple[str, str], tuple[int, int] | None]:
    return {
        ("B", "B"): boundary_cancellation_rule(SOURCE_B_KERNEL, SOURCE_B_KERNEL),
        ("B", "D"): boundary_cancellation_rule(
            SOURCE_B_KERNEL,
            SOURCE_A_KERNEL_INVERSE,
        ),
        ("D", "B"): boundary_cancellation_rule(
            SOURCE_A_KERNEL_INVERSE,
            SOURCE_B_KERNEL,
        ),
    }


@dataclass(frozen=True)
class TargetBasisCertificate:
    source_a_kernel_length: int
    source_b_kernel_length: int
    expanded_kernel_length: int
    maximum_cancellation_pairs: int
    minimum_cyclic_length: int
    maximum_is_attained_at: tuple[int, int, int, int]


def rationally_consistent(conditions: tuple[LinearCondition, ...]) -> bool:
    matrix = [
        [Fraction(value) for value in condition.coefficients]
        + [Fraction(condition.right_hand_side)]
        for condition in conditions
    ]
    pivot_row = 0
    for column in range(4):
        pivot = next(
            (row for row in range(pivot_row, len(matrix)) if matrix[row][column]),
            None,
        )
        if pivot is None:
            continue
        matrix[pivot_row], matrix[pivot] = matrix[pivot], matrix[pivot_row]
        pivot_value = matrix[pivot_row][column]
        matrix[pivot_row] = [value / pivot_value for value in matrix[pivot_row]]
        for row in range(len(matrix)):
            if row == pivot_row or not matrix[row][column]:
                continue
            multiplier = matrix[row][column]
            matrix[row] = [
                value - multiplier * pivot_entry
                for value, pivot_entry in zip(matrix[row], matrix[pivot_row])
            ]
        pivot_row += 1
    return not any(
        not any(row[:4]) and row[4]
        for row in matrix
    )


def target_basis_certificate() -> TargetBasisCertificate:
    maximum = 0
    for count in range(len(CONDITIONS) + 1):
        for selected in combinations(CONDITIONS, count):
            if rationally_consistent(selected):
                maximum = max(
                    maximum,
                    sum(condition.cancellation_pairs for condition in selected),
                )

    witness = (0, 0, 0, 0)
    witness_weight = sum(
        condition.cancellation_pairs
        for condition in CONDITIONS
        if sum(
            coefficient * value
            for coefficient, value in zip(condition.coefficients, witness)
        )
        == condition.right_hand_side
    )
    assert witness_weight == maximum
    expanded_length = 3 * len(SOURCE_A_KERNEL) + 5 * len(SOURCE_B_KERNEL)
    return TargetBasisCertificate(
        source_a_kernel_length=len(SOURCE_A_KERNEL),
        source_b_kernel_length=len(SOURCE_B_KERNEL),
        expanded_kernel_length=expanded_length,
        maximum_cancellation_pairs=maximum,
        minimum_cyclic_length=expanded_length - 2 * maximum,
        maximum_is_attained_at=witness,
    )


if __name__ == "__main__":
    print(target_basis_certificate())
