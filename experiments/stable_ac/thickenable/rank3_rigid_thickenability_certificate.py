"""Chained certificate for primitive-free rigid AK(3) thickenability."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from dataclasses import asdict, fields
from pathlib import Path

from experiments.stable_ac.rank3_compression.primitive_single_certificate import (
    RESULT_PATH as UPSTREAM_PATH,
    verify_certificate as verify_upstream_certificate,
)
from experiments.stable_ac.thickenable.neuwirth_permutation_certificate import (
    enumerate_trace,
)
from experiments.stable_ac.thickenable.neuwirth_rank3_rigid_solver import (
    RigidSearchCounters,
    classify_rigid_support,
    solve_rigid_spherical,
)


SCHEMA = "ak3-rank3-rigid-thickenability-v1"
ROOT = Path(__file__).resolve().parents[3]
RESULT_PATH = (
    ROOT / "results/stable_ac/theory/ak3_rank3_rigid_thickenability.json"
)
CALIBRATION_WORDS = ("XZXTz", "ZTxZZ", "ttXzX")
CALIBRATION_TRACE = (
    "04d2dde2da74fa1e3120a029fd1442afe46ec4c99d08665c01234b871885e40e"
)
SOURCE_PATHS = {
    "base_rank_solver": (
        ROOT / "experiments/stable_ac/thickenable/neuwirth_rank_solver.py"
    ),
    "factorial_solver": (
        ROOT
        / "experiments/stable_ac/thickenable/neuwirth_permutation_certificate.py"
    ),
    "rigid_rank_solver": (
        ROOT
        / "experiments/stable_ac/thickenable/neuwirth_rank3_rigid_solver.py"
    ),
    "rigid_theorem": (
        ROOT
        / "literature/proofs/AK3_RANK3_RIGID_THICKENABILITY.md"
    ),
    "certificate_driver": Path(__file__).resolve(),
}


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")


def _ordered_digest(items: tuple[object, ...]) -> str:
    digest = hashlib.sha256()
    for item in items:
        digest.update(_canonical_json(item))
        digest.update(b"\n")
    return digest.hexdigest()


def _source_hashes() -> dict[str, str]:
    return {
        name: hashlib.sha256(path.read_bytes()).hexdigest()
        for name, path in SOURCE_PATHS.items()
    }


def _jsonable(value: object) -> object:
    return json.loads(json.dumps(value, ensure_ascii=True))


def _load_upstream() -> tuple[
    tuple[tuple[int, tuple[str, str, str]], ...],
    str,
    dict[str, int],
]:
    with UPSTREAM_PATH.open() as handle:
        upstream = json.load(handle)
    all_sources = tuple(tuple(words) for words in upstream["sources"])
    primitive_sources = {
        int(row["source_index"])
        for row in upstream["primitive_occurrences"]
    }
    sources = tuple(
        (index, words)
        for index, words in enumerate(all_sources)
        if index not in primitive_sources
    )
    metadata = {
        "rank3_source_count": len(all_sources),
        "source_with_primitive_count": len(primitive_sources),
        "source_without_primitive_count": len(sources),
        "primitive_occurrence_count": int(
            upstream["primitive_occurrence_count"]
        ),
    }
    return sources, str(upstream["trace_sha256"]), metadata


def _decision_record(
    source_index: int,
    words: tuple[str, str, str],
) -> dict[str, object]:
    decision = solve_rigid_spherical(words)
    if decision.spherical is None:
        verdict = "UNSUPPORTED"
    elif decision.spherical:
        verdict = "SPHERICAL_REQUIRES_REGINA"
    else:
        verdict = "NOT_SPHERICAL"
    if decision.spherical is False and not decision.counters.exhaustive:
        raise AssertionError(
            f"incomplete negative decision for source {source_index}"
        )
    if decision.spherical is True and decision.witness is None:
        raise AssertionError(
            f"positive decision lacks witness for source {source_index}"
        )

    multiplicities = {
        f"{left}-{right}": len(edges)
        for (left, right), edges in decision.support.data.class_edges.items()
    }
    return {
        "source_index": source_index,
        "words": list(words),
        "total_length": sum(map(len, words)),
        "generator_occurrences": {
            generator: sum(
                letter.lower() == generator
                for word in words
                for letter in word
            )
            for generator in ("x", "z", "t")
        },
        "support": decision.support.kind,
        "simple_edges": [
            list(edge) for edge in sorted(decision.support.simple_edges)
        ],
        "parallel_multiplicities": multiplicities,
        "macro_rotation_count": len(decision.support.macro_rotations),
        "verdict": verdict,
        "reason": decision.reason,
        "counters": _jsonable(asdict(decision.counters)),
        "witness": (
            _jsonable(asdict(decision.witness))
            if decision.witness is not None
            else None
        ),
    }


def _factorial_crosscheck() -> dict[str, object]:
    decision = solve_rigid_spherical(CALIBRATION_WORDS)
    factorial = enumerate_trace(CALIBRATION_WORDS)
    if decision.spherical is not bool(factorial.accepting_orders):
        raise AssertionError("rigid-rank/factorial calibration disagreement")
    expected_histogram = {2: 6, 4: 296, 6: 3916, 8: 10674, 10: 2388}
    if (
        decision.support.kind != "K6-P5"
        or len(decision.support.macro_rotations) != 2
        or factorial.expected_cases != 17_280
        or factorial.enumerated_cases != factorial.expected_cases
        or factorial.accepting_orders
        or factorial.minimum_genus != 1
        or factorial.defect_histogram != expected_histogram
        or factorial.trace_sha256 != CALIBRATION_TRACE
    ):
        raise AssertionError("unexpected rigid factorial calibration census")

    degrees = Counter()
    for left, right in decision.support.simple_edges:
        degrees[left] += 1
        degrees[right] += 1
    macro_budget = math.prod(
        math.factorial(degrees[vertex] - 1) for vertex in range(6)
    )
    if macro_budget != 6_912:
        raise AssertionError("unexpected simple-support rotation budget")
    return {
        "words": list(CALIBRATION_WORDS),
        "support": decision.support.kind,
        "macro_rotation_enumeration_cases": macro_budget,
        "spherical_macro_rotation_count": len(
            decision.support.macro_rotations
        ),
        "factorial_cases": factorial.enumerated_cases,
        "accepting_factorial_orders": len(factorial.accepting_orders),
        "minimum_genus": factorial.minimum_genus,
        "defect_histogram": {
            str(defect): count
            for defect, count in sorted(factorial.defect_histogram.items())
        },
        "factorial_trace_sha256": factorial.trace_sha256,
        "rank_verdict": decision.verdict,
    }


def _aggregate_counters(
    records: tuple[dict[str, object], ...],
) -> dict[str, int]:
    names = tuple(
        field.name
        for field in fields(RigidSearchCounters)
        if field.name != "exhaustive"
    )
    aggregate = {
        name: sum(int(record["counters"][name]) for record in records)
        for name in names
    }
    aggregate["exhaustive_source_count"] = sum(
        bool(record["counters"]["exhaustive"]) for record in records
    )
    return aggregate


def build_certificate(
    sources: tuple[tuple[int, tuple[str, str, str]], ...] | None = None,
    upstream_trace: str | None = None,
    run_factorial_crosscheck: bool = True,
) -> dict[str, object]:
    if sources is None:
        sources, loaded_trace, metadata = _load_upstream()
        if upstream_trace is not None and upstream_trace != loaded_trace:
            raise ValueError("explicit upstream trace disagrees with certificate")
        upstream_trace = loaded_trace
    else:
        sources = tuple(
            sorted(
                (int(source_index), tuple(words))
                for source_index, words in sources
            )
        )
        metadata = {
            "rank3_source_count": None,
            "source_with_primitive_count": None,
            "source_without_primitive_count": None,
            "primitive_occurrence_count": None,
        }
    if not isinstance(upstream_trace, str):
        raise ValueError("upstream_trace is required")
    if len({source_index for source_index, _ in sources}) != len(sources):
        raise ValueError("source indices must be distinct")
    if any(len(words) != 3 for _, words in sources):
        raise ValueError("every rank-three source must have three relators")

    records = tuple(
        _decision_record(source_index, words)
        for source_index, words in sources
    )
    verdict_counts = Counter(record["verdict"] for record in records)
    support_counts = Counter(record["support"] for record in records)
    if verdict_counts.get("UNSUPPORTED"):
        candidate_lemma = "INCOMPLETE"
    elif verdict_counts.get("SPHERICAL_REQUIRES_REGINA"):
        candidate_lemma = "POSITIVE_REQUIRES_REGINA"
    else:
        candidate_lemma = "REFUTED"
    return {
        "schema": SCHEMA,
        "claim": (
            "Every primitive-free source in the certified rank-three AK(3) "
            "corridor has a non-spherical compatible Neuwirth link."
        ),
        "candidate_lemma": candidate_lemma,
        "upstream_trace": upstream_trace,
        **metadata,
        "source_count": len(sources),
        "support_counts": dict(sorted(support_counts.items())),
        "verdict_counts": dict(sorted(verdict_counts.items())),
        "aggregate_counters": _aggregate_counters(records),
        "source_records": list(records),
        "factorial_crosscheck": (
            _factorial_crosscheck() if run_factorial_crosscheck else None
        ),
        "source_sha256": _source_hashes(),
        "trace_sha256": _ordered_digest(records),
    }


def verify_certificate(
    data: dict[str, object],
    verify_upstream: bool = True,
    run_factorial_crosscheck: bool = True,
) -> None:
    if data.get("schema") != SCHEMA:
        raise AssertionError(f"wrong schema: {data.get('schema')!r}")
    rows = data.get("source_records")
    if not isinstance(rows, list):
        raise AssertionError("source_records must be a list")
    sources = tuple(
        (int(row.get("source_index")), tuple(row.get("words", ())))
        for row in rows
        if isinstance(row, dict)
    )
    if len(sources) != len(rows) or any(len(words) != 3 for _, words in sources):
        raise AssertionError("malformed source records")
    if sources != tuple(sorted(sources)):
        raise AssertionError("source records are not sorted")
    if len({source_index for source_index, _ in sources}) != len(sources):
        raise AssertionError("source indices are not distinct")
    if data.get("source_count") != len(sources):
        raise AssertionError("source count mismatch")

    upstream_trace = data.get("upstream_trace")
    if not isinstance(upstream_trace, str):
        raise AssertionError("upstream_trace must be a string")
    if verify_upstream:
        with UPSTREAM_PATH.open() as handle:
            upstream = json.load(handle)
        verify_upstream_certificate(upstream)
        expected_sources, expected_trace, expected_metadata = _load_upstream()
        if sources != expected_sources:
            raise AssertionError(
                "primitive-free sources differ from verified upstream"
            )
        if upstream_trace != expected_trace:
            raise AssertionError("upstream trace mismatch")
        for key, value in expected_metadata.items():
            if data.get(key) != value:
                raise AssertionError(f"upstream metadata mismatch: {key}")

    if data.get("source_sha256") != _source_hashes():
        raise AssertionError("source hash mismatch")

    expected = build_certificate(
        sources=sources,
        upstream_trace=upstream_trace,
        run_factorial_crosscheck=run_factorial_crosscheck,
    )
    if verify_upstream:
        _, _, metadata = _load_upstream()
        expected.update(metadata)
    if data != expected:
        differing = sorted(
            key
            for key in set(data) | set(expected)
            if data.get(key) != expected.get(key)
        )
        raise AssertionError(
            "certificate differs from complete replay in keys: "
            + ", ".join(differing)
        )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--output", type=Path)
    action.add_argument("--verify", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if args.output is not None:
        data = build_certificate()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"wrote {args.output}")
        return

    with RESULT_PATH.open() as handle:
        data = json.load(handle)
    verify_certificate(data)
    print(
        "CERTIFICATE VERIFIES: "
        f"{data['source_count']} primitive-free rank3 sources, "
        f"{data['verdict_counts'].get('NOT_SPHERICAL', 0)} non-spherical, "
        f"{data['verdict_counts'].get('SPHERICAL_REQUIRES_REGINA', 0)} "
        "Regina candidates"
    )


if __name__ == "__main__":
    main()
