from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

try:
    from experiments.stable_ac import depth4_period_two_binomial_forest_certificate as forest
    from experiments.stable_ac import depth4_period_two_degree_two_escape_certificate as escape
    from experiments.stable_ac import depth4_period_two_remote_syzygy_certificate as remote
except ModuleNotFoundError:
    import depth4_period_two_binomial_forest_certificate as forest
    import depth4_period_two_degree_two_escape_certificate as escape
    import depth4_period_two_remote_syzygy_certificate as remote


lift = escape.lift


PHI4_ESCAPE_SYZYGY = (
    (1, 1, "ct"),
    (2, -1, ""),
    (2, 1, "ct"),
    (2, -1, "ctct"),
    (3, -1, "TTctct"),
    (3, -1, "TTctcTct"),
    (3, 1, "TTctcTctt"),
    (3, -1, "TTctcTcttct"),
    (4, -1, ""),
    (4, -1, "t"),
    (4, 1, "ct"),
    (4, 1, "tct"),
    (4, 1, "Tctct"),
    (4, 1, "TctcTct"),
    (4, -1, "TctcTctt"),
    (4, 1, "TctcTcttct"),
)


FOREST_PATHS = (
    ("ctcTcttct", "aGbaGaGbAA", "tt"),
    ("ttct", "aaBgA", "ctcTctt"),
)


def orbit_state(word: lift.Word) -> int:
    c_action = (1, 0, 3, 2)
    t_action = (0, 2, 3, 1)
    t_inverse = remote.permutation_inverse(t_action)
    state = 0
    for letter in word:
        action = (
            c_action
            if abs(letter) == lift.C
            else t_action
            if letter == lift.T
            else t_inverse
        )
        state = action[state]
    return state


def forest_generators(
    operators: tuple[lift.GroupRing, ...],
) -> dict[str, lift.Word]:
    x_element = next(word for word, coefficient in operators[2].items() if coefficient == -1)
    u_inverse = next(word for word, coefficient in operators[3].items() if coefficient == 1)
    return {
        "A": (lift.T,),
        "B": x_element,
        "G": lift.quotient_multiply(u_inverse, (-lift.T,)),
    }


def reconstruct_from_forest_paths(
    operators: tuple[lift.GroupRing, ...],
) -> escape.ModuleVariables:
    generators = forest_generators(operators)
    generators.update({
        name.lower(): lift.quotient_inverse(word)
        for name, word in tuple(generators.items())
    })
    variables: list[dict[lift.Word, int]] = [defaultdict(int) for _ in range(5)]
    variables[1][lift.parse_quotient("ct")] = 1
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


@dataclass(frozen=True)
class PeriodTwoPhi4EscapeCertificate:
    right_coset_action: tuple[tuple[int, ...], tuple[int, ...]]
    right_coset_action_transitive: bool
    forest_generators_fix_base: bool
    subgroup_index_from_euler_characteristic: int
    coset_stabilizer_is_forest_subgroup: bool
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
    obstruction_bits: tuple[int, int, int]


def period_two_phi4_escape_certificate() -> PeriodTwoPhi4EscapeCertificate:
    _, _, _, defect, operators = escape.recurrence_data()
    syzygy = escape.variables_from_entries(PHI4_ESCAPE_SYZYGY)
    assert syzygy == reconstruct_from_forest_paths(operators)

    c_action = (1, 0, 3, 2)
    t_action = (0, 2, 3, 1)
    right_coset_action = (c_action, t_action)
    t_inverse = remote.permutation_inverse(t_action)
    seen = {0}
    boundary = [0]
    while boundary:
        state = boundary.pop()
        for action in (c_action, t_action, t_inverse):
            target = action[state]
            if target not in seen:
                seen.add(target)
                boundary.append(target)
    generators_fix_base = all(
        orbit_state(word) == 0
        for word in forest_generators(operators).values()
    )
    forest_certificate = forest.period_two_binomial_forest_certificate()
    subgroup_index = 2 * (len(forest_certificate.ambient_generators) - 1)
    stabilizer_is_subgroup = (
        forest_certificate.free_rank_three
        and generators_fix_base
        and len(seen) == subgroup_index == 4
    )

    source_column = lift.apply_operator(
        operators[1],
        {lift.parse_quotient("ct"): 1},
    )
    source_sums = [0, 0]
    for word, coefficient in source_column.items():
        source_sums[0 if orbit_state(word) in (0, 1) else 1] += coefficient

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
        (0, 1, 3, 2),
        (1, 2, 0, 3),
    )
    full_sum = sum(wedge.values())
    obstruction_bits = (
        full_sum % 2,
        sum(three_point) % 2,
        sum(four_point) % 2,
    )

    homogeneous_tuple = tuple(sorted(
        ((lift.literal(word), coefficient) for word, coefficient in homogeneous.items()),
        key=lambda item: (len(item[0]), item[0], item[1]),
    ))
    certificate = PeriodTwoPhi4EscapeCertificate(
        right_coset_action=right_coset_action,
        right_coset_action_transitive=len(seen) == 4,
        forest_generators_fix_base=generators_fix_base,
        subgroup_index_from_euler_characteristic=subgroup_index,
        coset_stabilizer_is_forest_subgroup=stabilizer_is_subgroup,
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
        full_wedge_sum=full_sum,
        three_point_defect=three_point,
        four_point_defect=four_point,
        obstruction_bits=obstruction_bits,
    )
    assert certificate.coset_stabilizer_is_forest_subgroup
    assert certificate.source_component_sums == (0, 0)
    assert certificate.homogeneous_image == ()
    assert certificate.relation_module_terms == 0
    assert certificate.obstruction_bits == (0, 0, 0)
    return certificate


if __name__ == "__main__":
    print(period_two_phi4_escape_certificate())
