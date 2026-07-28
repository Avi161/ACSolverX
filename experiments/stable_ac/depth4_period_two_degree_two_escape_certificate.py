from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache

try:
    from experiments.stable_ac import depth4_period_two_lift_certificate as lift
except ModuleNotFoundError:
    import depth4_period_two_lift_certificate as lift


ModuleVariables = tuple[lift.ModuleVector, ...]
KernelLetter = tuple[lift.Word, int]
KernelWord = tuple[KernelLetter, ...]
Wedge = tuple[lift.Word, lift.Word]
WedgeVector = dict[Wedge, int]


ALTERNATE_10 = (
    (0, 1, "cT"),
    (0, -3, "cTTct"),
    (0, -2, "cTTctt"),
    (2, -2, "cT"),
    (2, -3, "cTct"),
    (2, -2, "cTTct"),
    (2, -2, "cTctt"),
    (3, -2, ""),
    (3, -1, "TT"),
    (3, -1, "TTcT"),
    (3, -2, "TTct"),
    (3, -1, "TTcTct"),
    (3, -1, "TTctcT"),
    (3, -1, "TTcTTct"),
    (3, -1, "TTctcTcTct"),
    (4, 1, "T"),
    (4, 1, "TcT"),
    (4, 1, "Tct"),
    (4, 1, "TcTct"),
    (4, 1, "TctcT"),
    (4, 1, "TcTTct"),
    (4, 1, "TctcTcTct"),
)

ALTERNATE_01 = (
    (0, 4, "cT"),
    (0, 2, "cTTct"),
    (0, -1, "cTTctt"),
    (2, 4, ""),
    (2, 8, "cT"),
    (2, 2, "ct"),
    (2, 4, "cTTct"),
    (2, -2, "cTctt"),
    (3, -2, ""),
    (3, 5, "TT"),
    (3, 4, "TTcT"),
    (3, 6, "TTct"),
    (3, 1, "TTctt"),
    (3, 2, "TTcTct"),
    (3, 6, "TTctcT"),
    (3, 2, "TTcTTct"),
    (3, -1, "TTctcTcTctt"),
    (4, -5, "T"),
    (4, -4, "TcT"),
    (4, -2, "Tct"),
    (4, -2, "TcTct"),
    (4, -6, "TctcT"),
    (4, -2, "TcTTct"),
    (4, 1, "TctcTcTctt"),
)


def variables_from_entries(entries: tuple[tuple[int, int, str], ...]) -> ModuleVariables:
    variables: list[lift.ModuleVector] = [{} for _ in range(5)]
    for operator_index, coefficient, module_vertex in entries:
        vertex = lift.parse_quotient(module_vertex)
        variables[operator_index][vertex] = variables[operator_index].get(vertex, 0) + coefficient
    return tuple(lift.clean_vector(variable) for variable in variables)


def add_variables(*values: ModuleVariables) -> ModuleVariables:
    return tuple(
        lift.add_vectors(*(value[index] for value in values))
        for index in range(5)
    )


def subtract_variables(left: ModuleVariables, right: ModuleVariables) -> ModuleVariables:
    return tuple(
        lift.add_vectors(left[index], lift.scale_vector(right[index], -1))
        for index in range(5)
    )


def recurrence_data():
    r = lift.multiply(lift.SOURCE_A, lift.conjugate(lift.inverse(lift.SOURCE_B), lift.H0))
    s = lift.multiply(lift.SOURCE_B, lift.conjugate(lift.inverse(r), lift.H1))
    u = lift.multiply(r, lift.conjugate(lift.inverse(s), lift.H2))
    z = lift.multiply(lift.inverse(u), lift.conjugate(s, lift.H3))
    defect = lift.relation_module(lift.multiply(z, lift.inverse(lift.TARGET)))
    return r, s, u, defect, lift.build_operators(r, s, u)


def act(group_element: lift.Word, module_vertex: lift.Word) -> lift.Word:
    return lift.c_vertex(lift.quotient_multiply(group_element, module_vertex))


def local_columns(
    defect: lift.ModuleVector,
    operators: tuple[lift.GroupRing, ...],
):
    candidates = set()
    for operator_index, operator in enumerate(operators):
        for group_element in operator:
            group_inverse = lift.quotient_inverse(group_element)
            for target_row in defect:
                candidates.add((operator_index, act(group_inverse, target_row)))
    columns = sorted(candidates, key=lambda item: (item[0], len(item[1]), item[1]))
    output_rows = set(defect)
    column_entries = []
    for operator_index, module_vertex in columns:
        entries: dict[lift.Word, int] = defaultdict(int)
        for group_element, coefficient in operators[operator_index].items():
            entries[act(group_element, module_vertex)] += coefficient
        clean_entries = {row: value for row, value in entries.items() if value}
        output_rows.update(clean_entries)
        column_entries.append(clean_entries)
    rows = sorted(output_rows, key=lambda word: (len(word), word))
    row_index = {row: index for index, row in enumerate(rows)}
    matrix_entries = {
        (row_index[row], column_index): coefficient
        for column_index, column in enumerate(column_entries)
        for row, coefficient in column.items()
    }
    return rows, columns, matrix_entries


def rank_mod(
    entries: dict[tuple[int, int], int],
    row_count: int,
    column_count: int,
    prime: int,
) -> int:
    rows = [
        [entries.get((row, column), 0) % prime for column in range(column_count)]
        for row in range(row_count)
    ]
    rank = 0
    for column in range(column_count):
        pivot = next((row for row in range(rank, row_count) if rows[row][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inverse = pow(rows[rank][column], -1, prime)
        rows[rank] = [(value * inverse) % prime for value in rows[rank]]
        for row in range(rank + 1, row_count):
            if rows[row][column]:
                factor = rows[row][column]
                rows[row] = [
                    (left - factor * right) % prime
                    for left, right in zip(rows[row], rows[rank])
                ]
        rank += 1
    return rank


def flatten_variables(
    variables: ModuleVariables,
    columns: list[tuple[int, lift.Word]],
) -> tuple[int, ...]:
    return tuple(variables[operator_index].get(module_vertex, 0) for operator_index, module_vertex in columns)


def correction_image(
    variables: ModuleVariables,
    operators: tuple[lift.GroupRing, ...],
) -> lift.ModuleVector:
    return lift.add_vectors(*(
        lift.apply_operator(operator, variable)
        for operator, variable in zip(operators, variables)
    ))


def corrected_residual(variables: ModuleVariables) -> lift.Word:
    corrections = tuple(lift.lift_module_vector(variable) for variable in variables)
    conjugators = (
        lift.multiply(corrections[0], lift.H0),
        lift.multiply(corrections[1], lift.H1),
        lift.multiply(corrections[2], lift.H2),
        lift.multiply(corrections[3], lift.H3),
    )
    r = lift.multiply(
        lift.SOURCE_A,
        lift.conjugate(lift.inverse(lift.SOURCE_B), conjugators[0]),
    )
    s = lift.multiply(
        lift.SOURCE_B,
        lift.conjugate(lift.inverse(r), conjugators[1]),
    )
    u = lift.multiply(r, lift.conjugate(lift.inverse(s), conjugators[2]))
    z = lift.multiply(lift.inverse(u), lift.conjugate(s, conjugators[3]))
    target = lift.conjugate(lift.TARGET, corrections[4])
    return lift.multiply(z, lift.inverse(target))


def schreier_word(word: lift.Word) -> KernelWord:
    quotient_prefix: lift.Word = ()
    reduced: list[KernelLetter] = []
    for letter in word:
        next_letter = None
        if letter == lift.C and quotient_prefix and abs(quotient_prefix[-1]) == lift.C:
            next_letter = (quotient_prefix[:-1], 1)
        elif letter == -lift.C and not (
            quotient_prefix and abs(quotient_prefix[-1]) == lift.C
        ):
            next_letter = (quotient_prefix, -1)
        if next_letter is not None:
            if (
                reduced
                and reduced[-1][0] == next_letter[0]
                and reduced[-1][1] == -next_letter[1]
            ):
                reduced.pop()
            else:
                reduced.append(next_letter)
        quotient_prefix = lift.quotient_append(quotient_prefix, letter)
    assert quotient_prefix == ()
    return tuple(reduced)


def degree_two(word: KernelWord) -> WedgeVector:
    linear: dict[lift.Word, int] = defaultdict(int)
    quadratic: dict[tuple[lift.Word, lift.Word], int] = defaultdict(int)
    for module_vertex, sign in word:
        for left_vertex, coefficient in tuple(linear.items()):
            quadratic[left_vertex, module_vertex] += coefficient * sign
        if sign == -1:
            quadratic[module_vertex, module_vertex] += 1
        linear[module_vertex] += sign
        if not linear[module_vertex]:
            del linear[module_vertex]
    assert not linear
    result = {}
    for (left, right), coefficient in quadratic.items():
        if (len(left), left) >= (len(right), right):
            continue
        assert quadratic.get((right, left), 0) == -coefficient
        if coefficient:
            result[left, right] = coefficient
    return result


def s3_point(module_vertex: lift.Word) -> int:
    c_image = (0, 2, 1)
    t_image = (1, 2, 0)
    t_inverse = (2, 0, 1)
    point = 0
    for letter in reversed(module_vertex):
        permutation = c_image if abs(letter) == lift.C else t_image if letter == lift.T else t_inverse
        point = permutation[point]
    return point


def degree_two_obstructions(value: WedgeVector) -> tuple[int, int]:
    full_augmentation = sum(value.values()) % 2
    finite_vector = [0, 0, 0]
    pair_index = {(0, 1): 0, (0, 2): 1, (1, 2): 2}
    for (left, right), coefficient in value.items():
        left_point = s3_point(left)
        right_point = s3_point(right)
        if left_point == right_point:
            continue
        pair = tuple(sorted((left_point, right_point)))
        finite_vector[pair_index[pair]] = (
            finite_vector[pair_index[pair]] + coefficient
        ) % 2
    return full_augmentation, sum(finite_vector) % 2


@dataclass(frozen=True)
class PeriodTwoDegreeTwoEscapeCertificate:
    local_matrix_shape: tuple[int, int]
    local_matrix_nonzero: int
    local_matrix_ranks: tuple[tuple[int, int], ...]
    local_kernel_dimension: int
    parity_classes: tuple[tuple[int, int], ...]
    degree_two_obstructions: tuple[tuple[int, int], ...]
    residual_lengths: tuple[int, ...]
    kernel_lengths: tuple[int, ...]
    escape_required: bool


@lru_cache(maxsize=1)
def period_two_degree_two_escape_certificate() -> PeriodTwoDegreeTwoEscapeCertificate:
    _, _, _, defect, operators = recurrence_data()
    rows, columns, matrix_entries = local_columns(defect, operators)
    base = variables_from_entries(lift.CORRECTION)
    alternate_10 = variables_from_entries(ALTERNATE_10)
    alternate_01 = variables_from_entries(ALTERNATE_01)
    kernel_0 = subtract_variables(alternate_10, base)
    kernel_1 = subtract_variables(alternate_01, base)
    alternate_11 = add_variables(base, kernel_0, kernel_1)
    classes = (base, alternate_10, alternate_01, alternate_11)

    for variables in classes:
        assert not lift.add_vectors(defect, correction_image(variables, operators))
        assert all(
            (operator_index, module_vertex) in set(columns)
            for operator_index, variable in enumerate(variables)
            for module_vertex in variable
        )
    flat_kernel_0 = tuple(value % 2 for value in flatten_variables(kernel_0, columns))
    flat_kernel_1 = tuple(value % 2 for value in flatten_variables(kernel_1, columns))
    assert any(flat_kernel_0)
    assert any(flat_kernel_1)
    assert flat_kernel_0 != flat_kernel_1

    residuals = tuple(corrected_residual(variables) for variables in classes)
    kernel_words = tuple(schreier_word(residual) for residual in residuals)
    wedges = tuple(degree_two(word) for word in kernel_words)
    obstructions = tuple(degree_two_obstructions(value) for value in wedges)
    ranks = tuple(
        (prime, rank_mod(matrix_entries, len(rows), len(columns), prime))
        for prime in (2, 3, 5)
    )
    certificate = PeriodTwoDegreeTwoEscapeCertificate(
        local_matrix_shape=(len(rows), len(columns)),
        local_matrix_nonzero=len(matrix_entries),
        local_matrix_ranks=ranks,
        local_kernel_dimension=len(columns) - dict(ranks)[2],
        parity_classes=((0, 0), (1, 0), (0, 1), (1, 1)),
        degree_two_obstructions=obstructions,
        residual_lengths=tuple(len(residual) for residual in residuals),
        kernel_lengths=tuple(len(word) for word in kernel_words),
        escape_required=all(any(value) for value in obstructions),
    )
    assert certificate.local_kernel_dimension == 2
    assert certificate.escape_required
    return certificate


if __name__ == "__main__":
    print(period_two_degree_two_escape_certificate())
