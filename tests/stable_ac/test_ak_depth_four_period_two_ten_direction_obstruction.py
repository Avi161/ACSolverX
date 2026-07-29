from experiments.stable_ac.depth4_period_two_ten_direction_obstruction_certificate import (
    period_two_ten_direction_obstruction_certificate,
)


def test_tenth_source_direction_is_exact_and_independent() -> None:
    certificate = period_two_ten_direction_obstruction_certificate()

    assert certificate.forest_paths == (
        ("cTTct", "BgAb", ""),
        ("ctcTTTTct", "gABgAbaGaGaGbaBgA", "ctcTctcTcTTT"),
        ("ctcTTTcttcTcTTT", "gABaG", "ctcTcTctcTcTTT"),
        ("ctcTTTct", "gAB", "ctcT"),
        ("cTTcttcTcTTT", "BgAbgAgAB", "ctcTcT"),
        ("ctcTTTTcttcTcTTT", "gABgAbgAgABaGbaGaGbA", "tcTcTTT"),
    )
    assert certificate.syzygy_entries == 43
    assert certificate.syzygy_l1 == 56
    assert certificate.component_image_stats == (
        (12, 12),
        (0, 0),
        (22, 32),
        (28, 36),
        (32, 40),
    )
    assert certificate.homogeneous_image == ()
    assert certificate.ninth_and_tenth_direction_ranks_mod_two == (9, 10)


def test_five_cycle_detects_the_tenth_direction() -> None:
    certificate = period_two_ten_direction_obstruction_certificate()

    assert certificate.tenth_residual_length == 1208
    assert certificate.tenth_kernel_length == 204
    assert certificate.tenth_degree_two_terms == 640
    assert certificate.tenth_degree_two_l1 == 1116
    assert certificate.tenth_prior_mod_two_bits == (0,) * 11
    assert certificate.five_point_action == (
        (0, 1, 2, 3, 4),
        (1, 2, 3, 4, 0),
    )
    assert certificate.five_point_covectors == (
        (0, 1, 1, 0, 0, 1, 1, 0, 1, 0),
        (1, 0, 0, 1, 1, 0, 0, 1, 0, 1),
    )
    assert certificate.five_point_defect == (-6, 9, 0, -14, 0, -2, 12, 2, -4, 1)
    assert certificate.five_point_values_mod_two == (1, 1)
    assert certificate.five_point_operator_rank == 8
    assert certificate.five_point_covector_rank == 2
    assert certificate.five_point_augmented_rank == 9


def test_thirteen_functionals_close_every_ten_direction_class() -> None:
    certificate = period_two_ten_direction_obstruction_certificate()

    assert certificate.quadratic_model_replays == 66
    assert certificate.quadratic_validation_replays == 55
    assert certificate.coefficient_class_count == 1048576
    assert certificate.undetected_classes == ()
    assert certificate.coefficient_table_sha256 == (
        "9c695ef0446c0033cc193f0e6f562633128b09bb4664e6a15d99f53e3f011707"
    )
    assert certificate.known_integer_span_obstructed
