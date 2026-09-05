"""Replayable signed-rank census of the closed height-17 AK(3) component."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections import Counter, deque
from dataclasses import asdict, dataclass
from pathlib import Path

from experiments.equivalence_classes.lib.acmoves import canon, children
from experiments.stable_ac.thickenable.neuwirth_rank_solver import (
    RankDecision,
    solve_spherical,
)


AK3 = ("xxxYYYY", "xyxYXY")
CEILING = 17
POP_CAP = 1_000
CHILD_OPTIONS = {
    "cap": CEILING - 1,
    "cyclic": True,
    "seam_only": False,
}
SCHEMA = "ak3-component-thickenability-v1"
EXPECTED_SUPPORT_HISTOGRAM = {"K4": 720, "K4-e": 278, "C4": 2}
REPO_ROOT = Path(__file__).resolve().parents[3]
SCANNER_PATH = "experiments/stable_ac/thickenable/scan_ak3_component.py"
RANK_SOLVER_PATH = (
    "experiments/stable_ac/thickenable/neuwirth_rank_solver.py"
)
ACMOVES_PATH = "experiments/equivalence_classes/lib/acmoves.py"
GREEDY_BASELINE_PATH = "experiments/search/greedy_baseline.py"
SOURCE_PATHS = {
    "scanner": SCANNER_PATH,
    "rank_solver": RANK_SOLVER_PATH,
    "acmoves": ACMOVES_PATH,
    "greedy_baseline": GREEDY_BASELINE_PATH,
}


class CertificateError(RuntimeError):
    pass


@dataclass(frozen=True)
class ComponentCensus:
    root: tuple[str, str]
    canonical_root: tuple[str, str]
    ceiling: int
    node_budget: int
    child_options: dict[str, int | bool]
    actual_pops: int
    component_size: int
    queue_exhausted: bool
    closure_verified: bool
    canonical_fixed_points_verified: bool
    sorted_state_sha256: str
    states: tuple[tuple[str, str], ...]


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, separators=(",", ":"), sort_keys=True
    ).encode("ascii")


def _ordered_digest(items: tuple[object, ...]) -> str:
    digest = hashlib.sha256()
    for item in items:
        digest.update(_canonical_json(item))
        digest.update(b"\n")
    return digest.hexdigest()


def _git(*args: str) -> bytes:
    try:
        return subprocess.run(
            ("git",) + args,
            cwd=REPO_ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
    except subprocess.CalledProcessError as exc:
        message = exc.stderr.decode("utf-8", errors="replace").strip()
        raise CertificateError(f"git {' '.join(args)} failed: {message}") from exc


def _head_commit() -> str:
    return _git("rev-parse", "HEAD").decode("ascii").strip()


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _current_blob(relative_path: str) -> bytes:
    path = REPO_ROOT / relative_path
    if not path.is_file():
        raise CertificateError(f"source path is missing: {relative_path}")
    return path.read_bytes()


def _commit_blob(source_commit: str, relative_path: str) -> bytes:
    if not re.fullmatch(r"[0-9a-f]{40,64}", source_commit):
        raise CertificateError("source commit is not a full hexadecimal object id")
    resolved = _git("rev-parse", "--verify", f"{source_commit}^{{commit}}")
    if resolved.decode("ascii").strip() != source_commit:
        raise CertificateError("source commit does not resolve to itself")
    return _git("show", f"{source_commit}:{relative_path}")


def _source_binding(
    relative_path: str, source_commit: str
) -> dict[str, str]:
    current_sha256 = _sha256(_current_blob(relative_path))
    historical_sha256 = _sha256(_commit_blob(source_commit, relative_path))
    if current_sha256 != historical_sha256:
        raise CertificateError(
            f"current source differs from {source_commit}: {relative_path}"
        )
    return {
        "path": relative_path,
        "source_commit_sha256": historical_sha256,
        "current_sha256": current_sha256,
    }


def _authenticate_binding(
    binding: dict[str, str], source_commit: str
) -> None:
    relative_path = binding.get("path")
    if not isinstance(relative_path, str):
        raise CertificateError("source binding has no path")
    historical = _sha256(_commit_blob(source_commit, relative_path))
    current = _sha256(_current_blob(relative_path))
    if binding.get("source_commit_sha256") != historical:
        raise CertificateError(
            f"recorded historical hash mismatch: {relative_path}"
        )
    if binding.get("current_sha256") != current:
        raise CertificateError(f"recorded current hash mismatch: {relative_path}")
    if historical != current:
        raise CertificateError(
            f"historical/current source mismatch: {relative_path}"
        )


def recompute_component() -> ComponentCensus:
    canonical_root = canon(*AK3, cyclic=True)
    if canon(*canonical_root, cyclic=True) != canonical_root:
        raise CertificateError("canonical root is not a canon fixed point")
    seen = {canonical_root}
    queue = deque([canonical_root])
    pops = 0
    while queue:
        if pops >= POP_CAP:
            raise CertificateError(
                f"component exceeds the hard {POP_CAP}-pop budget"
            )
        state = queue.popleft()
        pops += 1
        for child in children(
            state[0],
            state[1],
            cap=CHILD_OPTIONS["cap"],
            cyclic=CHILD_OPTIONS["cyclic"],
            seam_only=CHILD_OPTIONS["seam_only"],
        ):
            if canon(*child, cyclic=True) != child:
                raise CertificateError("move generator emitted a noncanonical child")
            if len(child[0]) + len(child[1]) > CEILING:
                continue
            if child not in seen:
                seen.add(child)
                queue.append(child)

    queue_exhausted = not queue
    if pops != POP_CAP or len(seen) != POP_CAP or not queue_exhausted:
        raise CertificateError(
            "height-17 component did not exhaust at exactly 1,000 states"
        )

    for state in seen:
        for child in children(
            state[0],
            state[1],
            cap=CHILD_OPTIONS["cap"],
            cyclic=CHILD_OPTIONS["cyclic"],
            seam_only=CHILD_OPTIONS["seam_only"],
        ):
            if canon(*child, cyclic=True) != child:
                raise CertificateError("closure replay found a noncanonical child")
            if len(child[0]) + len(child[1]) <= CEILING and child not in seen:
                raise CertificateError(
                    f"component is not closed: {state!r} -> {child!r}"
                )

    states = tuple(sorted(seen))
    if any(canon(*state, cyclic=True) != state for state in states):
        raise CertificateError("component contains a noncanonical state")
    return ComponentCensus(
        root=AK3,
        canonical_root=canonical_root,
        ceiling=CEILING,
        node_budget=POP_CAP,
        child_options=dict(CHILD_OPTIONS),
        actual_pops=pops,
        component_size=len(states),
        queue_exhausted=queue_exhausted,
        closure_verified=True,
        canonical_fixed_points_verified=True,
        sorted_state_sha256=_ordered_digest(states),
        states=states,
    )


def _counter_record(decision: RankDecision) -> dict[str, int | bool]:
    counters = asdict(decision.counters)
    if decision.spherical is False:
        required_equalities = (
            ("schemes_considered", "scheme_budget"),
            ("phase_pairs_considered", "phase_pair_budget"),
            ("component_seed_attempts", "component_seed_budget"),
            (
                "component_combinations_considered",
                "component_combination_budget",
            ),
        )
        if not counters["exhaustive"] or any(
            counters[actual] != counters[budget]
            for actual, budget in required_equalities
        ):
            raise CertificateError(
                f"incomplete negative rank search for {decision.words!r}"
            )
        if counters["witness_replay_failures"]:
            raise CertificateError(
                f"unreplayed candidate for {decision.words!r}"
            )
    return counters


def _witness_record(decision: RankDecision) -> dict[str, object] | None:
    if decision.witness is None:
        return None
    witness = asdict(decision.witness)
    if not (
        witness["euler_characteristic"] == 2
        and witness["genus"] == 0
        and witness["b_reversal_verified"]
        and witness["rank_partition_verified"]
        and witness["phase_equations_verified"]
    ):
        raise CertificateError(
            f"positive witness did not independently replay: {decision.words!r}"
        )
    return json.loads(json.dumps(witness, ensure_ascii=True))


def _decision_record(
    state: tuple[str, str], decision: RankDecision
) -> dict[str, object]:
    if decision.words != state:
        raise CertificateError("rank solver returned a decision for another state")
    if decision.spherical is None or decision.support.kind == "UNSUPPORTED":
        raise CertificateError(f"unsupported component state: {state!r}")
    witness = _witness_record(decision)
    if decision.spherical:
        verdict = "SPHERICAL"
        disposition = "REGINA_REQUIRED"
        if witness is None:
            raise CertificateError("positive decision has no replayed witness")
    else:
        verdict = "NOT_SPHERICAL"
        disposition = "NOT_THICKENABLE_EXACT_COMPLEX"
        if witness is not None:
            raise CertificateError("negative decision unexpectedly has a witness")
    return {
        "words": list(state),
        "support": decision.support.kind,
        "verdict": verdict,
        "disposition": disposition,
        "counters": _counter_record(decision),
        "witness": witness,
    }


def _component_record(component: ComponentCensus) -> dict[str, object]:
    return {
        "root": list(component.root),
        "canonical_root": list(component.canonical_root),
        "ceiling": component.ceiling,
        "node_budget": component.node_budget,
        "child_options": component.child_options,
        "actual_pops": component.actual_pops,
        "component_size": component.component_size,
        "queue_exhausted": component.queue_exhausted,
        "closure_verified": component.closure_verified,
        "canonical_fixed_points_verified": (
            component.canonical_fixed_points_verified
        ),
        "sorted_state_sha256": component.sorted_state_sha256,
    }


def build_scan_payload() -> dict[str, object]:
    component = recompute_component()
    records = tuple(
        _decision_record(state, solve_spherical(state))
        for state in component.states
    )
    support_histogram = Counter(record["support"] for record in records)
    if dict(support_histogram) != EXPECTED_SUPPORT_HISTOGRAM:
        raise CertificateError(
            f"support histogram changed: {dict(support_histogram)!r}"
        )
    verdict_histogram = Counter(record["verdict"] for record in records)
    if sum(verdict_histogram.values()) != component.component_size:
        raise CertificateError("not every component state received a verdict")

    return {
        "schema": SCHEMA,
        "component": _component_record(component),
        "support_histogram": {
            kind: support_histogram[kind]
            for kind in ("K4", "K4-e", "C4")
        },
        "verdict_histogram": dict(sorted(verdict_histogram.items())),
        "decision_sha256": _ordered_digest(records),
        "states": list(records),
    }


def _validate_scan_payload(payload: dict[str, object]) -> None:
    if payload.get("schema") != SCHEMA:
        raise CertificateError("schema mismatch")
    component = payload.get("component")
    states = payload.get("states")
    if not isinstance(component, dict) or not isinstance(states, list):
        raise CertificateError("malformed component payload")
    if len(states) != POP_CAP:
        raise CertificateError("state record count is not 1,000")
    if component.get("child_options") != CHILD_OPTIONS:
        raise CertificateError("recorded child options mismatch")
    if not component.get("canonical_fixed_points_verified"):
        raise CertificateError("canonical fixed-point audit is missing")
    words = tuple(tuple(record.get("words", ())) for record in states)
    if words != tuple(sorted(words)) or len(set(words)) != POP_CAP:
        raise CertificateError("state records are not unique and canonical")
    if any(canon(*state, cyclic=True) != state for state in words):
        raise CertificateError("state record is not a canon fixed point")
    if _ordered_digest(words) != component.get("sorted_state_sha256"):
        raise CertificateError("sorted state digest does not replay")
    if _ordered_digest(tuple(states)) != payload.get("decision_sha256"):
        raise CertificateError("decision digest does not replay")

    support_histogram = Counter(record.get("support") for record in states)
    if dict(support_histogram) != payload.get("support_histogram"):
        raise CertificateError("support histogram does not replay")
    verdict_histogram = Counter(record.get("verdict") for record in states)
    if dict(sorted(verdict_histogram.items())) != payload.get(
        "verdict_histogram"
    ):
        raise CertificateError("verdict histogram does not replay")

    for record in states:
        verdict = record.get("verdict")
        counters = record.get("counters")
        witness = record.get("witness")
        if not isinstance(counters, dict):
            raise CertificateError("state record has no counters")
        if verdict == "NOT_SPHERICAL":
            if record.get("disposition") != "NOT_THICKENABLE_EXACT_COMPLEX":
                raise CertificateError("negative disposition is not fail-closed")
            if witness is not None or not counters.get("exhaustive"):
                raise CertificateError("negative state is not exhaustive")
            for actual, budget in (
                ("schemes_considered", "scheme_budget"),
                ("phase_pairs_considered", "phase_pair_budget"),
                ("component_seed_attempts", "component_seed_budget"),
                (
                    "component_combinations_considered",
                    "component_combination_budget",
                ),
            ):
                if counters.get(actual) != counters.get(budget):
                    raise CertificateError("negative budget does not replay")
            if counters.get("witness_replay_failures") != 0:
                raise CertificateError("negative retained an unreplayed candidate")
        elif verdict == "SPHERICAL":
            if record.get("disposition") != "REGINA_REQUIRED":
                raise CertificateError("positive was not quarantined")
            if not isinstance(witness, dict):
                raise CertificateError("positive has no witness")
            if not (
                witness.get("euler_characteristic") == 2
                and witness.get("genus") == 0
                and witness.get("b_reversal_verified")
                and witness.get("rank_partition_verified")
                and witness.get("phase_equations_verified")
            ):
                raise CertificateError("positive witness replay flags failed")
        else:
            raise CertificateError("unsupported or unknown state verdict")


def verify_scan_payload(
    recorded: dict[str, object], recomputed: dict[str, object]
) -> None:
    if recorded.get("schema") != recomputed.get("schema"):
        raise CertificateError("schema mismatch")
    if recorded.get("component") != recomputed.get("component"):
        raise CertificateError("component metadata mismatch")
    if recorded.get("support_histogram") != recomputed.get(
        "support_histogram"
    ):
        raise CertificateError("support histogram mismatch")
    if recorded.get("verdict_histogram") != recomputed.get(
        "verdict_histogram"
    ):
        raise CertificateError("verdict histogram mismatch")
    if recorded.get("decision_sha256") != recomputed.get("decision_sha256"):
        raise CertificateError("decision digest mismatch")
    if recorded.get("states") != recomputed.get("states"):
        raise CertificateError("state records mismatch")
    _validate_scan_payload(recorded)
    _validate_scan_payload(recomputed)


def _implementation_record() -> dict[str, object]:
    return {
        "acmoves_dependencies": {
            "greedy_baseline": "greedy_baseline",
        },
        "canonicalization": {
            "qualified_name": (
                "experiments.equivalence_classes.lib.acmoves.canon"
            ),
            "source_binding": "acmoves",
        },
        "move_generator": {
            "qualified_name": (
                "experiments.equivalence_classes.lib.acmoves.children"
            ),
            "source_binding": "acmoves",
            "options": dict(CHILD_OPTIONS),
            "total_length_filter": CEILING,
        },
        "rank_solver": {
            "qualified_name": (
                "experiments.stable_ac.thickenable."
                "neuwirth_rank_solver.solve_spherical"
            ),
            "source_binding": "rank_solver",
        },
    }


def _require_clean_tracked_worktree() -> None:
    status = _git("status", "--porcelain", "--untracked-files=no")
    if status.strip():
        raise CertificateError(
            "production --output requires a clean tracked worktree"
        )


def _source_record(source_commit: str) -> dict[str, object]:
    return {
        "commit": source_commit,
        "bindings": {
            name: _source_binding(path, source_commit)
            for name, path in SOURCE_PATHS.items()
        },
    }


def build_certificate() -> dict[str, object]:
    _require_clean_tracked_worktree()
    source_commit = _head_commit()
    source_before = _source_record(source_commit)
    certificate = build_scan_payload()
    _require_clean_tracked_worktree()
    if _head_commit() != source_commit:
        raise CertificateError("HEAD changed while building the certificate")
    source_after = _source_record(source_commit)
    if source_after != source_before:
        raise CertificateError(
            "source bindings changed while building the certificate"
        )
    certificate["source"] = source_after
    certificate["implementations"] = _implementation_record()
    return certificate


def _authenticate_source(certificate: dict[str, object]) -> None:
    source = certificate.get("source")
    if not isinstance(source, dict):
        raise CertificateError("certificate has no source record")
    source_commit = source.get("commit")
    bindings = source.get("bindings")
    if not isinstance(source_commit, str) or not isinstance(bindings, dict):
        raise CertificateError("malformed source record")
    if set(bindings) != set(SOURCE_PATHS):
        raise CertificateError("source binding set mismatch")
    for name, expected_path in SOURCE_PATHS.items():
        binding = bindings[name]
        if not isinstance(binding, dict) or binding.get("path") != expected_path:
            raise CertificateError(f"source path mismatch: {name}")
        _authenticate_binding(binding, source_commit)
    if certificate.get("implementations") != _implementation_record():
        raise CertificateError("implementation identity/options mismatch")


def verify_certificate(certificate: dict[str, object]) -> None:
    _validate_scan_payload(certificate)
    _authenticate_source(certificate)
    recomputed = build_scan_payload()
    recorded_payload = {
        key: certificate[key]
        for key in (
            "schema",
            "component",
            "support_histogram",
            "verdict_histogram",
            "decision_sha256",
            "states",
        )
    }
    verify_scan_payload(recorded_payload, recomputed)


def write_certificate(output_path: Path) -> dict[str, object]:
    certificate = build_certificate()
    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(certificate, ensure_ascii=True, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    return certificate


def load_certificate(input_path: Path) -> dict[str, object]:
    try:
        value = json.loads(input_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CertificateError(f"cannot read certificate: {exc}") from exc
    if not isinstance(value, dict):
        raise CertificateError("certificate root is not an object")
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--output", type=Path)
    modes.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.output is not None:
        certificate = write_certificate(args.output)
        print(
            f"WROTE {len(certificate['states'])} exact decisions to "
            f"{args.output}"
        )
        return
    certificate = load_certificate(args.verify)
    verify_certificate(certificate)
    print(
        f"VERIFIED {len(certificate['states'])} exact decisions from "
        f"{args.verify}"
    )


if __name__ == "__main__":
    main()
