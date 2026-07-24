"""Primitive relator-pair census for the bounded AK(3) rank-three corridors."""

from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations

from experiments.stable_ac.rank3_compression import (
    two_stabilization as two_stage,
)
from experiments.stable_ac.rank3_compression.one_edge import (
    Rank3Source,
    canonical_rank3,
)
from experiments.stable_ac.rank3_compression.rank3_whitehead import (
    WhiteheadReduction,
    canonical_cyclic_pair,
    is_primitive_pair,
    reduce_pair,
)


AK3 = ("xxxYYYY", "xyxYXY")


@dataclass(frozen=True)
class PrimitivePairRow:
    source: Rank3Source
    indices: tuple[int, int]
    pair: tuple[str, str]
    reduction: WhiteheadReduction


@dataclass(frozen=True)
class PrimitivePairCensus:
    pair: tuple[str, str]
    max_word_length: int
    max_template_length: int
    defining_word_count: int
    structural_template_count: int
    tested_cases: int
    accepted_source_identities: int
    distinct_raw_rank3_count: int
    sources: tuple[Rank3Source, ...]
    tested_relator_pair_count: int
    distinct_relator_pair_count: int
    minimum_distribution: dict[int, int]
    primitive_rows: tuple[PrimitivePairRow, ...]
    source_trace_sha256: str
    trace_sha256: str

    @property
    def distinct_cyclic_rank3_count(self) -> int:
        return len(self.sources)

    @property
    def primitive_pair_count(self) -> int:
        return len(self.primitive_rows)


def enumerate_primitive_pair_corridors(
    pair: tuple[str, str] = AK3,
    max_word_length: int = 2,
    max_template_length: int = 6,
) -> PrimitivePairCensus:
    sources, source_counts, source_trace = _enumerate_all_sources(
        pair,
        max_word_length=max_word_length,
        max_template_length=max_template_length,
    )
    trace = sha256()
    trace.update(b"SOURCE\0" + source_trace.encode("ascii") + b"\n")
    reduction_cache: dict[
        tuple[str, str],
        WhiteheadReduction,
    ] = {}
    minimum_distribution: Counter[int] = Counter()
    primitive_rows: list[PrimitivePairRow] = []

    for source in sources:
        for left, right in combinations(range(3), 2):
            relator_pair = canonical_cyclic_pair(
                (source.rank3[left], source.rank3[right])
            )
            reduction = reduction_cache.get(relator_pair)
            if reduction is None:
                reduction = reduce_pair(relator_pair)
                reduction_cache[relator_pair] = reduction
            primitive = is_primitive_pair(reduction)
            minimum_distribution[reduction.minimum_total] += 1
            trace.update(
                b"P\0"
                + "\0".join(
                    (
                        *source.rank3,
                        str(left),
                        str(right),
                        *relator_pair,
                        str(reduction.minimum_total),
                        *reduction.minimum,
                        reduction.phi["x"],
                        reduction.phi["z"],
                        reduction.phi["t"],
                        "1" if primitive else "0",
                    )
                ).encode("ascii")
                + b"\n"
            )
            if primitive:
                primitive_rows.append(
                    PrimitivePairRow(
                        source=source,
                        indices=(left, right),
                        pair=relator_pair,
                        reduction=reduction,
                    )
                )

    return PrimitivePairCensus(
        pair=tuple(pair),
        max_word_length=max_word_length,
        max_template_length=max_template_length,
        defining_word_count=source_counts["defining_word_count"],
        structural_template_count=source_counts[
            "structural_template_count"
        ],
        tested_cases=source_counts["tested_cases"],
        accepted_source_identities=source_counts[
            "accepted_source_identities"
        ],
        distinct_raw_rank3_count=source_counts[
            "distinct_raw_rank3_count"
        ],
        sources=sources,
        tested_relator_pair_count=len(sources) * 3,
        distinct_relator_pair_count=len(reduction_cache),
        minimum_distribution=dict(sorted(minimum_distribution.items())),
        primitive_rows=tuple(primitive_rows),
        source_trace_sha256=source_trace,
        trace_sha256=trace.hexdigest(),
    )


def _enumerate_all_sources(
    pair: tuple[str, str],
    max_word_length: int,
    max_template_length: int,
) -> tuple[
    tuple[Rank3Source, ...],
    dict[str, int],
    str,
]:
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
    raw_states: set[tuple[str, str, str]] = set()
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
                raw_states.add(raw_rank3)
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

    sources = tuple(
        first_by_cyclic[rank3] for rank3 in sorted(first_by_cyclic)
    )
    counts = {
        "defining_word_count": len(words),
        "structural_template_count": len(templates),
        "tested_cases": len(words) * len(words) * len(templates),
        "accepted_source_identities": accepted,
        "distinct_raw_rank3_count": len(raw_states),
    }
    return sources, counts, trace.hexdigest()
