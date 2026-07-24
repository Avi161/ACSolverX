from experiments.stable_ac.rank3_compression.ridge_return_certificate import (
    ORBIT2,
    build_certificate,
    extract_ridge_roots,
    verify_certificate,
)


def test_extracts_exactly_five_floor_fifteen_roots():
    roots, minimum, trace = extract_ridge_roots()
    assert len(roots) == 5
    assert minimum == 15
    assert trace == (
        "925532ca88d917931f577cc1b4e14ad"
        "1e4204b8064c92b1a590345d236e4fd14"
    )


def test_ridge_return_certificate_replays():
    data = build_certificate()
    assert data["schema"] == "ak3-ridge-return-v1"
    assert data["ridge"]["root_count"] == 5
    assert data["ridge"]["distinct_root_child_count"] == 540
    assert data["ridge"]["distinct_child_count"] == 536
    assert data["ridge"]["minimum_child_floor"] == 13
    assert data["minimum_representatives"] == [list(ORBIT2)]
    assert data["return_proposition"] == "PROVED"
    verify_certificate(data, verify_upstream=False)
