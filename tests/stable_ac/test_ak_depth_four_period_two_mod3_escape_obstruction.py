from experiments.stable_ac.depth4_period_two_mod3_escape_obstruction_certificate import (
    period_two_mod3_escape_obstruction_certificate,
)


def test_second_l1_source_column_has_an_exact_forest_flow() -> None:
    certificate = period_two_mod3_escape_obstruction_certificate()

    assert certificate.source_component_sums == (0, 0)
    assert certificate.forest_paths == (
        ("", "aaBgA", "ctcTctcTT"),
        ("ctcT", "aGaGbA", "tcTT"),
    )
    assert certificate.support_entries == 12
    assert certificate.coefficient_l1 == 12
    assert certificate.component_augmentations == (0, 1, 0, -1, 2)
    assert certificate.component_image_stats == (
        (0, 0),
        (4, 4),
        (4, 4),
        (6, 6),
        (10, 10),
    )
    assert certificate.homogeneous_image == ()


def test_second_source_direction_is_remote_and_new_mod_two() -> None:
    certificate = period_two_mod3_escape_obstruction_certificate()

    assert certificate.outside_one_hop == (
        (2, "TT", 1),
        (2, "cTT", -1),
        (3, "TTctcTcT", -1),
        (3, "TTctcTctcTT", 1),
        (4, "TT", 1),
        (4, "TctcTctcTT", -1),
        (4, "cTT", -1),
    )
    assert certificate.old_mod_two_bits == (0, 0, 0, 0)
    assert certificate.known_direction_ranks_mod_two == (4, 5)
    assert certificate.outside_known_mod_two_affine_span


def test_cyclic_three_point_functional_detects_the_new_lift_mod_three() -> None:
    certificate = period_two_mod3_escape_obstruction_certificate()

    assert certificate.residual_length == 276
    assert certificate.kernel_length == 64
    assert certificate.relation_module_terms == 0
    assert certificate.degree_two_terms == 79
    assert certificate.degree_two_l1 == 94
    assert certificate.full_wedge_sum == -24
    assert certificate.three_point_defect == (-4, 3, 3)
    assert certificate.four_point_defect == (2, 3, 1, 2, 0, 2)
    assert certificate.cyclic_defect == (-1, -3, -4)
    assert certificate.cyclic_signed_functional == (1, -1, 1)
    assert certificate.cyclic_signed_value == -2
    assert certificate.operator_functional_values_mod_three == (0,) * 15
    assert certificate.cyclic_obstruction_mod_three == 1
    assert certificate.operator_rank_mod_three == 2
    assert certificate.augmented_rank_mod_three == 3
