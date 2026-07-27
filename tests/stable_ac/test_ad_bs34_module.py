from experiments.stable_ac.verify_ad_bs34_module import (
    A,
    D,
    evaluated_ad_rows,
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


def test_four_state_identities_annihilate_every_evaluated_coordinate():
    for sigma in (1, -1):
        for g in ("", "qZ", "xTqZ", "qzQZ"):
            assert four_state_residuals(sigma, g) == ({}, {}, {}, {})
