from experiments.stable_ac.depth4_period_two_source_flow_certificate import (
    build_l0_direction,
    build_l0_direction_from_pairs,
    lift,
    source_flow_certificate,
    source_from_entries,
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


def test_raw_source_collisions_cancel_and_sum_before_flow_replay() -> None:
    """Raw coset aliases must aggregate before their L0 boundary is paired."""
    cancelled = build_l0_direction({(): 1, (lift.C,): -1})
    doubled = build_l0_direction({
        (): 1,
        (lift.C,): 1,
        lift.parse_quotient("Tct"): 2,
    })

    assert cancelled.source == ()
    assert cancelled.paths == ()
    assert cancelled.variables == ({}, {}, {}, {}, {})
    assert doubled.source == (("", 2), ("Tct", 2))


def test_crossed_result_153_pairing_changes_paths_not_sparse_variables() -> None:
    """The forest flow is fixed by the boundary, not its endpoint matching."""
    source = source_from_entries((("T", 1), ("ttttct", 1)))
    canonical = build_l0_direction(source)
    crossed = build_l0_direction_from_pairs(
        source,
        (
            (lift.parse_quotient("ctcTTTcttcT"), lift.parse_quotient("tcttttct")),
            (lift.parse_quotient("cTTcttcttttct"), lift.parse_quotient("ctcTctcT")),
            (lift.parse_quotient("ctcTTTTcttcttttct"), lift.parse_quotient("ctcTcTctcT")),
            (lift.parse_quotient("cTTcttcT"), lift.parse_quotient("tcT")),
            (lift.parse_quotient("ctcTTTTcttcT"), lift.parse_quotient("ctcTctcttttct")),
            (lift.parse_quotient("ctcTTTcttcttttct"), lift.parse_quotient("ctcTcTctcttttct")),
        ),
    )

    assert crossed.paths != canonical.paths
    assert crossed.variables == canonical.variables
