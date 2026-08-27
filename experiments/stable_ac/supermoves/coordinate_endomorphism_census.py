"""Census a fixed quotient-isolator coordinate action on rank-two data."""

from __future__ import annotations

import argparse
import csv
import json
from hashlib import sha256
from pathlib import Path

from experiments.stable_ac.supermoves.aca124_acm_census import (
    OrbitKey,
    _load_orbit_key,
)
from experiments.stable_ac.supermoves.certified_acm import cyclic_reduce, inverse
from experiments.stable_ac.supermoves.quotient_isolator import (
    coordinate_endomorphism_move,
    specialize_old_generators_to_identity,
)


def build_census(
    rows: list[dict[str, str]],
    orbit_key: OrbitKey,
    *,
    generator: str,
    image: str,
    triviality_provenance: dict[str, str] | None = None,
) -> dict[str, object]:
    x_image = image if generator == "x" else "x"
    y_image = image if generator == "y" else "y"
    commutator_image = cyclic_reduce(
        x_image + y_image + inverse(x_image) + inverse(y_image)
    )
    records: list[dict[str, object]] = []
    for row in rows:
        source = (row["r1"], row["r2"])
        move = coordinate_endomorphism_move(source, generator, image)
        old_generators = tuple(sorted({letter.lower() for word in source for letter in word}))
        specialized_isolator = specialize_old_generators_to_identity(
            move.quotient_isolator, old_generators
        )
        specialized_difference = specialize_old_generators_to_identity(
            move.quotient_difference, old_generators
        )
        expected_stabilizer = (
            move.fresh_generator
            if move.exponent == 1
            else move.fresh_generator.upper()
        )
        if specialized_isolator != expected_stabilizer or specialized_difference:
            raise AssertionError(f"quotient identity failed for {row['name']}")

        source_floor, source_rep = orbit_key(source)
        target_floor, target_rep = orbit_key(move.target)
        records.append(
            {
                "name": row["name"],
                "source": list(source),
                "target": list(move.target),
                "source_floor": source_floor,
                "target_floor": target_floor,
                "floor_delta": target_floor - source_floor,
                "source_representative": list(source_rep),
                "target_representative": list(target_rep),
                "nonautomorphic": source_rep != target_rep,
                "quotient_isolator": move.quotient_isolator,
                "quotient_difference": move.quotient_difference,
                "quotient_specialization_verified": True,
                "quotient_identity_conditionally_established": (
                    triviality_provenance is not None
                ),
            }
        )

    payload: dict[str, object] = {
        "schema": "aca124-coordinate-endomorphism-v1",
        "move": {
            "generator": generator,
            "image": image,
            "mechanism": "quotient-isolator elimination",
            "atomic_stable_ac_cost": (
                "witness-dependent normal-area replay plus Lemma 11; "
                "no effective input-visible bound supplied"
            ),
            "nonautomorphism_certificate": {
                "cyclically_reduced_commutator_image": commutator_image,
                "commutator_image_length": len(commutator_image),
                "basis_commutator_length": 4,
                "verified": len(commutator_image) != 4,
            },
        },
        "source_triviality_provenance": triviality_provenance,
        "summary": {
            "class_count": len(records),
            "quotient_specializations_verified": len(records),
            "quotient_identities_conditionally_established": (
                len(records) if triviality_provenance is not None else 0
            ),
            "nonautomorphic_targets": sum(row["nonautomorphic"] for row in records),
            "automorphic_targets": sum(not row["nonautomorphic"] for row in records),
            "strict_floor_descents": sum(row["floor_delta"] < 0 for row in records),
            "minimum_floor_delta": min(row["floor_delta"] for row in records),
            "maximum_floor_delta": max(row["floor_delta"] for row in records),
        },
        "records": records,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["payload_sha256"] = sha256(encoded.encode()).hexdigest()
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--checker-root", type=Path, required=True)
    parser.add_argument("--generator", choices=("x", "y"), required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--trivial-provenance-file", type=Path, required=True)
    args = parser.parse_args()

    with args.data.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    payload = build_census(
        rows,
        _load_orbit_key(args.checker_root),
        generator=args.generator,
        image=args.image,
        triviality_provenance=json.loads(args.trivial_provenance_file.read_text()),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
