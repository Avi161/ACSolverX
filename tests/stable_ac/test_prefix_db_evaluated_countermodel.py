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


def relative_axis_length_counts(left_word: str, right_word: str) -> Counter[int]:
    left = projected_cyclic_reduce(normal_form(left_word)[1])
    right = projected_cyclic_reduce(normal_form(right_word)[1])
    twists = ("", "x", "xx", "t", "tt", "ttt")
    length_counts = Counter()

    for left_rotation in syllable_rotations(left):
        for right_rotation in syllable_rotations(right):
            for twist in twists:
                product_shadow = (
                    syllable_word(left_rotation)
                    + twist
                    + syllable_word(right_rotation)
                    + inv(twist)
                )
                length_counts[len(projected_conjugacy_key(product_shadow))] += 1

    return length_counts


def evaluate_stable_letter(word: str, replacement: str) -> str:
    evaluated = ""
    for letter in word:
        if letter == "z":
            evaluated += replacement
        elif letter == "Z":
            evaluated += inv(replacement)
        else:
            evaluated += letter
    return free_reduce(evaluated)


def evaluation_kernel_cyclic_word(
    word: str,
    replacement: str,
) -> tuple[tuple[tuple[int, tuple[tuple[str, int], ...]], int], ...]:
    prefix = ""
    basis_word: list[
        tuple[tuple[int, tuple[tuple[str, int], ...]], int]
    ] = []

    def append_basis(
        index: tuple[int, tuple[tuple[str, int], ...]],
        sign: int,
    ) -> None:
        if basis_word and basis_word[-1] == (index, -sign):
            basis_word.pop()
        else:
            basis_word.append((index, sign))

    for letter in word:
        if letter == "z":
            append_basis(normal_form(prefix), 1)
            prefix = free_reduce(prefix + replacement)
        elif letter == "Z":
            prefix = free_reduce(prefix + inv(replacement))
            append_basis(normal_form(prefix), -1)
        else:
            prefix = free_reduce(prefix + letter)

    assert normal_form(prefix) == (0, ())

    while (
        len(basis_word) > 1
        and basis_word[0][0] == basis_word[-1][0]
        and basis_word[0][1] == -basis_word[-1][1]
    ):
        basis_word = basis_word[1:-1]

    return tuple(basis_word)


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


def test_first_cross_excludes_only_the_four_fixed_minimum_templates():
    expected = {
        ("positive", "xttt"): Counter({20: 118, 18: 42, 16: 26, 14: 20, 12: 10}),
        ("positive", "xtt"): Counter({20: 118, 14: 40, 18: 35, 16: 23}),
        ("dual", "xttt"): Counter({24: 150, 20: 59, 22: 35, 16: 10, 18: 10}),
        ("dual", "xtt"): Counter(
            {24: 142, 22: 49, 16: 30, 20: 23, 14: 10, 18: 10}
        ),
    }

    for row, candidate_c in (("positive", C), ("dual", inv(C))):
        for rho in ("xttt", "xtt"):
            candidate_b = free_reduce(
                candidate_c + rho + candidate_c + inv(rho)
            )
            candidate_e = free_reduce(P + inv(candidate_b))
            candidate_d = free_reduce(
                "T" + candidate_e + "x" + inv(candidate_e)
            )
            counts = relative_axis_length_counts(inv(candidate_d), inv(C))

            assert counts == expected[(row, rho)]
            assert 6 not in counts


def test_repositioned_minimum_tail_solves_all_evaluated_equations():
    repositioner = "xtX"
    candidate_c = free_reduce(repositioner + inv(C) + inv(repositioner))
    rho = free_reduce(repositioner + "xT" + inv(repositioner))
    gamma = "xTX"
    beta = free_reduce(rho + inv(gamma))
    candidate_b = free_reduce(
        candidate_c + rho + candidate_c + inv(rho)
    )
    candidate_e = free_reduce(P + inv(candidate_b))
    candidate_d = free_reduce(
        "T" + candidate_e + "x" + inv(candidate_e)
    )
    candidate_k = free_reduce(gamma + candidate_c + inv(gamma))
    alpha = "t"

    assert normal_form(candidate_k) == normal_form(
        candidate_d + alpha + candidate_b + inv(alpha)
    )
    assert normal_form(candidate_c) == normal_form(
        candidate_b + beta + inv(candidate_k) + inv(beta)
    )
    assert normal_form(
        candidate_k + gamma + inv(candidate_c) + inv(gamma)
    ) == (0, ())

    assert torus_weight(candidate_e) == 9
    assert torus_weight(candidate_b) == -2
    assert torus_weight(candidate_c) == -1
    assert projected_conjugacy_key(candidate_c) == (("t", 1), ("x", 2))
    assert len(projected_conjugacy_key(candidate_c)) == 2
    assert len(projected_conjugacy_key(D_P)) == 6
    assert projected_conjugacy_key(inv(candidate_b)) == (
        ("t", 1),
        ("x", 1),
        ("t", 2),
        ("x", 2),
        ("t", 3),
        ("x", 2),
    )


def test_repositioned_tail_replays_synchronized_quotient_b_arithmetic():
    repositioner = "xtX"
    candidate_c = free_reduce(repositioner + inv(C) + inv(repositioner))
    rho = free_reduce(repositioner + "xT" + inv(repositioner))
    gamma = "xTX"
    beta = free_reduce(rho + inv(gamma))
    candidate_b = free_reduce(
        candidate_c + rho + candidate_c + inv(rho)
    )

    quotient_witness = "xtX"
    beta_at_p = "xttX"
    bridge_difference = free_reduce(inv(beta) + beta_at_p)
    quotient_product = free_reduce(
        D_P + quotient_witness + D_P + inv(quotient_witness)
    )

    assert normal_form(gamma + beta) == normal_form("xT")
    assert normal_form(gamma + beta_at_p) == normal_form(quotient_witness)
    assert normal_form(bridge_difference) == normal_form("ttX")
    assert torus_weight(bridge_difference) == 2
    assert normal_form(quotient_product) == normal_form(inv(candidate_b))


def test_literal_g_bridge_lift_is_not_the_required_kernel_basis_letter():
    repositioner = "xtX"
    candidate_c = free_reduce(repositioner + inv(C) + inv(repositioner))
    rho = free_reduce(repositioner + "xT" + inv(repositioner))
    gamma = "xTX"
    beta = free_reduce(rho + inv(gamma))
    candidate_b = free_reduce(
        candidate_c + rho + candidate_c + inv(rho)
    )
    candidate_e = free_reduce(P + inv(candidate_b))
    alpha = "t"

    original_b = "Z" + P
    original_d = "TzxZ"
    first_target = free_reduce(
        original_d + alpha + original_b + inv(alpha)
    )
    second_target = free_reduce(
        original_b + beta + inv(first_target) + inv(beta)
    )
    third_target = free_reduce(
        first_target + gamma + inv(second_target) + inv(gamma)
    )
    isolator = "Z" + candidate_e

    assert normal_form(
        evaluate_stable_letter(third_target, candidate_e)
    ) == (0, ())
    assert len(evaluation_kernel_cyclic_word(isolator, candidate_e)) == 1
    assert len(evaluation_kernel_cyclic_word(third_target, candidate_e)) == 7
