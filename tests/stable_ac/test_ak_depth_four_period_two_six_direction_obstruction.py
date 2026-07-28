from experiments.stable_ac.depth4_period_two_six_direction_obstruction_certificate import (
    period_two_six_direction_obstruction_certificate,
)


def test_sixth_source_direction_is_exact_and_independent() -> None:
    certificate = period_two_six_direction_obstruction_certificate()

    assert certificate.forest_paths == (
        ("tttcTTT", "aaBgA", "ctcTctctcTTT"),
        ("ctcTctttcTTT", "aGbaGBgAbaGA", "tctcTTT"),
    )
    assert certificate.syzygy_entries == 18
    assert certificate.syzygy_l1 == 18
    assert certificate.component_image_stats == (
        (0, 0),
        (4, 4),
        (8, 8),
        (10, 10),
        (14, 14),
    )
    assert certificate.homogeneous_image == ()
    assert certificate.fifth_and_sixth_direction_ranks_mod_two == (5, 6)


def test_sixth_direction_escapes_five_bits_but_not_mod_three() -> None:
    certificate = period_two_six_direction_obstruction_certificate()

    assert certificate.sixth_residual_length == 608
    assert certificate.sixth_kernel_length == 88
    assert certificate.sixth_degree_two_terms == 165
    assert certificate.sixth_degree_two_l1 == 196
    assert certificate.sixth_known_mod_two_bits == (0, 0, 0, 0, 0)
    assert certificate.sixth_cyclic_signed_mod_three == 2


def test_two_point_action_detects_the_integral_six_direction_escape() -> None:
    certificate = period_two_six_direction_obstruction_certificate()

    assert certificate.combination_coefficients == (0, 0, 0, 4, -4, -3)
    assert certificate.combination_entries == 51
    assert certificate.combination_l1 == 162
    assert certificate.combination_residual_length == 1372
    assert certificate.combination_kernel_length == 372
    assert certificate.combination_degree_two_terms == 612
    assert certificate.combination_degree_two_l1 == 6122
    assert certificate.combination_known_mod_two_bits == (0, 0, 0, 0, 0)
    assert certificate.combination_cyclic_signed_mod_three == 0
    assert certificate.two_point_action == ((0, 1), (1, 0))
    assert certificate.two_point_defect == (45,)
    assert certificate.two_point_operator_rank == 0
    assert certificate.two_point_augmented_rank == 1


def test_six_functionals_close_every_mod_four_class() -> None:
    certificate = period_two_six_direction_obstruction_certificate()

    assert certificate.quadratic_model_replays == 28
    assert certificate.quadratic_validation_replays == 21
    assert certificate.coefficient_class_count == 4096
    assert certificate.undetected_classes == ()
    assert certificate.coefficient_table_sha256 == (
        "58994ebbd8531bc402c4c8e15410c2a70448db8f8f50298f24f9c87fc1811298"
    )
    assert certificate.known_integer_span_obstructed
