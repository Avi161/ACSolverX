import hashlib
import subprocess
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
    COMPOSITION,
    SCHEMA,
    TARGETS as CANONICAL_TARGETS,
    _verdict,
    build_certificate,
    verify_certificate,
)


TRACE_TARGETS = (
    ("xxxYYYY", "xyxYXY"),
    ("YYXXyx", "YYYxyXX"),
)


@pytest.mark.parametrize("words", TRACE_TARGETS)
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


def _head_commit() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _git_blob_sha256(commit: str, relative_path: str) -> str:
    content = subprocess.run(
        ["git", "show", f"{commit}:{relative_path}"],
        check=True,
        capture_output=True,
    ).stdout
    return hashlib.sha256(content).hexdigest()


def test_certificate_schema_and_fail_closed_verdicts():
    targets = {
        "negative": ("XXYXZYYZZ",),
        "untrusted_euler": ("x", "xyXY"),
        "trusted_transitive": ("xyY", "y"),
        "disconnected": ("x", "y"),
    }
    source_commit = "0" * 40

    certificate = build_certificate(
        targets,
        source_commit=source_commit,
        trusted_balanced_trivial_targets={"trusted_transitive"},
    )

    assert set(certificate) == {
        "schema",
        "composition",
        "targets",
        "source_commit",
        "direct_module_sha256",
        "audit_module_sha256",
        "driver_module_sha256",
    }
    assert certificate["schema"] == SCHEMA
    assert certificate["composition"] == COMPOSITION
    assert certificate["source_commit"] == source_commit

    direct_path = Path(
        "experiments/stable_ac/thickenable/neuwirth_permutation_certificate.py"
    )
    audit_path = Path(
        "experiments/stable_ac/thickenable/neuwirth_dart_audit.py"
    )
    driver_path = Path(
        "experiments/stable_ac/thickenable/neuwirth_target_certificate.py"
    )
    assert certificate["direct_module_sha256"] == hashlib.sha256(
        direct_path.read_bytes()
    ).hexdigest()
    assert certificate["audit_module_sha256"] == hashlib.sha256(
        audit_path.read_bytes()
    ).hexdigest()
    assert certificate["driver_module_sha256"] == hashlib.sha256(
        driver_path.read_bytes()
    ).hexdigest()

    expected_target_fields = {
        "words",
        "degrees",
        "expected_cases",
        "enumerated_cases",
        "link_components",
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
    assert certificate["targets"]["untrusted_euler"]["link_components"] == [1]
    assert certificate["targets"]["untrusted_euler"]["verdict"] == (
        "EULER_ACCEPTING_UNTRUSTED"
    )
    assert certificate["targets"]["trusted_transitive"]["verdict"] == (
        "REGINA_REQUIRED"
    )
    assert all(
        order["boundary_orbits_BC"] == 1
        for order in certificate["targets"]["trusted_transitive"][
            "accepting_orders"
        ]
    )
    assert certificate["targets"]["disconnected"]["link_components"] == [2]
    assert certificate["targets"]["disconnected"]["verdict"] == (
        "OUT_OF_SCOPE_DISCONNECTED_LINK"
    )


def test_trusted_connected_nontransitive_order_dominates():
    accepting_orders = (
        ((), (1, 2, 0, 1, 1)),
        ((), (1, 2, 0, 2, 1)),
    )

    assert _verdict(
        link_components={1},
        accepting_orders=accepting_orders,
        trusted_balanced_trivial=True,
    ) == "AUDIT_CONTRADICTION"


def test_verify_rejects_nonexistent_source_commit():
    certificate = build_certificate({}, source_commit="f" * 40)

    with pytest.raises(ValueError, match="source commit"):
        verify_certificate(certificate)


@pytest.mark.parametrize(
    "targets",
    [
        {},
        {"ak3": ("x",)},
        {"ak3": ("x",), "orbit_2": ("y",), "extra": ("z",)},
        {"ak3": ("x",), "orbit_2": ("y",)},
    ],
    ids=["empty", "missing", "extra", "changed"],
)
def test_verify_rejects_noncanonical_targets(targets):
    certificate = build_certificate(targets, source_commit=_head_commit())

    with pytest.raises(ValueError, match="canonical targets"):
        verify_certificate(certificate)


def test_verify_authenticates_recorded_module_hashes_against_source_commit():
    source_commit = _head_commit()
    certificate = {
        "schema": SCHEMA,
        "composition": COMPOSITION,
        "targets": {
            name: {"words": list(words)}
            for name, words in CANONICAL_TARGETS.items()
        },
        "source_commit": source_commit,
        "direct_module_sha256": _git_blob_sha256(
            source_commit,
            "experiments/stable_ac/thickenable/"
            "neuwirth_permutation_certificate.py",
        ),
        "audit_module_sha256": _git_blob_sha256(
            source_commit,
            "experiments/stable_ac/thickenable/neuwirth_dart_audit.py",
        ),
        "driver_module_sha256": _git_blob_sha256(
            source_commit,
            "experiments/stable_ac/thickenable/neuwirth_target_certificate.py",
        ),
    }

    for field in (
        "direct_module_sha256",
        "audit_module_sha256",
        "driver_module_sha256",
    ):
        corrupted = dict(certificate)
        corrupted[field] = "0" * 64
        with pytest.raises(AssertionError, match="recorded .* hash"):
            verify_certificate(corrupted)
