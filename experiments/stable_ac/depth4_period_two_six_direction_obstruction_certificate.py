from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations, product

try:
    from experiments.stable_ac import depth4_period_two_cyclic_degree_two_obstruction_certificate as cyclic
    from experiments.stable_ac import depth4_period_two_degree_two_escape_certificate as escape
    from experiments.stable_ac import depth4_period_two_five_direction_obstruction_certificate as five
    from experiments.stable_ac import depth4_period_two_mod3_escape_obstruction_certificate as mod3
    from experiments.stable_ac import depth4_period_two_phi4_escape_certificate as phi4
    from experiments.stable_ac import depth4_period_two_remote_syzygy_certificate as remote
except ModuleNotFoundError:
    import depth4_period_two_cyclic_degree_two_obstruction_certificate as cyclic
    import depth4_period_two_degree_two_escape_certificate as escape
    import depth4_period_two_five_direction_obstruction_certificate as five
    import depth4_period_two_mod3_escape_obstruction_certificate as mod3
    import depth4_period_two_phi4_escape_certificate as phi4
    import depth4_period_two_remote_syzygy_certificate as remote


lift = escape.lift


SIXTH_SYZYGY = (
    (1, 1, "tcTTT"),
    (2, -1, "cT"),
    (2, 1, "cTT"),
    (2, 1, "tcTTT"),
    (2, -1, "cttcTTT"),
    (3, -1, "TTcT"),
    (3, 1, "TTctcTcT"),
    (3, -1, "TTcttcTTT"),
    (3, 1, "TTctcTctctcTTT"),
    (3, -1, "TTctcTctttcTTT"),
    (4, 1, "TcT"),
    (4, 1, "tcTTT"),
    (4, -1, "ctcTTT"),
    (4, 1, "ttcTTT"),
    (4, -1, "TctcTcT"),
    (4, 1, "TcttcTTT"),
    (4, -1, "TctcTctctcTTT"),
    (4, 1, "TctcTctttcTTT"),
)


FOREST_PATHS = (
    ("tttcTTT", "aaBgA", "ctcTctctcTTT"),
    ("ctcTctttcTTT", "aGbaGBgAbaGA", "tctcTTT"),
)


TWO_POINT_ACTION = (
    (0, 1),
    (1, 0),
)


def scale_variables(value: escape.ModuleVariables, coefficient: int):
    return tuple(lift.scale_vector(variable, coefficient) for variable in value)


def reconstruct_from_forest_paths(
    operators: tuple[lift.GroupRing, ...],
) -> escape.ModuleVariables:
    generators = phi4.forest_generators(operators)
    generators.update({
        name.lower(): lift.quotient_inverse(word)
        for name, word in tuple(generators.items())
    })
    variables: list[dict[lift.Word, int]] = [defaultdict(int) for _ in range(5)]
    variables[1][lift.parse_quotient("tcTTT")] = 1
    for start_label, path, end_label in FOREST_PATHS:
        current = lift.parse_quotient(start_label)
        for name in path:
            target = escape.act(generators[name], current)
            if name == "A":
                variables[4][current] -= 1
            elif name == "a":
                variables[4][target] += 1
            elif name == "B":
                variables[2][current] += 1
            elif name == "b":
                variables[2][target] -= 1
            elif name == "G":
                variables[3][lift.quotient_multiply((-lift.T,), current)] -= 1
            elif name == "g":
                variables[3][lift.quotient_multiply((-lift.T,), target)] += 1
            current = target
        assert current == lift.parse_quotient(end_label)
    return tuple(lift.clean_vector(variable) for variable in variables)


def known_directions(base: escape.ModuleVariables):
    alternate_10 = escape.variables_from_entries(escape.ALTERNATE_10)
    alternate_01 = escape.variables_from_entries(escape.ALTERNATE_01)
    return (
        escape.subtract_variables(alternate_10, base),
        escape.subtract_variables(alternate_01, base),
        escape.variables_from_entries(remote.REMOTE_SYZYGY),
        escape.variables_from_entries(phi4.PHI4_ESCAPE_SYZYGY),
        escape.variables_from_entries(mod3.MOD3_ESCAPE_SYZYGY),
        escape.variables_from_entries(SIXTH_SYZYGY),
    )


def variables_for(base, directions, coefficients):
    values = [base]
    values.extend(
        scale_variables(direction, coefficient)
        for coefficient, direction in zip(coefficients, directions)
        if coefficient
    )
    return escape.add_variables(*values)


def wedge_for(variables: escape.ModuleVariables) -> escape.WedgeVector:
    residual = escape.corrected_residual(variables)
    return escape.degree_two(escape.schreier_word(residual))


def six_mod_two_bits(value: escape.WedgeVector) -> tuple[int, ...]:
    previous = five.five_mod_two_bits(value)
    two_point = remote.finite_wedge_vector(value, *TWO_POINT_ACTION)
    return (*previous, sum(two_point) % 2)


def direction_rank(directions: tuple[escape.ModuleVariables, ...]) -> int:
    rows = sorted({
        (operator_index, module_vertex)
        for direction in directions
        for operator_index, variable in enumerate(direction)
        for module_vertex in variable
    })
    columns = tuple(
        tuple(
            direction[operator_index].get(module_vertex, 0)
            for operator_index, module_vertex in rows
        )
        for direction in directions
    )
    return remote.rank_mod_two(columns)


def basis_vector(size: int, index: int, coefficient: int = 1):
    return tuple(coefficient if position == index else 0 for position in range(size))


def add_coefficients(*values):
    return tuple(sum(entries) for entries in zip(*values))


def quadratic_model(base, directions):
    size = len(directions)

    def bits(coefficients):
        return six_mod_two_bits(wedge_for(variables_for(base, directions, coefficients)))

    constant = bits((0,) * size)
    linear = []
    diagonal = []
    for index in range(size):
        at_one = bits(basis_vector(size, index))
        at_two = bits(basis_vector(size, index, 2))
        linear.append(tuple(left ^ right for left, right in zip(at_one, constant)))
        diagonal.append(tuple(left ^ right for left, right in zip(at_two, constant)))
    cross = {}
    for left, right in combinations(range(size), 2):
        point = add_coefficients(basis_vector(size, left), basis_vector(size, right))
        value = bits(point)
        cross[left, right] = tuple(
            entry ^ constant_entry ^ left_entry ^ right_entry
            for entry, constant_entry, left_entry, right_entry in zip(
                value,
                constant,
                linear[left],
                linear[right],
            )
        )
    return constant, tuple(linear), tuple(diagonal), cross


def evaluate_model(coefficients, model):
    constant, linear, diagonal, cross = model
    value = list(constant)
    for index, coefficient in enumerate(coefficients):
        if coefficient % 2:
            value = [left ^ right for left, right in zip(value, linear[index])]
        if (coefficient * (coefficient - 1) // 2) % 2:
            value = [left ^ right for left, right in zip(value, diagonal[index])]
    for (left_index, right_index), entries in cross.items():
        if (coefficients[left_index] * coefficients[right_index]) % 2:
            value = [left ^ right for left, right in zip(value, entries)]
    return tuple(value)


@dataclass(frozen=True)
class PeriodTwoSixDirectionObstructionCertificate:
    forest_paths: tuple[tuple[str, str, str], ...]
    syzygy_entries: int
    syzygy_l1: int
    component_image_stats: tuple[tuple[int, int], ...]
    homogeneous_image: tuple[tuple[str, int], ...]
    fifth_and_sixth_direction_ranks_mod_two: tuple[int, int]
    sixth_residual_length: int
    sixth_kernel_length: int
    sixth_degree_two_terms: int
    sixth_degree_two_l1: int
    sixth_known_mod_two_bits: tuple[int, ...]
    sixth_cyclic_signed_mod_three: int
    combination_coefficients: tuple[int, ...]
    combination_entries: int
    combination_l1: int
    combination_residual_length: int
    combination_kernel_length: int
    combination_degree_two_terms: int
    combination_degree_two_l1: int
    combination_known_mod_two_bits: tuple[int, ...]
    combination_cyclic_signed_mod_three: int
    two_point_action: tuple[tuple[int, ...], tuple[int, ...]]
    two_point_defect: tuple[int, ...]
    two_point_operator_rank: int
    two_point_augmented_rank: int
    quadratic_model_replays: int
    quadratic_validation_replays: int
    coefficient_class_count: int
    undetected_classes: tuple[tuple[int, ...], ...]
    coefficient_table_sha256: str
    known_integer_span_obstructed: bool


def period_two_six_direction_obstruction_certificate(
) -> PeriodTwoSixDirectionObstructionCertificate:
    _, _, _, defect, operators = escape.recurrence_data()
    syzygy = escape.variables_from_entries(SIXTH_SYZYGY)
    assert syzygy == reconstruct_from_forest_paths(operators)
    component_images = tuple(
        lift.apply_operator(operator, variable)
        for operator, variable in zip(operators, syzygy)
    )
    homogeneous = lift.add_vectors(*component_images)

    base = escape.variables_from_entries(lift.CORRECTION)
    directions = known_directions(base)
    direction_ranks = (direction_rank(directions[:-1]), direction_rank(directions))

    sixth_variables = escape.add_variables(base, syzygy)
    assert not lift.add_vectors(defect, escape.correction_image(sixth_variables, operators))
    sixth_residual = escape.corrected_residual(sixth_variables)
    sixth_kernel = escape.schreier_word(sixth_residual)
    sixth_wedge = escape.degree_two(sixth_kernel)
    sixth_cyclic = remote.finite_wedge_vector(sixth_wedge, *cyclic.CYCLIC_ACTION)

    combination_coefficients = (0, 0, 0, 4, -4, -3)
    combination = variables_for(base, directions, combination_coefficients)
    assert not lift.add_vectors(defect, escape.correction_image(combination, operators))
    combination_residual = escape.corrected_residual(combination)
    combination_kernel = escape.schreier_word(combination_residual)
    combination_wedge = escape.degree_two(combination_kernel)
    combination_cyclic = remote.finite_wedge_vector(
        combination_wedge,
        *cyclic.CYCLIC_ACTION,
    )
    two_point_defect = remote.finite_wedge_vector(combination_wedge, *TWO_POINT_ACTION)
    two_point_columns = remote.operator_columns(operators, *TWO_POINT_ACTION)
    two_point_rank = remote.rank_mod_two(two_point_columns)
    two_point_augmented_rank = remote.rank_mod_two((*two_point_columns, two_point_defect))

    model = quadratic_model(base, directions)
    size = len(directions)
    validation_points = []
    validation_points.extend(basis_vector(size, index, 3) for index in range(size))
    for left, right in combinations(range(size), 2):
        validation_points.append(add_coefficients(
            basis_vector(size, left, 3),
            basis_vector(size, right),
        ))
    for point in validation_points:
        direct = six_mod_two_bits(wedge_for(variables_for(base, directions, point)))
        assert direct == evaluate_model(point, model)

    table = []
    for coefficients in product(range(4), repeat=size):
        table.append((coefficients, evaluate_model(coefficients, model)))
    undetected = tuple(coefficients for coefficients, bits in table if not any(bits))
    record = "\n".join(
        f"{''.join(map(str, coefficients))}:{''.join(map(str, bits))}"
        for coefficients, bits in table
    )
    homogeneous_tuple = tuple(sorted(
        ((lift.literal(word), coefficient) for word, coefficient in homogeneous.items()),
        key=lambda item: (len(item[0]), item[0], item[1]),
    ))

    certificate = PeriodTwoSixDirectionObstructionCertificate(
        forest_paths=FOREST_PATHS,
        syzygy_entries=sum(len(variable) for variable in syzygy),
        syzygy_l1=sum(
            abs(coefficient)
            for variable in syzygy
            for coefficient in variable.values()
        ),
        component_image_stats=tuple(
            (len(value), sum(abs(coefficient) for coefficient in value.values()))
            for value in component_images
        ),
        homogeneous_image=homogeneous_tuple,
        fifth_and_sixth_direction_ranks_mod_two=direction_ranks,
        sixth_residual_length=len(sixth_residual),
        sixth_kernel_length=len(sixth_kernel),
        sixth_degree_two_terms=len(sixth_wedge),
        sixth_degree_two_l1=sum(abs(coefficient) for coefficient in sixth_wedge.values()),
        sixth_known_mod_two_bits=five.five_mod_two_bits(sixth_wedge),
        sixth_cyclic_signed_mod_three=(
            sixth_cyclic[0] - sixth_cyclic[1] + sixth_cyclic[2]
        ) % 3,
        combination_coefficients=combination_coefficients,
        combination_entries=sum(len(variable) for variable in combination),
        combination_l1=sum(
            abs(coefficient)
            for variable in combination
            for coefficient in variable.values()
        ),
        combination_residual_length=len(combination_residual),
        combination_kernel_length=len(combination_kernel),
        combination_degree_two_terms=len(combination_wedge),
        combination_degree_two_l1=sum(
            abs(coefficient) for coefficient in combination_wedge.values()
        ),
        combination_known_mod_two_bits=five.five_mod_two_bits(combination_wedge),
        combination_cyclic_signed_mod_three=(
            combination_cyclic[0] - combination_cyclic[1] + combination_cyclic[2]
        ) % 3,
        two_point_action=TWO_POINT_ACTION,
        two_point_defect=two_point_defect,
        two_point_operator_rank=two_point_rank,
        two_point_augmented_rank=two_point_augmented_rank,
        quadratic_model_replays=1 + 2 * size + size * (size - 1) // 2,
        quadratic_validation_replays=len(validation_points),
        coefficient_class_count=len(table),
        undetected_classes=undetected,
        coefficient_table_sha256=sha256(record.encode()).hexdigest(),
        known_integer_span_obstructed=(direction_ranks == (5, 6) and not undetected),
    )
    assert certificate.homogeneous_image == ()
    assert certificate.sixth_known_mod_two_bits == (0, 0, 0, 0, 0)
    assert certificate.sixth_cyclic_signed_mod_three == 2
    assert certificate.combination_known_mod_two_bits == (0, 0, 0, 0, 0)
    assert certificate.combination_cyclic_signed_mod_three == 0
    assert certificate.two_point_augmented_rank > certificate.two_point_operator_rank
    assert certificate.known_integer_span_obstructed
    return certificate


if __name__ == "__main__":
    print(period_two_six_direction_obstruction_certificate())
