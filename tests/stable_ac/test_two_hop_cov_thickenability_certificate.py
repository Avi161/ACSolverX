import copy

import pytest

from experiments.stable_ac.thickenable.two_hop_cov_thickenability_certificate import (
    build_certificate,
    enumerate_two_hop_paths,
    verify_certificate,
)


def test_small_two_hop_cov_certificate_replays():
    first_hops, paths, raw_count = enumerate_two_hop_paths()
    data = build_certificate(
        first_hops=first_hops,
        paths=paths[:2],
        raw_second_hop_count=raw_count,
        upstream_trace="test",
        run_factorial_crosscheck=False,
    )
    assert data["schema"] == "ak3-two-hop-cov-thickenability-v1"
    assert data["first_hop_count"] == 34
    assert data["output_count"] == 2
    assert data["stable_equivalence_count"] == 2
    assert data["verdict_counts"] == {"NOT_SPHERICAL": 2}
    verify_certificate(
        data,
        verify_upstream=False,
        first_hops=first_hops,
        paths=paths[:2],
        raw_second_hop_count=raw_count,
        run_factorial_crosscheck=False,
    )


def test_two_hop_cov_certificate_rejects_tampering():
    first_hops, paths, raw_count = enumerate_two_hop_paths()
    data = build_certificate(
        first_hops=first_hops,
        paths=paths[:1],
        raw_second_hop_count=raw_count,
        upstream_trace="test",
        run_factorial_crosscheck=False,
    )
    tampered = copy.deepcopy(data)
    tampered["output_records"][0]["counters"][
        "component_seed_attempts"
    ] -= 1
    with pytest.raises(AssertionError, match="complete replay"):
        verify_certificate(
            tampered,
            verify_upstream=False,
            first_hops=first_hops,
            paths=paths[:1],
            raw_second_hop_count=raw_count,
            run_factorial_crosscheck=False,
        )
