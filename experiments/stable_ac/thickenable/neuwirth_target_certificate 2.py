"""Build and replay the independent AK(3) Neuwirth census certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Mapping

from experiments.stable_ac.thickenable.neuwirth_dart_audit import audit_trace
from experiments.stable_ac.thickenable.neuwirth_permutation_certificate import (
    enumerate_trace,
)

SCHEMA = "ak3-neuwirth-census-v1"
COMPOSITION = "right-to-left: PQ(e)=P(Q(e))"
TARGETS = {
    "ak3": ("xxxYYYY", "xyxYXY"),
    "orbit_2": ("YYXXyx", "YYYxyXX"),
}
ROOT = Path(__file__).resolve().parents[3]
MODULE_PATHS = {
    "direct_module_sha256": Path(
        "experiments/stable_ac/thickenable/neuwirth_permutation_certificate.py"
    ),
    "audit_module_sha256": Path(
        "experiments/stable_ac/thickenable/neuwirth_dart_audit.py"
    ),
    "driver_module_sha256": Path(
        "experiments/stable_ac/thickenable/neuwirth_target_certificate.py"
    ),
}


def _module_sha256(module_file: str | Path) -> str:
    return hashlib.sha256(Path(module_file).read_bytes()).hexdigest()


def _accepting_orders_json(accepting_orders: tuple) -> list[dict[str, object]]:
    encoded = []
    for descriptor, trace_item in accepting_orders:
        encoded.append(
            {
                "order": [
                    [generator, list(occurrences)]
                    for generator, occurrences in descriptor
                ],
                "link_components": trace_item[0],
                "faces": trace_item[1],
                "defect": trace_item[2],
                "boundary_orbits_BC": trace_item[3],
                "boundary_orbits_CB": trace_item[4],
            }
        )
    return encoded


def _verdict(
    *,
    link_components: set[int],
    accepting_orders: tuple,
    trusted_balanced_trivial: bool,
) -> str:
    if link_components != {1}:
        return "OUT_OF_SCOPE_DISCONNECTED_LINK"
    if not accepting_orders:
        return "NOT_THICKENABLE_EXACT_COMPLEX"
    if not trusted_balanced_trivial:
        return "EULER_ACCEPTING_UNTRUSTED"
    if any(trace_item[3] != 1 for _, trace_item in accepting_orders):
        return "AUDIT_CONTRADICTION"
    return "REGINA_REQUIRED"


def build_certificate(
    targets: Mapping[str, tuple[str, ...]],
    *,
    source_commit: str,
    trusted_balanced_trivial_targets: set[str] | frozenset[str] = frozenset(),
) -> dict[str, object]:
    """Run both complete enumerators and return their compact certificate."""
    if not source_commit:
        raise ValueError("source_commit must be nonempty")
    trusted_targets = frozenset(trusted_balanced_trivial_targets)
    unknown_trusted_targets = trusted_targets.difference(targets)
    if unknown_trusted_targets:
        raise ValueError(
            "trusted balanced-trivial targets are absent from the census: "
            f"{sorted(unknown_trusted_targets)!r}"
        )

    target_entries: dict[str, object] = {}
    for name, words in targets.items():
        exact_words = tuple(words)
        direct = enumerate_trace(exact_words)
        audit = audit_trace(exact_words)

        if direct.trace != audit.trace:
            raise AssertionError(f"ordered trace mismatch for target {name!r}")
        if direct.trace_sha256 != audit.trace_sha256:
            raise AssertionError(f"trace digest mismatch for target {name!r}")
        if direct.expected_cases != direct.enumerated_cases:
            raise AssertionError(f"incomplete direct census for target {name!r}")
        if audit.expected_cases != audit.enumerated_cases:
            raise AssertionError(f"incomplete audit census for target {name!r}")

        target_entries[name] = {
            "words": list(exact_words),
            "degrees": dict(direct.degrees),
            "expected_cases": direct.expected_cases,
            "enumerated_cases": direct.enumerated_cases,
            "link_components": sorted(direct.link_components),
            "defect_histogram": {
                str(defect): count
                for defect, count in sorted(direct.defect_histogram.items())
            },
            "minimum_genus": direct.minimum_genus,
            "accepting_orders": _accepting_orders_json(direct.accepting_orders),
            "direct_trace_sha256": direct.trace_sha256,
            "audit_trace_sha256": audit.trace_sha256,
            "verdict": _verdict(
                link_components=direct.link_components,
                accepting_orders=direct.accepting_orders,
                trusted_balanced_trivial=name in trusted_targets,
            ),
        }

    return {
        "schema": SCHEMA,
        "composition": COMPOSITION,
        "targets": target_entries,
        "source_commit": source_commit,
        **{
            field: _module_sha256(ROOT / relative_path)
            for field, relative_path in MODULE_PATHS.items()
        },
    }


def _resolve_source_commit(source_commit: object) -> str:
    if (
        not isinstance(source_commit, str)
        or re.fullmatch(r"[0-9a-f]{40}", source_commit) is None
    ):
        raise ValueError("certificate source commit must be a full Git commit")
    try:
        resolved = subprocess.run(
            ["git", "rev-parse", "--verify", f"{source_commit}^{{commit}}"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except subprocess.CalledProcessError as error:
        raise ValueError("certificate source commit does not resolve") from error
    if resolved != source_commit:
        raise ValueError("certificate source commit did not resolve exactly")
    return resolved


def _git_blob_sha256(source_commit: str, relative_path: Path) -> str:
    try:
        content = subprocess.run(
            ["git", "show", f"{source_commit}:{relative_path.as_posix()}"],
            cwd=ROOT,
            check=True,
            capture_output=True,
        ).stdout
    except subprocess.CalledProcessError as error:
        raise ValueError(
            f"source commit does not contain {relative_path.as_posix()}"
        ) from error
    return hashlib.sha256(content).hexdigest()


def _authenticate_source_modules(
    certificate: Mapping[str, object],
    source_commit: str,
) -> None:
    for field, relative_path in MODULE_PATHS.items():
        recorded_hash = certificate.get(field)
        if not isinstance(recorded_hash, str):
            raise ValueError(f"certificate has no {field}")
        committed_hash = _git_blob_sha256(source_commit, relative_path)
        if recorded_hash != committed_hash:
            raise AssertionError(f"recorded {field} hash does not match source commit")
        current_hash = _module_sha256(ROOT / relative_path)
        if current_hash != committed_hash:
            raise AssertionError(f"current {field} hash does not match source commit")


def verify_certificate(certificate: Mapping[str, object]) -> bool:
    """Recompute both ordered traces and compare the complete certificate."""
    if certificate.get("schema") != SCHEMA:
        raise ValueError("unsupported certificate schema")
    if certificate.get("composition") != COMPOSITION:
        raise ValueError("unsupported permutation composition convention")
    source_commit = _resolve_source_commit(certificate.get("source_commit"))
    encoded_targets = certificate.get("targets")
    if not isinstance(encoded_targets, Mapping):
        raise ValueError("certificate targets must be an object")

    targets: dict[str, tuple[str, ...]] = {}
    for name, entry in encoded_targets.items():
        if not isinstance(name, str) or not isinstance(entry, Mapping):
            raise ValueError("invalid target entry")
        words = entry.get("words")
        if not isinstance(words, list) or not all(
            isinstance(word, str) for word in words
        ):
            raise ValueError(f"invalid exact words for target {name!r}")
        targets[name] = tuple(words)
    if targets != TARGETS:
        raise ValueError("certificate does not contain the exact canonical targets")

    _authenticate_source_modules(certificate, source_commit)
    recomputed = build_certificate(
        targets,
        source_commit=source_commit,
        trusted_balanced_trivial_targets=frozenset(TARGETS),
    )
    if dict(certificate) != recomputed:
        raise AssertionError("certificate replay mismatch")
    return True


def _clean_source_commit() -> str:
    status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if status:
        raise RuntimeError("refusing to generate from a dirty tracked worktree")
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--output", type=Path)
    action.add_argument("--verify", type=Path)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if args.output is not None:
        certificate = build_certificate(
            TARGETS,
            source_commit=_clean_source_commit(),
            trusted_balanced_trivial_targets=frozenset(TARGETS),
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"wrote {args.output}")
        return

    certificate = json.loads(args.verify.read_text(encoding="utf-8"))
    verify_certificate(certificate)
    print(f"verified {args.verify}")


if __name__ == "__main__":
    main()
