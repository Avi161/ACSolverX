from experiments.stable_ac.depth4_period_two_source_flow_certificate import (
    source_flow_certificate,
)


def test_six_vertex_action_classes_and_signatures() -> None:
    """A changed quotient action or orbit partition changes these source columns."""
    certificate = source_flow_certificate()

    assert certificate.vertex_action_classes == 6
    assert certificate.representative_signatures == (
        ("", (2, -2), (1, -1)),
        ("T", (1, -1), (-1, 1)),
        ("t", (-1, 1), (0, 0)),
        ("cT", (-1, 1), (1, -1)),
        ("ct", (1, -1), (0, 0)),
        ("Tct", (-2, 2), (-1, 1)),
    )


def test_result_153_through_157_sources_reconstruct() -> None:
    """The generic L0 flow replay must recover each published two-source direction."""
    fixtures = (
        (("T", 1), ("ttttct", 1)),
        (("T", 1), ("TTct", 1)),
        (("TT", 1), ("tcTct", 1)),
        (("cT", 1), ("TcTTT", 1)),
        (("TTcttt", 1), ("cTcTct", 1)),
    )
    certificate = source_flow_certificate()

    assert certificate.known_sources == fixtures
    assert certificate.known_reconstructions == 5
