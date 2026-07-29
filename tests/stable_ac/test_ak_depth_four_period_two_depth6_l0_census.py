from experiments.stable_ac.depth4_period_two_depth6_l0_census_certificate import (
    depth6_l0_census_certificate,
)


def test_projected_bits_match_direct_wedge_on_known_directions() -> None:
    """Streaming finite quotients must agree with the direct full wedge."""
    certificate = depth6_l0_census_certificate()

    assert certificate.projected_direct_fixtures == 5
    assert certificate.projected_direct_matches == 5


def test_depth_six_balanced_l0_census() -> None:
    """Every balanced two-source L0 direction through depth six is detected."""
    certificate = depth6_l0_census_certificate()

    assert certificate.max_source_depth == 6
    assert certificate.source_vertices == 127
    assert certificate.balanced_pairs == 4671
    assert certificate.projected_near_survivors == (
        ("TT", "TTTct", 1, 1),
        ("Tctt", "Tctct", 1, 1),
    )
    assert certificate.zero_syndrome_pairs == ()
    assert certificate.census_sha256 == (
        "02a688c2e0bfd1831202c6b76f8d3af9b4340c71e08d9b1e2efeea59d8301ff3"
    )
