from experiments.equivalence_classes.lib.autcanon import is_automorphism
from experiments.equivalence_classes.lib.words import (
    apply_hom,
    cyc_reduce,
    free_reduce,
    inv,
)
from experiments.stable_ac.rank3_compression.recovery_word_equation import (
    equals_t,
)


def direct_endpoint(recovery: str) -> tuple[str, str]:
    e = free_reduce("x" + recovery)
    return (
        free_reduce("xxx" + e + "XXXX" + inv(e)),
        free_reduce("T" + e + "x" + inv(e)),
    )


def conjugate(word: str, by: str) -> str:
    return free_reduce(by + word + inv(by))


def rewritten_endpoint(recovery: str) -> tuple[str, str]:
    e = free_reduce("x" + recovery)
    y = conjugate("x", e)
    return (
        free_reduce("xxx" + inv(y) * 4),
        free_reduce("T" + y),
    )


def test_endpoint_has_the_exact_conjugate_power_rewriting():
    for recovery in (
        "t",
        "xxxTTT",
        "TTTxxx",
        "xxxtXXX",
        "XXXtxxx",
        "TTTxxxTTTTxxx",
    ):
        assert equals_t(recovery)
        assert direct_endpoint(recovery) == rewritten_endpoint(recovery)


def test_literal_recovery_has_an_explicit_length_fourteen_witness():
    endpoint = tuple(
        word.translate(str.maketrans("tT", "yY"))
        for word in direct_endpoint("t")
    )
    witness = {"x": "Y", "y": "yx"}

    assert endpoint == ("xxxxyXXXXYX", "YxyxYX")
    assert is_automorphism(witness)
    assert tuple(
        cyc_reduce(apply_hom(word, witness))
        for word in endpoint
    ) == ("YYYxyyyyX", "XYxYX")
    assert sum(
        len(cyc_reduce(apply_hom(word, witness)))
        for word in endpoint
    ) == 14


def test_mod_four_bridge_obstruction_has_only_the_length_one_sign_match():
    solutions = {
        (distance, delta, epsilon)
        for distance in (1, 2)
        for delta in (-1, 1)
        for epsilon in (-1, 1)
        if (delta * distance * epsilon - 1) % 4 == 0
    }
    assert solutions == {
        (1, -1, -1),
        (1, 1, 1),
    }
