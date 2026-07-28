from experiments.stable_ac.depth4_period_two_cyclic_degree_two_obstruction_certificate import (
    period_two_cyclic_degree_two_obstruction_certificate,
)


def test_cyclic_three_point_action_separates_the_phi4_escape_lift() -> None:
    certificate = period_two_cyclic_degree_two_obstruction_certificate()

    assert certificate.cyclic_action == (
        (0, 1, 2),
        (1, 2, 0),
    )
    assert certificate.projected_defect == (-1, -3, -3)
    assert certificate.projected_sum == -7
    assert certificate.operator_augmentations == (0, 0, 0, 0, 0)
    assert certificate.operator_rank_mod_two == 2
    assert certificate.augmented_rank_mod_two == 3
    assert certificate.obstruction == 1


def test_four_functionals_separate_the_known_affine_span() -> None:
    certificate = period_two_cyclic_degree_two_obstruction_certificate()

    assert certificate.known_affine_bits == (
        ((0, 0, 0, 0), (1, 1, 1, 1)),
        ((0, 0, 0, 1), (0, 0, 0, 1)),
        ((0, 0, 1, 0), (0, 0, 1, 1)),
        ((0, 0, 1, 1), (1, 1, 0, 1)),
        ((0, 1, 0, 0), (0, 1, 0, 0)),
        ((0, 1, 0, 1), (1, 1, 0, 1)),
        ((0, 1, 1, 0), (1, 0, 0, 0)),
        ((0, 1, 1, 1), (0, 0, 0, 1)),
        ((1, 0, 0, 0), (0, 1, 0, 0)),
        ((1, 0, 0, 1), (1, 0, 1, 0)),
        ((1, 0, 1, 0), (1, 0, 1, 0)),
        ((1, 0, 1, 1), (0, 1, 0, 0)),
        ((1, 1, 0, 0), (1, 0, 1, 1)),
        ((1, 1, 0, 1), (0, 0, 1, 0)),
        ((1, 1, 1, 0), (0, 1, 0, 1)),
        ((1, 1, 1, 1), (1, 1, 0, 0)),
    )
    assert certificate.known_affine_span_separated
