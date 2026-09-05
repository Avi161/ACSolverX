from experiments.stable_ac.depth4_period_two_remote_syzygy_certificate import (
    period_two_remote_syzygy_certificate,
)


def test_remote_vector_is_an_exact_homogeneous_syzygy() -> None:
    certificate = period_two_remote_syzygy_certificate()

    assert certificate.support_entries == 23
    assert certificate.coefficient_l1 == 35
    assert certificate.component_image_stats == (
        (15, 20),
        (0, 0),
        (10, 20),
        (16, 22),
        (14, 20),
    )
    assert certificate.homogeneous_image == ()


def test_syzygy_escapes_one_hop_and_clears_the_first_two_bits() -> None:
    certificate = period_two_remote_syzygy_certificate()

    assert certificate.outside_one_hop == (
        (2, "cTT"),
        (3, "TTcTT"),
        (3, "TTctcTcT"),
        (4, "TcTT"),
    )
    assert certificate.residual_length == 476
    assert certificate.kernel_length == 124
    assert certificate.degree_two_terms == 170
    assert certificate.degree_two_coefficient_sum == 8
    assert certificate.old_obstructions == (0, 0)


def test_four_point_wedge_functional_detects_the_remote_lift() -> None:
    certificate = period_two_remote_syzygy_certificate()

    assert certificate.four_point_action == (
        (0, 1, 3, 2),
        (1, 2, 0, 3),
    )
    assert certificate.four_point_defect == (-5, 4, -36, 17, 15, -18)
    assert certificate.four_point_operator_rank == 5
    assert certificate.four_point_augmented_rank == 6
    assert certificate.four_point_obstruction == 1
