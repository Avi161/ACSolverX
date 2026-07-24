"""Exact signed-rank solver for the four-germ Neuwirth link.

This module implements only the connected loopless K4, K4-e, and C4
classifications proved in ``AK3_SYNCHRONIZED_PLANARITY.md``.  Exact relator
words are parsed occurrence by occurrence; no word reduction is performed.
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass
from typing import Mapping


G_X_POS = 0
G_X_NEG = 1
G_Y_POS = 2
G_Y_NEG = 3
GERMS = (G_X_POS, G_X_NEG, G_Y_POS, G_Y_NEG)

ClassKey = tuple[int, int]


@dataclass(frozen=True)
class LinkData:
    words: tuple[str, ...]
    A: tuple[int, ...]
    B: tuple[int, ...]
    germ: tuple[int, ...]
    edge_of_dart: tuple[int, ...]
    edge_darts: tuple[tuple[int, int], ...]
    edge_class: tuple[ClassKey, ...]
    class_edges: Mapping[ClassKey, tuple[int, ...]]
    vertex_darts: Mapping[int, tuple[int, ...]]


@dataclass(frozen=True)
class SupportClass:
    kind: str
    data: LinkData
    simple_edges: frozenset[ClassKey]
    missing_edge: ClassKey | None = None
    reason: str | None = None


@dataclass(frozen=True)
class Scheme:
    name: str
    support_kind: str
    cut: int | None
    slots: tuple[tuple[int, ...], ...]
    slot_partition_verified: bool


@dataclass(frozen=True)
class SearchCounters:
    scheme_budget: int = 0
    schemes_considered: int = 0
    phase_pair_budget: int = 0
    phase_pairs_considered: int = 0
    component_seed_budget: int = 0
    component_seed_attempts: int = 0
    closed_component_assignments: int = 0
    within_cycle_collision_rejections: int = 0
    component_combination_budget: int = 0
    component_combinations_considered: int = 0
    cross_cycle_collision_rejections: int = 0
    union_cardinality_checks: int = 0
    union_cardinality_rejections: int = 0
    witness_replay_failures: int = 0
    exhaustive: bool = False


@dataclass(frozen=True)
class RankWitness:
    scheme: str
    cut: int | None
    phases: tuple[int, int]
    ranks: tuple[int, ...]
    rotations: tuple[tuple[int, ...], ...]
    faces: tuple[tuple[int, ...], ...]
    face_count: int
    euler_characteristic: int
    genus: int
    b_reversal_verified: bool
    rank_partition_verified: bool
    phase_equations_verified: bool


@dataclass(frozen=True)
class RankDecision:
    words: tuple[str, ...]
    verdict: str
    spherical: bool | None
    support: SupportClass
    witness: RankWitness | None
    counters: SearchCounters
    reason: str | None = None


@dataclass(frozen=True)
class _Constraint:
    edge_positive: int
    edge_negative: int
    dart_positive: int
    dart_negative: int
    phase_index: int
    modulus: int


@dataclass(frozen=True)
class _ComponentSolution:
    assignments: tuple[tuple[int, int], ...]
    class_masks: tuple[tuple[ClassKey, int], ...]


def _letter_germs(letter: str) -> tuple[int, int]:
    try:
        return {
            "x": (G_X_POS, G_X_NEG),
            "X": (G_X_NEG, G_X_POS),
            "y": (G_Y_POS, G_Y_NEG),
            "Y": (G_Y_NEG, G_Y_POS),
        }[letter]
    except KeyError as exc:
        raise ValueError(f"unsupported letter {letter!r}") from exc


def _build_link_data(words: tuple[str, ...]) -> LinkData:
    words = tuple(words)
    if not words or any(not word for word in words):
        raise ValueError("at least one nonempty relator is required")

    occurrence_count = sum(map(len, words))
    dart_count = 2 * occurrence_count
    A = [-1] * dart_count
    B = [-1] * dart_count
    germ = [-1] * dart_count
    offset = 0
    for word in words:
        occurrence_ids = tuple(range(offset, offset + len(word)))
        for local_index, occurrence in enumerate(occurrence_ids):
            letter = word[local_index]
            departure = 2 * occurrence
            arrival = departure + 1
            departure_germ, arrival_germ = _letter_germs(letter)
            germ[departure] = departure_germ
            germ[arrival] = arrival_germ
            B[departure] = arrival
            B[arrival] = departure

            next_occurrence = occurrence_ids[(local_index + 1) % len(word)]
            next_departure = 2 * next_occurrence
            A[arrival] = next_departure
            A[next_departure] = arrival
        offset += len(word)

    if any(value < 0 for value in A + B + germ):
        raise AssertionError("incomplete exact occurrence dictionary")

    edge_of_dart = [-1] * dart_count
    edge_darts: list[tuple[int, int]] = []
    edge_class: list[ClassKey] = []
    class_edges_lists: dict[ClassKey, list[int]] = {}
    for dart, mate in enumerate(A):
        if dart > mate:
            continue
        edge = len(edge_darts)
        edge_darts.append((dart, mate))
        edge_of_dart[dart] = edge
        edge_of_dart[mate] = edge
        key = tuple(sorted((germ[dart], germ[mate])))
        edge_class.append(key)
        class_edges_lists.setdefault(key, []).append(edge)

    vertex_darts = {
        vertex: tuple(dart for dart, at in enumerate(germ) if at == vertex)
        for vertex in GERMS
    }
    return LinkData(
        words=words,
        A=tuple(A),
        B=tuple(B),
        germ=tuple(germ),
        edge_of_dart=tuple(edge_of_dart),
        edge_darts=tuple(edge_darts),
        edge_class=tuple(edge_class),
        class_edges={
            key: tuple(edges) for key, edges in sorted(class_edges_lists.items())
        },
        vertex_darts=vertex_darts,
    )


def classify_support(words: tuple[str, ...]) -> SupportClass:
    data = _build_link_data(tuple(words))
    simple_edges = frozenset(data.class_edges)
    if any(u == v for u, v in simple_edges):
        return SupportClass(
            "UNSUPPORTED", data, simple_edges, reason="A-link contains a loop"
        )

    adjacency = {vertex: set() for vertex in GERMS}
    for u, v in simple_edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    reached = {GERMS[0]}
    frontier = [GERMS[0]]
    while frontier:
        vertex = frontier.pop()
        new_vertices = adjacency[vertex] - reached
        reached.update(new_vertices)
        frontier.extend(new_vertices)
    if reached != set(GERMS):
        return SupportClass(
            "UNSUPPORTED", data, simple_edges, reason="support is disconnected"
        )

    degrees = sorted(len(adjacency[vertex]) for vertex in GERMS)
    all_edges = frozenset(
        (u, v) for u in GERMS for v in GERMS if u < v
    )
    if len(simple_edges) == 6:
        return SupportClass("K4", data, simple_edges)
    if len(simple_edges) == 5 and degrees == [2, 2, 3, 3]:
        (missing_edge,) = all_edges - simple_edges
        return SupportClass("K4-e", data, simple_edges, missing_edge=missing_edge)
    if len(simple_edges) == 4 and degrees == [2, 2, 2, 2]:
        return SupportClass("C4", data, simple_edges)
    return SupportClass(
        "UNSUPPORTED",
        data,
        simple_edges,
        reason="simple support is outside K4, K4-e, and C4",
    )


def _dart_for_edge_at(data: LinkData, edge: int, vertex: int) -> int:
    darts = data.edge_darts[edge]
    matches = tuple(dart for dart in darts if data.germ[dart] == vertex)
    if len(matches) != 1:
        raise AssertionError("loopless incident edge must have one endpoint dart")
    return matches[0]


def _empty_slots(data: LinkData) -> list[list[int]]:
    return [[-1] * len(data.class_edges[data.edge_class[data.edge_of_dart[dart]]])
            for dart in range(len(data.A))]


def _set_class_block(
    data: LinkData,
    slots: list[list[int]],
    key: ClassKey,
    vertex: int,
    start: int,
    reverse: bool,
) -> None:
    multiplicity = len(data.class_edges[key])
    for edge in data.class_edges[key]:
        dart = _dart_for_edge_at(data, edge, vertex)
        slots[dart][:] = [
            start + (multiplicity - 1 - rank if reverse else rank)
            for rank in range(multiplicity)
        ]


def _verify_slot_partition(data: LinkData, slots: list[list[int]]) -> bool:
    for vertex in GERMS:
        degree = len(data.vertex_darts[vertex])
        images = []
        for key in data.class_edges:
            if vertex not in key:
                continue
            edge = data.class_edges[key][0]
            dart = _dart_for_edge_at(data, edge, vertex)
            image = slots[dart]
            if len(set(image)) != len(image):
                return False
            images.extend(image)
        if sorted(images) != list(range(degree)):
            return False
    return all(all(slot >= 0 for slot in image) for image in slots)


def _block_scheme(
    support: SupportClass,
    name: str,
    neighbor_orders: Mapping[int, tuple[int, ...]],
) -> Scheme:
    data = support.data
    slots = _empty_slots(data)
    for vertex in GERMS:
        start = 0
        for neighbor in neighbor_orders[vertex]:
            key = tuple(sorted((vertex, neighbor)))
            reverse = vertex != key[0]
            _set_class_block(data, slots, key, vertex, start, reverse)
            start += len(data.class_edges[key])
    verified = _verify_slot_partition(data, slots)
    return Scheme(name, support.kind, None, tuple(map(tuple, slots)), verified)


def _k4_scheme(support: SupportClass) -> Scheme:
    neighbor_orders = {
        0: (1, 2, 3),
        1: (0, 3, 2),
        2: (0, 1, 3),
        3: (0, 2, 1),
    }
    return _block_scheme(support, "K4-tetrahedral", neighbor_orders)


def _c4_scheme(support: SupportClass) -> Scheme:
    adjacency = {vertex: [] for vertex in GERMS}
    for u, v in support.simple_edges:
        adjacency[u].append(v)
        adjacency[v].append(u)
    neighbor_orders = {
        vertex: tuple(sorted(neighbors))
        for vertex, neighbors in adjacency.items()
    }
    return _block_scheme(support, "C4-cycle", neighbor_orders)


def _k4_minus_edge_scheme(support: SupportClass, cut: int) -> Scheme:
    data = support.data
    c, d = support.missing_edge or (-1, -1)
    poles = tuple(vertex for vertex in GERMS if vertex not in (c, d))
    if len(poles) != 2:
        raise AssertionError("K4-e must have two poles")
    a, b = poles
    central = tuple(sorted((a, b)))
    ac = tuple(sorted((a, c)))
    ad = tuple(sorted((a, d)))
    bc = tuple(sorted((b, c)))
    bd = tuple(sorted((b, d)))
    m = len(data.class_edges[central])
    if not 0 <= cut <= m:
        raise ValueError("central cut is out of range")

    slots = _empty_slots(data)
    mac = len(data.class_edges[ac])
    mad = len(data.class_edges[ad])
    mbc = len(data.class_edges[bc])
    mbd = len(data.class_edges[bd])

    _set_class_block(data, slots, ac, a, 0, False)
    _set_class_block(data, slots, ad, a, mac + cut, False)
    for edge in data.class_edges[central]:
        dart = _dart_for_edge_at(data, edge, a)
        slots[dart][:] = [
            mac + rank if rank < cut else mac + mad + rank
            for rank in range(m)
        ]

    _set_class_block(data, slots, bc, b, 0, False)
    _set_class_block(data, slots, bd, b, mbc + (m - cut), False)
    for edge in data.class_edges[central]:
        dart = _dart_for_edge_at(data, edge, b)
        slots[dart][:] = [
            mbc + (m - 1 - rank)
            if rank >= cut
            else mbc + (m - cut) + mbd + (cut - 1 - rank)
            for rank in range(m)
        ]

    _set_class_block(data, slots, ac, c, 0, True)
    _set_class_block(data, slots, bc, c, mac, True)
    _set_class_block(data, slots, ad, d, 0, True)
    _set_class_block(data, slots, bd, d, mad, True)

    verified = _verify_slot_partition(data, slots)
    return Scheme(
        f"K4-e-missing-{c}{d}-cut-{cut}",
        support.kind,
        cut,
        tuple(map(tuple, slots)),
        verified,
    )


def embedding_schemes(data: LinkData) -> tuple[Scheme, ...]:
    support = classify_support(data.words)
    if support.kind == "K4":
        schemes = (_k4_scheme(support),)
    elif support.kind == "K4-e":
        c, d = support.missing_edge or (-1, -1)
        poles = tuple(vertex for vertex in GERMS if vertex not in (c, d))
        central = tuple(sorted(poles))
        schemes = tuple(
            _k4_minus_edge_scheme(support, cut)
            for cut in range(len(data.class_edges[central]) + 1)
        )
    elif support.kind == "C4":
        schemes = (_c4_scheme(support),)
    else:
        return ()
    if not all(scheme.slot_partition_verified for scheme in schemes):
        raise AssertionError("proved scheme produced invalid slot partition")
    return schemes


def _constraints(data: LinkData) -> tuple[_Constraint, ...]:
    constraints = []
    for departure in range(0, len(data.B), 2):
        arrival = data.B[departure]
        if data.germ[departure] in (G_X_POS, G_Y_POS):
            positive, negative = departure, arrival
        else:
            positive, negative = arrival, departure
        positive_germ = data.germ[positive]
        if positive_germ not in (G_X_POS, G_Y_POS):
            raise AssertionError("every occurrence has exactly one positive germ")
        constraints.append(
            _Constraint(
                edge_positive=data.edge_of_dart[positive],
                edge_negative=data.edge_of_dart[negative],
                dart_positive=positive,
                dart_negative=negative,
                phase_index=0 if positive_germ == G_X_POS else 1,
                modulus=len(data.vertex_darts[positive_germ]),
            )
        )

    degree = [0] * len(data.edge_darts)
    for constraint in constraints:
        degree[constraint.edge_positive] += 1
        degree[constraint.edge_negative] += 1
    if any(value != 2 for value in degree):
        raise AssertionError("A-contracted B-constraint graph must be 2-regular")
    return tuple(constraints)


def _constraint_components(
    edge_count: int, constraints: tuple[_Constraint, ...]
) -> tuple[tuple[tuple[int, ...], tuple[int, ...]], ...]:
    incident: list[list[int]] = [[] for _ in range(edge_count)]
    for index, constraint in enumerate(constraints):
        incident[constraint.edge_positive].append(index)
        incident[constraint.edge_negative].append(index)

    unseen = set(range(edge_count))
    components = []
    while unseen:
        seed = min(unseen)
        vertices = {seed}
        constraint_indices = set()
        stack = [seed]
        unseen.remove(seed)
        while stack:
            edge = stack.pop()
            for index in incident[edge]:
                constraint_indices.add(index)
                constraint = constraints[index]
                for neighbor in (
                    constraint.edge_positive,
                    constraint.edge_negative,
                ):
                    if neighbor not in vertices:
                        vertices.add(neighbor)
                        unseen.remove(neighbor)
                        stack.append(neighbor)
        components.append(
            (tuple(sorted(vertices)), tuple(sorted(constraint_indices)))
        )
    return tuple(components)


def _inverse_slot(
    scheme: Scheme, dart: int, required_slot: int
) -> int | None:
    matches = tuple(
        rank for rank, slot in enumerate(scheme.slots[dart])
        if slot == required_slot
    )
    if not matches:
        return None
    if len(matches) != 1:
        raise AssertionError("slot map is not injective")
    return matches[0]


def _propagate_component(
    data: LinkData,
    scheme: Scheme,
    constraints: tuple[_Constraint, ...],
    component: tuple[tuple[int, ...], tuple[int, ...]],
    phases: tuple[int, int],
    seed_rank: int,
) -> tuple[_ComponentSolution | None, bool]:
    edges, constraint_indices = component
    seed_edge = edges[0]
    assignments = {seed_edge: seed_rank}
    changed = True
    while changed:
        changed = False
        for index in constraint_indices:
            constraint = constraints[index]
            left = constraint.edge_positive
            right = constraint.edge_negative
            phase = phases[constraint.phase_index]
            modulus = constraint.modulus
            if left in assignments and right not in assignments:
                required = (
                    -phase
                    - scheme.slots[constraint.dart_positive][assignments[left]]
                ) % modulus
                rank = _inverse_slot(
                    scheme, constraint.dart_negative, required
                )
                if rank is None:
                    return None, False
                assignments[right] = rank
                changed = True
            elif right in assignments and left not in assignments:
                required = (
                    -phase
                    - scheme.slots[constraint.dart_negative][assignments[right]]
                ) % modulus
                rank = _inverse_slot(
                    scheme, constraint.dart_positive, required
                )
                if rank is None:
                    return None, False
                assignments[left] = rank
                changed = True

    if set(assignments) != set(edges):
        raise AssertionError("seed propagation did not cover its component")
    for index in constraint_indices:
        constraint = constraints[index]
        if (
            scheme.slots[constraint.dart_positive][
                assignments[constraint.edge_positive]
            ]
            + scheme.slots[constraint.dart_negative][
                assignments[constraint.edge_negative]
            ]
            + phases[constraint.phase_index]
        ) % constraint.modulus:
            return None, False

    used: dict[ClassKey, dict[int, int]] = {}
    for edge, rank in assignments.items():
        key = data.edge_class[edge]
        previous = used.setdefault(key, {}).get(rank)
        if previous is not None and previous != edge:
            return None, True
        used[key][rank] = edge
    masks = tuple(
        (key, sum(1 << rank for rank in ranks))
        for key, ranks in sorted(used.items())
    )
    return (
        _ComponentSolution(tuple(sorted(assignments.items())), masks),
        False,
    )


def _cyclically_equal(left: tuple[int, ...], right: tuple[int, ...]) -> bool:
    if len(left) != len(right):
        return False
    if not left:
        return True
    doubled = right + right
    return any(
        doubled[start:start + len(left)] == left
        for start in range(len(right))
    )


def _permutation_cycles(permutation: tuple[int, ...]) -> tuple[tuple[int, ...], ...]:
    unseen = set(range(len(permutation)))
    cycles = []
    while unseen:
        start = min(unseen)
        cycle = []
        dart = start
        while dart in unseen:
            unseen.remove(dart)
            cycle.append(dart)
            dart = permutation[dart]
        if dart != start:
            raise AssertionError("face permutation is invalid")
        cycles.append(tuple(cycle))
    return tuple(cycles)


def _replay_witness(
    data: LinkData,
    scheme: Scheme,
    constraints: tuple[_Constraint, ...],
    phases: tuple[int, int],
    ranks: tuple[int, ...],
) -> RankWitness | None:
    rank_partition_verified = all(
        {ranks[edge] for edge in edges} == set(range(len(edges)))
        for edges in data.class_edges.values()
    )
    if not rank_partition_verified:
        return None

    rotations = []
    sigma = [-1] * len(data.A)
    for vertex in GERMS:
        rotation = tuple(
            sorted(
                data.vertex_darts[vertex],
                key=lambda dart: scheme.slots[dart][
                    ranks[data.edge_of_dart[dart]]
                ],
            )
        )
        if {
            scheme.slots[dart][ranks[data.edge_of_dart[dart]]]
            for dart in rotation
        } != set(range(len(rotation))):
            return None
        rotations.append(rotation)
        for index, dart in enumerate(rotation):
            sigma[dart] = rotation[(index + 1) % len(rotation)]

    b_reversal_verified = True
    for positive, negative in (
        (G_X_POS, G_X_NEG),
        (G_Y_POS, G_Y_NEG),
    ):
        expected = tuple(
            data.B[dart] for dart in reversed(rotations[positive])
        )
        if not _cyclically_equal(expected, rotations[negative]):
            b_reversal_verified = False

    phase_equations_verified = all(
        (
            scheme.slots[constraint.dart_positive][
                ranks[constraint.edge_positive]
            ]
            + scheme.slots[constraint.dart_negative][
                ranks[constraint.edge_negative]
            ]
            + phases[constraint.phase_index]
        ) % constraint.modulus
        == 0
        for constraint in constraints
    )

    phi = tuple(sigma[data.A[dart]] for dart in range(len(data.A)))
    faces = _permutation_cycles(phi)
    euler_characteristic = len(GERMS) - len(data.edge_darts) + len(faces)
    if (
        euler_characteristic != 2
        or not b_reversal_verified
        or not phase_equations_verified
    ):
        return None
    return RankWitness(
        scheme=scheme.name,
        cut=scheme.cut,
        phases=phases,
        ranks=ranks,
        rotations=tuple(rotations),
        faces=faces,
        face_count=len(faces),
        euler_characteristic=euler_characteristic,
        genus=0,
        b_reversal_verified=b_reversal_verified,
        rank_partition_verified=rank_partition_verified,
        phase_equations_verified=phase_equations_verified,
    )


def _frozen_counters(values: dict[str, int], exhaustive: bool) -> SearchCounters:
    return SearchCounters(
        scheme_budget=values["scheme_budget"],
        schemes_considered=values["schemes_considered"],
        phase_pair_budget=values["phase_pair_budget"],
        phase_pairs_considered=values["phase_pairs_considered"],
        component_seed_budget=values["component_seed_budget"],
        component_seed_attempts=values["component_seed_attempts"],
        closed_component_assignments=values["closed_component_assignments"],
        within_cycle_collision_rejections=values[
            "within_cycle_collision_rejections"
        ],
        component_combination_budget=values[
            "component_combination_budget"
        ],
        component_combinations_considered=values[
            "component_combinations_considered"
        ],
        cross_cycle_collision_rejections=values[
            "cross_cycle_collision_rejections"
        ],
        union_cardinality_checks=values["union_cardinality_checks"],
        union_cardinality_rejections=values[
            "union_cardinality_rejections"
        ],
        witness_replay_failures=values["witness_replay_failures"],
        exhaustive=exhaustive,
    )


def solve_spherical(words: tuple[str, ...]) -> RankDecision:
    """Decide compatible sphericity for the three proved support types.

    A negative is returned only after every scheme, phase pair, component
    seed, and retained component combination has been exhausted.
    """

    words = tuple(words)
    support = classify_support(words)
    zero = SearchCounters()
    if support.kind == "UNSUPPORTED":
        return RankDecision(
            words,
            "UNSUPPORTED",
            None,
            support,
            None,
            zero,
            reason=support.reason,
        )

    data = support.data
    schemes = embedding_schemes(data)
    constraints = _constraints(data)
    components = _constraint_components(len(data.edge_darts), constraints)
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
    nx = len(data.vertex_darts[G_X_POS])
    ny = len(data.vertex_darts[G_Y_POS])
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
                    solution, within_collision = _propagate_component(
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
                masks: dict[ClassKey, int] = {}
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
                    assignments[edge] for edge in range(len(data.edge_darts))
                )
                witness = _replay_witness(
                    data, scheme, constraints, phases, ranks
                )
                if witness is None:
                    values["witness_replay_failures"] += 1
                    continue
                return RankDecision(
                    words,
                    "SPHERICAL",
                    True,
                    support,
                    witness,
                    _frozen_counters(values, exhaustive=False),
                )

    exhaustive = (
        values["schemes_considered"] == values["scheme_budget"]
        and values["phase_pairs_considered"] == values["phase_pair_budget"]
        and values["component_seed_attempts"] == values["component_seed_budget"]
        and values["component_combinations_considered"]
        == values["component_combination_budget"]
    )
    if not exhaustive:
        raise AssertionError("negative search did not exhaust its finite budget")
    return RankDecision(
        words,
        "NOT_SPHERICAL",
        False,
        support,
        None,
        _frozen_counters(values, exhaustive=exhaustive),
    )
