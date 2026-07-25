from experiments.equivalence_classes.lib.words import free_reduce, inv
from experiments.stable_ac.rank3_compression.recovery_word_equation import (
    normal_form,
    recoveries_up_to,
)


R = "xxxTTTT"
B = "xtxTXT"


def recovery_words(recovery: str) -> tuple[str, str, str]:
    e = free_reduce("x" + recovery)
    y = free_reduce(e + "x" + inv(e))
    s = free_reduce("T" + y)
    a = free_reduce("xxx" + inv(y) * 4)
    return y, s, a


def conjugate(word: str, by: str) -> str:
    return free_reduce(by + word + inv(by))


def test_restored_to_unrestored_difference_is_four_explicit_conjugates():
    for recovery in recoveries_up_to(9):
        _, s, a = recovery_words(recovery)
        four_conjugates = free_reduce(
            "".join(conjugate(s, "t" * power) for power in range(1, 5))
        )
        assert free_reduce(inv(a) + R) == four_conjugates


def test_all_short_recoveries_return_to_literal_modulo_retained_relator():
    _, literal_s, _ = recovery_words("t")
    recoveries = recoveries_up_to(9)

    assert len(recoveries) == 61
    for recovery in recoveries:
        _, s, _ = recovery_words(recovery)
        assert normal_form(free_reduce(inv(s) + literal_s)) == (0, ())


def test_literal_unrestored_endpoint_is_exactly_ak3_up_to_conjugation():
    _, literal_s, _ = recovery_words("t")
    assert literal_s == "TxtxTX"
    assert free_reduce("T" + B + "t") == literal_s
