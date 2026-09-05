from fractions import Fraction

from experiments.stable_ac.depth4_three_class_certificates import (
    three_class_certificates,
)


def test_three_class_certificates_close_five_metric_residues() -> None:
    certificates = three_class_certificates()

    assert {certificate.signature for certificate in certificates} == {
        (7, 3, 4, -3, 2),
        (7, 3, 4, -3, 4),
        (7, 4, 3, -2, -3),
        (8, 3, 5, -3, 1),
        (8, 5, 3, -3, 1),
    }
    assert all(
        certificate.target_vector
        == (
            3 * certificate.signature[3] + certificate.signature[4],
            -4 * certificate.signature[3] - certificate.signature[4],
        )
        for certificate in certificates
    )
    assert all(certificate.source_scalar.lower > Fraction(1, 2) for certificate in certificates)
    assert all(certificate.margin.lower > Fraction(1, 1000) for certificate in certificates)
