"""Certificate for short hidden corridors across a complete primitive basis ball."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
from typing import Callable

from experiments.equivalence_classes.lib.acmoves import canon
from experiments.equivalence_classes.lib.autcanon import check
from experiments.stable_ac.rank3_compression.corridors import (
    CorridorCensus,
    enumerate_short_corridors,
)
from experiments.stable_ac.rank3_compression.primitive_bases import (
    BasisClass,
    NielsenMove,
    apply_basis,
    apply_nielsen,
    primitive_basis_classes,
    replay_nielsen,
    signed_pair_key,
)


AK3 = ("xxxYYYY", "xyxYXY")
SCHEMA = "ak3-primitive-basis-corridors-v1"
ROOT = Path(__file__).resolve().parents[3]
RESULT_PATH = (
    ROOT / "results/stable_ac/theory/ak3_primitive_basis_corridors.json"
)
Progress = Callable[[int, int, tuple[str, str]], None]


def build_certificate(
    max_basis_total: int = 4,
    max_word_length: int = 4,
    max_template_length: int = 6,
    progress: Progress | None = None,
) -> dict[str, object]:
    classes = primitive_basis_classes(AK3, max_basis_total)
    basis_rows = sorted(
        (
            member.to_json(cls.key)
            for cls in classes
            for member in cls.members
        ),
        key=lambda row: tuple(row["basis"]),
    )
    compact_rows = json.dumps(
        basis_rows, sort_keys=True, separators=(",", ":")
    ).encode()
    partition_digest = sha256(compact_rows).hexdigest()

    class_rows: list[dict[str, object]] = []
    for index, cls in enumerate(classes, 1):
        if progress is not None:
            progress(index, len(classes), cls.key)
        census = enumerate_short_corridors(
            cls.key,
            max_word_length=max_word_length,
            max_template_length=max_template_length,
        )
        class_rows.append(_class_summary(cls, census))

    minima = [
        row["minimum_output_floor"]
        for row in class_rows
        if row["minimum_output_floor"] is not None
    ]
    global_minimum = min(minima) if minima else None
    return {
        "schema": SCHEMA,
        "claim": "finite decision of the stated primitive-basis lemma only",
        "pair": list(AK3),
        "basis_bound": max_basis_total,
        "corridor_bounds": {
            "max_word_length": max_word_length,
            "max_template_length": max_template_length,
            "minimum_z_occurrences": 2,
        },
        "basis_count": len(basis_rows),
        "class_count": len(classes),
        "class_sizes": sorted(len(cls.members) for cls in classes),
        "partition_sha256": partition_digest,
        "bases": basis_rows,
        "classes": class_rows,
        "global_minimum_output_floor": global_minimum,
        "candidate_lemma": (
            "PROVED"
            if global_minimum is not None and global_minimum <= 12
            else "REFUTED"
        ),
    }


def verify_certificate(
    data: dict[str, object],
    progress: Progress | None = None,
) -> None:
    errors: list[str] = []
    if data.get("schema") != SCHEMA:
        errors.append(f"wrong schema: {data.get('schema')!r}")
    if data.get("pair") != list(AK3):
        errors.append("certificate pair is not AK(3)")
    basis_bound = data.get("basis_bound")
    corridor_bounds = data.get("corridor_bounds")
    if not isinstance(basis_bound, int) or basis_bound < 2:
        errors.append("invalid basis_bound")
    if not isinstance(corridor_bounds, dict):
        errors.append("corridor_bounds must be an object")
        corridor_bounds = {}
    max_word_length = corridor_bounds.get("max_word_length")
    max_template_length = corridor_bounds.get("max_template_length")
    if not isinstance(max_word_length, int) or max_word_length < 1:
        errors.append("invalid max_word_length")
    if not isinstance(max_template_length, int) or max_template_length < 2:
        errors.append("invalid max_template_length")
    if corridor_bounds.get("minimum_z_occurrences") != 2:
        errors.append("minimum_z_occurrences must be 2")

    basis_rows = data.get("bases")
    if not isinstance(basis_rows, list):
        errors.append("bases must be a list")
        basis_rows = []
    for index, row in enumerate(basis_rows):
        if not isinstance(row, dict):
            errors.append(f"bases[{index}] is not an object")
            continue
        _verify_basis_row(row, index, errors)
    compact_rows = json.dumps(
        basis_rows, sort_keys=True, separators=(",", ":")
    ).encode()
    if sha256(compact_rows).hexdigest() != data.get("partition_sha256"):
        errors.append("partition_sha256 mismatch")

    classes = data.get("classes")
    if not isinstance(classes, list):
        errors.append("classes must be a list")
        classes = []
    for class_index, class_row in enumerate(classes):
        if not isinstance(class_row, dict):
            errors.append(f"classes[{class_index}] is not an object")
            continue
        _verify_aut_rows(class_row, class_index, errors)

    if errors:
        raise AssertionError("\n".join(errors))

    expected = build_certificate(
        max_basis_total=basis_bound,
        max_word_length=max_word_length,
        max_template_length=max_template_length,
        progress=progress,
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


def _verify_basis_row(
    row: dict[str, object],
    index: int,
    errors: list[str],
) -> None:
    where = f"bases[{index}]"
    try:
        basis = tuple(row["basis"])
        moves = tuple(
            NielsenMove.from_json(move) for move in row["moves"]
        )
        transformed_pair = tuple(row["transformed_pair"])
        class_key = tuple(row["class_key"])
    except (KeyError, TypeError, ValueError) as exc:
        errors.append(f"{where} malformed: {exc}")
        return
    if len(basis) != 2:
        errors.append(f"{where} basis does not have two words")
        return
    current = basis
    try:
        for move_index, move in enumerate(moves):
            child = apply_nielsen(current, move)
            if sum(map(len, child)) >= sum(map(len, current)):
                errors.append(
                    f"{where}.moves[{move_index}] is not strictly decreasing"
                )
            current = child
    except ValueError as exc:
        errors.append(f"{where} Nielsen replay rejected: {exc}")
        return
    replayed = replay_nielsen(basis, moves)
    if replayed != current:
        errors.append(f"{where} replay implementations disagree")
    if not _is_signed_standard(current):
        errors.append(f"{where} witness does not end at a signed basis")
    try:
        got_pair = apply_basis(AK3, basis)
        got_key = signed_pair_key(got_pair)
    except ValueError as exc:
        errors.append(f"{where} basis application rejected: {exc}")
        return
    if got_pair != transformed_pair:
        errors.append(f"{where} transformed_pair mismatch")
    if got_key != class_key:
        errors.append(f"{where} class_key mismatch")


def _verify_aut_rows(
    class_row: dict[str, object],
    class_index: int,
    errors: list[str],
) -> None:
    output_orbits = class_row.get("output_orbits")
    if not isinstance(output_orbits, list):
        errors.append(f"classes[{class_index}].output_orbits is not a list")
        return
    for orbit_index, orbit in enumerate(output_orbits):
        if not isinstance(orbit, dict):
            errors.append(
                f"classes[{class_index}].output_orbits[{orbit_index}] "
                "is not an object"
            )
            continue
        representative = tuple(orbit.get("representative", ()))
        if orbit.get("minimum_total") != sum(map(len, representative)):
            errors.append(
                f"classes[{class_index}].output_orbits[{orbit_index}] "
                "minimum mismatch"
            )
        outputs = orbit.get("outputs")
        if not isinstance(outputs, list) or not outputs:
            errors.append(
                f"classes[{class_index}].output_orbits[{orbit_index}] "
                "has no outputs"
            )
            continue
        for output_index, output_row in enumerate(outputs):
            if not isinstance(output_row, dict):
                errors.append(
                    f"classes[{class_index}].output_orbits[{orbit_index}]"
                    f".outputs[{output_index}] is not an object"
                )
                continue
            output = tuple(output_row.get("output", ()))
            phi = output_row.get("phi")
            if (
                len(output) != 2
                or not isinstance(phi, dict)
                or not check(output, representative, phi)
            ):
                errors.append(
                    f"classes[{class_index}].output_orbits[{orbit_index}]"
                    f".outputs[{output_index}] invalid Aut witness"
                )


def _class_summary(
    cls: BasisClass,
    census: CorridorCensus,
) -> dict[str, object]:
    grouped: dict[tuple[str, str], dict[str, object]] = {}
    for record in census.aut_records:
        orbit = grouped.setdefault(
            record.representative,
            {
                "minimum_total": record.minimum_total,
                "representative": list(record.representative),
                "outputs": [],
            },
        )
        orbit["outputs"].append(
            {"output": list(record.output), "phi": record.phi}
        )
    output_orbits = [grouped[key] for key in sorted(grouped)]
    minimum = census.minimum_output_floor
    minimum_outputs = {
        record.output
        for record in census.aut_records
        if record.minimum_total == minimum
    }
    minimum_corridors = [
        row.to_json()
        for row in census.accepted
        if canon(*row.output) in minimum_outputs
    ]
    return {
        "key": list(cls.key),
        "member_count": len(cls.members),
        "enumerated_templates": census.enumerated_templates,
        "accepted_count": census.accepted_count,
        "trace_sha256": census.trace_sha256,
        "minimum_output_floor": minimum,
        "output_orbits": output_orbits,
        "minimum_corridors": minimum_corridors,
    }


def _is_signed_standard(pair: tuple[str, str]) -> bool:
    return (
        len(pair) == 2
        and len(pair[0]) == len(pair[1]) == 1
        and pair[0].lower() != pair[1].lower()
    )


def _print_progress(
    index: int,
    total: int,
    key: tuple[str, str],
) -> None:
    print(f"CLASS {index}/{total}: {key[0]} | {key[1]}", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--output", type=Path, default=RESULT_PATH)
    args = parser.parse_args()
    if args.verify:
        with args.output.open() as handle:
            data = json.load(handle)
        verify_certificate(data, progress=_print_progress)
        print(
            "CERTIFICATE VERIFIES: "
            f"{data['basis_count']} bases, {data['class_count']} classes, "
            f"minimum {data['global_minimum_output_floor']}, "
            f"lemma {data['candidate_lemma']}"
        )
        return
    data = build_certificate(progress=_print_progress)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print(
        "CERTIFICATE WRITTEN: "
        f"{data['basis_count']} bases, {data['class_count']} classes, "
        f"minimum {data['global_minimum_output_floor']}, "
        f"lemma {data['candidate_lemma']} -> {args.output}"
    )


if __name__ == "__main__":
    main()
