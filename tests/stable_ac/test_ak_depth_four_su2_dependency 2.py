from fractions import Fraction

from experiments.stable_ac.depth4_su2_dependency_certificate import (
    dependency_hypergroup_certificate,
    normalized_final_interval,
)


def test_dependency_recurrence_equals_flat_three_a_five_b_interval() -> None:
    certificate = dependency_hypergroup_certificate()

    assert certificate.flat_polygon_row_count == 24
    assert certificate.dependency_elimination_counts == (28, 32, 60, 278)
    assert certificate.nonbox_facet_count == 4
    assert certificate.vertex_count == 12
    assert certificate.dependency_lift_count == 12


def test_exact_common_interval_has_the_four_projected_facets() -> None:
    assert normalized_final_interval(Fraction(1, 10), Fraction(0)) == (
        Fraction(0),
        Fraction(3, 10),
    )
    assert normalized_final_interval(Fraction(4, 5), Fraction(1)) == (
        Fraction(0),
        Fraction(3, 5),
    )
    assert normalized_final_interval(Fraction(1), Fraction(1, 10)) == (
        Fraction(1, 2),
        Fraction(1),
    )
    assert normalized_final_interval(Fraction(1, 10), Fraction(1)) == (
        Fraction(7, 10),
        Fraction(1),
    )
