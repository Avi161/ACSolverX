from __future__ import annotations

from dataclasses import dataclass

try:
    from experiments.stable_ac import depth4_period_two_degree_two_escape_certificate as escape
except ModuleNotFoundError:
    import depth4_period_two_degree_two_escape_certificate as escape


lift = escape.lift

REMOTE_SYZYGY = (
    (0, 1, "cT"),
    (0, -1, "cTT"),
    (0, 2, "cTTct"),
    (2, 2, ""),
    (2, 3, "cT"),
    (2, -2, "cTT"),
    (2, 1, "cTct"),
    (2, 2, "cTTct"),
    (3, 2, "TT"),
    (3, 1, "TTcT"),
    (3, 2, "TTct"),
    (3, -1, "TTcTT"),
    (3, 1, "TTcTct"),
    (3, 1, "TTcTTct"),
    (3, 2, "TTctcT"),
    (3, -1, "TTctcTcT"),
    (4, -3, "T"),
    (4, -1, "TcT"),
    (4, 1, "TcTT"),
    (4, -1, "TcTct"),
    (4, -1, "TcTTct"),
    (4, -2, "TctcT"),
    (4, 1, "TctcTcT"),
)


def permutation_inverse(value: tuple[int, ...]) -> tuple[int, ...]:
    result = [0] * len(value)
    for index, image in enumerate(value):
        result[image] = index
    return tuple(result)


def point_image(
    word: lift.Word,
    point: int,
    c_image: tuple[int, ...],
    t_image: tuple[int, ...],
) -> int:
    t_inverse = permutation_inverse(t_image)
    for letter in reversed(word):
        permutation = (
            c_image
            if abs(letter) == lift.C
            else t_image
            if letter == lift.T
            else t_inverse
        )
        point = permutation[point]
    return point


def finite_wedge_vector(
    value: escape.WedgeVector,
    c_image: tuple[int, ...],
    t_image: tuple[int, ...],
) -> tuple[int, ...]:
    size = len(c_image)
    pairs = tuple((left, right) for left in range(size) for right in range(left + 1, size))
    pair_index = {pair: index for index, pair in enumerate(pairs)}
    result = [0] * len(pairs)
    for (left, right), coefficient in value.items():
        left_point = point_image(left, 0, c_image, t_image)
        right_point = point_image(right, 0, c_image, t_image)
        if left_point == right_point:
            continue
        sign = 1
        if left_point > right_point:
            left_point, right_point = right_point, left_point
            sign = -1
        result[pair_index[left_point, right_point]] += sign * coefficient
    return tuple(result)


def operator_columns(
    operators: tuple[lift.GroupRing, ...],
    c_image: tuple[int, ...],
    t_image: tuple[int, ...],
) -> tuple[tuple[int, ...], ...]:
    size = len(c_image)
    pairs = tuple((left, right) for left in range(size) for right in range(left + 1, size))
    pair_index = {pair: index for index, pair in enumerate(pairs)}
    columns = []
    for operator in operators:
        for source_left, source_right in pairs:
            column = [0] * len(pairs)
            for group_element, coefficient in operator.items():
                target_left = point_image(group_element, source_left, c_image, t_image)
                target_right = point_image(group_element, source_right, c_image, t_image)
                if target_left == target_right:
                    continue
                sign = 1
                if target_left > target_right:
                    target_left, target_right = target_right, target_left
                    sign = -1
                column[pair_index[target_left, target_right]] += sign * coefficient
            columns.append(tuple(column))
    return tuple(columns)


def rank_mod_two(columns: tuple[tuple[int, ...], ...]) -> int:
    if not columns:
        return 0
    row_count = len(columns[0])
    rows = [
        [column[row] % 2 for column in columns]
        for row in range(row_count)
    ]
    rank = 0
    for column in range(len(columns)):
        pivot = next((row for row in range(rank, row_count) if rows[row][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for row in range(row_count):
            if row != rank and rows[row][column]:
                rows[row] = [left ^ right for left, right in zip(rows[row], rows[rank])]
        rank += 1
        if rank == row_count:
            break
    return rank


@dataclass(frozen=True)
class PeriodTwoRemoteSyzygyCertificate:
    support_entries: int
    coefficient_l1: int
    component_image_stats: tuple[tuple[int, int], ...]
    homogeneous_image: tuple[tuple[str, int], ...]
    outside_one_hop: tuple[tuple[int, str], ...]
    residual_length: int
    kernel_length: int
    degree_two_terms: int
    degree_two_coefficient_sum: int
    old_obstructions: tuple[int, int]
    four_point_action: tuple[tuple[int, ...], tuple[int, ...]]
    four_point_defect: tuple[int, ...]
    four_point_operator_rank: int
    four_point_augmented_rank: int
    four_point_obstruction: int


def period_two_remote_syzygy_certificate() -> PeriodTwoRemoteSyzygyCertificate:
    _, _, _, defect, operators = escape.recurrence_data()
    syzygy = escape.variables_from_entries(REMOTE_SYZYGY)
    component_images = tuple(
        lift.apply_operator(operator, variable)
        for operator, variable in zip(operators, syzygy)
    )
    homogeneous = lift.add_vectors(*component_images)
    base = escape.variables_from_entries(lift.CORRECTION)
    corrected = escape.add_variables(base, syzygy)
    assert not lift.add_vectors(defect, escape.correction_image(corrected, operators))

    rows, local_columns, _ = escape.local_columns(defect, operators)
    assert rows
    local_set = set(local_columns)
    outside = tuple(sorted(
        (
            (operator_index, lift.literal(module_vertex))
            for operator_index, variable in enumerate(syzygy)
            for module_vertex in variable
            if (operator_index, module_vertex) not in local_set
        ),
        key=lambda item: (item[0], len(item[1]), item[1]),
    ))

    residual = escape.corrected_residual(corrected)
    kernel_word = escape.schreier_word(residual)
    wedge = escape.degree_two(kernel_word)
    old_obstructions = escape.degree_two_obstructions(wedge)

    c_image = (0, 1, 3, 2)
    t_image = (1, 2, 0, 3)
    finite_defect = finite_wedge_vector(wedge, c_image, t_image)
    columns = operator_columns(operators, c_image, t_image)
    operator_rank = rank_mod_two(columns)
    augmented_rank = rank_mod_two((*columns, finite_defect))

    homogeneous_tuple = tuple(sorted(
        ((lift.literal(word), coefficient) for word, coefficient in homogeneous.items()),
        key=lambda item: (len(item[0]), item[0], item[1]),
    ))
    certificate = PeriodTwoRemoteSyzygyCertificate(
        support_entries=sum(len(variable) for variable in syzygy),
        coefficient_l1=sum(
            abs(coefficient)
            for variable in syzygy
            for coefficient in variable.values()
        ),
        component_image_stats=tuple(
            (len(value), sum(abs(coefficient) for coefficient in value.values()))
            for value in component_images
        ),
        homogeneous_image=homogeneous_tuple,
        outside_one_hop=outside,
        residual_length=len(residual),
        kernel_length=len(kernel_word),
        degree_two_terms=len(wedge),
        degree_two_coefficient_sum=sum(wedge.values()),
        old_obstructions=old_obstructions,
        four_point_action=(c_image, t_image),
        four_point_defect=finite_defect,
        four_point_operator_rank=operator_rank,
        four_point_augmented_rank=augmented_rank,
        four_point_obstruction=sum(finite_defect) % 2,
    )
    assert certificate.homogeneous_image == ()
    assert certificate.old_obstructions == (0, 0)
    assert certificate.four_point_augmented_rank > certificate.four_point_operator_rank
    return certificate


if __name__ == "__main__":
    print(period_two_remote_syzygy_certificate())
