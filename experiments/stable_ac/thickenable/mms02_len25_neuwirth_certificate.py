"""Exact Neuwirth decision for the MMS02 length-25 AK(3) representative."""

from __future__ import annotations

from dataclasses import dataclass

from experiments.stable_ac.thickenable import neuwirth_rank_solver as rank


PUBLISHED_WORDS = (
    "XYxYXyxYYxyXy",
    "YXyyXYxyxYYx",
)


@dataclass(frozen=True)
class MMS02Length25Decision:
    words: tuple[str, str]
    word_lengths: tuple[int, int]
    occurrence_count: int
    support_kind: str
    missing_edge: rank.ClassKey
    simple_edges: frozenset[rank.ClassKey]
    parallel_multiplicities: tuple[tuple[rank.ClassKey, int], ...]
    vertex_degrees: tuple[int, ...]
    scheme_names: tuple[str, ...]
    scheme_cuts: tuple[int, ...]
    verdict: str
    witness: rank.RankWitness | None
    counters: rank.SearchCounters


def decide_mms02_length25_neuwirth() -> MMS02Length25Decision:
    if tuple(map(len, PUBLISHED_WORDS)) != (13, 12):
        raise AssertionError("the published length-25 relators drifted")

    support = rank.classify_support(PUBLISHED_WORDS)
    if support.kind != "K4-e" or support.missing_edge != (0, 1):
        raise AssertionError("unexpected MMS02 length-25 support")
    schemes = rank.embedding_schemes(support.data)
    if tuple(scheme.cut for scheme in schemes) != (0, 1, 2, 3):
        raise AssertionError("the complete central-cut family drifted")
    if not all(scheme.slot_partition_verified for scheme in schemes):
        raise AssertionError("a central-cut scheme has invalid slots")

    decision = rank.solve_spherical(PUBLISHED_WORDS)
    if decision.support != support:
        raise AssertionError("support reconstruction disagrees with the solver")
    if decision.spherical is False and not decision.counters.exhaustive:
        raise AssertionError("a negative decision did not exhaust its budget")

    return MMS02Length25Decision(
        words=PUBLISHED_WORDS,
        word_lengths=tuple(map(len, PUBLISHED_WORDS)),
        occurrence_count=sum(map(len, PUBLISHED_WORDS)),
        support_kind=support.kind,
        missing_edge=support.missing_edge,
        simple_edges=support.simple_edges,
        parallel_multiplicities=tuple(
            (key, len(edges))
            for key, edges in sorted(support.data.class_edges.items())
        ),
        vertex_degrees=tuple(
            len(support.data.vertex_darts[vertex]) for vertex in rank.GERMS
        ),
        scheme_names=tuple(scheme.name for scheme in schemes),
        scheme_cuts=tuple(scheme.cut for scheme in schemes if scheme.cut is not None),
        verdict=(
            "SPHERICAL_CANDIDATE_REQUIRES_INDEPENDENT_AUDIT"
            if decision.spherical
            else "NOT_SPHERICAL_EXACT_COMPLEX"
        ),
        witness=decision.witness,
        counters=decision.counters,
    )
