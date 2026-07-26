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


def data():
    identity = {generator: generator for generator in GENERATORS}
    kill_q = {"x": "x", "t": "t", "z": "z", "q": ""}

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

    delta_plus = {
        "x": "x",
        "t": "t",
        "z": P + "Q" + R,
        "q": "q" + inverse_word(U) + "q",
    }
    delta_plus_inverse = {
        "x": "x",
        "t": "t",
        "z": P + inverse_word(U) + "q" + inverse_word(U) + R,
        "q": U,
    }
    delta_minus = {
        "x": "x",
        "t": "t",
        "z": P + "Q" + R,
        "q": U,
    }

    return {
        "identity": identity,
        "kill_q": kill_q,
        "beta": beta,
        "phi": phi,
        "phi_inverse": phi_inverse,
        "delta_plus": delta_plus,
        "delta_plus_inverse": delta_plus_inverse,
        "delta_minus": delta_minus,
    }


def quotient(word: str, inverse_map: WordMap, kill_q: WordMap) -> str:
    return substitute(substitute(word, inverse_map), kill_q)


def test_u_is_a_basis_element_by_an_explicit_unique_z_automorphism():
    identity = {generator: generator for generator in GENERATORS}
    nu = {"x": "x", "t": "t", "z": U, "q": "q"}
    nu_inverse = {
        "x": "x",
        "t": "t",
        "z": P + "Z" + R,
        "q": "q",
    }

    assert nu["z"] == U
    assert U.count("z") + U.count("Z") == 1
    assert compose(nu_inverse, nu) == identity
    assert compose(nu, nu_inverse) == identity


def test_positive_pullback_is_an_explicit_basis_image():
    maps = data()
    identity = maps["identity"]
    phi = maps["phi"]
    phi_inverse = maps["phi_inverse"]
    delta_plus = maps["delta_plus"]
    delta_plus_inverse = maps["delta_plus_inverse"]

    assert compose(phi_inverse, phi) == identity
    assert compose(phi, phi_inverse) == identity
    assert compose(delta_plus_inverse, delta_plus) == identity
    assert compose(delta_plus, delta_plus_inverse) == identity
    assert substitute(U, delta_plus) == "q"
    assert substitute(U, delta_plus_inverse) == free_reduce(
        U + "Q" + U
    )

    primitive = phi["q"]
    target = free_reduce(primitive + "q")
    pullback = substitute(target, phi_inverse)
    chi = compose(phi, delta_plus)

    assert pullback == free_reduce("q" + inverse_word(U) + "q")
    assert chi["q"] == target
    assert sum(letter in "qQ" for letter in target) == 6


def test_negative_pullback_is_the_swapped_primitive_u():
    maps = data()
    identity = maps["identity"]
    phi = maps["phi"]
    phi_inverse = maps["phi_inverse"]
    delta_minus = maps["delta_minus"]

    assert compose(delta_minus, delta_minus) == identity
    assert substitute(U, delta_minus) == "q"

    primitive = phi["q"]
    target = free_reduce(primitive + "Q")
    pullback = substitute(target, phi_inverse)
    chi = compose(phi, delta_minus)

    assert pullback == U
    assert chi["q"] == target
    assert sum(letter in "qQ" for letter in target) == 4


def test_positive_straightening_quotient_and_two_factor_return():
    maps = data()
    beta = maps["beta"]
    phi = maps["phi"]
    phi_inverse = maps["phi_inverse"]
    delta_plus = maps["delta_plus"]
    delta_plus_inverse = maps["delta_plus_inverse"]
    kill_q = maps["kill_q"]

    chi = compose(phi, delta_plus)
    chi_inverse = compose(delta_plus_inverse, phi_inverse)
    identity = maps["identity"]
    assert compose(chi_inverse, chi) == identity
    assert compose(chi, chi_inverse) == identity

    y_word = free_reduce(U + "x" + inverse_word(U))
    h_word = conjugate(inverse_word(R), inverse_word(U))
    expected_z = free_reduce("z" + h_word)
    target = free_reduce(phi["q"] + "q")
    beta_r = substitute(R, beta)

    assert quotient(beta_r, chi_inverse, kill_q) == R
    assert quotient(target, chi_inverse, kill_q) == ""
    assert quotient("q", chi_inverse, kill_q) == inverse_word(U)
    assert quotient("x", chi_inverse, kill_q) == y_word
    assert quotient("t", chi_inverse, kill_q) == "t"
    assert quotient("z", chi_inverse, kill_q) == expected_z

    old_d = free_reduce("Tz" + y_word + "Z")
    new_d = free_reduce(
        "T" + expected_z + y_word + inverse_word(expected_z)
    )
    factors = free_reduce(
        conjugate("z" + inverse_word(y_word), h_word)
        + conjugate("z", inverse_word(h_word))
    )

    assert quotient(D, chi_inverse, kill_q) == new_d
    assert free_reduce(inverse_word(old_d) + new_d) == factors
    assert free_reduce(old_d + factors) == new_d


def test_negative_straightening_quotient_and_six_factor_return():
    maps = data()
    beta = maps["beta"]
    phi = maps["phi"]
    phi_inverse = maps["phi_inverse"]
    delta_minus = maps["delta_minus"]
    kill_q = maps["kill_q"]

    chi = compose(phi, delta_minus)
    chi_inverse = compose(delta_minus, phi_inverse)
    identity = maps["identity"]
    assert compose(chi_inverse, chi) == identity
    assert compose(chi, chi_inverse) == identity

    y_word = free_reduce(U + "x" + inverse_word(U))
    y_minus = free_reduce(inverse_word(U) + "x" + U)
    h_minus = conjugate(inverse_word(R), U)
    expected_z = free_reduce("z" + h_minus)
    target = free_reduce(phi["q"] + "Q")
    beta_r = substitute(R, beta)

    assert expected_z == free_reduce(P + R)
    assert quotient(beta_r, chi_inverse, kill_q) == R
    assert quotient(target, chi_inverse, kill_q) == ""
    assert quotient("q", chi_inverse, kill_q) == U
    assert quotient("x", chi_inverse, kill_q) == y_minus
    assert quotient("t", chi_inverse, kill_q) == "t"
    assert quotient("z", chi_inverse, kill_q) == expected_z

    old_d = free_reduce("Tz" + y_word + "Z")
    new_d = free_reduce(
        "T" + expected_z + y_minus + inverse_word(expected_z)
    )
    factors = free_reduce(
        conjugate("z" + inverse_word(y_word), h_minus)
        + conjugate("z", U)
        + conjugate("zX", inverse_word(U))
        + conjugate("zX", inverse_word(U))
        + conjugate("z", U)
        + conjugate("z", inverse_word(h_minus))
    )

    assert quotient(D, chi_inverse, kill_q) == new_d
    assert free_reduce(inverse_word(old_d) + new_d) == factors
    assert free_reduce(old_d + factors) == new_d


if __name__ == "__main__":
    test_u_is_a_basis_element_by_an_explicit_unique_z_automorphism()
    test_positive_pullback_is_an_explicit_basis_image()
    test_negative_pullback_is_the_swapped_primitive_u()
    test_positive_straightening_quotient_and_two_factor_return()
    test_negative_straightening_quotient_and_six_factor_return()
