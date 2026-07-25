from __future__ import annotations

from itertools import product

from experiments.equivalence_classes.lib.words import cyc_reduce, free_reduce, inv


B = "Zxt"
D = "TzxZ"
D_P = "TxtxTX"


def rotations(word: str) -> tuple[str, ...]:
    word = cyc_reduce(word)
    return tuple(word[index:] + word[:index] for index in range(len(word)))


def signed_rotations(word: str) -> tuple[str, ...]:
    return tuple(set(rotations(word) + rotations(inv(word))))


def cyclic_key(word: str) -> str:
    return min(signed_rotations(cyc_reduce(word)))


def cross_classes(target: str, source: str) -> set[str]:
    return {
        cyclic_key(cyc_reduce(target_rotation + source_rotation))
        for target_rotation in signed_rotations(target)
        for source_rotation in signed_rotations(source)
    }


def z_incidence(word: str) -> int:
    return sum(letter in "zZ" for letter in word)


def one_z_tail(word: str) -> str | None:
    word = cyc_reduce(word)
    if z_incidence(word) != 1:
        return None
    if "z" in word:
        word = inv(word)
    z_index = word.index("Z")
    word = word[z_index:] + word[:z_index]
    return free_reduce(word[1:])


def substitute_z(word: str, value: str) -> str:
    inverse_value = inv(value)
    return free_reduce(
        "".join(
            value if letter == "z" else inverse_value if letter == "Z" else letter
            for letter in word
        )
    )


def test_three_closed_one_switch_target_words_have_the_forced_exponents():
    for first_sign, second_sign, third_sign in product((1, -1), repeat=3):
        bbd_b2_exponent = -1
        bbd_d1_exponent = third_sign * bbd_b2_exponent
        assert abs(bbd_b2_exponent) == 1
        assert abs(bbd_d1_exponent) == 1

        bdd_b1_exponent = -1
        bdd_d2_exponent = (
            second_sign * bdd_b1_exponent
            + third_sign * bdd_b1_exponent
        )
        assert abs(bdd_d2_exponent) in (0, 2)

        ddb_d2_exponent = -(first_sign + second_sign)
        ddb_b1_exponent = -1 + third_sign * ddb_d2_exponent
        assert abs(ddb_d2_exponent) in (0, 2)
        assert abs(ddb_b1_exponent) in (1, 3)


def test_dbb_has_exactly_six_killer_rows():
    expected = {
        (1, 1, -1): (1, 7, -1, 1),
        (1, -1, 1): (1, 7, -1, 1),
        (1, -1, -1): (-1, 9, -1, -1),
        (-1, 1, 1): (-1, 5, 1, -1),
        (-1, 1, -1): (1, 7, 1, 1),
        (-1, -1, 1): (1, 7, 1, 1),
    }
    actual = {}

    for first_sign, second_sign, third_sign in product((1, -1), repeat=3):
        d1_exponent = -first_sign
        b1_exponent = -1 + second_sign * d1_exponent
        b2_exponent = b1_exponent + third_sign * d1_exponent
        if abs(b2_exponent) != 1:
            assert (first_sign, second_sign, third_sign) in {
                (1, 1, 1),
                (-1, -1, -1),
            }
            assert abs(b2_exponent) == 3
            continue

        final_orientation = -b2_exponent
        d1_weight = 1 + 7 * first_sign
        b1_weight = 7 + second_sign * d1_weight
        b2_weight = b1_weight + third_sign * d1_weight
        tail_weight = final_orientation * b2_weight
        survivor_weight = d1_weight + d1_exponent * tail_weight

        actual[(first_sign, second_sign, third_sign)] = (
            final_orientation,
            tail_weight,
            d1_exponent,
            survivor_weight,
        )

    assert actual == expected


def test_every_untwisted_dbb_seam_returns_to_the_d_p_class():
    first_targets = cross_classes(D, B)
    intermediate_pairs = {
        (first_target, second_target)
        for first_target in first_targets
        for second_target in cross_classes(B, first_target)
    }
    final_triples = set()
    final_targets = set()
    survivor_classes = set()

    for first_target, second_target in intermediate_pairs:
        for third_target in cross_classes(second_target, first_target):
            tail = one_z_tail(third_target)
            if tail is None:
                continue
            final_triples.add((first_target, second_target, third_target))
            final_targets.add(third_target)
            survivor_classes.add(
                cyclic_key(substitute_z(first_target, tail))
            )

    assert len(first_targets) == 16
    assert len(intermediate_pairs) == 416
    assert len(final_triples) == 522
    assert len(final_targets) == 69
    assert survivor_classes == {cyclic_key(D_P)}
