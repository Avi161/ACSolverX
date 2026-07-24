"""Build and replay the independent AK(3) Neuwirth census certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
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


def _module_sha256(module_file: str) -> str:
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


def _verdict(accepting_orders: tuple) -> str:
    if not accepting_orders:
        return "NOT_THICKENABLE_EXACT_COMPLEX"
    if any(trace_item[3] == 1 for _, trace_item in accepting_orders):
        return "REGINA_REQUIRED"
    return "AUDIT_CONTRADICTION"


def build_certificate(
    targets: Mapping[str, tuple[str, ...]],
    *,
    source_commit: str,
) -> dict[str, object]:
    """Run both complete enumerators and return their compact certificate."""
    if not source_commit:
        raise ValueError("source_commit must be nonempty")

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
            "defect_histogram": {
                str(defect): count
                for defect, count in sorted(direct.defect_histogram.items())
            },
            "minimum_genus": direct.minimum_genus,
            "accepting_orders": _accepting_orders_json(direct.accepting_orders),
            "direct_trace_sha256": direct.trace_sha256,
            "audit_trace_sha256": audit.trace_sha256,
            "verdict": _verdict(direct.accepting_orders),
        }

    direct_module = Path(__file__).with_name("neuwirth_permutation_certificate.py")
    audit_module = Path(__file__).with_name("neuwirth_dart_audit.py")
    return {
        "schema": SCHEMA,
        "composition": COMPOSITION,
        "targets": target_entries,
        "source_commit": source_commit,
        "direct_module_sha256": _module_sha256(str(direct_module)),
        "audit_module_sha256": _module_sha256(str(audit_module)),
    }


def verify_certificate(certificate: Mapping[str, object]) -> bool:
    """Recompute both ordered traces and compare the complete certificate."""
    if certificate.get("schema") != SCHEMA:
        raise ValueError("unsupported certificate schema")
    if certificate.get("composition") != COMPOSITION:
        raise ValueError("unsupported permutation composition convention")
    source_commit = certificate.get("source_commit")
    if not isinstance(source_commit, str) or not source_commit:
        raise ValueError("certificate has no source commit")
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

    recomputed = build_certificate(targets, source_commit=source_commit)
    if dict(certificate) != recomputed:
        raise AssertionError("certificate replay mismatch")
    return True


def _clean_source_commit() -> str:
    root = Path(__file__).resolve().parents[3]
    status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if status:
        raise RuntimeError("refusing to generate from a dirty tracked worktree")
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
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
