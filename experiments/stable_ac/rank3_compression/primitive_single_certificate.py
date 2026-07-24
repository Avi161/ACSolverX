"""Chained certificate for primitive-single AK(3) corridor removals."""

import argparse
import json
from pathlib import Path

from experiments.equivalence_classes.lib.autcanon import check
from experiments.equivalence_classes.lib.words import canon_pair
from experiments.stable_ac.rank3_compression.primitive_pair_certificate import (
    RESULT_PATH as UPSTREAM_PATH,
    _apply,
    _canonical_relator,
    _compose,
    _second_kind_automorphisms,
    verify_certificate as verify_upstream_certificate,
)
from experiments.stable_ac.rank3_compression.primitive_single import (
    BASIS,
    PrimitiveSingleCensus,
    enumerate_primitive_single_removals,
    load_upstream_sources,
)


SCHEMA = "ak3-primitive-single-v1"
GENERATORS = ("x", "z", "t")
ROOT = Path(__file__).resolve().parents[3]
RESULT_PATH = ROOT / "results/stable_ac/theory/ak3_primitive_single.json"


def build_certificate(
    sources: tuple[tuple[str, str, str], ...] | None = None,
    upstream_trace: str | None = None,
) -> dict[str, object]:
    census = enumerate_primitive_single_removals(
        sources=sources,
        upstream_trace=upstream_trace,
    )
    return _certificate_from_census(census)


def verify_certificate(
    data: dict[str, object],
    verify_upstream: bool = True,
) -> None:
    errors: list[str] = []
    if data.get("schema") != SCHEMA:
        errors.append(f"wrong schema: {data.get('schema')!r}")
    source_rows = data.get("sources")
    if not isinstance(source_rows, list):
        errors.append("sources must be a list")
        source_rows = []
    sources = tuple(
        tuple(source) for source in source_rows if isinstance(source, list)
    )
    if len(sources) != len(source_rows) or any(
        len(source) != 3 for source in sources
    ):
        errors.append("malformed sources")
    upstream_trace = data.get("upstream_trace")
    if not isinstance(upstream_trace, str):
        errors.append("upstream_trace must be a string")

    if verify_upstream:
        with UPSTREAM_PATH.open() as handle:
            upstream = json.load(handle)
        verify_upstream_certificate(upstream)
        expected_sources, expected_trace = load_upstream_sources()
        if sources != expected_sources:
            errors.append("sources differ from verified upstream certificate")
        if upstream_trace != expected_trace:
            errors.append("trace differs from verified upstream certificate")

    records = data.get("word_records")
    if not isinstance(records, list):
        errors.append("word_records must be a list")
        records = []
    record_words: list[str | None] = []
    record_primitive: list[bool] = []
    record_phi: list[dict[str, str] | None] = []
    for index, row in enumerate(records):
        if not isinstance(row, dict):
            errors.append(f"word_records[{index}] is not an object")
            record_words.append(None)
            record_primitive.append(False)
            record_phi.append(None)
            continue
        word, primitive, phi = _verify_word_record(row, index, errors)
        record_words.append(word)
        record_primitive.append(primitive)
        record_phi.append(phi)

    occurrences = data.get("primitive_occurrences")
    if not isinstance(occurrences, list):
        errors.append("primitive_occurrences must be a list")
        occurrences = []
    output_set: set[tuple[str, str]] = set()
    for index, row in enumerate(occurrences):
        if not isinstance(row, dict):
            errors.append(
                f"primitive_occurrences[{index}] is not an object"
            )
            continue
        output = _verify_occurrence(
            row,
            index,
            sources,
            record_words,
            record_primitive,
            record_phi,
            errors,
        )
        if output is not None:
            output_set.add(output)

    aut_orbits = data.get("aut_orbits")
    if not isinstance(aut_orbits, list):
        errors.append("aut_orbits must be a list")
        aut_orbits = []
    aut_outputs: set[tuple[str, str]] = set()
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
        for output_index, row in enumerate(outputs):
            if not isinstance(row, dict):
                errors.append(
                    f"aut_orbits[{orbit_index}].outputs[{output_index}] "
                    "is not an object"
                )
                continue
            output = tuple(row.get("output", ()))
            phi = row.get("phi")
            if (
                len(output) != 2
                or not isinstance(phi, dict)
                or not check(output, representative, phi)
            ):
                errors.append(
                    f"aut_orbits[{orbit_index}].outputs[{output_index}] "
                    "has an invalid Aut witness"
                )
            else:
                aut_outputs.add(output)
    if output_set != aut_outputs:
        errors.append("occurrence outputs differ from Aut-certified outputs")

    minimum = data.get("minimum_output_floor")
    if data.get("candidate_lemma") != (
        "PROVED" if isinstance(minimum, int) and minimum <= 12 else "REFUTED"
    ):
        errors.append("candidate verdict mismatch")

    if errors:
        raise AssertionError("\n".join(errors))

    expected = build_certificate(
        sources=sources,
        upstream_trace=upstream_trace,
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


def _verify_word_record(
    row: dict[str, object],
    index: int,
    errors: list[str],
) -> tuple[str | None, bool, dict[str, str] | None]:
    where = f"word_records[{index}]"
    try:
        word = str(row["word"])
        minimum_total = int(row["minimum_total"])
        minimum = str(row["minimum"])
        phi = {generator: str(row["phi"][generator]) for generator in GENERATORS}
        steps = tuple(
            {
                generator: str(step[generator])
                for generator in GENERATORS
            }
            for step in row["steps"]
        )
        primitive = bool(row["primitive"])
        current = _canonical_relator(word)
        previous_total = len(current)
        composed = {generator: generator for generator in GENERATORS}
        for step_index, step in enumerate(steps):
            current = _canonical_relator(_apply(current, step))
            if len(current) >= previous_total:
                raise ValueError(
                    f"step {step_index} does not strictly descend"
                )
            previous_total = len(current)
            composed = _compose(step, composed)
        direct = _canonical_relator(_apply(word, phi))
        if composed != phi:
            raise ValueError("composed automorphism mismatch")
        if current != minimum or direct != minimum:
            raise ValueError("minimum witness mismatch")
        if minimum_total != len(minimum):
            raise ValueError("minimum total mismatch")
        for automorphism in _second_kind_automorphisms():
            image = _canonical_relator(_apply(minimum, automorphism))
            if len(image) < minimum_total:
                raise ValueError("endpoint admits a Whitehead descent")
        got_primitive = minimum_total == 1
        if primitive != got_primitive:
            raise ValueError("primitive verdict mismatch")
    except (KeyError, TypeError, ValueError) as exc:
        errors.append(f"{where} replay rejected: {exc}")
        return None, False, None
    return word, primitive, phi


def _verify_occurrence(
    row: dict[str, object],
    index: int,
    sources: tuple[tuple[str, str, str], ...],
    record_words: list[str | None],
    record_primitive: list[bool],
    record_phi: list[dict[str, str] | None],
    errors: list[str],
) -> tuple[str, str] | None:
    where = f"primitive_occurrences[{index}]"
    try:
        source_index = int(row["source_index"])
        relator_index = int(row["relator_index"])
        record_index = int(row["word_record_index"])
        transformed = tuple(row["transformed_rank3"])
        eliminated = str(row["eliminated_generator"])
        output = tuple(row["output"])
        source = sources[source_index]
        word = record_words[record_index]
        primitive = record_primitive[record_index]
        phi = record_phi[record_index]
        if relator_index not in (0, 1, 2):
            raise ValueError("invalid relator index")
        if word is None or phi is None or not primitive:
            raise ValueError("referenced word is not primitive")
        if source[relator_index] != word:
            raise ValueError("word record does not match source")
        got_transformed = tuple(
            _cyclic_reduce(_apply(source_word, phi))
            for source_word in source
        )
        if got_transformed != transformed:
            raise ValueError("transformed rank3 mismatch")
        if len(transformed[relator_index]) != 1:
            raise ValueError("primitive relator is not a basis letter")
        got_eliminated = transformed[relator_index].lower()
        if got_eliminated != eliminated:
            raise ValueError("eliminated generator mismatch")
        got_output = _quotient(
            transformed,
            relator_index,
            eliminated,
        )
        if got_output != output:
            raise ValueError("quotient output mismatch")
    except (IndexError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"{where} replay rejected: {exc}")
        return None
    return output


def _quotient(
    transformed: tuple[str, str, str],
    relator_index: int,
    eliminated: str,
) -> tuple[str, str]:
    survivors = tuple(generator for generator in BASIS if generator != eliminated)
    relabel = {
        survivors[0]: "x",
        survivors[0].upper(): "X",
        survivors[1]: "y",
        survivors[1].upper(): "Y",
    }
    words = []
    for index, word in enumerate(transformed):
        if index == relator_index:
            continue
        quotient = _free_reduce(
            "".join(
                "" if letter.lower() == eliminated else letter
                for letter in word
            )
        )
        words.append(
            _free_reduce("".join(relabel[letter] for letter in quotient))
        )
    return canon_pair(*words)


def _free_reduce(word: str) -> str:
    stack: list[str] = []
    for letter in word:
        if stack and stack[-1] == letter.swapcase():
            stack.pop()
        else:
            stack.append(letter)
    return "".join(stack)


def _cyclic_reduce(word: str) -> str:
    reduced = _free_reduce(word)
    while len(reduced) >= 2 and reduced[0] == reduced[-1].swapcase():
        reduced = reduced[1:-1]
    return reduced


def _certificate_from_census(
    census: PrimitiveSingleCensus,
) -> dict[str, object]:
    source_index = {
        source: index for index, source in enumerate(census.sources)
    }
    record_index = {
        word: index
        for index, (word, _) in enumerate(census.reduction_records)
    }
    word_records = [
        {
            "word": word,
            "minimum_total": reduction.minimum_total,
            "minimum": reduction.minimum,
            "phi": reduction.phi,
            "steps": list(reduction.steps),
            "primitive": reduction.minimum_total == 1,
        }
        for word, reduction in census.reduction_records
    ]
    primitive_occurrences = [
        {
            "source_index": source_index[witness.rank3],
            "relator_index": witness.relator_index,
            "word_record_index": record_index[witness.relator],
            "transformed_rank3": list(witness.transformed_rank3),
            "eliminated_generator": witness.eliminated_generator,
            "output": list(witness.output),
        }
        for witness in census.primitive_witnesses
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
        list(witness.output)
        for witness in census.output_witnesses
        if floor_by_output[witness.output] == minimum
    ]
    return {
        "schema": SCHEMA,
        "claim": (
            "finite decision of individually primitive relator removals "
            "from the bounded rank-three corridors"
        ),
        "upstream_trace": census.upstream_trace,
        "sources": [list(source) for source in census.sources],
        "source_count": census.source_count,
        "relators_tested": census.relators_tested,
        "distinct_relator_count": census.distinct_relator_count,
        "primitive_relator_count": census.primitive_relator_count,
        "primitive_occurrence_count": census.primitive_occurrence_count,
        "distinct_output_count": census.distinct_output_count,
        "trace_sha256": census.trace_sha256,
        "floor_distribution": {
            str(floor): count
            for floor, count in sorted(census.floor_distribution.items())
        },
        "minimum_output_floor": minimum,
        "word_records": word_records,
        "primitive_occurrences": primitive_occurrences,
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
            f"{data['source_count']} rank3 states, "
            f"{data['primitive_occurrence_count']} primitive occurrences, "
            f"minimum {data['minimum_output_floor']}, "
            f"lemma {data['candidate_lemma']}"
        )
        return
    data = build_certificate()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print(
        "CERTIFICATE WRITTEN: "
        f"{data['source_count']} rank3 states, "
        f"{data['primitive_occurrence_count']} primitive occurrences, "
        f"minimum {data['minimum_output_floor']}, "
        f"lemma {data['candidate_lemma']} -> {args.output}"
    )


if __name__ == "__main__":
    main()
