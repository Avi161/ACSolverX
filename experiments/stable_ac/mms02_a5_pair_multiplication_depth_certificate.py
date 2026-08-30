"""Minimum A5-visible multiplication depth for the MMS02 terminal pair."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from experiments.stable_ac.mms02_fixed_b_a5_conjugacy_certificate import (
    IDENTITY,
    IMAGES,
    Permutation,
    compose,
    conjugate,
    evaluate_word,
    inverse,
)

U_WORD = "zYX"
V_WORD = "Xyz"

Pair = tuple[Permutation, Permutation]
Matrix = tuple[tuple[int, int], tuple[int, int]]


def zero_cost_neighbors(pair: Pair) -> tuple[Pair, ...]:
    left, right = pair
    conjugators = tuple(IMAGES.values()) + tuple(inverse(value) for value in IMAGES.values())
    neighbors = [
        (inverse(left), right),
        (left, inverse(right)),
        (right, left),
    ]
    neighbors.extend((conjugate(value, left), right) for value in conjugators)
    neighbors.extend((left, conjugate(value, right)) for value in conjugators)
    return tuple(neighbors)


def multiplication_neighbors(pair: Pair) -> tuple[Pair, Pair]:
    left, right = pair
    return (compose(left, right), right), (left, compose(right, left))


def minimum_multiplication_depth(source: Pair, target: Pair) -> int:
    distances = {source: 0}
    queue = deque((source,))
    while queue:
        current = queue.popleft()
        distance = distances[current]
        if current == target:
            return distance
        for neighbor in zero_cost_neighbors(current):
            if distance < distances.get(neighbor, 10**9):
                distances[neighbor] = distance
                queue.appendleft(neighbor)
        for neighbor in multiplication_neighbors(current):
            next_distance = distance + 1
            if next_distance < distances.get(neighbor, 10**9):
                distances[neighbor] = next_distance
                queue.append(neighbor)
    raise AssertionError("the finite A5 pair orbit was not exhausted correctly")


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
class PairDepthDecision:
    minimum_depth: int
    normalized_cycle: Permutation
    transcript: tuple[Pair, ...]
    nielsen_matrix: Matrix
    source_homology_image: tuple[int, int]
    verdict: str


def decide_pair_multiplication_depth() -> PairDepthDecision:
    source = evaluate_word(U_WORD)
    target = evaluate_word(V_WORD)
    minimum_depth = minimum_multiplication_depth(
        (source, IDENTITY),
        (target, IDENTITY),
    )
    if minimum_depth != 4:
        raise AssertionError("the complete A5 multiplication depth drifted")

    normalizer = (1, 2, 0, 3, 4)
    normalized_cycle = conjugate(inverse(normalizer), source)
    if normalized_cycle != (3, 4, 1, 2, 0):
        raise AssertionError("the normalized source cycle drifted")
    square = compose(normalized_cycle, normalized_cycle)
    cube = compose(normalized_cycle, square)
    fifth = compose(square, cube)
    if square != target or cube != inverse(target) or fifth != IDENTITY:
        raise AssertionError("the order-five quotient transcript drifted")

    transcript = (
        (source, IDENTITY),
        (source, source),
        (normalized_cycle, normalized_cycle),
        (square, normalized_cycle),
        (square, cube),
        (square, IDENTITY),
    )
    if transcript[-1] != (target, IDENTITY):
        raise AssertionError("the quotient transcript no longer reaches the target")

    row_one = ((1, 1), (0, 1))
    row_two = ((1, 0), (1, 1))
    nielsen_matrix = matrix_multiply(
        row_two,
        matrix_multiply(row_two, matrix_multiply(row_one, row_two)),
    )
    if nielsen_matrix != ((2, 1), (5, 3)):
        raise AssertionError("the quotient transcript Nielsen matrix drifted")
    source_homology_image = (-nielsen_matrix[0][0], -nielsen_matrix[1][0])
    if source_homology_image != (-2, -5):
        raise AssertionError("the nonlifting homology image drifted")

    return PairDepthDecision(
        minimum_depth=minimum_depth,
        normalized_cycle=normalized_cycle,
        transcript=transcript,
        nielsen_matrix=nielsen_matrix,
        source_homology_image=source_homology_image,
        verdict="FOUR_A5_VISIBLE_MULTIPLICATIONS_REQUIRED",
    )


if __name__ == "__main__":
    print(decide_pair_multiplication_depth())
