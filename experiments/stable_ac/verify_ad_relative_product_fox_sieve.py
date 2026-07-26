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


def fox_gradient_qz(
    word: str,
) -> tuple[dict[str, int], ...]:
    gradient = {
        generator: {} for generator in GENERATORS
    }
    prefix = ""

    def add_term(
        coordinate: dict[str, int],
        group_word: str,
        coefficient: int,
    ) -> None:
        coordinate[group_word] = (
            coordinate.get(group_word, 0) + coefficient
        )
        if coordinate[group_word] == 0:
            del coordinate[group_word]

    for letter in word:
        generator = letter.lower()
        if letter.islower():
            add_term(gradient[generator], prefix, 1)
            if generator in {"q", "z"}:
                prefix = free_reduce(prefix + letter)
        else:
            inverse_image = (
                letter if generator in {"q", "z"} else ""
            )
            prefix = free_reduce(prefix + inverse_image)
            add_term(gradient[generator], prefix, -1)

    return tuple(
        gradient[generator] for generator in GENERATORS
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


def project_qz(word: str) -> str:
    return free_reduce(
        "".join(
            letter for letter in word
            if letter.lower() in {"q", "z"}
        )
    )


def qz_axis_power(projected_word: str) -> int | None:
    projected_word = free_reduce(projected_word)
    if not projected_word:
        return 0

    positive_axis = "qZ"
    negative_axis = inverse_word(positive_axis)
    if (
        len(projected_word) % len(positive_axis) == 0
        and projected_word
        == positive_axis * (
            len(projected_word) // len(positive_axis)
        )
    ):
        return len(projected_word) // len(positive_axis)
    if (
        len(projected_word) % len(negative_axis) == 0
        and projected_word
        == negative_axis * (
            len(projected_word) // len(negative_axis)
        )
    ):
        return -len(projected_word) // len(negative_axis)
    return None


def projection_sieve_kind(
    conjugator: str,
    sigma: int,
) -> str:
    projected = project_qz(conjugator)
    axis_power = qz_axis_power(projected)
    if axis_power is None:
        return "induced-module"
    if finite_modulus_witness(sigma, axis_power) is not None:
        return "cyclic-modular"
    return "residual"
