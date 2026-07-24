"""One rank-three AC edge followed by primitive-relator removal."""

from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
import json
from math import gcd
from pathlib import Path

from experiments.equivalence_classes.lib.autcanon import aut_canon
from experiments.stable_ac.rank3_compression.one_edge import (
    canonical_relator,
    cyclic_reduce,
    rotations,
)
from experiments.stable_ac.rank3_compression.primitive_single import (
    PrimitiveSingleAutRecord,
    remove_primitive_relator,
)
from experiments.stable_ac.rank3_compression.primitive_single_certificate import (
    RESULT_PATH as UPSTREAM_PATH,
)
from experiments.stable_ac.rank3_compression.rank3_whitehead import (
    WhiteheadWordReduction,
    is_primitive_word,
    reduce_word_fast,
)
from experiments.stable_ac.rank3_compression.two_stabilization import inverse


BASIS = ("x", "z", "t")
SIGNED_BASIS = ("x", "X", "z", "Z", "t", "T")


@dataclass(frozen=True)
class PrimitiveEdgeWitness:
    source: tuple[str, str, str]
    target: int
    other: int
    sign: int
    target_rotation: int
    other_rotation: int
    product_word: str
    reduction: WhiteheadWordReduction
    transformed_rank3: tuple[str, str, str]
    eliminated_generator: str
    output: tuple[str, str]


@dataclass(frozen=True)
class OneEdgePrimitiveCensus:
    sources: tuple[tuple[str, str, str], ...]
    upstream_trace: str
    literal_move_count: int
    abelian_gated_literal_count: int
    distinct_source_target_word_count: int
    distinct_product_word_count: int
    graph_gated_word_count: int
    primitive_product_word_count: int
    primitive_edge_count: int
    reduction_records: tuple[
        tuple[str, WhiteheadWordReduction | None],
        ...,
    ]
    primitive_witnesses: tuple[PrimitiveEdgeWitness, ...]
    output_witnesses: tuple[PrimitiveEdgeWitness, ...]
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
    if data.get("schema") != "ak3-primitive-single-v1":
        raise ValueError("primitive-single certificate has wrong schema")
    trace = data.get("trace_sha256")
    if not isinstance(trace, str) or len(trace) != 64:
        raise ValueError("primitive-single certificate has invalid trace")
    rows = data.get("sources")
    if not isinstance(rows, list):
        raise ValueError("primitive-single certificate has no sources")
    sources = tuple(tuple(row) for row in rows if isinstance(row, list))
    if len(sources) != len(rows) or any(len(source) != 3 for source in sources):
        raise ValueError("primitive-single certificate has malformed sources")
    return tuple(sorted(set(sources))), trace


def whitehead_graph_gate(word: str) -> bool:
    reduced = cyclic_reduce(word)
    if len(reduced) <= 1:
        return True
    adjacency = {letter: set() for letter in SIGNED_BASIS}
    for left, right in zip(reduced, reduced[1:] + reduced[:1]):
        inverse_right = right.swapcase()
        adjacency[left].add(inverse_right)
        adjacency[inverse_right].add(left)
    components = _component_count(adjacency)
    if components > 1:
        return True
    return any(
        _component_count(adjacency, removed=letter) > components
        for letter in SIGNED_BASIS
    )


def enumerate_one_edge_primitive_compressions(
    sources: tuple[tuple[str, str, str], ...] | None = None,
    upstream_trace: str | None = None,
    progress=None,
) -> OneEdgePrimitiveCensus:
    if sources is None:
        sources, loaded_trace = load_upstream_sources()
        upstream_trace = loaded_trace
    sources = tuple(sorted(set(sources)))
    if upstream_trace is None:
        raise ValueError("upstream_trace is required for explicit sources")

    trace = sha256()
    trace.update(b"UPSTREAM\0" + upstream_trace.encode("ascii") + b"\n")
    literal_moves = 0
    abelian_gated_literals = 0
    distinct_edges = 0
    reduction_cache: dict[str, WhiteheadWordReduction | None] = {}
    primitive_witnesses: list[PrimitiveEdgeWitness] = []
    first_by_output: dict[tuple[str, str], PrimitiveEdgeWitness] = {}

    for source_index, source in enumerate(sources):
        exponent_vectors = tuple(_exponent_vector(word) for word in source)
        first_move_by_target_word: dict[
            tuple[int, str],
            tuple[int, int, int, int],
        ] = {}
        for target in range(3):
            target_rotations = rotations(source[target])
            for other in range(3):
                if target == other:
                    continue
                for sign in (1, -1):
                    other_word = (
                        source[other]
                        if sign == 1
                        else inverse(source[other])
                    )
                    other_rotations = rotations(other_word)
                    move_spellings = (
                        len(target_rotations) * len(other_rotations)
                    )
                    literal_moves += move_spellings
                    vector = tuple(
                        left + sign * right
                        for left, right in zip(
                            exponent_vectors[target],
                            exponent_vectors[other],
                        )
                    )
                    if gcd(*(abs(value) for value in vector)) != 1:
                        continue
                    abelian_gated_literals += move_spellings
                    for target_offset, rotated_target in enumerate(
                        target_rotations
                    ):
                        for other_offset, rotated_other in enumerate(
                            other_rotations
                        ):
                            product_word = canonical_relator(
                                cyclic_reduce(
                                    rotated_target + rotated_other
                                )
                            )
                            if not product_word:
                                continue
                            first_move_by_target_word.setdefault(
                                (target, product_word),
                                (
                                    other,
                                    sign,
                                    target_offset,
                                    other_offset,
                                ),
                            )

        for (target, product_word), move in sorted(
            first_move_by_target_word.items()
        ):
            distinct_edges += 1
            if product_word not in reduction_cache:
                reduction_cache[product_word] = (
                    reduce_word_fast(product_word)
                    if whitehead_graph_gate(product_word)
                    else None
                )
            reduction = reduction_cache[product_word]
            primitive = (
                reduction is not None and is_primitive_word(reduction)
            )
            other, sign, target_offset, other_offset = move
            trace.update(
                b"E\0"
                + "\0".join(
                    (
                        *source,
                        str(target),
                        str(other),
                        str(sign),
                        str(target_offset),
                        str(other_offset),
                        product_word,
                        "1" if primitive else "0",
                    )
                ).encode("ascii")
                + b"\n"
            )
            if not primitive:
                continue
            child = list(source)
            child[target] = product_word
            transformed, eliminated, output = remove_primitive_relator(
                tuple(child),
                target,
                reduction,
            )
            witness = PrimitiveEdgeWitness(
                source=source,
                target=target,
                other=other,
                sign=sign,
                target_rotation=target_offset,
                other_rotation=other_offset,
                product_word=product_word,
                reduction=reduction,
                transformed_rank3=transformed,
                eliminated_generator=eliminated,
                output=output,
            )
            primitive_witnesses.append(witness)
            first_by_output.setdefault(output, witness)

        if progress is not None:
            progress(
                source_index + 1,
                len(sources),
                literal_moves,
                distinct_edges,
                len(reduction_cache),
                len(primitive_witnesses),
                len(first_by_output),
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
    graph_gated = sum(
        reduction is not None for reduction in reduction_cache.values()
    )
    primitive_words = sum(
        reduction is not None and is_primitive_word(reduction)
        for reduction in reduction_cache.values()
    )
    return OneEdgePrimitiveCensus(
        sources=sources,
        upstream_trace=upstream_trace,
        literal_move_count=literal_moves,
        abelian_gated_literal_count=abelian_gated_literals,
        distinct_source_target_word_count=distinct_edges,
        distinct_product_word_count=len(reduction_cache),
        graph_gated_word_count=graph_gated,
        primitive_product_word_count=primitive_words,
        primitive_edge_count=len(primitive_witnesses),
        reduction_records=tuple(sorted(reduction_cache.items())),
        primitive_witnesses=tuple(primitive_witnesses),
        output_witnesses=tuple(
            first_by_output[output] for output in outputs
        ),
        aut_records=tuple(aut_records),
        floor_distribution=dict(sorted(floor_distribution.items())),
        trace_sha256=trace.hexdigest(),
    )


def _exponent_vector(word: str) -> tuple[int, int, int]:
    return tuple(
        word.count(generator) - word.count(generator.upper())
        for generator in BASIS
    )


def _component_count(
    adjacency: dict[str, set[str]],
    removed: str | None = None,
) -> int:
    remaining = {
        letter for letter in SIGNED_BASIS if letter != removed
    }
    components = 0
    while remaining:
        components += 1
        stack = [remaining.pop()]
        while stack:
            letter = stack.pop()
            for neighbor in adjacency[letter]:
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    stack.append(neighbor)
    return components
