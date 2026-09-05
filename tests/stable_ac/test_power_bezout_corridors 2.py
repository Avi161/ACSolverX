from math import gcd

from experiments.equivalence_classes.lib.autcanon import aut_canon
from experiments.equivalence_classes.lib.words import apply_hom, cyc_reduce
from experiments.stable_ac.rank3_compression.two_stabilization import (
    cyclic_orientations,
    free_reduce,
    substitute_generator,
)


V = "zxZ"
V_INVERSE = "zXZ"
A = "xxxzXXXXZ"
B = "ZxzxZ"
P0 = ("xxxyXXXXY", "YxyxY")


def x_power(exponent: int) -> str:
    return "x" * exponent if exponent >= 0 else "X" * (-exponent)


def v_power(exponent: int) -> str:
    block = V if exponent >= 0 else V_INVERSE
    return free_reduce(block * abs(exponent))


def relabel_t(pair: tuple[str, str]) -> tuple[str, str]:
    return tuple(
        word.translate(str.maketrans("tT", "yY"))
        for word in pair
    )


def test_euclidean_relator_reduction_for_both_odd_residue_classes():
    rotated_a = free_reduce(v_power(-4) + "xxx")
    assert rotated_a in cyclic_orientations(A)

    for r in range(5):
        for residue in (1, 3):
            k = 4 * r + residue
            current = free_reduce("T" + v_power(k))

            for step in range(r):
                product = free_reduce(current + rotated_a)
                current = free_reduce(
                    x_power(3 * (step + 1))
                    + "T"
                    + v_power(k - 4 * (step + 1))
                )
                assert current in cyclic_orientations(product)

            if residue == 1:
                assert current == free_reduce(
                    x_power(3 * r) + "T" + V
                )
            else:
                assert current == free_reduce(
                    x_power(3 * r) + "T" + v_power(3)
                )
                rotated_current = free_reduce(
                    v_power(3) + x_power(3 * r) + "T"
                )
                product = free_reduce(A + rotated_current)
                isolator = free_reduce(
                    x_power(3 * r) + "Txxx" + V_INVERSE
                )
                assert isolator in cyclic_orientations(product)


def test_power_bezout_endpoints_have_only_two_aut_orbits():
    plus_base = None
    minus_base = None

    for r in range(5):
        plus_u = "t" + x_power(-3 * r)
        plus_z = free_reduce("x" + plus_u)
        plus_pair = relabel_t(
            (
                substitute_generator(
                    x_power(3 * r) + "T" + V,
                    "z",
                    plus_z,
                ),
                substitute_generator(A, "z", plus_z),
            )
        )
        assert plus_pair == (
            x_power(3 * r) + "YxyxYX",
            "xxxxyXXXXYX",
        )

        minus_u = x_power(3 * r) + "Txxx"
        minus_z = free_reduce("x" + minus_u)
        minus_pair = relabel_t(
            (
                substitute_generator(
                    x_power(3 * r) + "Txxx" + V_INVERSE,
                    "z",
                    minus_z,
                ),
                substitute_generator(
                    x_power(3 * r) + "T" + v_power(3),
                    "z",
                    minus_z,
                ),
            )
        )
        assert minus_pair == (
            x_power(3 * r)
            + "Y"
            + x_power(3 * r + 4)
            + "YXy"
            + x_power(-3 * r - 1),
            x_power(3 * r)
            + "Y"
            + x_power(3 * r + 1)
            + "Yxxxy"
            + x_power(-3 * r - 1),
        )

        shear = {"x": "x", "y": "y" + x_power(3 * r)}
        plus_image = tuple(
            free_reduce(apply_hom(word, shear)) for word in plus_pair
        )
        minus_image = tuple(
            free_reduce(apply_hom(word, shear)) for word in minus_pair
        )
        if r == 0:
            plus_base = plus_image
            minus_base = minus_image
        assert plus_image == plus_base
        assert minus_image == minus_base

        plus_floor, plus_rep, _ = aut_canon(plus_pair)
        minus_floor, minus_rep, _ = aut_canon(minus_pair)
        assert (plus_floor, plus_rep) == (
            14,
            ("YXXYx", "YYYYXyyyx"),
        )
        assert (minus_floor, minus_rep) == (
            15,
            ("YXXYx", "YYYXYxyyyX"),
        )

    root_map = {"x": "x", "y": "Xy"}
    assert tuple(
        free_reduce(apply_hom(word, root_map))
        for word in plus_base
    ) == (P0[1], P0[0])


def test_even_powers_fail_the_abelian_recovery_equation():
    for k in range(-20, 21):
        recoverable = gcd(4, 3 * k) == 1
        assert recoverable == (k % 2 != 0)
        if k % 2 == 0:
            assert all(
                4 * m + 3 * k * n != 3
                for m in range(-20, 21)
                for n in range(-20, 21)
            )


def test_two_sided_x_flanks_are_removed_by_an_ambient_shear():
    for p in range(-3, 4):
        for q in range(-3, 4):
            for k in range(-5, 6):
                defining = free_reduce(
                    "T"
                    + x_power(p)
                    + v_power(k)
                    + x_power(q)
                )
                sheared = substitute_generator(
                    defining,
                    "t",
                    x_power(p) + "t" + x_power(q),
                )
                bare = free_reduce("T" + v_power(k))
                assert bare in cyclic_orientations(cyc_reduce(sheared))


def test_k1_recovery_word_is_not_unique_modulo_the_power_relator():
    compressed_power = "xxxTTTT"
    rotated_power = "TTTTxxx"
    assert rotated_power in cyclic_orientations(compressed_power)

    canonical_u = "t"
    twisted_u = free_reduce(canonical_u + rotated_power)
    assert twisted_u == "TTTxxx"

    z_expression = free_reduce("x" + twisted_u)
    endpoint = relabel_t(
        (
            substitute_generator(A, "z", z_expression),
            substitute_generator("T" + V, "z", z_expression),
        )
    )
    assert endpoint == (
        "xxxxYYYXXXXyyyX",
        "YxYYYxyyyX",
    )

    floor, representative, _ = aut_canon(endpoint)
    assert floor == 23
    assert representative == (
        "YXXXYxxxyX",
        "YYYYxxxyyyXXX",
    )
