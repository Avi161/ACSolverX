"""Build and independently replay the bounded AK(3) one-edge certificate."""

import argparse
import json
from pathlib import Path

from experiments.equivalence_classes.lib.acmoves import canon
from experiments.equivalence_classes.lib.autcanon import check
from experiments.stable_ac.rank3_compression.one_edge import (
    OneEdgeCensus,
    OneEdgeMove,
    canonical_rank3,
    enumerate_one_edge_compressions,
)
from experiments.stable_ac.rank3_compression import (
    two_stabilization as two_stage,
)


AK3 = ("xxxYYYY", "xyxYXY")
SCHEMA = "ak3-one-edge-v1"
ROOT = Path(__file__).resolve().parents[3]
RESULT_PATH = ROOT / "results/stable_ac/theory/ak3_one_edge.json"


def build_certificate(
    max_word_length: int = 2,
    max_template_length: int = 6,
) -> dict[str, object]:
    census = enumerate_one_edge_compressions(
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

    sources = data.get("eligible_sources")
    if not isinstance(sources, list):
        errors.append("eligible_sources must be a list")
        sources = []
    replayed_sources: list[tuple[str, str, str] | None] = []
    for source_index, row in enumerate(sources):
        if not isinstance(row, dict):
            errors.append(f"eligible_sources[{source_index}] is not an object")
            replayed_sources.append(None)
            continue
        replayed_sources.append(
            _verify_source_row(row, source_index, errors)
        )

    witnesses = data.get("output_witnesses")
    if not isinstance(witnesses, list):
        errors.append("output_witnesses must be a list")
        witnesses = []
    for witness_index, row in enumerate(witnesses):
        if not isinstance(row, dict):
            errors.append(
                f"output_witnesses[{witness_index}] is not an object"
            )
            continue
        _verify_output_row(
            row,
            witness_index,
            replayed_sources,
            errors,
        )

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


def _verify_source_row(
    row: dict[str, object],
    index: int,
    errors: list[str],
) -> tuple[str, str, str] | None:
    where = f"eligible_sources[{index}]"
    try:
        word_z = str(row["word_z"])
        word_t = str(row["word_t"])
        template = str(row["template"])
        raw_rank3 = tuple(row["raw_rank3"])
        rank3 = tuple(row["rank3"])
    except (KeyError, TypeError) as exc:
        errors.append(f"{where} malformed: {exc}")
        return None
    try:
        expanded = two_stage.substitute_new(template, word_z, word_t)
        if expanded not in two_stage.cyclic_orientations(AK3[1]):
            raise ValueError("template does not expand to the braid relator")
        got_raw = two_stage.derive_rank3(
            AK3,
            1,
            word_z,
            word_t,
            template,
            eliminated="y",
        )
        got_rank3 = _independent_canonical_rank3(got_raw)
    except ValueError as exc:
        errors.append(f"{where} replay rejected: {exc}")
        return None
    if got_raw != raw_rank3:
        errors.append(f"{where} raw rank3 mismatch")
    if got_rank3 != rank3:
        errors.append(f"{where} canonical rank3 mismatch")
    if any(_x_count(relator) == 1 for relator in got_rank3):
        errors.append(f"{where} is an immediate-isolator source")
    return got_rank3


def _verify_output_row(
    row: dict[str, object],
    index: int,
    sources: list[tuple[str, str, str] | None],
    errors: list[str],
) -> None:
    where = f"output_witnesses[{index}]"
    try:
        source_index = int(row["source_index"])
        move_row = row["move"]
        if not isinstance(move_row, dict):
            raise TypeError("move must be an object")
        move = OneEdgeMove(
            target=int(move_row["target"]),
            other=int(move_row["other"]),
            sign=int(move_row["sign"]),
            target_rotation=int(move_row["target_rotation"]),
            other_rotation=int(move_row["other_rotation"]),
            child_relator=str(move_row["child_relator"]),
        )
        isolator_index = int(row["isolator_index"])
        expression_x = str(row["expression_x"])
        output = tuple(row["output"])
        source = sources[source_index]
        if source is None:
            raise ValueError("source row did not replay")
    except (IndexError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"{where} malformed: {exc}")
        return
    try:
        child = _independent_replay_move(source, move)
        got_expression = two_stage.solve_isolator(
            child[isolator_index],
            "x",
        )
        got_output = two_stage.remove_second(
            child,
            isolator_index,
            "x",
        )
    except (IndexError, ValueError) as exc:
        errors.append(f"{where} replay rejected: {exc}")
        return
    if got_expression != expression_x:
        errors.append(f"{where} isolator expression mismatch")
    if got_output != output:
        errors.append(f"{where} output mismatch")


def _independent_replay_move(
    source: tuple[str, str, str],
    move: OneEdgeMove,
) -> tuple[str, str, str]:
    if move.target not in (0, 1, 2) or move.other not in (0, 1, 2):
        raise ValueError("invalid move index")
    if move.target == move.other:
        raise ValueError("target and other must differ")
    if move.sign not in (1, -1):
        raise ValueError("invalid move sign")

    target = source[move.target]
    other = (
        source[move.other]
        if move.sign == 1
        else two_stage.inverse(source[move.other])
    )
    target_rotations = _independent_rotations(target)
    other_rotations = _independent_rotations(other)
    try:
        target_word = target_rotations[move.target_rotation]
        other_word = other_rotations[move.other_rotation]
    except IndexError as exc:
        raise ValueError("rotation offset out of range") from exc
    if target_word[-1] != other_word[0].swapcase():
        raise ValueError("stored move has no cancelling seam")
    child_relator = _independent_cyclic_reduce(target_word + other_word)
    if child_relator != move.child_relator:
        raise ValueError("stored child relator mismatch")
    child = list(source)
    child[move.target] = child_relator
    return tuple(child)


def _independent_cyclic_reduce(word: str) -> str:
    stack: list[str] = []
    for letter in word:
        if stack and stack[-1] == letter.swapcase():
            stack.pop()
        else:
            stack.append(letter)
    while len(stack) >= 2 and stack[0] == stack[-1].swapcase():
        stack = stack[1:-1]
    return "".join(stack)


def _independent_rotations(word: str) -> tuple[str, ...]:
    reduced = _independent_cyclic_reduce(word)
    if not reduced:
        return ("",)
    return tuple(
        reduced[offset:] + reduced[:offset]
        for offset in range(len(reduced))
    )


def _independent_canonical_rank3(
    rank3: tuple[str, str, str],
) -> tuple[str, str, str]:
    canonical: list[str] = []
    for word in rank3:
        reduced = _independent_cyclic_reduce(word)
        inverse = "".join(
            letter.swapcase() for letter in reversed(reduced)
        )
        canonical.append(
            min(
                _independent_rotations(reduced)
                + _independent_rotations(inverse)
            )
        )
    return tuple(sorted(canonical))


def _certificate_from_census(
    census: OneEdgeCensus,
) -> dict[str, object]:
    source_index_by_rank3 = {
        source.rank3: index
        for index, source in enumerate(census.source_census.eligible_sources)
    }
    output_witnesses = [
        {
            "source_index": source_index_by_rank3[witness.source.rank3],
            "move": witness.move.to_json(),
            "isolator_index": witness.isolator_index,
            "expression_x": witness.expression_x,
            "output": list(witness.output),
        }
        for witness in census.output_witnesses
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
    sources = census.source_census
    return {
        "schema": SCHEMA,
        "claim": (
            "finite decision for non-immediate first-stage corridors "
            "followed by one signed cyclic multiplication"
        ),
        "pair": list(sources.pair),
        "bounds": {
            "max_word_length": sources.max_word_length,
            "max_template_length": sources.max_template_length,
        },
        "defining_word_count": sources.defining_word_count,
        "defining_word_pair_count": sources.defining_word_count**2,
        "structural_template_count": sources.structural_template_count,
        "tested_cases": sources.tested_cases,
        "accepted_source_identities": sources.accepted_source_identities,
        "distinct_raw_rank3_count": sources.distinct_raw_rank3_count,
        "distinct_cyclic_rank3_count": sources.distinct_cyclic_rank3_count,
        "immediate_rank3_count": sources.immediate_rank3_count,
        "eligible_rank3_count": sources.eligible_rank3_count,
        "source_trace_sha256": sources.trace_sha256,
        "seam_move_count": census.seam_move_count,
        "one_x_incidence_count": census.one_x_incidence_count,
        "distinct_raw_output_count": census.distinct_raw_output_count,
        "canonical_output_count": len(census.aut_records),
        "trace_sha256": census.trace_sha256,
        "floor_distribution": {
            str(floor): count
            for floor, count in sorted(census.floor_distribution.items())
        },
        "minimum_output_floor": minimum,
        "eligible_sources": [
            source.to_json() for source in sources.eligible_sources
        ],
        "output_witnesses": output_witnesses,
        "aut_orbits": aut_orbits,
        "minimum_outputs": minimum_outputs,
        "candidate_lemma": (
            "PROVED" if minimum is not None and minimum <= 12 else "REFUTED"
        ),
    }


def _x_count(word: str) -> int:
    return sum(letter.lower() == "x" for letter in word)


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
            f"{data['eligible_rank3_count']} eligible rank3 states, "
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
        f"{data['eligible_rank3_count']} eligible rank3 states, "
        f"{data['distinct_raw_output_count']} outputs, "
        f"minimum {data['minimum_output_floor']}, "
        f"lemma {data['candidate_lemma']} -> {args.output}"
    )


if __name__ == "__main__":
    main()
