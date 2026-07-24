from collections import Counter

from experiments.equivalence_classes.lib.autcanon import aut_min_len
from experiments.equivalence_classes.lib.words import free_reduce, inv
from experiments.stable_ac.rank3_compression.recovery_word_equation import (
    equals_t,
    normal_form,
    recoveries_up_to,
)


A = "xxxzXXXXZ"
D = "TzxZ"


def recovery_endpoint(recovery: str) -> tuple[str, str]:
    z_expression = free_reduce("x" + recovery)

    def substitute(word: str) -> str:
        return free_reduce(
            "".join(
                z_expression
                if letter == "z"
                else inv(z_expression)
                if letter == "Z"
                else letter
                for letter in word
            )
        ).translate(str.maketrans("tT", "yY"))

    return substitute(A), substitute(D)


def test_torus_knot_normal_form_recognizes_the_defining_relation():
    assert normal_form("xxxTTTT") == (0, ())
    assert normal_form("ttttXXX") == (0, ())
    assert normal_form("xX") == (0, ())
    assert normal_form("tT") == (0, ())

    for recovery in (
        "t",
        "xxxTTT",
        "TxxxTT",
        "TTxxxT",
        "TTTxxx",
        "xxxtXXX",
    ):
        assert equals_t(recovery)

    for non_recovery in ("", "x", "T", "xxx", "tttt"):
        assert not equals_t(non_recovery)


def test_shortest_nontrivial_recoveries_are_complete():
    recoveries = recoveries_up_to(6)
    assert recoveries == (
        "t",
        "xxxTTT",
        "TxxxTT",
        "TTxxxT",
        "TTTxxx",
    )


def test_exact_recovery_census_through_length_sixteen():
    recoveries = recoveries_up_to(16)
    assert len(recoveries) == 17_155
    assert Counter(map(len, recoveries)) == {
        1: 1,
        6: 4,
        7: 2,
        8: 16,
        9: 38,
        10: 68,
        11: 114,
        12: 308,
        13: 788,
        14: 1_748,
        15: 4_040,
        16: 10_028,
    }

    scored = sorted(
        (aut_min_len(recovery_endpoint(word)), len(word), word)
        for word in recoveries
    )
    assert [entry for entry in scored if entry[0] <= 23] == [
        (14, 1, "t"),
        (15, 7, "XXXtxxx"),
        (17, 7, "xxxtXXX"),
        (18, 13, "XXXXXXtxxxxxx"),
        (20, 13, "xxxxxxtXXXXXX"),
        (23, 6, "TTTxxx"),
    ]
    assert {
        length: min(
            floor
            for floor, word_length, _ in scored
            if word_length == length
        )
        for length in sorted(set(map(len, recoveries)))
    } == {
        1: 14,
        6: 23,
        7: 15,
        8: 29,
        9: 33,
        10: 25,
        11: 30,
        12: 24,
        13: 18,
        14: 29,
        15: 29,
        16: 36,
    }
