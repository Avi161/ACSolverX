from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.stable_ac.thickenable.neuwirth_dart_audit import (  # noqa: E402
    audit_trace,
)
from experiments.stable_ac.thickenable.neuwirth_permutation_certificate import (  # noqa: E402
    enumerate_trace,
)


SOURCE = ("ZYx", "ZxyX", "ZZZyyyy")
ACTUAL_RENAMED = ("TZx", "TxzX", "TTTzzzz")
WRONG_SIGNED_INPUT = ("TZX", "TxzX", "TTTzzzz")
ALLEGED_POSITIVES = (
    ("TTX", "TZX", "TTTzzzz"),
    ("TZX", "ZZX", "TTTzzzz"),
)

EXPECTED_ACTUAL_HISTOGRAM = {4: 184, 6: 2244, 8: 3332}
EXPECTED_ACTUAL_TRACE = (
    "bf3dc3e105d3c5ab8b54ee5ab8a6ffea7c1386b849009b859f92b58371586172"
)
EXPECTED_WRONG_HISTOGRAM = {2: 4, 4: 506, 6: 3022, 8: 2228}
EXPECTED_WRONG_TRACE = (
    "f19ed35d59b4bad10a339f61ec7f3256bb6fa0a040b6c0a3edde78b9a3268a51"
)
EXPECTED_POSITIVE_TRACES = (
    "e189c4f6c5153f9b349ec6569eb8692c58155f9644a489b188bbcfe959987520",
    "f53c5bbd9a0442d6a422825cb66e8dfd3781651dff56baee6a455b040f86e550",
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


def cyclic_reduce(word: str) -> str:
    word = free_reduce(word)
    while len(word) > 1 and word[0] == word[-1].swapcase():
        word = free_reduce(word[1:-1])
    return word


def rotations(word: str) -> tuple[str, ...]:
    return tuple(word[index:] + word[:index] for index in range(len(word)))


def canonical_word(word: str) -> str:
    word = cyclic_reduce(word)
    return min(rotations(word) + rotations(inverse(word)))


def canonical_state(words: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(sorted(map(canonical_word, words), key=lambda word: (len(word), word)))


def rename_source() -> tuple[str, ...]:
    images = {"x": "x", "y": "z", "z": "t"}
    renamed = []
    for word in SOURCE:
        renamed.append(
            "".join(
                images[letter]
                if letter.islower()
                else images[letter.lower()].upper()
                for letter in word
            )
        )
    return tuple(renamed)


def definition_21_children(words: tuple[str, ...]) -> set[tuple[str, ...]]:
    """Enumerate every signed cyclic concatenation, then canonicalize.

    Rotating or inverting an input row and canonicalizing the result expands
    into primitive relator conjugations/inversions.  This is the full one-move
    convention used by the bridge memo, implemented independently here.
    """

    children: set[tuple[str, ...]] = set()
    for target in range(len(words)):
        for source in range(len(words)):
            if target == source:
                continue
            for sign in (1, -1):
                source_word = words[source] if sign == 1 else inverse(words[source])
                for left in rotations(words[target]):
                    for right in rotations(source_word):
                        product = cyclic_reduce(left + right)
                        if not product:
                            continue
                        child = list(words)
                        child[target] = product
                        children.add(canonical_state(tuple(child)))
    return children


def check_census(
    words: tuple[str, ...],
    expected_cases: int,
    expected_histogram: dict[int, int],
    expected_accepting: int,
    expected_trace: str,
) -> None:
    direct = enumerate_trace(words)
    dart = audit_trace(words)
    assert direct.enumerated_cases == expected_cases
    assert dart.enumerated_cases == expected_cases
    assert direct.defect_histogram == expected_histogram
    assert dart.defect_histogram == expected_histogram
    assert len(direct.accepting_orders) == expected_accepting
    assert len(dart.accepting_orders) == expected_accepting
    assert direct.trace_sha256 == expected_trace
    assert dart.trace_sha256 == expected_trace
    assert direct.link_components == dart.link_components == {1}

    if expected_accepting:
        for _, trace_item in direct.accepting_orders:
            link_components, faces, defect, boundary_bc, boundary_cb = trace_item
            assert (link_components, faces, defect) == (1, 9, 0)
            assert (boundary_bc, boundary_cb) == (1, 1)


def main() -> None:
    assert rename_source() == ACTUAL_RENAMED
    assert ACTUAL_RENAMED != WRONG_SIGNED_INPUT
    assert canonical_word(ACTUAL_RENAMED[0]) != canonical_word(WRONG_SIGNED_INPUT[0])

    actual_children = definition_21_children(ACTUAL_RENAMED)
    wrong_children = definition_21_children(WRONG_SIGNED_INPUT)
    alleged_keys = tuple(map(canonical_state, ALLEGED_POSITIVES))
    assert all(key not in actual_children for key in alleged_keys)
    assert all(key in wrong_children for key in alleged_keys)
    assert len(actual_children) == 172
    length_histogram = Counter(sum(map(len, child)) for child in actual_children)
    assert length_histogram == Counter(
        {15: 11, 16: 11, 17: 33, 18: 47, 19: 14, 21: 56}
    )
    assert min(length_histogram) == 15

    check_census(
        WRONG_SIGNED_INPUT,
        5760,
        EXPECTED_WRONG_HISTOGRAM,
        0,
        EXPECTED_WRONG_TRACE,
    )
    check_census(
        ACTUAL_RENAMED,
        5760,
        EXPECTED_ACTUAL_HISTOGRAM,
        0,
        EXPECTED_ACTUAL_TRACE,
    )
    for words, cases, trace in zip(
        ALLEGED_POSITIVES,
        (2880, 4320),
        EXPECTED_POSITIVE_TRACES,
    ):
        check_census(words, cases, {0: 2, 2: 70, 4: 800, 6: 1684, 8: 324} if cases == 2880 else {0: 2, 2: 94, 4: 1100, 6: 2576, 8: 548}, 2, trace)

    print("PASS: the alleged positives are children only of the wrong-signed input")
    print("actual rename:", " | ".join(ACTUAL_RENAMED))
    print("actual one-move shell: 172 states, minimum total length 15")
    print("actual P* Neuwirth minimum genus: 2")
    print("wrong-signed P* Neuwirth minimum genus: 1")
    print("quarantined wrong-input positives: 2 spherical orders each")


if __name__ == "__main__":
    main()
