from fractions import Fraction
from math import gcd

from experiments.stable_ac.verify_ad_bs34_module import (
    A,
    D,
    affine_word_action,
    evaluated_ad_rows,
    evaluated_relative_row,
    finite_bs34_order_compatible,
    finite_cyclic_collapse_certificate,
    finite_module_replay,
    four_state_residuals,
    free_reduce,
    integer_progression_partition,
    inverse_word,
    progression_right_word,
    relative_free_u_action,
    substitute_word,
)


def test_universal_quotient_substitution_kills_d_and_conjugates_a_to_bs34():
    forward = {"x": "x", "t": "zxZ", "z": "z", "q": "zy"}

    assert free_reduce(substitute_word(D, forward)) == ""
    assert free_reduce(substitute_word(A, forward)) == "z" + "yxxxYXXXX" + "Z"
    assert forward["t"] == "zxZ"
    assert forward["q"] == "zy"
    assert free_reduce(inverse_word(forward["z"]) + forward["q"]) == "y"


def test_evaluated_fox_rows_are_the_literal_a_d_rows_in_the_quotient():
    a_row, d_row = evaluated_ad_rows()

    assert a_row == (
        {"q": 1, "qx": 1, "qxx": 1},
        {"": -1, "t": -1, "tt": -1, "ttt": -1},
        {},
        {"": 1, "tttt": -1},
    )
    assert d_row == (
        {"Tz": 1},
        {"T": -1},
        {"T": 1, "": -1},
        {},
    )


def test_relative_row_prefixes_g_times_d_row_and_rewrites_the_prefix():
    assert evaluated_relative_row(1, "x") == (
        {"q": 1, "qx": 1, "qxx": 1, "xTz": 1},
        {"": -1, "t": -1, "tt": -1, "ttt": -1, "xT": -1},
        {"xT": 1, "x": -1},
        {"": 1, "tttt": -1},
    )
    assert evaluated_relative_row(-1, "qxxxQ") == (
        {"q": 1, "qx": 1, "qxx": 1, "tttz": -1},
        {"": -1, "t": -1, "tt": -1},
        {"ttt": -1, "tttt": 1},
        {"": 1, "tttt": -1},
    )
    assert evaluated_relative_row(-1, "qxxxQ") == evaluated_relative_row(-1, "tttt")
    assert evaluated_relative_row(1, "qXXXQ") == evaluated_relative_row(1, "TTTT")
    assert evaluated_relative_row(-1, "qxxxxxxQ") == evaluated_relative_row(-1, "tttttttt")
    assert evaluated_relative_row(1, "zXZ") == evaluated_relative_row(1, "T")


def test_four_state_identities_annihilate_every_evaluated_coordinate():
    for sigma in (1, -1):
        for g in ("", "qZ", "xTqZ", "qzQZ", "qXXXQ", "TTTT", "zXZ", "T"):
            assert four_state_residuals(sigma, g) == ({}, {}, {}, {})


def test_finite_bs34_order_spectrum_is_exact_through_300():
    for n in range(1, 301):
        assert finite_bs34_order_compatible(n) == (gcd(n, 12) == 1)


def test_compatible_finite_orders_have_cyclic_collapse_certificates():
    for n in range(1, 301):
        if finite_bs34_order_compatible(n):
            a, b = finite_cyclic_collapse_certificate(n)
            assert (4 * a) % n == 1 % n
            assert (3 * b) % n == 1 % n


def test_finite_module_replay_derives_the_full_result_57_chain():
    trace = finite_module_replay(7)

    assert all(step.expansion == step.target for step in trace.values())
    assert trace["vt4_implies_vt"].target == {("v", "t"): 1, ("v", ""): -1}
    assert trace["wx_equals_w"].target == {
        ("v", "zx"): 1,
        ("v", "z"): -1,
    }
    assert trace["wyx3_equals_wy"].target == {
        ("v", "zyxxx"): 1,
        ("v", "zy"): -1,
    }
    assert trace["wyx_equals_wy"].target == {
        ("v", "zyx"): 1,
        ("v", "zy"): -1,
    }
    assert trace["three_wy_equals_four_w"].target == {
        ("v", "zy"): 3,
        ("v", "z"): -4,
    }
    assert trace["three_vh_equals_four_v"].target == {
        ("v", "qZ"): 3,
        ("v", ""): -4,
    }


def test_finite_module_replay_uses_integer_and_invertible_right_actions():
    trace = finite_module_replay(7)

    for literal_pair in ("positive_h", "negative_one", "negative_h"):
        zero_step = trace[f"{literal_pair}_v_equals_zero"]
        assert zero_step.target == {("v", ""): 1}
        assert zero_step.expansion == zero_step.target


def test_finite_module_replay_detects_mutated_three_or_four_coefficients():
    mutated_three = finite_module_replay(7, three=2)
    mutated_four = finite_module_replay(7, four=5)

    assert (
        mutated_three["wyx3_equals_wy"].expansion
        != mutated_three["wyx3_equals_wy"].target
    )
    assert (
        mutated_four["three_wy_equals_four_w"].expansion
        != mutated_four["three_wy_equals_four_w"].target
    )


def test_affine_bs34_action_and_comb_partitions_are_exact():
    assert affine_word_action("yxxxY") == affine_word_action("xxxx")
    assert affine_word_action("xxxx") == (Fraction(1), Fraction(4))

    four_z = (Fraction(4), Fraction(0))
    assert progression_right_word(four_z, "xxxx") == four_z

    y_r3 = tuple(
        progression_right_word(four_z, "y" + "x" * power)
        for power in range(3)
    )
    r4 = tuple(
        progression_right_word(four_z, "x" * power)
        for power in range(4)
    )
    assert y_r3 == (
        (Fraction(3), Fraction(0)),
        (Fraction(3), Fraction(1)),
        (Fraction(3), Fraction(2)),
    )
    assert r4 == (
        (Fraction(4), Fraction(0)),
        (Fraction(4), Fraction(1)),
        (Fraction(4), Fraction(2)),
        (Fraction(4), Fraction(3)),
    )
    assert integer_progression_partition(y_r3)
    assert integer_progression_partition(r4)


def test_w_to_v_coordinate_change_is_literal_in_the_universal_quotient():
    forward = {"x": "x", "t": "zxZ", "z": "z", "q": "zy"}

    assert substitute_word("Zq", forward) == "y"
    for power in range(5):
        assert substitute_word("Z" + "t" * power + "z", forward) == "x" * power


def test_relative_free_u_action_is_an_explicit_automorphism():
    w = (1, 0)
    w_r4 = (0, 1)

    for sigma in (1, -1):
        assert relative_free_u_action(sigma, w) == (0, -sigma)
        assert relative_free_u_action(sigma, w_r4) == w
        assert relative_free_u_action(
            sigma,
            relative_free_u_action(sigma, (7, -5)),
        ) == (-7 * sigma, 5 * sigma)


def test_two_comb_vectors_are_nonzero_and_linearly_independent():
    def values_at_zero_and_one(vector):
        w_coefficient, w_r4_coefficient = vector
        return (
            w_coefficient + w_r4_coefficient,
            w_r4_coefficient,
        )

    w_values = values_at_zero_and_one((1, 0))
    w_r4_values = values_at_zero_and_one((0, 1))

    assert w_values == (1, 0)
    assert w_r4_values == (1, 1)
    assert w_values[0] * w_r4_values[1] - w_values[1] * w_r4_values[0] == 1
