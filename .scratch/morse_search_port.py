"""Pure-Python port of the Fernández Morse-presentation constructor.

This is a search prototype.  It follows the exact cell labels and attaching
maps in the author's GPL reference implementation, but uses no Sage objects.
"""

from __future__ import annotations

import random
from dataclasses import dataclass


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


def presentation_poset(generators: tuple[str, ...], relators: tuple[str, ...]) -> PresentationPoset:
    cells: set[Cell] = set(range(len(relators) + 1))
    covers: set[Edge] = set()
    rank: dict[Cell, int] = {cell: 0 for cell in cells}

    for generator in generators:
        for kind in ("1", "2", "3"):
            cell = generator + kind
            cells.add(cell)
            rank[cell] = 0 if kind == "1" else 1
        covers.update(((0, generator + "2"), (0, generator + "3")))
        covers.update(((generator + "1", generator + "2"), (generator + "1", generator + "3")))

    for relator_index, word in enumerate(relators, start=1):
        counts = {generator: sum(letter.lower() == generator for letter in word) for generator in generators}
        total = len(word)
        for generator in generators:
            for occurrence in range(1, counts[generator] + 1):
                for kind in ("1", "2", "3"):
                    cell = aux_label(relator_index, generator, kind, occurrence)
                    cells.add(cell)
                    rank[cell] = 1 if kind == "1" else 2
        for occurrence in range(1, total + 1):
            cell = aux_label(relator_index, 0, "", occurrence)
            cells.add(cell)
            rank[cell] = 1

        for occurrence in range(1, total + 1):
            covers.add((relator_index, aux_label(relator_index, 0, "", occurrence)))
            covers.add((0, aux_label(relator_index, 0, "", occurrence)))
        for generator in generators:
            for occurrence in range(1, counts[generator] + 1):
                covers.add((relator_index, aux_label(relator_index, generator, "1", occurrence)))
                for kind in ("1", "2", "3"):
                    covers.add((generator + kind, aux_label(relator_index, generator, kind, occurrence)))
                covers.add((aux_label(relator_index, generator, "1", occurrence),
                            aux_label(relator_index, generator, "2", occurrence)))
                covers.add((aux_label(relator_index, generator, "1", occurrence),
                            aux_label(relator_index, generator, "3", occurrence)))

        seen = {generator: 0 for generator in generators}
        for position, letter in enumerate(word):
            generator = letter.lower()
            seen[generator] += 1
            occurrence = seen[generator]
            base = aux_label(relator_index, 0, "", position + 1)
            right_kind = "2" if letter.islower() else "3"
            covers.add((base, aux_label(relator_index, generator, right_kind, occurrence)))

            previous_position = (position - 1) % total
            previous = word[previous_position]
            previous_generator = previous.lower()
            previous_occurrence = sum(
                word[j].lower() == previous_generator for j in range(previous_position + 1)
            )
            left_kind = "3" if previous.islower() else "2"
            covers.add((base, aux_label(
                relator_index, previous_generator, left_kind, previous_occurrence
            )))

    for lower, upper in covers:
        if rank[upper] != rank[lower] + 1:
            raise AssertionError((lower, upper, rank[lower], rank[upper]))
    return PresentationPoset(
        cells=tuple(sorted(cells, key=lambda cell: (rank[cell], str(cell)))),
        covers=tuple(sorted(covers, key=lambda edge: (rank[edge[0]], str(edge)))),
        rank=rank,
    )


def attaching_maps(generators: tuple[str, ...], relators: tuple[str, ...]) -> dict[Cell, tuple[Letter, ...]]:
    attaching: dict[Cell, tuple[Letter, ...]] = {}
    for relator_index, word in enumerate(relators, start=1):
        seen = {generator: 0 for generator in generators}
        for position, letter in enumerate(word):
            generator = letter.lower()
            seen[generator] += 1
            occurrence = seen[generator]
            current_base = aux_label(relator_index, 0, "", position + 1)
            next_base = aux_label(relator_index, 0, "", (position + 1) % len(word) + 1)
            middle = aux_label(relator_index, generator, "1", occurrence)
            if letter.islower():
                attaching[aux_label(relator_index, generator, "2", occurrence)] = (
                    (generator + "2", 1), (middle, -1), (current_base, 1)
                )
                attaching[aux_label(relator_index, generator, "3", occurrence)] = (
                    (generator + "3", 1), (next_base, -1), (middle, 1)
                )
            else:
                attaching[aux_label(relator_index, generator, "2", occurrence)] = (
                    (generator + "2", -1), (next_base, -1), (middle, 1)
                )
                attaching[aux_label(relator_index, generator, "3", occurrence)] = (
                    (generator + "3", -1), (middle, -1), (current_base, 1)
                )
    return attaching


def _acyclic(cells: tuple[Cell, ...], oriented_edges: set[Edge]) -> bool:
    indegree = {cell: 0 for cell in cells}
    outgoing = {cell: [] for cell in cells}
    for lower, upper in oriented_edges:
        outgoing[lower].append(upper)
        indegree[upper] += 1
    stack = [cell for cell, degree in indegree.items() if degree == 0]
    visited = 0
    while stack:
        cell = stack.pop()
        visited += 1
        for upper in outgoing[cell]:
            indegree[upper] -= 1
            if indegree[upper] == 0:
                stack.append(upper)
    return visited == len(cells)


def greedy_acyclic_matching(poset: PresentationPoset, rng: random.Random) -> tuple[Edge, ...]:
    candidates = list(poset.covers)
    rng.shuffle(candidates)
    oriented = set(poset.covers)
    matched: set[Cell] = set()
    matching: list[Edge] = []
    for lower, upper in candidates:
        if lower in matched or upper in matched:
            continue
        oriented.remove((lower, upper))
        oriented.add((upper, lower))
        if _acyclic(poset.cells, oriented):
            matched.update((lower, upper))
            matching.append((lower, upper))
        else:
            oriented.remove((upper, lower))
            oriented.add((lower, upper))
    return tuple(matching)


def critical_cells(poset: PresentationPoset, matching: tuple[Edge, ...]) -> tuple[tuple[Cell, ...], ...]:
    matched = {cell for edge in matching for cell in edge}
    return tuple(
        tuple(cell for cell in poset.cells if poset.rank[cell] == dimension and cell not in matched)
        for dimension in range(3)
    )


def _inverse(word: tuple[Letter, ...]) -> tuple[Letter, ...]:
    return tuple((cell, -sign) for cell, sign in reversed(word))


def _free_reduce(word: list[Letter] | tuple[Letter, ...]) -> tuple[Letter, ...]:
    result: list[Letter] = []
    for letter in word:
        if result and result[-1] == (letter[0], -letter[1]):
            result.pop()
        else:
            result.append(letter)
    return tuple(result)


def morse_endpoint(
    generators: tuple[str, ...], relators: tuple[str, ...], matching: tuple[Edge, ...]
) -> tuple[tuple[Cell, ...], tuple[tuple[Letter, ...], ...]]:
    poset = presentation_poset(generators, relators)
    critical = critical_cells(poset, matching)
    attaching = attaching_maps(generators, relators)
    isolate: dict[Letter, tuple[Letter, ...]] = {}

    for one_cell, two_cell in matching:
        if two_cell in attaching:
            boundary = attaching[two_cell]
            positions = [index for index, (cell, _) in enumerate(boundary) if cell == one_cell]
            if len(positions) != 1:
                raise AssertionError((one_cell, two_cell, boundary))
            position = positions[0]
            orientation = boundary[position][1]
            before = boundary[:position]
            after = boundary[position + 1:]
            expression = _inverse(before) + _inverse(after)
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
            raise AssertionError(f"cyclic gradient rewrite through {letter!r}")
        output: list[Letter] = []
        for child in isolate[letter]:
            output.extend(expand(child, active | {letter}))
        return _free_reduce(output)

    output_relators = []
    for two_cell in critical[2]:
        word: list[Letter] = []
        for letter in attaching[two_cell]:
            word.extend(expand(letter))
        output_relators.append(_free_reduce(word))
    return critical[1], tuple(output_relators)


def encoded_rank_two(endpoint: tuple[tuple[Cell, ...], tuple[tuple[Letter, ...], ...]]) -> tuple[str, str] | None:
    generators, relators = endpoint
    if len(generators) != 2 or len(relators) != 2:
        return None
    alphabet = {generators[0]: "x", generators[1]: "y"}
    words = []
    for relator in relators:
        words.append("".join(
            alphabet[cell] if sign == 1 else alphabet[cell].upper()
            for cell, sign in relator
        ))
    return tuple(words)  # type: ignore[return-value]


def collapse_unique_occurrences(
    endpoint: tuple[tuple[Cell, ...], tuple[tuple[Letter, ...], ...]],
    *,
    stop_rank: int = 0,
) -> tuple[tuple[Cell, ...], tuple[tuple[Letter, ...], ...], tuple[tuple[Cell, int], ...]]:
    """Perform explicit free 1-cell/2-cell collapses on a Morse presentation."""
    generators = list(endpoint[0])
    relators = list(endpoint[1])
    ledger: list[tuple[Cell, int]] = []
    while len(generators) > stop_rank:
        choice = None
        for relator_index, relator in enumerate(relators):
            counts = {
                generator: sum(cell == generator for cell, _ in relator)
                for generator in generators
            }
            generator = next((g for g in generators if counts[g] == 1), None)
            if generator is not None:
                choice = relator_index, generator
                break
        if choice is None:
            break
        relator_index, generator = choice
        relator = relators[relator_index]
        position = next(i for i, (cell, _) in enumerate(relator) if cell == generator)
        orientation = relator[position][1]
        expression = _inverse(relator[:position]) + _inverse(relator[position + 1:])
        if orientation == -1:
            expression = _inverse(expression)
        inverse_expression = _inverse(expression)

        rewritten = []
        for index, other in enumerate(relators):
            if index == relator_index:
                continue
            output: list[Letter] = []
            for cell, sign in other:
                if cell != generator:
                    output.append((cell, sign))
                else:
                    output.extend(expression if sign == 1 else inverse_expression)
            rewritten.append(_free_reduce(output))
        generators.remove(generator)
        relators = rewritten
        ledger.append((generator, relator_index))
    return tuple(generators), tuple(relators), tuple(ledger)


def verify_matching(poset: PresentationPoset, matching: tuple[Edge, ...]) -> bool:
    if len({cell for edge in matching for cell in edge}) != 2 * len(matching):
        return False
    if any(edge not in poset.covers for edge in matching):
        return False
    oriented = set(poset.covers)
    for lower, upper in matching:
        oriented.remove((lower, upper))
        oriented.add((upper, lower))
    return _acyclic(poset.cells, oriented)
