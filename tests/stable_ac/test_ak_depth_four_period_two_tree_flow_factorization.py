from experiments.stable_ac import depth4_period_two_source_flow_certificate as source
from experiments.stable_ac.depth4_period_two_tree_flow_factorization_certificate import (
    add_directions,
    anchored_direction,
    finite_pair_summary,
    polarization,
    scale_direction,
    source_scalar,
    syndrome,
    tree_flow_factorization_certificate,
)


lift = source.lift


def _bits(value: tuple[int, ...]) -> str:
    return "".join(str(bit) for bit in value)


def _xor(*values: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(map(lambda entries: sum(entries) % 2, zip(*values)))


def test_certificate_separates_recorded_premises_proof_conclusions_and_fixtures() -> None:
    """A rank-five predicate alone must not masquerade as the full tree proof."""
    certificate = tree_flow_factorization_certificate()

    assert certificate.recorded_complete_cover == (4, 16, True)
    assert certificate.recorded_parity_kernel_rank == 5
    assert certificate.recorded_parity_kernel_generator_count == 5
    assert certificate.recorded_parity_kernel_image_rank == 5
    assert certificate.proof_conclusion_parity_kernel_restriction_isomorphic
    assert certificate.proof_conclusion_k_injective
    assert certificate.proof_conclusion_k_index_in_q == 4
    assert certificate.proof_conclusion_k_rank == 3
    assert certificate.proof_conclusion_k_torsion_free
    assert certificate.proof_conclusion_vertex_stabilizers_trivial
    assert certificate.proof_conclusion_tree_components == 2
    assert certificate.proof_conclusion_tree_actions_are_cayley_trees
    assert certificate.proof_conclusion_finite_edge_boundary_injective
    assert certificate.proof_conclusion_unique_finite_forest_flow
    assert certificate.proof_conclusion_flow_pairing_independent
    assert certificate.proof_conclusion_flow_linear
    assert certificate.proof_conclusion_syndrome_factors_through_homogeneous_directions_mod_two
    assert certificate.proof_conclusion_polarization_is_biadditive
    assert certificate.proof_conclusion_polarization_is_alternating
    assert certificate.bounded_raw_collision_checks == 2
    assert certificate.bounded_crossed_pairing_paths_differ
    assert certificate.bounded_crossed_pairing_variables_equal
    assert certificate.bounded_period_two_direction == "TT"
    assert certificate.bounded_period_two_coefficient_records == (
        (0, 0, "111010110101011"),
        (1, 1, "001111101110010"),
        (2, 0, "111010110101011"),
        (3, 1, "001111101110010"),
        (4, 0, "111010110101011"),
    )
    assert certificate.bounded_depth_six_anchored_atoms == 127
    assert certificate.bounded_depth_six_zero_self_polarizations == 127
    assert certificate.bounded_tracked_homogeneous_directions == 11
    assert certificate.bounded_tracked_zero_self_polarizations == 11
    assert certificate.bounded_max_fixture_source_depth == 6


def test_anchor_decomposes_sign_and_magnitude_two_balanced_sources() -> None:
    """Changing the anchor sign or dropping multiplicity two breaks these equalities."""
    fixtures = (
        ("TT", "tt", 1),
        ("TTT", "cTTT", -1),
        ("TTT", "Tct", 1),
        ("TT", "TTTct", 1),
        ("Tctt", "Tctct", 1),
    )

    assert source_scalar(lift.parse_quotient("T")) == 1
    assert source_scalar(lift.parse_quotient("TTT")) == 2
    assert source_scalar(lift.parse_quotient("Tct")) == -2
    for left_label, right_label, right_coefficient in fixtures:
        left = lift.parse_quotient(left_label)
        right = lift.parse_quotient(right_label)
        direct = source.build_l0_direction({left: 1, right: right_coefficient}).variables
        anchored = add_directions(
            anchored_direction(left),
            scale_direction(anchored_direction(right), right_coefficient),
        )
        assert anchored == direct


def test_direction_scaling_aggregates_raw_canonical_aliases() -> None:
    """Scaling must sum raw aliases before multiplication rather than overwrite them."""
    raw_direction = ({(): 1, (lift.C,): 1}, {}, {}, {}, {})

    assert scale_direction(raw_direction, 2) == ({(): 4}, {}, {}, {}, {})


def test_near_survivor_factorization_biadditivity_alternation_and_period_two() -> None:
    """Wrong bit order, a cross-term error, or a final period-four term fails."""
    zero = scale_direction(anchored_direction(lift.parse_quotient("T")), 0)
    x = anchored_direction(lift.parse_quotient("TT"))
    y = anchored_direction(lift.parse_quotient("TTTct"))
    z = anchored_direction(lift.parse_quotient("Tctt"))
    constant = syndrome(zero)
    unary_x = _xor(syndrome(x), constant)
    unary_y = _xor(syndrome(y), constant)
    cross = polarization(x, y)

    assert _bits(constant) == "111010110101011"
    assert _bits(unary_x) == "110101011011001"
    assert _bits(unary_y) == "101111111110111"
    assert _bits(cross) == "100000010000100"
    assert _xor(constant, unary_x, unary_y, cross) == syndrome(add_directions(x, y))
    assert polarization(add_directions(x, y), z) == _xor(
        polarization(x, z), polarization(y, z)
    )
    assert all(
        polarization(direction, direction) == (0,) * 15
        for direction in (x, y, z, add_directions(x, y))
    )
    assert tuple(_bits(syndrome(scale_direction(x, coefficient))) for coefficient in range(5)) == (
        "111010110101011",
        "001111101110010",
        "111010110101011",
        "001111101110010",
        "111010110101011",
    )


def test_defined_finite_pair_summary_is_not_markov() -> None:
    """The exact bounded collision refutes this summary, not every finite state."""
    left = lift.parse_quotient("TT")
    right = lift.parse_quotient("TTTct")
    other_left = lift.parse_quotient("Tctt")
    other_right = lift.parse_quotient("Tctct")
    expected_summary = (
        (
            (0, 2, 3, 1),
            (2, 0, 1, 3),
        ),
        (-1, 1),
        (
            ((0, 1, 2, 3), (0, 2, 3, 1), 1),
            ((0, 2, 3, 1), (0, 3, 1, 2), 0),
            ((0, 2, 3, 1), (0, 3, 1, 2), 1),
            ((2, 0, 1, 3), (2, 1, 3, 0), 0),
            ((2, 0, 1, 3), (2, 1, 3, 0), 1),
            ((2, 3, 0, 1), (2, 0, 1, 3), 1),
        ),
        (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1),
    )

    assert finite_pair_summary(left, right, 1) == expected_summary
    assert finite_pair_summary(other_left, other_right, 1) == expected_summary
    assert tree_flow_factorization_certificate().bounded_no_markov_extensions == (
        ("c", "000100000000100", "100100011000001"),
        ("t", "000000001000000", "100100011000100"),
        ("T", "011110110101110", "011110111101010"),
    )
