"""Exact Fox obstruction for the terminal MMS02 HNN killer."""

from __future__ import annotations

from dataclasses import dataclass

from experiments.stable_ac.mms02_terminal_target_hnn_certificate import (
    apply_images,
    decide_target_hnn,
)

Laurent1 = dict[int, int]
Laurent2 = dict[tuple[int, int], int]

P_WORD = "QpQQPQQpqPqqpqqPqqpqPqpqqPq"
Q_WORD = "QpQPPqpqPqpqqPq"

EXPECTED_C_P = (
    (-10, 1),
    (-8, -1),
    (-6, -1),
    (-4, 1),
    (-2, 1),
    (0, -1),
    (4, 1),
    (6, -1),
    (8, 1),
    (12, -1),
)
EXPECTED_C_Q = (
    (-10, -1),
    (-9, 1),
    (-6, 1),
    (-5, -1),
    (-2, -1),
    (-1, 1),
    (0, 1),
    (2, 1),
    (5, 1),
    (6, 1),
    (9, 1),
    (11, 1),
    (12, 1),
)
EXPECTED_R = (
    (4, 1),
    (5, -1),
    (8, -2),
    (9, 1),
    (12, 2),
    (13, -1),
    (14, -1),
    (19, -1),
    (20, -2),
    (23, -1),
    (24, -1),
    (25, -1),
    (26, -1),
    (28, 1),
    (36, -1),
    (40, 1),
    (44, -1),
    (52, 1),
)


def add_term(polynomial: dict, exponent, coefficient: int) -> None:
    if not coefficient:
        return
    polynomial[exponent] = polynomial.get(exponent, 0) + coefficient
    if not polynomial[exponent]:
        del polynomial[exponent]


def abelianization(word: str) -> tuple[int, int]:
    p_exponent = 0
    q_exponent = 0
    for letter in word:
        if letter.lower() == "p":
            p_exponent += 1 if letter == "p" else -1
        elif letter.lower() == "q":
            q_exponent += 1 if letter == "q" else -1
        else:
            raise AssertionError("the terminal base word uses an unknown letter")
    return p_exponent, q_exponent


def fox_abelian(word: str, generator: str) -> Laurent2:
    derivative: Laurent2 = {}
    prefix = [0, 0]
    coordinate = 0 if generator == "p" else 1
    for letter in word:
        letter_coordinate = 0 if letter.lower() == "p" else 1
        sign = 1 if letter.islower() else -1
        if letter.lower() not in {"p", "q"}:
            raise AssertionError("the Fox word uses an unknown letter")
        if letter_coordinate == coordinate:
            exponent = list(prefix)
            if sign == -1:
                exponent[coordinate] -= 1
            add_term(derivative, tuple(exponent), sign)
        prefix[letter_coordinate] += sign
    return derivative


def specialize_t(polynomial: Laurent2) -> Laurent1:
    specialized: Laurent1 = {}
    for (p_exponent, q_exponent), coefficient in polynomial.items():
        add_term(specialized, p_exponent + 2 * q_exponent, coefficient)
    return specialized


def build_rhs(c_p: Laurent1, c_q: Laurent1) -> Laurent1:
    rhs: Laurent1 = {}
    for exponent, coefficient in c_p.items():
        add_term(rhs, 28 + 2 * exponent, -coefficient)
    for exponent, coefficient in c_q.items():
        add_term(rhs, 14 + exponent, -coefficient)
    return rhs


def l_vector(degree: int) -> dict[int, int]:
    vector: dict[int, int] = {}
    for index in range(13):
        if degree == index:
            add_term(vector, index, 1)
        if degree == 2 * index + 1:
            add_term(vector, index, -1)
        if degree == 2 * index + 2:
            add_term(vector, index, -1)
        if degree == 4 * index:
            add_term(vector, index, -1)
        if degree == 4 * index + 4:
            add_term(vector, index, 1)
    return vector


def l_coefficient(coefficients: dict[int, int], degree: int) -> int:
    return sum(
        multiplier * coefficients.get(index, 0)
        for index, multiplier in l_vector(degree).items()
    )


def force_high_coefficients(rhs: Laurent1) -> dict[int, int]:
    schedule = (
        (52, 12),
        (48, 11),
        (44, 10),
        (40, 9),
        (36, 8),
        (32, 7),
        (28, 6),
        (24, 5),
        (20, 4),
        (16, 3),
        (12, 2),
    )
    coefficients: dict[int, int] = {}
    for degree, index in schedule:
        vector = l_vector(degree)
        unresolved = sorted(set(vector) - set(coefficients))
        if unresolved != [index]:
            raise AssertionError("the high-degree coefficient cascade drifted")
        known = sum(
            multiplier * coefficients[known_index]
            for known_index, multiplier in vector.items()
            if known_index in coefficients
        )
        numerator = rhs.get(degree, 0) - known
        multiplier = vector[index]
        if numerator % multiplier:
            raise AssertionError("the forced Laurent coefficient is nonintegral")
        coefficients[index] = numerator // multiplier
    return coefficients


@dataclass(frozen=True)
class TwistedCoboundaryDecision:
    p_word: str
    q_word: str
    p_abelianization: tuple[int, int]
    q_abelianization: tuple[int, int]
    c_p: tuple[tuple[int, int], ...]
    c_q: tuple[tuple[int, int], ...]
    rhs: tuple[tuple[int, int], ...]
    forced_coefficients: tuple[tuple[int, int], ...]
    contradiction_degree: int
    left_coefficient: int
    right_coefficient: int
    verdict: str


def decide_twisted_coboundary() -> TwistedCoboundaryDecision:
    hnn = decide_target_hnn()
    shifted = apply_images(hnn.shifted_base_word, {"a": "p", "b": "q"})
    if shifted != P_WORD:
        raise AssertionError("the terminal HNN base word drifted")

    phi_images = {"p": "q", "q": "pqPq"}
    if apply_images(Q_WORD, phi_images) != P_WORD:
        raise AssertionError("the exact one-step HNN descent drifted")
    if abelianization(P_WORD) != (0, 7):
        raise AssertionError("the terminal HNN base abelianization drifted")
    if abelianization(Q_WORD) != (-1, 4):
        raise AssertionError("the descended HNN word abelianization drifted")

    c_p = specialize_t(fox_abelian(P_WORD, "p"))
    c_q = specialize_t(fox_abelian(P_WORD, "q"))
    if tuple(sorted(c_p.items())) != EXPECTED_C_P:
        raise AssertionError("the specialized p-Fox row drifted")
    if tuple(sorted(c_q.items())) != EXPECTED_C_Q:
        raise AssertionError("the specialized q-Fox row drifted")

    rhs = build_rhs(c_p, c_q)
    if tuple(sorted(rhs.items())) != EXPECTED_R:
        raise AssertionError("the terminal Mahler right side drifted")
    forced = force_high_coefficients(rhs)
    expected_forced = {
        12: 1,
        11: 1,
        10: 0,
        9: 1,
        8: 0,
        7: 0,
        6: 1,
        5: 1,
        4: 0,
        3: 0,
        2: 2,
    }
    if forced != expected_forced:
        raise AssertionError("the forced Mahler coefficients drifted")
    left_coefficient = l_coefficient(forced, 6)
    right_coefficient = rhs.get(6, 0)
    if left_coefficient == right_coefficient:
        raise AssertionError("the terminal Mahler contradiction disappeared")

    return TwistedCoboundaryDecision(
        p_word=P_WORD,
        q_word=Q_WORD,
        p_abelianization=abelianization(P_WORD),
        q_abelianization=abelianization(Q_WORD),
        c_p=tuple(sorted(c_p.items())),
        c_q=tuple(sorted(c_q.items())),
        rhs=tuple(sorted(rhs.items())),
        forced_coefficients=tuple(sorted(forced.items())),
        contradiction_degree=6,
        left_coefficient=left_coefficient,
        right_coefficient=right_coefficient,
        verdict="NO_TERMINAL_HNN_BASE_CONJUGATOR",
    )


if __name__ == "__main__":
    print(decide_twisted_coboundary())
