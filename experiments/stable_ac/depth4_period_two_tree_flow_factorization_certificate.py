"""Exact bounded data supporting the tree-flow factorization proof.

The ``recorded_*`` fields are executable premises, ``proof_conclusion_*``
fields record conclusions of the accompanying abstract free-group/tree
arguments, and ``bounded_*`` fields are fixed fixtures.  The executable
fixtures alone are not a proof of those general conclusions.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

try:
    from experiments.stable_ac import depth4_period_two_binomial_forest_certificate as forest
    from experiments.stable_ac import depth4_period_two_degree_two_escape_certificate as escape
    from experiments.stable_ac import depth4_period_two_depth6_l0_census_certificate as census
    from experiments.stable_ac import depth4_period_two_source_flow_certificate as source
    from experiments.stable_ac import depth4_period_two_subgroup_rewrite_certificate as rewrite
except ModuleNotFoundError:
    import depth4_period_two_binomial_forest_certificate as forest
    import depth4_period_two_degree_two_escape_certificate as escape
    import depth4_period_two_depth6_l0_census_certificate as census
    import depth4_period_two_source_flow_certificate as source
    import depth4_period_two_subgroup_rewrite_certificate as rewrite


lift = escape.lift
ANCHOR = lift.parse_quotient("T")


@lru_cache(maxsize=1)
def _fixed_data() -> tuple[escape.ModuleVariables, tuple[lift.GroupRing, ...]]:
    _, _, _, _, operators = escape.recurrence_data()
    return escape.variables_from_entries(lift.CORRECTION), operators


def _zero_direction() -> escape.ModuleVariables:
    return ({}, {}, {}, {}, {})


def source_scalar(vertex: lift.Word) -> int:
    _, operators = _fixed_data()
    canonical_vertex = lift.c_vertex(vertex)
    boundary = lift.apply_operator(operators[0], {canonical_vertex: 1})
    first, second = source.orbit_sums(boundary)
    assert first + second == 0
    return first


def anchored_direction(vertex: lift.Word) -> escape.ModuleVariables:
    _, operators = _fixed_data()
    canonical_vertex = lift.c_vertex(vertex)
    anchored_source = lift.add_vectors(
        {canonical_vertex: 1},
        {ANCHOR: -source_scalar(canonical_vertex)},
    )
    boundary = lift.apply_operator(operators[0], anchored_source)
    assert source.orbit_sums(boundary) == (0, 0)
    direction = source.build_l0_direction(anchored_source).variables
    assert not escape.correction_image(direction, operators)
    return direction


def add_directions(*directions: escape.ModuleVariables) -> escape.ModuleVariables:
    if not directions:
        return _zero_direction()
    assert all(len(direction) == 5 for direction in directions)
    return tuple(
        lift.add_vectors(*(direction[index] for direction in directions))
        for index in range(5)
    )


def scale_direction(
    direction: escape.ModuleVariables,
    coefficient: int,
) -> escape.ModuleVariables:
    assert len(direction) == 5
    return tuple(
        lift.scale_vector(lift.add_vectors(variable), coefficient)
        for variable in direction
    )


def syndrome(direction: escape.ModuleVariables) -> tuple[int, ...]:
    base, operators = _fixed_data()
    assert not escape.correction_image(direction, operators)
    residual = escape.corrected_residual(add_directions(base, direction))
    kernel_word = escape.schreier_word(residual)
    finite_bits = census.projected_fourteen_bits(kernel_word)
    wedge = escape.degree_two(kernel_word)
    bits = (*finite_bits, sum(wedge.values()) % 2)
    assert len(bits) == 15 and all(bit in (0, 1) for bit in bits)
    return bits


def _xor(*values: tuple[int, ...]) -> tuple[int, ...]:
    assert values and all(len(value) == len(values[0]) for value in values)
    return tuple(sum(entries) % 2 for entries in zip(*values))


def polarization(
    left: escape.ModuleVariables,
    right: escape.ModuleVariables,
) -> tuple[int, ...]:
    return _xor(
        syndrome(add_directions(left, right)),
        syndrome(left),
        syndrome(right),
        syndrome(_zero_direction()),
    )


def _pair_epsilon(start: lift.Word, end: lift.Word) -> int:
    start_inverse = rewrite.q_inverse(rewrite.q_normal_form(start))
    candidates = []
    for epsilon in (0, 1):
        end_c = rewrite.q_multiply(rewrite.q_normal_form(end), ((), epsilon))
        ratio = rewrite.q_multiply(end_c, start_inverse)
        if rewrite.in_k(ratio):
            candidates.append(epsilon)
    assert len(candidates) == 1
    return candidates[0]


def finite_pair_summary(
    left: lift.Word,
    right: lift.Word,
    right_coefficient: int,
) -> tuple:
    assert right_coefficient in (-1, 1)
    canonical_left = lift.c_vertex(left)
    canonical_right = lift.c_vertex(right)
    pair_source = lift.add_vectors(
        {canonical_left: 1},
        {canonical_right: right_coefficient},
    )
    _, operators = _fixed_data()
    boundary = lift.apply_operator(operators[0], pair_source)
    assert source.orbit_sums(boundary) == (0, 0)
    pairs = source.paired_boundaries(boundary)
    assert pairs is not None
    source_records = tuple(sorted((
        (source.vertex_action_class(canonical_left), source_scalar(canonical_left)),
        (
            source.vertex_action_class(canonical_right),
            right_coefficient * source_scalar(canonical_right),
        ),
    )))
    pair_records = tuple(sorted(
        (
            source.vertex_action_class(start),
            source.vertex_action_class(end),
            _pair_epsilon(start, end),
        )
        for start, end in pairs
    ))
    direction = source.build_l0_direction_from_pairs(pair_source, pairs).variables
    source_action_classes = tuple(action for action, _ in source_records)
    signed_orbit_scalars = tuple(scalar for _, scalar in source_records)
    return source_action_classes, signed_orbit_scalars, pair_records, syndrome(direction)


def _bits(value: tuple[int, ...]) -> str:
    return "".join(str(bit) for bit in value)


@dataclass(frozen=True)
class PeriodTwoTreeFlowFactorizationCertificate:
    """Keeps finite premises, proof conclusions, and bounded fixtures distinct."""

    recorded_complete_cover: tuple[int, int, bool]
    recorded_parity_kernel_rank: int
    recorded_parity_kernel_generator_count: int
    recorded_parity_kernel_image_rank: int
    proof_conclusion_parity_kernel_restriction_isomorphic: bool
    proof_conclusion_k_injective: bool
    proof_conclusion_k_index_in_q: int
    proof_conclusion_k_rank: int
    proof_conclusion_k_torsion_free: bool
    proof_conclusion_vertex_stabilizers_trivial: bool
    proof_conclusion_tree_components: int
    proof_conclusion_tree_actions_are_cayley_trees: bool
    proof_conclusion_finite_edge_boundary_injective: bool
    proof_conclusion_unique_finite_forest_flow: bool
    proof_conclusion_flow_pairing_independent: bool
    proof_conclusion_flow_linear: bool
    proof_conclusion_syndrome_factors_through_homogeneous_directions_mod_two: bool
    proof_conclusion_polarization_is_biadditive: bool
    proof_conclusion_polarization_is_alternating: bool
    bounded_raw_collision_checks: int
    bounded_crossed_pairing_paths_differ: bool
    bounded_crossed_pairing_variables_equal: bool
    bounded_anchor_label: str
    bounded_anchor_scalar: int
    bounded_anchored_decompositions: tuple[str, ...]
    bounded_quadratic_constant: str
    bounded_near_survivor_unaries: tuple[str, str]
    bounded_near_survivor_cross: str
    bounded_biadditivity: str
    bounded_fixed_zero_self_polarizations: int
    bounded_period_two_direction: str
    bounded_period_two_coefficient_records: tuple[tuple[int, int, str], ...]
    bounded_period_two_syndromes: tuple[str, ...]
    bounded_depth_six_anchored_atoms: int
    bounded_depth_six_zero_self_polarizations: int
    bounded_tracked_homogeneous_directions: int
    bounded_tracked_zero_self_polarizations: int
    bounded_no_markov_summary: tuple
    bounded_no_markov_extensions: tuple[tuple[str, str, str], ...]
    bounded_max_fixture_source_depth: int


@lru_cache(maxsize=1)
def tree_flow_factorization_certificate() -> PeriodTwoTreeFlowFactorizationCertificate:
    base, operators = _fixed_data()
    forest_certificate = forest.period_two_binomial_forest_certificate()
    rewrite_certificate = rewrite.subgroup_rewrite_certificate()
    core_vertices = {vertex for edge in rewrite.CORE for vertex in (edge[0], edge[2])}
    transitions = {(start, label) for start, label, _ in rewrite.CORE}
    cover_is_complete = all(
        (vertex, label) in transitions
        for vertex in core_vertices
        for label in (forest.P, -forest.P, forest.Q, -forest.Q)
    )
    recorded_complete_cover = (
        len(core_vertices),
        len(rewrite.CORE),
        cover_is_complete,
    )
    parity_kernel_rank = 1 + 2 * (3 - 1)
    assert recorded_complete_cover == (4, 16, True)
    assert rewrite_certificate.core_free_rank == forest_certificate.core_rank == 5
    assert parity_kernel_rank == len(forest.RS_KERNEL_GENERATORS) == 5

    cancelled = source.build_l0_direction({(): 1, (lift.C,): -1})
    doubled = source.build_l0_direction({
        (): 1,
        (lift.C,): 1,
        lift.parse_quotient("Tct"): 2,
    })
    assert cancelled.variables == _zero_direction()
    assert doubled.source == (("", 2), ("Tct", 2))

    crossed_source = source.source_from_entries((("T", 1), ("ttttct", 1)))
    canonical = source.build_l0_direction(crossed_source)
    crossed = source.build_l0_direction_from_pairs(
        crossed_source,
        (
            (lift.parse_quotient("ctcTTTcttcT"), lift.parse_quotient("tcttttct")),
            (lift.parse_quotient("cTTcttcttttct"), lift.parse_quotient("ctcTctcT")),
            (
                lift.parse_quotient("ctcTTTTcttcttttct"),
                lift.parse_quotient("ctcTcTctcT"),
            ),
            (lift.parse_quotient("cTTcttcT"), lift.parse_quotient("tcT")),
            (
                lift.parse_quotient("ctcTTTTcttcT"),
                lift.parse_quotient("ctcTctcttttct"),
            ),
            (
                lift.parse_quotient("ctcTTTcttcttttct"),
                lift.parse_quotient("ctcTcTctcttttct"),
            ),
        ),
    )
    pairing_paths_differ = crossed.paths != canonical.paths
    pairing_variables_equal = crossed.variables == canonical.variables
    assert pairing_paths_differ and pairing_variables_equal

    anchored_fixtures = (
        ("TT", "tt", 1),
        ("TTT", "cTTT", -1),
        ("TTT", "Tct", 1),
        ("TT", "TTTct", 1),
        ("Tctt", "Tctct", 1),
    )
    anchored_labels = []
    for left_label, right_label, right_coefficient in anchored_fixtures:
        left = lift.parse_quotient(left_label)
        right = lift.parse_quotient(right_label)
        direct = source.build_l0_direction({left: 1, right: right_coefficient}).variables
        decomposed = add_directions(
            anchored_direction(left),
            scale_direction(anchored_direction(right), right_coefficient),
        )
        assert decomposed == direct
        assert not escape.correction_image(decomposed, operators)
        sign = "+" if right_coefficient == 1 else "-"
        anchored_labels.append(f"{left_label}{sign}{right_label}")

    zero = _zero_direction()
    x = anchored_direction(lift.parse_quotient("TT"))
    y = anchored_direction(lift.parse_quotient("TTTct"))
    z = anchored_direction(lift.parse_quotient("Tctt"))
    constant = syndrome(zero)
    unary_x = _xor(syndrome(x), constant)
    unary_y = _xor(syndrome(y), constant)
    cross = polarization(x, y)
    pair_syndrome = syndrome(add_directions(x, y))
    assert _bits(constant) == "111010110101011"
    assert _bits(unary_x) == "110101011011001"
    assert _bits(unary_y) == "101111111110111"
    assert _bits(cross) == "100000010000100"
    assert _xor(constant, unary_x, unary_y, cross) == pair_syndrome
    assert _bits(pair_syndrome) == "000000000000001"

    biadditivity = polarization(add_directions(x, y), z)
    assert biadditivity == _xor(polarization(x, z), polarization(y, z))
    assert _bits(biadditivity) == "100000001000100"
    zero_bits = (0,) * 15
    fixed_directions = (x, y, z, add_directions(x, y))
    assert all(polarization(direction, direction) == zero_bits for direction in fixed_directions)

    period_two_records = []
    for coefficient in range(5):
        parity = coefficient % 2
        model = _xor(constant, unary_x) if parity else constant
        direct = syndrome(scale_direction(x, coefficient))
        assert model == direct
        period_two_records.append((coefficient, parity, _bits(direct)))
    period_two_coefficient_records = tuple(period_two_records)
    period_two_syndromes = tuple(record[-1] for record in period_two_coefficient_records)
    assert period_two_syndromes == (
        "111010110101011",
        "001111101110010",
        "111010110101011",
        "001111101110010",
        "111010110101011",
    )

    depth_six_atoms = source.source_vertices(6)
    depth_six_zero_self_polarizations = sum(
        _xor(
            syndrome(scale_direction(anchored_direction(vertex), 2)),
            constant,
        ) == zero_bits
        for vertex in depth_six_atoms
    )
    assert depth_six_zero_self_polarizations == len(depth_six_atoms) == 127

    tracked_directions = (
        *census.six.known_directions(base),
        census.seven.reconstruct_from_forest_paths(operators),
        census.eight.reconstruct_from_forest_paths(operators),
        census.nine.reconstruct_from_forest_paths(operators),
        census.ten.reconstruct_from_forest_paths(operators),
        census.eleven.reconstruct_from_forest_paths(operators),
    )
    tracked_zero_self_polarizations = sum(
        _xor(syndrome(scale_direction(direction, 2)), constant) == zero_bits
        for direction in tracked_directions
    )
    assert tracked_zero_self_polarizations == len(tracked_directions) == 11

    first_pair = (lift.parse_quotient("TT"), lift.parse_quotient("TTTct"))
    second_pair = (lift.parse_quotient("Tctt"), lift.parse_quotient("Tctct"))
    first_summary = finite_pair_summary(*first_pair, 1)
    second_summary = finite_pair_summary(*second_pair, 1)
    assert first_summary == second_summary
    assert _bits(first_summary[-1]) == "000000000000001"

    extension_letters = (("c", lift.C), ("t", lift.T), ("T", -lift.T))
    extension_records = []
    extended_vertices = []
    for label, letter in extension_letters:
        syndromes = []
        for pair in (first_pair, second_pair):
            extended = tuple(
                lift.c_vertex(lift.quotient_multiply((letter,), vertex))
                for vertex in pair
            )
            extended_vertices.extend(extended)
            direction = source.build_l0_direction({extended[0]: 1, extended[1]: 1}).variables
            syndromes.append(_bits(syndrome(direction)))
        extension_records.append((label, syndromes[0], syndromes[1]))
    extensions = tuple(extension_records)
    assert extensions == (
        ("c", "000100000000100", "100100011000001"),
        ("t", "000000001000000", "100100011000100"),
        ("T", "011110110101110", "011110111101010"),
    )

    fixture_vertices = [
        lift.parse_quotient(label)
        for fixture in anchored_fixtures
        for label in fixture[:2]
    ]
    fixture_vertices.extend((
        *crossed_source,
        *first_pair,
        *second_pair,
        *extended_vertices,
    ))
    fixture_vertices.extend(
        vertex
        for direction in tracked_directions
        for vertex in direction[0]
    )
    max_fixture_depth = max(len(vertex) for vertex in fixture_vertices)
    assert max_fixture_depth == max(len(vertex) for vertex in depth_six_atoms) == 6
    assert not escape.correction_image(zero, operators)

    return PeriodTwoTreeFlowFactorizationCertificate(
        recorded_complete_cover=recorded_complete_cover,
        recorded_parity_kernel_rank=parity_kernel_rank,
        recorded_parity_kernel_generator_count=len(forest.RS_KERNEL_GENERATORS),
        recorded_parity_kernel_image_rank=forest_certificate.core_rank,
        proof_conclusion_parity_kernel_restriction_isomorphic=True,
        proof_conclusion_k_injective=True,
        proof_conclusion_k_index_in_q=4,
        proof_conclusion_k_rank=3,
        proof_conclusion_k_torsion_free=True,
        proof_conclusion_vertex_stabilizers_trivial=True,
        proof_conclusion_tree_components=2,
        proof_conclusion_tree_actions_are_cayley_trees=True,
        proof_conclusion_finite_edge_boundary_injective=True,
        proof_conclusion_unique_finite_forest_flow=True,
        proof_conclusion_flow_pairing_independent=True,
        proof_conclusion_flow_linear=True,
        proof_conclusion_syndrome_factors_through_homogeneous_directions_mod_two=True,
        proof_conclusion_polarization_is_biadditive=True,
        proof_conclusion_polarization_is_alternating=True,
        bounded_raw_collision_checks=2,
        bounded_crossed_pairing_paths_differ=pairing_paths_differ,
        bounded_crossed_pairing_variables_equal=pairing_variables_equal,
        bounded_anchor_label="T",
        bounded_anchor_scalar=source_scalar(ANCHOR),
        bounded_anchored_decompositions=tuple(anchored_labels),
        bounded_quadratic_constant=_bits(constant),
        bounded_near_survivor_unaries=(_bits(unary_x), _bits(unary_y)),
        bounded_near_survivor_cross=_bits(cross),
        bounded_biadditivity=_bits(biadditivity),
        bounded_fixed_zero_self_polarizations=len(fixed_directions),
        bounded_period_two_direction="TT",
        bounded_period_two_coefficient_records=period_two_coefficient_records,
        bounded_period_two_syndromes=period_two_syndromes,
        bounded_depth_six_anchored_atoms=len(depth_six_atoms),
        bounded_depth_six_zero_self_polarizations=depth_six_zero_self_polarizations,
        bounded_tracked_homogeneous_directions=len(tracked_directions),
        bounded_tracked_zero_self_polarizations=tracked_zero_self_polarizations,
        bounded_no_markov_summary=first_summary,
        bounded_no_markov_extensions=extensions,
        bounded_max_fixture_source_depth=max_fixture_depth,
    )


if __name__ == "__main__":
    print(tree_flow_factorization_certificate())
