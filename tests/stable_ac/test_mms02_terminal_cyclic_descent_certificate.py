from experiments.equivalence_classes.lib.autcanon import aut_min_len
from experiments.stable_ac.mms02_terminal_base_pair_certificate import to_xy
from experiments.stable_ac.mms02_terminal_cyclic_descent_certificate import (
    EXPECTED_TRANSITION_WITNESSES,
    FLOOR_PAIRS,
    TRANSITION_PRODUCTS,
    decide_cyclic_descent,
    product_witness,
)


def test_terminal_cyclic_descent_has_exact_strict_floor_chain():
    decision = decide_cyclic_descent()
    assert decision.initial_floor == 104
    assert tuple(floor for floor, _ in decision.floor_pairs) == (
        93,
        89,
        77,
        69,
        64,
        53,
        45,
        41,
        34,
        31,
    )
    assert all(
        left > right
        for left, right in zip(
            (decision.initial_floor,) + tuple(floor for floor, _ in decision.floor_pairs[:-1]),
            tuple(floor for floor, _ in decision.floor_pairs),
            strict=True,
        )
    )


def test_every_terminal_cyclic_transition_has_a_literal_row_witness():
    decision = decide_cyclic_descent()
    assert len(decision.transitions) == len(TRANSITION_PRODUCTS) == 9
    assert decision.transitions == EXPECTED_TRANSITION_WITNESSES
    for transition, (_, source_pair) in zip(
        decision.transitions,
        FLOOR_PAIRS[:-1],
        strict=True,
    ):
        assert product_witness(source_pair, transition.product) == (
            transition.factor_order,
            transition.signs,
            transition.rotations,
        )
        assert transition.target_floor < transition.source_floor
    assert any(transition.ambient_descent for transition in decision.transitions)


def test_terminal_floor_31_is_local_only_for_complete_cyclic_neighborhood():
    decision = decide_cyclic_descent()
    assert decision.terminal_pair == (
        "PPQpqPqqpQPQQpQ",
        "PQQpQPqPQpqPqpQQ",
    )
    assert aut_min_len(tuple(to_xy(word) for word in decision.terminal_pair)) == 31
    assert decision.terminal_product_count == 238
    assert decision.terminal_neighbor_floor == 32
    assert decision.verdict == "TARGET_CYCLIC_DESCENT_FLOOR_31"
