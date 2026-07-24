"""Build and replay the immediate AK(3) two-stabilization certificate."""

import argparse
import json
from pathlib import Path

from experiments.equivalence_classes.lib.acmoves import canon
from experiments.equivalence_classes.lib.autcanon import check
from experiments.stable_ac.rank3_compression.two_stabilization import (
    TwoStabilizationCensus,
    derive_rank3,
    enumerate_immediate_two_stabilizations,
    remove_second,
    solve_isolator,
    substitute_new,
)


AK3 = ("xxxYYYY", "xyxYXY")
SCHEMA = "ak3-two-stabilization-v1"
ROOT = Path(__file__).resolve().parents[3]
RESULT_PATH = ROOT / "results/stable_ac/theory/ak3_two_stabilization.json"


def build_certificate(
    max_word_length: int = 2,
    max_template_length: int = 6,
) -> dict[str, object]:
    census = enumerate_immediate_two_stabilizations(
        AK3,
        max_word_length=max_word_length,
        max_template_length=max_template_length,
    )
    return _certificate_from_census(census)


def verify_certificate(data: dict[str, object]) -> None:
    errors: list[str] = []
    if data.get("schema") != SCHEMA:
        errors.append(f"wrong schema: {data.get('schema')!r}")
    if data.get("pair") != list(AK3):
        errors.append("certificate pair is not AK(3)")
    bounds = data.get("bounds")
    if not isinstance(bounds, dict):
        errors.append("bounds must be an object")
        bounds = {}
    max_word_length = bounds.get("max_word_length")
    max_template_length = bounds.get("max_template_length")
    if not isinstance(max_word_length, int) or max_word_length < 1:
        errors.append("invalid max_word_length")
    if not isinstance(max_template_length, int) or max_template_length < 2:
        errors.append("invalid max_template_length")

    witnesses = data.get("output_witnesses")
    if not isinstance(witnesses, list):
        errors.append("output_witnesses must be a list")
        witnesses = []
    for index, row in enumerate(witnesses):
        if not isinstance(row, dict):
            errors.append(f"output_witnesses[{index}] is not an object")
            continue
        _verify_output_row(row, index, errors)

    aut_orbits = data.get("aut_orbits")
    if not isinstance(aut_orbits, list):
        errors.append("aut_orbits must be a list")
        aut_orbits = []
    for orbit_index, orbit in enumerate(aut_orbits):
        if not isinstance(orbit, dict):
            errors.append(f"aut_orbits[{orbit_index}] is not an object")
            continue
        representative = tuple(orbit.get("representative", ()))
        minimum_total = orbit.get("minimum_total")
        if minimum_total != sum(len(word) for word in representative):
            errors.append(f"aut_orbits[{orbit_index}] minimum mismatch")
        outputs = orbit.get("outputs")
        if not isinstance(outputs, list) or not outputs:
            errors.append(f"aut_orbits[{orbit_index}] has no outputs")
            continue
        for output_index, output_row in enumerate(outputs):
            if not isinstance(output_row, dict):
                errors.append(
                    f"aut_orbits[{orbit_index}].outputs[{output_index}] "
                    "is not an object"
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
                    f"aut_orbits[{orbit_index}].outputs[{output_index}] "
                    "has an invalid Aut witness"
                )

    if errors:
        raise AssertionError("\n".join(errors))

    expected = build_certificate(
        max_word_length=max_word_length,
        max_template_length=max_template_length,
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


def _verify_output_row(
    row: dict[str, object],
    index: int,
    errors: list[str],
) -> None:
    where = f"output_witnesses[{index}]"
    try:
        word_z = str(row["word_z"])
        word_t = str(row["word_t"])
        template = str(row["template"])
        expanded = str(row["expanded"])
        expression_y = str(row["expression_y"])
        rank3 = tuple(row["rank3"])
        second_index = int(row["second_isolator_index"])
        expression_x = str(row["expression_x"])
        output = tuple(row["output"])
    except (KeyError, TypeError, ValueError) as exc:
        errors.append(f"{where} malformed: {exc}")
        return
    try:
        got_expanded = substitute_new(template, word_z, word_t)
        got_expression_y = solve_isolator(template, "y")
        got_rank3 = derive_rank3(
            AK3, 1, word_z, word_t, template, eliminated="y"
        )
        got_expression_x = solve_isolator(got_rank3[second_index], "x")
        got_output = remove_second(got_rank3, second_index, "x")
    except (IndexError, ValueError) as exc:
        errors.append(f"{where} replay rejected: {exc}")
        return
    if got_expanded != expanded:
        errors.append(f"{where} expanded source mismatch")
    if got_expression_y != expression_y:
        errors.append(f"{where} first expression mismatch")
    if got_rank3 != rank3:
        errors.append(f"{where} rank3 mismatch")
    if got_expression_x != expression_x:
        errors.append(f"{where} second expression mismatch")
    if got_output != output:
        errors.append(f"{where} output mismatch")


def _certificate_from_census(
    census: TwoStabilizationCensus,
) -> dict[str, object]:
    first_by_output = {}
    for row in census.certificates:
        first_by_output.setdefault(row.output, row)
    output_witnesses = [
        first_by_output[output].to_json() for output in sorted(first_by_output)
    ]

    grouped: dict[tuple[str, str], dict[str, object]] = {}
    floor_by_output: dict[tuple[str, str], int] = {}
    for record in census.aut_records:
        floor_by_output[record.output] = record.minimum_total
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
    aut_orbits = [grouped[key] for key in sorted(grouped)]
    minimum = census.minimum_output_floor
    minimum_outputs = [
        row
        for row in output_witnesses
        if floor_by_output[canon(*tuple(row["output"]))] == minimum
    ]
    return {
        "schema": SCHEMA,
        "claim": "finite decision of the immediate two-stabilization lemma only",
        "pair": list(census.pair),
        "bounds": {
            "max_word_length": census.max_word_length,
            "max_template_length": census.max_template_length,
        },
        "defining_word_count": census.defining_word_count,
        "defining_word_pair_count": census.defining_word_count**2,
        "structural_template_count": census.structural_template_count,
        "tested_cases": census.tested_cases,
        "accepted_source_identities": census.accepted_source_identities,
        "distinct_rank3_count": census.distinct_rank3_count,
        "triangular_certificate_count": census.triangular_certificate_count,
        "distinct_raw_output_count": census.distinct_raw_output_count,
        "canonical_output_count": len(census.aut_records),
        "trace_sha256": census.trace_sha256,
        "floor_distribution": {
            str(floor): count
            for floor, count in sorted(census.floor_distribution.items())
        },
        "minimum_output_floor": minimum,
        "output_witnesses": output_witnesses,
        "aut_orbits": aut_orbits,
        "minimum_outputs": minimum_outputs,
        "candidate_lemma": (
            "PROVED" if minimum is not None and minimum <= 12 else "REFUTED"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--output", type=Path, default=RESULT_PATH)
    args = parser.parse_args()
    if args.verify:
        with args.output.open() as handle:
            data = json.load(handle)
        verify_certificate(data)
        print(
            "CERTIFICATE VERIFIES: "
            f"{data['defining_word_pair_count']} word pairs, "
            f"{data['distinct_raw_output_count']} outputs, "
            f"minimum {data['minimum_output_floor']}, "
            f"lemma {data['candidate_lemma']}"
        )
        return
    data = build_certificate()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print(
        "CERTIFICATE WRITTEN: "
        f"{data['defining_word_pair_count']} word pairs, "
        f"{data['distinct_raw_output_count']} outputs, "
        f"minimum {data['minimum_output_floor']}, "
        f"lemma {data['candidate_lemma']} -> {args.output}"
    )


if __name__ == "__main__":
    main()
