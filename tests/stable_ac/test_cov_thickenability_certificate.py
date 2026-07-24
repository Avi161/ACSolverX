import copy

import pytest

from experiments.stable_ac.thickenable.cov_thickenability_certificate import (
    build_certificate,
    verify_certificate,
)


def test_ak3_cov_thickenability_certificate_replays():
    data = build_certificate(run_factorial_crosscheck=False)
    assert data["schema"] == "ak3-cov-thickenability-v1"
    assert data["cov_output_count"] == 34
    assert data["stable_equivalence_count"] == 34
    assert data["support_counts"] == {
        "K4": 15,
        "K4+1loop": 2,
        "K4-e": 9,
        "K4-e+1loop": 8,
    }
    assert data["verdict_counts"] == {"NOT_SPHERICAL": 34}
    assert data["candidate_lemma"] == "REFUTED"
    verify_certificate(data, run_factorial_crosscheck=False)


def test_ak3_cov_thickenability_certificate_rejects_tampering():
    data = build_certificate(run_factorial_crosscheck=False)
    tampered = copy.deepcopy(data)
    tampered["output_records"][0]["counters"][
        "component_seed_attempts"
    ] -= 1
    with pytest.raises(AssertionError, match="complete replay"):
        verify_certificate(tampered, run_factorial_crosscheck=False)
