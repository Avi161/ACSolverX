from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import reduce
from itertools import combinations, product
from math import gcd


VARIABLES = ("a", "b", "t", "r", "s", "u")


@dataclass(frozen=True)
class LinearRow:
    coefficients: tuple[int, int, int, int, int, int]
    right_hand_side: int


def canonical_row(
    coefficients: tuple[int, int, int, int, int, int],
    right_hand_side: int,
) -> LinearRow:
    divisor = reduce(
        gcd,
        (abs(value) for value in coefficients + (right_hand_side,)),
    )
    if divisor:
        coefficients = tuple(value // divisor for value in coefficients)
        right_hand_side //= divisor
    return LinearRow(coefficients, right_hand_side)


def row_from_terms(
    terms: tuple[tuple[str, int], ...],
    right_hand_side: int,
) -> LinearRow:
    accumulated = {variable: 0 for variable in VARIABLES}
    for variable, coefficient in terms:
        accumulated[variable] += coefficient
    return canonical_row(
        tuple(accumulated[variable] for variable in VARIABLES),
        right_hand_side,
    )


def triangle_rows(left: str, right: str, result: str) -> dict[str, LinearRow]:
    return {
        "P": row_from_terms(((left, 1), (right, 1), (result, 1)), 2),
        "Z": row_from_terms(((left, -1), (right, -1), (result, 1)), 0),
        "Y": row_from_terms(((left, -1), (right, 1), (result, -1)), 0),
        "X": row_from_terms(((left, 1), (right, -1), (result, -1)), 0),
    }


STAGE_ROWS = tuple(
    triangle_rows(*triple)
    for triple in (
        ("a", "b", "r"),
        ("b", "r", "s"),
        ("r", "s", "u"),
        ("u", "s", "t"),
    )
)


FACETS = (
    row_from_terms((("a", -3), ("b", -5), ("t", 1)), 0),
    row_from_terms((("a", 3), ("b", -5), ("t", -1)), 2),
    row_from_terms((("a", -3), ("b", 5), ("t", -1)), 4),
    row_from_terms((("a", 3), ("b", 5), ("t", 1)), 8),
)


FACET_CERTIFICATES = (
    ((3, 0, "Z"), (2, 1, "Z"), (1, 2, "Z"), (1, 3, "Z")),
    ((3, 0, "X"), (2, 1, "Y"), (1, 2, "P"), (1, 3, "Y")),
    ((3, 0, "Y"), (2, 1, "P"), (1, 2, "X"), (1, 3, "X")),
    ((3, 0, "P"), (2, 1, "X"), (1, 2, "Y"), (1, 3, "P")),
)


VERTICES = {
    (Fraction(0), Fraction(0), Fraction(0)),
    (Fraction(0), Fraction(1, 5), Fraction(1)),
    (Fraction(0), Fraction(4, 5), Fraction(0)),
    (Fraction(0), Fraction(1), Fraction(1)),
    (Fraction(1, 3), Fraction(0), Fraction(1)),
    (Fraction(1, 3), Fraction(1), Fraction(0)),
    (Fraction(2, 3), Fraction(0), Fraction(0)),
    (Fraction(2, 3), Fraction(1), Fraction(1)),
    (Fraction(1), Fraction(0), Fraction(1)),
    (Fraction(1), Fraction(1, 5), Fraction(0)),
    (Fraction(1), Fraction(4, 5), Fraction(1)),
    (Fraction(1), Fraction(1), Fraction(0)),
}


LIFTS = {
    (Fraction(0), Fraction(0), Fraction(0), Fraction(0), Fraction(0), Fraction(0)),
    (Fraction(0), Fraction(1, 5), Fraction(1), Fraction(1, 5), Fraction(2, 5), Fraction(3, 5)),
    (Fraction(0), Fraction(4, 5), Fraction(0), Fraction(4, 5), Fraction(2, 5), Fraction(2, 5)),
    (Fraction(0), Fraction(1), Fraction(1), Fraction(1), Fraction(0), Fraction(1)),
    (Fraction(1, 3), Fraction(0), Fraction(1), Fraction(1, 3), Fraction(1, 3), Fraction(2, 3)),
    (Fraction(1, 3), Fraction(1), Fraction(0), Fraction(2, 3), Fraction(1, 3), Fraction(1, 3)),
    (Fraction(2, 3), Fraction(0), Fraction(0), Fraction(2, 3), Fraction(2, 3), Fraction(2, 3)),
    (Fraction(2, 3), Fraction(1), Fraction(1), Fraction(1, 3), Fraction(2, 3), Fraction(1, 3)),
    (Fraction(1), Fraction(0), Fraction(1), Fraction(1), Fraction(1), Fraction(0)),
    (Fraction(1), Fraction(1, 5), Fraction(0), Fraction(4, 5), Fraction(3, 5), Fraction(3, 5)),
    (Fraction(1), Fraction(4, 5), Fraction(1), Fraction(1, 5), Fraction(3, 5), Fraction(2, 5)),
    (Fraction(1), Fraction(1), Fraction(0), Fraction(0), Fraction(1), Fraction(1)),
}


def add_rows(certificate: tuple[tuple[int, int, str], ...]) -> LinearRow:
    coefficients = [0] * len(VARIABLES)
    right_hand_side = 0
    for weight, stage, name in certificate:
        row = STAGE_ROWS[stage][name]
        coefficients = [
            value + weight * entry
            for value, entry in zip(coefficients, row.coefficients)
        ]
        right_hand_side += weight * row.right_hand_side
    return canonical_row(tuple(coefficients), right_hand_side)


def flat_polygon_rows() -> set[LinearRow]:
    rows = set()
    for source_a_count, source_b_count, target_count in product(
        range(4),
        range(6),
        range(2),
    ):
        if (source_a_count + source_b_count + target_count) % 2 != 1:
            continue
        rows.add(
            row_from_terms(
                (
                    ("a", 2 * source_a_count - 3),
                    ("b", 2 * source_b_count - 5),
                    ("t", 2 * target_count - 1),
                ),
                source_a_count + source_b_count + target_count - 1,
            )
        )
    return rows


def box_rows() -> set[LinearRow]:
    return {
        row_from_terms(((variable, sign),), right_hand_side)
        for variable in VARIABLES
        for sign, right_hand_side in ((-1, 0), (1, 1))
    }


def satisfies(row: LinearRow, point: tuple[Fraction, ...]) -> bool:
    return sum(
        coefficient * value
        for coefficient, value in zip(row.coefficients, point)
    ) <= row.right_hand_side


def solve_three(rows: tuple[LinearRow, LinearRow, LinearRow]) -> tuple[Fraction, Fraction, Fraction] | None:
    matrix = [
        [Fraction(value) for value in row.coefficients[:3]]
        + [Fraction(row.right_hand_side)]
        for row in rows
    ]
    pivot_row = 0
    for column in range(3):
        pivot = next(
            (index for index in range(pivot_row, 3) if matrix[index][column]),
            None,
        )
        if pivot is None:
            return None
        matrix[pivot_row], matrix[pivot] = matrix[pivot], matrix[pivot_row]
        pivot_value = matrix[pivot_row][column]
        matrix[pivot_row] = [value / pivot_value for value in matrix[pivot_row]]
        for index in range(3):
            if index == pivot_row or not matrix[index][column]:
                continue
            multiplier = matrix[index][column]
            matrix[index] = [
                value - multiplier * pivot_entry
                for value, pivot_entry in zip(matrix[index], matrix[pivot_row])
            ]
        pivot_row += 1
    return tuple(matrix[index][3] for index in range(3))


def facet_vertices() -> set[tuple[Fraction, Fraction, Fraction]]:
    defining_rows = set(FACETS)
    defining_rows |= {
        row_from_terms(((variable, sign),), right_hand_side)
        for variable in ("a", "b", "t")
        for sign, right_hand_side in ((-1, 0), (1, 1))
    }
    vertices = set()
    for selected in combinations(defining_rows, 3):
        point = solve_three(selected)
        if point is not None and all(satisfies(row, point) for row in defining_rows):
            vertices.add(point)
    return vertices


def eliminate(system: set[LinearRow], variable: str) -> set[LinearRow]:
    column = VARIABLES.index(variable)
    positive = [row for row in system if row.coefficients[column] > 0]
    negative = [row for row in system if row.coefficients[column] < 0]
    result = {row for row in system if row.coefficients[column] == 0}
    for upper in positive:
        for lower in negative:
            upper_scale = -lower.coefficients[column]
            lower_scale = upper.coefficients[column]
            row = canonical_row(
                tuple(
                    upper_scale * left + lower_scale * right
                    for left, right in zip(upper.coefficients, lower.coefficients)
                ),
                upper_scale * upper.right_hand_side
                + lower_scale * lower.right_hand_side,
            )
            if any(row.coefficients) or row.right_hand_side < 0:
                result.add(row)
    return result


def dependency_elimination_counts() -> tuple[int, int, int, int]:
    system = set(box_rows())
    for stage in STAGE_ROWS:
        system |= set(stage.values())
    counts = [len(system)]
    for variable in ("u", "s", "r"):
        system = eliminate(system, variable)
        counts.append(len(system))
    return tuple(counts)


def normalized_final_interval(
    source_a_angle: Fraction,
    source_b_angle: Fraction,
) -> tuple[Fraction, Fraction]:
    assert 0 <= source_a_angle <= 1
    assert 0 <= source_b_angle <= 1
    lower = max(
        Fraction(0),
        3 * source_a_angle - 5 * source_b_angle - 2,
        5 * source_b_angle - 3 * source_a_angle - 4,
    )
    upper = min(
        Fraction(1),
        3 * source_a_angle + 5 * source_b_angle,
        8 - 3 * source_a_angle - 5 * source_b_angle,
    )
    assert lower <= upper
    return lower, upper


@dataclass(frozen=True)
class DependencyHypergroupCertificate:
    flat_polygon_row_count: int
    dependency_elimination_counts: tuple[int, int, int, int]
    nonbox_facet_count: int
    vertex_count: int
    dependency_lift_count: int


def dependency_hypergroup_certificate() -> DependencyHypergroupCertificate:
    polygon_rows = flat_polygon_rows()
    assert len(polygon_rows) == 24
    assert set(FACETS) <= polygon_rows
    assert tuple(
        add_rows(certificate)
        for certificate in FACET_CERTIFICATES
    ) == FACETS

    vertices = facet_vertices()
    assert vertices == VERTICES
    assert all(
        satisfies(row, vertex)
        for row in polygon_rows
        for vertex in vertices
    )

    dependency_rows = set(box_rows())
    for stage in STAGE_ROWS:
        dependency_rows |= set(stage.values())
    assert {lift[:3] for lift in LIFTS} == VERTICES
    assert all(
        satisfies(row, lift)
        for row in dependency_rows
        for lift in LIFTS
    )

    counts = dependency_elimination_counts()
    assert counts == (28, 32, 60, 278)
    return DependencyHypergroupCertificate(
        flat_polygon_row_count=len(polygon_rows),
        dependency_elimination_counts=counts,
        nonbox_facet_count=len(FACETS),
        vertex_count=len(vertices),
        dependency_lift_count=len(LIFTS),
    )


if __name__ == "__main__":
    print(dependency_hypergroup_certificate())
