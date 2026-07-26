from __future__ import annotations

from collections.abc import Mapping


INVERSE_LETTER = {
    "x": "X",
    "X": "x",
    "t": "T",
    "T": "t",
    "z": "Z",
    "Z": "z",
    "q": "Q",
    "Q": "q",
}
GENERATORS = ("x", "t", "z", "q")

A = "qxxxQTTTT"
D = "TzxZ"

FOX_SLICE_RESIDUAL_CASES = frozenset({
    (1, 1),
    (-1, 0),
    (-1, 1),
})


def free_reduce(word: str) -> str:
    stack: list[str] = []
    for letter in word:
        if stack and INVERSE_LETTER[letter] == stack[-1]:
            stack.pop()
        else:
            stack.append(letter)
    return "".join(stack)


def inverse_word(word: str) -> str:
    return "".join(
        INVERSE_LETTER[letter] for letter in reversed(word)
    )


def abelian_exponent_sums(word: str) -> dict[str, int]:
    result = {generator: 0 for generator in GENERATORS}
    for letter in word:
        result[letter.lower()] += 1 if letter.islower() else -1
    return result


def word_value_mod(
    word: str,
    values: Mapping[str, int],
    modulus: int,
) -> int:
    value = 1
    for letter in word:
        image = values[letter.lower()] % modulus
        if letter.isupper():
            image = pow(image, -1, modulus)
        value = value * image % modulus
    return value


def fox_gradient_mod(
    word: str,
    values: Mapping[str, int],
    modulus: int,
) -> tuple[int, ...]:
    gradient = {generator: 0 for generator in GENERATORS}
    prefix = 1

    for letter in word:
        generator = letter.lower()
        image = values[generator] % modulus
        if letter.islower():
            gradient[generator] += prefix
            prefix = prefix * image % modulus
        else:
            inverse_image = pow(image, -1, modulus)
            gradient[generator] -= prefix * inverse_image
            prefix = prefix * inverse_image % modulus

    return tuple(
        gradient[generator] % modulus for generator in GENERATORS
    )


def finite_modulus_witness(
    sigma: int,
    q_exponent: int,
) -> int | None:
    if sigma not in (1, -1):
        raise ValueError("sigma must be +1 or -1")

    if q_exponent >= 0:
        obstruction_integer = (
            4**q_exponent
            + 4 * sigma * 3**q_exponent
        )
    else:
        positive_exponent = -q_exponent
        obstruction_integer = (
            3**positive_exponent
            + 4 * sigma * 4**positive_exponent
        )

    modulus = abs(obstruction_integer)
    while modulus and modulus % 2 == 0:
        modulus //= 2
    while modulus and modulus % 3 == 0:
        modulus //= 3

    return modulus if modulus > 1 else None
