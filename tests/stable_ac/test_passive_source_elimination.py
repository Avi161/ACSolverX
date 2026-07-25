from __future__ import annotations

from experiments.equivalence_classes.lib.words import free_reduce, inv
from experiments.stable_ac.rank3_compression.recovery_word_equation import (
    normal_form,
)


R = "xxxTTTT"
P = "xt"
B = "Zxt"
D = "TzxZ"
BRAID = "xtxTXT"
IDENTITY = (0, ())


def conjugate(word: str, by: str) -> str:
    return free_reduce(by + word + inv(by))


def substitute_z(word: str, value: str) -> str:
    inverse_value = inv(value)
    return free_reduce(
        "".join(
            value if letter == "z" else inverse_value if letter == "Z" else letter
            for letter in word
        )
    )


def z_exponent(word: str) -> int:
    return word.count("z") - word.count("Z")


def test_passive_source_factors_vanish_after_source_elimination():
    e = free_reduce(P + R)
    final_isolator = free_reduce("Z" + e)
    source_1 = free_reduce(B + conjugate(R, "zX"))
    source_2 = conjugate(
        free_reduce(B + conjugate(inv(R), "tZ")),
        "xzt",
    )
    target = free_reduce(D + conjugate(R, "Zx"))
    target = free_reduce(target + conjugate(source_1, "ztX"))
    target = free_reduce(conjugate(inv(source_2), "xZt") + target)
    target = free_reduce(target + conjugate(R, "zzT"))

    assert substitute_z(final_isolator, e) == ""
    assert normal_form(substitute_z(source_1, e)) == IDENTITY
    assert normal_form(substitute_z(source_2, e)) == IDENTITY
    assert normal_form(substitute_z(target, e)) == normal_form(
        substitute_z(D, P)
    )


def test_target_conjugation_and_inversion_are_only_ac1_ac3_changes():
    e = free_reduce(P + R)
    source = free_reduce(B + conjugate(R, "zXt"))
    target = free_reduce(D + conjugate(source, "tZZx"))
    outer = "tzX"
    final_target = conjugate(inv(target), outer)
    evaluated_outer = substitute_z(outer, e)
    expected = conjugate(
        inv(substitute_z(D, P)),
        evaluated_outer,
    )

    assert normal_form(substitute_z(final_target, e)) == normal_form(expected)


def test_baseline_survivor_is_the_ak3_braid_relator():
    endpoint = substitute_z(D, P)

    assert endpoint == "TxtxTX"
    assert endpoint == conjugate(BRAID, "T")


def test_passive_d_source_cannot_become_a_one_z_isolator():
    d_shadow_variants = (
        D,
        inv(D),
        conjugate(D, "xzT"),
        free_reduce(D + conjugate(R, "zX")),
        conjugate(
            free_reduce(inv(D) + conjugate(inv(R), "Tzz")),
            "xtZ",
        ),
    )

    assert all(z_exponent(word) == 0 for word in d_shadow_variants)
    assert z_exponent("Z" + P) == -1
    assert z_exponent("z" + P) == 1
