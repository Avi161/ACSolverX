from experiments.stable_ac.depth4_period_two_phi4_escape_certificate import (
    period_two_phi4_escape_certificate,
)


def test_source_column_has_an_exact_forest_flow() -> None:
    certificate = period_two_phi4_escape_certificate()

    assert certificate.right_coset_action == (
        (1, 0, 3, 2),
        (0, 2, 3, 1),
    )
    assert certificate.right_coset_action_transitive
    assert certificate.forest_generators_fix_base
    assert certificate.subgroup_index_from_euler_characteristic == 4
    assert certificate.coset_stabilizer_is_forest_subgroup
    assert certificate.source_component_sums == (0, 0)
    assert certificate.forest_paths == (
        ("ctcTcttct", "aGbaGaGbAA", "tt"),
        ("ttct", "aaBgA", "ctcTctt"),
    )
    assert certificate.support_entries == 16
    assert certificate.coefficient_l1 == 16
    assert certificate.component_augmentations == (0, 1, -1, -2, 2)


def test_new_vector_is_an_exact_remote_homogeneous_syzygy() -> None:
    certificate = period_two_phi4_escape_certificate()

    assert certificate.component_image_stats == (
        (0, 0),
        (4, 4),
        (6, 6),
        (8, 8),
        (12, 12),
    )
    assert certificate.homogeneous_image == ()
    assert certificate.outside_one_hop == (
        (1, "ct", 1),
        (2, "ctct", -1),
        (3, "TTctcTcttct", -1),
        (4, "TctcTctt", -1),
        (4, "TctcTcttct", 1),
        (4, "Tctct", 1),
        (4, "tct", 1),
    )


def test_new_lift_kills_all_three_recorded_degree_two_bits() -> None:
    certificate = period_two_phi4_escape_certificate()

    assert certificate.residual_length == 322
    assert certificate.kernel_length == 70
    assert certificate.relation_module_terms == 0
    assert certificate.degree_two_terms == 112
    assert certificate.degree_two_l1 == 124
    assert certificate.full_wedge_sum == -10
    assert certificate.three_point_defect == (-1, -21, -10)
    assert certificate.four_point_defect == (6, 6, 5, 6, -3, -4)
    assert certificate.obstruction_bits == (0, 0, 0)
