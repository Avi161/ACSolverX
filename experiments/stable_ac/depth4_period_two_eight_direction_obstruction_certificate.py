from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations, product

try:
    from experiments.stable_ac import depth4_period_two_degree_two_escape_certificate as escape
    from experiments.stable_ac import depth4_period_two_phi4_escape_certificate as phi4
    from experiments.stable_ac import depth4_period_two_remote_syzygy_certificate as remote
    from experiments.stable_ac import depth4_period_two_seven_direction_obstruction_certificate as seven
    from experiments.stable_ac import depth4_period_two_six_direction_obstruction_certificate as six
except ModuleNotFoundError:
    import depth4_period_two_degree_two_escape_certificate as escape
    import depth4_period_two_phi4_escape_certificate as phi4
    import depth4_period_two_remote_syzygy_certificate as remote
    import depth4_period_two_seven_direction_obstruction_certificate as seven
    import depth4_period_two_six_direction_obstruction_certificate as six


lift = escape.lift


SOURCE = (
    (1, "T"),
    (1, "TTct"),
)


FOREST_PATHS = (
    ("cTTcttcTTct", "BgAbgBaGbA", "tcTTct"),
    ("ctcTTTcttcT", "gAB", "ctcTctcT"),
    ("ctcTTTTcttcTTct", "gABgAbgaB", "ctcTcTctcT"),
    ("cTTcttcT", "BgAbaGbA", "tcT"),
    ("ctcTTTTcttcT", "gABgAbgaBgA", "ctcTctcTTct"),
    ("ctcTTTcttcTTct", "gABaG", "ctcTcTctcTTct"),
)


NEW_FOUR_POINT_ACTION = (
    (0, 2, 1, 3),
    (1, 3, 2, 0),
)


NEW_FOUR_POINT_COVECTOR = (1, 1, 1, 1, 1, 1)


def reconstruct_from_forest_paths(
    operators: tuple[lift.GroupRing, ...],
) -> escape.ModuleVariables:
    generators = phi4.forest_generators(operators)
    generators.update({
        name.lower(): lift.quotient_inverse(word)
        for name, word in tuple(generators.items())
    })
    variables: list[dict[lift.Word, int]] = [defaultdict(int) for _ in range(5)]
    for coefficient, label in SOURCE:
        variables[0][lift.parse_quotient(label)] += coefficient
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


def obstruction_bits(value: escape.WedgeVector) -> tuple[int, ...]:
    previous = seven.obstruction_bits(value)
    vector = remote.finite_wedge_vector(value, *NEW_FOUR_POINT_ACTION)
    new_bit = sum(
        left * right
        for left, right in zip(NEW_FOUR_POINT_COVECTOR, vector)
    ) % 2
    return (*previous, new_bit)


def quadratic_model(base, directions):
    size = len(directions)

    def bits(coefficients):
        return obstruction_bits(six.wedge_for(six.variables_for(
            base,
            directions,
            coefficients,
        )))

    constant = bits((0,) * size)
    linear = []
    diagonal = []
    for index in range(size):
        at_one = bits(six.basis_vector(size, index))
        at_two = bits(six.basis_vector(size, index, 2))
        linear.append(tuple(left ^ right for left, right in zip(at_one, constant)))
        diagonal.append(tuple(left ^ right for left, right in zip(at_two, constant)))
    cross = {}
    for left, right in combinations(range(size), 2):
        point = six.add_coefficients(
            six.basis_vector(size, left),
            six.basis_vector(size, right),
        )
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
    for (left, right), entries in cross.items():
        if (coefficients[left] * coefficients[right]) % 2:
            value = [old ^ entry for old, entry in zip(value, entries)]
    return tuple(value)


@dataclass(frozen=True)
class PeriodTwoEightDirectionObstructionCertificate:
    forest_paths: tuple[tuple[str, str, str], ...]
    syzygy_entries: int
    syzygy_l1: int
    component_image_stats: tuple[tuple[int, int], ...]
    homogeneous_image: tuple[tuple[str, int], ...]
    seventh_and_eighth_direction_ranks_mod_two: tuple[int, int]
    eighth_residual_length: int
    eighth_kernel_length: int
    eighth_degree_two_terms: int
    eighth_degree_two_l1: int
    eighth_prior_mod_two_bits: tuple[int, ...]
    new_four_point_action: tuple[tuple[int, ...], tuple[int, ...]]
    new_four_point_covector: tuple[int, ...]
    new_four_point_defect: tuple[int, ...]
    new_four_point_value_mod_two: int
    new_four_point_operator_rank: int
    new_four_point_augmented_rank: int
    quadratic_model_replays: int
    quadratic_validation_replays: int
    coefficient_class_count: int
    undetected_classes: tuple[tuple[int, ...], ...]
    coefficient_table_sha256: str
    known_integer_span_obstructed: bool


def period_two_eight_direction_obstruction_certificate(
) -> PeriodTwoEightDirectionObstructionCertificate:
    _, _, _, defect, operators = escape.recurrence_data()
    syzygy = reconstruct_from_forest_paths(operators)
    component_images = tuple(
        lift.apply_operator(operator, variable)
        for operator, variable in zip(operators, syzygy)
    )
    homogeneous = lift.add_vectors(*component_images)

    base = escape.variables_from_entries(lift.CORRECTION)
    seventh_direction = seven.reconstruct_from_forest_paths(operators)
    directions = (*six.known_directions(base), seventh_direction, syzygy)
    direction_ranks = (
        six.direction_rank(directions[:-1]),
        six.direction_rank(directions),
    )

    eighth_variables = escape.add_variables(base, syzygy)
    assert not lift.add_vectors(
        defect,
        escape.correction_image(eighth_variables, operators),
    )
    eighth_residual = escape.corrected_residual(eighth_variables)
    eighth_kernel = escape.schreier_word(eighth_residual)
    eighth_wedge = escape.degree_two(eighth_kernel)

    new_columns = remote.operator_columns(operators, *NEW_FOUR_POINT_ACTION)
    assert all(
        sum(
            left * right
            for left, right in zip(NEW_FOUR_POINT_COVECTOR, column)
        ) % 2 == 0
        for column in new_columns
    )
    new_defect = remote.finite_wedge_vector(eighth_wedge, *NEW_FOUR_POINT_ACTION)
    new_value = sum(
        left * right
        for left, right in zip(NEW_FOUR_POINT_COVECTOR, new_defect)
    ) % 2
    new_rank = remote.rank_mod_two(new_columns)
    new_augmented_rank = remote.rank_mod_two((*new_columns, new_defect))

    model = quadratic_model(base, directions)
    size = len(directions)
    validation_points = []
    validation_points.extend(six.basis_vector(size, index, 3) for index in range(size))
    for left, right in combinations(range(size), 2):
        validation_points.append(six.add_coefficients(
            six.basis_vector(size, left, 3),
            six.basis_vector(size, right),
        ))
    for point in validation_points:
        direct = obstruction_bits(six.wedge_for(six.variables_for(
            base,
            directions,
            point,
        )))
        assert direct == evaluate_model(point, model)

    digest = sha256()
    undetected = []
    coefficient_class_count = 0
    for coefficients in product(range(4), repeat=size):
        bits = evaluate_model(coefficients, model)
        digest.update(bytes((*coefficients, *bits)))
        coefficient_class_count += 1
        if not any(bits):
            undetected.append(coefficients)

    homogeneous_tuple = tuple(sorted(
        ((lift.literal(word), coefficient) for word, coefficient in homogeneous.items()),
        key=lambda item: (len(item[0]), item[0], item[1]),
    ))
    certificate = PeriodTwoEightDirectionObstructionCertificate(
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
        seventh_and_eighth_direction_ranks_mod_two=direction_ranks,
        eighth_residual_length=len(eighth_residual),
        eighth_kernel_length=len(eighth_kernel),
        eighth_degree_two_terms=len(eighth_wedge),
        eighth_degree_two_l1=sum(
            abs(coefficient) for coefficient in eighth_wedge.values()
        ),
        eighth_prior_mod_two_bits=seven.obstruction_bits(eighth_wedge),
        new_four_point_action=NEW_FOUR_POINT_ACTION,
        new_four_point_covector=NEW_FOUR_POINT_COVECTOR,
        new_four_point_defect=new_defect,
        new_four_point_value_mod_two=new_value,
        new_four_point_operator_rank=new_rank,
        new_four_point_augmented_rank=new_augmented_rank,
        quadratic_model_replays=1 + 2 * size + size * (size - 1) // 2,
        quadratic_validation_replays=len(validation_points),
        coefficient_class_count=coefficient_class_count,
        undetected_classes=tuple(undetected),
        coefficient_table_sha256=digest.hexdigest(),
        known_integer_span_obstructed=(
            direction_ranks == (7, 8)
            and not homogeneous_tuple
            and not undetected
        ),
    )
    assert certificate.homogeneous_image == ()
    assert certificate.eighth_prior_mod_two_bits == (0,) * 9
    assert certificate.new_four_point_value_mod_two == 1
    assert certificate.new_four_point_augmented_rank > new_rank
    assert certificate.known_integer_span_obstructed
    return certificate


if __name__ == "__main__":
    print(period_two_eight_direction_obstruction_certificate())
