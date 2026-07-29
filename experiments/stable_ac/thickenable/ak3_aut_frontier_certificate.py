"""Frozen prior exact-certificate index for the AK(3) Aut(F2) frontier.

This module is deliberately limited to provenance lookup.  It neither imports
nor invokes a topology solver, and it does not make a thickenability decision.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from experiments.stable_ac.thickenable.ak3_aut_frontier_manifest import (
    exact_cellular_key,
)

PRIOR_INDEX_SCHEMA = "ak3-aut-frontier-prior-index-v1"
PRIOR_EXACT_DUPLICATE = "PRIOR_EXACT_DUPLICATE"
FROZEN_PRIOR_CORPUS = (
    "results/stable_ac/theory/ak3_neuwirth_census.json",
    "results/stable_ac/theory/ak3_component_thickenability.json",
    "results/stable_ac/theory/ak3_cov_thickenability.json",
    "results/stable_ac/theory/ak3_two_hop_cov_thickenability.json",
    "results/stable_ac/theory/ak3_primitive_quotient_thickenability.json",
)
RANK3_RIGID_PATH = "results/stable_ac/theory/ak3_rank3_rigid_thickenability.json"
_ROOT = Path(__file__).resolve().parents[3]
_WORD_ALPHABET = frozenset("xXyY")


class PriorCertificateSchemaError(ValueError):
    """A frozen prior certificate cannot safely be interpreted as exact data."""


@dataclass(frozen=True)
class PriorProvenance:
    """One literal rank-two record from the immutable prior corpus."""

    corpus_path: str
    source_sha256: str
    record_id: str
    verdict: str
    raw_relators: tuple[str, str]
    cellular_key: tuple[str, str]


@dataclass(frozen=True)
class PriorExactDuplicate:
    """All prior records sharing one exact-cellular key."""

    category: str
    provenance: tuple[PriorProvenance, ...]


@dataclass(frozen=True)
class PriorCertificateIndex:
    """Ordered prior rows and their exact-cellular lookup buckets."""

    schema: str
    corpus_paths: tuple[str, ...]
    rows: tuple[PriorProvenance, ...]
    buckets: Mapping[tuple[str, str], tuple[PriorProvenance, ...]]


def _schema_error(path: str, message: str) -> PriorCertificateSchemaError:
    return PriorCertificateSchemaError(f"{path}: {message}")


def _require_mapping(value: object, path: str, field: str) -> Mapping[str, object]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise _schema_error(path, f"{field} must be an object")
    return value


def _require_list(value: object, path: str, field: str) -> list[object]:
    if not isinstance(value, list):
        raise _schema_error(path, f"{field} must be a list")
    return value


def _require_verdict(record: Mapping[str, object], path: str, record_id: str) -> str:
    verdict = record.get("verdict")
    if not isinstance(verdict, str) or not verdict:
        raise _schema_error(path, f"{record_id} is missing a verdict")
    return verdict


def _require_words(record: Mapping[str, object], path: str, record_id: str) -> tuple[str, str]:
    words = record.get("words")
    if not isinstance(words, list) or len(words) != 2 or not all(isinstance(word, str) for word in words):
        raise _schema_error(path, f"{record_id} must provide exactly two literal words")
    first, second = words
    if not first or not second or any(set(word) - _WORD_ALPHABET for word in (first, second)):
        raise _schema_error(path, f"{record_id} has an ambiguous exact word spelling")
    return (first, second)


def _provenance_row(
    corpus_path: str,
    source_sha256: str,
    record_id: str,
    record: Mapping[str, object],
) -> PriorProvenance:
    raw_relators = _require_words(record, corpus_path, record_id)
    return PriorProvenance(
        corpus_path=corpus_path,
        source_sha256=source_sha256,
        record_id=record_id,
        verdict=_require_verdict(record, corpus_path, record_id),
        raw_relators=raw_relators,
        cellular_key=exact_cellular_key(raw_relators),
    )


def _adapt_neuwirth_census(
    payload: Mapping[str, object], corpus_path: str, source_sha256: str
) -> tuple[PriorProvenance, ...]:
    if payload.get("schema") != "ak3-neuwirth-census-v1":
        raise _schema_error(corpus_path, "unexpected neuwirth census schema")
    targets = _require_mapping(payload.get("targets"), corpus_path, "targets")
    if not targets:
        raise _schema_error(corpus_path, "targets must not be empty")
    rows = []
    for target_id, target in targets.items():
        if not target_id:
            raise _schema_error(corpus_path, "target record ID must not be empty")
        rows.append(
            _provenance_row(
                corpus_path,
                source_sha256,
                f"target:{target_id}",
                _require_mapping(target, corpus_path, f"target:{target_id}"),
            )
        )
    return tuple(rows)


def _adapt_component_thickenability(
    payload: Mapping[str, object], corpus_path: str, source_sha256: str
) -> tuple[PriorProvenance, ...]:
    if payload.get("schema") != "ak3-component-thickenability-v1":
        raise _schema_error(corpus_path, "unexpected component thickenability schema")
    states = _require_list(payload.get("states"), corpus_path, "states")
    if not states:
        raise _schema_error(corpus_path, "states must not be empty")
    rows = []
    for position, state in enumerate(states):
        record_id = f"state:{position}"
        record = _require_mapping(state, corpus_path, record_id)
        disposition = record.get("disposition")
        if not isinstance(disposition, str) or not disposition:
            raise _schema_error(corpus_path, f"{record_id} is missing a disposition")
        rows.append(_provenance_row(corpus_path, source_sha256, record_id, record))
    return tuple(rows)


def _adapt_cov_thickenability(
    payload: Mapping[str, object], corpus_path: str, source_sha256: str
) -> tuple[PriorProvenance, ...]:
    if payload.get("schema") != "ak3-cov-thickenability-v1":
        raise _schema_error(corpus_path, "unexpected CoV thickenability schema")
    return _adapt_indexed_output_records(payload, corpus_path, source_sha256, "output")


def _adapt_two_hop_cov_thickenability(
    payload: Mapping[str, object], corpus_path: str, source_sha256: str
) -> tuple[PriorProvenance, ...]:
    if payload.get("schema") != "ak3-two-hop-cov-thickenability-v1":
        raise _schema_error(corpus_path, "unexpected two-hop CoV thickenability schema")
    return _adapt_indexed_output_records(payload, corpus_path, source_sha256, "output")


def _adapt_indexed_output_records(
    payload: Mapping[str, object], corpus_path: str, source_sha256: str, prefix: str
) -> tuple[PriorProvenance, ...]:
    records = _require_list(payload.get("output_records"), corpus_path, "output_records")
    if not records:
        raise _schema_error(corpus_path, "output_records must not be empty")
    rows = []
    seen_ids: set[int] = set()
    for record_value in records:
        record = _require_mapping(record_value, corpus_path, "output record")
        index = record.get("index")
        if type(index) is not int or index < 0 or index in seen_ids:
            raise _schema_error(corpus_path, "output record has a missing or invalid record ID")
        seen_ids.add(index)
        rows.append(_provenance_row(corpus_path, source_sha256, f"{prefix}:{index}", record))
    return tuple(rows)


def _adapt_primitive_quotient_thickenability(
    payload: Mapping[str, object], corpus_path: str, source_sha256: str
) -> tuple[PriorProvenance, ...]:
    if payload.get("schema") != "ak3-primitive-quotient-thickenability-v1":
        raise _schema_error(corpus_path, "unexpected primitive quotient thickenability schema")
    records = _require_list(payload.get("output_records"), corpus_path, "output_records")
    if not records:
        raise _schema_error(corpus_path, "output_records must not be empty")
    return tuple(
        _provenance_row(
            corpus_path,
            source_sha256,
            f"output:{position}",
            _require_mapping(record, corpus_path, f"output:{position}"),
        )
        for position, record in enumerate(records)
    )


_ADAPTERS: tuple[Callable[[Mapping[str, object], str, str], tuple[PriorProvenance, ...]], ...] = (
    _adapt_neuwirth_census,
    _adapt_component_thickenability,
    _adapt_cov_thickenability,
    _adapt_two_hop_cov_thickenability,
    _adapt_primitive_quotient_thickenability,
)


def build_prior_certificate_index(root: Path = _ROOT) -> PriorCertificateIndex:
    """Read exactly the five frozen certificates and index their literal complexes."""
    rows: list[PriorProvenance] = []
    for corpus_path, adapter in zip(FROZEN_PRIOR_CORPUS, _ADAPTERS, strict=True):
        try:
            raw_bytes = (root / corpus_path).read_bytes()
            decoded = json.loads(raw_bytes)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            raise _schema_error(corpus_path, "cannot read frozen certificate bytes") from error
        payload = _require_mapping(decoded, corpus_path, "certificate")
        rows.extend(adapter(payload, corpus_path, sha256(raw_bytes).hexdigest()))
    buckets: dict[tuple[str, str], list[PriorProvenance]] = {}
    for row in rows:
        buckets.setdefault(row.cellular_key, []).append(row)
    return PriorCertificateIndex(
        schema=PRIOR_INDEX_SCHEMA,
        corpus_paths=FROZEN_PRIOR_CORPUS,
        rows=tuple(rows),
        buckets={key: tuple(bucket) for key, bucket in buckets.items()},
    )


def lookup_prior_exact(
    index: PriorCertificateIndex, relators: tuple[str, str]
) -> PriorExactDuplicate | None:
    """Return provenance only for exact-cellular equality; never dispatch a solver."""
    if not isinstance(relators, tuple):
        raise TypeError("relators must be a literal two-word tuple")
    words = _require_words({"words": list(relators)}, "lookup", "candidate")
    provenance = index.buckets.get(exact_cellular_key(words))
    if provenance is None:
        return None
    return PriorExactDuplicate(PRIOR_EXACT_DUPLICATE, provenance)
