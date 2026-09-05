from __future__ import annotations

from collections.abc import Mapping


GENERATORS = "xtzq"
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

R = "xxxTTTT"
B = "Zxt"
D = "TzxZ"
U = R + B

WordMap = Mapping[str, str]


def free_reduce(word: str) -> str:
    stack: list[str] = []
    for letter in word:
        if stack and INVERSE_LETTER[letter] == stack[-1]:
            stack.pop()
        else:
            stack.append(letter)
    return "".join(stack)


def inverse_word(word: str) -> str:
    return "".join(INVERSE_LETTER[letter] for letter in reversed(word))


def conjugate(conjugator: str, word: str) -> str:
    return free_reduce(conjugator + word + inverse_word(conjugator))


def substitute(word: str, images: WordMap) -> str:
    result = ""
    for letter in word:
        image = images[letter.lower()]
        if letter.isupper():
            image = inverse_word(image)
        result = free_reduce(result + image)
    return result


def compose(outer: WordMap, inner: WordMap) -> dict[str, str]:
    return {
        generator: substitute(inner[generator], outer)
        for generator in GENERATORS
    }


def multiply_target(
    relators: tuple[str, ...],
    target: int,
    source: int,
    conjugator: str,
    sign: int = 1,
) -> tuple[str, ...]:
    source_word = relators[source]
    if sign == -1:
        source_word = inverse_word(source_word)
    updated = list(relators)
    updated[target] = free_reduce(
        relators[target] + conjugate(conjugator, source_word)
    )
    return tuple(updated)


def invert_target(
    relators: tuple[str, ...],
    target: int,
) -> tuple[str, ...]:
    updated = list(relators)
    updated[target] = inverse_word(updated[target])
    return tuple(updated)


def conjugate_target(
    relators: tuple[str, ...],
    target: int,
    conjugator: str,
) -> tuple[str, ...]:
    updated = list(relators)
    updated[target] = conjugate(conjugator, updated[target])
    return tuple(updated)


def checkpoint_and_quotient():
    alpha_u = {"x": "x", "t": "t", "z": "z", "q": U + "q"}
    alpha_u_inverse = {
        "x": "x",
        "t": "t",
        "z": "z",
        "q": inverse_word(U) + "q",
    }
    beta = {"x": "qxQ", "t": "t", "z": "z", "q": "q"}
    beta_inverse = {"x": "Qxq", "t": "t", "z": "z", "q": "q"}
    phi = compose(beta, alpha_u)
    phi_inverse = compose(alpha_u_inverse, beta_inverse)
    kill_q = {"x": "x", "t": "t", "z": "z", "q": ""}

    def quotient(word: str) -> str:
        return substitute(substitute(word, phi_inverse), kill_q)

    beta_r = substitute(R, beta)
    primitive = free_reduce(substitute(U, beta) + "q")
    return (beta_r, primitive, D, "q"), quotient


def test_checkpoint_has_the_expected_immediate_quotient():
    checkpoint, quotient = checkpoint_and_quotient()
    beta_r, primitive, d_word, q_word = checkpoint
    p_x = free_reduce(U + "x" + inverse_word(U))

    assert quotient(beta_r) == R
    assert quotient(primitive) == ""
    assert quotient(d_word) == free_reduce("Tz" + p_x + "Z")
    assert quotient(q_word) == inverse_word(U)


def test_mixed_post_primitive_history_commutes_with_deletion():
    checkpoint, quotient = checkpoint_and_quotient()

    upstairs = conjugate_target(checkpoint, 1, "t")
    upstairs = invert_target(upstairs, 1)
    assert quotient(upstairs[1]) == ""

    upstairs = multiply_target(upstairs, 3, 2, "x")

    downstairs = (
        quotient(checkpoint[0]),
        quotient(checkpoint[2]),
        quotient(checkpoint[3]),
    )
    downstairs = multiply_target(
        downstairs,
        2,
        1,
        quotient("x"),
    )

    upstairs = multiply_target(upstairs, 2, 1, "z")
    assert (
        quotient(upstairs[0]),
        quotient(upstairs[2]),
        quotient(upstairs[3]),
    ) == downstairs

    upstairs = multiply_target(upstairs, 0, 3, "t")
    upstairs = invert_target(upstairs, 3)
    upstairs = conjugate_target(upstairs, 2, "qx")

    quotient_after_history = (
        quotient(upstairs[0]),
        quotient(upstairs[2]),
        quotient(upstairs[3]),
    )

    assert quotient(checkpoint[1]) == ""

    downstairs = multiply_target(
        downstairs,
        0,
        2,
        quotient("t"),
    )
    downstairs = invert_target(downstairs, 2)
    downstairs = conjugate_target(
        downstairs,
        1,
        quotient("qx"),
    )

    assert quotient_after_history == downstairs


if __name__ == "__main__":
    test_checkpoint_has_the_expected_immediate_quotient()
    test_mixed_post_primitive_history_commutes_with_deletion()
