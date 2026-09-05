"""Exact signed-rank solver for rigid six-germ Neuwirth links.

Only connected loopless support isomorphic to K6 minus a five-vertex path is
decided.  Every other support fails closed.
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass
from typing import Mapping

from experiments.stable_ac.thickenable import neuwirth_rank_solver as base


GERMS = tuple(range(6))
POSITIVE_GERMS = (0, 2, 4)
GERM_PAIRS = ((0, 1), (2, 3), (4, 5))


@dataclass(frozen=True)
class RigidSupport:
    kind: str
    data: base.LinkData
    simple_edges: frozenset[base.ClassKey]
    macro_rotations: tuple[tuple[tuple[int, ...], ...], ...]
    reason: str | None = None


@dataclass(frozen=True)
class RigidSearchCounters:
    scheme_budget: int = 0
    schemes_considered: int = 0
    phase_tuple_budget: int = 0
    phase_tuples_considered: int = 0
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
class RigidRankWitness:
    scheme: str
    phases: tuple[int, int, int]
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
class RigidRankDecision:
    words: tuple[str, ...]
    verdict: str
    spherical: bool | None
    support: RigidSupport
    witness: RigidRankWitness | None
    counters: RigidSearchCounters
    reason: str | None = None


def _letter_germs(letter: str) -> tuple[int, int]:
    try:
        return {
            "x": (0, 1),
            "X": (1, 0),
            "z": (2, 3),
            "Z": (3, 2),
            "t": (4, 5),
            "T": (5, 4),
        }[letter]
    except KeyError as exc:
        raise ValueError(f"unsupported rank-three letter {letter!r}") from exc


def _build_link_data(words: tuple[str, ...]) -> base.LinkData:
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
        occurrences = tuple(range(offset, offset + len(word)))
        for local_index, occurrence in enumerate(occurrences):
            departure = 2 * occurrence
            arrival = departure + 1
            departure_germ, arrival_germ = _letter_germs(word[local_index])
            germ[departure] = departure_germ
            germ[arrival] = arrival_germ
            B[departure] = arrival
            B[arrival] = departure

            following = occurrences[(local_index + 1) % len(word)]
            following_departure = 2 * following
            A[arrival] = following_departure
            A[following_departure] = arrival
        offset += len(word)
    if any(value < 0 for value in A + B + germ):
        raise AssertionError("incomplete exact rank-three dictionary")

    edge_of_dart = [-1] * dart_count
    edge_darts = []
    edge_class = []
    class_edges: dict[base.ClassKey, list[int]] = {}
    for dart, mate in enumerate(A):
        if dart > mate:
            continue
        edge = len(edge_darts)
        edge_darts.append((dart, mate))
        edge_of_dart[dart] = edge
        edge_of_dart[mate] = edge
        key = tuple(sorted((germ[dart], germ[mate])))
        edge_class.append(key)
        class_edges.setdefault(key, []).append(edge)
    return base.LinkData(
        words=words,
        A=tuple(A),
        B=tuple(B),
        germ=tuple(germ),
        edge_of_dart=tuple(edge_of_dart),
        edge_darts=tuple(edge_darts),
        edge_class=tuple(edge_class),
        class_edges={
            key: tuple(edges) for key, edges in sorted(class_edges.items())
        },
        vertex_darts={
            vertex: tuple(
                dart for dart, at in enumerate(germ) if at == vertex
            )
            for vertex in GERMS
        },
    )


def _is_connected(simple_edges: frozenset[base.ClassKey]) -> bool:
    adjacency = {vertex: set() for vertex in GERMS}
    for left, right in simple_edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    reached = {GERMS[0]}
    stack = [GERMS[0]]
    while stack:
        vertex = stack.pop()
        for neighbor in adjacency[vertex] - reached:
            reached.add(neighbor)
            stack.append(neighbor)
    return reached == set(GERMS)


def _complement_is_p5_plus_isolate(
    simple_edges: frozenset[base.ClassKey],
) -> bool:
    all_edges = {
        (left, right)
        for left in GERMS
        for right in GERMS
        if left < right
    }
    complement = all_edges - set(simple_edges)
    if len(complement) != 4:
        return False
    adjacency = {vertex: set() for vertex in GERMS}
    for left, right in complement:
        adjacency[left].add(right)
        adjacency[right].add(left)
    if sorted(map(len, adjacency.values())) != [0, 1, 1, 2, 2, 2]:
        return False
    nonisolated = {vertex for vertex in GERMS if adjacency[vertex]}
    reached = {min(nonisolated)}
    stack = list(reached)
    while stack:
        vertex = stack.pop()
        for neighbor in adjacency[vertex] - reached:
            reached.add(neighbor)
            stack.append(neighbor)
    return reached == nonisolated


def _simple_face_count(
    rotation: tuple[tuple[int, ...], ...],
    simple_edges: frozenset[base.ClassKey],
) -> int:
    directed = {
        (left, right)
        for edge in simple_edges
        for left, right in (edge, tuple(reversed(edge)))
    }
    seen = set()
    faces = 0
    for start in sorted(directed):
        if start in seen:
            continue
        faces += 1
        dart = start
        while dart not in seen:
            seen.add(dart)
            left, right = dart
            order = rotation[right]
            index = order.index(left)
            dart = (right, order[(index + 1) % len(order)])
    if seen != directed:
        raise AssertionError("simple face trace missed a directed edge")
    return faces


def _macro_rotations(
    simple_edges: frozenset[base.ClassKey],
) -> tuple[tuple[tuple[int, ...], ...], ...]:
    adjacency = {vertex: set() for vertex in GERMS}
    for left, right in simple_edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    per_vertex = []
    for vertex in GERMS:
        neighbors = sorted(adjacency[vertex])
        head, *tail = neighbors
        per_vertex.append(
            tuple((head, *order) for order in itertools.permutations(tail))
        )

    spherical = []
    for rotation in itertools.product(*per_vertex):
        faces = _simple_face_count(rotation, simple_edges)
        if len(GERMS) - len(simple_edges) + faces == 2:
            spherical.append(tuple(map(tuple, rotation)))
    if len(spherical) != 2:
        raise AssertionError(
            f"rigid support must have two macro rotations, got {len(spherical)}"
        )
    first = min(spherical)
    reflected = tuple(tuple(reversed(order)) for order in first)
    if not any(
        all(
            base._cyclically_equal(left, right)
            for left, right in zip(reflected, candidate)
        )
        for candidate in spherical
    ):
        raise AssertionError("second macro rotation is not the global reflection")
    return (first, reflected)


def classify_rigid_support(words: tuple[str, ...]) -> RigidSupport:
    data = _build_link_data(tuple(words))
    simple_edges = frozenset(data.edge_class)
    if any(left == right for left, right in simple_edges):
        return RigidSupport(
            "UNSUPPORTED",
            data,
            simple_edges,
            (),
            reason="A-link contains a loop",
        )
    if not _is_connected(simple_edges):
        return RigidSupport(
            "UNSUPPORTED",
            data,
            simple_edges,
            (),
            reason="A-link is disconnected",
        )
    if (
        len(simple_edges) != 11
        or not _complement_is_p5_plus_isolate(simple_edges)
    ):
        return RigidSupport(
            "UNSUPPORTED",
            data,
            simple_edges,
            (),
            reason="simple support is not K6 minus P5",
        )
    return RigidSupport(
        "K6-P5",
        data,
        simple_edges,
        _macro_rotations(simple_edges),
    )


def _verify_slot_partition(
    data: base.LinkData,
    slots: list[list[int]],
) -> bool:
    for vertex in GERMS:
        images = []
        for key in data.class_edges:
            if vertex not in key:
                continue
            edge = data.class_edges[key][0]
            dart = base._dart_for_edge_at(data, edge, vertex)
            image = slots[dart]
            if len(set(image)) != len(image):
                return False
            images.extend(image)
        if sorted(images) != list(range(len(data.vertex_darts[vertex]))):
            return False
    return all(all(slot >= 0 for slot in image) for image in slots)


def rigid_embedding_scheme(support: RigidSupport) -> base.Scheme:
    if support.kind != "K6-P5" or len(support.macro_rotations) != 2:
        raise ValueError("rigid scheme requires K6-P5 support")
    data = support.data
    slots = base._empty_slots(data)
    rotation = support.macro_rotations[0]
    for vertex in GERMS:
        start = 0
        for neighbor in rotation[vertex]:
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
    verified = _verify_slot_partition(data, slots)
    if not verified:
        raise AssertionError("rigid scheme produced invalid slot maps")
    return base.Scheme(
        name="K6-P5-Whitney",
        support_kind="K6-P5",
        cut=None,
        slots=tuple(map(tuple, slots)),
        slot_partition_verified=True,
    )


def _constraints(data: base.LinkData) -> tuple[base._Constraint, ...]:
    constraints = []
    for departure in range(0, len(data.B), 2):
        arrival = data.B[departure]
        if data.germ[departure] in POSITIVE_GERMS:
            positive, negative = departure, arrival
        else:
            positive, negative = arrival, departure
        positive_germ = data.germ[positive]
        if positive_germ not in POSITIVE_GERMS:
            raise AssertionError("occurrence has no positive generator germ")
        constraints.append(
            base._Constraint(
                edge_positive=data.edge_of_dart[positive],
                edge_negative=data.edge_of_dart[negative],
                dart_positive=positive,
                dart_negative=negative,
                phase_index=positive_germ // 2,
                modulus=len(data.vertex_darts[positive_germ]),
            )
        )
    degree = [0] * len(data.edge_darts)
    for constraint in constraints:
        degree[constraint.edge_positive] += 1
        degree[constraint.edge_negative] += 1
    if any(value != 2 for value in degree):
        raise AssertionError("rank-three constraint graph is not 2-regular")
    return tuple(constraints)


def _replay_witness(
    data: base.LinkData,
    scheme: base.Scheme,
    constraints: tuple[base._Constraint, ...],
    phases: tuple[int, int, int],
    ranks: tuple[int, ...],
) -> RigidRankWitness | None:
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

    b_reversal_verified = all(
        base._cyclically_equal(
            tuple(data.B[dart] for dart in reversed(rotations[positive])),
            rotations[negative],
        )
        for positive, negative in GERM_PAIRS
    )
    phase_equations_verified = all(
        (
            scheme.slots[constraint.dart_positive][
                ranks[constraint.edge_positive]
            ]
            + scheme.slots[constraint.dart_negative][
                ranks[constraint.edge_negative]
            ]
            + phases[constraint.phase_index]
        )
        % constraint.modulus
        == 0
        for constraint in constraints
    )
    phi = tuple(sigma[data.A[dart]] for dart in range(len(data.A)))
    faces = base._permutation_cycles(phi)
    euler_characteristic = (
        len(GERMS) - len(data.edge_darts) + len(faces)
    )
    if (
        euler_characteristic != 2
        or not b_reversal_verified
        or not phase_equations_verified
    ):
        return None
    return RigidRankWitness(
        scheme=scheme.name,
        phases=phases,
        ranks=ranks,
        rotations=tuple(rotations),
        faces=faces,
        face_count=len(faces),
        euler_characteristic=euler_characteristic,
        genus=0,
        b_reversal_verified=True,
        rank_partition_verified=True,
        phase_equations_verified=True,
    )


def _freeze(
    values: Mapping[str, int],
    exhaustive: bool,
) -> RigidSearchCounters:
    return RigidSearchCounters(
        **{
            field: values[field]
            for field in RigidSearchCounters.__dataclass_fields__
            if field != "exhaustive"
        },
        exhaustive=exhaustive,
    )


def solve_rigid_spherical(words: tuple[str, ...]) -> RigidRankDecision:
    words = tuple(words)
    support = classify_rigid_support(words)
    if support.kind != "K6-P5":
        return RigidRankDecision(
            words,
            "UNSUPPORTED",
            None,
            support,
            None,
            RigidSearchCounters(),
            reason=support.reason,
        )

    data = support.data
    scheme = rigid_embedding_scheme(support)
    constraints = _constraints(data)
    components = base._constraint_components(
        len(data.edge_darts),
        constraints,
    )
    values = {
        field: 0
        for field in RigidSearchCounters.__dataclass_fields__
        if field != "exhaustive"
    }
    phase_ranges = tuple(
        range(len(data.vertex_darts[positive]))
        for positive in POSITIVE_GERMS
    )
    phase_budget = math.prod(map(len, phase_ranges))
    seed_budget_per_phase = sum(
        len(data.class_edges[data.edge_class[component[0][0]]])
        for component in components
    )
    values["scheme_budget"] = 1
    values["phase_tuple_budget"] = phase_budget
    values["component_seed_budget"] = (
        phase_budget * seed_budget_per_phase
    )
    values["schemes_considered"] = 1

    for phases in itertools.product(*phase_ranges):
        values["phase_tuples_considered"] += 1
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
            witness = _replay_witness(
                data,
                scheme,
                constraints,
                phases,
                ranks,
            )
            if witness is None:
                values["witness_replay_failures"] += 1
                continue
            return RigidRankDecision(
                words,
                "SPHERICAL",
                True,
                support,
                witness,
                _freeze(values, exhaustive=False),
            )

    exhaustive = (
        values["schemes_considered"] == values["scheme_budget"]
        and values["phase_tuples_considered"] == values["phase_tuple_budget"]
        and values["component_seed_attempts"]
        == values["component_seed_budget"]
        and values["component_combinations_considered"]
        == values["component_combination_budget"]
    )
    if not exhaustive:
        raise AssertionError("negative rigid search did not exhaust its budget")
    return RigidRankDecision(
        words,
        "NOT_SPHERICAL",
        False,
        support,
        None,
        _freeze(values, exhaustive=True),
    )
