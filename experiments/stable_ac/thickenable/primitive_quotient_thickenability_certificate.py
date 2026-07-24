"""Certificate for thickenability of AK(3) primitive-single quotients."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from dataclasses import asdict
from pathlib import Path

from experiments.stable_ac.rank3_compression.primitive_single_certificate import (
    RESULT_PATH as UPSTREAM_PATH,
    verify_certificate as verify_upstream_certificate,
)
from experiments.stable_ac.thickenable.neuwirth_p4_solver import (
    solve_four_germ_spherical,
)
from experiments.stable_ac.thickenable.neuwirth_permutation_certificate import (
    enumerate_trace,
)
from experiments.stable_ac.thickenable.neuwirth_rank_solver import (
    classify_support,
)


SCHEMA = "ak3-primitive-quotient-thickenability-v1"
ROOT = Path(__file__).resolve().parents[3]
RESULT_PATH = (
    ROOT
    / "results/stable_ac/theory/ak3_primitive_quotient_thickenability.json"
)
SOURCE_PATHS = {
    "base_rank_solver": (
        ROOT
        / "experiments/stable_ac/thickenable/neuwirth_rank_solver.py"
    ),
    "p4_rank_solver": (
        ROOT
        / "experiments/stable_ac/thickenable/neuwirth_p4_solver.py"
    ),
    "p4_theorem": (
        ROOT
        / "literature/proofs/AK3_P4_SYNCHRONIZED_PLANARITY.md"
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


def _decision_record(words: tuple[str, str]) -> dict[str, object]:
    decision = solve_four_germ_spherical(words)
    if decision.spherical is None:
        verdict = "UNSUPPORTED"
    elif decision.spherical:
        verdict = "SPHERICAL_REQUIRES_REGINA"
    else:
        verdict = "NOT_SPHERICAL"
    if decision.spherical is False and not decision.counters.exhaustive:
        raise AssertionError(f"incomplete negative decision for {words!r}")
    if decision.spherical is True and decision.witness is None:
        raise AssertionError(f"positive decision has no witness for {words!r}")
    return {
        "words": list(words),
        "support": decision.support.kind,
        "verdict": verdict,
        "reason": decision.reason,
        "counters": _jsonable(asdict(decision.counters)),
        "witness": (
            _jsonable(asdict(decision.witness))
            if decision.witness is not None
            else None
        ),
    }


_INVERSE = {"x": "X", "X": "x", "y": "Y", "Y": "y"}
_LETTERS = "xXyY"


def _cyclically_reduced(word: str) -> bool:
    return all(
        word[(index + 1) % len(word)] != _INVERSE[letter]
        for index, letter in enumerate(word)
    )


def _least_rotation(word: str) -> str:
    return min(word[index:] + word[:index] for index in range(len(word)))


def _small_p4_pairs() -> tuple[tuple[str, str], ...]:
    words_by_length = {
        length: sorted(
            {
                _least_rotation("".join(letters))
                for letters in itertools.product(_LETTERS, repeat=length)
                if _cyclically_reduced("".join(letters))
            }
        )
        for length in range(1, 7)
    }
    pairs = set()
    for total_length in range(2, 8):
        for first_length in range(1, total_length):
            second_length = total_length - first_length
            for first in words_by_length[first_length]:
                for second in words_by_length[second_length]:
                    pair = tuple(sorted((first, second)))
                    support = classify_support(pair)
                    degrees = Counter()
                    for left, right in support.simple_edges:
                        degrees[left] += 1
                        degrees[right] += 1
                    if (
                        len(support.simple_edges) == 3
                        and sorted(degrees[vertex] for vertex in range(4))
                        == [1, 1, 2, 2]
                    ):
                        pairs.add(pair)
    return tuple(sorted(pairs))


def _small_p4_crosscheck() -> dict[str, object]:
    records = []
    counts = Counter()
    nonzero_shifts = 0
    for words in _small_p4_pairs():
        decision = solve_four_germ_spherical(words)
        factorial = enumerate_trace(words)
        rank_accepts = decision.spherical is True
        factorial_accepts = bool(factorial.accepting_orders)
        if rank_accepts != factorial_accepts:
            raise AssertionError(f"P4/factorial disagreement for {words!r}")
        counts["SPHERICAL" if rank_accepts else "NOT_SPHERICAL"] += 1
        if (
            decision.witness is not None
            and decision.witness.cut not in (None, 0)
        ):
            nonzero_shifts += 1
        records.append((list(words), rank_accepts))
    if len(records) != 476 or counts != {
        "SPHERICAL": 444,
        "NOT_SPHERICAL": 32,
    }:
        raise AssertionError("unexpected small P4 calibration census")
    if not nonzero_shifts:
        raise AssertionError("small P4 census did not exercise a nonzero shift")
    return {
        "pair_count": len(records),
        "verdict_counts": dict(sorted(counts.items())),
        "nonzero_shift_positive_count": nonzero_shifts,
        "trace_sha256": _ordered_digest(tuple(records)),
    }


def _load_upstream() -> tuple[
    tuple[tuple[str, str], ...],
    str,
    dict[str, int],
]:
    with UPSTREAM_PATH.open() as handle:
        upstream = json.load(handle)
    outputs = tuple(
        sorted(
            {
                tuple(row["output"])
                for row in upstream["primitive_occurrences"]
            }
        )
    )
    primitive_sources = {
        int(row["source_index"])
        for row in upstream["primitive_occurrences"]
    }
    metadata = {
        "rank3_source_count": int(upstream["source_count"]),
        "source_with_primitive_count": len(primitive_sources),
        "source_without_primitive_count": (
            int(upstream["source_count"]) - len(primitive_sources)
        ),
        "primitive_occurrence_count": int(
            upstream["primitive_occurrence_count"]
        ),
    }
    return outputs, str(upstream["trace_sha256"]), metadata


def build_certificate(
    outputs: tuple[tuple[str, str], ...] | None = None,
    upstream_trace: str | None = None,
    run_small_crosscheck: bool = True,
) -> dict[str, object]:
    if outputs is None:
        outputs, loaded_trace, metadata = _load_upstream()
        if upstream_trace is not None and upstream_trace != loaded_trace:
            raise ValueError("explicit upstream trace disagrees with certificate")
        upstream_trace = loaded_trace
    else:
        outputs = tuple(sorted(set(map(tuple, outputs))))
        metadata = {
            "rank3_source_count": None,
            "source_with_primitive_count": None,
            "source_without_primitive_count": None,
            "primitive_occurrence_count": None,
        }
    if not isinstance(upstream_trace, str):
        raise ValueError("upstream_trace is required")
    if any(len(output) != 2 for output in outputs):
        raise ValueError("every quotient must have two relators")

    records = tuple(_decision_record(output) for output in outputs)
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
            "Every exact primitive-single rank-two quotient in the certified "
            "AK(3) corridor has a non-spherical compatible Neuwirth link."
        ),
        "candidate_lemma": candidate_lemma,
        "upstream_trace": upstream_trace,
        **metadata,
        "distinct_output_count": len(outputs),
        "support_counts": dict(sorted(support_counts.items())),
        "verdict_counts": dict(sorted(verdict_counts.items())),
        "output_records": list(records),
        "small_p4_crosscheck": (
            _small_p4_crosscheck() if run_small_crosscheck else None
        ),
        "source_sha256": _source_hashes(),
        "trace_sha256": _ordered_digest(records),
    }


def verify_certificate(
    data: dict[str, object],
    verify_upstream: bool = True,
    run_small_crosscheck: bool = True,
) -> None:
    if data.get("schema") != SCHEMA:
        raise AssertionError(f"wrong schema: {data.get('schema')!r}")
    rows = data.get("output_records")
    if not isinstance(rows, list):
        raise AssertionError("output_records must be a list")
    outputs = tuple(
        tuple(row.get("words", ()))
        for row in rows
        if isinstance(row, dict)
    )
    if len(outputs) != len(rows) or any(len(output) != 2 for output in outputs):
        raise AssertionError("malformed output records")
    if outputs != tuple(sorted(set(outputs))):
        raise AssertionError("output records are not sorted and distinct")

    upstream_trace = data.get("upstream_trace")
    if not isinstance(upstream_trace, str):
        raise AssertionError("upstream_trace must be a string")
    if verify_upstream:
        with UPSTREAM_PATH.open() as handle:
            upstream = json.load(handle)
        verify_upstream_certificate(upstream)
        expected_outputs, expected_trace, expected_metadata = _load_upstream()
        if outputs != expected_outputs:
            raise AssertionError("outputs differ from verified upstream")
        if upstream_trace != expected_trace:
            raise AssertionError("upstream trace mismatch")
        for key, value in expected_metadata.items():
            if data.get(key) != value:
                raise AssertionError(f"upstream metadata mismatch: {key}")

    if data.get("source_sha256") != _source_hashes():
        raise AssertionError("source hash mismatch")

    expected = build_certificate(
        outputs=outputs,
        upstream_trace=upstream_trace,
        run_small_crosscheck=run_small_crosscheck,
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
        f"{data['distinct_output_count']} primitive quotients, "
        f"{data['verdict_counts'].get('NOT_SPHERICAL', 0)} non-spherical, "
        f"{data['verdict_counts'].get('SPHERICAL_REQUIRES_REGINA', 0)} "
        "Regina candidates"
    )


if __name__ == "__main__":
    main()
