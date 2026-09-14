"""Independent corner-dart audit of Neuwirth rotation systems.

The two darts of each cyclic relator corner are numbered consecutively, so
the corner involution is ``alpha[d] = d ^ 1``.  Occurrence tube ends are
recovered only after every corner has been numbered.

Products in the occurrence certificate act right-to-left.  Here faces are
traced geometrically by ``phi[d] = sigma[alpha[d]]``: cross a corner edge,
then take the vertex-rotation successor.  This is the ``CA`` convention,
whereas the direct certificate counts ``AC``.  The two permutations are
conjugate by the corner involution, so their cycle counts agree.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from dataclasses import dataclass

Permutation = tuple[int, ...]
OrderDescriptor = tuple[tuple[str, tuple[int, ...]], ...]
TraceItem = tuple[int, int, int, int, int]
TraceRecord = tuple[OrderDescriptor, TraceItem]
AcceptingOrder = TraceRecord


def _cycle_count(successor: Permutation) -> int:
    seen = bytearray(len(successor))
    count = 0
    for start in range(len(successor)):
        if seen[start]:
            continue
        count += 1
        dart = start
        while not seen[dart]:
            seen[dart] = 1
            dart = successor[dart]
    return count


def _orbit_count(transitions: tuple[Permutation, ...]) -> int:
    degree = len(transitions[0])
    parent = list(range(degree))

    def find(dart: int) -> int:
        while parent[dart] != dart:
            parent[dart] = parent[parent[dart]]
            dart = parent[dart]
        return dart

    for transition in transitions:
        for dart, image in enumerate(transition):
            root = find(dart)
            image_root = find(image)
            if root != image_root:
                parent[image_root] = root
    return sum(find(dart) == dart for dart in range(degree))


@dataclass(frozen=True)
class CornerDarts:
    words: tuple[str, ...]
    letters: tuple[str, ...]
    alpha: Permutation
    tube_pair: Permutation
    departure: tuple[int, ...]
    arrival: tuple[int, ...]
    positive_occurrences: dict[str, tuple[int, ...]]

    @classmethod
    def from_words(cls, words: tuple[str, ...]) -> CornerDarts:
        if not words:
            raise ValueError("at least one nonempty word is required")

        letters: list[str] = []
        word_occurrences: list[tuple[int, ...]] = []
        next_occurrence = 0
        for word in words:
            if not isinstance(word, str) or not word:
                raise ValueError("every word must be a nonempty string")
            if any(not letter.isascii() or not letter.isalpha() for letter in word):
                raise ValueError(f"word contains a nonletter: {word!r}")
            occurrences = tuple(range(next_occurrence, next_occurrence + len(word)))
            word_occurrences.append(occurrences)
            letters.extend(word)
            next_occurrence += len(word)

        departure = [-1] * next_occurrence
        arrival = [-1] * next_occurrence
        next_dart = 0
        for occurrences in word_occurrences:
            for position, occurrence in enumerate(occurrences):
                following = occurrences[(position + 1) % len(occurrences)]
                arrival[occurrence] = next_dart
                departure[following] = next_dart + 1
                next_dart += 2

        if -1 in departure or -1 in arrival:
            raise AssertionError("every occurrence must have two corner darts")

        alpha = tuple(dart ^ 1 for dart in range(next_dart))
        tube_pair_list = [-1] * next_dart
        positive_occurrences_lists: dict[str, list[int]] = {}
        for occurrence, letter in enumerate(letters):
            departing = departure[occurrence]
            arriving = arrival[occurrence]
            tube_pair_list[departing] = arriving
            tube_pair_list[arriving] = departing
            positive_occurrences_lists.setdefault(letter.lower(), []).append(occurrence)

        if -1 in tube_pair_list:
            raise AssertionError("every corner dart must meet one occurrence tube")

        return cls(
            words=tuple(words),
            letters=tuple(letters),
            alpha=alpha,
            tube_pair=tuple(tube_pair_list),
            departure=tuple(departure),
            arrival=tuple(arrival),
            positive_occurrences={
                generator: tuple(occurrences)
                for generator, occurrences in sorted(positive_occurrences_lists.items())
            },
        )

    def positive_dart(self, occurrence: int) -> int:
        if self.letters[occurrence].islower():
            return self.departure[occurrence]
        return self.arrival[occurrence]


@dataclass(frozen=True)
class AuditCensus:
    words: tuple[str, ...]
    degrees: dict[str, int]
    expected_cases: int
    enumerated_cases: int
    link_components: set[int]
    defect_histogram: dict[int, int]
    minimum_genus: int
    trace: tuple[TraceRecord, ...]
    accepting_orders: tuple[AcceptingOrder, ...]
    trace_sha256: str

    def to_json(self) -> dict[str, object]:
        return {
            "words": list(self.words),
            "degrees": dict(self.degrees),
            "expected_cases": self.expected_cases,
            "enumerated_cases": self.enumerated_cases,
            "link_components": sorted(self.link_components),
            "defect_histogram": {
                str(defect): count
                for defect, count in sorted(self.defect_histogram.items())
            },
            "minimum_genus": self.minimum_genus,
            "accepting_orders": [
                {
                    "order": [
                        [generator, list(occurrences)]
                        for generator, occurrences in descriptor
                    ],
                    "link_components": trace_item[0],
                    "faces": trace_item[1],
                    "defect": trace_item[2],
                    "boundary_orbits_BC": trace_item[3],
                    "boundary_orbits_CB": trace_item[4],
                }
                for descriptor, trace_item in self.accepting_orders
            ],
            "trace_sha256": self.trace_sha256,
        }


def _order_options(
    data: CornerDarts,
) -> tuple[tuple[tuple[int, ...], ...], ...]:
    options = []
    for occurrences in data.positive_occurrences.values():
        first, *tail = occurrences
        options.append(
            tuple((first, *permutation) for permutation in itertools.permutations(tail))
        )
    return tuple(options)


def _rotation_successor(
    data: CornerDarts,
    positive_orders: tuple[tuple[int, ...], ...],
) -> Permutation:
    sigma = [-1] * len(data.alpha)
    for occurrence_order in positive_orders:
        positive_cycle = tuple(data.positive_dart(occurrence) for occurrence in occurrence_order)
        negative_cycle = tuple(
            data.tube_pair[dart] for dart in reversed(positive_cycle)
        )
        for cycle in (positive_cycle, negative_cycle):
            for dart, successor in zip(cycle, cycle[1:] + cycle[:1]):
                if sigma[dart] != -1:
                    raise AssertionError("rotation dart assigned more than once")
                sigma[dart] = successor
    if -1 in sigma:
        raise AssertionError("every dart must receive a rotation successor")
    return tuple(sigma)


def audit_trace(words: tuple[str, ...]) -> AuditCensus:
    """Enumerate compatible orders using an independent corner-dart model."""
    data = CornerDarts.from_words(words)
    generators = tuple(data.positive_occurrences)
    options = _order_options(data)
    expected_cases = math.prod(len(generator_options) for generator_options in options)

    trace_digest = hashlib.sha256()
    enumerated_cases = 0
    link_components: set[int] = set()
    defect_histogram: dict[int, int] = {}
    trace: list[TraceRecord] = []
    accepting_orders: list[AcceptingOrder] = []

    for positive_orders in itertools.product(*options):
        sigma = _rotation_successor(data, positive_orders)

        phi = tuple(sigma[data.alpha[dart]] for dart in range(len(data.alpha)))
        corner_after_rotation = tuple(
            data.alpha[sigma[dart]] for dart in range(len(data.alpha))
        )
        tube_after_rotation = tuple(
            data.tube_pair[sigma[dart]] for dart in range(len(data.alpha))
        )
        rotation_after_tube = tuple(
            sigma[data.tube_pair[dart]] for dart in range(len(data.alpha))
        )

        link_component_count = _orbit_count((data.alpha, sigma))
        faces = _cycle_count(phi)
        defect = (
            _cycle_count(data.alpha)
            - _cycle_count(sigma)
            + 2 * link_component_count
            - faces
        )
        boundary_orbits_BC = _orbit_count(
            (corner_after_rotation, tube_after_rotation)
        )
        boundary_orbits_CB = _orbit_count(
            (corner_after_rotation, rotation_after_tube)
        )
        trace_item: TraceItem = (
            link_component_count,
            faces,
            defect,
            boundary_orbits_BC,
            boundary_orbits_CB,
        )
        descriptor: OrderDescriptor = tuple(
            (generator, occurrence_order)
            for generator, occurrence_order in zip(generators, positive_orders)
        )

        canonical_line = json.dumps(
            (descriptor, trace_item),
            ensure_ascii=True,
            separators=(",", ":"),
        )
        trace_digest.update(canonical_line.encode("ascii"))
        trace_digest.update(b"\n")

        enumerated_cases += 1
        trace.append((descriptor, trace_item))
        link_components.add(link_component_count)
        defect_histogram[defect] = defect_histogram.get(defect, 0) + 1
        if defect == 0:
            accepting_orders.append((descriptor, trace_item))

    if enumerated_cases != expected_cases:
        raise AssertionError("the order census was not exhaustive")
    if any(defect < 0 or defect % 2 for defect in defect_histogram):
        raise AssertionError("surface defects must be nonnegative even integers")

    return AuditCensus(
        words=tuple(words),
        degrees={
            generator: len(occurrences)
            for generator, occurrences in data.positive_occurrences.items()
        },
        expected_cases=expected_cases,
        enumerated_cases=enumerated_cases,
        link_components=link_components,
        defect_histogram=defect_histogram,
        minimum_genus=min(defect_histogram) // 2,
        trace=tuple(trace),
        accepting_orders=tuple(accepting_orders),
        trace_sha256=trace_digest.hexdigest(),
    )
