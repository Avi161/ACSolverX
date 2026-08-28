"""Exact finite boundary-donor Neuwirth checks for the MMS02 Tpub rows."""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass

from experiments.stable_ac.thickenable import (
    mms02_tpub_neuwirth_certificate as tpub,
)
from experiments.stable_ac.thickenable import (
    neuwirth_rank3_rigid_solver as rigid,
)
from experiments.stable_ac.thickenable import neuwirth_rank_solver as base


A_ROW = tpub.ORIGINAL_WORDS[0]
B_ROW = tpub.ORIGINAL_WORDS[1]
V_WORD = tpub.ORIGINAL_WORDS[2]
INVERSES = str.maketrans("xXyYzZ", "XxYyZz")
EXPECTED_SHORTENING_PRODUCTS = (
    ("A", "+", "yzX", "zYXyxZXYxyZyz"),
    ("A", "+", "zXy", "xzYXyxZXYxyXy"),
    ("B", "-", "ZYx", "xZXYXyxzXYxyZ"),
    ("B", "-", "YxZ", "XyxZXYXyxzXYxxZ"),
)


@dataclass(frozen=True)
class BoundaryDonorProduct:
    row: str
    sign: str
    multiplier: str
    transformed_word: str


@dataclass(frozen=True)
class BoundaryDonorDecision:
    transformed_word: str
    macro_rotation_budget: int
    spherical_scheme_count: int
    witness: rigid.RigidRankWitness | None
    counters: rigid.RigidSearchCounters
    verdict: str


def inverse_word(word: str) -> str:
    return word.translate(INVERSES)[::-1]


def free_reduce(word: str) -> str:
    reduced: list[str] = []
    for letter in word:
        if reduced and reduced[-1] == letter.translate(INVERSES):
            reduced.pop()
        else:
            reduced.append(letter)
    return "".join(reduced)


def cyclic_reduce(word: str) -> str:
    reduced = free_reduce(word)
    while len(reduced) > 1 and reduced[0] == reduced[-1].translate(
        INVERSES
    ):
        reduced = free_reduce(reduced[1:-1])
    return reduced


def cyclic_shifts(word: str) -> tuple[str, ...]:
    return tuple(word[index:] + word[:index] for index in range(len(word)))


def enumerate_boundary_products() -> tuple[BoundaryDonorProduct, ...]:
    products = []
    for row_name, row in (("A", A_ROW), ("B", B_ROW)):
        for sign, donor in (("+", V_WORD), ("-", inverse_word(V_WORD))):
            for multiplier in cyclic_shifts(donor):
                products.append(
                    BoundaryDonorProduct(
                        row_name,
                        sign,
                        multiplier,
                        cyclic_reduce(row + multiplier),
                    )
                )
    return tuple(products)


def shortening_products() -> tuple[BoundaryDonorProduct, ...]:
    products = enumerate_boundary_products()
    if len(products) != 12:
        raise AssertionError("boundary donor product enumeration drifted")
    shortened = tuple(
        product
        for product in products
        if len(product.transformed_word)
        < len(A_ROW if product.row == "A" else B_ROW) + 3
    )
    observed = tuple(
        (
            product.row,
            product.sign,
            product.multiplier,
            product.transformed_word,
        )
        for product in shortened
    )
    if observed != EXPECTED_SHORTENING_PRODUCTS:
        raise AssertionError("boundary donor shortening products drifted")
    return shortened


def _presentation_words(product: BoundaryDonorProduct) -> tuple[str, ...]:
    words = list(tpub.ORIGINAL_WORDS)
    words[0 if product.row == "A" else 1] = product.transformed_word
    return tpub.relabel_words(tuple(words))


def _validate_loopless_connected(data: base.LinkData) -> frozenset[base.ClassKey]:
    simple_edges = frozenset(data.class_edges)
    if any(left == right for left, right in simple_edges):
        raise AssertionError("boundary donor A-link unexpectedly contains a loop")
    if not rigid._is_connected(simple_edges):
        raise AssertionError("boundary donor A-link unexpectedly disconnected")
    return simple_edges


def _repeated_classes_are_deletion_connected(
    data: base.LinkData,
    simple_edges: frozenset[base.ClassKey],
) -> bool:
    return all(
        tpub._connected_after_deleting(simple_edges, key)
        for key, edges in data.class_edges.items()
        if len(edges) > 1
    )


def _canonical_cyclic_order(order: tuple[int, ...]) -> tuple[int, ...]:
    return min(
        order[index:] + order[:index]
        for index in range(len(order))
    )


def _cyclic_multiset_orders(
    neighbors: tuple[int, ...],
) -> tuple[tuple[int, ...], ...]:
    return tuple(
        sorted(
            {
                _canonical_cyclic_order(order)
                for order in itertools.permutations(neighbors)
            }
        )
    )


def _partial_neighbor_orders(
    data: base.LinkData,
    special: base.ClassKey,
) -> tuple[tuple[tuple[int, ...], ...], ...]:
    orders = []
    for vertex in rigid.GERMS:
        neighbors = []
        for key, edges in sorted(data.class_edges.items()):
            if vertex not in key:
                continue
            left, right = key
            neighbor = right if vertex == left else left
            neighbors.extend((neighbor,) * (len(edges) if key == special else 1))
        orders.append(_cyclic_multiset_orders(tuple(neighbors)))
    return tuple(orders)


def _partial_expansion_scheme(
    data: base.LinkData,
    special: base.ClassKey,
    rotation: tuple[tuple[int, ...], ...],
    pairing: int,
    index: int,
) -> base.Scheme:
    if pairing not in (0, 1):
        raise ValueError("special endpoint pairing must be binary")
    left, right = special
    slots = base._empty_slots(data)
    special_positions = {left: [], right: []}
    for vertex in rigid.GERMS:
        start = 0
        for neighbor in rotation[vertex]:
            key = tuple(sorted((vertex, neighbor)))
            if key == special:
                special_positions[vertex].append(start)
                start += 1
                continue
            base._set_class_block(
                data,
                slots,
                key,
                vertex,
                start,
                reverse=vertex != key[0],
            )
            start += len(data.class_edges[key])
        if start != len(data.vertex_darts[vertex]):
            raise AssertionError("partial expansion does not cover a vertex")

    if (
        len(special_positions[left]) != 2
        or len(special_positions[right]) != 2
    ):
        raise AssertionError("partial expansion lost a special class endpoint")
    right_mapping = (
        tuple(reversed(special_positions[right]))
        if pairing
        else tuple(special_positions[right])
    )
    endpoint_slots = {
        left: tuple(special_positions[left]),
        right: right_mapping,
    }
    for vertex, mapping in endpoint_slots.items():
        for edge in data.class_edges[special]:
            dart = base._dart_for_edge_at(data, edge, vertex)
            slots[dart][:] = mapping
    if not rigid._verify_slot_partition(data, slots):
        raise AssertionError("partial expansion produced invalid slot maps")
    return base.Scheme(
        name=f"Tpub-boundary-partial-{index}",
        support_kind="Tpub-boundary-partial",
        cut=None,
        slots=tuple(map(tuple, slots)),
        slot_partition_verified=True,
    )


def _canonical_euler_characteristic(
    data: base.LinkData,
    scheme: base.Scheme,
) -> int:
    ranks = [-1] * len(data.edge_darts)
    for edges in data.class_edges.values():
        for rank, edge in enumerate(edges):
            ranks[edge] = rank
    if any(rank < 0 for rank in ranks):
        raise AssertionError("canonical ranks do not cover the A-link")

    sigma = [-1] * len(data.A)
    for vertex in rigid.GERMS:
        rotation = tuple(
            sorted(
                data.vertex_darts[vertex],
                key=lambda dart: scheme.slots[dart][
                    ranks[data.edge_of_dart[dart]]
                ],
            )
        )
        positions = {
            scheme.slots[dart][ranks[data.edge_of_dart[dart]]]
            for dart in rotation
        }
        if positions != set(range(len(rotation))):
            raise AssertionError("canonical ranks do not define a rotation")
        for offset, dart in enumerate(rotation):
            sigma[dart] = rotation[(offset + 1) % len(rotation)]
    faces = base._permutation_cycles(
        tuple(sigma[data.A[dart]] for dart in range(len(data.A)))
    )
    return len(rigid.GERMS) - len(data.edge_darts) + len(faces)


def _partial_expansion_schemes(
    data: base.LinkData,
    simple_edges: frozenset[base.ClassKey],
) -> tuple[int, tuple[base.Scheme, ...]]:
    disconnected_repeated = tuple(
        (key, len(edges))
        for key, edges in sorted(data.class_edges.items())
        if len(edges) > 1
        and not tpub._connected_after_deleting(simple_edges, key)
    )
    if disconnected_repeated != (((1, 3), 2),):
        raise AssertionError("unexpected boundary donor special class")
    special = (1, 3)
    local_orders = _partial_neighbor_orders(data, special)
    macro_budget = math.prod(map(len, local_orders))
    if macro_budget != 144:
        raise AssertionError("partial expansion multiset budget drifted")

    schemes = []
    candidate_count = 0
    for rotation in itertools.product(*local_orders):
        for pairing in range(2):
            candidate_count += 1
            scheme = _partial_expansion_scheme(
                data,
                special,
                rotation,
                pairing,
                candidate_count,
            )
            if _canonical_euler_characteristic(data, scheme) == 2:
                schemes.append(scheme)
    if candidate_count != 288 or len(schemes) != 12:
        raise AssertionError("partial expansion scheme census drifted")
    return candidate_count, tuple(schemes)


def _schemes_for_data(
    data: base.LinkData,
) -> tuple[int, tuple[base.Scheme, ...]]:
    simple_edges = _validate_loopless_connected(data)
    if _repeated_classes_are_deletion_connected(data, simple_edges):
        macro_budget, macro_rotations = tpub.enumerate_macro_rotations(
            simple_edges
        )
        return macro_budget, tuple(
            tpub._scheme(data, rotation, index)
            for index, rotation in enumerate(macro_rotations, start=1)
        )
    return _partial_expansion_schemes(data, simple_edges)


def decide_tpub_boundary_donors() -> tuple[BoundaryDonorDecision, ...]:
    decisions = []
    for product in shortening_products():
        data = rigid._build_link_data(_presentation_words(product))
        macro_budget, schemes = _schemes_for_data(data)
        witness, counters = rigid._search_signed_ranks(data, schemes)
        decisions.append(
            BoundaryDonorDecision(
                transformed_word=product.transformed_word,
                macro_rotation_budget=macro_budget,
                spherical_scheme_count=len(schemes),
                witness=witness,
                counters=counters,
                verdict=(
                    "SPHERICAL_CANDIDATE_REQUIRES_INDEPENDENT_AUDIT"
                    if witness is not None
                    else "NOT_SPHERICAL_EXACT_COMPLEX"
                ),
            )
        )
    return tuple(decisions)
