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


def reverse_target_isolators(recovery: str) -> set[str]:
    w = free_reduce("x" + recovery)
    source = "Z" + w
    outputs = set()
    for target in (D, inv(D)):
        for oriented_source in (source, inv(source)):
            for target_rotation in rotations(target):
                for source_rotation in rotations(oriented_source):
                    product = cyc_reduce(target_rotation + source_rotation)
                    if sum(letter in "zZ" for letter in product) == 1:
                        outputs.add(cyclic_key(product))
    return outputs


def survivor(expression: str, recovery_word: str) -> str:
    return free_reduce(inv(expression) + recovery_word)


def test_reverse_order_has_only_the_two_forced_isolator_classes():
    for recovery in (
        "t",
        "TTTxxx",
        "XXXtxxx",
        "XttttXXt",
        "TXXXttxxx",
    ):
        w = free_reduce("x" + recovery)
        assert reverse_target_isolators(recovery) == {
            cyclic_key("ZT" + w + "x"),
            cyclic_key("Zt" + w + "X"),
        }


def test_reverse_target_survivors_are_conjugates_of_direct_recovery():
    recoveries = recoveries_up_to(9)
    assert len(recoveries) == 61

    for recovery in recoveries:
        w = free_reduce("x" + recovery)
        direct = free_reduce("T" + w + "x" + inv(w))

        positive_expression = free_reduce("T" + w + "x")
        negative_expression = free_reduce("t" + w + "X")
        positive_survivor = survivor(positive_expression, w)
        negative_survivor = survivor(negative_expression, w)

        assert positive_survivor == free_reduce(
            inv(w) + inv(direct) + w
        )
        assert negative_survivor == free_reduce(
            inv("T" + w) + direct + "T" + w
        )
        assert cyclic_key(positive_survivor) == cyclic_key(inv(direct))
        assert cyclic_key(negative_survivor) == cyclic_key(direct)
