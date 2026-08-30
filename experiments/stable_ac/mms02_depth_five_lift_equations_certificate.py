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

IndexedLetter = tuple[int, int]
IndexedWord = tuple[IndexedLetter, ...]

EXPECTED_MAGNUS_RELATOR: IndexedWord = (
    (-1, -1),
    (-2, 1),
    (0, 1),
    (-1, -1),
    (0, 1),
    (1, -1),
    (0, 1),
    (2, 1),
    (1, -1),
    (0, 1),
    (1, -1),
    (-1, -1),
    (0, 1),
)
EXPECTED_D2_WORD: IndexedWord = (
    (0, -1),
    (1, 1),
    (0, -1),
    (-1, 1),
    (0, -1),
    (-2, -1),
    (-1, 1),
    (0, -1),
    (-1, 1),
    (1, 1),
    (0, -1),
    (1, 1),
)
EXPECTED_ENDPOINT_BASE_WORDS: tuple[IndexedWord, IndexedWord] = (
    (
        (0, 1),
        (1, -1),
        (0, -1),
        (1, 1),
        (0, -1),
        (-1, 1),
        (0, -1),
        (-2, -1),
        (-1, 1),
        (1, -1),
    ),
    (
        (1, 1),
        (0, -1),
        (1, 1),
        (-1, -1),
        (-2, 1),
        (0, 1),
        (-1, -1),
        (0, 1),
        (1, -1),
        (0, 1),
    ),
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


def inverse_indexed_word(word: IndexedWord) -> IndexedWord:
    return tuple((index, -sign) for index, sign in reversed(word))


def reduce_indexed_word(word: IndexedWord) -> IndexedWord:
    stack: list[IndexedLetter] = []
    for letter in word:
        if stack and stack[-1] == (letter[0], -letter[1]):
            stack.pop()
        else:
            stack.append(letter)
    return tuple(stack)


def magnus_rewrite(word: str) -> tuple[IndexedWord, int]:
    expanded = apply_images(word, {"y": "y", "z": "yyyd"})
    height = 0
    indexed = []
    for letter in expanded:
        if letter == "y":
            height += 1
        elif letter == "Y":
            height -= 1
        elif letter == "d":
            indexed.append((height, 1))
        elif letter == "D":
            indexed.append((height, -1))
        else:
            raise AssertionError("the Magnus alphabet drifted")
    return tuple(indexed), height


def substitute_d2(word: IndexedWord, d2_word: IndexedWord) -> IndexedWord:
    expanded = []
    for letter in word:
        if letter == (2, 1):
            expanded.extend(d2_word)
        elif letter == (2, -1):
            expanded.extend(inverse_indexed_word(d2_word))
        else:
            expanded.append(letter)
    return reduce_indexed_word(tuple(expanded))


def apply_indexed_images(
    word: IndexedWord, images: dict[int, IndexedWord]
) -> IndexedWord:
    expanded = []
    for index, sign in word:
        image = images[index]
        if sign == -1:
            image = inverse_indexed_word(image)
        expanded.extend(image)
    return reduce_indexed_word(tuple(expanded))


@dataclass(frozen=True)
class LiftEquationCoordinateDecision:
    collapsed_generators: tuple[str, str, str]
    collapsed_endpoints: tuple[str, str]
    relator_exponent_vector: tuple[int, int]
    magnus_relator: IndexedWord
    d2_word: IndexedWord
    endpoint_base_words: tuple[IndexedWord, IndexedWord]
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

    magnus_relator, relator_height = magnus_rewrite(R_STAR)
    if relator_height != 0 or magnus_relator != EXPECTED_MAGNUS_RELATOR:
        raise AssertionError("the indexed Magnus relator drifted")
    if magnus_relator.count((-2, 1)) != 1 or magnus_relator.count((2, 1)) != 1:
        raise AssertionError("a Magnus extremal occurrence stopped being unique")
    d2_position = magnus_relator.index((2, 1))
    d2_word = reduce_indexed_word(
        inverse_indexed_word(magnus_relator[:d2_position])
        + inverse_indexed_word(magnus_relator[d2_position + 1 :])
    )
    if d2_word != EXPECTED_D2_WORD or d2_word.count((-2, -1)) != 1:
        raise AssertionError("the free-base d2 elimination word drifted")

    endpoint_base_words = []
    for word, shift in zip(collapsed_endpoints, (-3, -2), strict=True):
        indexed, height = magnus_rewrite(word)
        if height != 1:
            raise AssertionError("a terminal endpoint left HNN height one")
        shifted = tuple((index + shift, sign) for index, sign in indexed)
        endpoint_base_words.append(substitute_d2(shifted, d2_word))
    if tuple(endpoint_base_words) != EXPECTED_ENDPOINT_BASE_WORDS:
        raise AssertionError("the endpoint HNN base words drifted")

    phi_images = {
        -2: ((-1, 1),),
        -1: ((0, 1),),
        0: ((1, 1),),
        1: d2_word,
    }
    d_minus_two_position = d2_word.index((-2, -1))
    before = d2_word[:d_minus_two_position]
    after = d2_word[d_minus_two_position + 1 :]
    lower_index = {-1: -2, 0: -1, 1: 0}
    phi_inverse_images = {
        -2: (
            tuple((lower_index[index], sign) for index, sign in after)
            + ((1, -1),)
            + tuple((lower_index[index], sign) for index, sign in before)
        ),
        -1: ((-2, 1),),
        0: ((-1, 1),),
        1: ((0, 1),),
    }
    for index in range(-2, 2):
        generator = ((index, 1),)
        if apply_indexed_images(
            apply_indexed_images(generator, phi_images), phi_inverse_images
        ) != generator:
            raise AssertionError("the Magnus monodromy lost its left inverse")
        if apply_indexed_images(
            apply_indexed_images(generator, phi_inverse_images), phi_images
        ) != generator:
            raise AssertionError("the Magnus monodromy lost its right inverse")

    return LiftEquationCoordinateDecision(
        collapsed_generators=collapsed_generators,
        collapsed_endpoints=collapsed_endpoints,
        relator_exponent_vector=relator_exponent_vector,
        magnus_relator=magnus_relator,
        d2_word=d2_word,
        endpoint_base_words=tuple(endpoint_base_words),
        verdict="EXACT_DEPTH_FIVE_LIFT_EQUATION_COORDINATES_PINNED",
    )


if __name__ == "__main__":
    print(decide_lift_equation_coordinates())
