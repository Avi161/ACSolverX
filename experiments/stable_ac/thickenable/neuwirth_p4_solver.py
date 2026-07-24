"""Exact signed-rank extension for four-germ path support.

The existing rank solver remains the authority for K4, K4-e, and C4.  This
module adds only the P4 central-gap schemes proved in
``AK3_P4_SYNCHRONIZED_PLANARITY.md`` and otherwise fails closed.
"""

from __future__ import annotations

import itertools
import math

from experiments.stable_ac.thickenable import neuwirth_rank_solver as base


def _p4_support(
    support: base.SupportClass,
) -> tuple[base.SupportClass, tuple[int, int, int, int]] | None:
    if any(left == right for left, right in support.simple_edges):
        return None
    adjacency = {vertex: set() for vertex in base.GERMS}
    for left, right in support.simple_edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    if len(support.simple_edges) != 3:
        return None
    if sorted(map(len, adjacency.values())) != [1, 1, 2, 2]:
        return None

    internal = tuple(
        sorted(vertex for vertex in base.GERMS if len(adjacency[vertex]) == 2)
    )
    if len(internal) != 2 or internal[1] not in adjacency[internal[0]]:
        return None
    middle_left, middle_right = internal
    left_leaf = next(iter(adjacency[middle_left] - {middle_right}))
    right_leaf = next(iter(adjacency[middle_right] - {middle_left}))
    path = (left_leaf, middle_left, middle_right, right_leaf)
    return (
        base.SupportClass(
            "P4",
            support.data,
            support.simple_edges,
        ),
        path,
    )


def classify_four_germ_support(words: tuple[str, ...]) -> base.SupportClass:
    """Return the existing support classes plus proved connected loopless P4."""
    support = base.classify_support(tuple(words))
    if support.kind != "UNSUPPORTED":
        return support
    recognized = _p4_support(support)
    return recognized[0] if recognized is not None else support


def p4_embedding_schemes(
    support: base.SupportClass,
) -> tuple[base.Scheme, ...]:
    """Enumerate the relative central-bundle gap, not edge permutations."""
    recognized = _p4_support(support)
    if support.kind == "P4":
        adjacency = {vertex: set() for vertex in base.GERMS}
        for left, right in support.simple_edges:
            adjacency[left].add(right)
            adjacency[right].add(left)
        internal = tuple(
            sorted(
                vertex
                for vertex in base.GERMS
                if len(adjacency[vertex]) == 2
            )
        )
        if len(internal) != 2 or internal[1] not in adjacency[internal[0]]:
            return ()
        middle_left, middle_right = internal
        path = (
            next(iter(adjacency[middle_left] - {middle_right})),
            middle_left,
            middle_right,
            next(iter(adjacency[middle_right] - {middle_left})),
        )
        p4 = support
    elif recognized is not None:
        p4, path = recognized
    else:
        return ()

    left_leaf, middle_left, middle_right, right_leaf = path
    neighbor_orders = {
        left_leaf: (middle_left,),
        middle_left: (left_leaf, middle_right),
        middle_right: (middle_left, right_leaf),
        right_leaf: (middle_right,),
    }
    unshifted = base._block_scheme(
        p4,
        "P4-central-shift-0",
        neighbor_orders,
    )
    central = tuple(sorted((middle_left, middle_right)))
    multiplicity = len(p4.data.class_edges[central])
    schemes = []
    for shift in range(multiplicity):
        slots = [list(row) for row in unshifted.slots]
        for edge in p4.data.class_edges[central]:
            dart = base._dart_for_edge_at(p4.data, edge, middle_right)
            start = min(slots[dart])
            slots[dart][:] = [
                start + ((slot - start + shift) % multiplicity)
                for slot in slots[dart]
            ]
        verified = base._verify_slot_partition(p4.data, slots)
        schemes.append(
            base.Scheme(
                name=f"P4-central-shift-{shift}",
                support_kind="P4",
                cut=shift,
                slots=tuple(map(tuple, slots)),
                slot_partition_verified=verified,
            )
        )
    if not all(scheme.slot_partition_verified for scheme in schemes):
        raise AssertionError("P4 scheme produced an invalid slot partition")
    return tuple(schemes)


def _solve_p4(
    words: tuple[str, ...],
    support: base.SupportClass,
) -> base.RankDecision:
    data = support.data
    schemes = p4_embedding_schemes(support)
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
                        values["within_cycle_collision_rejections"] += 1
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
        raise AssertionError("negative P4 search did not exhaust its finite budget")
    return base.RankDecision(
        words,
        "NOT_SPHERICAL",
        False,
        support,
        None,
        base._frozen_counters(values, exhaustive=True),
    )


def solve_four_germ_spherical(
    words: tuple[str, ...],
) -> base.RankDecision:
    """Decide the four proved support types and fail closed on every other one."""
    words = tuple(words)
    existing = base.solve_spherical(words)
    if existing.spherical is not None:
        return existing
    recognized = _p4_support(existing.support)
    if recognized is None:
        return existing
    support, _ = recognized
    return _solve_p4(words, support)
