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


def test_both_retained_sources_have_exact_q_factorizations():
    beta = {"x": "qxQ", "t": "t", "z": "z", "q": "q"}
    beta_r = substitute(R, beta)
    beta_b = substitute(B, beta)

    r_factors = free_reduce(
        conjugate(inverse_word(R), "q")
        + conjugate("tttt", "Q")
    )
    b_factors = free_reduce(
        conjugate("TX", "q")
        + conjugate("T", "Q")
    )

    assert free_reduce(inverse_word(R) + beta_r) == r_factors
    assert free_reduce(R + r_factors) == beta_r
    assert free_reduce(inverse_word(B) + beta_b) == b_factors
    assert free_reduce(B + b_factors) == beta_b


def test_exact_five_q_primitive_manufacture():
    beta = {"x": "qxQ", "t": "t", "z": "z", "q": "q"}
    beta_r = substitute(R, beta)
    beta_b = substitute(B, beta)
    beta_u = substitute(U, beta)
    word = free_reduce(beta_u + "q")

    assert beta_u == free_reduce(beta_r + beta_b)
    assert word == "qxxxQTTTTZqxQtq"
    assert sum(letter in "qQ" for letter in word) == 5
    assert sum(letter == "q" for letter in word) == 3
    assert sum(letter == "Q" for letter in word) == 2

    target = free_reduce("q" + beta_r + beta_b)
    assert conjugate("Q", target) == word


def test_straightening_returns_both_sources_and_computes_survivor():
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
    identity = {generator: generator for generator in GENERATORS}

    assert compose(phi_inverse, phi) == identity
    assert compose(phi, phi_inverse) == identity
    assert phi["q"] == free_reduce(substitute(U, beta) + "q")

    kill_q = {"x": "x", "t": "t", "z": "z", "q": ""}

    def quotient(word: str) -> str:
        return substitute(substitute(word, phi_inverse), kill_q)

    p_x = free_reduce(U + "x" + inverse_word(U))
    assert quotient("x") == p_x
    assert quotient("t") == "t"
    assert quotient("z") == "z"
    assert quotient("q") == inverse_word(U)
    assert quotient(substitute(R, beta)) == R
    assert quotient(substitute(B, beta)) == B
    assert quotient(D) == free_reduce("Tz" + p_x + "Z")


def test_four_retained_source_factors_return_the_survivor():
    p_x = free_reduce(U + "x" + inverse_word(U))
    d_prime = free_reduce("Tz" + p_x + "Z")

    two_u_factors = free_reduce(
        conjugate("zX", U)
        + conjugate("z", inverse_word(U))
    )
    four_source_factors = free_reduce(
        conjugate("zX", R)
        + conjugate("zX", B)
        + conjugate("z", inverse_word(B))
        + conjugate("z", inverse_word(R))
    )

    assert free_reduce(inverse_word(D) + d_prime) == two_u_factors
    assert two_u_factors == four_source_factors
    assert free_reduce(D + four_source_factors) == d_prime


if __name__ == "__main__":
    test_both_retained_sources_have_exact_q_factorizations()
    test_exact_five_q_primitive_manufacture()
    test_straightening_returns_both_sources_and_computes_survivor()
    test_four_retained_source_factors_return_the_survivor()
