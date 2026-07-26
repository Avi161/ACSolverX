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
V = "qxxxQTTTTq"

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


def test_literal_two_factor_creation_of_the_split_relator():
    beta = {"x": "qxQ", "t": "t", "z": "z", "q": "q"}
    beta_r = substitute(R, beta)
    assert beta_r == "qxxxQTTTT"

    first = conjugate(inverse_word(R), "q")
    second = conjugate("tttt", "Q")
    assert free_reduce(inverse_word(R) + beta_r) == free_reduce(first + second)
    assert free_reduce(R + first + second) == beta_r


def test_one_target_multiplication_produces_the_primitive_word():
    beta = {"x": "qxQ", "t": "t", "z": "z", "q": "q"}
    beta_r = substitute(R, beta)
    target_after_multiplication = free_reduce("q" + beta_r)
    target_after_conjugation = conjugate("Q", target_after_multiplication)
    assert target_after_conjugation == beta_r + "q"
    assert target_after_conjugation == V


def test_straightening_automorphism_and_quotient_endpoint():
    alpha = {"x": "x", "t": "t", "z": "z", "q": R + "q"}
    alpha_inverse = {
        "x": "x",
        "t": "t",
        "z": "z",
        "q": inverse_word(R) + "q",
    }
    beta = {"x": "qxQ", "t": "t", "z": "z", "q": "q"}
    beta_inverse = {"x": "Qxq", "t": "t", "z": "z", "q": "q"}
    phi = compose(beta, alpha)
    phi_inverse = compose(alpha_inverse, beta_inverse)
    identity = {generator: generator for generator in GENERATORS}

    assert phi["q"] == V
    assert compose(phi_inverse, phi) == identity
    assert compose(phi, phi_inverse) == identity

    kill_q = {"x": "x", "t": "t", "z": "z", "q": ""}

    def quotient(word: str) -> str:
        return substitute(substitute(word, phi_inverse), kill_q)

    p_x = free_reduce(R + "x" + inverse_word(R))
    assert quotient("x") == p_x
    assert quotient("t") == "t"
    assert quotient("z") == "z"
    assert quotient("q") == inverse_word(R)

    beta_r = substitute(R, beta)
    assert quotient(beta_r) == R
    assert quotient(B) == free_reduce("Z" + p_x + "t")
    assert quotient(D) == free_reduce("Tz" + p_x + "Z")


def test_two_factor_return_of_each_ak3_survivor():
    p_x = free_reduce(R + "x" + inverse_word(R))
    b_prime = free_reduce("Z" + p_x + "t")
    d_prime = free_reduce("Tz" + p_x + "Z")

    b_first = conjugate("TX", R)
    b_second = conjugate("T", inverse_word(R))
    d_first = conjugate("zX", R)
    d_second = conjugate("z", inverse_word(R))

    assert free_reduce(inverse_word(B) + b_prime) == free_reduce(
        b_first + b_second
    )
    assert free_reduce(B + b_first + b_second) == b_prime

    assert free_reduce(inverse_word(D) + d_prime) == free_reduce(
        d_first + d_second
    )
    assert free_reduce(D + d_first + d_second) == d_prime


def test_nontrivial_retained_consequence_extension():
    u_word = free_reduce(R + conjugate("x", inverse_word(R)))
    alpha_u = {
        "x": "x",
        "t": "t",
        "z": "z",
        "q": u_word + "q",
    }
    alpha_u_inverse = {
        "x": "x",
        "t": "t",
        "z": "z",
        "q": inverse_word(u_word) + "q",
    }
    beta = {"x": "qxQ", "t": "t", "z": "z", "q": "q"}
    beta_inverse = {"x": "Qxq", "t": "t", "z": "z", "q": "q"}
    phi = compose(beta, alpha_u)
    phi_inverse = compose(alpha_u_inverse, beta_inverse)
    identity = {generator: generator for generator in GENERATORS}

    beta_r = substitute(R, beta)
    beta_x = beta["x"]
    beta_u = substitute(u_word, beta)
    assert beta_u == free_reduce(
        beta_r + conjugate(beta_x, inverse_word(beta_r))
    )
    assert phi["q"] == free_reduce(beta_u + "q")
    assert compose(phi_inverse, phi) == identity
    assert compose(phi, phi_inverse) == identity

    kill_q = {"x": "x", "t": "t", "z": "z", "q": ""}

    def quotient(word: str) -> str:
        return substitute(substitute(word, phi_inverse), kill_q)

    assert quotient("x") == free_reduce(
        u_word + "x" + inverse_word(u_word)
    )
    assert quotient("q") == inverse_word(u_word)


if __name__ == "__main__":
    test_literal_two_factor_creation_of_the_split_relator()
    test_one_target_multiplication_produces_the_primitive_word()
    test_straightening_automorphism_and_quotient_endpoint()
    test_two_factor_return_of_each_ak3_survivor()
    test_nontrivial_retained_consequence_extension()
