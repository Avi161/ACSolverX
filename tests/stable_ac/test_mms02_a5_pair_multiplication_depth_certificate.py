from experiments.stable_ac.mms02_a5_pair_multiplication_depth_certificate import (
    decide_pair_multiplication_depth,
)
from experiments.stable_ac.mms02_fixed_b_a5_conjugacy_certificate import (
    IDENTITY,
    compose,
    evaluate_word,
    inverse,
)


def test_a5_pair_depth_is_complete_and_equals_four():
    decision = decide_pair_multiplication_depth()
    assert decision.minimum_depth == 4
    assert decision.verdict == "FOUR_A5_VISIBLE_MULTIPLICATIONS_REQUIRED"


def test_a5_pair_shortest_transcript_replays_literally():
    decision = decide_pair_multiplication_depth()
    source = evaluate_word("zYX")
    target = evaluate_word("Xyz")
    x_value = decision.normalized_cycle
    square = compose(x_value, x_value)
    cube = compose(x_value, square)
    assert decision.transcript[0] == (source, IDENTITY)
    assert decision.transcript[1] == (source, source)
    assert decision.transcript[2] == (x_value, x_value)
    assert decision.transcript[3] == (square, x_value)
    assert decision.transcript[4] == (square, cube)
    assert decision.transcript[5] == (target, IDENTITY)
    assert square == target
    assert cube == inverse(target)
    assert compose(cube, target) == IDENTITY


def test_a5_pair_shortest_transcript_has_wrong_actual_homology():
    decision = decide_pair_multiplication_depth()
    assert decision.nielsen_matrix == ((2, 1), (5, 3))
    assert decision.source_homology_image == (-2, -5)
    assert decision.source_homology_image != (1, 0)


def test_three_multiplications_cannot_change_the_split_class_and_clear_buffer():
    decision = decide_pair_multiplication_depth()
    source_class_representative = decision.transcript[0][0]
    target_class_representative = decision.transcript[-1][0]
    assert source_class_representative != target_class_representative
    assert decision.minimum_depth > 3
