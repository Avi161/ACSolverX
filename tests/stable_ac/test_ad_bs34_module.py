from math import gcd

from experiments.stable_ac.verify_ad_bs34_module import (
    A,
    D,
    evaluated_ad_rows,
    evaluated_relative_row,
    finite_bs34_order_compatible,
    finite_cyclic_collapse_certificate,
    four_state_residuals,
    free_reduce,
    inverse_word,
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
