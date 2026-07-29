"""Exact prior-certificate boundary for the AK(3) Aut(F2) frontier."""

from __future__ import annotations

import json
from collections.abc import Callable
from hashlib import sha256
from pathlib import Path

import pytest

from experiments.stable_ac.thickenable import (
    ak3_aut_frontier_certificate as certificate,
)
from experiments.stable_ac.thickenable.ak3_aut_frontier_certificate import (
    PRIOR_EXACT_DUPLICATE,
    RANK3_RIGID_PATH,
    PriorCertificateSchemaError,
    build_prior_certificate_index,
    lookup_prior_exact,
)

_EXPECTED_FROZEN_PRIOR_CORPUS = (
    "results/stable_ac/theory/ak3_neuwirth_census.json",
    "results/stable_ac/theory/ak3_component_thickenability.json",
    "results/stable_ac/theory/ak3_cov_thickenability.json",
    "results/stable_ac/theory/ak3_two_hop_cov_thickenability.json",
    "results/stable_ac/theory/ak3_primitive_quotient_thickenability.json",
)
_ORACLE_INVERSE = {"x": "X", "X": "x", "y": "Y", "Y": "y"}


def _oracle_free_reduce(word: str) -> str:
    reduced: list[str] = []
    for letter in word:
        if reduced and reduced[-1] == _ORACLE_INVERSE[letter]:
            reduced.pop()
        else:
            reduced.append(letter)
    return "".join(reduced)


def _oracle_cyclic_peel(word: str) -> str:
    core = word
    while len(core) >= 2 and core[0] == _ORACLE_INVERSE[core[-1]]:
        core = core[1:-1]
    return core


def _write_fixture_corpus(root: Path) -> dict[str, bytes]:
    """Write one complete, hand-authored record for each frozen schema."""
    fixtures = {
        _EXPECTED_FROZEN_PRIOR_CORPUS[0]: {
            "schema": "ak3-neuwirth-census-v1",
            "targets": {
                "first": {"words": ["x", "y"], "verdict": "NOT_THICKENABLE_EXACT_COMPLEX"},
                "second": {"words": ["xx", "y"], "verdict": "NOT_THICKENABLE_EXACT_COMPLEX"},
            },
        },
        _EXPECTED_FROZEN_PRIOR_CORPUS[1]: {
            "schema": "ak3-component-thickenability-v1",
            "states": [
                {
                    "words": ["xx", "x"],
                    "verdict": "NOT_SPHERICAL",
                    "disposition": "NOT_THICKENABLE_EXACT_COMPLEX",
                }
            ],
        },
        _EXPECTED_FROZEN_PRIOR_CORPUS[2]: {
            "schema": "ak3-cov-thickenability-v1",
            "output_records": [
                {"index": 7, "words": ["xxY", "y"], "verdict": "NOT_SPHERICAL"}
            ],
        },
        _EXPECTED_FROZEN_PRIOR_CORPUS[3]: {
            "schema": "ak3-two-hop-cov-thickenability-v1",
            "output_records": [
                {"index": 9, "words": ["xx", "Y"], "verdict": "UNSUPPORTED"}
            ],
        },
        _EXPECTED_FROZEN_PRIOR_CORPUS[4]: {
            "schema": "ak3-primitive-quotient-thickenability-v1",
            "output_records": [{"words": ["XX", "y"], "verdict": "NOT_SPHERICAL"}],
        },
    }
    raw_bytes: dict[str, bytes] = {}
    for relative_path, payload in fixtures.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = json.dumps(payload, indent=2).encode("utf-8")
        path.write_bytes(raw)
        raw_bytes[relative_path] = raw
    return raw_bytes


def test_frozen_fixture_corpus_preserves_raw_words_order_hashes_and_provenance(
    tmp_path: Path,
) -> None:
    """Catches adapters that normalize spellings, reorder records, or lose provenance."""
    raw_bytes = _write_fixture_corpus(tmp_path)

    index = build_prior_certificate_index(tmp_path)

    assert index.schema == "ak3-aut-frontier-prior-index-v1"
    assert certificate.FROZEN_PRIOR_CORPUS == _EXPECTED_FROZEN_PRIOR_CORPUS
    assert index.corpus_paths == _EXPECTED_FROZEN_PRIOR_CORPUS
    assert RANK3_RIGID_PATH not in index.corpus_paths
    assert tuple(row.record_id for row in index.rows) == (
        "target:first",
        "target:second",
        "state:0",
        "output:7",
        "output:9",
        "output:0",
    )
    assert tuple(row.raw_relators for row in index.rows) == (
        ("x", "y"),
        ("xx", "y"),
        ("xx", "x"),
        ("xxY", "y"),
        ("xx", "Y"),
        ("XX", "y"),
    )
    assert tuple(row.verdict for row in index.rows) == (
        "NOT_THICKENABLE_EXACT_COMPLEX",
        "NOT_THICKENABLE_EXACT_COMPLEX",
        "NOT_SPHERICAL",
        "NOT_SPHERICAL",
        "UNSUPPORTED",
        "NOT_SPHERICAL",
    )
    assert tuple(row.source_sha256 for row in index.rows) == tuple(
        sha256(raw_bytes[path]).hexdigest()
        for path in _EXPECTED_FROZEN_PRIOR_CORPUS
        for _ in range(2 if path == _EXPECTED_FROZEN_PRIOR_CORPUS[0] else 1)
    )
    # Hand-derived: signed inversion sends (x, y) to the raw-ASCII least (X, Y).
    assert index.rows[0].cellular_key == ("X", "Y")


def test_exact_duplicate_returns_every_prior_row_in_its_frozen_bucket_order(
    tmp_path: Path,
) -> None:
    """Catches duplicate handling that drops/reorders provenance or claims a decision."""
    raw_bytes = _write_fixture_corpus(tmp_path)
    index = build_prior_certificate_index(tmp_path)

    match = lookup_prior_exact(index, ("xx", "y"))

    assert match is not None
    assert match.category == PRIOR_EXACT_DUPLICATE
    assert tuple(
        (
            row.corpus_path,
            row.source_sha256,
            row.record_id,
            row.raw_relators,
            row.verdict,
        )
        for row in match.provenance
    ) == (
        (
            _EXPECTED_FROZEN_PRIOR_CORPUS[0],
            sha256(raw_bytes[_EXPECTED_FROZEN_PRIOR_CORPUS[0]]).hexdigest(),
            "target:second",
            ("xx", "y"),
            "NOT_THICKENABLE_EXACT_COMPLEX",
        ),
        (
            _EXPECTED_FROZEN_PRIOR_CORPUS[3],
            sha256(raw_bytes[_EXPECTED_FROZEN_PRIOR_CORPUS[3]]).hexdigest(),
            "output:9",
            ("xx", "Y"),
            "UNSUPPORTED",
        ),
        (
            _EXPECTED_FROZEN_PRIOR_CORPUS[4],
            sha256(raw_bytes[_EXPECTED_FROZEN_PRIOR_CORPUS[4]]).hexdigest(),
            "output:0",
            ("XX", "y"),
            "NOT_SPHERICAL",
        ),
    )


@pytest.mark.parametrize(
    ("candidate", "reason"),
    (
        (("xXx", "y"), "free reduction"),
        (("xy", "y"), "ambient transvection"),
        (("xy", "y"), "AC relator multiplication"),
    ),
)
def test_non_exact_equivalences_are_not_prior_duplicate_evidence(
    tmp_path: Path, candidate: tuple[str, str], reason: str
) -> None:
    """Catches lookup widened beyond signed cellular symmetries into {reason}."""
    _write_fixture_corpus(tmp_path)
    index = build_prior_certificate_index(tmp_path)

    assert lookup_prior_exact(index, candidate) is None


def test_cyclic_reduction_only_equivalence_is_not_prior_duplicate_evidence(
    tmp_path: Path,
) -> None:
    """Catches lookup that strips a conjugating shell before exact-key comparison."""
    _write_fixture_corpus(tmp_path)
    index = build_prior_certificate_index(tmp_path)
    candidate = ("yxY", "y")

    assert _oracle_free_reduce(candidate[0]) == "yxY"
    assert _oracle_cyclic_peel(candidate[0]) == "x"
    assert _oracle_cyclic_peel(candidate[1]) == "y"
    assert lookup_prior_exact(index, candidate) is None


@pytest.mark.parametrize(
    ("relative_path", "mutate"),
    (
        (_EXPECTED_FROZEN_PRIOR_CORPUS[0], lambda payload: payload["targets"]["first"].pop("verdict")),
        (_EXPECTED_FROZEN_PRIOR_CORPUS[1], lambda payload: payload["states"][0].__setitem__("words", ["x"])),
        (_EXPECTED_FROZEN_PRIOR_CORPUS[2], lambda payload: payload["output_records"][0].pop("index")),
        (_EXPECTED_FROZEN_PRIOR_CORPUS[3], lambda payload: payload.__setitem__("schema", "wrong")),
        (_EXPECTED_FROZEN_PRIOR_CORPUS[4], lambda payload: payload["output_records"][0].__setitem__("words", ["x", "z"])),
    ),
)
def test_each_schema_adapter_fails_closed_on_missing_or_ambiguous_exact_data(
    tmp_path: Path, relative_path: str, mutate: Callable[[dict[str, object]], None]
) -> None:
    """Catches one of the five adapters accepting malformed rank, IDs, verdicts, or spelling."""
    _write_fixture_corpus(tmp_path)
    path = tmp_path / relative_path
    payload = json.loads(path.read_bytes())
    mutate(payload)
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(PriorCertificateSchemaError):
        build_prior_certificate_index(tmp_path)


def test_live_frozen_corpus_has_only_rank_two_rows_and_excludes_rank_three() -> None:
    """Catches accidental corpus extension or a live rank-three ingestion path."""
    index = build_prior_certificate_index()

    assert certificate.FROZEN_PRIOR_CORPUS == _EXPECTED_FROZEN_PRIOR_CORPUS
    assert index.corpus_paths == _EXPECTED_FROZEN_PRIOR_CORPUS
    assert RANK3_RIGID_PATH not in index.corpus_paths
    assert len(index.rows) == 2_691
    assert all(len(row.raw_relators) == 2 for row in index.rows)
