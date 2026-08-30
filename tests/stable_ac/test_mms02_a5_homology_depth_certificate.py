from experiments.stable_ac.mms02_a5_homology_depth_certificate import (
    DEPTH_FIVE_WITNESS_CONJUGATORS,
    DEPTH_FIVE_WITNESS_MATRIX,
    DEPTH_FIVE_WITNESS_MOVES,
    EXPECTED_COMPATIBLE_MATRICES,
    EXPECTED_LAYER_SIZES,
    IDENTITY_MATRIX,
    decide_homology_compatible_depth,
    depth_five_witness_matrix,
    depth_five_witness_pairs,
    matrix_multiply,
)
from experiments.stable_ac.mms02_fixed_b_a5_conjugacy_certificate import (
    IDENTITY,
    compose,
    conjugate,
    inverse,
)


def test_homology_compatible_layers_are_complete_through_depth_five():
    decision = decide_homology_compatible_depth()
    assert decision.layer_sizes == EXPECTED_LAYER_SIZES
    assert decision.first_compatible_depth == 5


def test_no_depth_four_a5_path_can_lift_through_actual_homology():
    decision = decide_homology_compatible_depth()
    assert decision.layer_sizes[:5] == (8, 32, 272, 1896, 7056)
    assert decision.first_compatible_depth > 4


def test_depth_five_contains_the_complete_homology_stabilizer_fiber():
    decision = decide_homology_compatible_depth()
    assert decision.compatible_matrices == EXPECTED_COMPATIBLE_MATRICES
    assert len(decision.compatible_matrices) == 14
    assert IDENTITY_MATRIX in decision.compatible_matrices
    assert decision.identity_matrix_reached


def test_homology_depth_scope_verdict_is_pinned():
    decision = decide_homology_compatible_depth()
    assert (
        decision.verdict
        == "FIVE_TOTAL_ROW_MULTIPLICATIONS_REQUIRED_IN_COMBINED_SHADOW"
    )


def test_explicit_depth_five_witness_replays_in_a5():
    pairs = depth_five_witness_pairs()
    assert DEPTH_FIVE_WITNESS_MOVES == ("R2+", "R1-", "R2+", "R1+", "R2-")
    assert pairs == (
        ((3, 4, 0, 1, 2), IDENTITY),
        ((3, 4, 0, 1, 2), (3, 4, 0, 1, 2)),
        ((3, 4, 0, 1, 2), (2, 3, 4, 0, 1)),
        ((1, 2, 3, 4, 0), (2, 3, 4, 0, 1)),
        ((2, 0, 4, 1, 3), (3, 4, 1, 2, 0)),
        ((2, 0, 4, 1, 3), (1, 3, 0, 4, 2)),
        ((3, 2, 0, 4, 1), (1, 2, 3, 4, 0)),
        ((2, 0, 4, 1, 3), (1, 2, 3, 4, 0)),
        ((2, 0, 4, 1, 3), (2, 0, 4, 1, 3)),
        ((2, 0, 4, 1, 3), IDENTITY),
    )
    assert pairs[1][1] == compose(pairs[0][1], pairs[0][0])
    assert pairs[3][0] == compose(pairs[2][0], inverse(pairs[2][1]))
    assert pairs[5][1] == compose(pairs[4][1], pairs[4][0])
    assert pairs[7][0] == compose(pairs[6][0], pairs[6][1])
    assert pairs[9][1] == compose(pairs[8][1], inverse(pairs[8][0]))

    conjugated_rows = (
        (pairs[1][1], pairs[2][1]),
        (pairs[3][0], pairs[4][0]),
        (pairs[3][1], pairs[4][1]),
        (pairs[5][0], pairs[6][0]),
        (pairs[5][1], pairs[6][1]),
        (pairs[7][1], pairs[8][1]),
    )
    for conjugator, (source, target) in zip(
        DEPTH_FIVE_WITNESS_CONJUGATORS, conjugated_rows, strict=True
    ):
        assert conjugate(conjugator, source) == target


def test_explicit_depth_five_witness_preserves_source_homology():
    moves = (
        (1, 0, 1, 1),
        (1, -1, 0, 1),
        (1, 0, 1, 1),
        (1, 1, 0, 1),
        (1, 0, -1, 1),
    )
    matrix = IDENTITY_MATRIX
    for move in moves:
        matrix = matrix_multiply(move, matrix)
    assert matrix == DEPTH_FIVE_WITNESS_MATRIX == (1, -1, 0, 1)
    assert depth_five_witness_matrix() == matrix
    assert (matrix[0], matrix[2]) == (1, 0)
    assert decide_homology_compatible_depth().witness_matrix == matrix
