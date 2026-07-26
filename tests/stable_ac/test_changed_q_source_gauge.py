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
P = "xt"
B = "Zxt"
D = "TzxZ"
U = R + B
Q_SOURCE = "q" + D
W = "qxxxQTTTTZqxQtq"

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


def maps():
    identity = {generator: generator for generator in GENERATORS}
    tau = {"x": "x", "t": "t", "z": "z", "q": Q_SOURCE}
    tau_inverse = {
        "x": "x",
        "t": "t",
        "z": "z",
        "q": "q" + inverse_word(D),
    }
    sigma_d = {
        "x": "x",
        "t": "t",
        "z": "z",
        "q": inverse_word(D),
    }

    assert compose(tau_inverse, tau) == identity
    assert compose(tau, tau_inverse) == identity
    return sigma_d


def exact_words():
    sigma_d = maps()
    beta_r = "qxxxQTTTT"
    beta_p = "qxQt"
    r_d = substitute(beta_r, sigma_d)
    p_d = substitute(beta_p, sigma_d)
    w_d = substitute(W, sigma_d)
    return r_d, p_d, w_d


def d_factors():
    r_d, p_d, _ = exact_words()
    r_difference = free_reduce(inverse_word(R) + r_d)
    p_difference = free_reduce(inverse_word(P) + p_d)
    d1 = conjugate(inverse_word(R), inverse_word(D))
    d2 = conjugate("tttt", D)
    e1 = conjugate(inverse_word(P), inverse_word(D))
    e2 = conjugate("T", D)
    return r_difference, p_difference, (d1, d2), (e1, e2)


def test_qd_transvection_and_exact_deletion_images():
    sigma_d = maps()
    r_d, p_d, w_d = exact_words()

    assert substitute(Q_SOURCE, sigma_d) == ""
    assert r_d == free_reduce(inverse_word(D) + "xxx" + D + "TTTT")
    assert p_d == free_reduce(inverse_word(D) + "x" + D + "t")
    assert w_d == free_reduce(
        r_d + "Z" + p_d + inverse_word(D)
    )
    assert substitute(D, sigma_d) == D


def test_representative_qd_source_traffic_vanishes_on_deletion():
    sigma_d = maps()
    r_d, _, w_d = exact_words()
    factors = (
        conjugate("z", Q_SOURCE),
        conjugate("qX", inverse_word(Q_SOURCE)),
        conjugate(free_reduce("Z" + D + "q"), Q_SOURCE),
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
        assert substitute(multiplier, sigma_d) == ""
        assert substitute("qxxxQTTTT" + multiplier, sigma_d) == r_d
        assert substitute(W + multiplier, sigma_d) == w_d
        assert substitute(D + multiplier, sigma_d) == D


def test_two_d_factor_differences_and_reverse_return():
    r_d, _, _ = exact_words()
    r_difference, p_difference, r_factors, p_factors = d_factors()

    assert r_difference == free_reduce("".join(r_factors))
    assert p_difference == free_reduce("".join(p_factors))
    assert free_reduce(
        r_d
        + inverse_word(r_factors[1])
        + inverse_word(r_factors[0])
    ) == R


def test_five_d_factors_return_wd_to_u():
    _, _, w_d = exact_words()
    _, _, r_factors, p_factors = d_factors()
    outer = inverse_word(P) + "z"
    five_factors = (
        conjugate(outer, r_factors[0]),
        conjugate(outer, r_factors[1]),
        p_factors[0],
        p_factors[1],
        inverse_word(D),
    )

    assert free_reduce(inverse_word(U) + w_d) == free_reduce(
        "".join(five_factors)
    )
    returned = w_d
    for factor in reversed(five_factors):
        returned = free_reduce(returned + inverse_word(factor))
    assert returned == U


def test_one_r_factor_returns_u_to_b():
    factor = conjugate(inverse_word(B), inverse_word(R))

    assert free_reduce(inverse_word(U) + B) == factor
    assert free_reduce(U + factor) == B


if __name__ == "__main__":
    test_qd_transvection_and_exact_deletion_images()
    test_representative_qd_source_traffic_vanishes_on_deletion()
    test_two_d_factor_differences_and_reverse_return()
    test_five_d_factors_return_wd_to_u()
    test_one_r_factor_returns_u_to_b()
