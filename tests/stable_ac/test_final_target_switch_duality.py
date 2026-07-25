from __future__ import annotations

from itertools import product

from experiments.equivalence_classes.lib.words import cyc_reduce, free_reduce, inv


ISOLATOR = "Zxt"
TAIL = "xt"


def rotations(word: str) -> tuple[str, ...]:
    word = cyc_reduce(word)
    return tuple(word[index:] + word[:index] for index in range(len(word)))


def cyclic_key(word: str) -> str:
    word = cyc_reduce(word)
    return min(rotations(word) + rotations(inv(word)))


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


def test_switching_the_final_target_preserves_the_target_cyclic_class():
    samples = (
        ("TzxZ", "Zxt", ""),
        ("xZTzt", "zzTXZ", "xtZ"),
        ("ZtxzXT", "tzXZZ", "zTXt"),
    )

    for (target, source, bridge), sign, side in product(
        samples,
        (1, -1),
        ("left", "right"),
    ):
        oriented_source = source if sign == 1 else inv(source)
        source_factor = conjugate(oriented_source, bridge)
        canonical = free_reduce(target + source_factor)
        original = (
            free_reduce(source_factor + target)
            if side == "left"
            else canonical
        )
        switched = free_reduce(
            oriented_source + inv(bridge) + target + bridge
        )

        switching_conjugator = free_reduce(target + bridge)
        assert conjugate(canonical, inv(switching_conjugator)) == switched
        assert cyclic_key(original) == cyclic_key(switched)


def test_one_z_target_switch_makes_the_survivors_signed_conjugates():
    targets = ("TzxZ", "xZtzX", "ZTxxzT")
    bridges = ("", "xtZ", "zTXt")

    for target, bridge, sign, side in product(
        targets,
        bridges,
        (1, -1),
        ("left", "right"),
    ):
        signed_source = free_reduce(
            inv(bridge) + inv(target) + ISOLATOR + bridge
        )
        source = signed_source if sign == 1 else inv(signed_source)
        source_factor = conjugate(source if sign == 1 else inv(source), bridge)
        original = (
            free_reduce(source_factor + target)
            if side == "left"
            else free_reduce(target + source_factor)
        )
        switched = free_reduce(
            (source if sign == 1 else inv(source))
            + inv(bridge)
            + target
            + bridge
        )

        assert cyclic_key(original) == cyclic_key(ISOLATOR)
        assert cyclic_key(switched) == cyclic_key(ISOLATOR)

        evaluated_target = substitute_z(target, TAIL)
        evaluated_source = substitute_z(source, TAIL)
        evaluated_bridge = substitute_z(bridge, TAIL)
        expected_target = conjugate(
            inv(evaluated_source) if sign == 1 else evaluated_source,
            evaluated_bridge,
        )

        assert evaluated_target == expected_target
