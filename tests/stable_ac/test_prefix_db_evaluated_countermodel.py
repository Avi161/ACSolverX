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


def test_fox_subgroup_has_disjoint_projected_axes():
    repositioner = "xtX"
    candidate_c = free_reduce(repositioner + inv(C) + inv(repositioner))
    rho = free_reduce(repositioner + "xT" + inv(repositioner))
    conjugate_c = free_reduce(rho + candidate_c + inv(rho))
    candidate_b = free_reduce(candidate_c + conjugate_c)

    assert len(projected_conjugacy_key(candidate_c)) == 2
    assert len(projected_conjugacy_key(conjugate_c)) == 2
    assert len(projected_conjugacy_key(candidate_b)) == 6


def test_fox_s4_projection_restricts_the_target_to_the_p_stabilizer():
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
    candidate_h = free_reduce(gamma + candidate_b + inv(gamma))
    alpha = "t"

    def compose(
        left: tuple[int, ...],
        right: tuple[int, ...],
    ) -> tuple[int, ...]:
        return tuple(left[right[index]] for index in range(4))

    def permutation_inverse(
        permutation: tuple[int, ...],
    ) -> tuple[int, ...]:
        result = [0] * 4
        for source, target in enumerate(permutation):
            result[target] = source
        return tuple(result)

    identity = (0, 1, 2, 3)
    x_permutation = (0, 2, 3, 1)
    t_permutation = (1, 2, 3, 0)
    letter_permutations = {
        "x": x_permutation,
        "X": permutation_inverse(x_permutation),
        "t": t_permutation,
        "T": permutation_inverse(t_permutation),
    }

    def evaluate_permutation(word: str) -> tuple[int, ...]:
        result = identity
        for letter in word:
            result = compose(result, letter_permutations[letter])
        return result

    def generated_subgroup(
        generators: tuple[tuple[int, ...], ...],
    ) -> set[tuple[int, ...]]:
        subgroup = {identity}
        frontier = [identity]
        signed_generators = generators + tuple(
            permutation_inverse(generator) for generator in generators
        )
        while frontier:
            current = frontier.pop()
            for generator in signed_generators:
                product_permutation = compose(current, generator)
                if product_permutation not in subgroup:
                    subgroup.add(product_permutation)
                    frontier.append(product_permutation)
        return subgroup

    quotient_group = generated_subgroup((x_permutation, t_permutation))
    p_image = generated_subgroup(
        (
            evaluate_permutation(candidate_k),
            evaluate_permutation(candidate_h),
        )
    )

    assert len(quotient_group) == 24
    assert len(p_image) == 6
    assert all(permutation[3] == 3 for permutation in p_image)

    multiplier = free_reduce(
        gamma + candidate_b + beta + inv(candidate_k)
    )
    constant_seed = (
        ("T", 1),
        (candidate_d, -1),
        (free_reduce(candidate_d + alpha + inv(candidate_e)), -1),
    )
    constant_terms = []
    for word, coefficient in constant_seed:
        constant_terms.append((word, coefficient))
        constant_terms.append(
            (free_reduce(multiplier + word), coefficient)
        )
    constant_terms.append((free_reduce(gamma + inv(candidate_e)), 1))
    u_terms = (
        (candidate_d, 1),
        (free_reduce(multiplier + candidate_d), 1),
        (candidate_k, -1),
        (free_reduce(multiplier + candidate_k), -1),
    )

    def coset_index(word: str) -> int:
        permutation = evaluate_permutation(word)
        return permutation_inverse(permutation)[3]

    def coset_vector(
        terms: list[tuple[str, int]] | tuple[tuple[str, int], ...],
    ) -> tuple[int, int, int, int]:
        result = [0, 0, 0, 0]
        for word, coefficient in terms:
            result[coset_index(word)] += coefficient
        return tuple(result)

    constant_vector = coset_vector(constant_terms)
    u_vector = coset_vector(u_terms)

    assert constant_vector == (0, -2, 0, 1)
    assert u_vector == (2, 0, 0, -2)

    target_differences = []
    for target_index in range(4):
        difference = tuple(
            -(1 if index == target_index else 0) - constant_vector[index]
            for index in range(4)
        )
        target_differences.append(
            sum(difference) == 0
            and all(coordinate % 2 == 0 for coordinate in difference)
        )

    assert target_differences == [False, False, False, True]


def test_fox_folded_core_recognizes_p_and_its_central_lifts():
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
    candidate_h = free_reduce(gamma + candidate_b + inv(gamma))
    multiplier = free_reduce(
        gamma + candidate_b + beta + inv(candidate_k)
    )
    target_q = free_reduce(gamma + inv(candidate_e))

    core_states = (0, 1, 2, 4, 5, 8, 9, 11, 12)
    core_index = {
        state: index
        for index, state in enumerate(core_states)
    }
    x_cycles = ((0, 1, 2), (5, 8, 9))
    t_cycles = ((1, 2, 4, 5), (8, 9, 11, 12))

    def transition(
        cycles: tuple[tuple[int, ...], ...],
        state: int,
        exponent: int,
    ) -> int | None:
        for cycle in cycles:
            if state in cycle:
                return cycle[(cycle.index(state) + exponent) % len(cycle)]
        return None

    def loop_coordinates(word: str) -> tuple[int, int] | None:
        state = 0
        raw_chain = [0] * len(core_states)
        for generator, exponent in normal_form(word)[1]:
            cycles = x_cycles if generator == "x" else t_cycles
            destination = transition(cycles, state, exponent)
            if destination is None:
                return None
            source_index = core_index[state]
            destination_index = core_index[destination]
            if generator == "x":
                raw_chain[source_index] -= 1
                raw_chain[destination_index] += 1
            else:
                raw_chain[source_index] += 1
                raw_chain[destination_index] -= 1
            state = destination

        if state != 0 or any(value % 2 for value in raw_chain):
            return None
        chain = [value // 2 for value in raw_chain]
        h_exponent = chain[5]
        k_exponent = chain[1] - h_exponent
        return k_exponent, h_exponent

    def lies_in_p(word: str) -> bool:
        coordinates = loop_coordinates(word)
        if coordinates is None:
            return False
        k_exponent, h_exponent = coordinates
        return torus_weight(word) == -k_exponent - 2 * h_exponent

    assert loop_coordinates(candidate_k) == (1, 0)
    assert loop_coordinates(candidate_h) == (0, 1)
    assert lies_in_p(candidate_k)
    assert lies_in_p(candidate_h)
    assert lies_in_p(free_reduce(candidate_k + candidate_h))
    assert not lies_in_p(free_reduce("xxx" + candidate_k))
    assert not lies_in_p(multiplier)
    assert not lies_in_p(target_q)
    assert normal_form(target_q) == normal_form("XXX" + multiplier)


def test_fox_binary_s4_lift_excludes_identity_and_q_targets():
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
    candidate_h = free_reduce(gamma + candidate_b + inv(gamma))
    alpha = "t"
    multiplier = free_reduce(
        gamma + candidate_b + beta + inv(candidate_k)
    )
    target_q = free_reduce(gamma + inv(candidate_e))

    prime = 3
    identity = (1, 0, 0, 1)
    negative_identity = (2, 0, 0, 2)
    x_matrix = (0, 1, 2, 1)
    t_matrix = (0, 1, 1, 1)

    def multiply(
        left: tuple[int, int, int, int],
        right: tuple[int, int, int, int],
    ) -> tuple[int, int, int, int]:
        a, b, c, d = left
        e, f, g, h = right
        return (
            (a * e + b * g) % prime,
            (a * f + b * h) % prime,
            (c * e + d * g) % prime,
            (c * f + d * h) % prime,
        )

    def matrix_inverse(
        matrix: tuple[int, int, int, int],
    ) -> tuple[int, int, int, int]:
        a, b, c, d = matrix
        determinant = (a * d - b * c) % prime
        scale = pow(determinant, -1, prime)
        return (
            d * scale % prime,
            -b * scale % prime,
            -c * scale % prime,
            a * scale % prime,
        )

    letter_matrices = {
        "x": x_matrix,
        "X": matrix_inverse(x_matrix),
        "t": t_matrix,
        "T": matrix_inverse(t_matrix),
    }

    def evaluate_matrix(word: str) -> tuple[int, int, int, int]:
        result = identity
        for letter in word:
            result = multiply(result, letter_matrices[letter])
        return result

    def add_terms(
        terms: tuple[tuple[str, int], ...] | list[tuple[str, int]],
    ) -> tuple[int, int, int, int]:
        result = [0, 0, 0, 0]
        for word, coefficient in terms:
            matrix = evaluate_matrix(word)
            for index, value in enumerate(matrix):
                result[index] = (
                    result[index] + coefficient * value
                ) % prime
        return tuple(result)

    def row_multiply(
        row: tuple[int, int],
        matrix: tuple[int, int, int, int],
    ) -> tuple[int, int]:
        return (
            (row[0] * matrix[0] + row[1] * matrix[2]) % prime,
            (row[0] * matrix[1] + row[1] * matrix[3]) % prime,
        )

    def generated_group(
        generators: tuple[tuple[int, int, int, int], ...],
    ) -> set[tuple[int, int, int, int]]:
        subgroup = {identity}
        frontier = [identity]
        signed_generators = generators + tuple(
            matrix_inverse(generator)
            for generator in generators
        )
        while frontier:
            current = frontier.pop()
            for generator in signed_generators:
                candidate = multiply(current, generator)
                if candidate not in subgroup:
                    subgroup.add(candidate)
                    frontier.append(candidate)
        return subgroup

    constant_terms: list[tuple[str, int]] = []
    for word, coefficient in (
        ("T", 1),
        (candidate_d, -1),
        (free_reduce(candidate_d + alpha + inv(candidate_e)), -1),
    ):
        constant_terms.append((word, coefficient))
        constant_terms.append(
            (free_reduce(multiplier + word), coefficient)
        )
    constant_terms.append((target_q, 1))
    u_terms = (
        (candidate_d, 1),
        (free_reduce(multiplier + candidate_d), 1),
        (candidate_k, -1),
        (free_reduce(multiplier + candidate_k), -1),
    )

    assert evaluate_matrix("xxx") == negative_identity
    assert evaluate_matrix("tttt") == negative_identity
    assert evaluate_matrix(candidate_k) == (1, 1, 0, 2)
    assert evaluate_matrix(candidate_h) == (2, 2, 1, 0)

    constant_matrix = add_terms(constant_terms)
    u_matrix = add_terms(u_terms)
    assert constant_matrix == (2, 1, 1, 2)
    assert u_matrix == (1, 0, 1, 0)

    row = (1, 2)
    assert row_multiply(row, evaluate_matrix(candidate_k)) == row
    assert row_multiply(row, evaluate_matrix(candidate_h)) == row
    assert row_multiply(row, constant_matrix) == row
    assert row_multiply(row, u_matrix) == (0, 0)

    quotient_group = generated_group((x_matrix, t_matrix))
    p_image = generated_group(
        (
            evaluate_matrix(candidate_k),
            evaluate_matrix(candidate_h),
        )
    )
    assert len(quotient_group) == 48
    assert len(p_image) == 6
    assert all(row_multiply(row, element) == row for element in p_image)

    allowed_targets = {
        element
        for element in quotient_group
        if row_multiply(row, element) == (2, 1)
    }
    assert allowed_targets == {
        multiply(negative_identity, element)
        for element in p_image
    }
    assert identity not in allowed_targets
    assert evaluate_matrix(target_q) not in allowed_targets
    assert negative_identity in allowed_targets
