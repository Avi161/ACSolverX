"""Literal one-relator coordinates for the MMS02 depth-five lift gate."""

from __future__ import annotations

from dataclasses import dataclass

A_WORD = "xzYXyxZXYxyZ"
B_WORD = "XyxZXYXyxzXYxy"
U_INVERSE_WORD = "xyZ"
V_WORD = "Xyz"
R_STAR = "YZYzYzYZyzyZYzYzYZYzyZyZyz"

FORWARD = {
    "x": "zXyZ",
    "y": "y",
    "z": "zYxZYzYzYxZyzXyZ",
}
DELETE_X = {"x": "", "y": "y", "z": "z"}

EXPECTED_COLLAPSED_GENERATORS = (
    "zyZ",
    "y",
    "zYZYzYzYZyzyZ",
)
EXPECTED_COLLAPSED_ENDPOINTS = (
    "zyZyzYZYzyZyZyzyZ",
    "zYZyzYZYzYzYZyzyZ",
)


def inverse_word(word: str) -> str:
    return word[::-1].swapcase()


def reduce_word(word: str) -> str:
    stack = []
    for letter in word:
        if stack and stack[-1] == letter.swapcase():
            stack.pop()
        else:
            stack.append(letter)
    return "".join(stack)


def cyclic_reduce(word: str) -> str:
    reduced = reduce_word(word)
    while reduced and reduced[0] == reduced[-1].swapcase():
        reduced = reduce_word(reduced[1:-1])
    return reduced


def apply_images(word: str, images: dict[str, str]) -> str:
    expanded = []
    for letter in word:
        image = images[letter.lower()]
        if letter.isupper():
            image = inverse_word(image)
        expanded.append(image)
    return reduce_word("".join(expanded))


def cyclic_rotations(word: str) -> tuple[str, ...]:
    return tuple(word[index:] + word[:index] for index in range(len(word)))


def exponent_vector(word: str) -> tuple[int, int]:
    return word.count("y") - word.count("Y"), word.count("z") - word.count("Z")


@dataclass(frozen=True)
class LiftEquationCoordinateDecision:
    collapsed_generators: tuple[str, str, str]
    collapsed_endpoints: tuple[str, str]
    relator_exponent_vector: tuple[int, int]
    verdict: str


def decide_lift_equation_coordinates() -> LiftEquationCoordinateDecision:
    if apply_images(B_WORD, FORWARD) != "x":
        raise AssertionError("the Tietze deletion row drifted")

    collapsed_generators = tuple(
        apply_images(apply_images(generator, FORWARD), DELETE_X)
        for generator in "xyz"
    )
    if collapsed_generators != EXPECTED_COLLAPSED_GENERATORS:
        raise AssertionError("the collapsed original-generator images drifted")

    collapsed_endpoints = tuple(
        apply_images(apply_images(word, FORWARD), DELETE_X)
        for word in (U_INVERSE_WORD, V_WORD)
    )
    if collapsed_endpoints != EXPECTED_COLLAPSED_ENDPOINTS:
        raise AssertionError("the collapsed depth-five endpoints drifted")

    transformed_relator = apply_images(
        apply_images(A_WORD, FORWARD),
        DELETE_X,
    )
    cyclic_relator = cyclic_reduce(transformed_relator)
    unoriented_rotations = set(cyclic_rotations(cyclic_relator))
    unoriented_rotations.update(cyclic_rotations(inverse_word(cyclic_relator)))
    if R_STAR not in unoriented_rotations:
        raise AssertionError("the collapsed one-relator orientation drifted")
    relator_exponent_vector = exponent_vector(R_STAR)
    if len(R_STAR) != 26 or relator_exponent_vector != (-3, 1):
        raise AssertionError("the Magnus exponent vector drifted")

    return LiftEquationCoordinateDecision(
        collapsed_generators=collapsed_generators,
        collapsed_endpoints=collapsed_endpoints,
        relator_exponent_vector=relator_exponent_vector,
        verdict="EXACT_DEPTH_FIVE_LIFT_EQUATION_COORDINATES_PINNED",
    )


if __name__ == "__main__":
    print(decide_lift_equation_coordinates())
