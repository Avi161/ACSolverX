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


def normalize_linear_rotation(word: str) -> str:
    word = cyc_reduce(word)
    index = word.index("Z")
    return free_reduce(word[index:] + word[:index])


def seam_step(isolator: str, sign: int) -> str:
    seam = POSITIVE_D_SEAM if sign == 1 else NEGATIVE_D_SEAM
    return normalize_linear_rotation(free_reduce(isolator + seam))


def z_exponent(word: str) -> int:
    return word.count("z") - word.count("Z")


def test_d_source_seams_realize_the_entire_integer_tail_recurrence():
    for exponent in range(-8, 9):
        isolator = "Z" + tail(exponent)

        assert seam_step(isolator, 1) == "Z" + tail(exponent + 1)
        assert seam_step(isolator, -1) == "Z" + tail(exponent - 1)


def test_all_signed_two_d_histories_have_the_weight_forced_tail():
    for first_sign, second_sign in product((1, -1), repeat=2):
        target = seam_step(B, first_sign)
        target = seam_step(target, second_sign)
        exponent = first_sign + second_sign

        assert target == "Z" + tail(exponent)
        assert evaluate_d(tail(exponent)) == conjugate(
            D_P,
            t_power(-exponent),
        )


def test_actual_tail_r_gauges_do_not_change_the_endpoint_class():
    for exponent in (-5, -2, 0, 3, 6):
        quotient_tail = tail(exponent)
        actual_tail = free_reduce(quotient_tail + conjugate(R, "xtX"))

        assert normal_form(actual_tail) == normal_form(quotient_tail)
        assert normal_form(evaluate_d(actual_tail)) == normal_form(
            evaluate_d(quotient_tail)
        )


def test_b_source_quotient_makes_the_survivor_the_braid_endpoint():
    for sign, outer in ((1, "xT"), (-1, "tXX")):
        target_class = conjugate(D_P if sign == 1 else inv(D_P), outer)
        isolator_tail = free_reduce(P + target_class)
        survivor = free_reduce(inv(isolator_tail) + P)

        assert survivor == inv(target_class)
        assert survivor == conjugate(
            inv(D_P) if sign == 1 else D_P,
            outer,
        )


def test_two_b_source_factors_cannot_make_a_one_z_target():
    for first_sign, second_sign in product((1, -1), repeat=2):
        exponent = (
            z_exponent(D)
            + first_sign * z_exponent(B)
            + second_sign * z_exponent(B)
        )

        assert exponent % 2 == 0
        assert abs(exponent) != 1
        assert abs(-exponent) != 1
