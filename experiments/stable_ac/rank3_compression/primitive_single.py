"""Primitive-single-relator removals from certified AK(3) rank-three states."""

from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path

from experiments.equivalence_classes.lib.acmoves import canon
from experiments.equivalence_classes.lib.autcanon import aut_canon
from experiments.stable_ac.rank3_compression.one_edge import cyclic_reduce
from experiments.stable_ac.rank3_compression.primitive_pair_certificate import (
    RESULT_PATH as UPSTREAM_PATH,
)
from experiments.stable_ac.rank3_compression.rank3_whitehead import (
    WhiteheadWordReduction,
    apply_automorphism,
    is_primitive_word,
    reduce_word,
)
from experiments.stable_ac.rank3_compression.two_stabilization import (
    free_reduce,
)


BASIS = ("x", "z", "t")


@dataclass(frozen=True)
class PrimitiveSingleWitness:
    rank3: tuple[str, str, str]
    relator_index: int
    relator: str
    reduction: WhiteheadWordReduction
    transformed_rank3: tuple[str, str, str]
    eliminated_generator: str
    output: tuple[str, str]


@dataclass(frozen=True)
class PrimitiveSingleAutRecord:
    output: tuple[str, str]
    minimum_total: int
    representative: tuple[str, str]
    phi: dict[str, str]


@dataclass(frozen=True)
class PrimitiveSingleCensus:
    sources: tuple[tuple[str, str, str], ...]
    upstream_trace: str
    relators_tested: int
    distinct_relator_count: int
    primitive_relator_count: int
    primitive_occurrence_count: int
    output_witnesses: tuple[PrimitiveSingleWitness, ...]
    aut_records: tuple[PrimitiveSingleAutRecord, ...]
    floor_distribution: dict[int, int]
    trace_sha256: str

    @property
    def source_count(self) -> int:
        return len(self.sources)

    @property
    def distinct_output_count(self) -> int:
        return len(self.output_witnesses)

    @property
    def minimum_output_floor(self) -> int | None:
        if not self.aut_records:
            return None
        return min(record.minimum_total for record in self.aut_records)


def load_upstream_sources(
    path: Path = UPSTREAM_PATH,
) -> tuple[tuple[tuple[str, str, str], ...], str]:
    with path.open() as handle:
        data = json.load(handle)
    if data.get("schema") != "ak3-primitive-pair-v1":
        raise ValueError("primitive-pair certificate has wrong schema")
    trace = data.get("trace_sha256")
    if not isinstance(trace, str) or len(trace) != 64:
        raise ValueError("primitive-pair certificate has invalid trace")
    source_rows = data.get("sources")
    if not isinstance(source_rows, list):
        raise ValueError("primitive-pair certificate has no sources")
    sources = tuple(
        tuple(row["rank3"])
        for row in source_rows
        if isinstance(row, dict) and isinstance(row.get("rank3"), list)
    )
    if len(sources) != len(source_rows) or any(
        len(source) != 3 for source in sources
    ):
        raise ValueError("primitive-pair certificate has malformed sources")
    return tuple(sorted(set(sources))), trace


def remove_primitive_relator(
    rank3: tuple[str, str, str],
    relator_index: int,
    reduction: WhiteheadWordReduction,
) -> tuple[tuple[str, str, str], str, tuple[str, str]]:
    if len(rank3) != 3:
        raise ValueError("rank3 must have three relators")
    if relator_index not in (0, 1, 2):
        raise ValueError("relator_index must be 0, 1, or 2")
    if not is_primitive_word(reduction):
        raise ValueError("selected relator is not primitive")
    transformed = tuple(
        cyclic_reduce(apply_automorphism(word, reduction.phi))
        for word in rank3
    )
    isolator = transformed[relator_index]
    if len(isolator) != 1:
        raise ValueError("primitive witness did not produce a basis letter")
    eliminated = isolator.lower()
    if eliminated not in BASIS:
        raise ValueError("isolator is outside the rank-three basis")
    survivors = tuple(generator for generator in BASIS if generator != eliminated)
    relabel = {
        survivors[0]: "x",
        survivors[0].upper(): "X",
        survivors[1]: "y",
        survivors[1].upper(): "Y",
    }
    output_words: list[str] = []
    for index, word in enumerate(transformed):
        if index == relator_index:
            continue
        quotient = free_reduce(
            "".join(
                "" if letter.lower() == eliminated else letter
                for letter in word
            )
        )
        output_words.append(
            free_reduce("".join(relabel[letter] for letter in quotient))
        )
    return transformed, eliminated, canon(*output_words)


def enumerate_primitive_single_removals(
    sources: tuple[tuple[str, str, str], ...] | None = None,
    upstream_trace: str | None = None,
) -> PrimitiveSingleCensus:
    if sources is None:
        sources, loaded_trace = load_upstream_sources()
        upstream_trace = loaded_trace
    sources = tuple(sorted(set(sources)))
    if upstream_trace is None:
        raise ValueError("upstream_trace is required for explicit sources")

    trace = sha256()
    trace.update(b"UPSTREAM\0" + upstream_trace.encode("ascii") + b"\n")
    reduction_cache: dict[str, WhiteheadWordReduction] = {}
    primitive_occurrences = 0
    first_by_output: dict[
        tuple[str, str],
        PrimitiveSingleWitness,
    ] = {}

    for rank3 in sources:
        if len(rank3) != 3:
            raise ValueError("every source must have three relators")
        for relator_index, relator in enumerate(rank3):
            reduction = reduction_cache.get(relator)
            if reduction is None:
                reduction = reduce_word(relator)
                reduction_cache[relator] = reduction
            primitive = is_primitive_word(reduction)
            trace.update(
                b"R\0"
                + "\0".join(
                    (
                        *rank3,
                        str(relator_index),
                        relator,
                        str(reduction.minimum_total),
                        reduction.minimum,
                        reduction.phi["x"],
                        reduction.phi["z"],
                        reduction.phi["t"],
                        "1" if primitive else "0",
                    )
                ).encode("ascii")
                + b"\n"
            )
            if not primitive:
                continue
            primitive_occurrences += 1
            transformed, eliminated, output = remove_primitive_relator(
                rank3,
                relator_index,
                reduction,
            )
            first_by_output.setdefault(
                output,
                PrimitiveSingleWitness(
                    rank3=rank3,
                    relator_index=relator_index,
                    relator=relator,
                    reduction=reduction,
                    transformed_rank3=transformed,
                    eliminated_generator=eliminated,
                    output=output,
                ),
            )

    outputs = tuple(sorted(first_by_output))
    aut_records: list[PrimitiveSingleAutRecord] = []
    for output in outputs:
        minimum_total, representative, phi = aut_canon(output)
        aut_records.append(
            PrimitiveSingleAutRecord(
                output=output,
                minimum_total=minimum_total,
                representative=representative,
                phi=phi,
            )
        )
    floor_distribution = Counter(
        record.minimum_total for record in aut_records
    )
    primitive_relators = sum(
        is_primitive_word(reduction)
        for reduction in reduction_cache.values()
    )
    return PrimitiveSingleCensus(
        sources=sources,
        upstream_trace=upstream_trace,
        relators_tested=len(sources) * 3,
        distinct_relator_count=len(reduction_cache),
        primitive_relator_count=primitive_relators,
        primitive_occurrence_count=primitive_occurrences,
        output_witnesses=tuple(
            first_by_output[output] for output in outputs
        ),
        aut_records=tuple(aut_records),
        floor_distribution=dict(sorted(floor_distribution.items())),
        trace_sha256=trace.hexdigest(),
    )
