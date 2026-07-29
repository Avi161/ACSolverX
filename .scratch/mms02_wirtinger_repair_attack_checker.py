from __future__ import annotations

import runpy
import sys
from dataclasses import dataclass
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from experiments.equivalence_classes.lib.words import (  # noqa: E402
    canon_pair,
    canon_rel,
    free_reduce,
    inv,
    rot,
)


CORRECTED_THREE = ("yZXzYXyZxz", "YxyZxzYXyZxZXz")
MISPRINTED_THREE = ("xzYXyxZXYxyZ", "XyxZXYXyxzXYxy")
W_IMAGE = "Yx"  # w = Xyz, hence z = y^-1 x.
CORRECTED_TWO = ("yXyXYxYXyXyxYx", "YxyXyxYxYXyXyyXYx")
MISPRINTED_RAW_TWO = ("xYxYXyyXYxyXy", "XyyXYXyxYYxy")
PUBLISHED_P = ("XYxYXyxYYxyXy", "YXyyXYxyxYYx")
AK3 = ("xxxYYYY", "xyxYXY")

CORRECTED_MOVES = (
    (2, 1, 0, 11),
    (2, -1, 0, 0),
    (2, 1, 1, 2),
    (2, -1, 0, 0),
    (2, -1, 1, 0),
    (2, -1, 1, 0),
)

MISPRINTED_TO_AK3 = tuple(
    map(
        int,
        (
            "9 7 4 8 11 5 11 9 3 10 12 7 7 9 11 5 3 5 4 3 12 5 7 7 1 "
            "9 11 8 3 5 10 2 6 12 9 7 5 11 10 3 8 11 9 2 10 12 5 7 9 11 "
            "1 9 8"
        ).split(),
    )
)


@dataclass(frozen=True)
class PrimitiveStep:
    kind: str
    target: int
    operand: str | None
    before: tuple[str, str]
    after: tuple[str, str]


def substitute(word: str, generator: str, image: str) -> str:
    return free_reduce(
        "".join(
            image
            if letter == generator
            else inv(image)
            if letter == generator.upper()
            else letter
            for letter in word
        )
    )


def _record(
    pair: list[str], kind: str, target: int, operand: str | None
) -> PrimitiveStep:
    before = tuple(pair)
    if kind == "AC1":
        pair[target] = free_reduce(pair[target] + pair[1 - target])
    elif kind == "AC2":
        pair[target] = inv(pair[target])
    elif kind == "AC3":
        assert operand is not None
        pair[target] = free_reduce(operand + pair[target] + inv(operand))
    else:
        raise AssertionError(kind)
    return PrimitiveStep(kind, target + 1, operand, before, tuple(pair))


def _rotate_with_ac3(
    pair: list[str], target: int, amount: int, steps: list[PrimitiveStep]
) -> None:
    word = pair[target]
    if not word or amount % len(word) == 0:
        return
    amount %= len(word)
    conjugator = word[-amount:]
    steps.append(_record(pair, "AC3", target, conjugator))
    assert pair[target] == rot(word, amount)


def _cyclic_reduce_with_ac3(
    pair: list[str], target: int, steps: list[PrimitiveStep]
) -> None:
    pair[target] = free_reduce(pair[target])
    while len(pair[target]) >= 2 and pair[target][0] == pair[target][-1].swapcase():
        conjugator = pair[target][0].swapcase()
        steps.append(_record(pair, "AC3", target, conjugator))


def _to_canonical_relator(
    pair: list[str], target: int, steps: list[PrimitiveStep]
) -> None:
    _cyclic_reduce_with_ac3(pair, target, steps)
    desired = canon_rel(pair[target])
    for invert_first in (False, True):
        oriented = inv(pair[target]) if invert_first else pair[target]
        for amount in range(len(oriented)):
            if rot(oriented, amount) != desired:
                continue
            if invert_first:
                steps.append(_record(pair, "AC2", target, None))
            _rotate_with_ac3(pair, target, amount, steps)
            assert pair[target] == desired
            return
    raise AssertionError((pair[target], desired))


def _swap_with_ac1_ac2(pair: list[str], steps: list[PrimitiveStep]) -> None:
    original = tuple(pair)
    steps.append(_record(pair, "AC1", 0, None))
    steps.append(_record(pair, "AC2", 0, None))
    steps.append(_record(pair, "AC1", 1, None))
    steps.append(_record(pair, "AC2", 1, None))
    steps.append(_record(pair, "AC1", 0, None))
    steps.append(_record(pair, "AC2", 0, None))
    assert tuple(pair) == (original[1], original[0])


def normalize_with_primitive_ac(pair: tuple[str, str]) -> tuple[tuple[str, str], list[PrimitiveStep]]:
    current = list(pair)
    steps: list[PrimitiveStep] = []
    _to_canonical_relator(current, 0, steps)
    _to_canonical_relator(current, 1, steps)
    desired = canon_pair(*pair)
    if tuple(current) != desired:
        _swap_with_ac1_ac2(current, steps)
    assert tuple(current) == desired
    return tuple(current), steps


def apply_definition_21_with_primitive_ac(
    pair: tuple[str, str], move: tuple[int, int, int, int]
) -> tuple[tuple[str, str], list[PrimitiveStep]]:
    target_one, sign, target_rotation, source_rotation = move
    target = target_one - 1
    source = 1 - target
    current = list(pair)
    steps: list[PrimitiveStep] = []
    _rotate_with_ac3(current, target, target_rotation, steps)
    if sign == -1:
        steps.append(_record(current, "AC2", source, None))
    _rotate_with_ac3(current, source, source_rotation, steps)
    steps.append(_record(current, "AC1", target, None))
    if source_rotation:
        _rotate_with_ac3(
            current,
            source,
            len(current[source]) - source_rotation,
            steps,
        )
    if sign == -1:
        steps.append(_record(current, "AC2", source, None))
    normalized, normalization = normalize_with_primitive_ac(tuple(current))
    steps.extend(normalization)
    return normalized, steps


def apply_h(pair: tuple[str, str], move: int) -> tuple[str, str]:
    first, second = pair
    if move == 1:
        second = second + first
    elif move == 2:
        first = first + inv(second)
    elif move == 3:
        second = second + inv(first)
    elif move == 4:
        first = first + second
    elif move == 5:
        second = "X" + second + "x"
    elif move == 6:
        first = "Y" + first + "y"
    elif move == 7:
        second = "Y" + second + "y"
    elif move == 8:
        first = "x" + first + "X"
    elif move == 9:
        second = "x" + second + "X"
    elif move == 10:
        first = "y" + first + "Y"
    elif move == 11:
        second = "y" + second + "Y"
    elif move == 12:
        first = "X" + first + "x"
    else:
        raise AssertionError(move)
    return free_reduce(first), free_reduce(second)


def main() -> None:
    corridor = runpy.run_path(".scratch/mms02_wirtinger_repair_checker.py")
    rename = corridor["rename_xyz"]
    descendant = corridor["three_generator_descendant"]
    corrected_three = tuple(rename(word) for word in descendant(corrected=True)[0])
    misprinted_three = tuple(rename(word) for word in descendant(corrected=False)[0])
    assert corrected_three == CORRECTED_THREE
    assert misprinted_three == MISPRINTED_THREE
    assert tuple(substitute(word, "z", W_IMAGE) for word in corrected_three) == CORRECTED_TWO
    assert tuple(substitute(word, "z", W_IMAGE) for word in misprinted_three) == MISPRINTED_RAW_TWO

    corrected_state, prefix = normalize_with_primitive_ac(CORRECTED_TWO)
    corrected_primitive_steps = list(prefix)
    corrected_states = [corrected_state]
    for move in CORRECTED_MOVES:
        corrected_state, primitive = apply_definition_21_with_primitive_ac(
            corrected_state, move
        )
        corrected_primitive_steps.extend(primitive)
        corrected_states.append(corrected_state)
    assert corrected_state == ("Y", "X")
    assert all(step.kind in {"AC1", "AC2", "AC3"} for step in corrected_primitive_steps)

    misprinted_state = MISPRINTED_RAW_TWO
    # Raw replay descendant -> the exact MMS/Shehper spelling P.
    misprinted_state = (inv(misprinted_state[0]), misprinted_state[1])
    misprinted_state = (rot(misprinted_state[0], 1), misprinted_state[1])
    misprinted_state = (misprinted_state[0], inv(misprinted_state[1]))
    assert misprinted_state == PUBLISHED_P
    for move in MISPRINTED_TO_AK3:
        misprinted_state = apply_h(misprinted_state, move)
    assert misprinted_state == AK3

    print("corridor descendants: exact")
    print(
        "corrected descendant -> trivial:",
        len(CORRECTED_MOVES),
        "Definition-2.1 moves expanded to",
        len(corrected_primitive_steps),
        "primitive AC1-AC3 moves",
    )
    for index, state in enumerate(corrected_states):
        print(" corrected", index, "|".join(state))
    print("misprinted descendant -> AK(3):", len(MISPRINTED_TO_AK3), "paper h_i moves")
    print("all exact AC replays: OK")


if __name__ == "__main__":
    main()
