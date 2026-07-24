"""Chained thickenability certificate for two exact AK(3) CoV hops."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

from experiments.greedy_tests.spec.words import word_to_str
from experiments.stable_ac.cov import cov
from experiments.stable_ac.thickenable import (
    cov_thickenability_certificate as upstream_driver,
)
from experiments.stable_ac.thickenable.neuwirth_one_loop_solver import (
    solve_one_loop_spherical,
)
from experiments.stable_ac.thickenable.neuwirth_p4_solver import (
    solve_four_germ_spherical,
)
from experiments.stable_ac.thickenable.neuwirth_paw_one_loop_solver import (
    solve_paw_one_loop_spherical,
)
from experiments.stable_ac.thickenable.neuwirth_permutation_certificate import (
    enumerate_trace,
)
from experiments.stable_ac.thickenable.neuwirth_rank_solver import (
    solve_spherical,
)


SCHEMA = "ak3-two-hop-cov-thickenability-v1"
ROOT = Path(__file__).resolve().parents[3]
RESULT_PATH = (
    ROOT / "results/stable_ac/theory/ak3_two_hop_cov_thickenability.json"
)
SOURCE_PATHS = {
    "word_codec": ROOT / "experiments/greedy_tests/spec/words.py",
    "cov_implementation": ROOT / "experiments/stable_ac/cov/cov.py",
    "cov_stability_proof": (
        ROOT / "results/stable_ac/theory/MU_CRITERION.md"
    ),
    "base_rank_solver": (
        ROOT / "experiments/stable_ac/thickenable/neuwirth_rank_solver.py"
    ),
    "p4_rank_solver": (
        ROOT / "experiments/stable_ac/thickenable/neuwirth_p4_solver.py"
    ),
    "one_loop_rank_solver": (
        ROOT
        / "experiments/stable_ac/thickenable/neuwirth_one_loop_solver.py"
    ),
    "paw_loop_rank_solver": (
        ROOT
        / "experiments/stable_ac/thickenable/neuwirth_paw_one_loop_solver.py"
    ),
    "base_theorem": (
        ROOT / "literature/proofs/AK3_SYNCHRONIZED_PLANARITY.md"
    ),
    "p4_theorem": (
        ROOT / "literature/proofs/AK3_P4_SYNCHRONIZED_PLANARITY.md"
    ),
    "one_loop_theorem": (
        ROOT
        / "literature/proofs/AK3_ONE_LOOP_SYNCHRONIZED_PLANARITY.md"
    ),
    "paw_loop_theorem": (
        ROOT / "literature/proofs/AK3_PAW_ONE_LOOP_PLANARITY.md"
    ),
    "factorial_solver": (
        ROOT
        / "experiments/stable_ac/thickenable/neuwirth_permutation_certificate.py"
    ),
    "upstream_certificate_driver": (
        ROOT
        / "experiments/stable_ac/thickenable/cov_thickenability_certificate.py"
    ),
    "certificate_driver": Path(__file__).resolve(),
}
CALIBRATIONS = (
    {
        "words": ("yx", "yxXX"),
        "spherical": True,
        "expected_cases": 6,
        "accepting_orders": 2,
        "minimum_genus": 0,
        "trace_sha256": (
            "86603f18c16d639a4bc169949db5d356eec5d5c7f7adf776056685f2f9683f64"
        ),
    },
    {
        "words": ("XYyyX", "X"),
        "spherical": False,
        "expected_cases": 4,
        "accepting_orders": 0,
        "minimum_genus": 1,
        "trace_sha256": (
            "001ff74eb0aabb9cf2c79af67c7a4625ccbd4d44704a2c2107446edc966e76f5"
        ),
    },
    {
        "words": ("x", "xxyxYy"),
        "spherical": True,
        "expected_cases": 12,
        "accepting_orders": 2,
        "minimum_genus": 0,
        "trace_sha256": (
            "4a25122e7456ebadfbe2b8a1179d77a8196e963c9fd073c7ab437df943a75680"
        ),
    },
)


@dataclass(frozen=True)
class TwoHopPath:
    parent_index: int
    candidate_count: int
    result: object


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


def _stable_hypotheses(result, family) -> bool:
    return bool(
        result.applicable
        and result.n_cov == 1
        and result.n_subs >= 1
        and result.z_word in family
        and result.iso_gen in ("x", "y")
        and result.iso_index in (0, 1)
        and result.expr is not None
        and len(result.meta.get("intermediate", ())) == 3
    )


def enumerate_two_hop_paths():
    _, first_hops = upstream_driver._stable_cov_results()
    paths_by_output = {}
    raw_count = 0
    for parent_index, parent in enumerate(first_hops):
        family = cov.subword_candidates(parent.r1, parent.r2)
        second_hops = cov.enumerate_cov(
            parent.r1,
            parent.r2,
            family=family,
        )
        for result in second_hops:
            raw_count += 1
            if not _stable_hypotheses(result, family):
                raise AssertionError(
                    "second CoV misses a stable-move hypothesis"
                )
            paths_by_output.setdefault(
                (result.r1, result.r2),
                TwoHopPath(parent_index, len(family), result),
            )
    paths = tuple(paths_by_output.values())
    if (
        len(first_hops) != 34
        or raw_count != 1_724
        or len(paths) != 1_352
    ):
        raise AssertionError("unexpected two-hop AK(3) CoV census")
    return first_hops, paths, raw_count


def _validate_exact_paths(first_hops, paths, raw_second_hop_count: int) -> None:
    _, exact_first_hops = upstream_driver._stable_cov_results()
    if tuple(first_hops) != tuple(exact_first_hops):
        raise ValueError("first-hop inputs must be the exact AK(3) CoV census")

    exact_by_parent = {}
    exact_raw_count = 0
    for parent_index, parent in enumerate(first_hops):
        family = cov.subword_candidates(parent.r1, parent.r2)
        results = tuple(
            cov.enumerate_cov(parent.r1, parent.r2, family=family)
        )
        exact_by_parent[parent_index] = (family, results)
        exact_raw_count += len(results)
    if raw_second_hop_count != exact_raw_count:
        raise ValueError("raw second-hop count does not match exact replay")

    for path in paths:
        if not 0 <= path.parent_index < len(first_hops):
            raise ValueError("two-hop path has invalid parent index")
        family, exact_results = exact_by_parent[path.parent_index]
        if path.candidate_count != len(family):
            raise ValueError("two-hop path has wrong candidate count")
        if not _stable_hypotheses(path.result, family):
            raise ValueError("two-hop path misses a stable-move hypothesis")
        if path.result not in exact_results:
            raise ValueError("two-hop path is not an exact CoV output")


def _cov_record(index: int, result) -> dict[str, object]:
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
        "words": [
            word_to_str(result.r1),
            word_to_str(result.r2),
        ],
        "stable_move_hypotheses_verified": True,
    }


def _dispatch(words: tuple[str, str]):
    decision = solve_spherical(words)
    if decision.spherical is None:
        decision = solve_four_germ_spherical(words)
    if decision.spherical is None:
        decision = solve_one_loop_spherical(words)
    if decision.spherical is None:
        decision = solve_paw_one_loop_spherical(words)
    return decision


def _decision_record(index: int, path: TwoHopPath) -> dict[str, object]:
    result = path.result
    words = (word_to_str(result.r1), word_to_str(result.r2))
    decision = _dispatch(words)
    if decision.spherical is None:
        verdict = "UNSUPPORTED"
    elif decision.spherical:
        verdict = "SPHERICAL_REQUIRES_REGINA"
    else:
        verdict = "NOT_SPHERICAL"
    if decision.spherical is False and not decision.counters.exhaustive:
        raise AssertionError(
            f"incomplete negative two-hop decision at row {index}"
        )
    if decision.spherical is True and decision.witness is None:
        raise AssertionError(
            f"positive two-hop decision lacks witness at row {index}"
        )
    return {
        "index": index,
        "parent_first_hop_index": path.parent_index,
        "second_candidate_count": path.candidate_count,
        "second_hop": _cov_record(index, result),
        "stable_move_hypotheses_verified": True,
        "words": list(words),
        "total_length": sum(map(len, words)),
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
        decision = solve_paw_one_loop_spherical(words)
        factorial = enumerate_trace(words)
        record = {
            "words": list(words),
            "support": decision.support.kind,
            "rank_spherical": decision.spherical,
            "factorial_cases": factorial.enumerated_cases,
            "accepting_factorial_orders": len(factorial.accepting_orders),
            "minimum_genus": factorial.minimum_genus,
            "trace_sha256": factorial.trace_sha256,
            "witness_scheme": (
                decision.witness.scheme
                if decision.witness is not None
                else None
            ),
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
                f"unexpected paw factorial calibration for {words!r}"
            )
        records.append(record)
    if "paw-gap-1-" not in records[2]["witness_scheme"]:
        raise AssertionError("inside-class paw gap was not exercised")
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
    names = (
        "scheme_budget",
        "schemes_considered",
        "phase_pair_budget",
        "phase_pairs_considered",
        "component_seed_budget",
        "component_seed_attempts",
        "closed_component_assignments",
        "within_cycle_collision_rejections",
        "witness_replay_failures",
    )
    aggregate = {
        name: sum(
            int(record["counters"].get(name, 0)) for record in records
        )
        for name in names
    }
    aggregate["exhaustive_output_count"] = sum(
        bool(record["counters"]["exhaustive"]) for record in records
    )
    aggregate["paw_raw_component_combination_budget"] = sum(
        int(
            record["counters"].get(
                "raw_component_combination_budget",
                0,
            )
        )
        for record in records
    )
    aggregate["paw_complement_lookups"] = sum(
        int(record["counters"].get("complement_lookups", 0))
        for record in records
    )
    return aggregate


def _load_upstream_trace() -> str:
    with upstream_driver.RESULT_PATH.open() as handle:
        upstream = json.load(handle)
    return str(upstream["trace_sha256"])


def build_certificate(
    first_hops=None,
    paths: tuple[TwoHopPath, ...] | None = None,
    raw_second_hop_count: int | None = None,
    upstream_trace: str | None = None,
    run_factorial_crosscheck: bool = True,
) -> dict[str, object]:
    full_census = paths is None
    if first_hops is None or paths is None or raw_second_hop_count is None:
        first_hops, paths, raw_second_hop_count = enumerate_two_hop_paths()
    first_hops = tuple(first_hops)
    paths = tuple(paths)
    if upstream_trace is None:
        upstream_trace = _load_upstream_trace()
    if not isinstance(upstream_trace, str):
        raise ValueError("upstream trace is required")
    _validate_exact_paths(first_hops, paths, raw_second_hop_count)
    output_pairs = tuple(
        (path.result.r1, path.result.r2) for path in paths
    )
    if len(set(output_pairs)) != len(output_pairs):
        raise ValueError("two-hop output paths must be distinct")

    first_records = tuple(
        _cov_record(index, result)
        for index, result in enumerate(first_hops)
    )
    records = tuple(
        _decision_record(index, path)
        for index, path in enumerate(paths)
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
            "Every distinct exact output of two composed gated subword-CoV "
            "moves from AK(3) has a non-spherical compatible Neuwirth link."
        ),
        "candidate_lemma": candidate_lemma,
        "upstream_trace": upstream_trace,
        "full_census": full_census,
        "first_hop_count": len(first_hops),
        "raw_second_hop_count": raw_second_hop_count,
        "output_count": len(records),
        "stable_equivalence_count": sum(
            bool(record["stable_move_hypotheses_verified"])
            for record in records
        ),
        "support_counts": dict(sorted(support_counts.items())),
        "verdict_counts": dict(sorted(verdict_counts.items())),
        "aggregate_counters": _aggregate_counters(records),
        "first_hop_records": list(first_records),
        "output_records": list(records),
        "factorial_crosscheck": (
            _factorial_crosscheck() if run_factorial_crosscheck else None
        ),
        "source_sha256": _source_hashes(),
        "trace_sha256": _ordered_digest(records),
    }


def verify_certificate(
    data: dict[str, object],
    verify_upstream: bool = True,
    first_hops=None,
    paths: tuple[TwoHopPath, ...] | None = None,
    raw_second_hop_count: int | None = None,
    run_factorial_crosscheck: bool = True,
) -> None:
    if data.get("schema") != SCHEMA:
        raise AssertionError(f"wrong schema: {data.get('schema')!r}")
    if verify_upstream:
        with upstream_driver.RESULT_PATH.open() as handle:
            upstream = json.load(handle)
        upstream_driver.verify_certificate(upstream)
        if data.get("upstream_trace") != upstream.get("trace_sha256"):
            raise AssertionError("upstream trace mismatch")
    if data.get("source_sha256") != _source_hashes():
        raise AssertionError("source hash mismatch")
    expected = build_certificate(
        first_hops=first_hops,
        paths=paths,
        raw_second_hop_count=raw_second_hop_count,
        upstream_trace=str(data.get("upstream_trace")),
        run_factorial_crosscheck=run_factorial_crosscheck,
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
        f"{data['output_count']} distinct two-hop stable CoV outputs, "
        f"{data['verdict_counts'].get('NOT_SPHERICAL', 0)} non-spherical, "
        f"{data['verdict_counts'].get('SPHERICAL_REQUIRES_REGINA', 0)} "
        "Regina candidates"
    )


if __name__ == "__main__":
    main()
