"""Exact cyclic one-edge compression after the first AK(3) removal."""

from collections import Counter
from dataclasses import dataclass
from hashlib import sha256

from experiments.equivalence_classes.lib.acmoves import canon
from experiments.equivalence_classes.lib.autcanon import aut_canon
from experiments.stable_ac.rank3_compression import (
    two_stabilization as two_stage,
)
from experiments.stable_ac.rank3_compression.two_stabilization import (
    free_reduce,
    inverse,
    remove_second,
    solve_isolator,
)


def cyclic_reduce(word: str) -> str:
    reduced = free_reduce(word)
    while (
        len(reduced) >= 2
        and reduced[0] == reduced[-1].swapcase()
    ):
        reduced = free_reduce(reduced[1:-1])
    return reduced


def rotations(word: str) -> tuple[str, ...]:
    reduced = cyclic_reduce(word)
    if not reduced:
        return ("",)
    return tuple(
        reduced[offset:] + reduced[:offset]
        for offset in range(len(reduced))
    )


def canonical_relator(word: str) -> str:
    reduced = cyclic_reduce(word)
    if not reduced:
        return ""
    return min(rotations(reduced) + rotations(inverse(reduced)))


def canonical_rank3(rank3: tuple[str, str, str]) -> tuple[str, str, str]:
    if len(rank3) != 3:
        raise ValueError("rank3 tuple must have exactly three relators")
    canonical = tuple(sorted(canonical_relator(word) for word in rank3))
    if any(not word for word in canonical):
        raise ValueError("rank3 relators must be nonempty")
    return canonical


@dataclass(frozen=True)
class OneEdgeMove:
    target: int
    other: int
    sign: int
    target_rotation: int
    other_rotation: int
    child_relator: str

    def to_json(self) -> dict[str, object]:
        return {
            "target": self.target,
            "other": self.other,
            "sign": self.sign,
            "target_rotation": self.target_rotation,
            "other_rotation": self.other_rotation,
            "child_relator": self.child_relator,
        }


@dataclass(frozen=True)
class Rank3Source:
    word_z: str
    word_t: str
    template: str
    raw_rank3: tuple[str, str, str]
    rank3: tuple[str, str, str]

    def to_json(self) -> dict[str, object]:
        return {
            "word_z": self.word_z,
            "word_t": self.word_t,
            "template": self.template,
            "raw_rank3": list(self.raw_rank3),
            "rank3": list(self.rank3),
        }


@dataclass(frozen=True)
class Rank3SourceCensus:
    pair: tuple[str, str]
    max_word_length: int
    max_template_length: int
    defining_word_count: int
    structural_template_count: int
    tested_cases: int
    accepted_source_identities: int
    distinct_raw_rank3_count: int
    distinct_cyclic_rank3_count: int
    immediate_rank3_count: int
    eligible_sources: tuple[Rank3Source, ...]
    trace_sha256: str

    @property
    def eligible_rank3_count(self) -> int:
        return len(self.eligible_sources)


@dataclass(frozen=True)
class OneEdgeWitness:
    source: Rank3Source
    move: OneEdgeMove
    isolator_index: int
    expression_x: str
    output: tuple[str, str]

    def to_json(self) -> dict[str, object]:
        return {
            "source": self.source.to_json(),
            "move": self.move.to_json(),
            "isolator_index": self.isolator_index,
            "expression_x": self.expression_x,
            "output": list(self.output),
        }


@dataclass(frozen=True)
class OneEdgeAutRecord:
    output: tuple[str, str]
    minimum_total: int
    representative: tuple[str, str]
    phi: dict[str, str]


@dataclass(frozen=True)
class OneEdgeCensus:
    source_census: Rank3SourceCensus
    seam_move_count: int
    one_x_incidence_count: int
    output_witnesses: tuple[OneEdgeWitness, ...]
    aut_records: tuple[OneEdgeAutRecord, ...]
    floor_distribution: dict[int, int]
    trace_sha256: str

    @property
    def distinct_raw_output_count(self) -> int:
        return len(self.output_witnesses)

    @property
    def minimum_output_floor(self) -> int | None:
        if not self.aut_records:
            return None
        return min(record.minimum_total for record in self.aut_records)


def enumerate_seam_moves(rank3: tuple[str, str, str]):
    if len(rank3) != 3:
        raise ValueError("rank3 tuple must have exactly three relators")
    for target, target_word in enumerate(rank3):
        target_rotations = rotations(target_word)
        for other, other_word in enumerate(rank3):
            if target == other:
                continue
            for sign in (1, -1):
                signed_other = other_word if sign == 1 else inverse(other_word)
                other_rotations = rotations(signed_other)
                for target_offset, target_rotation in enumerate(
                    target_rotations
                ):
                    for other_offset, other_rotation in enumerate(
                        other_rotations
                    ):
                        if (
                            target_rotation[-1]
                            != other_rotation[0].swapcase()
                        ):
                            continue
                        yield OneEdgeMove(
                            target=target,
                            other=other,
                            sign=sign,
                            target_rotation=target_offset,
                            other_rotation=other_offset,
                            child_relator=cyclic_reduce(
                                target_rotation + other_rotation
                            ),
                        )


def apply_one_edge(
    rank3: tuple[str, str, str],
    move: OneEdgeMove,
) -> tuple[str, str, str]:
    if len(rank3) != 3:
        raise ValueError("rank3 tuple must have exactly three relators")
    if move.target not in (0, 1, 2) or move.other not in (0, 1, 2):
        raise ValueError("move indices must be 0, 1, or 2")
    if move.target == move.other:
        raise ValueError("target and other indices must differ")
    if move.sign not in (1, -1):
        raise ValueError("move sign must be +1 or -1")

    target_rotations = rotations(rank3[move.target])
    signed_other = (
        rank3[move.other]
        if move.sign == 1
        else inverse(rank3[move.other])
    )
    other_rotations = rotations(signed_other)
    try:
        target_word = target_rotations[move.target_rotation]
        other_word = other_rotations[move.other_rotation]
    except IndexError as exc:
        raise ValueError("rotation offset is out of range") from exc
    if target_word[-1] != other_word[0].swapcase():
        raise ValueError("move does not have a cancelling seam")
    child_relator = cyclic_reduce(target_word + other_word)
    if move.child_relator and child_relator != move.child_relator:
        raise ValueError("stored child relator does not replay")

    child = list(rank3)
    child[move.target] = child_relator
    return tuple(child)


def remove_one_edge_isolator(
    rank3: tuple[str, str, str],
    move: OneEdgeMove,
    isolator_index: int,
) -> tuple[str, tuple[str, str]]:
    child = apply_one_edge(rank3, move)
    expression = solve_isolator(child[isolator_index], "x")
    output = remove_second(child, isolator_index, "x")
    return expression, output


def enumerate_rank3_sources(
    pair: tuple[str, str],
    max_word_length: int = 2,
    max_template_length: int = 6,
) -> Rank3SourceCensus:
    if len(pair) != 2:
        raise ValueError("source pair must have two relators")
    if max_word_length < 1:
        raise ValueError("max_word_length must be positive")
    if max_template_length < 2:
        raise ValueError("max_template_length must be at least two")

    words = tuple(
        two_stage._reduced_words(
            two_stage.OLD_ALPHABET,
            1,
            max_word_length,
        )
    )
    templates = tuple(
        template
        for template in two_stage._reduced_words(
            two_stage.ALPHABET,
            2,
            max_template_length,
            cyclic=True,
        )
        if sum(letter.lower() == "y" for letter in template) == 1
        and any(letter.lower() == "z" for letter in template)
        and any(letter.lower() == "t" for letter in template)
    )
    source_orientations = frozenset(
        two_stage.cyclic_orientations(pair[1])
    )
    trace = sha256()
    accepted = 0
    raw_rank3_states: set[tuple[str, str, str]] = set()
    first_by_cyclic: dict[tuple[str, str, str], Rank3Source] = {}

    for word_z in words:
        for word_t in words:
            for template in templates:
                expanded = two_stage.substitute_new(
                    template,
                    word_z,
                    word_t,
                )
                source_match = expanded in source_orientations
                trace.update(
                    b"S\0"
                    + "\0".join(
                        (
                            word_z,
                            word_t,
                            template,
                            expanded,
                            "1" if source_match else "0",
                        )
                    ).encode("ascii")
                    + b"\n"
                )
                if not source_match:
                    continue
                accepted += 1
                raw_rank3 = two_stage.derive_rank3(
                    pair,
                    1,
                    word_z,
                    word_t,
                    template,
                    eliminated="y",
                )
                raw_rank3_states.add(raw_rank3)
                rank3 = canonical_rank3(raw_rank3)
                first_by_cyclic.setdefault(
                    rank3,
                    Rank3Source(
                        word_z=word_z,
                        word_t=word_t,
                        template=template,
                        raw_rank3=raw_rank3,
                        rank3=rank3,
                    ),
                )

    immediate = {
        rank3
        for rank3 in first_by_cyclic
        if any(_x_count(relator) == 1 for relator in rank3)
    }
    eligible_sources = tuple(
        first_by_cyclic[rank3]
        for rank3 in sorted(set(first_by_cyclic) - immediate)
    )
    return Rank3SourceCensus(
        pair=tuple(pair),
        max_word_length=max_word_length,
        max_template_length=max_template_length,
        defining_word_count=len(words),
        structural_template_count=len(templates),
        tested_cases=len(words) * len(words) * len(templates),
        accepted_source_identities=accepted,
        distinct_raw_rank3_count=len(raw_rank3_states),
        distinct_cyclic_rank3_count=len(first_by_cyclic),
        immediate_rank3_count=len(immediate),
        eligible_sources=eligible_sources,
        trace_sha256=trace.hexdigest(),
    )


def enumerate_one_edge_compressions(
    pair: tuple[str, str],
    max_word_length: int = 2,
    max_template_length: int = 6,
) -> OneEdgeCensus:
    source_census = enumerate_rank3_sources(
        pair,
        max_word_length=max_word_length,
        max_template_length=max_template_length,
    )
    trace = sha256()
    trace.update(
        b"SOURCE\0"
        + source_census.trace_sha256.encode("ascii")
        + b"\n"
    )
    seam_move_count = 0
    one_x_incidence_count = 0
    first_by_output: dict[tuple[str, str], OneEdgeWitness] = {}

    for source in source_census.eligible_sources:
        for move in enumerate_seam_moves(source.rank3):
            seam_move_count += 1
            child = list(source.rank3)
            child[move.target] = move.child_relator
            child_tuple = tuple(child)
            counts = tuple(_x_count(relator) for relator in child_tuple)
            trace.update(
                b"M\0"
                + "\0".join(
                    (
                        *source.rank3,
                        str(move.target),
                        str(move.other),
                        str(move.sign),
                        str(move.target_rotation),
                        str(move.other_rotation),
                        move.child_relator,
                        ",".join(str(count) for count in counts),
                    )
                ).encode("ascii")
                + b"\n"
            )
            for isolator_index, count in enumerate(counts):
                if count != 1:
                    continue
                one_x_incidence_count += 1
                expression_x = solve_isolator(
                    child_tuple[isolator_index],
                    "x",
                )
                output = remove_second(
                    child_tuple,
                    isolator_index,
                    "x",
                )
                witness = OneEdgeWitness(
                    source=source,
                    move=move,
                    isolator_index=isolator_index,
                    expression_x=expression_x,
                    output=output,
                )
                first_by_output.setdefault(output, witness)
                trace.update(
                    b"X\0"
                    + "\0".join(
                        (
                            str(isolator_index),
                            expression_x,
                            *output,
                        )
                    ).encode("ascii")
                    + b"\n"
                )

    raw_outputs = tuple(sorted(first_by_output))
    canonical_outputs = sorted({canon(*output) for output in raw_outputs})
    aut_records: list[OneEdgeAutRecord] = []
    floor_by_canonical: dict[tuple[str, str], int] = {}
    for output in canonical_outputs:
        minimum_total, representative, phi = aut_canon(output)
        floor_by_canonical[output] = minimum_total
        aut_records.append(
            OneEdgeAutRecord(
                output=output,
                minimum_total=minimum_total,
                representative=representative,
                phi=phi,
            )
        )
    floor_distribution = Counter(
        floor_by_canonical[canon(*output)] for output in raw_outputs
    )
    return OneEdgeCensus(
        source_census=source_census,
        seam_move_count=seam_move_count,
        one_x_incidence_count=one_x_incidence_count,
        output_witnesses=tuple(
            first_by_output[output] for output in raw_outputs
        ),
        aut_records=tuple(aut_records),
        floor_distribution=dict(sorted(floor_distribution.items())),
        trace_sha256=trace.hexdigest(),
    )


def _x_count(word: str) -> int:
    return sum(letter.lower() == "x" for letter in word)
