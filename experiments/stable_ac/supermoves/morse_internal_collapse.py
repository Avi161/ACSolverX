"""Certified Fernández discrete-Morse supermoves for presentations.

The constructor follows Definition 2.6 of Fernández, *Morse theory for
group presentations*: build the face poset of the barycentric subdivision,
verify an acyclic matching with one critical 0-cell, and compute the attaching
words of the critical 2-cells by gradient rewriting.
"""

from __future__ import annotations

import heapq
import random
from dataclasses import dataclass
from typing import Iterable


Cell = int | str
Edge = tuple[Cell, Cell]
Letter = tuple[Cell, int]


def aux_label(relator: int, generator: str | int, kind: str, index: int) -> str:
    return f"c{relator}_{generator}{kind}_{index}"


@dataclass(frozen=True)
class PresentationPoset:
    cells: tuple[Cell, ...]
    covers: tuple[Edge, ...]
    rank: dict[Cell, int]


@dataclass(frozen=True)
class MorseReplay:
    source: tuple[str, ...]
    matching: tuple[Edge, ...]
    topological_order: tuple[Cell, ...]
    critical_cells: tuple[tuple[Cell, ...], ...]
    critical_generators: tuple[Cell, ...]
    critical_relators: tuple[Cell, ...]
    endpoint_words: tuple[str, ...]


def presentation_poset(
    generators: tuple[str, ...], relators: tuple[str, ...]
) -> PresentationPoset:
    cells: set[Cell] = set(range(len(relators) + 1))
    covers: set[Edge] = set()
    rank: dict[Cell, int] = {cell: 0 for cell in cells}

    for generator in generators:
        for kind in ("1", "2", "3"):
            cell = generator + kind
            cells.add(cell)
            rank[cell] = 0 if kind == "1" else 1
        covers.update(((0, generator + "2"), (0, generator + "3")))
        covers.update(
            ((generator + "1", generator + "2"),
             (generator + "1", generator + "3"))
        )

    for relator_index, word in enumerate(relators, start=1):
        counts = {
            generator: sum(letter.lower() == generator for letter in word)
            for generator in generators
        }
        for generator in generators:
            for occurrence in range(1, counts[generator] + 1):
                for kind in ("1", "2", "3"):
                    cell = aux_label(relator_index, generator, kind, occurrence)
                    cells.add(cell)
                    rank[cell] = 1 if kind == "1" else 2
        for occurrence in range(1, len(word) + 1):
            cell = aux_label(relator_index, 0, "", occurrence)
            cells.add(cell)
            rank[cell] = 1
            covers.add((0, cell))
            covers.add((relator_index, cell))

        for generator in generators:
            for occurrence in range(1, counts[generator] + 1):
                one = aux_label(relator_index, generator, "1", occurrence)
                two = aux_label(relator_index, generator, "2", occurrence)
                three = aux_label(relator_index, generator, "3", occurrence)
                covers.add((relator_index, one))
                covers.update(
                    ((generator + "1", one), (generator + "2", two),
                     (generator + "3", three), (one, two), (one, three))
                )

        seen = {generator: 0 for generator in generators}
        for position, letter in enumerate(word):
            generator = letter.lower()
            seen[generator] += 1
            occurrence = seen[generator]
            base = aux_label(relator_index, 0, "", position + 1)
            covers.add((base, aux_label(
                relator_index,
                generator,
                "2" if letter.islower() else "3",
                occurrence,
            )))

            previous_position = (position - 1) % len(word)
            previous = word[previous_position]
            previous_generator = previous.lower()
            previous_occurrence = sum(
                word[index].lower() == previous_generator
                for index in range(previous_position + 1)
            )
            covers.add((base, aux_label(
                relator_index,
                previous_generator,
                "3" if previous.islower() else "2",
                previous_occurrence,
            )))

    for lower, upper in covers:
        if rank[upper] != rank[lower] + 1:
            raise AssertionError((lower, upper, rank[lower], rank[upper]))
    cell_tuple = tuple(sorted(cells, key=lambda cell: (rank[cell], str(cell))))
    cover_tuple = tuple(sorted(
        covers, key=lambda edge: (rank[edge[0]], str(edge[0]), str(edge[1]))
    ))
    return PresentationPoset(cell_tuple, cover_tuple, rank)


def attaching_maps(
    generators: tuple[str, ...], relators: tuple[str, ...]
) -> dict[Cell, tuple[Letter, ...]]:
    attaching: dict[Cell, tuple[Letter, ...]] = {}
    for relator_index, word in enumerate(relators, start=1):
        seen = {generator: 0 for generator in generators}
        for position, letter in enumerate(word):
            generator = letter.lower()
            seen[generator] += 1
            occurrence = seen[generator]
            current = aux_label(relator_index, 0, "", position + 1)
            following = aux_label(
                relator_index, 0, "", (position + 1) % len(word) + 1
            )
            middle = aux_label(relator_index, generator, "1", occurrence)
            if letter.islower():
                attaching[aux_label(relator_index, generator, "2", occurrence)] = (
                    (generator + "2", 1), (middle, -1), (current, 1)
                )
                attaching[aux_label(relator_index, generator, "3", occurrence)] = (
                    (generator + "3", 1), (following, -1), (middle, 1)
                )
            else:
                attaching[aux_label(relator_index, generator, "2", occurrence)] = (
                    (generator + "2", -1), (following, -1), (middle, 1)
                )
                attaching[aux_label(relator_index, generator, "3", occurrence)] = (
                    (generator + "3", -1), (middle, -1), (current, 1)
                )
    return attaching


def _typed_key(cell: Cell) -> tuple[int, int | str]:
    return (0, cell) if isinstance(cell, int) else (1, cell)


def reversed_hasse_edges(poset: PresentationPoset, matching: tuple[Edge, ...]) -> set[Edge]:
    matched_cells = [cell for edge in matching for cell in edge]
    if len(set(matched_cells)) != len(matched_cells):
        raise ValueError("a cell occurs in more than one matching pair")
    if any(edge not in poset.covers for edge in matching):
        raise ValueError("matching contains a non-cover pair")
    oriented = set(poset.covers)
    for lower, upper in matching:
        oriented.remove((lower, upper))
        oriented.add((upper, lower))
    return oriented


def topological_order(
    poset: PresentationPoset, matching: tuple[Edge, ...]
) -> tuple[Cell, ...]:
    oriented = reversed_hasse_edges(poset, matching)
    indegree = {cell: 0 for cell in poset.cells}
    outgoing = {cell: [] for cell in poset.cells}
    for lower, upper in oriented:
        outgoing[lower].append(upper)
        indegree[upper] += 1
    heap = [(_typed_key(cell), cell) for cell, degree in indegree.items() if degree == 0]
    heapq.heapify(heap)
    order: list[Cell] = []
    while heap:
        _, cell = heapq.heappop(heap)
        order.append(cell)
        for upper in outgoing[cell]:
            indegree[upper] -= 1
            if indegree[upper] == 0:
                heapq.heappush(heap, (_typed_key(upper), upper))
    if len(order) != len(poset.cells):
        raise ValueError("the reversed matched Hasse graph contains a cycle")
    return tuple(order)


def critical_cells(
    poset: PresentationPoset, matching: tuple[Edge, ...]
) -> tuple[tuple[Cell, ...], ...]:
    matched = {cell for edge in matching for cell in edge}
    return tuple(
        tuple(
            cell for cell in poset.cells
            if poset.rank[cell] == dimension and cell not in matched
        )
        for dimension in range(3)
    )


def sample_greedy_matching(
    poset: PresentationPoset, seed: int
) -> tuple[Edge, ...]:
    """Sample a maximal acyclic matching and return its full certificate.

    The seed is only discovery provenance.  A mathematical certificate stores
    the returned matching itself and is replayed by :func:`replay`.
    """
    candidates = list(poset.covers)
    random.Random(seed).shuffle(candidates)
    matched: set[Cell] = set()
    matching: list[Edge] = []
    for edge in candidates:
        lower, upper = edge
        if lower in matched or upper in matched:
            continue
        tentative = tuple((*matching, edge))
        try:
            topological_order(poset, tentative)
        except ValueError:
            continue
        matching.append(edge)
        matched.update((lower, upper))
    return tuple(matching)


def sample_target_rank_matching(
    poset: PresentationPoset, seed: int, target_rank: int = 3
) -> tuple[Edge, ...] | None:
    """Sample an acyclic matching with critical counts ``(1,k,k)``.

    A random spanning tree in the rank-0/1 incidence graph first matches every
    vertex except a fixed root.  Random-priority rank-1/2 pairs are then added,
    subject to global acyclicity, until exactly ``target_rank`` cells remain in
    each positive dimension.  ``None`` means this random attempt got stuck.
    """
    if target_rank < 1:
        raise ValueError("target_rank must be positive")
    rng = random.Random(seed)
    vertices = tuple(cell for cell in poset.cells if poset.rank[cell] == 0)
    one_cells = tuple(cell for cell in poset.cells if poset.rank[cell] == 1)
    two_cells = tuple(cell for cell in poset.cells if poset.rank[cell] == 2)
    lower_vertices: dict[Cell, list[Cell]] = {cell: [] for cell in one_cells}
    for lower, upper in poset.covers:
        if poset.rank[lower] == 0:
            lower_vertices[upper].append(lower)
    if any(len(ends) != 2 for ends in lower_vertices.values()):
        raise ValueError("rank-1 cells must have exactly two rank-0 faces")

    adjacency: dict[Cell, list[tuple[Cell, Cell]]] = {
        vertex: [] for vertex in vertices
    }
    for one_cell, ends in lower_vertices.items():
        left, right = ends
        adjacency[left].append((right, one_cell))
        adjacency[right].append((left, one_cell))
    for neighbors in adjacency.values():
        rng.shuffle(neighbors)

    root = min(vertices, key=_typed_key)
    seen = {root}
    stack = [root]
    tree_matches: list[Edge] = []
    while stack:
        vertex = stack.pop()
        for neighbor, one_cell in adjacency[vertex]:
            if neighbor in seen:
                continue
            seen.add(neighbor)
            stack.append(neighbor)
            tree_matches.append((neighbor, one_cell))
    if len(seen) != len(vertices):
        raise ValueError("rank-0/1 incidence graph is disconnected")

    matching = list(tree_matches)
    topological_order(poset, tuple(matching))
    needed = len(two_cells) - target_rank
    if needed < 0:
        return None
    matched = {cell for edge in matching for cell in edge}
    candidates = [
        edge for edge in poset.covers
        if poset.rank[edge[0]] == 1 and poset.rank[edge[1]] == 2
    ]
    rng.shuffle(candidates)
    added = 0
    for edge in candidates:
        if added == needed:
            break
        lower, upper = edge
        if lower in matched or upper in matched:
            continue
        tentative = tuple((*matching, edge))
        try:
            topological_order(poset, tentative)
        except ValueError:
            continue
        matching.append(edge)
        matched.update((lower, upper))
        added += 1
    if added != needed:
        return None
    result = critical_cells(poset, tuple(matching))
    if tuple(map(len, result)) != (1, target_rank, target_rank):
        raise AssertionError("target-rank matching count mismatch")
    return tuple(matching)


def _inverse(word: Iterable[Letter]) -> tuple[Letter, ...]:
    return tuple((cell, -sign) for cell, sign in reversed(tuple(word)))


def _free_reduce(word: Iterable[Letter]) -> tuple[Letter, ...]:
    result: list[Letter] = []
    for letter in word:
        if result and result[-1] == (letter[0], -letter[1]):
            result.pop()
        else:
            result.append(letter)
    return tuple(result)


def morse_endpoint(
    generators: tuple[str, ...],
    relators: tuple[str, ...],
    matching: tuple[Edge, ...],
) -> tuple[tuple[Cell, ...], tuple[Cell, ...], tuple[tuple[Letter, ...], ...]]:
    poset = presentation_poset(generators, relators)
    topological_order(poset, matching)
    critical = critical_cells(poset, matching)
    if len(critical[0]) != 1:
        raise ValueError("Fernández Theorem 2.9 requires one critical 0-cell")
    attaching = attaching_maps(generators, relators)
    isolate: dict[Letter, tuple[Letter, ...]] = {}

    for one_cell, two_cell in matching:
        if two_cell in attaching:
            boundary = attaching[two_cell]
            positions = [
                index for index, (cell, _) in enumerate(boundary)
                if cell == one_cell
            ]
            if len(positions) != 1:
                raise AssertionError((one_cell, two_cell, boundary))
            position = positions[0]
            orientation = boundary[position][1]
            expression = (
                _inverse(boundary[:position])
                + _inverse(boundary[position + 1:])
            )
            if orientation == -1:
                expression = _inverse(expression)
            isolate[(one_cell, 1)] = expression
            isolate[(one_cell, -1)] = _inverse(expression)
        elif poset.rank[two_cell] == 1:
            isolate[(two_cell, 1)] = ()
            isolate[(two_cell, -1)] = ()

    def expand(letter: Letter, active: frozenset[Letter] = frozenset()) -> tuple[Letter, ...]:
        if letter not in isolate:
            return (letter,)
        if letter in active:
            raise AssertionError(f"cyclic gradient rewrite at {letter!r}")
        output: list[Letter] = []
        for child in isolate[letter]:
            output.extend(expand(child, active | {letter}))
        return _free_reduce(output)

    endpoint_relators = []
    for two_cell in critical[2]:
        word: list[Letter] = []
        for letter in attaching[two_cell]:
            word.extend(expand(letter))
        endpoint_relators.append(_free_reduce(word))
    return critical[1], critical[2], tuple(endpoint_relators)


def encode_endpoint(
    critical_generators: tuple[Cell, ...],
    relators: tuple[tuple[Letter, ...], ...],
    alphabet: str = "xyzabcdefghijklmnopqrstuvw",
) -> tuple[str, ...]:
    if len(critical_generators) > len(alphabet):
        raise ValueError("the display alphabet is too short")
    names = {
        generator: alphabet[index]
        for index, generator in enumerate(critical_generators)
    }
    return tuple(
        "".join(names[cell] if sign == 1 else names[cell].upper()
                for cell, sign in relator)
        for relator in relators
    )


def replay(
    source: tuple[str, ...], matching: tuple[Edge, ...]
) -> MorseReplay:
    generators = tuple(sorted({letter.lower() for word in source for letter in word}))
    poset = presentation_poset(generators, source)
    order = topological_order(poset, matching)
    critical = critical_cells(poset, matching)
    endpoint_generators, endpoint_relators, words = morse_endpoint(
        generators, source, matching
    )
    return MorseReplay(
        source=source,
        matching=matching,
        topological_order=order,
        critical_cells=critical,
        critical_generators=endpoint_generators,
        critical_relators=endpoint_relators,
        endpoint_words=encode_endpoint(endpoint_generators, words),
    )
