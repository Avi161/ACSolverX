"""Replay local incidence calculations in the internal BS(3,4) flow module.

The Bass--Serre identification and every unbounded conclusion are proved
in Markdown.  This module checks only the displayed finite half-stars and
their exact rational constraint matrices.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Sequence


Matrix = tuple[tuple[int, ...], ...]


@dataclass(frozen=True)
class OneYSelectedEdge:
    left_residue: int
    right_power: int
    britton_word: str
    local_half_star: str | None


def half_star_indices(kind: str, representative_power: int = 0) -> tuple[int, ...]:
    """Return the cyclic coset indices in one directed half-star."""
    if kind == "incoming":
        branching = 4
    elif kind == "outgoing":
        branching = 3
    else:
        raise ValueError("kind must be 'incoming' or 'outgoing'")
    return tuple(
        sorted((index + representative_power) % branching for index in range(branching))
    )


def canonical_collapse_matrix(branching: int, sigma: int) -> Matrix:
    """Build the local equations ``edge_i + sigma*star = 0`` and conservation."""
    if branching not in (3, 4):
        raise ValueError("branching must be 3 or 4")
    if sigma not in (-1, 1):
        raise ValueError("sigma must be -1 or 1")

    rows: list[tuple[int, ...]] = []
    for index in range(branching):
        row = [0] * (branching + 1)
        row[index] = 1
        row[-1] = sigma
        rows.append(tuple(row))
    rows.append(tuple([-1] * branching + [1]))
    return tuple(rows)


def matrix_rank(matrix: Sequence[Sequence[int]]) -> int:
    """Compute exact row rank over the rationals."""
    if not matrix:
        return 0
    width = len(matrix[0])
    if any(len(row) != width for row in matrix):
        raise ValueError("matrix rows must have equal length")

    rows = [[Fraction(value) for value in row] for row in matrix]
    rank = 0
    for column in range(width):
        pivot = next(
            (index for index in range(rank, len(rows)) if rows[index][column]),
            None,
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        pivot_value = rows[rank][column]
        rows[rank] = [value / pivot_value for value in rows[rank]]
        for index, row in enumerate(rows):
            if index == rank or not row[column]:
                continue
            scale = row[column]
            rows[index] = [
                value - scale * pivot_entry
                for value, pivot_entry in zip(row, rows[rank])
            ]
        rank += 1
        if rank == len(rows):
            break
    return rank


def one_y_double_coset_signature(left_x_power: int, right_x_power: int) -> int:
    """Return the left residue in ``C x^r y x^s H = C x^(r mod 4) y H``."""
    if not isinstance(left_x_power, int) or not isinstance(right_x_power, int):
        raise TypeError("powers must be integers")
    return left_x_power % 4


def _power_word(generator: str, exponent: int) -> str:
    return (
        generator * exponent
        if exponent >= 0
        else generator.upper() * (-exponent)
    )


def classify_one_y_selected_edge(
    left_x_power: int,
    right_x_power: int,
) -> OneYSelectedEdge:
    """Classify ``C x^r y x^s`` against the two local half-stars."""
    residue = one_y_double_coset_signature(left_x_power, right_x_power)
    return OneYSelectedEdge(
        left_residue=residue,
        right_power=right_x_power,
        britton_word=(
            _power_word("x", residue)
            + "y"
            + _power_word("x", right_x_power)
        ),
        local_half_star="outgoing" if residue == 0 else None,
    )
