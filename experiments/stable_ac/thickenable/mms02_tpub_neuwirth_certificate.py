"""Exact Neuwirth decision for the published MMS02 triple Tpub."""

from __future__ import annotations

import itertools
import math
from collections import Counter
from dataclasses import dataclass

from experiments.stable_ac.thickenable import neuwirth_rank_solver as base
from experiments.stable_ac.thickenable import (
    neuwirth_rank3_rigid_solver as rigid,
)


ORIGINAL_WORDS = (
    "xzYXyxZXYxyZ",
    "XyxZXYXyxzXYxy",
    "Xyz",
)
LETTER_RENAMING = {
    "x": "x",
    "X": "X",
    "y": "z",
    "Y": "Z",
    "z": "t",
    "Z": "T",
}
INTERNAL_WORDS = (
    "xtZXzxTXZxzT",
    "XzxTXZXzxtXZxz",
    "Xzt",
)


@dataclass(frozen=True)
class TpubNeuwirthDecision:
    original_words: tuple[str, ...]
    internal_words: tuple[str, ...]
    occurrence_count: int
    simple_edges: frozenset[base.ClassKey]
    parallel_multiplicities: tuple[tuple[base.ClassKey, int], ...]
    degrees: tuple[int, ...]
    macro_rotation_budget: int
    macro_rotations: tuple[tuple[tuple[int, ...], ...], ...]
    disconnecting_support_pairs: tuple[base.ClassKey, ...]
    verdict: str
    witness: rigid.RigidRankWitness | None
    counters: rigid.RigidSearchCounters


def relabel_words(words: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(
        "".join(LETTER_RENAMING[letter] for letter in word)
        for word in words
    )


def _connected_after_deleting(
    simple_edges: frozenset[base.ClassKey],
    deleted: base.ClassKey,
) -> bool:
    remaining = set(rigid.GERMS) - set(deleted)
    if len(remaining) < 2:
        return True
    adjacency = {vertex: set() for vertex in remaining}
    for left, right in simple_edges:
        if left in remaining and right in remaining:
            adjacency[left].add(right)
            adjacency[right].add(left)
    start = min(remaining)
    reached = {start}
    stack = [start]
    while stack:
        vertex = stack.pop()
        for neighbor in adjacency[vertex] - reached:
            reached.add(neighbor)
            stack.append(neighbor)
    return reached == remaining


def _face_count(
    rotation: tuple[tuple[int, ...], ...],
    simple_edges: frozenset[base.ClassKey],
) -> int:
    directed = {
        dart
        for edge in simple_edges
        for dart in (edge, tuple(reversed(edge)))
    }
    seen: set[tuple[int, int]] = set()
    faces = 0
    for start in sorted(directed):
        if start in seen:
            continue
        faces += 1
        dart = start
        while dart not in seen:
            seen.add(dart)
            left, right = dart
            order = rotation[right]
            dart = (right, order[(order.index(left) + 1) % len(order)])
    if seen != directed:
        raise AssertionError("macro face trace missed a directed edge")
    return faces


def enumerate_macro_rotations(
    simple_edges: frozenset[base.ClassKey],
) -> tuple[int, tuple[tuple[tuple[int, ...], ...], ...]]:
    adjacency = {vertex: set() for vertex in rigid.GERMS}
    for left, right in simple_edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    local_orders = []
    for vertex in rigid.GERMS:
        head, *tail = sorted(adjacency[vertex])
        local_orders.append(
            tuple((head, *order) for order in itertools.permutations(tail))
        )
    budget = math.prod(map(len, local_orders))
    spherical = tuple(
        rotation
        for rotation in itertools.product(*local_orders)
        if len(rigid.GERMS)
        - len(simple_edges)
        + _face_count(rotation, simple_edges)
        == 2
    )
    return budget, tuple(sorted(spherical))


def _scheme(
    data: base.LinkData,
    rotation: tuple[tuple[int, ...], ...],
    index: int,
) -> base.Scheme:
    slots = base._empty_slots(data)
    for vertex in rigid.GERMS:
        start = 0
        for neighbor in rotation[vertex]:
            key = tuple(sorted((vertex, neighbor)))
            base._set_class_block(
                data,
                slots,
                key,
                vertex,
                start,
                reverse=vertex != key[0],
            )
            start += len(data.class_edges[key])
    if not rigid._verify_slot_partition(data, slots):
        raise AssertionError("Tpub scheme produced invalid slot maps")
    return base.Scheme(
        name=f"Tpub-macro-{index}",
        support_kind="Tpub-exact-support",
        cut=None,
        slots=tuple(map(tuple, slots)),
        slot_partition_verified=True,
    )


def decide_tpub_neuwirth() -> TpubNeuwirthDecision:
    if relabel_words(ORIGINAL_WORDS) != INTERNAL_WORDS:
        raise AssertionError("Tpub generator renaming drifted")
    data = rigid._build_link_data(INTERNAL_WORDS)
    simple_edges = frozenset(data.class_edges)
    if any(left == right for left, right in simple_edges):
        raise AssertionError("Tpub A-link unexpectedly contains a loop")
    if not rigid._is_connected(simple_edges):
        raise AssertionError("Tpub A-link unexpectedly disconnected")

    disconnecting = tuple(
        key
        for key in sorted(simple_edges)
        if not _connected_after_deleting(simple_edges, key)
    )
    if disconnecting != ((1, 3),):
        raise AssertionError("unexpected Tpub support separation pairs")
    if len(data.class_edges[(1, 3)]) != 1:
        raise AssertionError("separating Tpub support class is not simple")
    if any(
        len(edges) > 1 and not _connected_after_deleting(simple_edges, key)
        for key, edges in data.class_edges.items()
    ):
        raise AssertionError("a repeated Tpub class lacks block rigidity")

    macro_budget, macro_rotations = enumerate_macro_rotations(simple_edges)
    if macro_budget != 144 or len(macro_rotations) != 4:
        raise AssertionError("unexpected Tpub macro-rotation census")
    schemes = tuple(
        _scheme(data, rotation, index)
        for index, rotation in enumerate(macro_rotations, start=1)
    )
    witness, counters = rigid._search_signed_ranks(data, schemes)
    verdict = (
        "SPHERICAL_CANDIDATE_REQUIRES_INDEPENDENT_AUDIT"
        if witness is not None
        else "NOT_SPHERICAL_EXACT_COMPLEX"
    )
    degrees = Counter()
    for left, right in simple_edges:
        degrees[left] += 1
        degrees[right] += 1
    return TpubNeuwirthDecision(
        original_words=ORIGINAL_WORDS,
        internal_words=INTERNAL_WORDS,
        occurrence_count=sum(map(len, INTERNAL_WORDS)),
        simple_edges=simple_edges,
        parallel_multiplicities=tuple(
            (key, len(edges))
            for key, edges in sorted(data.class_edges.items())
        ),
        degrees=tuple(degrees[vertex] for vertex in rigid.GERMS),
        macro_rotation_budget=macro_budget,
        macro_rotations=macro_rotations,
        disconnecting_support_pairs=disconnecting,
        verdict=verdict,
        witness=witness,
        counters=counters,
    )
