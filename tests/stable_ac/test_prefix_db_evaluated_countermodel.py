from __future__ import annotations

from collections import Counter
from itertools import product
from math import gcd

from experiments.equivalence_classes.lib.words import free_reduce, inv
from experiments.stable_ac.rank3_compression.recovery_word_equation import (
    normal_form,
)


P = "xt"
D_P = "TxtxTX"

E = "XXXXXX" + "xtxtttxtx"
B = "XXXXXXXXX" + "xxtttxxtxx"
C = "XXXXXX" + "xxtttxx"
ALPHA = "xtxtttxt"
BETA = "xx"

D = free_reduce("T" + E + "x" + inv(E))
K = free_reduce(D + ALPHA + B + inv(ALPHA))
SECOND_TARGET = free_reduce(B + BETA + K + inv(BETA))

ORDERS = {"x": 3, "t": 4}


def torus_weight(word: str) -> int:
    central, syllables = normal_form(word)
    return 12 * central + sum(
        (4 if generator == "x" else 3) * exponent
        for generator, exponent in syllables
    )


def projected_cyclic_reduce(
    syllables: tuple[tuple[str, int], ...],
) -> tuple[tuple[str, int], ...]:
    reduced = list(syllables)
    while len(reduced) > 1 and reduced[0][0] == reduced[-1][0]:
        generator = reduced[0][0]
        exponent = (reduced[-1][1] + reduced[0][1]) % ORDERS[generator]
        reduced = reduced[1:-1]
        if exponent:
            reduced.insert(0, (generator, exponent))
    return tuple(reduced)


def projected_conjugacy_key(word: str) -> tuple[tuple[str, int], ...]:
    projected = projected_cyclic_reduce(normal_form(word)[1])
    if not projected:
        return ()
    return min(
        projected[index:] + projected[:index]
        for index in range(len(projected))
    )


def syllable_rotations(
    syllables: tuple[tuple[str, int], ...],
) -> tuple[tuple[tuple[str, int], ...], ...]:
    return tuple(
        syllables[index:] + syllables[:index]
        for index in range(len(syllables))
    )


def syllable_word(syllables: tuple[tuple[str, int], ...]) -> str:
    return "".join(
        generator * exponent
        for generator, exponent in syllables
    )


def intersecting_axis_length_counts(right_word: str) -> Counter[int]:
    braid = normal_form(D_P)[1]
    right = normal_form(right_word)[1]
    twists = ("", "x", "xx", "t", "tt", "ttt")
    length_counts = Counter()

    for left_rotation in syllable_rotations(braid):
        for right_rotation in syllable_rotations(right):
            for twist in twists:
                product_shadow = (
                    syllable_word(left_rotation)
                    + twist
                    + syllable_word(right_rotation)
                    + inv(twist)
                )
                cyclic = projected_cyclic_reduce(
                    normal_form(product_shadow)[1]
                )
                length_counts[len(cyclic)] += 1

    return length_counts


def intersecting_axis_class_counts(
    right_word: str,
    cyclic_length: int,
) -> Counter[tuple[tuple[str, int], ...]]:
    braid = normal_form(D_P)[1]
    right = normal_form(right_word)[1]
    twists = ("", "x", "xx", "t", "tt", "ttt")
    class_counts = Counter()

    for left_rotation in syllable_rotations(braid):
        for right_rotation in syllable_rotations(right):
            for twist in twists:
                product_shadow = (
                    syllable_word(left_rotation)
                    + twist
                    + syllable_word(right_rotation)
                    + inv(twist)
                )
                key = projected_conjugacy_key(product_shadow)
                if len(key) == cyclic_length:
                    class_counts[key] += 1

    return class_counts


def test_explicit_lifts_solve_every_evaluated_prefix_db_equation():
    assert normal_form(inv(E) + P) == normal_form(B)
    assert normal_form(K) == normal_form(C)
    assert normal_form(SECOND_TARGET) == normal_form(C)
    assert normal_form(K + inv(C)) == (0, ())


def test_countermodel_occupies_the_positive_positive_negative_row():
    assert torus_weight(E) == 7
    assert torus_weight(B) == 0
    assert torus_weight(D) == 1
    assert torus_weight(K) == 1
    assert torus_weight(C) == 1
    assert torus_weight(SECOND_TARGET) == 1


def test_survivor_is_a_projected_killer_but_not_in_the_braid_class():
    survivor_key = projected_conjugacy_key(C)

    assert survivor_key == (("t", 3), ("x", 1))
    assert len(survivor_key) == 2
    assert len(projected_conjugacy_key(D_P)) == 6
    assert len(projected_conjugacy_key(inv(D_P))) == 6
    assert survivor_key != projected_conjugacy_key(D_P)
    assert survivor_key != projected_conjugacy_key(inv(D_P))

    # Killing x t^{-1} identifies the C3 and C4 generators.
    assert gcd(3, 4) == 1


def test_quotient_b_commutator_sieve_excludes_the_countermodel():
    length_counts = intersecting_axis_length_counts(inv(D_P))

    assert length_counts == Counter({12: 130, 8: 40, 10: 28, 0: 18})
    assert len(projected_conjugacy_key(B)) == 4
    assert 4 not in length_counts


def test_quotient_b_same_orientation_sieve_has_length_floor_six():
    length_counts = intersecting_axis_length_counts(D_P)

    assert length_counts == Counter({12: 122, 6: 52, 10: 42})
    assert 0 not in length_counts
    assert 2 not in length_counts
    assert 4 not in length_counts


def test_every_feasible_row_has_the_claimed_quotient_b_spectrum():
    expected = {
        (1, 1, -1): (-1, 7, 0, -1),
        (1, -1, 1): (1, 7, 0, -1),
        (1, -1, -1): (1, 9, -2, 1),
        (-1, 1, 1): (-1, 5, 2, 1),
        (-1, 1, -1): (-1, 7, 0, -1),
        (-1, -1, 1): (1, 7, 0, -1),
    }
    actual = {}

    for epsilon, eta, theta in product((1, -1), repeat=3):
        d1_exponent = -epsilon
        b1_exponent = -1 + eta * d1_exponent
        d2_exponent = d1_exponent + theta * b1_exponent
        if abs(d2_exponent) != 1:
            continue

        delta = -d2_exponent
        d1_weight = 1 + 7 * epsilon
        b1_weight = 7 + eta * d1_weight
        d2_weight = d1_weight + theta * b1_weight
        tail_weight = delta * d2_weight
        b_weight = 7 - tail_weight

        actual[(epsilon, eta, theta)] = (
            delta,
            tail_weight,
            b_weight,
            eta * theta,
        )

    assert actual == expected


def test_same_orientation_length_six_has_exactly_two_classes():
    first = (("t", 1), ("x", 1), ("t", 2), ("x", 2), ("t", 3), ("x", 2))
    second = (("t", 1), ("x", 2), ("t", 3), ("x", 2), ("t", 2), ("x", 1))
    class_counts = intersecting_axis_class_counts(D_P, 6)

    assert class_counts == Counter({first: 26, second: 26})

    first_lift = "XXXXXXXXX" + "txttxxtttxx"
    second_lift = "XXXXXXXXX" + "txxtttxxttx"
    assert torus_weight(first_lift) == 2
    assert torus_weight(second_lift) == 2
    assert projected_conjugacy_key(first_lift) == first
    assert projected_conjugacy_key(second_lift) == second


def test_length_six_last_two_equations_still_allow_the_nonbraid_killer():
    expected_keys = {
        (("t", 1), ("x", 1), ("t", 2), ("x", 2), ("t", 3), ("x", 2)),
        (("t", 1), ("x", 2), ("t", 3), ("x", 2), ("t", 2), ("x", 1)),
    }
    positive_keys = set()
    negative_keys = set()

    for rho in ("xttt", "xtt"):
        positive_b = free_reduce(C + rho + C + inv(rho))
        positive_k = inv(C)
        positive_second = free_reduce(
            positive_b + rho + positive_k + inv(rho)
        )
        assert normal_form(positive_second) == normal_form(C)
        assert torus_weight(positive_b) == 2
        positive_keys.add(projected_conjugacy_key(positive_b))

        negative_c = inv(C)
        negative_b = free_reduce(
            negative_c + rho + negative_c + inv(rho)
        )
        negative_k = negative_c
        negative_second = free_reduce(
            negative_b + rho + inv(negative_k) + inv(rho)
        )
        assert normal_form(negative_second) == normal_form(negative_c)
        assert torus_weight(negative_b) == -2
        negative_keys.add(projected_conjugacy_key(inv(negative_b)))

    assert positive_keys == expected_keys
    assert negative_keys == expected_keys
