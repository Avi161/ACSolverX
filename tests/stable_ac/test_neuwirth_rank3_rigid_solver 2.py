import json

from experiments.stable_ac.rank3_compression.primitive_single_certificate import (
    RESULT_PATH as PRIMITIVE_SINGLE_PATH,
)
from experiments.stable_ac.thickenable.neuwirth_permutation_certificate import (
    enumerate_trace,
)
from experiments.stable_ac.thickenable.neuwirth_rank3_rigid_solver import (
    classify_rigid_support,
    rigid_embedding_scheme,
    solve_rigid_spherical,
)


def test_primitive_free_source_has_the_two_reflected_rigid_rotations():
    with PRIMITIVE_SINGLE_PATH.open() as handle:
        data = json.load(handle)
    words = tuple(data["sources"][250])
    support = classify_rigid_support(words)
    assert support.kind == "K6-P5"
    assert len(support.simple_edges) == 11
    assert len(support.macro_rotations) == 2
    assert all(
        tuple(reversed(left)) == right
        for left, right in zip(
            support.macro_rotations[0],
            support.macro_rotations[1],
        )
    )
    scheme = rigid_embedding_scheme(support)
    assert scheme.slot_partition_verified


def test_rigid_rank_solver_matches_affordable_factorial_negative():
    words = ("XZXTz", "ZTxZZ", "ttXzX")
    rank = solve_rigid_spherical(words)
    factorial = enumerate_trace(words)
    assert factorial.expected_cases == 17_280
    assert rank.support.kind == "K6-P5"
    assert rank.spherical is bool(factorial.accepting_orders)
    assert rank.spherical is False
    assert rank.witness is None
    assert rank.counters.exhaustive
