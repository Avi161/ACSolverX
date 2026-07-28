from __future__ import annotations

from dataclasses import dataclass
from itertools import product

try:
    from experiments.stable_ac import depth4_period_two_degree_two_escape_certificate as escape
    from experiments.stable_ac import depth4_period_two_phi4_escape_certificate as phi4
    from experiments.stable_ac import depth4_period_two_remote_syzygy_certificate as remote
except ModuleNotFoundError:
    import depth4_period_two_degree_two_escape_certificate as escape
    import depth4_period_two_phi4_escape_certificate as phi4
    import depth4_period_two_remote_syzygy_certificate as remote


lift = escape.lift


CYCLIC_ACTION = (
    (0, 1, 2),
    (1, 2, 0),
)


@dataclass(frozen=True)
class PeriodTwoCyclicDegreeTwoObstructionCertificate:
    cyclic_action: tuple[tuple[int, ...], tuple[int, ...]]
    projected_defect: tuple[int, ...]
    projected_sum: int
    operator_augmentations: tuple[int, ...]
    operator_rank_mod_two: int
    augmented_rank_mod_two: int
    obstruction: int
    known_direction_rank_mod_two: int
    known_affine_bits: tuple[tuple[tuple[int, ...], tuple[int, ...]], ...]
    known_affine_span_separated: bool


def wedge_for_variables(variables: escape.ModuleVariables) -> escape.WedgeVector:
    residual = escape.corrected_residual(variables)
    kernel_word = escape.schreier_word(residual)
    return escape.degree_two(kernel_word)


def four_obstructions(value: escape.WedgeVector) -> tuple[int, int, int, int]:
    old = escape.degree_two_obstructions(value)
    old_four_action = remote.period_two_remote_syzygy_certificate().four_point_action
    old_four = remote.finite_wedge_vector(value, *old_four_action)
    cyclic = remote.finite_wedge_vector(value, *CYCLIC_ACTION)
    return (*old, sum(old_four) % 2, sum(cyclic) % 2)


def period_two_cyclic_degree_two_obstruction_certificate(
) -> PeriodTwoCyclicDegreeTwoObstructionCertificate:
    _, _, _, defect, operators = escape.recurrence_data()
    base = escape.variables_from_entries(lift.CORRECTION)
    phi4_direction = escape.variables_from_entries(phi4.PHI4_ESCAPE_SYZYGY)
    corrected = escape.add_variables(base, phi4_direction)
    assert not lift.add_vectors(defect, escape.correction_image(corrected, operators))
    wedge = wedge_for_variables(corrected)
    projected = remote.finite_wedge_vector(wedge, *CYCLIC_ACTION)
    columns = remote.operator_columns(operators, *CYCLIC_ACTION)
    operator_rank = remote.rank_mod_two(columns)
    augmented_rank = remote.rank_mod_two((*columns, projected))

    alternate_10 = escape.variables_from_entries(escape.ALTERNATE_10)
    alternate_01 = escape.variables_from_entries(escape.ALTERNATE_01)
    directions = (
        escape.subtract_variables(alternate_10, base),
        escape.subtract_variables(alternate_01, base),
        escape.variables_from_entries(remote.REMOTE_SYZYGY),
        phi4_direction,
    )
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
    affine_bits = []
    for coefficients in product((0, 1), repeat=4):
        variables = base
        for coefficient, direction in zip(coefficients, directions):
            if coefficient:
                variables = escape.add_variables(variables, direction)
        assert not lift.add_vectors(defect, escape.correction_image(variables, operators))
        affine_bits.append((coefficients, four_obstructions(wedge_for_variables(variables))))

    certificate = PeriodTwoCyclicDegreeTwoObstructionCertificate(
        cyclic_action=CYCLIC_ACTION,
        projected_defect=projected,
        projected_sum=sum(projected),
        operator_augmentations=tuple(sum(operator.values()) for operator in operators),
        operator_rank_mod_two=operator_rank,
        augmented_rank_mod_two=augmented_rank,
        obstruction=sum(projected) % 2,
        known_direction_rank_mod_two=direction_rank,
        known_affine_bits=tuple(affine_bits),
        known_affine_span_separated=all(any(bits) for _, bits in affine_bits),
    )
    assert certificate.operator_augmentations == (0, 0, 0, 0, 0)
    assert certificate.obstruction == 1
    assert certificate.augmented_rank_mod_two > certificate.operator_rank_mod_two
    assert certificate.known_direction_rank_mod_two == 4
    assert certificate.known_affine_span_separated
    return certificate


if __name__ == "__main__":
    print(period_two_cyclic_degree_two_obstruction_certificate())
