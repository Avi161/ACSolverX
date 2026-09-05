from __future__ import annotations

from experiments.equivalence_classes.lib.words import free_reduce, inv
from experiments.stable_ac.rank3_compression.recovery_word_equation import (
    normal_form,
)


R = "xxxTTTT"
B = "Zxt"
D = "TzxZ"
IDENTITY = (0, ())


def normal_form_word(state: tuple) -> str:
    central, syllables = state
    central_word = "xxx" * central if central >= 0 else "XXX" * (-central)
    return central_word + "".join(
        generator * exponent for generator, exponent in syllables
    )


def multiply_g(left: tuple, right: tuple) -> tuple:
    return normal_form(normal_form_word(left) + normal_form_word(right))


def inverse_g(state: tuple) -> tuple:
    return normal_form(inv(normal_form_word(state)))


def append_factor(factors: list, tag: str, value) -> None:
    if (tag == "g" and value == IDENTITY) or (tag == "z" and value == 0):
        return

    if factors and factors[-1][0] == tag:
        previous = factors.pop()[1]
        value = (
            multiply_g(previous, value)
            if tag == "g"
            else previous + value
        )
        if (
            (tag == "g" and value != IDENTITY)
            or (tag == "z" and value != 0)
        ):
            factors.append((tag, value))
        return

    factors.append((tag, value))


def free_product_normal_form(word: str) -> tuple:
    factors = []
    for letter in word:
        if letter == "z":
            append_factor(factors, "z", 1)
        elif letter == "Z":
            append_factor(factors, "z", -1)
        else:
            append_factor(factors, "g", normal_form(letter))
    return tuple(factors)


def multiply(left: tuple, right: tuple) -> tuple:
    factors = list(left)
    for tag, value in right:
        append_factor(factors, tag, value)
    return tuple(factors)


def inverse(word: tuple) -> tuple:
    factors = []
    for tag, value in reversed(word):
        append_factor(
            factors,
            tag,
            inverse_g(value) if tag == "g" else -value,
        )
    return tuple(factors)


def cyclic_reduce(word: tuple) -> tuple:
    factors = list(word)
    while len(factors) > 1 and factors[0][0] == factors[-1][0]:
        tag = factors[0][0]
        first = factors.pop(0)[1]
        last = factors.pop()[1]
        combined = (
            multiply_g(last, first)
            if tag == "g"
            else last + first
        )
        append_factor(factors, tag, combined)
    return tuple(factors)


def rotations(word: tuple) -> tuple:
    return tuple(word[index:] + word[:index] for index in range(len(word)))


def cyclic_key(word: tuple) -> tuple:
    word = cyclic_reduce(word)
    return min(rotations(word) + rotations(cyclic_reduce(inverse(word))))


def z_incidence(word: tuple) -> int:
    return sum(abs(value) for tag, value in word if tag == "z")


def conjugate(word: str, by: str) -> str:
    return free_reduce(by + word + inv(by))


def test_quotient_signed_rotation_residue_has_two_isolator_classes():
    b = free_product_normal_form(B)
    d = free_product_normal_form(D)
    witnesses = []

    for sign, source in ((1, d), (-1, inverse(d))):
        for b_index, b_rotation in enumerate(rotations(b)):
            for d_index, d_rotation in enumerate(rotations(source)):
                product = cyclic_reduce(multiply(b_rotation, d_rotation))
                if z_incidence(product) == 1:
                    witnesses.append(
                        (
                            sign,
                            b_index,
                            d_index,
                            cyclic_key(product),
                        )
                    )

    assert [(sign, b_index, d_index) for sign, b_index, d_index, _ in witnesses] == [
        (1, 0, 2),
        (1, 1, 1),
        (-1, 0, 1),
        (-1, 1, 0),
    ]
    assert {key for _, _, _, key in witnesses} == {
        cyclic_key(free_product_normal_form("ZTxtx")),
        cyclic_key(free_product_normal_form("ZtxtX")),
    }


def test_pre_catalyst_r_gauges_leave_both_quotient_shadows_unchanged():
    b_gauge = free_reduce(
        conjugate(R, "zX")
        + conjugate(inv(R), "Tzxt")
    )
    d_gauge = free_reduce(
        conjugate(inv(R), "xZt")
        + conjugate(R, "zzX")
    )
    twisted_b = free_reduce(B + b_gauge)
    twisted_d = free_reduce(D + d_gauge)

    assert free_product_normal_form(twisted_b) == free_product_normal_form(B)
    assert free_product_normal_form(twisted_d) == free_product_normal_form(D)
    assert free_product_normal_form(
        twisted_b + twisted_d
    ) == free_product_normal_form(B + D)


def test_g_vertex_stabilizer_twists_force_the_same_two_classes():
    b = free_product_normal_form(B)
    d = free_product_normal_form(D)
    positive_forcing = (
        (
            lambda h: "xt" + h + "T",
            lambda h: "xt" + h,
            lambda h: inv(h),
            lambda h: "x" + inv(h),
        ),
        (
            lambda h: h + "T",
            lambda h: h,
            lambda h: inv(h) + "xt",
            lambda h: "x" + inv(h) + "xt",
        ),
    )
    negative_forcing = (
        (
            lambda h: "xt" + h,
            lambda h: inv(h),
            lambda h: "X" + inv(h),
            lambda h: "xt" + h + "t",
        ),
        (
            lambda h: h,
            lambda h: inv(h) + "xt",
            lambda h: "X" + inv(h) + "xt",
            lambda h: h + "t",
        ),
    )
    tables = (
        (
            1,
            d,
            (
                ("TXt", "TX", "", "x"),
                ("t", "", "xt", "xtx"),
            ),
            positive_forcing,
            free_product_normal_form("ZTxtx"),
        ),
        (
            -1,
            inverse(d),
            (
                ("TX", "", "X", "TXT"),
                ("", "xt", "xtX", "T"),
            ),
            negative_forcing,
            free_product_normal_form("ZtxtX"),
        ),
    )

    for _, source, twist_table, forcing_table, expected in tables:
        for b_index, b_rotation in enumerate(rotations(b)):
            for d_index, d_rotation in enumerate(rotations(source)):
                twist_word = twist_table[b_index][d_index]
                assert normal_form(
                    free_reduce(
                        forcing_table[b_index][d_index](twist_word)
                    )
                ) == IDENTITY
                twist = free_product_normal_form(twist_word)
                product = cyclic_reduce(
                    multiply(
                        multiply(
                            multiply(b_rotation, twist),
                            d_rotation,
                        ),
                        inverse(twist),
                    )
                )
                assert z_incidence(product) == 1
                assert cyclic_key(product) == cyclic_key(expected)


def test_z_vertex_stabilizer_twists_have_only_four_solutions_per_sign():
    b = free_product_normal_form(B)
    d = free_product_normal_form(D)
    expected = {
        1: {
            (0, 1, -1),
            (0, 2, 0),
            (1, 1, 0),
            (1, 2, 1),
        },
        -1: {
            (0, 0, -1),
            (0, 1, 0),
            (1, 0, 0),
            (1, 1, 1),
        },
    }

    for sign, source in ((1, d), (-1, inverse(d))):
        witnesses = set()
        centered_exponents = {
            (b_index, d_index): solution
            for b_index, d_index, solution in expected[sign]
        }
        for exponent in range(-20, 21):
            twist = () if exponent == 0 else (("z", exponent),)
            for b_index, b_rotation in enumerate(rotations(b)):
                for d_index, d_rotation in enumerate(rotations(source)):
                    product = cyclic_reduce(
                        multiply(
                            multiply(
                                multiply(b_rotation, twist),
                                d_rotation,
                            ),
                            inverse(twist),
                        )
                    )
                    key = (b_index, d_index)
                    if key in centered_exponents:
                        assert z_incidence(product) == (
                            2
                            * abs(exponent - centered_exponents[key])
                            + 1
                        )
                    else:
                        assert z_incidence(product) >= 3

                    if z_incidence(product) == 1:
                        witnesses.add((b_index, d_index, exponent))
                        template = "ZTxtx" if sign == 1 else "ZtxtX"
                        assert cyclic_key(product) == cyclic_key(
                            free_product_normal_form(template)
                        )

        assert witnesses == expected[sign]
