from fractions import Fraction

from experiments.stable_ac.depth4_metric_certificates import metric_certificates


def test_metric_certificates_close_nineteen_depth_four_rows() -> None:
    certificates = metric_certificates()

    certified_signatures = {
        (7, 3, 4, -3, -4),
        (7, 3, 4, -3, -2),
        (7, 3, 4, -1, 0),
        (7, 3, 4, -1, 2),
        (7, 4, 3, -4, -3),
        (7, 4, 3, -4, 3),
        (7, 4, 3, -2, -1),
        (7, 4, 3, -2, 1),
        (7, 4, 3, -2, 3),
        (7, 4, 3, 0, -1),
        (8, 3, 5, -3, -5),
        (8, 3, 5, -3, -1),
        (8, 3, 5, -1, -3),
        (8, 3, 5, -1, 1),
        (8, 5, 3, -5, -3),
        (8, 5, 3, -5, 3),
        (8, 5, 3, -3, -1),
        (8, 5, 3, -1, -3),
        (8, 5, 3, -1, 1),
    }
    assert {certificate.signature for certificate in certificates} == certified_signatures
    assert all(
        certificate.target_vector
        == (
            3 * certificate.signature[3] + certificate.signature[4],
            -4 * certificate.signature[3] - certificate.signature[4],
        )
        for certificate in certificates
    )
    assert all(certificate.source_a_scalar > 0 for certificate in certificates)
    assert all(certificate.source_b_scalar > 0 for certificate in certificates)
    assert all(-1 < certificate.target_scalar < 1 for certificate in certificates)
    assert all(certificate.source_a_tangent_square < 1 for certificate in certificates)
    assert all(certificate.source_b_tangent_square < 1 for certificate in certificates)
    assert all(certificate.margin > Fraction(1, 100) for certificate in certificates)
