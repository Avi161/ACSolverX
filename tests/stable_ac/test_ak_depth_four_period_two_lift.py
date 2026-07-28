from experiments.stable_ac.depth4_period_two_lift_certificate import (
    period_two_lift_certificate,
)


def test_literal_lift_has_the_exact_free_group_defect() -> None:
    certificate = period_two_lift_certificate()

    assert certificate.row_lengths == (49, 63, 116, 177, 178)
    assert certificate.quotient_z_literal == "t"
    assert certificate.defect_terms == 21
    assert certificate.defect_l1 == 48
    assert certificate.defect_augmentation == 0


def test_lift_derivative_has_the_claimed_finite_operators() -> None:
    certificate = period_two_lift_certificate()

    assert certificate.operator_term_counts == (6, 4, 2, 2, 2)
    assert certificate.operator_augmentations == (0, 0, 0, 0, 0)


def test_eight_term_integral_correction_kills_the_relation_module_defect() -> None:
    certificate = period_two_lift_certificate()

    assert certificate.correction == (
        (0, 2, "cT"),
        (0, -2, "cTTct"),
        (0, -2, "cTTctt"),
        (2, -2, "cTct"),
        (2, -2, "cTctt"),
        (3, -2, ""),
        (3, -1, "TTct"),
        (4, 1, "Tct"),
    )
    assert certificate.correction_l1 == 14
    assert certificate.corrected_defect == ()
    assert certificate.corrected_direct_defect == ()
    assert certificate.corrected_residual_length > 0
