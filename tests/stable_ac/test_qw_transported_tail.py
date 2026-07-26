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
BASE_P = "xt"
D = "TzxZ"
A = "qxxxQTTTT"
C = "qxQtq"
W = A + "Z" + C

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


def q_power(sign: int) -> str:
    return "q" if sign == 1 else "Q"


def beta_maps():
    beta = {"x": "qxQ", "t": "t", "z": "z", "q": "q"}
    beta_inverse = {
        "x": "Qxq",
        "t": "t",
        "z": "z",
        "q": "q",
    }
    return beta, beta_inverse


def beta_image(word: str) -> str:
    beta, _ = beta_maps()
    return substitute(word, beta)


def changed_source(
    eta: int,
    epsilon: int,
    old_tail: str,
) -> str:
    transported_tail = beta_image(old_tail)
    w_power = W if epsilon == 1 else inverse_word(W)
    return free_reduce(
        q_power(eta) + w_power + transported_tail
    )


def z_coordinate_maps(
    eta: int,
    epsilon: int,
    old_tail: str,
):
    identity = {generator: generator for generator in GENERATORS}
    transported_tail = beta_image(old_tail)
    q_eta = q_power(eta)
    if epsilon == 1:
        left = free_reduce(q_eta + A)
        right = free_reduce(C + transported_tail)
        z_image = free_reduce(left + "Z" + right)
        z_inverse_image = free_reduce(right + "Z" + left)
    else:
        left = free_reduce(q_eta + inverse_word(C))
        right = free_reduce(inverse_word(A) + transported_tail)
        z_image = free_reduce(left + "z" + right)
        z_inverse_image = free_reduce(
            inverse_word(left) + "z" + inverse_word(right)
        )

    tau = {"x": "x", "t": "t", "z": z_image, "q": "q"}
    tau_inverse = {
        "x": "x",
        "t": "t",
        "z": z_inverse_image,
        "q": "q",
    }
    assert compose(tau_inverse, tau) == identity
    assert compose(tau, tau_inverse) == identity
    return tau, tau_inverse


def first_deletion_map(
    eta: int,
    epsilon: int,
    old_tail: str,
):
    _, tau_inverse = z_coordinate_maps(eta, epsilon, old_tail)
    kill_z = {"x": "x", "t": "t", "z": "", "q": "q"}
    return {
        generator: substitute(tau_inverse[generator], kill_z)
        for generator in GENERATORS
    }


def left_coordinate_maps(eta: int, old_tail: str):
    identity = {generator: generator for generator in GENERATORS}
    beta, beta_inverse = beta_maps()
    ell = {
        "x": "x",
        "t": "t",
        "z": "z",
        "q": old_tail + q_power(eta),
    }
    ell_inverse_q = (
        inverse_word(old_tail) + "q"
        if eta == 1
        else "Q" + old_tail
    )
    ell_inverse = {
        "x": "x",
        "t": "t",
        "z": "z",
        "q": ell_inverse_q,
    }
    theta = compose(beta, ell)
    theta_inverse = compose(ell_inverse, beta_inverse)

    assert compose(theta_inverse, theta) == identity
    assert compose(theta, theta_inverse) == identity
    return theta, theta_inverse


def tail_samples():
    return (
        "",
        R,
        inverse_word(R),
        conjugate("x", R),
        free_reduce(
            conjugate("t", R)
            + conjugate("X", inverse_word(R))
        ),
    )


def test_all_tail_sources_and_both_automorphism_stages():
    for old_tail in tail_samples():
        transported_tail = beta_image(old_tail)
        for eta in (1, -1):
            theta, _ = left_coordinate_maps(eta, old_tail)
            transferred = free_reduce(
                transported_tail + q_power(eta)
            )
            assert theta["q"] == transferred

            for epsilon in (1, -1):
                tau, tau_inverse = z_coordinate_maps(
                    eta,
                    epsilon,
                    old_tail,
                )
                source = changed_source(eta, epsilon, old_tail)
                assert tau["z"] == source
                assert sum(letter in "zZ" for letter in source) == 1
                assert substitute(source, tau_inverse) == "z"


def test_uniform_tail_transfer_and_first_d_image():
    for old_tail in tail_samples():
        transported_tail = beta_image(old_tail)
        for eta in (1, -1):
            transferred = free_reduce(
                transported_tail + q_power(eta)
            )
            for epsilon in (1, -1):
                first_map = first_deletion_map(
                    eta,
                    epsilon,
                    old_tail,
                )
                expected_w = (
                    inverse_word(transferred)
                    if epsilon == 1
                    else transferred
                )
                conjugator = free_reduce(
                    C
                    + (
                        transferred
                        if epsilon == 1
                        else inverse_word(transferred)
                    )
                    + A
                )
                expected_d = free_reduce(
                    "T"
                    + conjugator
                    + "x"
                    + inverse_word(conjugator)
                )

                assert substitute(W, first_map) == expected_w
                assert substitute(D, first_map) == expected_d


def test_first_source_traffic_vanishes_in_every_survivor():
    old_tail = free_reduce(
        conjugate("t", R) + conjugate("X", inverse_word(R))
    )
    for eta in (1, -1):
        for epsilon in (1, -1):
            source = changed_source(eta, epsilon, old_tail)
            first_map = first_deletion_map(eta, epsilon, old_tail)
            expected = tuple(
                substitute(word, first_map)
                for word in (A, W, D)
            )
            factors = (
                conjugate("x", source),
                conjugate("qZ", inverse_word(source)),
                conjugate(free_reduce("T" + R + "q"), source),
            )
            multiplier = free_reduce(
                factors[0] + factors[2] + factors[1]
            )

            assert substitute(multiplier, first_map) == ""
            for original, image in zip((A, W, D), expected):
                assert substitute(original + multiplier, first_map) == image


def test_exact_general_second_deletion_endpoint():
    kill_q = {"x": "x", "t": "t", "z": "z", "q": ""}
    for old_tail in tail_samples():
        for eta in (1, -1):
            _, theta_inverse = left_coordinate_maps(eta, old_tail)
            second_map = {
                generator: substitute(theta_inverse[generator], kill_q)
                for generator in GENERATORS
            }
            tail_power = (
                inverse_word(old_tail)
                if eta == 1
                else old_tail
            )
            tail_inverse_power = (
                old_tail
                if eta == 1
                else inverse_word(old_tail)
            )
            conjugator = free_reduce(
                BASE_P
                + tail_power
                + R
                + tail_inverse_power
            )
            expected_d = free_reduce(
                "T"
                + conjugator
                + "x"
                + inverse_word(conjugator)
            )

            for epsilon in (1, -1):
                first_map = first_deletion_map(
                    eta,
                    epsilon,
                    old_tail,
                )
                first_a = substitute(A, first_map)
                first_d = substitute(D, first_map)

                assert substitute(first_a, second_map) == R
                assert second_map["x"] == free_reduce(
                    tail_inverse_power
                    + "x"
                    + tail_power
                )
                assert substitute(first_d, second_map) == expected_d


def test_general_and_v_equals_r_two_factor_returns():
    endpoint_0 = free_reduce(
        "T" + BASE_P + "x" + inverse_word(BASE_P)
    )
    endpoint_r = free_reduce(
        "T" + BASE_P + R + "x" + inverse_word(BASE_P + R)
    )
    for old_tail in tail_samples():
        for eta in (1, -1):
            tail_power = (
                inverse_word(old_tail)
                if eta == 1
                else old_tail
            )
            tail_inverse_power = inverse_word(tail_power)
            h_word = free_reduce(
                tail_power + R + tail_inverse_power
            )
            conjugator = free_reduce(BASE_P + h_word)
            endpoint = free_reduce(
                "T"
                + conjugator
                + "x"
                + inverse_word(conjugator)
            )
            first_factor = conjugate(
                BASE_P + "X" + tail_power,
                R,
            )
            second_factor = conjugate(
                BASE_P + tail_power,
                inverse_word(R),
            )
            factors = (first_factor, second_factor)

            assert free_reduce(inverse_word(endpoint_0) + endpoint) == (
                free_reduce("".join(factors))
            )
            assert free_reduce(
                endpoint
                + inverse_word(second_factor)
                + inverse_word(first_factor)
            ) == endpoint_0

    for eta in (1, -1):
        tail_power = inverse_word(R) if eta == 1 else R
        tail_inverse_power = inverse_word(tail_power)
        conjugator = free_reduce(
            BASE_P + tail_power + R + tail_inverse_power
        )
        endpoint = free_reduce(
            "T"
            + conjugator
            + "x"
            + inverse_word(conjugator)
        )
        assert endpoint == endpoint_r


if __name__ == "__main__":
    test_all_tail_sources_and_both_automorphism_stages()
    test_uniform_tail_transfer_and_first_d_image()
    test_first_source_traffic_vanishes_in_every_survivor()
    test_exact_general_second_deletion_endpoint()
    test_general_and_v_equals_r_two_factor_returns()
