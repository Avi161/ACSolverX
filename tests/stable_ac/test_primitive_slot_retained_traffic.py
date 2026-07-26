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


def automorphism_data():
    alpha_u = {"x": "x", "t": "t", "z": "z", "q": U + "q"}
    alpha_u_inverse = {
        "x": "x",
        "t": "t",
        "z": "z",
        "q": inverse_word(U) + "q",
    }
    beta = {"x": "qxQ", "t": "t", "z": "z", "q": "q"}
    beta_inverse = {"x": "Qxq", "t": "t", "z": "z", "q": "q"}
    delta_r = {"x": "x", "t": "t", "z": "z", "q": "q" + R}
    delta_r_inverse = {
        "x": "x",
        "t": "t",
        "z": "z",
        "q": "q" + inverse_word(R),
    }

    phi = compose(beta, alpha_u)
    phi_inverse = compose(alpha_u_inverse, beta_inverse)
    chi = compose(phi, delta_r)
    chi_inverse = compose(delta_r_inverse, phi_inverse)
    return beta, phi, phi_inverse, chi, chi_inverse


def test_retained_source_target_move_is_phi_of_a_right_transvection():
    beta, phi, _, chi, _ = automorphism_data()
    primitive = phi["q"]
    beta_r = substitute(R, beta)
    primitive_r = free_reduce(primitive + beta_r)

    assert primitive_r == chi["q"]
    assert primitive_r == "qxxxQTTTTZqxQtqqxxxQTTTT"
    assert sum(letter == "q" for letter in primitive_r) == 4
    assert sum(letter == "Q" for letter in primitive_r) == 3
    assert sum(letter in "qQ" for letter in primitive_r) == 7


def test_new_straightening_automorphism_and_quotient():
    beta, _, _, chi, chi_inverse = automorphism_data()
    identity = {generator: generator for generator in GENERATORS}
    assert compose(chi_inverse, chi) == identity
    assert compose(chi, chi_inverse) == identity

    kill_q = {"x": "x", "t": "t", "z": "z", "q": ""}

    def quotient(word: str) -> str:
        return substitute(substitute(word, chi_inverse), kill_q)

    y_word = free_reduce(U + "x" + inverse_word(U))
    expected_x = free_reduce(R + y_word + inverse_word(R))
    beta_r = substitute(R, beta)
    primitive_r = chi["q"]

    assert quotient(beta_r) == R
    assert quotient(primitive_r) == ""
    assert quotient("q") == free_reduce(
        inverse_word(U) + inverse_word(R)
    )
    assert quotient("x") == expected_x
    assert quotient("t") == "t"
    assert quotient("z") == "z"
    assert quotient(D) == free_reduce("Tz" + expected_x + "Z")


def test_surviving_q_relator_recovers_b_with_two_r_factors():
    q_survivor = free_reduce(inverse_word(U) + inverse_word(R))
    recovered_inverse = free_reduce(q_survivor + R + R)
    assert recovered_inverse == inverse_word(B)
    assert inverse_word(recovered_inverse) == B


def test_new_d_survivor_differs_by_two_r_conjugates():
    y_word = free_reduce(U + "x" + inverse_word(U))
    old_d = free_reduce("Tz" + y_word + "Z")
    new_x = free_reduce(R + y_word + inverse_word(R))
    new_d = free_reduce("Tz" + new_x + "Z")
    factors = free_reduce(
        conjugate("z" + inverse_word(y_word), R)
        + conjugate("z", inverse_word(R))
    )

    assert free_reduce(inverse_word(old_d) + new_d) == factors
    assert free_reduce(old_d + factors) == new_d


if __name__ == "__main__":
    test_retained_source_target_move_is_phi_of_a_right_transvection()
    test_new_straightening_automorphism_and_quotient()
    test_surviving_q_relator_recovers_b_with_two_r_factors()
    test_new_d_survivor_differs_by_two_r_conjugates()
