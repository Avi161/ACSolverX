"""Exact Fernández internal-collapse certificate for ``aca_115``."""

from __future__ import annotations

import hashlib
import json

from .morse_internal_collapse import Cell, Edge, replay


SOURCE = ("YXYxyx", "YYYYxxx")
STABILIZED_SOURCE = ("YXYxyx", "YYYYxxx", "z")
ENDPOINT = ("YzxxYzX", "YzYzY", "YzxYzzxYzxYzx")
MATCHING: tuple[Edge, ...] = (
    (2, "c2_x1_1"),
    ("c1_x1_2", "c1_x2_2"),
    ("c1_0_3", "c1_y3_2"),
    ("c1_0_1", "c1_y3_1"),
    ("x1", "x3"),
    (1, "c1_0_2"),
    ("y2", "c1_y2_2"),
    ("c2_0_3", "c2_y2_2"),
    ("y3", "c2_y3_1"),
    ("c2_0_2", "c2_y2_1"),
    ("c2_0_1", "c2_x3_3"),
    ("c2_y1_4", "c2_y2_4"),
    ("c2_y1_3", "c2_y3_3"),
    ("c2_y1_2", "c2_y3_2"),
    ("x2", "c1_x2_1"),
    ("y1", "c1_y1_2"),
    ("c1_y1_3", "c1_y2_3"),
    ("c2_0_7", "c2_x2_3"),
    ("c1_x1_1", "c1_x3_1"),
    ("c2_x1_2", "c2_x3_2"),
    ("c1_0_6", "c1_x2_3"),
    ("c1_y1_1", "c1_y2_1"),
    ("c2_0_4", "c2_y2_3"),
    ("c1_x1_3", "c1_x3_3"),
    ("c2_0_6", "c2_x3_1"),
    ("c1_0_5", "c1_x3_2"),
    ("c2_0_5", "c2_x2_1"),
)
EXPECTED_CRITICAL = (
    (0,),
    ("c1_0_4", "c2_x1_3", "c2_y1_1"),
    ("c1_y3_3", "c2_x2_2", "c2_y3_4"),
)

# Whitehead descent on the three-generator endpoint.  Images are applied
# simultaneously to every relator.
WHITEHEAD_IMAGES = (
    {"x": "Zxz", "y": "yz", "z": "z"},
    {"x": "xy", "y": "y", "z": "Yz"},
)
WHITEHEAD_STATES = (
    ENDPOINT,
    ("YxxYX", "ZYYY", "YxYzxYxYx"),
    ("YxyxYX", "ZYY", "xYzxxx"),
)
TOPOLOGICAL_ORDER_SHA256 = (
    "69723365e792e6c2b5ad8e4d1184617e0620d32b7a2f89f958659954dceea3d5"
)


def _typed(cell: Cell) -> str:
    return f"i:{cell}" if isinstance(cell, int) else f"s:{cell}"


def topological_order_digest(order: tuple[Cell, ...]) -> str:
    encoded = json.dumps(
        [_typed(cell) for cell in order], separators=(",", ":")
    ).encode("ascii") + b"\n"
    return hashlib.sha256(encoded).hexdigest()


def _inverse(word: str) -> str:
    return word[::-1].swapcase()


def _cyclic_reduce(word: str) -> str:
    stack: list[str] = []
    for letter in word:
        if stack and stack[-1] == letter.swapcase():
            stack.pop()
        else:
            stack.append(letter)
    while len(stack) > 1 and stack[0] == stack[-1].swapcase():
        stack = stack[1:-1]
    return "".join(stack)


def apply_hom(word: str, images: dict[str, str]) -> str:
    output = []
    for letter in word:
        image = images[letter.lower()]
        output.append(image if letter.islower() else _inverse(image))
    return _cyclic_reduce("".join(output))


def whitehead_cut_minimum_delta(words: tuple[str, ...]) -> int:
    encode = {"x": 1, "X": -1, "y": 2, "Y": -2, "z": 3, "Z": -3}
    relators = [tuple(encode[letter] for letter in word) for word in words]
    letters = (1, 2, 3, -1, -2, -3)
    edges = []
    for word in relators:
        edges.extend((left, -right) for left, right in zip(word, word[1:] + word[:1]))
    minimum = 0
    for multiplier in letters:
        rest = [letter for letter in letters if abs(letter) != abs(multiplier)]
        for mask in range(1 << len(rest)):
            subset = {multiplier}
            subset.update(
                letter for index, letter in enumerate(rest) if mask & (1 << index)
            )
            cut = sum((left in subset) != (right in subset) for left, right in edges)
            degree = sum(
                (left == multiplier) + (right == multiplier)
                for left, right in edges
            )
            minimum = min(minimum, cut - degree)
    return minimum


def exponent_determinant(words: tuple[str, str, str]) -> int:
    matrix = [
        [word.count(generator) - word.count(generator.upper())
         for generator in "xyz"]
        for word in words
    ]
    a, b, c = matrix
    return (
        a[0] * (b[1] * c[2] - b[2] * c[1])
        - a[1] * (b[0] * c[2] - b[2] * c[0])
        + a[2] * (b[0] * c[1] - b[1] * c[0])
    )


def build_certificate() -> dict[str, object]:
    result = replay(SOURCE, MATCHING)
    return {
        "schema": "fernandez-morse-supermove-v1",
        "source_id": "aca_115",
        "source_provenance": (
            ".claude/worktrees/codex-proofs/data/ms_unsolved_reps/aca_124.csv"
        ),
        "trusted_triviality_provenance": (
            "results/stable_ac/theory/aca124_triviality_provenance.json"
        ),
        "source": list(SOURCE),
        "comparison_stabilization": list(STABILIZED_SOURCE),
        "cell_count": 61,
        "cover_count": 138,
        "matching": [list(edge) for edge in MATCHING],
        "matching_pair_count": len(MATCHING),
        "critical_cells": [list(level) for level in result.critical_cells],
        "topological_order": list(result.topological_order),
        "topological_order_sha256": topological_order_digest(
            result.topological_order
        ),
        "critical_generator_names": list(result.critical_generators),
        "critical_relator_names": list(result.critical_relators),
        "endpoint": list(result.endpoint_words),
        "endpoint_exponent_determinant": exponent_determinant(ENDPOINT),
        "whitehead_path": [
            {"images": images, "output": list(output)}
            for images, output in zip(WHITEHEAD_IMAGES, WHITEHEAD_STATES[1:])
        ],
        "stabilized_source_whitehead_floor": 14,
        "endpoint_whitehead_floor": 15,
        "whitehead_minimum_delta_source": whitehead_cut_minimum_delta(
            STABILIZED_SOURCE
        ),
        "whitehead_minimum_delta_endpoint_reduced": whitehead_cut_minimum_delta(
            WHITEHEAD_STATES[-1]
        ),
        "limitations": {
            "raw_total_length_improves": False,
            "primitive_relator_indices_zero_based": [1, 2],
            "primitive_deletions_return_to_source_aut_orbit": True,
            "claim": "mechanism and raw-orbit escape witness, not a solve",
        },
        "bound": {
            "fernandez_q_double_star": "O(n+m)+O(k)+O(k^2)",
            "atomic_sac": (
                "witness-dependent; use explicit normal-closure witnesses, "
                "or the fixed-machine Busy-Beaver existence ceiling"
            ),
        },
    }


def verify_certificate() -> bool:
    certificate = build_certificate()
    if certificate["critical_cells"] != [list(level) for level in EXPECTED_CRITICAL]:
        raise AssertionError("critical-cell replay mismatch")
    if certificate["endpoint"] != list(ENDPOINT):
        raise AssertionError("Morse endpoint replay mismatch")
    if certificate["topological_order_sha256"] != TOPOLOGICAL_ORDER_SHA256:
        raise AssertionError("reversed-Hasse topological order mismatch")
    current = ENDPOINT
    for images, expected in zip(WHITEHEAD_IMAGES, WHITEHEAD_STATES[1:]):
        current = tuple(apply_hom(word, images) for word in current)
        if current != expected:
            raise AssertionError("Whitehead path replay mismatch")
    if sum(map(len, STABILIZED_SOURCE)) != 14:
        raise AssertionError("unexpected stabilized-source length")
    if sum(map(len, current)) != 15:
        raise AssertionError("unexpected endpoint Whitehead length")
    if whitehead_cut_minimum_delta(STABILIZED_SOURCE) != 0:
        raise AssertionError("stabilized source is not Whitehead-minimal")
    if whitehead_cut_minimum_delta(current) != 0:
        raise AssertionError("endpoint reduction is not Whitehead-minimal")
    if exponent_determinant(ENDPOINT) != 1:
        raise AssertionError("endpoint exponent determinant is not +1")
    return True
