import copy
from collections import Counter

import pytest

from experiments.equivalence_classes.lib.acmoves import canon
import experiments.stable_ac.thickenable.scan_ak3_component as scanner
from experiments.stable_ac.thickenable.scan_ak3_component import (
    AK3,
    CEILING,
    POP_CAP,
    CertificateError,
    GREEDY_BASELINE_PATH,
    RANK_SOLVER_PATH,
    SOURCE_PATHS,
    _authenticate_binding,
    _head_commit,
    _implementation_record,
    _source_binding,
    build_certificate,
    build_scan_payload,
    recompute_component,
    verify_certificate,
    verify_scan_payload,
)


@pytest.fixture(scope="module")
def scan_payload():
    return build_scan_payload()


def test_component_is_exactly_exhausted_and_closed_at_the_hard_cap():
    component = recompute_component()
    assert component.root == AK3 == ("xxxYYYY", "xyxYXY")
    assert component.ceiling == CEILING == 17
    assert component.node_budget == POP_CAP == 1_000
    assert component.actual_pops == component.component_size == 1_000
    assert component.queue_exhausted
    assert component.closure_verified
    assert component.child_options == {
        "cap": 16,
        "cyclic": True,
        "seam_only": False,
    }
    assert component.canonical_fixed_points_verified
    assert canon(*component.canonical_root, cyclic=True) == (
        component.canonical_root
    )
    assert all(canon(*state, cyclic=True) == state for state in component.states)
    assert component.sorted_state_sha256 == (
        "630a583617aa0f24ac365eca2d5b151d2dd9e3f6a963130a0b36009871cb0361"
    )


def test_all_states_are_decided_with_no_unsupported_or_unreplayed_case(
    scan_payload,
):
    payload = scan_payload
    assert payload["component"]["component_size"] == 1_000
    assert payload["support_histogram"] == {"K4": 720, "K4-e": 278, "C4": 2}
    assert payload["verdict_histogram"] == {"NOT_SPHERICAL": 1_000}
    assert len(payload["states"]) == 1_000
    assert len({tuple(record["words"]) for record in payload["states"]}) == 1_000

    for record in payload["states"]:
        assert record["verdict"] == "NOT_SPHERICAL"
        assert record["disposition"] == "NOT_THICKENABLE_EXACT_COMPLEX"
        assert record["witness"] is None
        counters = record["counters"]
        assert counters["exhaustive"]
        assert counters["schemes_considered"] == counters["scheme_budget"]
        assert (
            counters["phase_pairs_considered"]
            == counters["phase_pair_budget"]
        )
        assert (
            counters["component_seed_attempts"]
            == counters["component_seed_budget"]
        )
        assert (
            counters["component_combinations_considered"]
            == counters["component_combination_budget"]
        )
        assert counters["witness_replay_failures"] == 0

    assert Counter(record["support"] for record in payload["states"]) == {
        "K4": 720,
        "K4-e": 278,
        "C4": 2,
    }
    assert payload["decision_sha256"] == (
        "04d662297d88910a423e955eb5456bdb6f6bbe4fb88e4e47879ab6bf6a6e660e"
    )


def test_scan_payload_verifier_compares_every_record_and_digest(scan_payload):
    payload = scan_payload
    verify_scan_payload(payload, payload)

    changed_record = copy.deepcopy(payload)
    changed_record["states"][511]["counters"]["component_seed_attempts"] += 1
    with pytest.raises(CertificateError, match="state records"):
        verify_scan_payload(changed_record, payload)

    changed_digest = copy.deepcopy(payload)
    changed_digest["decision_sha256"] = "0" * 64
    with pytest.raises(CertificateError, match="decision digest"):
        verify_scan_payload(changed_digest, payload)

    changed_options = copy.deepcopy(payload)
    changed_options["component"]["child_options"]["seam_only"] = True
    with pytest.raises(CertificateError, match="component metadata"):
        verify_scan_payload(changed_options, payload)

    noncanonical = copy.deepcopy(payload)
    noncanonical["states"][0]["words"] = list(reversed(payload["states"][0]["words"]))
    with pytest.raises(CertificateError, match="state records"):
        verify_scan_payload(noncanonical, payload)


def test_source_binding_authenticates_commit_blob_and_current_blob():
    source_commit = _head_commit()
    binding = _source_binding(RANK_SOLVER_PATH, source_commit)
    assert binding["path"] == RANK_SOLVER_PATH
    assert (
        binding["source_commit_sha256"]
        == binding["current_sha256"]
    )
    _authenticate_binding(binding, source_commit)

    changed = copy.deepcopy(binding)
    changed["current_sha256"] = "0" * 64
    with pytest.raises(CertificateError, match="recorded current hash"):
        _authenticate_binding(changed, source_commit)


def test_transitive_acmoves_dependency_is_bound_and_named():
    assert SOURCE_PATHS["greedy_baseline"] == GREEDY_BASELINE_PATH
    implementation = _implementation_record()
    assert implementation["acmoves_dependencies"] == {
        "greedy_baseline": "greedy_baseline"
    }
    assert implementation["move_generator"]["options"] == {
        "cap": 16,
        "cyclic": True,
        "seam_only": False,
    }


def test_certificate_assembler_rechecks_head_cleanliness_and_all_bindings(
    monkeypatch,
):
    source_commit = "a" * 40
    bindings = {
        name: {
            "path": path,
            "source_commit_sha256": name,
            "current_sha256": name,
        }
        for name, path in SOURCE_PATHS.items()
    }
    source = {"commit": source_commit, "bindings": bindings}
    events = []

    monkeypatch.setattr(
        scanner,
        "_require_clean_tracked_worktree",
        lambda: events.append("clean"),
    )
    monkeypatch.setattr(
        scanner, "_head_commit", lambda: events.append("head") or source_commit
    )
    monkeypatch.setattr(
        scanner,
        "_source_record",
        lambda commit: events.append("source") or copy.deepcopy(source),
    )
    monkeypatch.setattr(
        scanner,
        "build_scan_payload",
        lambda: events.append("payload") or {"schema": "payload"},
    )

    certificate = build_certificate()
    assert events == [
        "clean",
        "head",
        "source",
        "payload",
        "clean",
        "head",
        "source",
    ]
    assert certificate["source"] == source
    assert set(certificate["source"]["bindings"]) == set(SOURCE_PATHS)
    assert certificate["implementations"] == _implementation_record()


def test_certificate_assembler_rejects_head_or_binding_change(monkeypatch):
    commits = iter(("a" * 40, "b" * 40))
    monkeypatch.setattr(scanner, "_require_clean_tracked_worktree", lambda: None)
    monkeypatch.setattr(scanner, "_head_commit", lambda: next(commits))
    monkeypatch.setattr(
        scanner,
        "_source_record",
        lambda commit: {"commit": commit, "bindings": {}},
    )
    monkeypatch.setattr(scanner, "build_scan_payload", lambda: {"schema": "x"})
    with pytest.raises(CertificateError, match="HEAD changed"):
        build_certificate()

    monkeypatch.setattr(scanner, "_head_commit", lambda: "a" * 40)
    sources = iter(
        (
            {"commit": "a" * 40, "bindings": {"scanner": {"hash": "one"}}},
            {"commit": "a" * 40, "bindings": {"scanner": {"hash": "two"}}},
        )
    )
    monkeypatch.setattr(scanner, "_source_record", lambda commit: next(sources))
    with pytest.raises(CertificateError, match="source bindings changed"):
        build_certificate()


def test_production_verifier_rebuilds_payload_after_source_authentication(
    monkeypatch, scan_payload
):
    certificate = copy.deepcopy(scan_payload)
    certificate["source"] = {"commit": "a" * 40, "bindings": {}}
    certificate["implementations"] = _implementation_record()
    events = []
    monkeypatch.setattr(
        scanner,
        "_authenticate_source",
        lambda value: events.append(("source", value["source"]["commit"])),
    )
    monkeypatch.setattr(
        scanner,
        "build_scan_payload",
        lambda: events.append(("rebuild", len(scan_payload["states"])))
        or copy.deepcopy(scan_payload),
    )
    verify_certificate(certificate)
    assert events == [("source", "a" * 40), ("rebuild", 1_000)]
