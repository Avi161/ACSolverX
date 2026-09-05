from experiments.stable_ac.depth4_period_two_five_direction_obstruction_certificate import (
    period_two_five_direction_obstruction_certificate,
)


def test_integral_combination_clears_the_previous_five_bits() -> None:
    certificate = period_two_five_direction_obstruction_certificate()

    assert certificate.combination_coefficients == (0, 0, 0, 2, -1)
    assert certificate.combination_entries == 36
    assert certificate.combination_l1 == 58
    assert certificate.residual_length == 542
    assert certificate.kernel_length == 134
    assert certificate.relation_module_terms == 0
    assert certificate.degree_two_terms == 264
    assert certificate.degree_two_l1 == 602
    assert certificate.full_wedge_sum == -2
    assert certificate.three_point_defect == (24, -55, 9)
    assert certificate.four_point_defect == (0, 1, 19, 10, -8, -14)
    assert certificate.cyclic_defect == (-3, -5, -2)
    assert certificate.cyclic_signed_mod_three == 0


def test_new_three_point_action_detects_the_integral_combination() -> None:
    certificate = period_two_five_direction_obstruction_certificate()

    assert certificate.new_three_point_action == (
        (0, 2, 1),
        (1, 0, 2),
    )
    assert certificate.new_three_point_defect == (7, -10, 20)
    assert certificate.new_obstruction_mod_two == 1
    assert certificate.operator_rank_mod_two == 2
    assert certificate.augmented_rank_mod_two == 3


def test_five_mod_two_functionals_close_every_mod_four_class() -> None:
    certificate = period_two_five_direction_obstruction_certificate()

    assert certificate.known_direction_rank_mod_two == 5
    assert certificate.known_coefficient_modulus == 4
    assert certificate.known_coefficient_class_count == 1024
    assert certificate.known_coefficient_undetected == ()
    assert certificate.known_coefficient_table_sha256 == (
        "6910f180e44cfc215ccf5fc2d668498993673484b829e7210d436551e194c1d5"
    )
    assert certificate.known_integer_span_obstructed
