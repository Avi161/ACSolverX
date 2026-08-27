"""Numba-accelerated exact engine for the proved one-loop Neuwirth classes."""

from __future__ import annotations

import math
from dataclasses import asdict

import numpy as np
from numba import njit

from experiments.stable_ac.thickenable import neuwirth_rank_solver as base
from experiments.stable_ac.thickenable import neuwirth_one_loop_solver as loop

G_X_POS = 0
G_X_NEG = 1
G_Y_POS = 2
G_Y_NEG = 3


@njit(cache=True)
def _cyclic_b_reversal(rotation, degrees, B, positive, negative):
    degree = degrees[positive]
    if degree != degrees[negative]:
        return False
    if degree == 0:
        return True
    for shift in range(degree):
        good = True
        for index in range(degree):
            expected = B[rotation[positive, degree - 1 - index]]
            if expected != rotation[negative, (shift + index) % degree]:
                good = False
                break
        if good:
            return True
    return False


@njit(cache=True)
def _solve_scheme(
    slots,
    slot_lengths,
    edge_positive,
    edge_negative,
    dart_positive,
    dart_negative,
    phase_index,
    modulus,
    component_edge_offsets,
    component_edges,
    component_constraint_offsets,
    component_constraints,
    incident_offsets,
    incident_constraints,
    edge_class,
    class_multiplicity,
    A,
    B,
    germ,
    edge_of_dart,
    degrees,
):
    """Return (found, phase_x, phase_y, ranks, ten exact counters)."""
    edge_count = len(edge_class)
    dart_count = len(A)
    component_count = len(component_edge_offsets) - 1
    class_count = len(class_multiplicity)
    max_rank = slots.shape[1]
    max_degree = slots.shape[0]

    # phase pairs, seeds, closed, within, combination budget/considered,
    # cross collision, union checks/rejections, replay failures
    counters = np.zeros(10, dtype=np.int64)
    assignments = np.full(edge_count, -1, dtype=np.int64)
    queue = np.empty(edge_count, dtype=np.int64)
    solutions = np.full(
        (component_count, max_rank, edge_count), -1, dtype=np.int64
    )
    solution_counts = np.zeros(component_count, dtype=np.int64)
    used = np.zeros((class_count, max_rank), dtype=np.uint8)
    ranks = np.full(edge_count, -1, dtype=np.int64)
    result_ranks = np.full(edge_count, -1, dtype=np.int64)
    rotation = np.full((4, max_degree), -1, dtype=np.int64)
    sigma = np.full(dart_count, -1, dtype=np.int64)
    phi = np.full(dart_count, -1, dtype=np.int64)
    seen = np.zeros(dart_count, dtype=np.uint8)

    for phase_x in range(degrees[G_X_POS]):
        for phase_y in range(degrees[G_Y_POS]):
            counters[0] += 1
            phase_values = (phase_x, phase_y)
            all_components_live = True
            for component in range(component_count):
                solution_counts[component] = 0
                edge_start = component_edge_offsets[component]
                edge_stop = component_edge_offsets[component + 1]
                seed_edge = component_edges[edge_start]
                seed_domain = class_multiplicity[edge_class[seed_edge]]
                constraint_start = component_constraint_offsets[component]
                constraint_stop = component_constraint_offsets[component + 1]

                for seed_rank in range(seed_domain):
                    counters[1] += 1
                    assignments[:] = -1
                    assignments[seed_edge] = seed_rank
                    queue[0] = seed_edge
                    queue_head = 0
                    queue_stop = 1
                    valid = True
                    while queue_head < queue_stop and valid:
                        edge = queue[queue_head]
                        queue_head += 1
                        for incident_index in range(
                            incident_offsets[edge], incident_offsets[edge + 1]
                        ):
                            constraint = incident_constraints[incident_index]
                            left = edge_positive[constraint]
                            right = edge_negative[constraint]
                            phase = phase_values[phase_index[constraint]]
                            mod = modulus[constraint]
                            target = -1
                            required = -1
                            target_dart = -1
                            if assignments[left] >= 0 and assignments[right] < 0:
                                target = right
                                required = (
                                    -phase
                                    - slots[
                                        dart_positive[constraint],
                                        assignments[left],
                                    ]
                                ) % mod
                                target_dart = dart_negative[constraint]
                            elif assignments[right] >= 0 and assignments[left] < 0:
                                target = left
                                required = (
                                    -phase
                                    - slots[
                                        dart_negative[constraint],
                                        assignments[right],
                                    ]
                                ) % mod
                                target_dart = dart_positive[constraint]
                            if target >= 0:
                                inverse = -1
                                for rank in range(slot_lengths[target_dart]):
                                    if slots[target_dart, rank] == required:
                                        if inverse >= 0:
                                            return (
                                                -2,
                                                phase_x,
                                                phase_y,
                                                result_ranks,
                                                counters,
                                            )
                                        inverse = rank
                                if inverse < 0:
                                    valid = False
                                    break
                                assignments[target] = inverse
                                queue[queue_stop] = target
                                queue_stop += 1

                    if not valid:
                        continue
                    for position in range(edge_start, edge_stop):
                        if assignments[component_edges[position]] < 0:
                            return (
                                -3,
                                phase_x,
                                phase_y,
                                result_ranks,
                                counters,
                            )
                    for position in range(constraint_start, constraint_stop):
                        constraint = component_constraints[position]
                        equation = (
                            slots[
                                dart_positive[constraint],
                                assignments[edge_positive[constraint]],
                            ]
                            + slots[
                                dart_negative[constraint],
                                assignments[edge_negative[constraint]],
                            ]
                            + phase_values[phase_index[constraint]]
                        ) % modulus[constraint]
                        if equation:
                            valid = False
                            break
                    if not valid:
                        continue

                    used[:, :] = 0
                    collision = False
                    for position in range(edge_start, edge_stop):
                        edge = component_edges[position]
                        class_id = edge_class[edge]
                        rank = assignments[edge]
                        if used[class_id, rank]:
                            collision = True
                            break
                        used[class_id, rank] = 1
                    if collision:
                        counters[3] += 1
                        continue
                    counters[2] += 1
                    solution_index = solution_counts[component]
                    for position in range(edge_start, edge_stop):
                        edge = component_edges[position]
                        solutions[component, solution_index, edge] = assignments[edge]
                    solution_counts[component] += 1

                if solution_counts[component] == 0:
                    all_components_live = False

            if not all_components_live:
                continue

            product = 1
            for component in range(component_count):
                product *= solution_counts[component]
            counters[4] += product
            for combination in range(product):
                counters[5] += 1
                used[:, :] = 0
                ranks[:] = -1
                remainder = combination
                choices = np.empty(component_count, dtype=np.int64)
                for component in range(component_count - 1, -1, -1):
                    choices[component] = remainder % solution_counts[component]
                    remainder //= solution_counts[component]
                collision = False
                for component in range(component_count):
                    edge_start = component_edge_offsets[component]
                    edge_stop = component_edge_offsets[component + 1]
                    choice = choices[component]
                    for position in range(edge_start, edge_stop):
                        edge = component_edges[position]
                        rank = solutions[component, choice, edge]
                        class_id = edge_class[edge]
                        if used[class_id, rank]:
                            collision = True
                        used[class_id, rank] = 1
                        ranks[edge] = rank
                if collision:
                    counters[6] += 1
                    continue
                counters[7] += 1
                complete = True
                for class_id in range(class_count):
                    for rank in range(class_multiplicity[class_id]):
                        if not used[class_id, rank]:
                            complete = False
                for edge in range(edge_count):
                    if ranks[edge] < 0:
                        complete = False
                if not complete:
                    counters[8] += 1
                    continue

                rotation[:, :] = -1
                replay_ok = True
                for dart in range(dart_count):
                    vertex = germ[dart]
                    slot = slots[dart, ranks[edge_of_dart[dart]]]
                    if slot < 0 or slot >= degrees[vertex]:
                        replay_ok = False
                    elif rotation[vertex, slot] >= 0:
                        replay_ok = False
                    else:
                        rotation[vertex, slot] = dart
                for vertex in range(4):
                    for slot in range(degrees[vertex]):
                        if rotation[vertex, slot] < 0:
                            replay_ok = False
                    if replay_ok:
                        for slot in range(degrees[vertex]):
                            sigma[rotation[vertex, slot]] = rotation[
                                vertex, (slot + 1) % degrees[vertex]
                            ]
                if replay_ok:
                    replay_ok = _cyclic_b_reversal(
                        rotation, degrees, B, G_X_POS, G_X_NEG
                    ) and _cyclic_b_reversal(
                        rotation, degrees, B, G_Y_POS, G_Y_NEG
                    )
                if replay_ok:
                    for dart in range(dart_count):
                        phi[dart] = sigma[A[dart]]
                    seen[:] = 0
                    faces = 0
                    for start in range(dart_count):
                        if seen[start]:
                            continue
                        faces += 1
                        dart = start
                        while not seen[dart]:
                            seen[dart] = 1
                            dart = phi[dart]
                        if dart != start:
                            replay_ok = False
                            break
                    if 4 - edge_count + faces != 2:
                        replay_ok = False
                if not replay_ok:
                    counters[9] += 1
                    continue
                result_ranks[:] = ranks
                return 1, phase_x, phase_y, result_ranks, counters

    return 0, -1, -1, result_ranks, counters


def _arrays(data, scheme, components, constraints):
    edge_count = len(data.edge_darts)
    class_keys = tuple(sorted(data.class_edges))
    class_index = {key: index for index, key in enumerate(class_keys)}
    edge_class = np.array(
        [class_index[key] for key in data.edge_class], dtype=np.int64
    )
    class_multiplicity = np.array(
        [len(data.class_edges[key]) for key in class_keys], dtype=np.int64
    )
    max_rank = int(class_multiplicity.max())
    slots = np.full((len(data.A), max_rank), -1, dtype=np.int64)
    slot_lengths = np.empty(len(data.A), dtype=np.int64)
    for dart, image in enumerate(scheme.slots):
        slot_lengths[dart] = len(image)
        slots[dart, : len(image)] = image

    fields = (
        "edge_positive",
        "edge_negative",
        "dart_positive",
        "dart_negative",
        "phase_index",
        "modulus",
    )
    constraint_arrays = tuple(
        np.array([getattr(item, field) for item in constraints], dtype=np.int64)
        for field in fields
    )
    component_edge_offsets = [0]
    component_edges = []
    component_constraint_offsets = [0]
    component_constraints = []
    for edges, indices in components:
        component_edges.extend(edges)
        component_edge_offsets.append(len(component_edges))
        component_constraints.extend(indices)
        component_constraint_offsets.append(len(component_constraints))

    incident = [[] for _ in range(edge_count)]
    for index, constraint in enumerate(constraints):
        incident[constraint.edge_positive].append(index)
        incident[constraint.edge_negative].append(index)
    incident_offsets = [0]
    incident_constraints = []
    for indices in incident:
        incident_constraints.extend(indices)
        incident_offsets.append(len(incident_constraints))

    degrees = np.array(
        [len(data.vertex_darts[vertex]) for vertex in base.GERMS],
        dtype=np.int64,
    )
    return (
        slots,
        slot_lengths,
        *constraint_arrays,
        np.array(component_edge_offsets, dtype=np.int64),
        np.array(component_edges, dtype=np.int64),
        np.array(component_constraint_offsets, dtype=np.int64),
        np.array(component_constraints, dtype=np.int64),
        np.array(incident_offsets, dtype=np.int64),
        np.array(incident_constraints, dtype=np.int64),
        edge_class,
        class_multiplicity,
        np.array(data.A, dtype=np.int64),
        np.array(data.B, dtype=np.int64),
        np.array(data.germ, dtype=np.int64),
        np.array(data.edge_of_dart, dtype=np.int64),
        degrees,
    )


def _schemes(support):
    data = support.data
    loop_class = support.loop_class
    loop_vertex = loop_class[0]
    core_degree = len(data.vertex_darts[loop_vertex]) - 2
    if support.kind == "K4+1loop":
        core_schemes = ((None, loop._k4_core_slots(support)),)
    else:
        c, d = support.missing_edge
        poles = tuple(vertex for vertex in base.GERMS if vertex not in (c, d))
        central = tuple(sorted(poles))
        core_schemes = (
            (cut, loop._k4_minus_edge_core_slots(support, cut))
            for cut in range(len(data.class_edges[central]) + 1)
        )
    for cut, core_slots in core_schemes:
        for gap in range(core_degree):
            for orientation in (0, 1):
                slots = loop._insert_loop(
                    support, core_slots, gap, orientation
                )
                if not loop._verify_slot_partition(support, slots):
                    raise AssertionError("invalid one-loop slot partition")
                yield base.Scheme(
                    name=(
                        f"{support.kind}-cut-{cut}-gap-{gap}"
                        f"-orientation-{orientation}"
                    ),
                    support_kind=support.kind,
                    cut=cut,
                    slots=tuple(map(tuple, slots)),
                    slot_partition_verified=True,
                )


def solve_one_loop_spherical_fast(words):
    words = tuple(words)
    support = loop.classify_one_loop_support(words)
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
    constraints = base._constraints(data)
    components = base._constraint_components(len(data.edge_darts), constraints)
    loop_vertex = support.loop_class[0]
    core_degree = len(data.vertex_darts[loop_vertex]) - 2
    if support.kind == "K4+1loop":
        scheme_budget = 2 * core_degree
    else:
        c, d = support.missing_edge
        poles = tuple(vertex for vertex in base.GERMS if vertex not in (c, d))
        central = tuple(sorted(poles))
        scheme_budget = (
            2 * core_degree * (len(data.class_edges[central]) + 1)
        )
    nx = len(data.vertex_darts[base.G_X_POS])
    ny = len(data.vertex_darts[base.G_Y_POS])
    seed_budget_per_phase = sum(
        len(data.class_edges[data.edge_class[component[0][0]]])
        for component in components
    )
    values = {
        "scheme_budget": scheme_budget,
        "schemes_considered": 0,
        "phase_pair_budget": scheme_budget * nx * ny,
        "phase_pairs_considered": 0,
        "component_seed_budget": (
            scheme_budget * nx * ny * seed_budget_per_phase
        ),
        "component_seed_attempts": 0,
        "closed_component_assignments": 0,
        "within_cycle_collision_rejections": 0,
        "component_combination_budget": 0,
        "component_combinations_considered": 0,
        "cross_cycle_collision_rejections": 0,
        "union_cardinality_checks": 0,
        "union_cardinality_rejections": 0,
        "witness_replay_failures": 0,
    }
    counter_names = (
        "phase_pairs_considered",
        "component_seed_attempts",
        "closed_component_assignments",
        "within_cycle_collision_rejections",
        "component_combination_budget",
        "component_combinations_considered",
        "cross_cycle_collision_rejections",
        "union_cardinality_checks",
        "union_cardinality_rejections",
        "witness_replay_failures",
    )
    for scheme in _schemes(support):
        values["schemes_considered"] += 1
        found, phase_x, phase_y, ranks_array, counters = _solve_scheme(
            *_arrays(data, scheme, components, constraints)
        )
        if found < 0:
            raise AssertionError(f"accelerated solver invariant failure {found}")
        for name, value in zip(counter_names, counters):
            values[name] += int(value)
        if found:
            ranks = tuple(map(int, ranks_array))
            phases = (int(phase_x), int(phase_y))
            witness = base._replay_witness(
                data, scheme, constraints, phases, ranks
            )
            if witness is None:
                raise AssertionError("accelerated witness failed exact replay")
            return base.RankDecision(
                words,
                "SPHERICAL",
                True,
                support,
                witness,
                base._frozen_counters(values, exhaustive=False),
            )
    return base.RankDecision(
        words,
        "NOT_SPHERICAL",
        False,
        support,
        None,
        base._frozen_counters(values, exhaustive=True),
    )
