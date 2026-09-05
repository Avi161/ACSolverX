from fractions import Fraction

from experiments.stable_ac.depth4_period_two_elliptic_certificate import (
    period_two_elliptic_certificate,
)


def test_projective_quaternion_images_respect_the_period_two_relation() -> None:
    certificate = period_two_elliptic_certificate()

    assert certificate.c_square == certificate.central_minus_one
    assert certificate.t_norm == (Fraction(1), Fraction(0))


def test_fixed_rows_have_the_exact_separating_images() -> None:
    certificate = period_two_elliptic_certificate()

    assert certificate.source_b == certificate.central_minus_one
    assert certificate.source_a == (
        (Fraction(0), Fraction(1, 2)),
        (Fraction(0), Fraction(0)),
        (Fraction(0), Fraction(0)),
        (Fraction(0), Fraction(-1, 2)),
    )


def test_projective_conjugacy_invariant_separates_a_from_c() -> None:
    certificate = period_two_elliptic_certificate()

    assert certificate.source_b_is_projective_identity
    assert certificate.c_scalar_square == Fraction(0)
    assert certificate.source_a_scalar_square == Fraction(1, 2)
    assert certificate.source_a_scalar_square != certificate.c_scalar_square
