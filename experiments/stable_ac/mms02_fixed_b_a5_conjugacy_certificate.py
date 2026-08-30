"""A5 obstruction to every B-confined MMS02 terminal pair path."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations
from typing import cast

A_WORD = "xzYXyxZXYxyZ"
B_WORD = "XyxZXYXyxzXYxy"
U_WORD = "zYX"
V_WORD = "Xyz"

Permutation = tuple[int, int, int, int, int]

IDENTITY: Permutation = (0, 1, 2, 3, 4)
IMAGES: dict[str, Permutation] = {
    "x": (0, 1, 3, 4, 2),
    "y": (0, 2, 3, 1, 4),
    "z": (2, 0, 1, 3, 4),
}


def compose(left: Permutation, right: Permutation) -> Permutation:
    return cast(Permutation, tuple(left[right[index]] for index in range(5)))


def inverse(value: Permutation) -> Permutation:
    result = [0] * 5
    for index, image in enumerate(value):
        result[image] = index
    return cast(Permutation, tuple(result))


def evaluate_word(word: str) -> Permutation:
    result = IDENTITY
    for letter in word:
        image = IMAGES[letter.lower()]
        if letter.isupper():
            image = inverse(image)
        result = compose(result, image)
    return result


def parity(value: Permutation) -> int:
    inversions = sum(
        value[left] > value[right]
        for left in range(5)
        for right in range(left + 1, 5)
    )
    return inversions % 2


def conjugate(conjugator: Permutation, value: Permutation) -> Permutation:
    return compose(compose(conjugator, value), inverse(conjugator))


def cycle_type(value: Permutation) -> tuple[int, ...]:
    seen: set[int] = set()
    lengths = []
    for start in range(5):
        if start in seen:
            continue
        current = start
        length = 0
        while current not in seen:
            seen.add(current)
            current = value[current]
            length += 1
        if length > 1:
            lengths.append(length)
    return tuple(sorted(lengths, reverse=True))


def generated_subgroup(generators: tuple[Permutation, ...]) -> frozenset[Permutation]:
    subgroup = {IDENTITY}
    frontier = [IDENTITY]
    while frontier:
        current = frontier.pop()
        for generator in generators:
            candidate = compose(current, generator)
            if candidate not in subgroup:
                subgroup.add(candidate)
                frontier.append(candidate)
    return frozenset(subgroup)


@dataclass(frozen=True)
class FixedBConjugacyDecision:
    source_image: Permutation
    target_image: Permutation
    source_inverse_image: Permutation
    target_inverse_image: Permutation
    source_a5_class_size: int
    target_a5_class_size: int
    a5_conjugator_counts: tuple[tuple[int, int], tuple[int, int]]
    s5_odd_conjugator_counts: tuple[tuple[int, int], tuple[int, int]]
    verdict: str


def decide_fixed_b_conjugacy() -> FixedBConjugacyDecision:
    if evaluate_word(A_WORD) != IDENTITY or evaluate_word(B_WORD) != IDENTITY:
        raise AssertionError("the A5 assignment no longer kills the base rows")

    a5 = generated_subgroup(tuple(IMAGES.values()))
    if len(a5) != 60 or any(parity(value) for value in a5):
        raise AssertionError("the certified quotient is no longer A5")

    source_image = evaluate_word(U_WORD)
    target_image = evaluate_word(V_WORD)
    source_inverse_image = inverse(source_image)
    target_inverse_image = inverse(target_image)
    if source_image != (2, 3, 4, 0, 1):
        raise AssertionError("the source killer image drifted")
    if target_image != (2, 0, 4, 1, 3):
        raise AssertionError("the target killer image drifted")
    if conjugate((0, 3, 2, 1, 4), source_image) != target_image:
        raise AssertionError("the displayed odd cross-class conjugator drifted")

    source_orientations = (source_image, source_inverse_image)
    target_orientations = (target_image, target_inverse_image)
    if any(cycle_type(value) != (5,) for value in source_orientations + target_orientations):
        raise AssertionError("an endpoint left the 5-cycle classes")

    all_s5 = tuple(permutations(range(5)))
    a5_counts = []
    odd_counts = []
    for source in source_orientations:
        a5_row = []
        odd_row = []
        for target in target_orientations:
            conjugators = tuple(
                candidate
                for candidate in all_s5
                if conjugate(candidate, source) == target
            )
            a5_row.append(sum(parity(candidate) == 0 for candidate in conjugators))
            odd_row.append(sum(parity(candidate) == 1 for candidate in conjugators))
        a5_counts.append(tuple(a5_row))
        odd_counts.append(tuple(odd_row))

    source_class = frozenset(conjugate(candidate, source_image) for candidate in a5)
    target_class = frozenset(conjugate(candidate, target_image) for candidate in a5)
    if len(source_class) != 12 or len(target_class) != 12:
        raise AssertionError("a split 5-cycle class has the wrong size")
    if source_class & target_class:
        raise AssertionError("the two split A5 classes merged")
    if source_inverse_image not in source_class or target_inverse_image not in target_class:
        raise AssertionError("a split A5 class is no longer inversion-stable")
    if conjugate((0, 4, 3, 2, 1), source_image) != source_inverse_image:
        raise AssertionError("the displayed source reverser drifted")
    if conjugate((0, 2, 1, 4, 3), target_image) != target_inverse_image:
        raise AssertionError("the displayed target reverser drifted")

    a5_conjugator_counts = tuple(a5_counts)
    s5_odd_conjugator_counts = tuple(odd_counts)
    if a5_conjugator_counts != ((0, 0), (0, 0)):
        raise AssertionError("an A5 endpoint conjugator appeared")
    if s5_odd_conjugator_counts != ((5, 5), (5, 5)):
        raise AssertionError("the complete S5 conjugator parity table drifted")

    return FixedBConjugacyDecision(
        source_image=source_image,
        target_image=target_image,
        source_inverse_image=source_inverse_image,
        target_inverse_image=target_inverse_image,
        source_a5_class_size=len(source_class),
        target_a5_class_size=len(target_class),
        a5_conjugator_counts=a5_conjugator_counts,
        s5_odd_conjugator_counts=s5_odd_conjugator_counts,
        verdict="EVERY_B_CONFINED_TERMINAL_PAIR_PATH_OBSTRUCTED",
    )


if __name__ == "__main__":
    print(decide_fixed_b_conjugacy())
