from __future__ import annotations

from itertools import product

from experiments.equivalence_classes.lib.words import cyc_reduce, free_reduce, inv
from experiments.stable_ac.rank3_compression.recovery_word_equation import (
    normal_form,
)


R = "xxxTTTT"
P = "xt"
B = "Zxt"
D = "TzxZ"
D_P = "TxtxTX"
POSITIVE_D_SEAM = "xZTz"
NEGATIVE_D_SEAM = "XZtz"


def conjugate(word: str, by: str) -> str:
    return free_reduce(by + word + inv(by))


def t_power(exponent: int) -> str:
    return "t" * exponent if exponent >= 0 else "T" * (-exponent)


def x_power(exponent: int) -> str:
    return "x" * exponent if exponent >= 0 else "X" * (-exponent)


def tail(exponent: int) -> str:
    return free_reduce(t_power(-exponent) + P + x_power(exponent))


def evaluate_d(value: str) -> str:
    return free_reduce("T" + value + "x" + inv(value))


def substitute_z(word: str, value: str) -> str:
    inverse_value = inv(value)
    return free_reduce(
        "".join(
            value if letter == "z" else inverse_value if letter == "Z" else letter
            for letter in word
        )
    )


def normalize_linear_rotation(word: str) -> str:
    word = cyc_reduce(word)
    index = word.index("Z")
    return free_reduce(word[index:] + word[:index])


def seam_step(isolator: str, sign: int) -> str:
    seam = POSITIVE_D_SEAM if sign == 1 else NEGATIVE_D_SEAM
    return normalize_linear_rotation(free_reduce(isolator + seam))


def cyclic_conjugate(left: str, right: str) -> bool:
    left = cyc_reduce(left)
    right = cyc_reduce(right)
    return len(left) == len(right) and right in left + left


def test_all_four_aligned_feedback_histories_have_forced_hnn_tail():
    for first_sign, second_sign in product((1, -1), repeat=2):
        intermediate_source = seam_step(B, first_sign)
        final_isolator = seam_step(intermediate_source, second_sign)
        exponent = first_sign + second_sign

        assert final_isolator == "Z" + tail(exponent)


def test_feedback_survivor_is_the_signed_d_endpoint():
    for first_sign, second_sign in product((1, -1), repeat=2):
        intermediate_source = seam_step(B, first_sign)
        exponent = first_sign + second_sign
        value = tail(exponent)
        survivor = substitute_z(intermediate_source, value)
        d_endpoint = evaluate_d(value)
        expected = inv(d_endpoint) if second_sign == 1 else d_endpoint

        assert cyclic_conjugate(survivor, expected)
        assert d_endpoint == conjugate(D_P, t_power(-exponent))


def test_feedback_sign_table_pins_orientation_weight_and_parameter():
    for first_sign, second_sign in product((1, -1), repeat=2):
        intermediate_exponent = -1
        final_target_exponent = second_sign * intermediate_exponent
        final_orientation = second_sign
        intermediate_weight = 7 + first_sign
        final_target_weight = 1 + second_sign * intermediate_weight
        normalized_tail_weight = final_orientation * final_target_weight

        assert final_orientation * final_target_exponent == -1
        assert normalized_tail_weight == 7 + first_sign + second_sign


def test_actual_r_gauged_tail_has_the_same_feedback_endpoint_class():
    for exponent in (-2, 0, 2):
        quotient_tail = tail(exponent)
        actual_tail = free_reduce(quotient_tail + conjugate(R, "tX"))

        assert normal_form(actual_tail) == normal_form(quotient_tail)
        assert normal_form(evaluate_d(actual_tail)) == normal_form(
            evaluate_d(quotient_tail)
        )


def test_opposite_alternating_order_cannot_eliminate_second_target():
    for first_sign, second_sign in product((1, -1), repeat=2):
        first_target_exponent = first_sign * -1
        second_target_exponent = -1 + second_sign * first_target_exponent

        assert abs(second_target_exponent) in (0, 2)
        assert abs(second_target_exponent) != 1
