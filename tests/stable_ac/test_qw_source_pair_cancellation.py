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


def changed_source(eta: int, epsilon: int) -> str:
    w_power = W if epsilon == 1 else inverse_word(W)
    return free_reduce(q_power(eta) + w_power)


def z_coordinate_maps(eta: int, epsilon: int):
    identity = {generator: generator for generator in GENERATORS}
    q_eta = q_power(eta)
    if epsilon == 1:
        left = free_reduce(q_eta + A)
        z_image = free_reduce(left + "Z" + C)
        z_inverse_image = free_reduce(C + "Z" + left)
    else:
        left = free_reduce(q_eta + inverse_word(C))
        right = inverse_word(A)
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


def first_deletion_map(eta: int, epsilon: int):
    _, tau_inverse = z_coordinate_maps(eta, epsilon)
    kill_z = {"x": "x", "t": "t", "z": "", "q": "q"}
    return {
        generator: substitute(tau_inverse[generator], kill_z)
        for generator in GENERATORS
    }


def test_all_four_changed_sources_are_exact_unique_z_coordinates():
    for eta in (1, -1):
        for epsilon in (1, -1):
            tau, tau_inverse = z_coordinate_maps(eta, epsilon)
            source = changed_source(eta, epsilon)

            assert tau["z"] == source
            assert sum(letter in "zZ" for letter in source) == 1
            assert substitute(source, tau_inverse) == "z"


def test_surviving_w_slot_is_literal_q_with_exact_sign():
    for eta in (1, -1):
        for epsilon in (1, -1):
            first_map = first_deletion_map(eta, epsilon)
            expected = q_power(-eta * epsilon)

            assert substitute(changed_source(eta, epsilon), first_map) == ""
            assert substitute(W, first_map) == expected
            assert substitute(A, first_map) == A


def test_changed_source_traffic_vanishes_in_all_survivor_slots():
    for eta in (1, -1):
        for epsilon in (1, -1):
            source = changed_source(eta, epsilon)
            first_map = first_deletion_map(eta, epsilon)
            expected = tuple(
                substitute(word, first_map)
                for word in (A, W, D)
            )
            factors = (
                conjugate("x", source),
                conjugate("qZ", inverse_word(source)),
                conjugate(free_reduce("T" + R + "q"), source),
            )
            traffic = (
                "",
                factors[0],
                factors[1],
                free_reduce(factors[0] + factors[2] + factors[1]),
            )

            for multiplier in traffic:
                assert substitute(multiplier, first_map) == ""
                for original, image in zip((A, W, D), expected):
                    assert substitute(original + multiplier, first_map) == image


def test_all_four_second_deletions_give_common_endpoint():
    kill_q = {"x": "x", "t": "t", "z": "z", "q": ""}
    expected_endpoint = free_reduce(
        "T" + P + R + "x" + inverse_word(P + R)
    )

    for eta in (1, -1):
        for epsilon in (1, -1):
            first_map = first_deletion_map(eta, epsilon)
            first_relator = substitute(A, first_map)
            second_relator = substitute(D, first_map)
            q_eta = q_power(eta)
            if epsilon == 1:
                left = free_reduce(q_eta + A)
                conjugator = free_reduce(C + left)
            else:
                left = free_reduce(q_eta + inverse_word(C))
                right = inverse_word(A)
                conjugator = free_reduce(
                    inverse_word(left) + inverse_word(right)
                )
            expected_second = free_reduce(
                "T"
                + conjugator
                + "x"
                + inverse_word(conjugator)
            )

            assert second_relator == expected_second
            assert substitute(first_relator, kill_q) == R
            assert substitute(second_relator, kill_q) == expected_endpoint


def test_common_endpoint_returns_by_two_r_factors():
    endpoint_r = free_reduce(
        "T" + P + R + "x" + inverse_word(P + R)
    )
    endpoint_0 = free_reduce("T" + P + "x" + inverse_word(P))
    first_factor = conjugate(P + "X", R)
    second_factor = conjugate(P, inverse_word(R))

    assert free_reduce(inverse_word(endpoint_0) + endpoint_r) == (
        free_reduce(first_factor + second_factor)
    )
    assert free_reduce(
        endpoint_r
        + inverse_word(second_factor)
        + inverse_word(first_factor)
    ) == endpoint_0


if __name__ == "__main__":
    test_all_four_changed_sources_are_exact_unique_z_coordinates()
    test_surviving_w_slot_is_literal_q_with_exact_sign()
    test_changed_source_traffic_vanishes_in_all_survivor_slots()
    test_all_four_second_deletions_give_common_endpoint()
    test_common_endpoint_returns_by_two_r_factors()
