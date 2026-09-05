from experiments.stable_ac.depth4_period_two_degree_two_escape_certificate import (
    period_two_degree_two_escape_certificate,
)


def test_one_hop_relation_module_system_has_exact_nullity_two() -> None:
    certificate = period_two_degree_two_escape_certificate()

    assert certificate.local_matrix_shape == (449, 242)
    assert certificate.local_matrix_nonzero == 880
    assert certificate.local_matrix_ranks == ((2, 240), (3, 240), (5, 240))
    assert certificate.local_kernel_dimension == 2


def test_four_first_layer_parity_classes_are_all_blocked_in_degree_two() -> None:
    certificate = period_two_degree_two_escape_certificate()

    assert certificate.parity_classes == ((0, 0), (1, 0), (0, 1), (1, 1))
    assert certificate.degree_two_obstructions == (
        (1, 1),
        (0, 1),
        (0, 1),
        (1, 0),
    )
    assert all(any(obstructions) for obstructions in certificate.degree_two_obstructions)


def test_any_degree_two_lift_must_escape_the_one_hop_support() -> None:
    certificate = period_two_degree_two_escape_certificate()

    assert certificate.residual_lengths == (82, 442, 678, 614)
    assert certificate.kernel_lengths == (24, 104, 212, 178)
    assert certificate.escape_required
