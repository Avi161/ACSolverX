"""Build and replay the finite AK(3) short-corridor certificate."""

import argparse
import json
from pathlib import Path

from experiments.equivalence_classes.lib.autcanon import check
from experiments.stable_ac.rank3_compression.corridors import (
    CorridorCensus,
    corridor_output,
    cyclic_orientations,
    enumerate_short_corridors,
    free_reduce,
    solve_isolator,
    substitute_z,
)


AK3 = ("xxxYYYY", "xyxYXY")
SCHEMA = "ak3-rank3-corridors-v1"
ROOT = Path(__file__).resolve().parents[3]
RESULT_PATH = ROOT / "results/stable_ac/theory/ak3_rank3_corridors.json"


def build_certificate(
    max_word_length: int = 4,
    max_template_length: int = 6,
) -> dict[str, object]:
    census = enumerate_short_corridors(
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
        errors.append(f"certificate pair is not AK(3): {data.get('pair')!r}")
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
    if bounds.get("minimum_z_occurrences") != 2:
        errors.append("minimum_z_occurrences must be exactly 2")

    accepted = data.get("accepted")
    if not isinstance(accepted, list):
        errors.append("accepted must be a list")
        accepted = []
    for index, raw_row in enumerate(accepted):
        if not isinstance(raw_row, dict):
            errors.append(f"accepted[{index}] is not an object")
            continue
        _verify_row(raw_row, max_word_length, max_template_length, index, errors)

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
            errors.append(
                f"aut_orbits[{orbit_index}] minimum does not match representative"
            )
        outputs = orbit.get("outputs")
        if not isinstance(outputs, list) or not outputs:
            errors.append(f"aut_orbits[{orbit_index}] has no outputs")
            continue
        for output_index, output_row in enumerate(outputs):
            if not isinstance(output_row, dict):
                errors.append(
                    f"aut_orbits[{orbit_index}].outputs[{output_index}] is not an object"
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

    recomputed = build_certificate(
        max_word_length=max_word_length,
        max_template_length=max_template_length,
    )
    if data != recomputed:
        differing = sorted(
            key
            for key in set(data) | set(recomputed)
            if data.get(key) != recomputed.get(key)
        )
        raise AssertionError(
            "certificate differs from complete replay in keys: "
            + ", ".join(differing)
        )


def _verify_row(
    row: dict[str, object],
    max_word_length: object,
    max_template_length: object,
    index: int,
    errors: list[str],
) -> None:
    where = f"accepted[{index}]"
    try:
        source_index = int(row["source_index"])
        eliminated = str(row["eliminated"])
        word = str(row["word"])
        template = str(row["template"])
        substituted = str(row["substituted"])
        expression = str(row["expression"])
        output = tuple(row["output"])
    except (KeyError, TypeError, ValueError) as exc:
        errors.append(f"{where} malformed: {exc}")
        return

    if source_index not in (0, 1):
        errors.append(f"{where} invalid source_index")
        return
    if eliminated not in "xy":
        errors.append(f"{where} invalid eliminated generator")
        return
    if not isinstance(max_word_length, int) or not (
        1 <= len(word) <= max_word_length
    ):
        errors.append(f"{where} word is outside bounds")
    if not isinstance(max_template_length, int) or not (
        2 <= len(template) <= max_template_length
    ):
        errors.append(f"{where} template is outside bounds")
    try:
        if free_reduce(word) != word:
            errors.append(f"{where} word is not freely reduced")
        if free_reduce(template) != template:
            errors.append(f"{where} template is not freely reduced")
    except ValueError as exc:
        errors.append(f"{where} invalid alphabet: {exc}")
        return
    if len(template) > 1 and template[0] == template[-1].swapcase():
        errors.append(f"{where} template is not cyclically reduced")
    if sum(letter.lower() == eliminated for letter in template) != 1:
        errors.append(f"{where} does not have exactly one eliminated letter")
    if template.count("z") + template.count("Z") < 2:
        errors.append(f"{where} has fewer than two z letters")

    got_substituted = substitute_z(template, word)
    if got_substituted != substituted:
        errors.append(f"{where} substituted word mismatch")
    orientations = cyclic_orientations(AK3[source_index])
    if substituted not in orientations:
        errors.append(f"{where} does not expand to its source relator")
    if row.get("source_orientation") != substituted:
        errors.append(f"{where} source_orientation mismatch")
    try:
        got_expression = solve_isolator(template, eliminated)
        got_output = corridor_output(
            AK3, source_index, word, template, eliminated
        )
    except ValueError as exc:
        errors.append(f"{where} replay rejected: {exc}")
        return
    if got_expression != expression:
        errors.append(f"{where} isolator expression mismatch")
    if got_output != output:
        errors.append(f"{where} output mismatch")


def _certificate_from_census(census: CorridorCensus) -> dict[str, object]:
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
        if orbit["minimum_total"] != record.minimum_total:
            raise AssertionError("one Aut representative has inconsistent minima")
        orbit["outputs"].append(
            {"output": list(record.output), "phi": record.phi}
        )
    aut_orbits = [grouped[key] for key in sorted(grouped)]
    minimum = census.minimum_output_floor
    return {
        "schema": SCHEMA,
        "claim": "finite decision of the stated short-corridor lemma only",
        "pair": list(census.pair),
        "bounds": {
            "max_word_length": census.max_word_length,
            "max_template_length": census.max_template_length,
            "minimum_z_occurrences": census.minimum_z_occurrences,
        },
        "enumerated_templates": census.enumerated_templates,
        "accepted_count": census.accepted_count,
        "trace_sha256": census.trace_sha256,
        "accepted": [row.to_json() for row in census.accepted],
        "aut_orbits": aut_orbits,
        "minimum_output_floor": minimum,
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
            f"{data['enumerated_templates']} templates, "
            f"{data['accepted_count']} corridors, "
            f"minimum floor {data['minimum_output_floor']}, "
            f"lemma {data['candidate_lemma']}"
        )
        return
    data = build_certificate()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print(
        "CERTIFICATE WRITTEN: "
        f"{data['enumerated_templates']} templates, "
        f"{data['accepted_count']} corridors, "
        f"minimum floor {data['minimum_output_floor']}, "
        f"lemma {data['candidate_lemma']} -> {args.output}"
    )


if __name__ == "__main__":
    main()
