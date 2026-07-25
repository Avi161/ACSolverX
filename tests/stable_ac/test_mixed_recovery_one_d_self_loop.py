from experiments.equivalence_classes.lib.words import cyc_reduce, free_reduce, inv
from experiments.stable_ac.rank3_compression.recovery_word_equation import (
    recoveries_up_to,
)


D = "TzxZ"


def rotations(word: str) -> tuple[str, ...]:
    return tuple(word[index:] + word[:index] for index in range(len(word)))


def cyclic_key(word: str) -> str:
    word = cyc_reduce(word)
    return min(rotations(word) + rotations(inv(word)))


def signed_rotation_isolators(recovery: str) -> set[str]:
    w = free_reduce("x" + recovery)
    target = "Z" + w
    outputs = set()
    for source in (D, inv(D)):
        for target_rotation in rotations(target):
            for source_rotation in rotations(source):
                product = cyc_reduce(target_rotation + source_rotation)
                if sum(letter in "zZ" for letter in product) == 1:
                    outputs.add(cyclic_key(product))
    return outputs


def survivor(expression: str) -> str:
    return free_reduce("T" + expression + "x" + inv(expression))


def test_cancellation_heavy_recoveries_have_only_the_two_forced_seams():
    for recovery in (
        "t",
        "TTTxxx",
        "XXXtxxx",
        "XttttXXt",
        "TXXXttxxx",
    ):
        w = free_reduce("x" + recovery)
        assert signed_rotation_isolators(recovery) == {
            cyclic_key("ZT" + w + "x"),
            cyclic_key("Zt" + w + "X"),
        }


def test_both_catalyst_survivors_are_exact_conjugates_of_direct_recovery():
    recoveries = recoveries_up_to(9)
    assert len(recoveries) == 61

    for recovery in recoveries:
        w = free_reduce("x" + recovery)
        direct = free_reduce("T" + w + "x" + inv(w))

        positive_expression = free_reduce("T" + w + "x")
        negative_expression = free_reduce("t" + w + "X")

        assert survivor(positive_expression) == free_reduce(
            "T" + direct + "t"
        )
        assert survivor(negative_expression) == free_reduce(
            "t" + direct + "T"
        )
