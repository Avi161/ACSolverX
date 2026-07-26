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


def automorphism_from_u_image(u_image: str) -> dict[str, str]:
    return {
        "x": "x",
        "t": "t",
        "z": free_reduce(P + inverse_word(u_image) + R),
        "q": "q",
    }


def phi_data():
    identity = {generator: generator for generator in GENERATORS}
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

    assert compose(phi_inverse, phi) == identity
    assert compose(phi, phi_inverse) == identity
    return identity, beta, phi, phi_inverse


def complement_maps(
    a_word: str,
    sign: int,
) -> tuple[dict[str, str], dict[str, str]]:
    if sign == 1:
        u_image = free_reduce(
            "q"
            + a_word
            + inverse_word(U)
            + "q"
            + inverse_word(a_word)
        )
        inverse_u_image = free_reduce(
            "q"
            + inverse_word(a_word)
            + inverse_word(U)
            + "q"
            + a_word
        )
    else:
        u_image = free_reduce(
            "q"
            + a_word
            + "Q"
            + U
            + inverse_word(a_word)
        )
        inverse_u_image = free_reduce(
            "q"
            + inverse_word(a_word)
            + "Q"
            + U
            + a_word
        )

    return (
        automorphism_from_u_image(u_image),
        automorphism_from_u_image(inverse_u_image),
    )


def test_complement_automorphisms_and_double_quotients_for_sample_words():
    identity, _, phi, phi_inverse = phi_data()
    kill_u = {"x": "x", "t": "t", "z": free_reduce(P + R), "q": "q"}
    kill_uq = {"x": "x", "t": "t", "z": free_reduce(P + R), "q": ""}

    assert substitute(U, kill_u) == ""

    for a_word in ("", "x", "t", "xTXXt"):
        c_word = substitute(a_word, phi)
        for sign in (1, -1):
            delta, delta_inverse = complement_maps(a_word, sign)
            assert compose(delta_inverse, delta) == identity
            assert compose(delta, delta_inverse) == identity

            chi = compose(phi, delta)
            chi_inverse = compose(delta_inverse, phi_inverse)
            assert compose(chi_inverse, chi) == identity
            assert compose(chi, chi_inverse) == identity

            q_letter = "q" if sign == 1 else "Q"
            target = free_reduce(
                phi["q"]
                + c_word
                + q_letter
                + inverse_word(c_word)
            )
            pullback = substitute(target, phi_inverse)

            assert substitute(U, delta) == pullback
            assert substitute(U, chi) == target
            assert substitute(
                substitute(target, chi_inverse),
                kill_u,
            ) == ""

            expected_q = free_reduce(
                inverse_word(a_word)
                + ("Q" if sign == 1 else "q")
                + a_word
            )
            first_q = substitute(
                substitute("q", chi_inverse),
                kill_u,
            )
            assert first_q == expected_q

            for generator in GENERATORS:
                old_image = substitute(
                    substitute(generator, phi_inverse),
                    kill_uq,
                )
                new_image = substitute(
                    substitute(generator, chi_inverse),
                    kill_uq,
                )
                assert new_image == old_image


def test_literal_t_conjugator_targets_and_first_quotients():
    identity, _, phi, phi_inverse = phi_data()
    a_word = "t"
    c_word = substitute(a_word, phi)
    kill_u = {"x": "x", "t": "t", "z": free_reduce(P + R), "q": "q"}

    assert c_word == "t"

    for sign, expected_q in ((1, "TQt"), (-1, "Tqt")):
        delta, delta_inverse = complement_maps(a_word, sign)
        chi = compose(phi, delta)
        chi_inverse = compose(delta_inverse, phi_inverse)
        q_letter = "q" if sign == 1 else "Q"
        target = free_reduce(phi["q"] + "t" + q_letter + "T")

        assert compose(chi_inverse, chi) == identity
        assert compose(chi, chi_inverse) == identity
        assert substitute(U, chi) == target
        assert substitute(
            substitute("q", chi_inverse),
            kill_u,
        ) == expected_q


def test_both_signs_have_the_same_exact_rank_two_endpoint():
    _, beta, phi, phi_inverse = phi_data()
    kill_uq = {"x": "x", "t": "t", "z": free_reduce(P + R), "q": ""}
    beta_r = substitute(R, beta)
    expected_e = free_reduce(
        "T" + P + R + "x" + inverse_word(P + R)
    )

    old_r = substitute(substitute(beta_r, phi_inverse), kill_uq)
    old_d = substitute(substitute(D, phi_inverse), kill_uq)
    assert old_r == R
    assert old_d == expected_e

    for sign in (1, -1):
        delta, delta_inverse = complement_maps("t", sign)
        chi = compose(phi, delta)
        chi_inverse = compose(delta_inverse, phi_inverse)

        assert substitute(substitute(beta_r, chi_inverse), kill_uq) == R
        assert (
            substitute(substitute(D, chi_inverse), kill_uq)
            == expected_e
        )


def test_rank_two_endpoint_returns_by_two_r_factors():
    standard_e = free_reduce("T" + P + "x" + inverse_word(P))
    new_e = free_reduce("T" + P + R + "x" + inverse_word(P + R))
    factors = free_reduce(
        conjugate(P + "X", R)
        + conjugate(P, inverse_word(R))
    )

    assert standard_e == "TxtxTX"
    assert free_reduce(inverse_word(standard_e) + new_e) == factors
    assert free_reduce(standard_e + factors) == new_e


if __name__ == "__main__":
    test_complement_automorphisms_and_double_quotients_for_sample_words()
    test_literal_t_conjugator_targets_and_first_quotients()
    test_both_signs_have_the_same_exact_rank_two_endpoint()
    test_rank_two_endpoint_returns_by_two_r_factors()
