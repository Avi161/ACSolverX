from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
from itertools import combinations, product

try:
    from experiments.stable_ac import depth4_period_two_degree_two_escape_certificate as escape
    from experiments.stable_ac import depth4_period_two_eight_direction_obstruction_certificate as eight
    from experiments.stable_ac import depth4_period_two_nine_direction_obstruction_certificate as nine
    from experiments.stable_ac import depth4_period_two_phi4_escape_certificate as phi4
    from experiments.stable_ac import depth4_period_two_remote_syzygy_certificate as remote
    from experiments.stable_ac import depth4_period_two_seven_direction_obstruction_certificate as seven
    from experiments.stable_ac import depth4_period_two_six_direction_obstruction_certificate as six
    from experiments.stable_ac import depth4_period_two_ten_direction_obstruction_certificate as ten
except ModuleNotFoundError:
    import depth4_period_two_degree_two_escape_certificate as escape
    import depth4_period_two_eight_direction_obstruction_certificate as eight
    import depth4_period_two_nine_direction_obstruction_certificate as nine
    import depth4_period_two_phi4_escape_certificate as phi4
    import depth4_period_two_remote_syzygy_certificate as remote
    import depth4_period_two_seven_direction_obstruction_certificate as seven
    import depth4_period_two_six_direction_obstruction_certificate as six
    import depth4_period_two_ten_direction_obstruction_certificate as ten


lift = escape.lift
SOURCE = ((1, "TTcttt"), (1, "cTcTct"))
FOREST_PATHS = (
    ("ctcTTTctcTct", "gAB", "ctcTTct"),
    ("cTTcttcTTcttt", "BgAbgaaGaG", "ctcTcTTct"),
    ("ctcTTTcttcTTcttt", "gAB", "ctcTctcTTcttt"),
    ("ctcTTTTcttcTTcttt", "gABgAbgaaBgAgAgaB", "ctcTcTctcTTcttt"),
    ("cTTctcTct", "BgAbGb", "cTct"),
    ("ctcTTTTctcTct", "gABgAbAgABaGbA", "tcTTcttt"),
)
NEW_ACTION = ((0, 2, 1, 3), (1, 0, 3, 2))
NEW_COVECTORS = (
    (0, 0, 1, 1, 0, 0),
    (1, 1, 0, 0, 1, 1),
)


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
    previous = ten.obstruction_bits(value)
    vector = remote.finite_wedge_vector(value, *NEW_ACTION)
    added = tuple(
        sum(left * right for left, right in zip(covector, vector)) % 2
        for covector in NEW_COVECTORS
    )
    return (*previous, *added)


def quadratic_model(base, directions):
    size = len(directions)

    def bits(coefficients):
        return obstruction_bits(six.wedge_for(six.variables_for(
            base, directions, coefficients,
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
            six.basis_vector(size, left), six.basis_vector(size, right),
        )
        value = bits(point)
        cross[left, right] = tuple(
            entry ^ base_entry ^ left_entry ^ right_entry
            for entry, base_entry, left_entry, right_entry in zip(
                value, constant, linear[left], linear[right],
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
class PeriodTwoElevenDirectionObstructionCertificate:
    syzygy_entries: int
    syzygy_l1: int
    component_image_stats: tuple[tuple[int, int], ...]
    homogeneous_image: tuple[tuple[str, int], ...]
    tenth_and_eleventh_direction_ranks_mod_two: tuple[int, int]
    eleventh_residual_length: int
    eleventh_kernel_length: int
    eleventh_degree_two_terms: int
    eleventh_degree_two_l1: int
    eleventh_prior_mod_two_bits: tuple[int, ...]
    new_action: tuple[tuple[int, ...], tuple[int, ...]]
    new_covectors: tuple[tuple[int, ...], ...]
    new_defect: tuple[int, ...]
    new_values_mod_two: tuple[int, ...]
    new_operator_rank: int
    new_covector_rank: int
    new_augmented_rank: int
    quadratic_model_replays: int
    quadratic_validation_replays: int
    coefficient_class_count: int
    undetected_classes: tuple[tuple[int, ...], ...]
    coefficient_table_sha256: str
    known_integer_span_obstructed: bool


@lru_cache(maxsize=1)
def period_two_eleven_direction_obstruction_certificate(
) -> PeriodTwoElevenDirectionObstructionCertificate:
    _, _, _, defect, operators = escape.recurrence_data()
    syzygy = reconstruct_from_forest_paths(operators)
    component_images = tuple(
        lift.apply_operator(operator, variable)
        for operator, variable in zip(operators, syzygy)
    )
    homogeneous = lift.add_vectors(*component_images)
    base = escape.variables_from_entries(lift.CORRECTION)
    directions = (
        *six.known_directions(base),
        seven.reconstruct_from_forest_paths(operators),
        eight.reconstruct_from_forest_paths(operators),
        nine.reconstruct_from_forest_paths(operators),
        ten.reconstruct_from_forest_paths(operators),
        syzygy,
    )
    direction_ranks = (
        six.direction_rank(directions[:-1]), six.direction_rank(directions),
    )
    variables = escape.add_variables(base, syzygy)
    assert not lift.add_vectors(defect, escape.correction_image(variables, operators))
    residual = escape.corrected_residual(variables)
    kernel = escape.schreier_word(residual)
    wedge = escape.degree_two(kernel)

    columns = remote.operator_columns(operators, *NEW_ACTION)
    assert all(
        sum(left * right for left, right in zip(covector, column)) % 2 == 0
        for covector in NEW_COVECTORS for column in columns
    )
    projected_defect = remote.finite_wedge_vector(wedge, *NEW_ACTION)
    projected_values = tuple(
        sum(left * right for left, right in zip(covector, projected_defect)) % 2
        for covector in NEW_COVECTORS
    )
    operator_rank = remote.rank_mod_two(columns)
    augmented_rank = remote.rank_mod_two((*columns, projected_defect))

    model = quadratic_model(base, directions)
    size = len(directions)
    validations = [six.basis_vector(size, index, 3) for index in range(size)]
    validations.extend(
        six.add_coefficients(
            six.basis_vector(size, left, 3), six.basis_vector(size, right),
        )
        for left, right in combinations(range(size), 2)
    )
    for point in validations:
        direct = obstruction_bits(six.wedge_for(six.variables_for(
            base, directions, point,
        )))
        assert direct == evaluate_model(point, model)

    digest = sha256()
    undetected = []
    count = 0
    for coefficients in product(range(4), repeat=size):
        bits = evaluate_model(coefficients, model)
        digest.update(bytes((*coefficients, *bits)))
        count += 1
        if not any(bits):
            undetected.append(coefficients)

    homogeneous_tuple = tuple(sorted(
        ((lift.literal(word), coefficient) for word, coefficient in homogeneous.items()),
        key=lambda item: (len(item[0]), item[0], item[1]),
    ))
    certificate = PeriodTwoElevenDirectionObstructionCertificate(
        syzygy_entries=sum(len(variable) for variable in syzygy),
        syzygy_l1=sum(abs(c) for variable in syzygy for c in variable.values()),
        component_image_stats=tuple(
            (len(value), sum(abs(c) for c in value.values()))
            for value in component_images
        ),
        homogeneous_image=homogeneous_tuple,
        tenth_and_eleventh_direction_ranks_mod_two=direction_ranks,
        eleventh_residual_length=len(residual),
        eleventh_kernel_length=len(kernel),
        eleventh_degree_two_terms=len(wedge),
        eleventh_degree_two_l1=sum(abs(c) for c in wedge.values()),
        eleventh_prior_mod_two_bits=ten.obstruction_bits(wedge),
        new_action=NEW_ACTION,
        new_covectors=NEW_COVECTORS,
        new_defect=projected_defect,
        new_values_mod_two=projected_values,
        new_operator_rank=operator_rank,
        new_covector_rank=remote.rank_mod_two(NEW_COVECTORS),
        new_augmented_rank=augmented_rank,
        quadratic_model_replays=1 + 2 * size + size * (size - 1) // 2,
        quadratic_validation_replays=len(validations),
        coefficient_class_count=count,
        undetected_classes=tuple(undetected),
        coefficient_table_sha256=digest.hexdigest(),
        known_integer_span_obstructed=(
            direction_ranks == (10, 11) and not homogeneous_tuple and not undetected
        ),
    )
    assert certificate.eleventh_prior_mod_two_bits == (0,) * 13
    assert certificate.new_values_mod_two == (1, 0)
    assert certificate.new_augmented_rank > operator_rank
    assert certificate.known_integer_span_obstructed
    return certificate


if __name__ == "__main__":
    print(period_two_eleven_direction_obstruction_certificate())
