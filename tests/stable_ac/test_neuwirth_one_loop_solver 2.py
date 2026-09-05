from experiments.stable_ac.thickenable.neuwirth_one_loop_solver import (
    classify_one_loop_support,
    loop_embedding_schemes,
    solve_one_loop_spherical,
)
from experiments.stable_ac.thickenable.neuwirth_permutation_certificate import (
    enumerate_trace,
)


def test_one_loop_rank_solver_matches_factorial_positive():
    words = ("xxy", "yXYy")
    support = classify_one_loop_support(words)
    assert support.kind == "K4-e+1loop"
    assert support.loop_class == (2, 2)
    assert len(support.data.class_edges[support.loop_class]) == 1
    schemes = loop_embedding_schemes(support)
    assert schemes
    assert all(scheme.slot_partition_verified for scheme in schemes)

    rank = solve_one_loop_spherical(words)
    factorial = enumerate_trace(words)
    assert factorial.expected_cases == 12
    assert rank.spherical is bool(factorial.accepting_orders)
    assert rank.spherical is True
    assert rank.witness is not None
    assert rank.witness.euler_characteristic == 2


def test_one_loop_rank_solver_matches_factorial_negative():
    words = ("x", "YXyxyy")
    rank = solve_one_loop_spherical(words)
    factorial = enumerate_trace(words)
    assert factorial.expected_cases == 12
    assert rank.support.kind == "K4-e+1loop"
    assert rank.spherical is bool(factorial.accepting_orders)
    assert rank.spherical is False
    assert rank.witness is None
    assert rank.counters.exhaustive


def test_one_loop_solver_fails_closed_on_two_loop_edges():
    decision = solve_one_loop_spherical(("xX", "yy"))
    assert decision.spherical is None
    assert decision.verdict == "UNSUPPORTED"


def test_one_loop_solver_fails_closed_on_repeated_loop_class():
    decision = solve_one_loop_spherical(("xXy", "xXy"))
    assert decision.spherical is None
    assert decision.verdict == "UNSUPPORTED"
