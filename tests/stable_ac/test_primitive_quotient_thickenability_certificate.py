from experiments.stable_ac.thickenable.primitive_quotient_thickenability_certificate import (
    build_certificate,
    verify_certificate,
)


def test_small_primitive_quotient_thickenability_certificate_replays():
    data = build_certificate(
        outputs=(("X", "XY"), ("X", "XXXYXY")),
        upstream_trace="test",
        run_small_crosscheck=False,
    )
    assert data["schema"] == "ak3-primitive-quotient-thickenability-v1"
    assert data["distinct_output_count"] == 2
    assert data["verdict_counts"] == {
        "NOT_SPHERICAL": 1,
        "SPHERICAL_REQUIRES_REGINA": 1,
    }
    assert data["support_counts"] == {"P4": 2}
    verify_certificate(
        data,
        verify_upstream=False,
        run_small_crosscheck=False,
    )
