from experiments.equivalence_classes.lib.autcanon import aut_min_len
from experiments.stable_ac.mms02_terminal_base_pair_certificate import to_xy
from experiments.stable_ac.mms02_terminal_cyclic_descent_certificate import (
    EXPECTED_CANONICAL_EUCLIDEAN_LIFTS,
    EXPECTED_TRANSITION_WITNESSES,
    FLOOR_PAIRS,
    TRANSITION_PRODUCTS,
    decide_canonical_euclidean_lift,
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


def test_canonical_euclidean_lifts_are_exact_and_nonprimitive():
    decision = decide_canonical_euclidean_lift()
    assert decision.lifts == EXPECTED_CANONICAL_EUCLIDEAN_LIFTS
    assert all(len(lift.difference) == 27 for lift in decision.lifts)
    assert all(lift.singleton_floor == 25 for lift in decision.lifts)
    assert {lift.difference_abelianization for lift in decision.lifts} == {
        (0, -1),
        (0, 1),
    }


def test_canonical_euclidean_lifts_restore_only_the_abelian_basis():
    decision = decide_canonical_euclidean_lift()
    assert all(lift.a_endpoint_abelianization == (-1, 0) for lift in decision.lifts)
    assert all(lift.b_endpoint_abelianization == (-1, 0) for lift in decision.lifts)
    assert all(min(lift.a_floor_path) > 31 for lift in decision.lifts)
    assert all(min(lift.b_floor_path) > 31 for lift in decision.lifts)
    assert {lift.a_floor_path for lift in decision.lifts} == {
        (41, 60, 81),
        (41, 66, 91),
    }
    assert {lift.b_floor_path for lift in decision.lifts} == {
        (40, 61, 84, 109),
        (40, 65, 90, 115),
    }
    assert min(lift.a_endpoint_floor for lift in decision.lifts) == 81
    assert min(lift.b_endpoint_floor for lift in decision.lifts) == 109
    assert decision.verdict == "CANONICAL_EUCLIDEAN_LIFTS_DO_NOT_LOWER_FLOOR_31"
