from experiments.stable_ac.depth4_period_two_seven_direction_obstruction_certificate import (
    period_two_seven_direction_obstruction_certificate,
)


def test_seventh_source_direction_is_exact_and_independent() -> None:
    certificate = period_two_seven_direction_obstruction_certificate()

    assert certificate.forest_paths == (
        ("ctcTTTcttcT", "gAB", "ctcTctcT"),
        (
            "cTTcttcttttct",
            "BgAbaGaGbaGaGaGbaBgAgABgAgAgAA",
            "tcttttct",
        ),
        (
            "ctcTTTTcttcttttct",
            "gABgAbaGaGbaGaGaGbaaB",
            "ctcTcTctcT",
        ),
        ("cTTcttcT", "BgAbaGbA", "tcT"),
        (
            "ctcTTTTcttcT",
            "gABgAbgAAAAABgA",
            "ctcTctcttttct",
        ),
        (
            "ctcTTTcttcttttct",
            "gABaG",
            "ctcTcTctcttttct",
        ),
    )
    assert certificate.syzygy_entries == 59
    assert certificate.syzygy_l1 == 80
    assert certificate.component_image_stats == (
        (12, 12),
        (0, 0),
        (26, 38),
        (36, 50),
        (41, 56),
    )
    assert certificate.homogeneous_image == ()
    assert certificate.sixth_and_seventh_direction_ranks_mod_two == (6, 7)


def test_twisted_four_cycle_detects_the_seventh_direction() -> None:
    certificate = period_two_seven_direction_obstruction_certificate()

    assert certificate.seventh_residual_length == 2012
    assert certificate.seventh_kernel_length == 310
    assert certificate.seventh_degree_two_terms == 1001
    assert certificate.seventh_degree_two_l1 == 2016
    assert certificate.seventh_prior_mod_two_bits == (0, 0, 0, 0, 0, 0)
    assert certificate.twisted_four_point_action == (
        (0, 2, 1, 3),
        (1, 2, 3, 0),
    )
    assert certificate.twisted_four_point_covector == (1, 1, 1, 1, 1, 1)
    assert certificate.twisted_four_point_defect == (17, -8, -22, 28, -4, 14)
    assert certificate.twisted_four_point_value_mod_two == 1
    assert certificate.twisted_four_point_operator_rank == 5
    assert certificate.twisted_four_point_augmented_rank == 6


def test_nine_functionals_close_every_seven_direction_class() -> None:
    certificate = period_two_seven_direction_obstruction_certificate()

    assert certificate.identity_four_point_action == (
        (0, 1, 2, 3),
        (1, 2, 3, 0),
    )
    assert certificate.identity_four_point_covectors == (
        (0, 1, 0, 0, 1, 0),
        (1, 0, 1, 1, 0, 1),
    )
    assert certificate.identity_four_point_operator_rank == 4
    assert certificate.identity_four_point_covector_rank == 2
    assert certificate.quadratic_model_replays == 36
    assert certificate.quadratic_validation_replays == 28
    assert certificate.coefficient_class_count == 16384
    assert certificate.undetected_classes == ()
    assert certificate.coefficient_table_sha256 == (
        "0324d0c53b8247d06cb6f932b6859bc8bb319499290183ff71e6e979140353c2"
    )
    assert certificate.known_integer_span_obstructed
