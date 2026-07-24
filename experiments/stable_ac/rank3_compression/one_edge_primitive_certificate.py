"""Certificate for one-edge primitive compression of bounded AK(3) corridors."""

import argparse
import json
from pathlib import Path

from experiments.equivalence_classes.lib.autcanon import check
from experiments.equivalence_classes.lib.words import canon_pair
from experiments.stable_ac.rank3_compression.one_edge_primitive import (
    BASIS,
    OneEdgePrimitiveCensus,
    enumerate_one_edge_primitive_compressions,
    load_upstream_sources,
    whitehead_graph_gate,
)
from experiments.stable_ac.rank3_compression.primitive_pair_certificate import (
    _apply,
    _canonical_relator,
    _compose,
    _second_kind_automorphisms,
)
from experiments.stable_ac.rank3_compression.primitive_single_certificate import (
    RESULT_PATH as UPSTREAM_PATH,
    verify_certificate as verify_upstream_certificate,
)


SCHEMA = "ak3-one-edge-primitive-v1"
GENERATORS = ("x", "z", "t")
ROOT = Path(__file__).resolve().parents[3]
RESULT_PATH = (
    ROOT / "results/stable_ac/theory/ak3_one_edge_primitive.json"
)


def build_certificate(
    sources: tuple[tuple[str, str, str], ...] | None = None,
    upstream_trace: str | None = None,
    progress=None,
) -> dict[str, object]:
    census = enumerate_one_edge_primitive_compressions(
        sources=sources,
        upstream_trace=upstream_trace,
        progress=progress,
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
        primitive_words = [
            row["word"]
            for row in upstream["word_records"]
            if row["primitive"]
        ]
        rejected = [
            word for word in primitive_words if not whitehead_graph_gate(word)
        ]
        if rejected:
            errors.append(
                f"Whitehead graph gate rejects {len(rejected)} "
                "verified primitive words"
            )

    witnesses = data.get("output_witnesses")
    if not isinstance(witnesses, list):
        errors.append("output_witnesses must be a list")
        witnesses = []
    output_set: set[tuple[str, str]] = set()
    reduction_cache: dict[str, tuple[dict[str, str], str] | None] = {}
    for index, row in enumerate(witnesses):
        if not isinstance(row, dict):
            errors.append(f"output_witnesses[{index}] is not an object")
            continue
        output = _verify_output_witness(
            row,
            index,
            sources,
            reduction_cache,
            errors,
        )
        if output is not None:
            output_set.add(output)
    if len(output_set) != len(witnesses):
        errors.append("output witnesses are not unique")

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
    if aut_outputs != output_set:
        errors.append("Aut outputs differ from primitive-edge outputs")

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


def _verify_output_witness(
    row: dict[str, object],
    index: int,
    sources: tuple[tuple[str, str, str], ...],
    reduction_cache: dict[str, tuple[dict[str, str], str] | None],
    errors: list[str],
) -> tuple[str, str] | None:
    where = f"output_witnesses[{index}]"
    try:
        source_index = int(row["source_index"])
        source = sources[source_index]
        target = int(row["target"])
        other = int(row["other"])
        sign = int(row["sign"])
        target_offset = int(row["target_rotation"])
        other_offset = int(row["other_rotation"])
        product_word = str(row["product_word"])
        minimum = str(row["minimum"])
        phi = {generator: str(row["phi"][generator]) for generator in GENERATORS}
        steps = tuple(
            {
                generator: str(step[generator])
                for generator in GENERATORS
            }
            for step in row["steps"]
        )
        transformed = tuple(row["transformed_rank3"])
        eliminated = str(row["eliminated_generator"])
        output = tuple(row["output"])
        if target not in (0, 1, 2) or other not in (0, 1, 2) or target == other:
            raise ValueError("invalid move indices")
        if sign not in (1, -1):
            raise ValueError("invalid sign")
        target_rotations = _left_rotations(source[target])
        signed_other = (
            source[other] if sign == 1 else _inverse(source[other])
        )
        other_rotations = _left_rotations(signed_other)
        got_product = _canonical_relator(
            _cyclic_reduce(
                target_rotations[target_offset]
                + other_rotations[other_offset]
            )
        )
        if got_product != product_word:
            raise ValueError("product word mismatch")

        cached = reduction_cache.get(product_word)
        if cached is None and product_word not in reduction_cache:
            current = product_word
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
            direct = _canonical_relator(_apply(product_word, phi))
            if composed != phi:
                raise ValueError("composed automorphism mismatch")
            if current != minimum or direct != minimum or len(minimum) != 1:
                raise ValueError("primitive minimum witness mismatch")
            for automorphism in _second_kind_automorphisms():
                image = _canonical_relator(_apply(minimum, automorphism))
                if len(image) < 1:
                    raise ValueError("one-letter minimum admits descent")
            reduction_cache[product_word] = (phi, minimum)
        elif cached != (phi, minimum):
            raise ValueError("inconsistent repeated product witness")

        child = list(source)
        child[target] = product_word
        got_transformed = tuple(
            _cyclic_reduce(_apply(word, phi)) for word in child
        )
        if got_transformed != transformed:
            raise ValueError("transformed rank3 mismatch")
        if len(transformed[target]) != 1:
            raise ValueError("target did not become a basis letter")
        got_eliminated = transformed[target].lower()
        if got_eliminated != eliminated:
            raise ValueError("eliminated generator mismatch")
        got_output = _quotient(transformed, target, eliminated)
        if got_output != output:
            raise ValueError("quotient output mismatch")
    except (IndexError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"{where} replay rejected: {exc}")
        return None
    return output


def _certificate_from_census(
    census: OneEdgePrimitiveCensus,
) -> dict[str, object]:
    source_index = {
        source: index for index, source in enumerate(census.sources)
    }
    output_witnesses = [
        {
            "source_index": source_index[witness.source],
            "target": witness.target,
            "other": witness.other,
            "sign": witness.sign,
            "target_rotation": witness.target_rotation,
            "other_rotation": witness.other_rotation,
            "product_word": witness.product_word,
            "minimum": witness.reduction.minimum,
            "phi": witness.reduction.phi,
            "steps": list(witness.reduction.steps),
            "transformed_rank3": list(witness.transformed_rank3),
            "eliminated_generator": witness.eliminated_generator,
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
        list(witness.output)
        for witness in census.output_witnesses
        if floor_by_output[witness.output] == minimum
    ]
    return {
        "schema": SCHEMA,
        "claim": (
            "finite decision of one rank-three AC edge followed by "
            "primitive-relator removal"
        ),
        "upstream_trace": census.upstream_trace,
        "sources": [list(source) for source in census.sources],
        "source_count": census.source_count,
        "literal_move_count": census.literal_move_count,
        "abelian_gated_literal_count": census.abelian_gated_literal_count,
        "distinct_source_target_word_count": (
            census.distinct_source_target_word_count
        ),
        "distinct_product_word_count": census.distinct_product_word_count,
        "graph_gated_word_count": census.graph_gated_word_count,
        "primitive_product_word_count": census.primitive_product_word_count,
        "primitive_edge_count": census.primitive_edge_count,
        "distinct_output_count": census.distinct_output_count,
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


def _inverse(word: str) -> str:
    return "".join(letter.swapcase() for letter in reversed(word))


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


def _left_rotations(word: str) -> tuple[str, ...]:
    reduced = _cyclic_reduce(word)
    return tuple(
        reduced[offset:] + reduced[:offset]
        for offset in range(len(reduced))
    )


def _quotient(
    transformed: tuple[str, str, str],
    target: int,
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
        if index == target:
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


def _progress(
    done: int,
    total: int,
    literal: int,
    edges: int,
    words: int,
    primitive: int,
    outputs: int,
) -> None:
    if done % 100 == 0 or done == total:
        print(
            f"PROGRESS {done}/{total} literal={literal} edges={edges} "
            f"words={words} primitive_edges={primitive} outputs={outputs}",
            flush=True,
        )


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
            f"{data['primitive_edge_count']} primitive edges, "
            f"{data['distinct_output_count']} outputs, "
            f"minimum {data['minimum_output_floor']}, "
            f"lemma {data['candidate_lemma']}"
        )
        return
    data = build_certificate(progress=_progress)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print(
        "CERTIFICATE WRITTEN: "
        f"{data['source_count']} rank3 states, "
        f"{data['primitive_edge_count']} primitive edges, "
        f"{data['distinct_output_count']} outputs, "
        f"minimum {data['minimum_output_floor']}, "
        f"lemma {data['candidate_lemma']} -> {args.output}"
    )


if __name__ == "__main__":
    main()
