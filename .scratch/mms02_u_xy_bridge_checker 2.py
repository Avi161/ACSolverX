from __future__ import annotations

import argparse
import runpy
from dataclasses import dataclass
from itertools import permutations


CORRECTED_THREE = ("yZXzYXyZxz", "YxyZxzYXyZxZXz")
MISPRINTED_THREE = ("xzYXyxZXYxyZ", "XyxZXYXyxzXYxy")

CORRECTED_U_XY = ("Xy", "YxYXy")
MISPRINTED_U_XY = ("xyxYXXY", "XyxYXXYXyxxyXYxy")

CORRECTED_MOVES = ((2, -1, 1, 0),)
MISPRINTED_MOVES = (
    (2, 1, 5, 1),
    (2, -1, 1, 1),
    (2, 1, 4, 0),
    (2, 1, 1, 0),
    (2, -1, 1, 0),
)

MISPRINTED_RANK_THREE = MISPRINTED_THREE + ("zYX",)
RANK_THREE_MOVES = (
    (2, 1, -1, 3, 0),
    (2, 0, -1, 0, 0),
    (2, 0, -1, 1, 0),
    (2, 1, -1, 0, 0),
    (1, 0, 1, 2, 1),
    (0, 1, -1, 1, 2),
    (2, 0, -1, 2, 0),
    (2, 0, 1, 1, 0),
    (2, 0, -1, 0, 0),
    (2, 0, 1, 0, 0),
    (2, 1, 1, 0, 0),
)

CORRECTED_CANONICAL_STATES = (
    ("Y", "Yx"),
    ("Y", "X"),
)
MISPRINTED_CANONICAL_STATES = (
    ("YXyxxyX", "YXyxYXXYxyxxyXYx"),
    ("YXyxxyX", "YXyxxyXYx"),
    ("Yx", "YXyxxyX"),
    ("Yx", "YXXyx"),
    ("Y", "Yx"),
    ("Y", "X"),
)
RANK_THREE_CANONICAL_STATES = (
    ("Zxy", "ZXzYXyxzXYxy", "ZXYXyxzXYxyXyx"),
    ("Zxy", "ZXZxzXyx", "ZXzYXyxzXYxy"),
    ("Zxy", "ZXZxzXyx", "ZXYxyZxyx"),
    ("Zxy", "ZXYxyx", "ZXZxzXyx"),
    ("Zxy", "ZXzYxx", "ZXYxyx"),
    ("Zxy", "Zxx", "ZXYxyx"),
    ("Yx", "Zxx", "ZXYxyx"),
    ("Yx", "Zxx", "ZXyx"),
    ("Zx", "Yx", "Zxx"),
    ("X", "Zx", "Yx"),
    ("Y", "X", "Zx"),
    ("Z", "Y", "X"),
)


def inverse(word: str) -> str:
    return word[::-1].swapcase()


def free_reduce(word: str) -> str:
    stack: list[str] = []
    for letter in word:
        if stack and stack[-1] == letter.swapcase():
            stack.pop()
        else:
            stack.append(letter)
    return "".join(stack)


def rotate_right(word: str, amount: int) -> str:
    if not word:
        return word
    amount %= len(word)
    return word[-amount:] + word[:-amount] if amount else word


def substitute(word: str, generator: str, image: str) -> str:
    return free_reduce(
        "".join(
            image
            if letter == generator
            else inverse(image)
            if letter == generator.upper()
            else letter
            for letter in word
        )
    )


def cyclic_reduce(word: str) -> str:
    word = free_reduce(word)
    while len(word) >= 2 and word[0] == word[-1].swapcase():
        word = free_reduce(word[1:-1])
    return word


def letter_number(letter: str) -> int:
    return "xyzabcdefghijklmnopqrstuvw".index(letter.lower()) + 1


def booth_key(word: str) -> tuple[tuple[int, bool], ...]:
    return tuple((-letter_number(letter), letter.islower()) for letter in word)


def canonical_relator(word: str) -> str:
    word = cyclic_reduce(word)
    if not word:
        return ""
    candidates = [
        rotate_right(oriented, amount)
        for oriented in (word, inverse(word))
        for amount in range(len(word))
    ]
    return min(candidates, key=booth_key)


def state_sort_key(word: str) -> tuple[int, tuple[tuple[int, bool], ...]]:
    return len(word), booth_key(word)


def canonical_state(words: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(sorted(map(canonical_relator, words), key=state_sort_key))


@dataclass(frozen=True)
class PrimitiveStep:
    kind: str
    target: int
    operand: int | str | None
    before: tuple[str, ...]
    after: tuple[str, ...]


def record(
    current: list[str], kind: str, target: int, operand: int | str | None
) -> PrimitiveStep:
    before = tuple(current)
    if kind == "AC1":
        assert isinstance(operand, int) and operand != target
        current[target] = free_reduce(current[target] + current[operand])
    elif kind == "AC2":
        assert operand is None
        current[target] = inverse(current[target])
    elif kind == "AC3":
        assert isinstance(operand, str)
        current[target] = free_reduce(operand + current[target] + inverse(operand))
    else:
        raise AssertionError(kind)
    return PrimitiveStep(kind, target, operand, before, tuple(current))


def rotate_with_ac3(
    current: list[str], target: int, amount: int, steps: list[PrimitiveStep]
) -> None:
    word = current[target]
    if not word or amount % len(word) == 0:
        return
    amount %= len(word)
    conjugator = word[-amount:]
    expected = rotate_right(word, amount)
    steps.append(record(current, "AC3", target, conjugator))
    assert current[target] == expected


def cyclic_reduce_with_ac3(
    current: list[str], target: int, steps: list[PrimitiveStep]
) -> None:
    current[target] = free_reduce(current[target])
    while (
        len(current[target]) >= 2
        and current[target][0] == current[target][-1].swapcase()
    ):
        conjugator = current[target][0].swapcase()
        steps.append(record(current, "AC3", target, conjugator))


def canonicalize_row(
    current: list[str], target: int, steps: list[PrimitiveStep]
) -> None:
    cyclic_reduce_with_ac3(current, target, steps)
    desired = canonical_relator(current[target])
    if not current[target]:
        assert desired == ""
        return
    for invert_first in (False, True):
        oriented = inverse(current[target]) if invert_first else current[target]
        for amount in range(len(oriented)):
            if rotate_right(oriented, amount) != desired:
                continue
            if invert_first:
                steps.append(record(current, "AC2", target, None))
            rotate_with_ac3(current, target, amount, steps)
            assert current[target] == desired
            return
    raise AssertionError((current[target], desired))


def swap_rows(
    current: list[str], left: int, right: int, steps: list[PrimitiveStep]
) -> None:
    assert left != right
    original = tuple(current)
    steps.append(record(current, "AC1", left, right))
    steps.append(record(current, "AC2", left, None))
    steps.append(record(current, "AC1", right, left))
    steps.append(record(current, "AC2", right, None))
    steps.append(record(current, "AC1", left, right))
    steps.append(record(current, "AC2", left, None))
    expected = list(original)
    expected[left], expected[right] = expected[right], expected[left]
    assert current == expected


def normalize_with_primitive_ac(
    words: tuple[str, ...],
) -> tuple[tuple[str, ...], list[PrimitiveStep]]:
    current = list(words)
    steps: list[PrimitiveStep] = []
    for target in range(len(current)):
        canonicalize_row(current, target, steps)
    desired = sorted(current, key=state_sort_key)
    for position, word in enumerate(desired):
        if current[position] == word:
            continue
        source = next(
            index
            for index in range(position + 1, len(current))
            if current[index] == word
        )
        swap_rows(current, position, source, steps)
    assert tuple(current) == canonical_state(words)
    return tuple(current), steps


def apply_move_with_primitive_ac(
    words: tuple[str, ...], move: tuple[int, ...]
) -> tuple[tuple[str, ...], list[PrimitiveStep]]:
    if len(move) == 4:
        target_one, sign, target_rotation, source_rotation = move
        target = target_one - 1
        source = 1 - target
    else:
        target, source, sign, target_rotation, source_rotation = move
    assert target != source and sign in (-1, 1)
    current = list(words)
    steps: list[PrimitiveStep] = []
    rotate_with_ac3(current, target, target_rotation, steps)
    if sign == -1:
        steps.append(record(current, "AC2", source, None))
    rotate_with_ac3(current, source, source_rotation, steps)
    steps.append(record(current, "AC1", target, source))
    if source_rotation % len(current[source]):
        rotate_with_ac3(
            current,
            source,
            len(current[source]) - source_rotation % len(current[source]),
            steps,
        )
    if sign == -1:
        steps.append(record(current, "AC2", source, None))
    normalized, normalization = normalize_with_primitive_ac(tuple(current))
    steps.extend(normalization)
    return normalized, steps


def expand_path(
    raw: tuple[str, ...], moves: tuple[tuple[int, ...], ...]
) -> tuple[tuple[tuple[str, ...], ...], tuple[PrimitiveStep, ...]]:
    current, prefix = normalize_with_primitive_ac(raw)
    states = [current]
    steps = list(prefix)
    for move in moves:
        current, expansion = apply_move_with_primitive_ac(current, move)
        states.append(current)
        steps.extend(expansion)
    return tuple(states), tuple(steps)


def replay_step(current: tuple[str, ...], step: PrimitiveStep) -> tuple[str, ...]:
    assert current == step.before
    words = list(current)
    if step.kind == "AC1":
        assert isinstance(step.operand, int)
        words[step.target] = free_reduce(words[step.target] + words[step.operand])
    elif step.kind == "AC2":
        words[step.target] = inverse(words[step.target])
    elif step.kind == "AC3":
        assert isinstance(step.operand, str)
        words[step.target] = free_reduce(
            step.operand + words[step.target] + inverse(step.operand)
        )
    else:
        raise AssertionError(step.kind)
    assert tuple(words) == step.after
    return tuple(words)


def verify_transcript(raw: tuple[str, ...], steps: tuple[PrimitiveStep, ...]) -> None:
    current = raw
    for step in steps:
        current = replay_step(current, step)


Permutation = tuple[int, ...]


def compose(left: Permutation, right: Permutation) -> Permutation:
    return tuple(left[right[index]] for index in range(len(left)))


def permutation_inverse(permutation: Permutation) -> Permutation:
    result = [0] * len(permutation)
    for index, image in enumerate(permutation):
        result[image] = index
    return tuple(result)


def evaluate(word: str, images: dict[str, Permutation]) -> Permutation:
    result = tuple(range(len(next(iter(images.values())))))
    for letter in word:
        image = images[letter.lower()]
        result = compose(
            result, image if letter.islower() else permutation_inverse(image)
        )
    return result


def generated_subgroup(generators: tuple[Permutation, ...]) -> set[Permutation]:
    identity = tuple(range(len(generators[0])))
    subgroup = {identity}
    frontier = [identity]
    steps = generators + tuple(permutation_inverse(g) for g in generators)
    while frontier:
        current = frontier.pop()
        for step in steps:
            child = compose(current, step)
            if child not in subgroup:
                subgroup.add(child)
                frontier.append(child)
    return subgroup


def parity(permutation: Permutation) -> int:
    return sum(
        permutation[left] > permutation[right]
        for left in range(len(permutation))
        for right in range(left + 1, len(permutation))
    ) % 2


def conjugacy_class(element: Permutation, group: set[Permutation]) -> set[Permutation]:
    return {
        compose(compose(conjugator, element), permutation_inverse(conjugator))
        for conjugator in group
    }


def verify_a5_fixed_base_obstruction() -> tuple[Permutation, Permutation]:
    images = {
        "x": (0, 1, 3, 4, 2),
        "y": (0, 2, 3, 1, 4),
        "z": (2, 0, 1, 3, 4),
    }
    identity = tuple(range(5))
    assert all(evaluate(relator, images) == identity for relator in MISPRINTED_THREE)
    image_group = generated_subgroup(tuple(images.values()))
    alternating_group = {
        permutation for permutation in permutations(range(5)) if parity(permutation) == 0
    }
    assert image_group == alternating_group and len(image_group) == 60
    published = evaluate("Xyz", images)
    u_xy = evaluate("zYX", images)
    assert u_xy not in conjugacy_class(published, image_group)
    assert u_xy not in conjugacy_class(permutation_inverse(published), image_group)
    return u_xy, published


def operand_label(step: PrimitiveStep) -> str:
    if step.kind == "AC1":
        assert isinstance(step.operand, int)
        return f"r{step.operand + 1}"
    if step.kind == "AC3":
        return f"conj({step.operand})"
    return ""


def print_transcript(label: str, steps: tuple[PrimitiveStep, ...]) -> None:
    print(f"[{label}] {len(steps)} primitive moves")
    for index, step in enumerate(steps, start=1):
        before = " | ".join(step.before)
        after = " | ".join(step.after)
        print(
            f"{index:03d} {step.kind} r{step.target + 1} "
            f"{operand_label(step)} :: {before} -> {after}"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    corridor = runpy.run_path(".scratch/mms02_wirtinger_repair_checker.py")
    descendant = corridor["three_generator_descendant"]
    rename = corridor["rename_xyz"]
    corrected_three = tuple(rename(word) for word in descendant(corrected=True)[0])
    misprinted_three = tuple(rename(word) for word in descendant(corrected=False)[0])
    assert corrected_three == CORRECTED_THREE
    assert misprinted_three == MISPRINTED_THREE

    corrected_u_xy = tuple(substitute(word, "z", "xy") for word in corrected_three)
    misprinted_u_xy = tuple(substitute(word, "z", "xy") for word in misprinted_three)
    assert corrected_u_xy == CORRECTED_U_XY
    assert misprinted_u_xy == MISPRINTED_U_XY

    corrected_states, corrected_steps = expand_path(CORRECTED_U_XY, CORRECTED_MOVES)
    misprinted_states, misprinted_steps = expand_path(MISPRINTED_U_XY, MISPRINTED_MOVES)
    rank_three_states, rank_three_steps = expand_path(
        MISPRINTED_RANK_THREE, RANK_THREE_MOVES
    )
    assert corrected_states == CORRECTED_CANONICAL_STATES
    assert misprinted_states == MISPRINTED_CANONICAL_STATES
    assert rank_three_states == RANK_THREE_CANONICAL_STATES
    verify_transcript(CORRECTED_U_XY, corrected_steps)
    verify_transcript(MISPRINTED_U_XY, misprinted_steps)
    verify_transcript(MISPRINTED_RANK_THREE, rank_three_steps)
    assert corrected_steps[-1].after == ("Y", "X")
    assert misprinted_steps[-1].after == ("Y", "X")
    assert rank_three_steps[-1].after == ("Z", "Y", "X")

    u_xy_image, published_image = verify_a5_fixed_base_obstruction()

    print("PASS: exact MMS02 U=xy descendants")
    print("corrected", CORRECTED_U_XY)
    print("misprinted", MISPRINTED_U_XY)
    print(
        "PASS: corrected U=xy -> basis:",
        len(CORRECTED_MOVES),
        "macro /",
        len(corrected_steps),
        "primitive AC1-AC3",
    )
    print(
        "PASS: misprinted U=xy -> basis:",
        len(MISPRINTED_MOVES),
        "macros /",
        len(misprinted_steps),
        "primitive AC1-AC3",
    )
    print(
        "PASS: (A,B,zYX) -> rank-3 basis:",
        len(RANK_THREE_MOVES),
        "macros /",
        len(rank_three_steps),
        "primitive AC1-AC3",
    )
    print("PASS: A5 fixed-base obstruction")
    print("zYX", u_xy_image)
    print("Xyz", published_image)
    if args.verbose:
        print_transcript("corrected U=xy", corrected_steps)
        print_transcript("misprinted U=xy", misprinted_steps)
        print_transcript("rank-three zYX", rank_three_steps)


if __name__ == "__main__":
    main()
