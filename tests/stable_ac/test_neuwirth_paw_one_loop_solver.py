from experiments.stable_ac.thickenable.neuwirth_paw_one_loop_solver import (
    classify_paw_one_loop_support,
    paw_one_loop_embedding_schemes,
    solve_paw_one_loop_spherical,
)
from experiments.stable_ac.thickenable.neuwirth_permutation_certificate import (
    enumerate_trace,
)


def test_paw_one_loop_solver_matches_factorial_positive():
    words = ("yx", "yxXX")
    support = classify_paw_one_loop_support(words)
    assert support.kind == "paw+1loop"
    assert support.loop_vertex != support.articulation
    schemes = paw_one_loop_embedding_schemes(support)
    assert len(schemes) == 8
    assert all(scheme.slot_partition_verified for scheme in schemes)

    rank = solve_paw_one_loop_spherical(words)
    factorial = enumerate_trace(words)
    assert factorial.expected_cases == 6
    assert len(factorial.accepting_orders) == 2
    assert rank.spherical is bool(factorial.accepting_orders)
    assert rank.spherical is True
    assert rank.witness is not None
    assert rank.witness.euler_characteristic == 2


def test_paw_one_loop_solver_matches_factorial_negative():
    words = ("XYyyX", "X")
    support = classify_paw_one_loop_support(words)
    assert support.kind == "paw+1loop"
    assert support.loop_vertex != support.articulation
    assert len(paw_one_loop_embedding_schemes(support)) == 4

    rank = solve_paw_one_loop_spherical(words)
    factorial = enumerate_trace(words)
    assert factorial.expected_cases == 4
    assert rank.spherical is bool(factorial.accepting_orders)
    assert rank.spherical is False
    assert rank.witness is None
    assert rank.counters.exhaustive


def test_paw_loop_positive_requires_gap_inside_triangle_class():
    words = ("x", "xxyxYy")
    rank = solve_paw_one_loop_spherical(words)
    factorial = enumerate_trace(words)
    assert factorial.expected_cases == 12
    assert len(factorial.accepting_orders) == 2
    assert rank.spherical is True
    assert rank.witness is not None
    assert "paw-gap-1-" in rank.witness.scheme
