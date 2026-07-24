"""Build and independently replay the bounded AK(3) primitive-pair census."""

import argparse
import json
from pathlib import Path

from experiments.stable_ac.rank3_compression import (
    two_stabilization as two_stage,
)
from experiments.stable_ac.rank3_compression.primitive_pair import (
    AK3,
    PrimitivePairCensus,
    enumerate_primitive_pair_corridors,
)


SCHEMA = "ak3-primitive-pair-v1"
GENERATORS = ("x", "z", "t")
ROOT = Path(__file__).resolve().parents[3]
RESULT_PATH = ROOT / "results/stable_ac/theory/ak3_primitive_pair.json"


def build_certificate(
    max_word_length: int = 2,
    max_template_length: int = 6,
) -> dict[str, object]:
    census = enumerate_primitive_pair_corridors(
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

    sources_row = data.get("sources")
    if not isinstance(sources_row, list):
        errors.append("sources must be a list")
        sources_row = []
    sources: list[tuple[str, str, str] | None] = []
    for index, row in enumerate(sources_row):
        if not isinstance(row, dict):
            errors.append(f"sources[{index}] is not an object")
            sources.append(None)
            continue
        sources.append(_verify_source(row, index, errors))

    records_row = data.get("pair_records")
    if not isinstance(records_row, list):
        errors.append("pair_records must be a list")
        records_row = []
    record_pairs: list[tuple[str, str] | None] = []
    record_primitive: list[bool] = []
    for index, row in enumerate(records_row):
        if not isinstance(row, dict):
            errors.append(f"pair_records[{index}] is not an object")
            record_pairs.append(None)
            record_primitive.append(False)
            continue
        pair, primitive = _verify_pair_record(row, index, errors)
        record_pairs.append(pair)
        record_primitive.append(primitive)

    occurrences = data.get("occurrences")
    if not isinstance(occurrences, list):
        errors.append("occurrences must be a list")
        occurrences = []
    primitive_occurrences = 0
    for index, row in enumerate(occurrences):
        if not isinstance(row, dict):
            errors.append(f"occurrences[{index}] is not an object")
            continue
        try:
            source_index = int(row["source_index"])
            indices = tuple(row["relator_indices"])
            record_index = int(row["pair_record_index"])
            source = sources[source_index]
            record_pair = record_pairs[record_index]
            primitive = record_primitive[record_index]
            if source is None or record_pair is None:
                raise ValueError("referenced row did not replay")
            if (
                len(indices) != 2
                or indices[0] not in (0, 1, 2)
                or indices[1] not in (0, 1, 2)
                or indices[0] >= indices[1]
            ):
                raise ValueError("invalid relator indices")
            got_pair = _canonical_pair(
                (source[indices[0]], source[indices[1]])
            )
            if got_pair != record_pair:
                raise ValueError("pair record does not match source")
            primitive_occurrences += int(primitive)
        except (IndexError, KeyError, TypeError, ValueError) as exc:
            errors.append(f"occurrences[{index}] malformed: {exc}")

    if data.get("primitive_pair_count") != primitive_occurrences:
        errors.append("primitive occurrence count mismatch")
    if data.get("candidate_lemma") != (
        "PROVED" if primitive_occurrences else "REFUTED"
    ):
        errors.append("candidate verdict mismatch")

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


def _verify_source(
    row: dict[str, object],
    index: int,
    errors: list[str],
) -> tuple[str, str, str] | None:
    where = f"sources[{index}]"
    try:
        word_z = str(row["word_z"])
        word_t = str(row["word_t"])
        template = str(row["template"])
        raw_rank3 = tuple(row["raw_rank3"])
        rank3 = tuple(row["rank3"])
        expanded = two_stage.substitute_new(template, word_z, word_t)
        if expanded not in two_stage.cyclic_orientations(AK3[1]):
            raise ValueError("template does not expand to braid relator")
        got_raw = two_stage.derive_rank3(
            AK3,
            1,
            word_z,
            word_t,
            template,
            eliminated="y",
        )
        got_rank3 = _canonical_rank3(got_raw)
    except (KeyError, TypeError, ValueError) as exc:
        errors.append(f"{where} replay rejected: {exc}")
        return None
    if got_raw != raw_rank3:
        errors.append(f"{where} raw rank3 mismatch")
    if got_rank3 != rank3:
        errors.append(f"{where} canonical rank3 mismatch")
    return got_rank3


def _verify_pair_record(
    row: dict[str, object],
    index: int,
    errors: list[str],
) -> tuple[tuple[str, str] | None, bool]:
    where = f"pair_records[{index}]"
    try:
        pair = tuple(row["pair"])
        minimum_total = int(row["minimum_total"])
        minimum = tuple(row["minimum"])
        phi = {generator: str(row["phi"][generator]) for generator in GENERATORS}
        steps = tuple(
            {
                generator: str(step[generator])
                for generator in GENERATORS
            }
            for step in row["steps"]
        )
        primitive = bool(row["primitive"])
    except (KeyError, TypeError, ValueError) as exc:
        errors.append(f"{where} malformed: {exc}")
        return None, False

    try:
        current = _canonical_pair(pair)
        previous_total = sum(len(word) for word in current)
        composed = {generator: generator for generator in GENERATORS}
        for step_index, step in enumerate(steps):
            current = _canonical_pair(
                tuple(_apply(word, step) for word in current)
            )
            total = sum(len(word) for word in current)
            if total >= previous_total:
                raise ValueError(
                    f"step {step_index} does not strictly descend"
                )
            previous_total = total
            composed = _compose(step, composed)
        direct = _canonical_pair(tuple(_apply(word, phi) for word in pair))
        if composed != phi:
            raise ValueError("composed automorphism mismatch")
        if current != minimum or direct != minimum:
            raise ValueError("minimum witness mismatch")
        if minimum_total != sum(len(word) for word in minimum):
            raise ValueError("minimum total mismatch")
        for automorphism in _second_kind_automorphisms():
            image = _canonical_pair(
                tuple(_apply(word, automorphism) for word in minimum)
            )
            if sum(len(word) for word in image) < minimum_total:
                raise ValueError("endpoint admits a Whitehead descent")
        got_primitive = (
            minimum_total == 2
            and all(len(word) == 1 for word in minimum)
            and minimum[0].lower() != minimum[1].lower()
        )
        if got_primitive != primitive:
            raise ValueError("primitive verdict mismatch")
    except ValueError as exc:
        errors.append(f"{where} replay rejected: {exc}")
        return None, False
    return pair, primitive


def _certificate_from_census(
    census: PrimitivePairCensus,
) -> dict[str, object]:
    source_index = {
        source.rank3: index for index, source in enumerate(census.sources)
    }
    first_by_pair = {}
    for row in census.rows:
        first_by_pair.setdefault(row.pair, row.reduction)
    pairs = sorted(first_by_pair)
    pair_index = {pair: index for index, pair in enumerate(pairs)}

    pair_records = []
    for pair in pairs:
        reduction = first_by_pair[pair]
        primitive = (
            reduction.minimum_total == 2
            and all(len(word) == 1 for word in reduction.minimum)
            and reduction.minimum[0].lower()
            != reduction.minimum[1].lower()
        )
        pair_records.append(
            {
                "pair": list(pair),
                "minimum_total": reduction.minimum_total,
                "minimum": list(reduction.minimum),
                "phi": reduction.phi,
                "steps": list(reduction.steps),
                "primitive": primitive,
            }
        )
    occurrences = [
        {
            "source_index": source_index[row.source.rank3],
            "relator_indices": list(row.indices),
            "pair_record_index": pair_index[row.pair],
        }
        for row in census.rows
    ]
    minimum_pair_floor = min(census.minimum_distribution)
    return {
        "schema": SCHEMA,
        "claim": (
            "finite decision of primitive relator pairs in the bounded "
            "two-stabilization rank-three corridors"
        ),
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
        "distinct_raw_rank3_count": census.distinct_raw_rank3_count,
        "distinct_cyclic_rank3_count": census.distinct_cyclic_rank3_count,
        "tested_relator_pair_count": census.tested_relator_pair_count,
        "distinct_relator_pair_count": census.distinct_relator_pair_count,
        "minimum_distribution": {
            str(minimum): count
            for minimum, count in sorted(
                census.minimum_distribution.items()
            )
        },
        "minimum_pair_floor": minimum_pair_floor,
        "primitive_pair_count": census.primitive_pair_count,
        "source_trace_sha256": census.source_trace_sha256,
        "trace_sha256": census.trace_sha256,
        "sources": [source.to_json() for source in census.sources],
        "pair_records": pair_records,
        "occurrences": occurrences,
        "candidate_lemma": (
            "PROVED" if census.primitive_pair_count else "REFUTED"
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


def _canonical_relator(word: str) -> str:
    reduced = _cyclic_reduce(word)
    if not reduced:
        return ""
    inverse = _inverse(reduced)
    rotations = tuple(
        spelling[offset:] + spelling[:offset]
        for spelling in (reduced, inverse)
        for offset in range(len(spelling))
    )
    return min(rotations)


def _canonical_pair(pair: tuple[str, str]) -> tuple[str, str]:
    canonical = tuple(sorted(_canonical_relator(word) for word in pair))
    if len(canonical) != 2 or any(not word for word in canonical):
        raise ValueError("pair must contain two nontrivial cyclic words")
    return canonical


def _canonical_rank3(
    rank3: tuple[str, str, str],
) -> tuple[str, str, str]:
    canonical = tuple(sorted(_canonical_relator(word) for word in rank3))
    if len(canonical) != 3 or any(not word for word in canonical):
        raise ValueError("rank3 must contain nontrivial cyclic words")
    return canonical


def _apply(word: str, phi: dict[str, str]) -> str:
    pieces = []
    for letter in word:
        image = phi[letter.lower()]
        pieces.append(image if letter.islower() else _inverse(image))
    return _free_reduce("".join(pieces))


def _compose(
    after: dict[str, str],
    before: dict[str, str],
) -> dict[str, str]:
    return {
        generator: _apply(before[generator], after)
        for generator in GENERATORS
    }


def _second_kind_automorphisms() -> tuple[dict[str, str], ...]:
    signed = tuple(
        letter
        for generator in GENERATORS
        for letter in (generator, generator.upper())
    )
    unique = {}
    for multiplier in signed:
        others = tuple(
            letter
            for letter in signed
            if letter not in (multiplier, multiplier.swapcase())
        )
        for mask in range(1 << len(others)):
            subset = {multiplier}
            subset.update(
                letter
                for bit, letter in enumerate(others)
                if mask & (1 << bit)
            )
            phi = {}
            for generator in GENERATORS:
                if generator in (multiplier, multiplier.swapcase()):
                    phi[generator] = generator
                    continue
                positive = generator in subset
                negative = generator.upper() in subset
                if positive and not negative:
                    phi[generator] = generator + multiplier
                elif negative and not positive:
                    phi[generator] = multiplier.swapcase() + generator
                elif positive and negative:
                    phi[generator] = (
                        multiplier.swapcase()
                        + generator
                        + multiplier
                    )
                else:
                    phi[generator] = generator
            key = tuple(phi[generator] for generator in GENERATORS)
            unique.setdefault(key, phi)
    unique.pop(GENERATORS, None)
    automorphisms = tuple(unique[key] for key in sorted(unique))
    if len(automorphisms) != 90:
        raise AssertionError("rank-three Whitehead set must contain 90 maps")
    return automorphisms


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
            f"{data['distinct_cyclic_rank3_count']} rank3 states, "
            f"{data['tested_relator_pair_count']} relator pairs, "
            f"minimum {data['minimum_pair_floor']}, "
            f"lemma {data['candidate_lemma']}"
        )
        return
    data = build_certificate()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print(
        "CERTIFICATE WRITTEN: "
        f"{data['distinct_cyclic_rank3_count']} rank3 states, "
        f"{data['tested_relator_pair_count']} relator pairs, "
        f"minimum {data['minimum_pair_floor']}, "
        f"lemma {data['candidate_lemma']} -> {args.output}"
    )


if __name__ == "__main__":
    main()
