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


def checkpoint_data():
    beta = {"x": "qxQ", "t": "t", "z": "z", "q": "q"}
    beta_r = substitute(R, beta)
    beta_p = substitute(P, beta)
    primitive = free_reduce(substitute(U, beta) + "q")

    assert primitive == free_reduce(beta_r + "Z" + beta_p + "q")
    return beta, beta_r, beta_p, primitive


def unique_z_traffic_maps(
    multiplier: str,
) -> tuple[str, dict[str, str], dict[str, str]]:
    _, beta_r, beta_p, primitive = checkpoint_data()
    suffix = free_reduce(beta_p + "q" + multiplier)
    target = free_reduce(beta_r + "Z" + suffix)

    gamma = {"x": "x", "t": "t", "z": target, "q": "q"}
    gamma_inverse = {
        "x": "x",
        "t": "t",
        "z": free_reduce(suffix + "Z" + beta_r),
        "q": "q",
    }

    assert target == free_reduce(primitive + multiplier)
    return target, gamma, gamma_inverse


def q_normal_closure_samples() -> tuple[str, ...]:
    q_dependent_conjugator = "qxQ"
    first_factor = "xqX"
    second_factor = "tQT"
    return (
        "",
        "q",
        "Q",
        first_factor,
        second_factor,
        free_reduce(first_factor + second_factor),
        free_reduce(
            q_dependent_conjugator
            + "q"
            + inverse_word(q_dependent_conjugator)
        ),
    )


def test_unique_z_automorphisms_for_finite_q_source_traffic():
    identity = {generator: generator for generator in GENERATORS}
    kill_q = {"x": "x", "t": "t", "z": "z", "q": ""}

    for multiplier in q_normal_closure_samples():
        assert "z" not in multiplier.lower()
        assert substitute(multiplier, kill_q) == ""
        target, gamma, gamma_inverse = unique_z_traffic_maps(multiplier)

        assert target.count("z") + target.count("Z") == 1
        assert target.count("Z") == 1
        assert gamma["z"] == target
        assert compose(gamma_inverse, gamma) == identity
        assert compose(gamma, gamma_inverse) == identity


def test_literal_x_targets_are_in_the_z_free_family():
    _, _, _, primitive = checkpoint_data()

    for sign in (1, -1):
        q_letter = "q" if sign == 1 else "Q"
        multiplier = "x" + q_letter + "X"
        target, gamma, _ = unique_z_traffic_maps(multiplier)
        expected = free_reduce(primitive + "x" + q_letter + "X")

        assert target == expected
        assert gamma["z"] == expected


def test_double_quotient_is_independent_of_q_source_history():
    _, beta_r, _, _ = checkpoint_data()
    identity = {generator: generator for generator in GENERATORS}
    kill_z = {"x": "x", "t": "t", "z": "", "q": "q"}
    kill_zq = {"x": "x", "t": "t", "z": "", "q": ""}
    expected_z = free_reduce(P + R)
    expected_d = free_reduce(
        "T" + expected_z + "x" + inverse_word(expected_z)
    )

    for multiplier in q_normal_closure_samples():
        target, gamma, gamma_inverse = unique_z_traffic_maps(multiplier)

        assert compose(gamma_inverse, gamma) == identity
        assert substitute(
            substitute(target, gamma_inverse),
            kill_z,
        ) == ""
        assert substitute(
            substitute("q", gamma_inverse),
            kill_z,
        ) == "q"
        assert substitute(
            substitute("z", gamma_inverse),
            kill_zq,
        ) == expected_z
        assert substitute(
            substitute(beta_r, gamma_inverse),
            kill_zq,
        ) == R
        assert substitute(
            substitute(D, gamma_inverse),
            kill_zq,
        ) == expected_d


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
    test_unique_z_automorphisms_for_finite_q_source_traffic()
    test_literal_x_targets_are_in_the_z_free_family()
    test_double_quotient_is_independent_of_q_source_history()
    test_rank_two_endpoint_returns_by_two_r_factors()
