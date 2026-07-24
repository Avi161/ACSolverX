import copy
import json

import pytest

from experiments.stable_ac.rank3_compression.primitive_single_certificate import (
    RESULT_PATH as PRIMITIVE_SINGLE_PATH,
)
from experiments.stable_ac.thickenable.rank3_rigid_thickenability_certificate import (
    build_certificate,
    verify_certificate,
)


def _fixture_source():
    with PRIMITIVE_SINGLE_PATH.open() as handle:
        upstream = json.load(handle)
    return 250, tuple(upstream["sources"][250])


def test_small_rank3_rigid_certificate_replays():
    source = _fixture_source()
    data = build_certificate(
        sources=(source,),
        upstream_trace="test",
        run_factorial_crosscheck=False,
    )
    assert data["schema"] == "ak3-rank3-rigid-thickenability-v1"
    assert data["source_count"] == 1
    assert data["support_counts"] == {"K6-P5": 1}
    assert data["verdict_counts"] == {"NOT_SPHERICAL": 1}
    assert data["candidate_lemma"] == "REFUTED"
    assert data["aggregate_counters"]["phase_tuples_considered"] == 1_859
    verify_certificate(
        data,
        verify_upstream=False,
        run_factorial_crosscheck=False,
    )


def test_rank3_rigid_certificate_rejects_counter_tampering():
    source = _fixture_source()
    data = build_certificate(
        sources=(source,),
        upstream_trace="test",
        run_factorial_crosscheck=False,
    )
    tampered = copy.deepcopy(data)
    tampered["source_records"][0]["counters"][
        "component_seed_attempts"
    ] -= 1
    with pytest.raises(AssertionError, match="complete replay"):
        verify_certificate(
            tampered,
            verify_upstream=False,
            run_factorial_crosscheck=False,
        )
