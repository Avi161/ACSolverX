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


def test_beta_b_target_becomes_the_five_q_primitive_word():
    beta = {"x": "qxQ", "t": "t", "z": "z", "q": "q"}
    beta_r = substitute(R, beta)
    beta_b = substitute(B, beta)
    beta_u = substitute(U, beta)

    first_factor = conjugate(inverse_word(beta_b), beta_r)
    target_after_first = free_reduce(beta_b + first_factor)
    target_after_second = free_reduce(target_after_first + "q")

    assert target_after_first == beta_u
    assert target_after_second == "qxxxQTTTTZqxQtq"
    assert sum(letter in "qQ" for letter in target_after_second) == 5


def test_surviving_q_relator_becomes_u_inverse_after_straightening():
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
    word = free_reduce(substitute(U, beta) + "q")

    assert phi["q"] == word
    assert compose(phi_inverse, phi) == identity
    assert compose(phi, phi_inverse) == identity
    assert substitute(word, phi_inverse) == "q"

    kill_q = {"x": "x", "t": "t", "z": "z", "q": ""}

    def quotient(word_to_map: str) -> str:
        return substitute(
            substitute(word_to_map, phi_inverse),
            kill_q,
        )

    p_x = free_reduce(U + "x" + inverse_word(U))
    assert quotient(substitute(R, beta)) == R
    assert quotient("q") == inverse_word(U)
    assert quotient(D) == free_reduce("Tz" + p_x + "Z")


def test_u_inverse_recovers_the_deleted_b_source():
    u_inverse = inverse_word(U)
    assert free_reduce(u_inverse + R) == inverse_word(B)
    assert inverse_word(free_reduce(u_inverse + R)) == B


def test_recovered_sources_return_the_distorted_d_survivor():
    p_x = free_reduce(U + "x" + inverse_word(U))
    d_prime = free_reduce("Tz" + p_x + "Z")
    factors = free_reduce(
        conjugate("zX", R)
        + conjugate("zX", B)
        + conjugate("z", inverse_word(B))
        + conjugate("z", inverse_word(R))
    )

    assert free_reduce(inverse_word(D) + d_prime) == factors
    assert free_reduce(D + factors) == d_prime


if __name__ == "__main__":
    test_beta_b_target_becomes_the_five_q_primitive_word()
    test_surviving_q_relator_becomes_u_inverse_after_straightening()
    test_u_inverse_recovers_the_deleted_b_source()
    test_recovered_sources_return_the_distorted_d_survivor()
