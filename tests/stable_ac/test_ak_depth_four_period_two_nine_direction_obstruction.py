from experiments.stable_ac.depth4_period_two_nine_direction_obstruction_certificate import (
    period_two_nine_direction_obstruction_certificate,
)


def test_ninth_source_direction_is_exact_and_independent() -> None:
    certificate = period_two_nine_direction_obstruction_certificate()

    assert certificate.forest_paths == (
        ("cTTcttcTT", "BgAbgABgAA", "tctcTct"),
        ("ctcTTTcttcTT", "gAB", "ctcTctcTT"),
        ("ctcTTTTcttcTT", "gABgAbgaB", "ctcTcTctcTT"),
        ("cTTcttctcTct", "BgAbaGaGbGaGaGbA", "tcTT"),
        ("ctcTTTcttctcTct", "gAB", "ctcTctctcTct"),
        ("ctcTTTTcttctcTct", "gABgAbaGaGbGbAB", "ctcTcTctctcTct"),
    )
    assert certificate.syzygy_entries == 43
    assert certificate.syzygy_l1 == 58
    assert certificate.component_image_stats == (
        (12, 12),
        (0, 0),
        (24, 34),
        (26, 38),
        (29, 38),
    )
    assert certificate.homogeneous_image == ()
    assert certificate.eighth_and_ninth_direction_ranks_mod_two == (8, 9)


def test_inverse_four_cycle_detects_the_ninth_direction() -> None:
    certificate = period_two_nine_direction_obstruction_certificate()

    assert certificate.ninth_residual_length == 1578
    assert certificate.ninth_kernel_length == 262
    assert certificate.ninth_degree_two_terms == 535
    assert certificate.ninth_degree_two_l1 == 1096
    assert certificate.ninth_prior_mod_two_bits == (0,) * 10
    assert certificate.inverse_four_point_action == (
        (0, 2, 1, 3),
        (3, 0, 1, 2),
    )
    assert certificate.inverse_four_point_covector == (1, 1, 1, 1, 1, 1)
    assert certificate.inverse_four_point_defect == (26, -8, -18, -4, -3, 4)
    assert certificate.inverse_four_point_value_mod_two == 1
    assert certificate.inverse_four_point_operator_rank == 5
    assert certificate.inverse_four_point_augmented_rank == 6


def test_eleven_functionals_close_every_nine_direction_class() -> None:
    certificate = period_two_nine_direction_obstruction_certificate()

    assert certificate.quadratic_model_replays == 55
    assert certificate.quadratic_validation_replays == 45
    assert certificate.coefficient_class_count == 262144
    assert certificate.undetected_classes == ()
    assert certificate.coefficient_table_sha256 == (
        "117d932505b8cca90d7cedbbfee21edce90a99998620e75d97703f25c4777af9"
    )
    assert certificate.known_integer_span_obstructed
