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
NOT_SPHERICAL_EXACT = "NOT_SPHERICAL_EXACT"
SPHERICAL_REQUIRES_INDEPENDENT_VALIDATION = (
    "SPHERICAL_REQUIRES_INDEPENDENT_VALIDATION"
)
UNSUPPORTED = "UNSUPPORTED"
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


@dataclass(frozen=True)
class DispatchSupport:
    """The exact proved envelope selected from literal occurrence corners."""

    kind: str
    theorem: str | None
    solver: str | None
    simple_edges: tuple[tuple[int, int], ...]
    loop_class: tuple[int, int] | None = None
    reason: str | None = None


@dataclass(frozen=True)
class FrontierDispatchResult:
    """One quarantined finite-sphericity result, never a topology verdict."""

    category: str
    support: DispatchSupport
    provenance: tuple[PriorProvenance, ...] | None = None
    solver_verdict: str | None = None
    counters: object | None = None
    witness: object | None = None


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


_DISPATCH_GERMS = (0, 1, 2, 3)
_DISPATCH_GERM_PAIRS = {
    "x": (0, 1),
    "X": (1, 0),
    "y": (2, 3),
    "Y": (3, 2),
}
_RANK_THEOREM = "AK3_SYNCHRONIZED_PLANARITY.md"
_P4_THEOREM = "AK3_P4_SYNCHRONIZED_PLANARITY.md"
_ONE_LOOP_THEOREM = "AK3_ONE_LOOP_SYNCHRONIZED_PLANARITY.md"
_PAW_ONE_LOOP_THEOREM = "AK3_PAW_ONE_LOOP_PLANARITY.md"


def _unsupported_dispatch_support(
    simple_edges: tuple[tuple[int, int], ...] = (), reason: str | None = None
) -> DispatchSupport:
    return DispatchSupport(UNSUPPORTED, None, None, simple_edges, reason=reason)


def _exact_dispatch_inventory(
    relators: object,
) -> tuple[tuple[str, str], dict[tuple[int, int], int]] | None:
    if (
        not isinstance(relators, tuple)
        or len(relators) != 2
        or not all(isinstance(word, str) and word for word in relators)
        or any(set(word) - _WORD_ALPHABET for word in relators)
    ):
        return None
    words = (relators[0], relators[1])
    multiplicities: dict[tuple[int, int], int] = {}
    for word in words:
        for index, letter in enumerate(word):
            try:
                arrival = _DISPATCH_GERM_PAIRS[letter][1]
                departure = _DISPATCH_GERM_PAIRS[word[(index + 1) % len(word)]][0]
            except KeyError:
                return None
            edge = tuple(sorted((arrival, departure)))
            multiplicities[edge] = multiplicities.get(edge, 0) + 1
    return words, multiplicities


def _is_connected(simple_edges: tuple[tuple[int, int], ...]) -> bool:
    adjacency = {vertex: set() for vertex in _DISPATCH_GERMS}
    for left, right in simple_edges:
        if left == right:
            return False
        adjacency[left].add(right)
        adjacency[right].add(left)
    reached = {0}
    frontier = [0]
    while frontier:
        vertex = frontier.pop()
        unseen = adjacency[vertex] - reached
        reached.update(unseen)
        frontier.extend(unseen)
    return reached == set(_DISPATCH_GERMS)


def _loopless_kind(simple_edges: tuple[tuple[int, int], ...]) -> str | None:
    if not _is_connected(simple_edges):
        return None
    degrees = sorted(
        sum(vertex in edge for edge in simple_edges)
        for vertex in _DISPATCH_GERMS
    )
    if len(simple_edges) == 6:
        return "K4"
    if len(simple_edges) == 5 and degrees == [2, 2, 3, 3]:
        return "K4-e"
    if len(simple_edges) == 4 and degrees == [2, 2, 2, 2]:
        return "C4"
    if len(simple_edges) == 3 and degrees == [1, 1, 2, 2]:
        return "P4"
    return None


def _classify_dispatch_inventory(
    multiplicities: Mapping[tuple[int, int], int],
) -> DispatchSupport:
    """Classify one already-exact occurrence-link inventory."""
    simple_edges = tuple(sorted(multiplicities))
    loop_classes = tuple(edge for edge in simple_edges if edge[0] == edge[1])
    if not loop_classes:
        kind = _loopless_kind(simple_edges)
        if kind in {"K4", "K4-e", "C4"}:
            return DispatchSupport(
                kind,
                _RANK_THEOREM,
                "neuwirth_rank_solver.solve_spherical",
                simple_edges,
            )
        if kind == "P4":
            return DispatchSupport(
                kind,
                _P4_THEOREM,
                "neuwirth_p4_solver.solve_four_germ_spherical",
                simple_edges,
            )
        return _unsupported_dispatch_support(
            simple_edges, "unproved loopless support"
        )
    if len(loop_classes) != 1:
        return _unsupported_dispatch_support(simple_edges, "multiple loop classes")
    loop_class = loop_classes[0]
    if multiplicities[loop_class] != 1:
        return _unsupported_dispatch_support(
            simple_edges, "loop class multiplicity is not one"
        )
    core_edges = tuple(edge for edge in simple_edges if edge != loop_class)
    core_kind = _loopless_kind(core_edges)
    if core_kind in {"K4", "K4-e"}:
        return DispatchSupport(
            f"{core_kind}+1loop",
            _ONE_LOOP_THEOREM,
            "neuwirth_one_loop_solver.solve_one_loop_spherical",
            simple_edges,
            loop_class,
        )
    degrees = {
        vertex: sum(vertex in edge for edge in core_edges)
        for vertex in _DISPATCH_GERMS
    }
    if _is_connected(core_edges) and sorted(degrees.values()) == [1, 2, 2, 3]:
        articulation = next(
            vertex for vertex, degree in degrees.items() if degree == 3
        )
        if loop_class[0] == articulation:
            return _unsupported_dispatch_support(
                simple_edges, "paw loop is attached at the articulation"
            )
        return DispatchSupport(
            "paw+1loop",
            _PAW_ONE_LOOP_THEOREM,
            "neuwirth_paw_one_loop_solver.solve_paw_one_loop_spherical",
            simple_edges,
            loop_class,
        )
    return _unsupported_dispatch_support(simple_edges, "unproved one-loop core")


def _classify_dispatch_support(relators: object) -> DispatchSupport:
    """Classify literal A-corner support before any proved solver import."""
    inventory = _exact_dispatch_inventory(relators)
    if inventory is None:
        return _unsupported_dispatch_support(reason="malformed exact relators")
    _, multiplicities = inventory
    return _classify_dispatch_inventory(multiplicities)


def _cyclically_equal(left: tuple[int, ...], right: tuple[int, ...]) -> bool:
    return len(left) == len(right) and any(
        left == right[index:] + right[:index] for index in range(len(right))
    )


def _replay_spherical_rotation(decision: object) -> bool:
    """Independently replay only the returned occurrence rotations."""
    solver_support = getattr(decision, "support", None)
    data = getattr(solver_support, "data", None)
    witness = getattr(decision, "witness", None)
    rotations = getattr(witness, "rotations", None)
    if data is None or not isinstance(rotations, tuple) or len(rotations) != 4:
        return False
    if not all(isinstance(rotation, tuple) for rotation in rotations):
        return False
    sigma = [-1] * len(data.A)
    for vertex, rotation in enumerate(rotations):
        if not all(type(dart) is int for dart in rotation):
            return False
        if set(rotation) != set(data.vertex_darts[vertex]):
            return False
        if len(rotation) != len(data.vertex_darts[vertex]) or not rotation:
            return False
        for index, dart in enumerate(rotation):
            if not 0 <= dart < len(data.A):
                return False
            sigma[dart] = rotation[(index + 1) % len(rotation)]
    for positive, negative in ((0, 1), (2, 3)):
        expected = tuple(data.B[dart] for dart in reversed(rotations[positive]))
        if not _cyclically_equal(expected, rotations[negative]):
            return False
    if any(successor < 0 for successor in sigma):
        return False
    phi = tuple(sigma[data.A[dart]] for dart in range(len(data.A)))
    faces = 0
    unseen = set(range(len(phi)))
    while unseen:
        faces += 1
        dart = next(iter(unseen))
        while dart in unseen:
            unseen.remove(dart)
            dart = phi[dart]
    return len(_DISPATCH_GERMS) - len(data.edge_darts) + faces == 2


def _finalize_solver_decision(
    support: DispatchSupport, decision: object
) -> FrontierDispatchResult:
    spherical = getattr(decision, "spherical", None)
    verdict = getattr(decision, "verdict", None)
    if spherical is False and verdict == "NOT_SPHERICAL":
        counters = getattr(decision, "counters", None)
        if getattr(counters, "exhaustive", None) is True:
            return FrontierDispatchResult(
                NOT_SPHERICAL_EXACT,
                support,
                solver_verdict=verdict,
                counters=counters,
            )
    elif (
        spherical is True
        and verdict == "SPHERICAL"
        and _replay_spherical_rotation(decision)
    ):
        return FrontierDispatchResult(
            SPHERICAL_REQUIRES_INDEPENDENT_VALIDATION,
            support,
            solver_verdict=verdict,
            counters=getattr(decision, "counters", None),
            witness=getattr(decision, "witness", None),
        )
    return FrontierDispatchResult(UNSUPPORTED, support)


def dispatch_frontier_support(
    index: PriorCertificateIndex | None, relators: object
) -> FrontierDispatchResult:
    """Route only the four proved envelopes; never make a topology claim."""
    inventory = _exact_dispatch_inventory(relators)
    if inventory is None:
        return FrontierDispatchResult(
            UNSUPPORTED,
            _unsupported_dispatch_support(reason="malformed exact relators"),
        )
    words, _ = inventory
    if index is not None:
        if not isinstance(index, PriorCertificateIndex):
            return FrontierDispatchResult(
                UNSUPPORTED,
                _unsupported_dispatch_support(reason="ambiguous prior index"),
            )
        prior = lookup_prior_exact(index, words)
        if prior is not None:
            return FrontierDispatchResult(
                PRIOR_EXACT_DUPLICATE,
                DispatchSupport(
                    PRIOR_EXACT_DUPLICATE,
                    "frozen prior exact-certificate index",
                    None,
                    (),
                ),
                provenance=prior.provenance,
            )
    support = _classify_dispatch_support(words)
    if support.kind == UNSUPPORTED:
        return FrontierDispatchResult(UNSUPPORTED, support)
    if support.solver == "neuwirth_rank_solver.solve_spherical":
        from experiments.stable_ac.thickenable.neuwirth_rank_solver import (
            solve_spherical,
        )

        return _finalize_solver_decision(support, solve_spherical(words))
    if support.solver == "neuwirth_p4_solver.solve_four_germ_spherical":
        from experiments.stable_ac.thickenable.neuwirth_p4_solver import (
            solve_four_germ_spherical,
        )

        return _finalize_solver_decision(
            support, solve_four_germ_spherical(words)
        )
    if support.solver == "neuwirth_one_loop_solver.solve_one_loop_spherical":
        from experiments.stable_ac.thickenable.neuwirth_one_loop_solver import (
            solve_one_loop_spherical,
        )

        return _finalize_solver_decision(support, solve_one_loop_spherical(words))
    if support.solver == "neuwirth_paw_one_loop_solver.solve_paw_one_loop_spherical":
        from experiments.stable_ac.thickenable.neuwirth_paw_one_loop_solver import (
            solve_paw_one_loop_spherical,
        )

        return _finalize_solver_decision(
            support, solve_paw_one_loop_spherical(words)
        )
    return FrontierDispatchResult(UNSUPPORTED, support)
