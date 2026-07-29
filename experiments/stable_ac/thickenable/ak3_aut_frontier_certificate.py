"""Frozen prior exact-certificate index for the AK(3) Aut(F2) frontier.

This module is deliberately limited to provenance lookup.  It neither imports
nor invokes a topology solver, and it does not make a thickenability decision.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass
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

CERTIFICATE_SCHEMA = "ak3-aut-frontier-certificate-v1"
FROZEN_MANIFEST_SHA256 = (
    "96b710a0fd53e56c53c42e8bcd203286d98a982a735ec2d42fa9b4b856fd816a"
)
FROZEN_MANIFEST_PATH = (
    "results/stable_ac/theory/ak3_aut_frontier_manifest.json"
)
DEFAULT_CERTIFICATE_PATH = (
    _ROOT / "results/stable_ac/theory/ak3_aut_frontier_certificate.json"
)
DEFAULT_MARKDOWN_PATH = (
    _ROOT / "results/stable_ac/theory/AK3_AUT_FRONTIER_RESULT.md"
)
_MANIFEST_SCHEMA = "ak3-aut-frontier-manifest-v1"
_SPELLING_MODES = ("literal", "free", "cyclic")
_SOLVER_PATHS = (
    (
        "neuwirth_rank_solver.solve_spherical",
        "experiments/stable_ac/thickenable/neuwirth_rank_solver.py",
    ),
    (
        "neuwirth_p4_solver.solve_four_germ_spherical",
        "experiments/stable_ac/thickenable/neuwirth_p4_solver.py",
    ),
    (
        "neuwirth_one_loop_solver.solve_one_loop_spherical",
        "experiments/stable_ac/thickenable/neuwirth_one_loop_solver.py",
    ),
    (
        "neuwirth_paw_one_loop_solver.solve_paw_one_loop_spherical",
        "experiments/stable_ac/thickenable/neuwirth_paw_one_loop_solver.py",
    ),
)
_SUPPORT_PROOF_PATHS = (
    "literature/proofs/AK3_SYNCHRONIZED_PLANARITY.md",
    "literature/proofs/AK3_P4_SYNCHRONIZED_PLANARITY.md",
    "literature/proofs/AK3_ONE_LOOP_SYNCHRONIZED_PLANARITY.md",
    "literature/proofs/AK3_PAW_ONE_LOOP_PLANARITY.md",
)
_DRIVER_PATH = (
    "experiments/stable_ac/thickenable/ak3_aut_frontier_certificate.py"
)
_RESULT_DIGEST_DEFINITION = (
    "sha256 of the concatenation of each ordered result row's canonical "
    "UTF-8 JSON bytes (sorted keys, compact separators, ASCII escaping, "
    "one trailing newline per row)"
)
_PROOF_LIMITS = (
    (
        "This is a finite census of the frozen 1,000-map BFS prefix, not an "
        "Aut(F2) orbit closure or saturation theorem."
    ),
    (
        "Each negative applies only to its exact stored spelling; unsupported "
        "rows are not negative results."
    ),
    (
        "This is not an AC search, and no row proves an AC or stable-AC "
        "counterexample."
    ),
    (
        "Every spherical row is quarantined pending an independent exact "
        "neighborhood and 3-ball validation; it is not a thickenability, "
        "Lackenby, AC, or stable-AC result."
    ),
)


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
    spherical: bool | None = None


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


def _classify_support_inventory(
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
    return _classify_support_inventory(multiplicities)


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
                spherical=spherical,
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
            spherical=spherical,
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


def _canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )
        + "\n"
    ).encode("utf-8")


def _manifest_mapping(value: object, field: str) -> Mapping[str, object]:
    if not isinstance(value, dict) or not all(
        isinstance(key, str) for key in value
    ):
        raise AssertionError(f"manifest {field} must be an object")
    return value


def _manifest_list(value: object, field: str) -> list[object]:
    if not isinstance(value, list):
        raise TypeError(f"manifest {field} must be a list")
    return value


def _manifest_words(value: object, field: str) -> tuple[str, str]:
    if (
        not isinstance(value, list)
        or len(value) != 2
        or not all(isinstance(word, str) and word for word in value)
        or any(set(word) - _WORD_ALPHABET for word in value)
    ):
        raise AssertionError(f"manifest {field} must be two exact words")
    return (value[0], value[1])


def _validated_manifest(
    manifest_path: Path,
    expected_manifest_sha256: str,
    expected_map_count: int,
    expected_bucket_count: int,
    expected_membership_count: int,
) -> tuple[
    bytes,
    Mapping[str, object],
    tuple[Mapping[str, object], ...],
    tuple[Mapping[str, object], ...],
]:
    raw_bytes = manifest_path.read_bytes()
    if sha256(raw_bytes).hexdigest() != expected_manifest_sha256:
        raise AssertionError("manifest SHA-256 differs from the frozen input")
    try:
        decoded = json.loads(raw_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise AssertionError("manifest is not canonical UTF-8 JSON") from error
    payload = _manifest_mapping(decoded, "payload")
    if raw_bytes != _canonical_json_bytes(payload):
        raise AssertionError("manifest bytes are not canonical JSON")
    if payload.get("schema") != _MANIFEST_SCHEMA:
        raise AssertionError("manifest schema differs from the frozen contract")

    record_values = _manifest_list(payload.get("records"), "records")
    if len(record_values) != expected_map_count:
        raise AssertionError("manifest map count differs from the frozen bound")
    records: list[Mapping[str, object]] = []
    expected_members: dict[
        tuple[str, str], list[dict[str, object]]
    ] = {}
    for position, record_value in enumerate(record_values):
        record = _manifest_mapping(record_value, f"record {position}")
        if record.get("id") != position:
            raise AssertionError("manifest record IDs are not consecutive")
        spellings = _manifest_mapping(
            record.get("spellings"), f"record {position} spellings"
        )
        if set(spellings) != set(_SPELLING_MODES):
            raise AssertionError("manifest spelling modes differ from the contract")
        for mode in _SPELLING_MODES:
            track = _manifest_mapping(
                spellings[mode], f"record {position} {mode} spelling"
            )
            words = _manifest_words(
                track.get("raw"), f"record {position} {mode} raw relators"
            )
            stored_key = _manifest_words(
                track.get("cellular_key"),
                f"record {position} {mode} cellular key",
            )
            if stored_key != exact_cellular_key(words):
                raise AssertionError("manifest record cellular key is incorrect")
            expected_members.setdefault(stored_key, []).append(
                {"map_id": position, "mode": mode}
            )
        records.append(record)

    expected_buckets = [
        {"cellular_key": list(key), "members": expected_members[key]}
        for key in sorted(expected_members)
    ]
    bucket_values = _manifest_list(payload.get("buckets"), "buckets")
    membership_count = sum(
        len(_manifest_list(_manifest_mapping(bucket, "bucket").get("members"), "bucket members"))
        for bucket in bucket_values
    )
    if (
        len(bucket_values) != expected_bucket_count
        or membership_count != expected_membership_count
        or bucket_values != expected_buckets
    ):
        raise AssertionError(
            "manifest bucket partition differs from the ordered record spellings"
        )
    return (
        raw_bytes,
        payload,
        tuple(records),
        tuple(_manifest_mapping(bucket, "bucket") for bucket in bucket_values),
    )


def _json_dataclass(value: object | None) -> object | None:
    if value is None:
        return None
    return json.loads(json.dumps(asdict(value), ensure_ascii=True))


def _prior_payload(
    provenance: Sequence[PriorProvenance] | None,
) -> list[dict[str, object]] | None:
    if provenance is None:
        return None
    return [
        {
            "cellular_key": list(row.cellular_key),
            "corpus_path": row.corpus_path,
            "raw_relators": list(row.raw_relators),
            "record_id": row.record_id,
            "source_sha256": row.source_sha256,
            "verdict": row.verdict,
        }
        for row in provenance
    ]


def _member_payload(
    member: Mapping[str, object],
    records: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    map_id = member["map_id"]
    mode = member["mode"]
    if type(map_id) is not int or not isinstance(mode, str):
        raise AssertionError("validated manifest member changed type")
    record = records[map_id]
    spellings = _manifest_mapping(record["spellings"], "record spellings")
    track = _manifest_mapping(spellings[mode], "record spelling track")
    words = _manifest_words(track["raw"], "record raw relators")
    return {
        "map_id": map_id,
        "mode": mode,
        "raw_relators": list(words),
    }


def _result_row(
    bucket_id: int,
    bucket: Mapping[str, object],
    records: Sequence[Mapping[str, object]],
    prior_index: PriorCertificateIndex,
) -> dict[str, object]:
    members = tuple(
        _manifest_mapping(member, "bucket member")
        for member in _manifest_list(bucket["members"], "bucket members")
    )
    member_payloads = [
        _member_payload(member, records) for member in members
    ]
    representative = member_payloads[0]
    words = tuple(representative["raw_relators"])
    if not (
        len(words) == 2 and all(isinstance(word, str) for word in words)
    ):
        raise AssertionError("representative raw pair changed after validation")
    exact_words = (words[0], words[1])
    inventory = _exact_dispatch_inventory(exact_words)
    if inventory is None:
        raise AssertionError("validated representative has no exact inventory")
    _, multiplicities = inventory
    classified_support = _classify_dispatch_support(exact_words)

    prior = lookup_prior_exact(prior_index, exact_words)
    if prior is not None:
        category = PRIOR_EXACT_DUPLICATE
        support = classified_support
        selected_theorem = None
        selected_solver = None
        solver_verdict = None
        counters = None
        witness = None
        spherical = None
        provenance: Sequence[PriorProvenance] | None = prior.provenance
        fail_closed_reason = "prior exact duplicate; solver bypassed"
    else:
        decision = dispatch_frontier_support(None, exact_words)
        category = decision.category
        support = decision.support
        selected_theorem = support.theorem
        selected_solver = support.solver
        solver_verdict = decision.solver_verdict
        counters = decision.counters
        witness = decision.witness
        spherical = decision.spherical
        provenance = None
        if category == UNSUPPORTED:
            fail_closed_reason = (
                support.reason or "selected solver evidence failed closed"
            )
        else:
            fail_closed_reason = None

    if category not in {
        PRIOR_EXACT_DUPLICATE,
        NOT_SPHERICAL_EXACT,
        SPHERICAL_REQUIRES_INDEPENDENT_VALIDATION,
        UNSUPPORTED,
    }:
        raise AssertionError("dispatcher emitted an unknown certificate category")
    return {
        "category": category,
        "cellular_key": list(_manifest_words(bucket["cellular_key"], "bucket key")),
        "counters": _json_dataclass(counters),
        "fail_closed_reason": fail_closed_reason,
        "members": member_payloads,
        "prior_provenance": _prior_payload(provenance),
        "representative": representative,
        "row_id": f"bucket-{bucket_id:03d}",
        "selected_solver": selected_solver,
        "selected_theorem": selected_theorem,
        "solver_verdict": solver_verdict,
        "spherical": spherical,
        "support": {
            "kind": support.kind,
            "loop_class": (
                None if support.loop_class is None else list(support.loop_class)
            ),
            "reason": support.reason,
            "simple_edges": [list(edge) for edge in support.simple_edges],
        },
        "support_inventory": {
            "edge_multiplicities": [
                {"edge": list(edge), "multiplicity": multiplicities[edge]}
                for edge in sorted(multiplicities)
            ]
        },
        "witness": _json_dataclass(witness),
    }


def _source_hash_entry(root: Path, relative_path: str) -> dict[str, str]:
    return {
        "path": relative_path,
        "sha256": sha256((root / relative_path).read_bytes()).hexdigest(),
    }


def _ordered_result_digest(results: Sequence[Mapping[str, object]]) -> str:
    return sha256(
        b"".join(_canonical_json_bytes(row) for row in results)
    ).hexdigest()


def _verify_spherical_contract(row: Mapping[str, object]) -> None:
    if "spherical" not in row:
        raise AssertionError("certificate result is missing spherical")
    spherical = row["spherical"]
    if spherical is not None and type(spherical) is not bool:
        raise AssertionError("certificate result spherical must be boolean or null")
    expected_by_category = {
        PRIOR_EXACT_DUPLICATE: None,
        NOT_SPHERICAL_EXACT: False,
        SPHERICAL_REQUIRES_INDEPENDENT_VALIDATION: True,
        UNSUPPORTED: None,
    }
    category = row.get("category")
    if category not in expected_by_category:
        raise AssertionError("certificate result has an unknown category")
    if spherical is not expected_by_category[category]:
        raise AssertionError(
            "certificate result spherical disagrees with its category"
        )


def build_certificate_payload(
    root: Path = _ROOT,
    manifest_path: Path | None = None,
    *,
    expected_manifest_sha256: str = FROZEN_MANIFEST_SHA256,
    expected_map_count: int = 1_000,
    expected_bucket_count: int = 285,
    expected_membership_count: int = 3_000,
) -> dict[str, object]:
    """Evaluate every frozen exact-cellular bucket and retain replay evidence."""
    resolved_manifest_path = manifest_path or root / FROZEN_MANIFEST_PATH
    manifest_bytes, _, records, buckets = _validated_manifest(
        resolved_manifest_path,
        expected_manifest_sha256,
        expected_map_count,
        expected_bucket_count,
        expected_membership_count,
    )
    prior_index = build_prior_certificate_index(root)
    results = [
        _result_row(bucket_id, bucket, records, prior_index)
        for bucket_id, bucket in enumerate(buckets)
    ]

    selected_solver_names = {
        row["selected_solver"]
        for row in results
        if row["selected_solver"] is not None
    }
    solver_paths = dict(_SOLVER_PATHS)
    if selected_solver_names - set(solver_paths):
        raise AssertionError("certificate selected a solver outside the fixed list")
    selected_solvers = [
        _source_hash_entry(_ROOT, solver_path)
        for solver_name, solver_path in _SOLVER_PATHS
        if solver_name in selected_solver_names
    ]
    prior_hashes = [
        _source_hash_entry(root, relative_path)
        for relative_path in FROZEN_PRIOR_CORPUS
    ]
    support_proofs = [
        _source_hash_entry(_ROOT, relative_path)
        for relative_path in _SUPPORT_PROOF_PATHS
    ]

    mode_histogram = {mode: 0 for mode in _SPELLING_MODES}
    for row in results:
        for member in row["members"]:
            mode_histogram[member["mode"]] += 1
    support_histogram = dict(
        sorted(Counter(row["support"]["kind"] for row in results).items())
    )
    categories = (
        PRIOR_EXACT_DUPLICATE,
        NOT_SPHERICAL_EXACT,
        SPHERICAL_REQUIRES_INDEPENDENT_VALIDATION,
        UNSUPPORTED,
    )
    category_counts = Counter(row["category"] for row in results)
    verdict_histogram = {
        category: category_counts[category] for category in categories
    }
    quarantined_row_ids = [
        row["row_id"]
        for row in results
        if row["category"] == SPHERICAL_REQUIRES_INDEPENDENT_VALIDATION
    ]
    return {
        "bounded_census": {
            "exact_cellular_key_count": len(buckets),
            "map_count": len(records),
            "ordered_membership_count": sum(mode_histogram.values()),
            "spelling_mode_histogram": mode_histogram,
            "support_histogram": support_histogram,
            "verdict_histogram": verdict_histogram,
        },
        "ordered_result_digest": _ordered_result_digest(results),
        "ordered_result_digest_definition": _RESULT_DIGEST_DEFINITION,
        "proof_limits": list(_PROOF_LIMITS),
        "quarantined_row_ids": quarantined_row_ids,
        "results": results,
        "schema": CERTIFICATE_SCHEMA,
        "source_hashes": {
            "decision_driver": _source_hash_entry(_ROOT, _DRIVER_PATH),
            "manifest": {
                "path": FROZEN_MANIFEST_PATH,
                "sha256": sha256(manifest_bytes).hexdigest(),
            },
            "prior_corpus": prior_hashes,
            "selected_solvers": selected_solvers,
            "support_proofs": support_proofs,
        },
    }


def build_certificate_bytes(
    root: Path = _ROOT,
    manifest_path: Path | None = None,
    *,
    expected_manifest_sha256: str = FROZEN_MANIFEST_SHA256,
    expected_map_count: int = 1_000,
    expected_bucket_count: int = 285,
    expected_membership_count: int = 3_000,
) -> bytes:
    return _canonical_json_bytes(
        build_certificate_payload(
            root,
            manifest_path,
            expected_manifest_sha256=expected_manifest_sha256,
            expected_map_count=expected_map_count,
            expected_bucket_count=expected_bucket_count,
            expected_membership_count=expected_membership_count,
        )
    )


def verify_certificate_bytes(
    certificate_bytes: bytes,
    root: Path = _ROOT,
    manifest_path: Path | None = None,
    *,
    expected_manifest_sha256: str = FROZEN_MANIFEST_SHA256,
    expected_map_count: int = 1_000,
    expected_bucket_count: int = 285,
    expected_membership_count: int = 3_000,
) -> Mapping[str, object]:
    """Rerun every decision and require canonical payload byte identity."""
    try:
        decoded = json.loads(certificate_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise AssertionError("certificate is not canonical UTF-8 JSON") from error
    payload = _manifest_mapping(decoded, "certificate")
    if certificate_bytes != _canonical_json_bytes(payload):
        raise AssertionError("certificate bytes are not canonical JSON")
    if payload.get("schema") != CERTIFICATE_SCHEMA:
        raise AssertionError("certificate schema differs from the contract")
    stored_results = tuple(
        _manifest_mapping(row, "certificate result")
        for row in _manifest_list(payload.get("results"), "certificate results")
    )
    for row in stored_results:
        _verify_spherical_contract(row)
    if payload.get("ordered_result_digest") != _ordered_result_digest(
        stored_results
    ):
        raise AssertionError("ordered result digest does not replay")
    expected = build_certificate_payload(
        root,
        manifest_path,
        expected_manifest_sha256=expected_manifest_sha256,
        expected_map_count=expected_map_count,
        expected_bucket_count=expected_bucket_count,
        expected_membership_count=expected_membership_count,
    )
    expected_bytes = _canonical_json_bytes(expected)
    if payload != expected or certificate_bytes != expected_bytes:
        raise AssertionError(
            "certificate payload differs from the independent decision replay"
        )
    return payload


def _markdown_histogram(
    title: str, histogram: Mapping[str, object]
) -> list[str]:
    lines = [f"## {title}", "", "| Value | Count |", "| --- | ---: |"]
    lines.extend(f"| `{key}` | {value} |" for key, value in histogram.items())
    lines.append("")
    return lines


def build_markdown_bytes(payload: Mapping[str, object]) -> bytes:
    """Render only bounded histograms, exact hashes, quarantine, and limits."""
    census = _manifest_mapping(payload["bounded_census"], "bounded census")
    source_hashes = _manifest_mapping(payload["source_hashes"], "source hashes")
    lines = [
        "# Bounded AK(3) Aut(F2)-image exact-complex census",
        "",
        "## Frozen bound",
        "",
        f"- Maps: {census['map_count']}",
        f"- Exact cellular keys: {census['exact_cellular_key_count']}",
        f"- Ordered memberships: {census['ordered_membership_count']}",
        "",
    ]
    lines.extend(
        _markdown_histogram(
            "Spelling-mode membership histogram",
            _manifest_mapping(
                census["spelling_mode_histogram"], "mode histogram"
            ),
        )
    )
    lines.extend(
        _markdown_histogram(
            "Exact support histogram",
            _manifest_mapping(census["support_histogram"], "support histogram"),
        )
    )
    lines.extend(
        _markdown_histogram(
            "Verdict histogram",
            _manifest_mapping(census["verdict_histogram"], "verdict histogram"),
        )
    )
    lines.extend(["## Exact source hashes", ""])
    manifest_hash = _manifest_mapping(source_hashes["manifest"], "manifest hash")
    driver_hash = _manifest_mapping(
        source_hashes["decision_driver"], "driver hash"
    )
    lines.extend(
        (
            f"- `{manifest_hash['path']}`: `{manifest_hash['sha256']}`",
            f"- `{driver_hash['path']}`: `{driver_hash['sha256']}`",
        )
    )
    for group in ("prior_corpus", "selected_solvers", "support_proofs"):
        for entry_value in _manifest_list(source_hashes[group], group):
            entry = _manifest_mapping(entry_value, group)
            lines.append(f"- `{entry['path']}`: `{entry['sha256']}`")
    lines.extend(["", "## Quarantined spherical row IDs", ""])
    quarantined = _manifest_list(
        payload["quarantined_row_ids"], "quarantined row IDs"
    )
    if quarantined:
        lines.extend(f"- `{row_id}`" for row_id in quarantined)
    else:
        lines.append("- None")
    lines.extend(["", "## Proof limits", ""])
    lines.extend(
        f"- {limit}" for limit in _manifest_list(payload["proof_limits"], "proof limits")
    )
    return ("\n".join(lines) + "\n").encode("utf-8")


def write_certificate(
    json_path: Path = DEFAULT_CERTIFICATE_PATH,
    markdown_path: Path = DEFAULT_MARKDOWN_PATH,
    root: Path = _ROOT,
    manifest_path: Path | None = None,
    *,
    expected_manifest_sha256: str = FROZEN_MANIFEST_SHA256,
    expected_map_count: int = 1_000,
    expected_bucket_count: int = 285,
    expected_membership_count: int = 3_000,
) -> None:
    certificate_bytes = build_certificate_bytes(
        root,
        manifest_path,
        expected_manifest_sha256=expected_manifest_sha256,
        expected_map_count=expected_map_count,
        expected_bucket_count=expected_bucket_count,
        expected_membership_count=expected_membership_count,
    )
    verified = verify_certificate_bytes(
        certificate_bytes,
        root,
        manifest_path,
        expected_manifest_sha256=expected_manifest_sha256,
        expected_map_count=expected_map_count,
        expected_bucket_count=expected_bucket_count,
        expected_membership_count=expected_membership_count,
    )
    json_path.write_bytes(certificate_bytes)
    markdown_path.write_bytes(build_markdown_bytes(verified))


def check_certificate(
    json_path: Path = DEFAULT_CERTIFICATE_PATH,
    markdown_path: Path = DEFAULT_MARKDOWN_PATH,
    root: Path = _ROOT,
    manifest_path: Path | None = None,
    *,
    expected_manifest_sha256: str = FROZEN_MANIFEST_SHA256,
    expected_map_count: int = 1_000,
    expected_bucket_count: int = 285,
    expected_membership_count: int = 3_000,
) -> None:
    certificate_bytes = json_path.read_bytes()
    verified = verify_certificate_bytes(
        certificate_bytes,
        root,
        manifest_path,
        expected_manifest_sha256=expected_manifest_sha256,
        expected_map_count=expected_map_count,
        expected_bucket_count=expected_bucket_count,
        expected_membership_count=expected_membership_count,
    )
    if markdown_path.read_bytes() != build_markdown_bytes(verified):
        raise AssertionError("Markdown bytes differ from the verified certificate")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="emit or independently replay the bounded AK(3) frontier"
    )
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument("--write", action="store_true")
    operation.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        write_certificate()
        print("certificate write: OK")
    else:
        check_certificate()
        print("certificate check: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
