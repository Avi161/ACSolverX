"""Homology-compatible A5 multiplication depth for the MMS02 terminal gate."""

from __future__ import annotations

from dataclasses import dataclass

from experiments.stable_ac.mms02_fixed_b_a5_conjugacy_certificate import (
    IDENTITY,
    IMAGES,
    Permutation,
    compose,
    conjugate,
    evaluate_word,
    generated_subgroup,
    inverse,
)

Matrix = tuple[int, int, int, int]
ClassState = tuple[int, int, Matrix]

IDENTITY_MATRIX: Matrix = (1, 0, 0, 1)
SIGNED_PERMUTATION_MATRICES: tuple[Matrix, ...] = tuple(
    (left_sign, 0, 0, right_sign)
    for left_sign in (-1, 1)
    for right_sign in (-1, 1)
) + tuple(
    (0, left_sign, right_sign, 0)
    for left_sign in (-1, 1)
    for right_sign in (-1, 1)
)

EXPECTED_LAYER_SIZES = (8, 32, 272, 1896, 7056, 18416)
EXPECTED_COMPATIBLE_MATRICES: tuple[Matrix, ...] = tuple(
    (1, shear, 0, determinant)
    for shear in range(-3, 4)
    for determinant in (-1, 1)
)
DEPTH_FIVE_WITNESS_MATRIX: Matrix = (1, -1, 0, 1)
DEPTH_FIVE_WITNESS_MOVES = ("R2+", "R1-", "R2+", "R1+", "R2-")
DEPTH_FIVE_WITNESS_CONJUGATORS: tuple[Permutation, ...] = (
    (0, 4, 3, 2, 1),
    (0, 2, 4, 3, 1),
    (0, 1, 3, 4, 2),
    (0, 2, 3, 1, 4),
    (0, 1, 4, 2, 3),
    (0, 2, 4, 3, 1),
)


def matrix_multiply(left: Matrix, right: Matrix) -> Matrix:
    return (
        left[0] * right[0] + left[1] * right[2],
        left[0] * right[1] + left[1] * right[3],
        left[2] * right[0] + left[3] * right[2],
        left[2] * right[1] + left[3] * right[3],
    )


def a5_conjugacy_classes() -> tuple[frozenset[Permutation], ...]:
    a5 = generated_subgroup(tuple(IMAGES.values()))
    remaining = set(a5)
    classes = []
    while remaining:
        seed = min(remaining)
        orbit = frozenset(conjugate(value, seed) for value in a5)
        classes.append(orbit)
        remaining.difference_update(orbit)
    return tuple(classes)


def product_class_table(
    classes: tuple[frozenset[Permutation], ...],
) -> dict[tuple[int, int], frozenset[int]]:
    class_of = {
        value: class_index
        for class_index, conjugacy_class in enumerate(classes)
        for value in conjugacy_class
    }
    return {
        (left_index, right_index): frozenset(
            class_of[compose(left, right)]
            for left in classes[left_index]
            for right in classes[right_index]
        )
        for left_index in range(len(classes))
        for right_index in range(len(classes))
    }


def signed_permutation_closure(states: set[ClassState]) -> set[ClassState]:
    closed = set()
    for left_class, right_class, matrix in states:
        for normalization in SIGNED_PERMUTATION_MATRICES:
            normalized_matrix = matrix_multiply(normalization, matrix)
            if normalization[0]:
                closed.add((left_class, right_class, normalized_matrix))
            else:
                closed.add((right_class, left_class, normalized_matrix))
    return closed


def next_multiplication_layer(
    states: set[ClassState],
    products: dict[tuple[int, int], frozenset[int]],
) -> set[ClassState]:
    next_states = set()
    for left_class, right_class, matrix in states:
        for sign in (-1, 1):
            row_one = (1, sign, 0, 1)
            row_two = (1, 0, sign, 1)
            for product_class in products[left_class, right_class]:
                next_states.add(
                    (
                        product_class,
                        right_class,
                        matrix_multiply(row_one, matrix),
                    )
                )
            for product_class in products[right_class, left_class]:
                next_states.add(
                    (
                        left_class,
                        product_class,
                        matrix_multiply(row_two, matrix),
                    )
                )
    return signed_permutation_closure(next_states)


def depth_five_witness_pairs() -> tuple[tuple[Permutation, Permutation], ...]:
    source = evaluate_word("zYX")
    target = evaluate_word("Xyz")
    source_inverse = inverse(source)
    source_inverse_square = compose(source_inverse, source_inverse)
    target_cube = compose(compose(target, target), target)
    target_inverse = inverse(target)
    intermediate = (3, 2, 0, 4, 1)
    conjugators = iter(DEPTH_FIVE_WITNESS_CONJUGATORS)
    a5 = generated_subgroup(tuple(IMAGES.values()))
    if any(value not in a5 for value in DEPTH_FIVE_WITNESS_CONJUGATORS):
        raise AssertionError("a depth-five witness conjugator left A5")

    states = [(source_inverse, IDENTITY)]
    states.append((states[-1][0], compose(states[-1][1], states[-1][0])))
    states.append(
        (states[-1][0], conjugate(next(conjugators), states[-1][1]))
    )
    states.append(
        (compose(states[-1][0], inverse(states[-1][1])), states[-1][1])
    )
    states.append(
        (
            conjugate(next(conjugators), states[-1][0]),
            conjugate(next(conjugators), states[-1][1]),
        )
    )
    states.append((states[-1][0], compose(states[-1][1], states[-1][0])))
    states.append(
        (
            conjugate(next(conjugators), states[-1][0]),
            conjugate(next(conjugators), states[-1][1]),
        )
    )
    states.append((compose(states[-1][0], states[-1][1]), states[-1][1]))
    states.append(
        (states[-1][0], conjugate(next(conjugators), states[-1][1]))
    )
    states.append(
        (states[-1][0], compose(states[-1][1], inverse(states[-1][0])))
    )

    expected = (
        (source_inverse, IDENTITY),
        (source_inverse, source_inverse),
        (source_inverse, source),
        (source_inverse_square, source),
        (target, target_cube),
        (target, target_inverse),
        (intermediate, source_inverse_square),
        (target, source_inverse_square),
        (target, target),
        (target, IDENTITY),
    )
    if tuple(states) != expected:
        raise AssertionError("the explicit depth-five A5 transcript drifted")
    return expected


def depth_five_witness_matrix() -> Matrix:
    row_one_positive = (1, 1, 0, 1)
    row_one_negative = (1, -1, 0, 1)
    row_two_positive = (1, 0, 1, 1)
    row_two_negative = (1, 0, -1, 1)
    cumulative = IDENTITY_MATRIX
    for move in (
        row_two_positive,
        row_one_negative,
        row_two_positive,
        row_one_positive,
        row_two_negative,
    ):
        cumulative = matrix_multiply(move, cumulative)
    if cumulative != DEPTH_FIVE_WITNESS_MATRIX:
        raise AssertionError("the explicit depth-five Nielsen matrix drifted")
    return cumulative


@dataclass(frozen=True)
class HomologyDepthDecision:
    layer_sizes: tuple[int, ...]
    first_compatible_depth: int
    compatible_matrices: tuple[Matrix, ...]
    identity_matrix_reached: bool
    witness_matrix: Matrix
    witness_pairs: tuple[tuple[Permutation, Permutation], ...]
    verdict: str


def decide_homology_compatible_depth() -> HomologyDepthDecision:
    classes = a5_conjugacy_classes()
    if tuple(sorted(len(value) for value in classes)) != (1, 12, 12, 15, 20):
        raise AssertionError("the A5 conjugacy-class partition drifted")
    class_of = {
        value: class_index
        for class_index, conjugacy_class in enumerate(classes)
        for value in conjugacy_class
    }
    if any(class_of[value] != class_of[inverse(value)] for value in class_of):
        raise AssertionError("an A5 conjugacy class stopped being inversion-stable")

    source_class = class_of[evaluate_word("zYX")]
    target_class = class_of[evaluate_word("Xyz")]
    identity_class = class_of[IDENTITY]
    products = product_class_table(classes)
    states = signed_permutation_closure(
        {(source_class, identity_class, IDENTITY_MATRIX)}
    )
    layer_sizes = [len(states)]
    compatible_by_depth = []
    for depth in range(6):
        compatible = tuple(
            sorted(
                {
                    matrix
                    for left_class, right_class, matrix in states
                    if left_class == target_class
                    and right_class == identity_class
                    and matrix[0] == 1
                    and matrix[2] == 0
                }
            )
        )
        compatible_by_depth.append(compatible)
        if depth == 5:
            break
        states = next_multiplication_layer(states, products)
        layer_sizes.append(len(states))

    if tuple(layer_sizes) != EXPECTED_LAYER_SIZES:
        raise AssertionError("the homology-compatible reachability layers drifted")
    if any(compatible_by_depth[depth] for depth in range(5)):
        raise AssertionError("a homology-compatible target appeared below depth five")
    compatible_matrices = compatible_by_depth[5]
    if compatible_matrices != EXPECTED_COMPATIBLE_MATRICES:
        raise AssertionError("the depth-five compatible matrix fiber drifted")
    if IDENTITY_MATRIX not in compatible_matrices:
        raise AssertionError("the identity-matrix depth-five witness disappeared")
    witness_matrix = depth_five_witness_matrix()
    witness_pairs = depth_five_witness_pairs()
    if witness_matrix not in compatible_matrices:
        raise AssertionError("the explicit depth-five witness left the target fiber")

    return HomologyDepthDecision(
        layer_sizes=tuple(layer_sizes),
        first_compatible_depth=5,
        compatible_matrices=compatible_matrices,
        identity_matrix_reached=True,
        witness_matrix=witness_matrix,
        witness_pairs=witness_pairs,
        verdict="FIVE_TOTAL_ROW_MULTIPLICATIONS_REQUIRED_IN_COMBINED_SHADOW",
    )


if __name__ == "__main__":
    print(decide_homology_compatible_depth())
