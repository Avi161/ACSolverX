from experiments.stable_ac.depth4_period_two_eleven_direction_obstruction_certificate import (
    period_two_eleven_direction_obstruction_certificate,
)


def test_eleventh_source_direction_is_exact_and_independent() -> None:
    certificate = period_two_eleven_direction_obstruction_certificate()
    assert certificate.syzygy_entries == 44
    assert certificate.syzygy_l1 == 55
    assert certificate.component_image_stats == (
        (12, 12), (0, 0), (22, 30), (30, 36), (30, 36),
    )
    assert certificate.homogeneous_image == ()
    assert certificate.tenth_and_eleventh_direction_ranks_mod_two == (10, 11)


def test_double_transposition_detects_the_eleventh_direction() -> None:
    certificate = period_two_eleven_direction_obstruction_certificate()
    assert certificate.eleventh_residual_length == 1696
    assert certificate.eleventh_kernel_length == 228
    assert certificate.eleventh_degree_two_terms == 515
    assert certificate.eleventh_degree_two_l1 == 956
    assert certificate.eleventh_prior_mod_two_bits == (0,) * 13
    assert certificate.new_action == ((0, 2, 1, 3), (1, 0, 3, 2))
    assert certificate.new_covectors == (
        (0, 0, 1, 1, 0, 0),
        (1, 1, 0, 0, 1, 1),
    )
    assert certificate.new_defect == (-29, -6, -3, 20, -14, 19)
    assert certificate.new_values_mod_two == (1, 0)
    assert certificate.new_operator_rank == 4
    assert certificate.new_covector_rank == 2
    assert certificate.new_augmented_rank == 5


def test_fifteen_functionals_close_every_eleven_direction_class() -> None:
    certificate = period_two_eleven_direction_obstruction_certificate()
    assert certificate.quadratic_model_replays == 78
    assert certificate.quadratic_validation_replays == 66
    assert certificate.coefficient_class_count == 4194304
    assert certificate.undetected_classes == ()
    assert certificate.coefficient_table_sha256 == (
        "297fcafd277a752eff9b26b2de69f5de4540eebad8c76c31356cd8d478651912"
    )
    assert certificate.known_integer_span_obstructed
