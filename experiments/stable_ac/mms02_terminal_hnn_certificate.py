"""Exact HNN normalization of the terminal MMS02 fixed-row pair gate."""

from __future__ import annotations

from dataclasses import dataclass


ORIGINAL_WORDS = {
    "A": "xzYXyxZXYxyZ",
    "B": "XyxZXYXyxzXYxy",
    "u": "zYX",
    "v": "Xyz",
}
AUTOMORPHISMS = (
    {"x": "x", "y": "y", "z": "zy"},
    {"x": "x", "y": "xyX", "z": "z"},
    {"x": "x", "y": "Zy", "z": "z"},
)
TRANSFORMED_WORDS = {
    "A": "xyxYzXZY",
    "B": "ZyxYzXZYzXZyzxZyXYzxZyX",
    "u": "zX",
    "v": "ZyXzxZyX",
}
W = "YxyxY"
C = "yXYxy"
D0 = "XyXYXyxYxy"


@dataclass(frozen=True)
class TerminalHNNDecision:
    transformed_words: tuple[tuple[str, str], ...]
    hnn_relator: str
    w: str
    c: str
    d0: str
    normalized_source: tuple[str, str]
    normalized_target: tuple[str, str]
    source_tail_minimum: tuple[str, str]
    target_tail_minimum: tuple[str, str]
    source_floor: int
    target_floor: int
    source_descent: tuple[tuple[str, str], ...]
    target_descent: tuple[tuple[str, str], ...]
    whitehead_map_count: int
    verdict: str


def inverse(word: str) -> str:
    return word[::-1].swapcase()


def free_reduce(word: str) -> str:
    reduced: list[str] = []
    for letter in word:
        if reduced and reduced[-1] == letter.swapcase():
            reduced.pop()
        else:
            reduced.append(letter)
    return "".join(reduced)


def apply_images(word: str, images: dict[str, str]) -> str:
    return free_reduce(
        "".join(
            images[letter]
            if letter.islower()
            else inverse(images[letter.lower()])
            for letter in word
        )
    )


def canonical_cyclic_word(word: str) -> str:
    word = free_reduce(word)
    while len(word) > 1 and word[0] == word[-1].swapcase():
        word = free_reduce(word[1:-1])
    return min(
        oriented[index:] + oriented[:index]
        for oriented in (word, inverse(word))
        for index in range(len(oriented))
    )


def canonical_cyclic_pair(pair: tuple[str, str]) -> tuple[str, str]:
    return tuple(sorted(canonical_cyclic_word(word) for word in pair))


def rank_two_whitehead_automorphisms() -> tuple[dict[str, str], ...]:
    signed = ("x", "X", "y", "Y")
    unique: dict[tuple[str, str], dict[str, str]] = {}
    for multiplier in signed:
        others = tuple(
            letter
            for letter in signed
            if letter not in (multiplier, multiplier.swapcase())
        )
        for mask in range(1 << len(others)):
            subset = {multiplier}
            subset.update(
                letter
                for index, letter in enumerate(others)
                if mask & (1 << index)
            )
            images = {}
            for generator in ("x", "y"):
                positive = generator in subset
                negative = generator.upper() in subset
                if generator in (multiplier, multiplier.swapcase()):
                    images[generator] = generator
                elif positive and not negative:
                    images[generator] = generator + multiplier
                elif negative and not positive:
                    images[generator] = multiplier.swapcase() + generator
                elif positive and negative:
                    images[generator] = (
                        multiplier.swapcase() + generator + multiplier
                    )
                else:
                    images[generator] = generator
            key = tuple(images[generator] for generator in ("x", "y"))
            if key != ("x", "y"):
                unique[key] = images
    return tuple(unique[key] for key in sorted(unique))


def whitehead_minimum(
    pair: tuple[str, str],
) -> tuple[tuple[str, str], tuple[tuple[str, str], ...]]:
    automorphisms = rank_two_whitehead_automorphisms()
    current = canonical_cyclic_pair(pair)
    path = []
    while True:
        candidates = []
        for images in automorphisms:
            image = canonical_cyclic_pair(
                tuple(apply_images(word, images) for word in current)
            )
            if sum(map(len, image)) < sum(map(len, current)):
                candidates.append(
                    (
                        sum(map(len, image)),
                        image,
                        tuple(images[generator] for generator in ("x", "y")),
                    )
                )
        if not candidates:
            return current, tuple(path)
        _, current, step = min(candidates)
        path.append(step)


def transformed_words() -> dict[str, str]:
    result = {}
    for name, word in ORIGINAL_WORDS.items():
        for automorphism in AUTOMORPHISMS:
            word = apply_images(word, automorphism)
        result[name] = word
    if result != TRANSFORMED_WORDS:
        raise AssertionError("the terminal HNN automorphism replay drifted")
    return result


def decide_terminal_hnn_shortcut() -> TerminalHNNDecision:
    transformed = transformed_words()
    hnn_relator = "zxZ" + inverse(W)
    if canonical_cyclic_word(transformed["A"]) != canonical_cyclic_word(
        hnn_relator
    ):
        raise AssertionError("the transformed A row is not the HNN relator")

    raw_b = transformed["B"]
    b_skeleton = (
        "Z" + "yxY" + "zXZ" + "Y" + "zXZ" + "y"
        + "zxZ" + "yXY" + "zxZ" + "yX"
    )
    if raw_b != b_skeleton:
        raise AssertionError("the transformed B pinch decomposition drifted")
    d0 = free_reduce(
        "yxY" + inverse(W) + "Y" + inverse(W) + "y"
        + W + "yXY" + W + "yX"
    )
    if d0 != D0:
        raise AssertionError("the four B-row pinches do not reduce to d0")

    raw_v = transformed["v"]
    if raw_v != "Z" + "yX" + "zxZ" + "yX":
        raise AssertionError("the transformed v pinch decomposition drifted")
    c = free_reduce("yX" + W + "yX")
    if c != C:
        raise AssertionError("the transformed v row does not reduce to c")

    normalized_source = ("Zx", "Z" + D0)
    normalized_target = ("Z" + C, "Z" + D0)
    if free_reduce("X" + inverse(transformed["u"]) + "x") != "Zx":
        raise AssertionError("the source inversion/conjugation normalization failed")

    source_minimum, source_path = whitehead_minimum(("x", D0))
    target_minimum, target_path = whitehead_minimum((C, D0))
    source_floor = sum(map(len, source_minimum))
    target_floor = sum(map(len, target_minimum))
    if (source_floor, target_floor) != (10, 14):
        raise AssertionError("the corrected base-tail Whitehead floors drifted")
    return TerminalHNNDecision(
        transformed_words=tuple(sorted(transformed.items())),
        hnn_relator=hnn_relator,
        w=W,
        c=C,
        d0=D0,
        normalized_source=normalized_source,
        normalized_target=normalized_target,
        source_tail_minimum=source_minimum,
        target_tail_minimum=target_minimum,
        source_floor=source_floor,
        target_floor=target_floor,
        source_descent=source_path,
        target_descent=target_path,
        whitehead_map_count=len(rank_two_whitehead_automorphisms()),
        verdict="NO_SIMULTANEOUS_BASE_TAIL_AUTOMORPHISM",
    )
