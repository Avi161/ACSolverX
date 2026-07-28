from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from itertools import product

try:
    from experiments.stable_ac import depth4_period_two_cyclic_degree_two_obstruction_certificate as cyclic
    from experiments.stable_ac import depth4_period_two_degree_two_escape_certificate as escape
    from experiments.stable_ac import depth4_period_two_mod3_escape_obstruction_certificate as mod3
    from experiments.stable_ac import depth4_period_two_phi4_escape_certificate as phi4
    from experiments.stable_ac import depth4_period_two_remote_syzygy_certificate as remote
except ModuleNotFoundError:
    import depth4_period_two_cyclic_degree_two_obstruction_certificate as cyclic
    import depth4_period_two_degree_two_escape_certificate as escape
    import depth4_period_two_mod3_escape_obstruction_certificate as mod3
    import depth4_period_two_phi4_escape_certificate as phi4
    import depth4_period_two_remote_syzygy_certificate as remote


lift = escape.lift


NEW_THREE_POINT_ACTION = (
    (0, 2, 1),
    (1, 0, 2),
)


def scale_variables(value: escape.ModuleVariables, coefficient: int):
    return tuple(lift.scale_vector(variable, coefficient) for variable in value)


def known_directions(base: escape.ModuleVariables):
    alternate_10 = escape.variables_from_entries(escape.ALTERNATE_10)
    alternate_01 = escape.variables_from_entries(escape.ALTERNATE_01)
    return (
        escape.subtract_variables(alternate_10, base),
        escape.subtract_variables(alternate_01, base),
        escape.variables_from_entries(remote.REMOTE_SYZYGY),
        escape.variables_from_entries(phi4.PHI4_ESCAPE_SYZYGY),
        escape.variables_from_entries(mod3.MOD3_ESCAPE_SYZYGY),
    )


def variables_for(
    base: escape.ModuleVariables,
    directions: tuple[escape.ModuleVariables, ...],
    coefficients: tuple[int, ...],
) -> escape.ModuleVariables:
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


def five_mod_two_bits(value: escape.WedgeVector) -> tuple[int, ...]:
    previous = cyclic.four_obstructions(value)
    new_vector = remote.finite_wedge_vector(value, *NEW_THREE_POINT_ACTION)
    return (*previous, sum(new_vector) % 2)


@dataclass(frozen=True)
class PeriodTwoFiveDirectionObstructionCertificate:
    combination_coefficients: tuple[int, ...]
    combination_entries: int
    combination_l1: int
    residual_length: int
    kernel_length: int
    relation_module_terms: int
    degree_two_terms: int
    degree_two_l1: int
    full_wedge_sum: int
    three_point_defect: tuple[int, ...]
    four_point_defect: tuple[int, ...]
    cyclic_defect: tuple[int, ...]
    cyclic_signed_mod_three: int
    new_three_point_action: tuple[tuple[int, ...], tuple[int, ...]]
    new_three_point_defect: tuple[int, ...]
    new_obstruction_mod_two: int
    operator_rank_mod_two: int
    augmented_rank_mod_two: int
    known_direction_rank_mod_two: int
    known_coefficient_modulus: int
    known_coefficient_class_count: int
    known_coefficient_undetected: tuple[tuple[int, ...], ...]
    known_coefficient_table_sha256: str
    known_integer_span_obstructed: bool


def period_two_five_direction_obstruction_certificate(
) -> PeriodTwoFiveDirectionObstructionCertificate:
    _, _, _, defect, operators = escape.recurrence_data()
    base = escape.variables_from_entries(lift.CORRECTION)
    directions = known_directions(base)
    combination_coefficients = (0, 0, 0, 2, -1)
    combination = variables_for(base, directions, combination_coefficients)
    assert not lift.add_vectors(defect, escape.correction_image(combination, operators))

    residual = escape.corrected_residual(combination)
    relation_module = lift.relation_module(residual)
    kernel_word = escape.schreier_word(residual)
    wedge = escape.degree_two(kernel_word)
    three_point = remote.finite_wedge_vector(
        wedge,
        (0, 2, 1),
        (1, 2, 0),
    )
    four_point = remote.finite_wedge_vector(
        wedge,
        *remote.period_two_remote_syzygy_certificate().four_point_action,
    )
    cyclic_defect = remote.finite_wedge_vector(wedge, *cyclic.CYCLIC_ACTION)
    cyclic_signed_mod_three = (
        cyclic_defect[0] - cyclic_defect[1] + cyclic_defect[2]
    ) % 3
    new_defect = remote.finite_wedge_vector(wedge, *NEW_THREE_POINT_ACTION)
    columns = remote.operator_columns(operators, *NEW_THREE_POINT_ACTION)
    operator_rank = remote.rank_mod_two(columns)
    augmented_rank = remote.rank_mod_two((*columns, new_defect))

    direction_rows = sorted({
        (operator_index, module_vertex)
        for direction in directions
        for operator_index, variable in enumerate(direction)
        for module_vertex in variable
    })
    direction_columns = tuple(
        tuple(
            direction[operator_index].get(module_vertex, 0)
            for operator_index, module_vertex in direction_rows
        )
        for direction in directions
    )
    direction_rank = remote.rank_mod_two(direction_columns)

    coefficient_modulus = 4
    coefficient_table = []
    for coefficients in product(range(coefficient_modulus), repeat=5):
        variables = variables_for(base, directions, coefficients)
        assert not lift.add_vectors(defect, escape.correction_image(variables, operators))
        coefficient_table.append((coefficients, five_mod_two_bits(wedge_for(variables))))
    undetected = tuple(
        coefficients for coefficients, bits in coefficient_table if not any(bits)
    )
    record = "\n".join(
        f"{''.join(map(str, coefficients))}:{''.join(map(str, bits))}"
        for coefficients, bits in coefficient_table
    )

    certificate = PeriodTwoFiveDirectionObstructionCertificate(
        combination_coefficients=combination_coefficients,
        combination_entries=sum(len(variable) for variable in combination),
        combination_l1=sum(
            abs(coefficient)
            for variable in combination
            for coefficient in variable.values()
        ),
        residual_length=len(residual),
        kernel_length=len(kernel_word),
        relation_module_terms=len(relation_module),
        degree_two_terms=len(wedge),
        degree_two_l1=sum(abs(coefficient) for coefficient in wedge.values()),
        full_wedge_sum=sum(wedge.values()),
        three_point_defect=three_point,
        four_point_defect=four_point,
        cyclic_defect=cyclic_defect,
        cyclic_signed_mod_three=cyclic_signed_mod_three,
        new_three_point_action=NEW_THREE_POINT_ACTION,
        new_three_point_defect=new_defect,
        new_obstruction_mod_two=sum(new_defect) % 2,
        operator_rank_mod_two=operator_rank,
        augmented_rank_mod_two=augmented_rank,
        known_direction_rank_mod_two=direction_rank,
        known_coefficient_modulus=coefficient_modulus,
        known_coefficient_class_count=len(coefficient_table),
        known_coefficient_undetected=undetected,
        known_coefficient_table_sha256=sha256(record.encode()).hexdigest(),
        known_integer_span_obstructed=(direction_rank == 5 and not undetected),
    )
    assert certificate.relation_module_terms == 0
    assert five_mod_two_bits(wedge)[:4] == (0, 0, 0, 0)
    assert certificate.cyclic_signed_mod_three == 0
    assert certificate.new_obstruction_mod_two == 1
    assert certificate.augmented_rank_mod_two > certificate.operator_rank_mod_two
    assert certificate.known_integer_span_obstructed
    return certificate


if __name__ == "__main__":
    print(period_two_five_direction_obstruction_certificate())
