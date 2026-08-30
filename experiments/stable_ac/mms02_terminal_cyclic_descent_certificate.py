"""Exact cyclic row descent for the compressed MMS02 terminal pair."""

from __future__ import annotations

from dataclasses import dataclass

from experiments.equivalence_classes.lib.autcanon import aut_min_len
from experiments.stable_ac.mms02_terminal_base_pair_certificate import (
    decide_terminal_base_pair,
    from_xy,
    to_xy,
)
from experiments.stable_ac.mms02_terminal_hnn_certificate import (
    canonical_cyclic_word,
    whitehead_minimum,
)
from experiments.stable_ac.mms02_terminal_target_hnn_certificate import (
    free_reduce,
    inverse,
)

FLOOR_PAIRS = (
    (
        93,
        (
            "PPQQpqPqqpqqPqqpqPqpQPQpQPQQpQQPQQpQPqqpqq",
            "PQQpQPqqpqqPQpQQPQQpqPqqpqqPqqpqPqpqqPqpQPQpQPQQpQQ",
        ),
    ),
    (
        89,
        (
            "PPQQpqPqqpqqPqqpQPQpQPQQpQQPQQpQPqqpqq",
            "PQQpQPqqpqqPQpQQPQQpqPqqpqqPqqpqPqpqqPqpQPQpQPQQpQQ",
        ),
    ),
    (
        77,
        (
            "PPQQpqPqqpqqPqqpQPQpQPQQpQQPQQpQPqqpqq",
            "PQQpQPqqpQpQQPQQpqPqqpqqPqqpqPqpqqPQpQQ",
        ),
    ),
    (
        69,
        (
            "PPQQpqPqqpqqPqqpQPQpQPQQpQQPQQpQPqqpqq",
            "PQQpQPqqpQPQQpqPqqpqqPqqpqPQpQQ",
        ),
    ),
    (
        64,
        (
            "PPQQpqPqqpqqPqqpQPQQpQQPQQpQPqqpq",
            "PQQpQPqqpQPQQpqPqqpqqPqqpqPQpQQ",
        ),
    ),
    (
        53,
        (
            "PPQQpqPqqpqqPqpQQPQQpQ",
            "PQQpQPqqpQPQQpqPqqpqqPqqpqPQpQQ",
        ),
    ),
    (
        45,
        (
            "PPQQpqPqqpqqPqpQQPQQpQ",
            "PQPQQpqPqqpqqPqqpQPQQpQ",
        ),
    ),
    (
        41,
        (
            "PPQQpqPqqpqqPqpQQPQQpQ",
            "PQQpQPQpqPqqpqqPqpQ",
        ),
    ),
    (
        34,
        (
            "PPQpqPqqpQPQQpQ",
            "PQQpQPQpqPqqpqqPqpQ",
        ),
    ),
    (
        31,
        (
            "PPQpqPqqpQPQQpQ",
            "PQQpQPqPQpqPqpQQ",
        ),
    ),
)

TRANSITION_PRODUCTS = (
    "PQQpQPqqpQpQQPQQpqPqqpqqPqqpqPqpqPQQpQQ",
    "PQQpQPqqpQpQQPQQpqPqqpqqPqqpqPqpqqPQpQQ",
    "PQQpQPqqpQPQQpqPqqpqqPqqpqPQpQQ",
    "PPQQpqPqqpqqPqqpQPQQpQQPQQpQPqqpq",
    "PQQpQPqqPQQpqPqqpqqPqpQQ",
    "PQPQQpqPqqpqqPqqpQPQQpQ",
    "PQQpQPQpqPqqpqqPqpQ",
    "PPQpqPqqpQPQQpQ",
    "PQQpQPqPQpqPqpQQ",
)


@dataclass(frozen=True)
class ProductWitness:
    factor_order: tuple[int, int]
    signs: tuple[int, int]
    rotations: tuple[int, int]
    retained_index: int
    product: str
    source_floor: int
    target_floor: int
    ambient_descent: tuple[tuple[str, str], ...]


EXPECTED_TRANSITION_WITNESSES = (
    ProductWitness(
        factor_order=(0, 1),
        signs=(1, -1),
        rotations=(0, 40),
        retained_index=1,
        product="PQQpQPqqpQpQQPQQpqPqqpqqPqqpqPqpqPQQpQQ",
        source_floor=93,
        target_floor=89,
        ambient_descent=(("xy", "y"),),
    ),
    ProductWitness(
        factor_order=(0, 1),
        signs=(1, -1),
        rotations=(0, 40),
        retained_index=0,
        product="PQQpQPqqpQpQQPQQpqPqqpqqPqqpqPqpqqPQpQQ",
        source_floor=89,
        target_floor=77,
        ambient_descent=(),
    ),
    ProductWitness(
        factor_order=(0, 1),
        signs=(1, 1),
        rotations=(0, 11),
        retained_index=0,
        product="PQQpQPqqpQPQQpqPqqpqqPqqpqPQpQQ",
        source_floor=77,
        target_floor=69,
        ambient_descent=(),
    ),
    ProductWitness(
        factor_order=(0, 1),
        signs=(1, 1),
        rotations=(19, 27),
        retained_index=1,
        product="PPQQpqPqqpqqPqqpQPQQpQQPQQpQPqqpq",
        source_floor=69,
        target_floor=64,
        ambient_descent=(),
    ),
    ProductWitness(
        factor_order=(0, 1),
        signs=(1, 1),
        rotations=(0, 9),
        retained_index=1,
        product="PQQpQPqqPQQpqPqqpqqPqpQQ",
        source_floor=64,
        target_floor=53,
        ambient_descent=(("xy", "y"), ("xy", "y")),
    ),
    ProductWitness(
        factor_order=(0, 1),
        signs=(1, 1),
        rotations=(1, 9),
        retained_index=0,
        product="PQPQQpqPqqpqqPqqpQPQQpQ",
        source_floor=53,
        target_floor=45,
        ambient_descent=(),
    ),
    ProductWitness(
        factor_order=(0, 1),
        signs=(1, -1),
        rotations=(1, 21),
        retained_index=0,
        product="PQQpQPQpqPqqpqqPqpQ",
        source_floor=45,
        target_floor=41,
        ambient_descent=(),
    ),
    ProductWitness(
        factor_order=(0, 1),
        signs=(1, -1),
        rotations=(3, 13),
        retained_index=1,
        product="PPQpqPqqpQPQQpQ",
        source_floor=41,
        target_floor=34,
        ambient_descent=(),
    ),
    ProductWitness(
        factor_order=(0, 1),
        signs=(1, -1),
        rotations=(0, 14),
        retained_index=0,
        product="PQQpQPqPQpqPqpQQ",
        source_floor=34,
        target_floor=31,
        ambient_descent=(),
    ),
)


@dataclass(frozen=True)
class CyclicDescentDecision:
    initial_floor: int
    initial_product: str
    floor_pairs: tuple[tuple[int, tuple[str, str]], ...]
    transitions: tuple[ProductWitness, ...]
    terminal_product_count: int
    terminal_neighbor_floor: int
    terminal_pair: tuple[str, str]
    verdict: str


def rotations(word: str, sign: int) -> tuple[str, ...]:
    oriented = word if sign == 1 else inverse(word)
    return tuple(oriented[index:] + oriented[:index] for index in range(len(oriented)))


def product_witness(pair: tuple[str, str], target: str):
    for factor_order in ((0, 1), (1, 0)):
        for first_sign in (1, -1):
            for second_sign in (1, -1):
                first_rotations = rotations(pair[factor_order[0]], first_sign)
                second_rotations = rotations(pair[factor_order[1]], second_sign)
                for first_index, first in enumerate(first_rotations):
                    for second_index, second in enumerate(second_rotations):
                        product = canonical_cyclic_word(free_reduce(first + second))
                        if product == target:
                            return (
                                factor_order,
                                (first_sign, second_sign),
                                (first_index, second_index),
                            )
    raise AssertionError("the pinned cyclic row product has no legal witness")


def minimize_pair(pair: tuple[str, str]):
    minimum_xy, descent = whitehead_minimum(tuple(to_xy(word) for word in pair))
    minimum = tuple(from_xy(word) for word in minimum_xy)
    floor = sum(map(len, minimum))
    if aut_min_len(tuple(to_xy(word) for word in pair)) != floor:
        raise AssertionError("the independent ambient floor disagrees")
    return minimum, floor, descent


def terminal_neighborhood(pair: tuple[str, str]) -> tuple[int, int]:
    products = set()
    for factor_order in ((0, 1), (1, 0)):
        for first_sign in (1, -1):
            for second_sign in (1, -1):
                first_rotations = rotations(pair[factor_order[0]], first_sign)
                second_rotations = rotations(pair[factor_order[1]], second_sign)
                for first in first_rotations:
                    for second in second_rotations:
                        products.add(canonical_cyclic_word(free_reduce(first + second)))
    best = min(
        aut_min_len((to_xy(product), to_xy(pair[retained_index])))
        for product in products
        for retained_index in (0, 1)
    )
    for product in products:
        for retained_index in (0, 1):
            pair_floor = aut_min_len((to_xy(product), to_xy(pair[retained_index])))
            if pair_floor == best:
                _, replay_floor, _ = minimize_pair((product, pair[retained_index]))
                if replay_floor != best:
                    raise AssertionError("the terminal local-floor replay disagrees")
    return len(products), best


def decide_cyclic_descent() -> CyclicDescentDecision:
    base = decide_terminal_base_pair()
    if base.base_floor != 104:
        raise AssertionError("the terminal base-pair floor drifted")
    initial_product = free_reduce(inverse(base.base_pair[0]) + base.base_pair[1])
    first_pair, first_floor, _ = minimize_pair((initial_product, base.base_pair[1]))
    if (first_floor, first_pair) != FLOOR_PAIRS[0]:
        raise AssertionError("the initial AC row descent drifted")

    transitions = []
    for (source_floor, source_pair), product, (target_floor, target_pair) in zip(
        FLOOR_PAIRS[:-1],
        TRANSITION_PRODUCTS,
        FLOOR_PAIRS[1:],
        strict=True,
    ):
        factor_order, signs, rotation_indices = product_witness(source_pair, product)
        matches = []
        for retained_index in (0, 1):
            minimum, floor, descent = minimize_pair((product, source_pair[retained_index]))
            if (floor, minimum) == (target_floor, target_pair):
                matches.append((retained_index, descent))
        if not matches:
            raise AssertionError("the pinned cyclic transition missed its target floor")
        retained_index, descent = matches[0]
        transitions.append(
            ProductWitness(
                factor_order=factor_order,
                signs=signs,
                rotations=rotation_indices,
                retained_index=retained_index,
                product=product,
                source_floor=source_floor,
                target_floor=target_floor,
                ambient_descent=descent,
            )
        )

    if tuple(transitions) != EXPECTED_TRANSITION_WITNESSES:
        raise AssertionError("the independently pinned transition witnesses drifted")

    terminal_floor, terminal_pair = FLOOR_PAIRS[-1]
    if terminal_floor != 31:
        raise AssertionError("the terminal cyclic floor drifted")
    product_count, neighbor_floor = terminal_neighborhood(terminal_pair)
    if product_count != 238 or neighbor_floor != 32:
        raise AssertionError("the complete terminal cyclic neighborhood drifted")

    return CyclicDescentDecision(
        initial_floor=base.base_floor,
        initial_product=initial_product,
        floor_pairs=FLOOR_PAIRS,
        transitions=tuple(transitions),
        terminal_product_count=product_count,
        terminal_neighbor_floor=neighbor_floor,
        terminal_pair=terminal_pair,
        verdict="TARGET_CYCLIC_DESCENT_FLOOR_31",
    )


if __name__ == "__main__":
    print(decide_cyclic_descent())
