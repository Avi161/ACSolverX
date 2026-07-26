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
BETA_R = "qxxxQTTTT"
W = "qxxxQTTTTZqxQtq"
Q_SOURCE = "q" + BETA_R

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


def automorphisms():
    identity = {generator: generator for generator in GENERATORS}
    beta = {"x": "qxQ", "t": "t", "z": "z", "q": "q"}
    beta_inverse = {
        "x": "Qxq",
        "t": "t",
        "z": "z",
        "q": "q",
    }
    delta = {"x": "x", "t": "t", "z": "z", "q": "q" + R}
    delta_inverse = {
        "x": "x",
        "t": "t",
        "z": "z",
        "q": "q" + inverse_word(R),
    }
    tau = compose(beta, delta)
    tau_inverse = compose(delta_inverse, beta_inverse)

    assert compose(tau_inverse, tau) == identity
    assert compose(tau, tau_inverse) == identity
    assert tau["q"] == Q_SOURCE
    return tau, tau_inverse


def deletion_map():
    _, tau_inverse = automorphisms()
    kill_q = {"x": "x", "t": "t", "z": "z", "q": ""}
    return {
        generator: substitute(tau_inverse[generator], kill_q)
        for generator in GENERATORS
    }


def exact_endpoint():
    sigma = deletion_map()
    return (
        substitute(BETA_R, sigma),
        substitute(W, sigma),
        substitute(D, sigma),
    )


def test_tau_and_exact_deletion_map():
    _, tau_inverse = automorphisms()
    sigma = deletion_map()

    assert tau_inverse["q"] == "q" + inverse_word(R)
    assert sigma == {
        "x": free_reduce(R + "x" + inverse_word(R)),
        "t": "t",
        "z": "z",
        "q": inverse_word(R),
    }
    assert substitute(Q_SOURCE, sigma) == ""


def test_exact_ak_endpoint():
    first, middle, last = exact_endpoint()
    expected_middle = free_reduce(R + B + inverse_word(R))
    expected_last = free_reduce(
        "Tz" + R + "x" + inverse_word(R) + "Z"
    )

    assert first == R
    assert middle == expected_middle
    assert middle == free_reduce(U + inverse_word(R))
    assert last == expected_last


def test_representative_source_traffic_vanishes_in_every_slot():
    sigma = deletion_map()
    endpoint = exact_endpoint()
    factors = (
        conjugate("z", Q_SOURCE),
        conjugate("qX", inverse_word(Q_SOURCE)),
        conjugate(free_reduce("Z" + R + "q"), Q_SOURCE),
        conjugate("tqzQ", inverse_word(Q_SOURCE)),
    )
    traffic = (
        "",
        factors[0],
        factors[1],
        free_reduce(factors[0] + factors[2] + factors[1]),
        free_reduce(factors[3] + factors[0] + factors[2]),
    )

    for multiplier in traffic:
        assert substitute(multiplier, sigma) == ""
        for original, expected in zip((BETA_R, W, D), endpoint):
            assert substitute(original + multiplier, sigma) == expected


def test_middle_relator_returns_by_one_conjugation():
    _, middle, _ = exact_endpoint()

    assert conjugate(inverse_word(R), middle) == B


def test_two_r_factors_return_last_relator():
    _, _, last = exact_endpoint()
    first_factor = conjugate("zX", R)
    second_factor = conjugate("z", inverse_word(R))

    assert free_reduce(inverse_word(D) + last) == free_reduce(
        first_factor + second_factor
    )
    assert free_reduce(
        last
        + inverse_word(second_factor)
        + inverse_word(first_factor)
    ) == D


if __name__ == "__main__":
    test_tau_and_exact_deletion_map()
    test_exact_ak_endpoint()
    test_representative_source_traffic_vanishes_in_every_slot()
    test_middle_relator_returns_by_one_conjugation()
    test_two_r_factors_return_last_relator()
