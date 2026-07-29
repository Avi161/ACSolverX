from experiments.stable_ac.depth4_period_two_eight_direction_obstruction_certificate import (
    period_two_eight_direction_obstruction_certificate,
)


def test_eighth_source_direction_is_exact_and_independent() -> None:
    certificate = period_two_eight_direction_obstruction_certificate()

    assert certificate.forest_paths == (
        ("cTTcttcTTct", "BgAbgBaGbA", "tcTTct"),
        ("ctcTTTcttcT", "gAB", "ctcTctcT"),
        ("ctcTTTTcttcTTct", "gABgAbgaB", "ctcTcTctcT"),
        ("cTTcttcT", "BgAbaGbA", "tcT"),
        ("ctcTTTTcttcT", "gABgAbgaBgA", "ctcTctcTTct"),
        ("ctcTTTcttcTTct", "gABaG", "ctcTcTctcTTct"),
    )
    assert certificate.syzygy_entries == 35
    assert certificate.syzygy_l1 == 44
    assert certificate.component_image_stats == (
        (12, 12),
        (0, 0),
        (22, 30),
        (20, 26),
        (24, 28),
    )
    assert certificate.homogeneous_image == ()
    assert certificate.seventh_and_eighth_direction_ranks_mod_two == (7, 8)


def test_new_four_point_action_detects_the_eighth_direction() -> None:
    certificate = period_two_eight_direction_obstruction_certificate()

    assert certificate.eighth_residual_length == 1204
    assert certificate.eighth_kernel_length == 212
    assert certificate.eighth_degree_two_terms == 322
    assert certificate.eighth_degree_two_l1 == 566
    assert certificate.eighth_prior_mod_two_bits == (0, 0, 0, 0, 0, 0, 0, 0, 0)
    assert certificate.new_four_point_action == (
        (0, 2, 1, 3),
        (1, 3, 2, 0),
    )
    assert certificate.new_four_point_covector == (1, 1, 1, 1, 1, 1)
    assert certificate.new_four_point_defect == (-8, -7, 3, -5, 22, -4)
    assert certificate.new_four_point_value_mod_two == 1
    assert certificate.new_four_point_operator_rank == 5
    assert certificate.new_four_point_augmented_rank == 6


def test_ten_functionals_close_every_eight_direction_class() -> None:
    certificate = period_two_eight_direction_obstruction_certificate()

    assert certificate.quadratic_model_replays == 45
    assert certificate.quadratic_validation_replays == 36
    assert certificate.coefficient_class_count == 65536
    assert certificate.undetected_classes == ()
    assert certificate.coefficient_table_sha256 == (
        "4d0ce8f4039c38823ffe3ec3e94fd7200465f1501b9dfe585406c21a8cd68f4b"
    )
    assert certificate.known_integer_span_obstructed
