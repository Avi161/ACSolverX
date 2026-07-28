from experiments.stable_ac.depth4_target_basis_certificate import (
    boundary_cancellation_rules,
    target_basis_certificate,
)


def test_pure_companion_power_seams_have_cyclic_length_at_least_twenty_five() -> None:
    certificate = target_basis_certificate()

    assert certificate.source_a_kernel_length == 6
    assert certificate.source_b_kernel_length == 5
    assert certificate.expanded_kernel_length == 43
    assert certificate.maximum_cancellation_pairs == 9
    assert certificate.minimum_cyclic_length == 25
    assert certificate.maximum_is_attained_at == (0, 0, 0, 0)


def test_only_three_axial_block_boundary_rules_can_cancel() -> None:
    assert boundary_cancellation_rules() == {
        ("B", "B"): (4, 1),
        ("B", "D"): (-2, 1),
        ("D", "B"): (0, 2),
    }
