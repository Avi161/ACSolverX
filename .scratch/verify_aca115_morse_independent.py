"""Independent replay of the aca_115 Morse certificate.

This deliberately uses the earlier pure-Python reference port in
``.scratch/morse_search_port.py`` rather than the production constructor.
"""

from __future__ import annotations

import json
import runpy
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.stable_ac.supermoves.morse_aca115_certificate import (
    ENDPOINT,
    EXPECTED_CRITICAL,
    MATCHING,
    SOURCE,
    STABILIZED_SOURCE,
    WHITEHEAD_IMAGES,
    WHITEHEAD_STATES,
)


def inverse(word: str) -> str:
    return word[::-1].swapcase()


def cyclic_reduce(word: str) -> str:
    stack: list[str] = []
    for letter in word:
        if stack and stack[-1] == letter.swapcase():
            stack.pop()
        else:
            stack.append(letter)
    while len(stack) > 1 and stack[0] == stack[-1].swapcase():
        stack = stack[1:-1]
    return "".join(stack)


def independent_apply_hom(word: str, images: dict[str, str]) -> str:
    pieces = []
    for letter in word:
        image = images[letter.lower()]
        pieces.append(image if letter.islower() else inverse(image))
    return cyclic_reduce("".join(pieces))


def independent_cut_minimum_delta(words: tuple[str, ...]) -> int:
    code = {"x": 1, "X": -1, "y": 2, "Y": -2, "z": 3, "Z": -3}
    relators = [tuple(code[letter] for letter in word) for word in words]
    letters = (1, -1, 2, -2, 3, -3)
    graph_edges = []
    for word in relators:
        graph_edges.extend(
            (word[index], -word[(index + 1) % len(word)])
            for index in range(len(word))
        )
    best = 0
    for multiplier in letters:
        optional = [letter for letter in letters if abs(letter) != abs(multiplier)]
        for mask in range(1 << len(optional)):
            side = {multiplier}
            for index, letter in enumerate(optional):
                if mask & (1 << index):
                    side.add(letter)
            crossing = sum((left in side) ^ (right in side)
                           for left, right in graph_edges)
            multiplier_degree = sum(
                int(left == multiplier) + int(right == multiplier)
                for left, right in graph_edges
            )
            best = min(best, crossing - multiplier_degree)
    return best


def verify_inverse(images: dict[str, str], inverse_images: dict[str, str]) -> None:
    for generator in "xyz":
        forward_then_back = independent_apply_hom(images[generator], inverse_images)
        back_then_forward = independent_apply_hom(
            inverse_images[generator], images
        )
        if forward_then_back != generator or back_then_forward != generator:
            raise AssertionError("displayed Whitehead map is not an automorphism")


reference = types.SimpleNamespace(**runpy.run_path(".scratch/morse_search_port.py"))
poset = reference.presentation_poset(("x", "y"), SOURCE)
if not reference.verify_matching(poset, MATCHING):
    raise AssertionError("independent matching verification failed")
critical = reference.critical_cells(poset, MATCHING)
if critical != EXPECTED_CRITICAL:
    raise AssertionError("independent critical-cell replay mismatch")
endpoint = reference.morse_endpoint(("x", "y"), SOURCE, MATCHING)
encoded = reference.encoded_rank_two(endpoint)
if encoded is not None:
    raise AssertionError("the independent endpoint unexpectedly has rank two")
generators, relators = endpoint
names = {generator: "xyz"[index] for index, generator in enumerate(generators)}
words = tuple(
    "".join(names[cell] if sign == 1 else names[cell].upper()
            for cell, sign in relator)
    for relator in relators
)
if words != ENDPOINT:
    raise AssertionError("independent endpoint-word replay mismatch")

current = ENDPOINT
inverse_images = (
    {"x": "zxZ", "y": "yZ", "z": "z"},
    {"x": "xY", "y": "y", "z": "yz"},
)
for images, inverse_map, expected in zip(
    WHITEHEAD_IMAGES, inverse_images, WHITEHEAD_STATES[1:]
):
    verify_inverse(images, inverse_map)
    current = tuple(independent_apply_hom(word, images) for word in current)
    if current != expected:
        raise AssertionError("independent Whitehead path mismatch")
if independent_cut_minimum_delta(STABILIZED_SOURCE) != 0:
    raise AssertionError("source stabilization is not Whitehead-minimal")
if independent_cut_minimum_delta(current) != 0:
    raise AssertionError("Morse endpoint reduction is not Whitehead-minimal")

print(json.dumps({
    "verified": True,
    "cells": len(poset.cells),
    "covers": len(poset.covers),
    "matching_pairs": len(MATCHING),
    "critical_counts": [len(level) for level in critical],
    "endpoint": words,
    "stabilized_source_floor": sum(map(len, STABILIZED_SOURCE)),
    "endpoint_floor": sum(map(len, current)),
}, sort_keys=True))
