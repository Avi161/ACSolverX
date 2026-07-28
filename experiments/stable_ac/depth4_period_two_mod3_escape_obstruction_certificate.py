from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

try:
    from experiments.stable_ac import depth4_period_two_cyclic_degree_two_obstruction_certificate as cyclic
    from experiments.stable_ac import depth4_period_two_degree_two_escape_certificate as escape
    from experiments.stable_ac import depth4_period_two_phi4_escape_certificate as phi4
    from experiments.stable_ac import depth4_period_two_remote_syzygy_certificate as remote
except ModuleNotFoundError:
    import depth4_period_two_cyclic_degree_two_obstruction_certificate as cyclic
    import depth4_period_two_degree_two_escape_certificate as escape
    import depth4_period_two_phi4_escape_certificate as phi4
    import depth4_period_two_remote_syzygy_certificate as remote


lift = escape.lift


MOD3_ESCAPE_SYZYGY = (
    (1, 1, "TT"),
    (2, 1, "TT"),
    (2, -1, "cTT"),
    (3, -1, "TTctcT"),
    (3, -1, "TTctcTcT"),
    (3, 1, "TTctcTctcTT"),
    (4, 1, "T"),
    (4, 1, "TT"),
    (4, -1, "cTT"),
    (4, 1, "TctcT"),
    (4, 1, "TctcTcT"),
    (4, -1, "TctcTctcTT"),
)


FOREST_PATHS = (
    ("", "aaBgA", "ctcTctcTT"),
    ("ctcT", "aGaGbA", "tcTT"),
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
    variables[1][lift.parse_quotient("TT")] = 1
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


def rank_mod(columns: tuple[tuple[int, ...], ...], prime: int) -> int:
    basis: dict[int, list[int]] = {}
    for column in columns:
        value = [entry % prime for entry in column]
        while True:
            pivot = next((index for index, entry in enumerate(value) if entry), None)
            if pivot is None:
                break
            if pivot not in basis:
                inverse = pow(value[pivot], -1, prime)
                basis[pivot] = [(entry * inverse) % prime for entry in value]
                break
            factor = value[pivot]
            value = [
                (left - factor * right) % prime
                for left, right in zip(value, basis[pivot])
            ]
    return len(basis)


@dataclass(frozen=True)
class PeriodTwoMod3EscapeObstructionCertificate:
    source_component_sums: tuple[int, int]
    forest_paths: tuple[tuple[str, str, str], ...]
    support_entries: int
    coefficient_l1: int
    component_augmentations: tuple[int, ...]
    component_image_stats: tuple[tuple[int, int], ...]
    homogeneous_image: tuple[tuple[str, int], ...]
    outside_one_hop: tuple[tuple[int, str, int], ...]
    residual_length: int
    kernel_length: int
    relation_module_terms: int
    degree_two_terms: int
    degree_two_l1: int
    full_wedge_sum: int
    three_point_defect: tuple[int, ...]
    four_point_defect: tuple[int, ...]
    cyclic_defect: tuple[int, ...]
    old_mod_two_bits: tuple[int, int, int, int]
    cyclic_signed_functional: tuple[int, int, int]
    cyclic_signed_value: int
    operator_functional_values_mod_three: tuple[int, ...]
    cyclic_obstruction_mod_three: int
    operator_rank_mod_three: int
    augmented_rank_mod_three: int
    known_direction_ranks_mod_two: tuple[int, int]
    outside_known_mod_two_affine_span: bool


def period_two_mod3_escape_obstruction_certificate(
) -> PeriodTwoMod3EscapeObstructionCertificate:
    _, _, _, defect, operators = escape.recurrence_data()
    syzygy = escape.variables_from_entries(MOD3_ESCAPE_SYZYGY)
    assert syzygy == reconstruct_from_forest_paths(operators)

    source_column = lift.apply_operator(operators[1], syzygy[1])
    source_sums = [0, 0]
    for word, coefficient in source_column.items():
        source_sums[0 if phi4.orbit_state(word) in (0, 1) else 1] += coefficient

    component_images = tuple(
        lift.apply_operator(operator, variable)
        for operator, variable in zip(operators, syzygy)
    )
    homogeneous = lift.add_vectors(*component_images)
    base = escape.variables_from_entries(lift.CORRECTION)
    corrected = escape.add_variables(base, syzygy)
    assert not lift.add_vectors(defect, escape.correction_image(corrected, operators))

    _, local_columns, _ = escape.local_columns(defect, operators)
    local_set = set(local_columns)
    outside = tuple(sorted(
        (
            operator_index,
            lift.literal(module_vertex),
            coefficient,
        )
        for operator_index, variable in enumerate(syzygy)
        for module_vertex, coefficient in variable.items()
        if (operator_index, module_vertex) not in local_set
    ))

    residual = escape.corrected_residual(corrected)
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
    old_bits = (
        sum(wedge.values()) % 2,
        sum(three_point) % 2,
        sum(four_point) % 2,
        sum(cyclic_defect) % 2,
    )
    columns = remote.operator_columns(operators, *cyclic.CYCLIC_ACTION)
    signed_functional = (1, -1, 1)
    signed_value = sum(
        coefficient * value
        for coefficient, value in zip(signed_functional, cyclic_defect)
    )
    operator_functional_values = tuple(
        sum(coefficient * value for coefficient, value in zip(signed_functional, column)) % 3
        for column in columns
    )
    operator_rank = rank_mod(columns, 3)
    augmented_rank = rank_mod((*columns, cyclic_defect), 3)
    alternate_10 = escape.variables_from_entries(escape.ALTERNATE_10)
    alternate_01 = escape.variables_from_entries(escape.ALTERNATE_01)
    previous_directions = (
        escape.subtract_variables(alternate_10, base),
        escape.subtract_variables(alternate_01, base),
        escape.variables_from_entries(remote.REMOTE_SYZYGY),
        escape.variables_from_entries(phi4.PHI4_ESCAPE_SYZYGY),
    )

    def direction_rank(directions: tuple[escape.ModuleVariables, ...]) -> int:
        rows = sorted({
            (operator_index, module_vertex)
            for direction in directions
            for operator_index, variable in enumerate(direction)
            for module_vertex in variable
        })
        direction_columns = tuple(
            tuple(
                direction[operator_index].get(module_vertex, 0)
                for operator_index, module_vertex in rows
            )
            for direction in directions
        )
        return remote.rank_mod_two(direction_columns)

    direction_ranks = (
        direction_rank(previous_directions),
        direction_rank((*previous_directions, syzygy)),
    )

    homogeneous_tuple = tuple(sorted(
        ((lift.literal(word), coefficient) for word, coefficient in homogeneous.items()),
        key=lambda item: (len(item[0]), item[0], item[1]),
    ))
    certificate = PeriodTwoMod3EscapeObstructionCertificate(
        source_component_sums=tuple(source_sums),
        forest_paths=FOREST_PATHS,
        support_entries=sum(len(variable) for variable in syzygy),
        coefficient_l1=sum(
            abs(coefficient)
            for variable in syzygy
            for coefficient in variable.values()
        ),
        component_augmentations=tuple(sum(variable.values()) for variable in syzygy),
        component_image_stats=tuple(
            (len(value), sum(abs(coefficient) for coefficient in value.values()))
            for value in component_images
        ),
        homogeneous_image=homogeneous_tuple,
        outside_one_hop=outside,
        residual_length=len(residual),
        kernel_length=len(kernel_word),
        relation_module_terms=len(relation_module),
        degree_two_terms=len(wedge),
        degree_two_l1=sum(abs(coefficient) for coefficient in wedge.values()),
        full_wedge_sum=sum(wedge.values()),
        three_point_defect=three_point,
        four_point_defect=four_point,
        cyclic_defect=cyclic_defect,
        old_mod_two_bits=old_bits,
        cyclic_signed_functional=signed_functional,
        cyclic_signed_value=signed_value,
        operator_functional_values_mod_three=operator_functional_values,
        cyclic_obstruction_mod_three=signed_value % 3,
        operator_rank_mod_three=operator_rank,
        augmented_rank_mod_three=augmented_rank,
        known_direction_ranks_mod_two=direction_ranks,
        outside_known_mod_two_affine_span=direction_ranks == (4, 5),
    )
    assert certificate.source_component_sums == (0, 0)
    assert certificate.homogeneous_image == ()
    assert certificate.relation_module_terms == 0
    assert certificate.old_mod_two_bits == (0, 0, 0, 0)
    assert not any(certificate.operator_functional_values_mod_three)
    assert certificate.cyclic_obstruction_mod_three == 1
    assert certificate.augmented_rank_mod_three > certificate.operator_rank_mod_three
    assert certificate.known_direction_ranks_mod_two == (4, 5)
    assert certificate.outside_known_mod_two_affine_span
    return certificate


if __name__ == "__main__":
    print(period_two_mod3_escape_obstruction_certificate())
