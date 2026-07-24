"""Exact signed-rank solver for one-loop four-germ Neuwirth links.

Only a single loop edge over a positive parallel K4 or K4-e core is
decided.  Every other support fails closed.
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass

from experiments.stable_ac.thickenable import neuwirth_rank_solver as base


@dataclass(frozen=True)
class OneLoopSupport:
    kind: str
    data: base.LinkData
    simple_edges: frozenset[base.ClassKey]
    core_edges: frozenset[base.ClassKey]
    loop_class: base.ClassKey | None = None
    missing_edge: base.ClassKey | None = None
    reason: str | None = None


def classify_one_loop_support(words: tuple[str, ...]) -> OneLoopSupport:
    data = base._build_link_data(tuple(words))
    simple_edges = frozenset(data.class_edges)
    loop_classes = tuple(
        sorted(key for key in simple_edges if key[0] == key[1])
    )
    core_edges = frozenset(
        key for key in simple_edges if key[0] != key[1]
    )
    if len(loop_classes) != 1:
        return OneLoopSupport(
            "UNSUPPORTED",
            data,
            simple_edges,
            core_edges,
            reason="support must have exactly one loop class",
        )
    loop_class = loop_classes[0]
    if len(data.class_edges[loop_class]) != 1:
        return OneLoopSupport(
            "UNSUPPORTED",
            data,
            simple_edges,
            core_edges,
            loop_class=loop_class,
            reason="the loop class must contain exactly one edge",
        )

    adjacency = {vertex: set() for vertex in base.GERMS}
    for left, right in core_edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    degrees = sorted(len(adjacency[vertex]) for vertex in base.GERMS)
    all_edges = frozenset(
        (left, right)
        for left in base.GERMS
        for right in base.GERMS
        if left < right
    )
    if len(core_edges) == 6:
        return OneLoopSupport(
            "K4+1loop",
            data,
            simple_edges,
            core_edges,
            loop_class=loop_class,
        )
    if len(core_edges) == 5 and degrees == [2, 2, 3, 3]:
        (missing_edge,) = all_edges - core_edges
        return OneLoopSupport(
            "K4-e+1loop",
            data,
            simple_edges,
            core_edges,
            loop_class=loop_class,
            missing_edge=missing_edge,
        )
    return OneLoopSupport(
        "UNSUPPORTED",
        data,
        simple_edges,
        core_edges,
        loop_class=loop_class,
        reason="loop deletion does not leave a K4 or K4-e core",
    )


def _k4_core_slots(support: OneLoopSupport) -> list[list[int]]:
    data = support.data
    slots = base._empty_slots(data)
    neighbor_orders = {
        0: (1, 2, 3),
        1: (0, 3, 2),
        2: (0, 1, 3),
        3: (0, 2, 1),
    }
    for vertex in base.GERMS:
        start = 0
        for neighbor in neighbor_orders[vertex]:
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
    return slots


def _k4_minus_edge_core_slots(
    support: OneLoopSupport,
    cut: int,
) -> list[list[int]]:
    data = support.data
    c, d = support.missing_edge or (-1, -1)
    poles = tuple(vertex for vertex in base.GERMS if vertex not in (c, d))
    if len(poles) != 2:
        raise AssertionError("K4-e core must have two poles")
    a, b = poles
    central = tuple(sorted((a, b)))
    ac = tuple(sorted((a, c)))
    ad = tuple(sorted((a, d)))
    bc = tuple(sorted((b, c)))
    bd = tuple(sorted((b, d)))
    m = len(data.class_edges[central])
    if not 0 <= cut <= m:
        raise ValueError("central cut is out of range")

    slots = base._empty_slots(data)
    mac = len(data.class_edges[ac])
    mad = len(data.class_edges[ad])
    mbc = len(data.class_edges[bc])
    mbd = len(data.class_edges[bd])

    base._set_class_block(data, slots, ac, a, 0, False)
    base._set_class_block(data, slots, ad, a, mac + cut, False)
    for edge in data.class_edges[central]:
        dart = base._dart_for_edge_at(data, edge, a)
        slots[dart][:] = [
            mac + rank if rank < cut else mac + mad + rank
            for rank in range(m)
        ]

    base._set_class_block(data, slots, bc, b, 0, False)
    base._set_class_block(data, slots, bd, b, mbc + (m - cut), False)
    for edge in data.class_edges[central]:
        dart = base._dart_for_edge_at(data, edge, b)
        slots[dart][:] = [
            mbc + (m - 1 - rank)
            if rank >= cut
            else mbc + (m - cut) + mbd + (cut - 1 - rank)
            for rank in range(m)
        ]

    base._set_class_block(data, slots, ac, c, 0, True)
    base._set_class_block(data, slots, bc, c, mac, True)
    base._set_class_block(data, slots, ad, d, 0, True)
    base._set_class_block(data, slots, bd, d, mad, True)
    return slots


def _verify_slot_partition(
    support: OneLoopSupport,
    slots: list[list[int]],
) -> bool:
    data = support.data
    loop_class = support.loop_class
    if loop_class is None:
        return False
    loop_edge = data.class_edges[loop_class][0]
    loop_darts = data.edge_darts[loop_edge]
    loop_vertex = loop_class[0]
    for vertex in base.GERMS:
        images = []
        for key, edges in data.class_edges.items():
            if key == loop_class:
                if vertex == loop_vertex:
                    for dart in loop_darts:
                        images.extend(slots[dart])
                continue
            if vertex not in key:
                continue
            dart = base._dart_for_edge_at(data, edges[0], vertex)
            image = slots[dart]
            if len(set(image)) != len(image):
                return False
            images.extend(image)
        if sorted(images) != list(range(len(data.vertex_darts[vertex]))):
            return False
    return all(all(slot >= 0 for slot in image) for image in slots)


def _insert_loop(
    support: OneLoopSupport,
    core_slots: list[list[int]],
    gap: int,
    orientation: int,
) -> list[list[int]]:
    data = support.data
    loop_class = support.loop_class
    if loop_class is None:
        raise ValueError("loop insertion requires a loop class")
    loop_vertex = loop_class[0]
    loop_edge = data.class_edges[loop_class][0]
    loop_darts = data.edge_darts[loop_edge]
    core_degree = len(data.vertex_darts[loop_vertex]) - 2
    if not 0 <= gap < core_degree:
        raise ValueError("loop gap is out of range")
    if orientation not in (0, 1):
        raise ValueError("loop orientation must be zero or one")

    slots = [list(image) for image in core_slots]
    for dart in data.vertex_darts[loop_vertex]:
        if dart in loop_darts:
            continue
        slots[dart][:] = [
            slot if slot < gap else slot + 2 for slot in slots[dart]
        ]
    ordered_darts = (
        loop_darts if orientation == 0 else tuple(reversed(loop_darts))
    )
    slots[ordered_darts[0]][:] = [gap]
    slots[ordered_darts[1]][:] = [gap + 1]
    return slots


def loop_embedding_schemes(
    support: OneLoopSupport,
) -> tuple[base.Scheme, ...]:
    if support.kind not in ("K4+1loop", "K4-e+1loop"):
        return ()
    loop_class = support.loop_class
    if loop_class is None:
        return ()
    data = support.data
    loop_vertex = loop_class[0]
    core_degree = len(data.vertex_darts[loop_vertex]) - 2
    if core_degree <= 0:
        return ()

    if support.kind == "K4+1loop":
        core_schemes = ((None, _k4_core_slots(support)),)
    else:
        c, d = support.missing_edge or (-1, -1)
        poles = tuple(
            vertex for vertex in base.GERMS if vertex not in (c, d)
        )
        central = tuple(sorted(poles))
        multiplicity = len(data.class_edges[central])
        core_schemes = tuple(
            (cut, _k4_minus_edge_core_slots(support, cut))
            for cut in range(multiplicity + 1)
        )

    schemes = []
    for cut, core_slots in core_schemes:
        for gap in range(core_degree):
            for orientation in (0, 1):
                slots = _insert_loop(
                    support,
                    core_slots,
                    gap,
                    orientation,
                )
                verified = _verify_slot_partition(support, slots)
                if not verified:
                    raise AssertionError(
                        "one-loop scheme produced an invalid slot partition"
                    )
                schemes.append(
                    base.Scheme(
                        name=(
                            f"{support.kind}-cut-{cut}-gap-{gap}"
                            f"-orientation-{orientation}"
                        ),
                        support_kind=support.kind,
                        cut=cut,
                        slots=tuple(map(tuple, slots)),
                        slot_partition_verified=True,
                    )
                )
    return tuple(schemes)


def solve_one_loop_spherical(
    words: tuple[str, ...],
) -> base.RankDecision:
    words = tuple(words)
    support = classify_one_loop_support(words)
    if support.kind == "UNSUPPORTED":
        return base.RankDecision(
            words,
            "UNSUPPORTED",
            None,
            support,
            None,
            base.SearchCounters(),
            reason=support.reason,
        )

    data = support.data
    schemes = loop_embedding_schemes(support)
    constraints = base._constraints(data)
    components = base._constraint_components(
        len(data.edge_darts),
        constraints,
    )
    values = {
        field: 0
        for field in (
            "schemes_considered",
            "scheme_budget",
            "phase_pairs_considered",
            "phase_pair_budget",
            "component_seed_attempts",
            "component_seed_budget",
            "closed_component_assignments",
            "within_cycle_collision_rejections",
            "component_combination_budget",
            "component_combinations_considered",
            "cross_cycle_collision_rejections",
            "union_cardinality_checks",
            "union_cardinality_rejections",
            "witness_replay_failures",
        )
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
            values["component_combination_budget"] += math.prod(
                len(solutions) for solutions in per_component
            )
            for combination in itertools.product(*per_component):
                values["component_combinations_considered"] += 1
                assignments: dict[int, int] = {}
                masks: dict[base.ClassKey, int] = {}
                collision = False
                for solution in combination:
                    for edge, rank in solution.assignments:
                        if edge in assignments and assignments[edge] != rank:
                            raise AssertionError(
                                "constraint components share an A-edge"
                            )
                        assignments[edge] = rank
                    for key, mask in solution.class_masks:
                        if masks.get(key, 0) & mask:
                            collision = True
                        masks[key] = masks.get(key, 0) | mask
                if collision:
                    values["cross_cycle_collision_rejections"] += 1
                    continue
                values["union_cardinality_checks"] += 1
                if any(
                    masks.get(key, 0).bit_count() != len(edges)
                    for key, edges in data.class_edges.items()
                ):
                    values["union_cardinality_rejections"] += 1
                    continue
                if set(assignments) != set(range(len(data.edge_darts))):
                    values["union_cardinality_rejections"] += 1
                    continue
                ranks = tuple(
                    assignments[edge]
                    for edge in range(len(data.edge_darts))
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
                    continue
                return base.RankDecision(
                    words,
                    "SPHERICAL",
                    True,
                    support,
                    witness,
                    base._frozen_counters(values, exhaustive=False),
                )

    exhaustive = (
        values["schemes_considered"] == values["scheme_budget"]
        and values["phase_pairs_considered"] == values["phase_pair_budget"]
        and values["component_seed_attempts"]
        == values["component_seed_budget"]
        and values["component_combinations_considered"]
        == values["component_combination_budget"]
    )
    if not exhaustive:
        raise AssertionError(
            "negative one-loop search did not exhaust its finite budget"
        )
    return base.RankDecision(
        words,
        "NOT_SPHERICAL",
        False,
        support,
        None,
        base._frozen_counters(values, exhaustive=True),
    )
