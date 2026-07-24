"""Exact thickenability certificate for the one-hop AK(3) CoV family."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from dataclasses import asdict, fields
from pathlib import Path

from experiments.greedy_tests.spec.words import str_to_word, word_to_str
from experiments.stable_ac.cov import cov
from experiments.stable_ac.thickenable.neuwirth_one_loop_solver import (
    solve_one_loop_spherical,
)
from experiments.stable_ac.thickenable.neuwirth_permutation_certificate import (
    enumerate_trace,
)
from experiments.stable_ac.thickenable.neuwirth_rank_solver import (
    SearchCounters,
    solve_spherical,
)


SCHEMA = "ak3-cov-thickenability-v1"
AK3 = ("xyxYXY", "xxxYYYY")
ROOT = Path(__file__).resolve().parents[3]
RESULT_PATH = ROOT / "results/stable_ac/theory/ak3_cov_thickenability.json"
SOURCE_PATHS = {
    "cov_implementation": ROOT / "experiments/stable_ac/cov/cov.py",
    "cov_stability_proof": (
        ROOT / "results/stable_ac/theory/MU_CRITERION.md"
    ),
    "base_rank_solver": (
        ROOT / "experiments/stable_ac/thickenable/neuwirth_rank_solver.py"
    ),
    "one_loop_rank_solver": (
        ROOT
        / "experiments/stable_ac/thickenable/neuwirth_one_loop_solver.py"
    ),
    "base_theorem": (
        ROOT / "literature/proofs/AK3_SYNCHRONIZED_PLANARITY.md"
    ),
    "one_loop_theorem": (
        ROOT
        / "literature/proofs/AK3_ONE_LOOP_SYNCHRONIZED_PLANARITY.md"
    ),
    "factorial_solver": (
        ROOT
        / "experiments/stable_ac/thickenable/neuwirth_permutation_certificate.py"
    ),
    "certificate_driver": Path(__file__).resolve(),
}
CALIBRATIONS = (
    {
        "words": ("xxy", "yXYy"),
        "spherical": True,
        "expected_cases": 12,
        "accepting_orders": 2,
        "minimum_genus": 0,
        "trace_sha256": (
            "f6d207f62193e7f90d1a769fe722ca7eb6c86d309ee28670d8af87ae45bc0652"
        ),
    },
    {
        "words": ("x", "YXyxyy"),
        "spherical": False,
        "expected_cases": 12,
        "accepting_orders": 0,
        "minimum_genus": 1,
        "trace_sha256": (
            "72e931ec7e61c7b3b2f6ff675ec33c4a8b36c2cd4ffac72866955fc29190400f"
        ),
    },
)


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


def _stable_cov_results():
    r1, r2 = map(str_to_word, AK3)
    family = cov.subword_candidates(r1, r2)
    results = cov.enumerate_cov(r1, r2, family=family)
    output_pairs = tuple((result.r1, result.r2) for result in results)
    if len(results) != 34 or len(set(output_pairs)) != len(results):
        raise AssertionError("unexpected AK(3) CoV output census")
    for result in results:
        if not (
            result.applicable
            and result.n_cov == 1
            and result.n_subs >= 1
            and result.z_word in family
            and result.iso_gen in ("x", "y")
            and result.iso_index in (0, 1)
            and result.expr is not None
            and len(result.meta.get("intermediate", ())) == 3
        ):
            raise AssertionError("CoV output misses a stable-move hypothesis")
    return family, results


def _decision_record(index: int, result) -> dict[str, object]:
    words = (word_to_str(result.r1), word_to_str(result.r2))
    decision = solve_spherical(words)
    if decision.spherical is None:
        decision = solve_one_loop_spherical(words)
    if decision.spherical is None:
        verdict = "UNSUPPORTED"
    elif decision.spherical:
        verdict = "SPHERICAL_REQUIRES_REGINA"
    else:
        verdict = "NOT_SPHERICAL"
    if decision.spherical is False and not decision.counters.exhaustive:
        raise AssertionError(f"incomplete negative CoV decision at row {index}")
    if decision.spherical is True and decision.witness is None:
        raise AssertionError(f"positive CoV decision lacks witness at row {index}")
    return {
        "index": index,
        "z_word": word_to_str(result.z_word),
        "iso_gen": result.iso_gen,
        "iso_index": result.iso_index,
        "n_subs": result.n_subs,
        "expr": list(result.expr),
        "cap": result.cap,
        "intermediate": [
            list(word) for word in result.meta["intermediate"]
        ],
        "stable_move_hypotheses_verified": True,
        "words": list(words),
        "support": decision.support.kind,
        "simple_edges": [
            list(edge) for edge in sorted(decision.support.simple_edges)
        ],
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
    records = []
    for expected in CALIBRATIONS:
        words = expected["words"]
        decision = solve_one_loop_spherical(words)
        factorial = enumerate_trace(words)
        actual = {
            "words": list(words),
            "support": decision.support.kind,
            "rank_spherical": decision.spherical,
            "factorial_cases": factorial.enumerated_cases,
            "accepting_factorial_orders": len(factorial.accepting_orders),
            "minimum_genus": factorial.minimum_genus,
            "trace_sha256": factorial.trace_sha256,
        }
        if (
            decision.spherical is not expected["spherical"]
            or decision.spherical is not bool(factorial.accepting_orders)
            or factorial.expected_cases != expected["expected_cases"]
            or factorial.enumerated_cases != expected["expected_cases"]
            or len(factorial.accepting_orders)
            != expected["accepting_orders"]
            or factorial.minimum_genus != expected["minimum_genus"]
            or factorial.trace_sha256 != expected["trace_sha256"]
        ):
            raise AssertionError(
                f"unexpected one-loop factorial calibration for {words!r}"
            )
        records.append(actual)
    return {
        "fixture_count": len(records),
        "positive_fixture_count": sum(
            bool(record["rank_spherical"]) for record in records
        ),
        "negative_fixture_count": sum(
            not bool(record["rank_spherical"]) for record in records
        ),
        "records": records,
        "trace_sha256": _ordered_digest(tuple(records)),
    }


def _aggregate_counters(
    records: tuple[dict[str, object], ...],
) -> dict[str, int]:
    names = tuple(
        field.name
        for field in fields(SearchCounters)
        if field.name != "exhaustive"
    )
    aggregate = {
        name: sum(int(record["counters"][name]) for record in records)
        for name in names
    }
    aggregate["exhaustive_output_count"] = sum(
        bool(record["counters"]["exhaustive"]) for record in records
    )
    return aggregate


def build_certificate(
    run_factorial_crosscheck: bool = True,
) -> dict[str, object]:
    family, results = _stable_cov_results()
    records = tuple(
        _decision_record(index, result)
        for index, result in enumerate(results)
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
            "Every exact output of the complete no-collapse subword-CoV "
            "family on AK(3) has a non-spherical compatible Neuwirth link."
        ),
        "candidate_lemma": candidate_lemma,
        "ak3": list(AK3),
        "cov_family_tag": cov.SUBWORD_FAMILY_TAG,
        "subword_candidate_count": len(family),
        "cov_output_count": len(records),
        "stable_equivalence_count": sum(
            bool(record["stable_move_hypotheses_verified"])
            for record in records
        ),
        "support_counts": dict(sorted(support_counts.items())),
        "verdict_counts": dict(sorted(verdict_counts.items())),
        "aggregate_counters": _aggregate_counters(records),
        "output_records": list(records),
        "factorial_crosscheck": (
            _factorial_crosscheck() if run_factorial_crosscheck else None
        ),
        "source_sha256": _source_hashes(),
        "trace_sha256": _ordered_digest(records),
    }


def verify_certificate(
    data: dict[str, object],
    run_factorial_crosscheck: bool = True,
) -> None:
    if data.get("schema") != SCHEMA:
        raise AssertionError(f"wrong schema: {data.get('schema')!r}")
    if data.get("source_sha256") != _source_hashes():
        raise AssertionError("source hash mismatch")
    expected = build_certificate(
        run_factorial_crosscheck=run_factorial_crosscheck
    )
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
        f"{data['cov_output_count']} stable CoV outputs, "
        f"{data['verdict_counts'].get('NOT_SPHERICAL', 0)} non-spherical, "
        f"{data['verdict_counts'].get('SPHERICAL_REQUIRES_REGINA', 0)} "
        "Regina candidates"
    )


if __name__ == "__main__":
    main()
