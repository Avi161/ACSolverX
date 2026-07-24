import hashlib
from pathlib import Path

import pytest

from experiments.stable_ac.thickenable.neuwirth_dart_audit import (
    CornerDarts,
    audit_trace,
)
from experiments.stable_ac.thickenable.neuwirth_permutation_certificate import (
    enumerate_trace,
)
from experiments.stable_ac.thickenable.neuwirth_target_certificate import (
    build_certificate,
    verify_certificate,
)


TARGETS = (
    ("xxxYYYY", "xyxYXY"),
    ("YYXXyx", "YYYxyXX"),
)


@pytest.mark.parametrize("words", TARGETS)
def test_independent_ordered_trace_agrees(words):
    direct = enumerate_trace(words)
    audit = audit_trace(words)

    assert audit.enumerated_cases == direct.enumerated_cases == 86_400
    assert audit.trace_sha256 == direct.trace_sha256
    assert audit.defect_histogram == direct.defect_histogram
    assert audit.accepting_orders == direct.accepting_orders


def test_corner_first_numbering_and_independent_tube_pairing():
    data = CornerDarts.from_words(("xy",))

    assert data.alpha == (1, 0, 3, 2)
    assert data.departure == (3, 1)
    assert data.arrival == (0, 2)
    assert data.tube_pair == (3, 2, 1, 0)


def test_audit_has_no_direct_or_prototype_dependency():
    source = Path(
        "experiments/stable_ac/thickenable/neuwirth_dart_audit.py"
    ).read_text()

    assert "neuwirth_permutation_certificate" not in source
    assert "check_thickenable" not in source


def test_certificate_schema_replay_and_fail_closed_verdicts():
    targets = {
        "negative": ("XXYXZYYZZ",),
        "transitive": ("xyY", "y"),
        "nontransitive_trivial": ("x", "y"),
    }
    source_commit = "0123456789abcdef"

    certificate = build_certificate(targets, source_commit=source_commit)

    assert set(certificate) == {
        "schema",
        "composition",
        "targets",
        "source_commit",
        "direct_module_sha256",
        "audit_module_sha256",
    }
    assert certificate["schema"] == "ak3-neuwirth-census-v1"
    assert certificate["composition"] == "right-to-left: PQ(e)=P(Q(e))"
    assert certificate["source_commit"] == source_commit

    direct_path = Path(
        "experiments/stable_ac/thickenable/neuwirth_permutation_certificate.py"
    )
    audit_path = Path(
        "experiments/stable_ac/thickenable/neuwirth_dart_audit.py"
    )
    assert certificate["direct_module_sha256"] == hashlib.sha256(
        direct_path.read_bytes()
    ).hexdigest()
    assert certificate["audit_module_sha256"] == hashlib.sha256(
        audit_path.read_bytes()
    ).hexdigest()

    expected_target_fields = {
        "words",
        "degrees",
        "expected_cases",
        "enumerated_cases",
        "defect_histogram",
        "minimum_genus",
        "accepting_orders",
        "direct_trace_sha256",
        "audit_trace_sha256",
        "verdict",
    }
    for target in certificate["targets"].values():
        assert set(target) == expected_target_fields
        assert target["expected_cases"] == target["enumerated_cases"]
        assert target["direct_trace_sha256"] == target["audit_trace_sha256"]

    assert certificate["targets"]["negative"]["verdict"] == (
        "NOT_THICKENABLE_EXACT_COMPLEX"
    )
    assert certificate["targets"]["negative"]["accepting_orders"] == []
    assert certificate["targets"]["transitive"]["verdict"] == "REGINA_REQUIRED"
    assert all(
        order["boundary_orbits_BC"] == 1
        for order in certificate["targets"]["transitive"]["accepting_orders"]
    )
    assert certificate["targets"]["nontransitive_trivial"]["verdict"] == (
        "AUDIT_CONTRADICTION"
    )
    assert all(
        order["boundary_orbits_BC"] > 1
        for order in certificate["targets"]["nontransitive_trivial"][
            "accepting_orders"
        ]
    )
    assert verify_certificate(certificate) is True
