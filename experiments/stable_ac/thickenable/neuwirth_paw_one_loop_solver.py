"""Exact signed-rank solver for a one-loop parallel-paw Neuwirth link."""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass

from experiments.stable_ac.thickenable import neuwirth_rank_solver as base
from experiments.stable_ac.thickenable.neuwirth_one_loop_solver import (
    _insert_loop,
    _verify_slot_partition,
)


@dataclass(frozen=True)
class PawOneLoopSupport:
    kind: str
    data: base.LinkData
    simple_edges: frozenset[base.ClassKey]
    core_edges: frozenset[base.ClassKey]
    loop_class: base.ClassKey | None = None
    loop_vertex: int | None = None
    articulation: int | None = None
    pendant: int | None = None
    reason: str | None = None


@dataclass(frozen=True)
class PawSearchCounters:
    scheme_budget: int = 0
    schemes_considered: int = 0
    phase_pair_budget: int = 0
    phase_pairs_considered: int = 0
    component_seed_budget: int = 0
    component_seed_attempts: int = 0
    closed_component_assignments: int = 0
    within_cycle_collision_rejections: int = 0
    raw_component_combination_budget: int = 0
    left_signature_count: int = 0
    right_signature_count: int = 0
    complement_lookups: int = 0
    compatible_signature_matches: int = 0
    witness_replay_failures: int = 0
    exhaustive: bool = False


def classify_paw_one_loop_support(
    words: tuple[str, ...],
) -> PawOneLoopSupport:
    data = base._build_link_data(tuple(words))
    simple_edges = frozenset(data.class_edges)
    loop_classes = tuple(
        sorted(key for key in simple_edges if key[0] == key[1])
    )
    core_edges = frozenset(
        key for key in simple_edges if key[0] != key[1]
    )
    if len(loop_classes) != 1:
        return PawOneLoopSupport(
            "UNSUPPORTED",
            data,
            simple_edges,
            core_edges,
            reason="support must have exactly one loop class",
        )
    loop_class = loop_classes[0]
    loop_vertex = loop_class[0]
    if len(data.class_edges[loop_class]) != 1:
        return PawOneLoopSupport(
            "UNSUPPORTED",
            data,
            simple_edges,
            core_edges,
            loop_class=loop_class,
            loop_vertex=loop_vertex,
            reason="the loop class must contain exactly one edge",
        )

    adjacency = {vertex: set() for vertex in base.GERMS}
    for left, right in core_edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    degrees = {
        vertex: len(adjacency[vertex]) for vertex in base.GERMS
    }
    if (
        len(core_edges) != 4
        or sorted(degrees.values()) != [1, 2, 2, 3]
    ):
        return PawOneLoopSupport(
            "UNSUPPORTED",
            data,
            simple_edges,
            core_edges,
            loop_class=loop_class,
            loop_vertex=loop_vertex,
            reason="loop deletion does not leave a paw core",
        )
    articulation = next(
        vertex for vertex, degree in degrees.items() if degree == 3
    )
    pendant = next(
        vertex for vertex, degree in degrees.items() if degree == 1
    )
    if loop_vertex == articulation:
        return PawOneLoopSupport(
            "UNSUPPORTED",
            data,
            simple_edges,
            core_edges,
            loop_class=loop_class,
            loop_vertex=loop_vertex,
            articulation=articulation,
            pendant=pendant,
            reason="loop is attached at the paw articulation",
        )
    return PawOneLoopSupport(
        "paw+1loop",
        data,
        simple_edges,
        core_edges,
        loop_class=loop_class,
        loop_vertex=loop_vertex,
        articulation=articulation,
        pendant=pendant,
    )


def _paw_core_slots(
    support: PawOneLoopSupport,
    paw_gap: int,
) -> list[list[int]]:
    data = support.data
    articulation = support.articulation
    pendant = support.pendant
    if articulation is None or pendant is None:
        raise ValueError("paw core slots require identified special vertices")
    triangle = tuple(
        vertex for vertex in base.GERMS if vertex != pendant
    )
    triangle_neighbors = {
        vertex: tuple(
            sorted(neighbor for neighbor in triangle if neighbor != vertex)
        )
        for vertex in triangle
    }
    triangle_degree_at_articulation = sum(
        len(data.class_edges[tuple(sorted((articulation, neighbor)))])
        for neighbor in triangle_neighbors[articulation]
    )
    if not 0 <= paw_gap < triangle_degree_at_articulation:
        raise ValueError("paw insertion gap is out of range")

    slots = base._empty_slots(data)
    for vertex in triangle:
        start = 0
        for neighbor in triangle_neighbors[vertex]:
            key = tuple(sorted((vertex, neighbor)))
            base._set_class_block(
                data,
                slots,
                key,
                vertex,
                start,
                reverse=vertex != key[0],
            )
            start += len(data.class_edges[key])

    pendant_class = tuple(sorted((articulation, pendant)))
    pendant_multiplicity = len(data.class_edges[pendant_class])
    for dart in data.vertex_darts[articulation]:
        if data.edge_class[data.edge_of_dart[dart]] == pendant_class:
            continue
        slots[dart][:] = [
            slot
            if slot < paw_gap
            else slot + pendant_multiplicity
            for slot in slots[dart]
        ]
    base._set_class_block(
        data,
        slots,
        pendant_class,
        articulation,
        paw_gap,
        reverse=articulation != pendant_class[0],
    )
    base._set_class_block(
        data,
        slots,
        pendant_class,
        pendant,
        0,
        reverse=pendant != pendant_class[0],
    )
    return slots


def paw_one_loop_embedding_schemes(
    support: PawOneLoopSupport,
) -> tuple[base.Scheme, ...]:
    if support.kind != "paw+1loop":
        return ()
    data = support.data
    loop_vertex = support.loop_vertex
    articulation = support.articulation
    pendant = support.pendant
    if (
        loop_vertex is None
        or articulation is None
        or pendant is None
    ):
        return ()
    triangle = tuple(
        vertex for vertex in base.GERMS if vertex != pendant
    )
    triangle_degree_at_articulation = sum(
        len(data.class_edges[tuple(sorted((articulation, neighbor)))])
        for neighbor in triangle
        if neighbor != articulation
    )
    loop_core_degree = len(data.vertex_darts[loop_vertex]) - 2
    if triangle_degree_at_articulation <= 0 or loop_core_degree <= 0:
        return ()

    schemes = []
    for paw_gap in range(triangle_degree_at_articulation):
        core_slots = _paw_core_slots(support, paw_gap)
        for loop_gap in range(loop_core_degree):
            for orientation in (0, 1):
                slots = _insert_loop(
                    support,
                    core_slots,
                    loop_gap,
                    orientation,
                )
                if not _verify_slot_partition(support, slots):
                    raise AssertionError(
                        "paw-loop scheme produced an invalid slot partition"
                    )
                schemes.append(
                    base.Scheme(
                        name=(
                            f"paw+1loop-paw-gap-{paw_gap}"
                            f"-loop-gap-{loop_gap}"
                            f"-orientation-{orientation}"
                        ),
                        support_kind=support.kind,
                        cut=paw_gap,
                        slots=tuple(map(tuple, slots)),
                        slot_partition_verified=True,
                    )
                )
    return tuple(schemes)


def _solution_signature(
    solution: base._ComponentSolution,
    class_keys: tuple[base.ClassKey, ...],
) -> tuple[int, ...]:
    masks = dict(solution.class_masks)
    return tuple(masks.get(key, 0) for key in class_keys)


def _first_by_signature(
    solutions: tuple[base._ComponentSolution, ...],
    class_keys: tuple[base.ClassKey, ...],
) -> dict[tuple[int, ...], base._ComponentSolution]:
    indexed = {}
    for solution in solutions:
        indexed.setdefault(
            _solution_signature(solution, class_keys),
            solution,
        )
    return indexed


def _combined_ranks(
    data: base.LinkData,
    left: base._ComponentSolution,
    right: base._ComponentSolution,
) -> tuple[int, ...]:
    assignments = dict(left.assignments)
    for edge, rank in right.assignments:
        if edge in assignments:
            raise AssertionError("constraint components share an A-edge")
        assignments[edge] = rank
    if set(assignments) != set(range(len(data.edge_darts))):
        raise AssertionError("component pair does not cover every A-edge")
    return tuple(
        assignments[edge] for edge in range(len(data.edge_darts))
    )


def _freeze_counters(
    values: dict[str, int],
    exhaustive: bool,
) -> PawSearchCounters:
    return PawSearchCounters(
        **{
            name: values[name]
            for name in PawSearchCounters.__dataclass_fields__
            if name != "exhaustive"
        },
        exhaustive=exhaustive,
    )


def solve_paw_one_loop_spherical(
    words: tuple[str, ...],
) -> base.RankDecision:
    words = tuple(words)
    support = classify_paw_one_loop_support(words)
    if support.kind == "UNSUPPORTED":
        return base.RankDecision(
            words,
            "UNSUPPORTED",
            None,
            support,
            None,
            PawSearchCounters(),
            reason=support.reason,
        )

    data = support.data
    schemes = paw_one_loop_embedding_schemes(support)
    constraints = base._constraints(data)
    components = base._constraint_components(
        len(data.edge_darts),
        constraints,
    )
    if len(components) != 2:
        raise AssertionError(
            "an exact two-relator dictionary must give two constraint cycles"
        )
    values = {
        field: 0
        for field in PawSearchCounters.__dataclass_fields__
        if field != "exhaustive"
    }
    nx = len(data.vertex_darts[base.G_X_POS])
    ny = len(data.vertex_darts[base.G_Y_POS])
    seed_budget_per_phase = sum(
        len(data.class_edges[data.edge_class[component[0][0]]])
        for component in components
    )
    values["scheme_budget"] = len(schemes)
    values["phase_pair_budget"] = len(schemes) * nx * ny
    values["component_seed_budget"] = (
        values["phase_pair_budget"] * seed_budget_per_phase
    )

    for scheme in schemes:
        values["schemes_considered"] += 1
        for phases in itertools.product(range(nx), range(ny)):
            values["phase_pairs_considered"] += 1
            per_component = []
            for component in components:
                seed_edge = component[0][0]
                seed_domain = len(
                    data.class_edges[data.edge_class[seed_edge]]
                )
                solutions = []
                for seed_rank in range(seed_domain):
                    values["component_seed_attempts"] += 1
                    solution, within_collision = base._propagate_component(
                        data,
                        scheme,
                        constraints,
                        component,
                        phases,
                        seed_rank,
                    )
                    if within_collision:
                        values[
                            "within_cycle_collision_rejections"
                        ] += 1
                    elif solution is not None:
                        values["closed_component_assignments"] += 1
                        solutions.append(solution)
                per_component.append(tuple(solutions))

            if any(not solutions for solutions in per_component):
                continue
            values["raw_component_combination_budget"] += math.prod(
                len(solutions) for solutions in per_component
            )
            class_keys = tuple(sorted(data.class_edges))
            full_signature = tuple(
                (1 << len(data.class_edges[key])) - 1
                for key in class_keys
            )
            left_index = _first_by_signature(
                per_component[0],
                class_keys,
            )
            right_index = _first_by_signature(
                per_component[1],
                class_keys,
            )
            values["left_signature_count"] += len(left_index)
            values["right_signature_count"] += len(right_index)
            for left_signature, left_solution in left_index.items():
                values["complement_lookups"] += 1
                required = tuple(
                    full ^ used
                    for full, used in zip(
                        full_signature,
                        left_signature,
                    )
                )
                right_solution = right_index.get(required)
                if right_solution is None:
                    continue
                values["compatible_signature_matches"] += 1
                ranks = _combined_ranks(
                    data,
                    left_solution,
                    right_solution,
                )
                witness = base._replay_witness(
                    data,
                    scheme,
                    constraints,
                    phases,
                    ranks,
                )
                if witness is None:
                    values["witness_replay_failures"] += 1
                    raise AssertionError(
                        "compatible complement masks failed witness replay"
                    )
                return base.RankDecision(
                    words,
                    "SPHERICAL",
                    True,
                    support,
                    witness,
                    _freeze_counters(values, exhaustive=False),
                )

    exhaustive = (
        values["schemes_considered"] == values["scheme_budget"]
        and values["phase_pairs_considered"] == values["phase_pair_budget"]
        and values["component_seed_attempts"]
        == values["component_seed_budget"]
    )
    if not exhaustive:
        raise AssertionError(
            "negative paw-loop search did not exhaust its finite budget"
        )
    return base.RankDecision(
        words,
        "NOT_SPHERICAL",
        False,
        support,
        None,
        _freeze_counters(values, exhaustive=True),
    )
