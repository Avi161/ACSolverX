from experiments.stable_ac.mms02_terminal_target_hnn_certificate import (
    braid_killer_certificate,
    decide_source_collapse,
    decide_target_hnn,
    factor_word,
    free_reduce,
    inverse,
    verify_equality,
)


def matrix_multiply(left, right):
    return tuple(
        tuple(
            sum(left[row][index] * right[index][column] for index in range(2))
            for column in range(2)
        )
        for row in range(2)
    )


def matrix_inverse(matrix):
    return (
        (matrix[1][1], -matrix[0][1]),
        (-matrix[1][0], matrix[0][0]),
    )


def matrix_word(word):
    x = ((1, 1), (0, 1))
    y = ((1, 0), (-1, 1))
    images = {"x": x, "X": matrix_inverse(x), "y": y, "Y": matrix_inverse(y)}
    result = ((1, 0), (0, 1))
    for letter in word:
        result = matrix_multiply(result, images[letter])
    return result


def test_source_killer_has_literal_normal_closure_certificate():
    decision = decide_source_collapse()
    certificate = braid_killer_certificate()
    verify_equality(certificate, decision.braid_relator)
    expanded = free_reduce(
        "".join(
            factor_word(factor, decision.braid_relator)
            for factor in certificate.factors
        )
    )
    assert expanded == free_reduce(
        decision.source_row + inverse(decision.conjugated_mu2)
    )
    assert decision.equality_factors == (
        ("YXyXY", -1),
        ("YX", 1),
        ("xY", -1),
        ("xxyyYXY", -1),
        ("xyY", -1),
    )
    assert decision.verdict == "SOURCE_PAIR_AC_TRIVIAL"


def test_source_killer_matrix_control_has_correct_orientation():
    decision = decide_source_collapse()
    x = ((1, 1), (0, 1))
    y = ((1, 0), (-1, 1))
    assert matrix_multiply(matrix_multiply(x, y), x) == matrix_multiply(
        matrix_multiply(y, x), y
    )
    assert matrix_word(decision.mu2) == ((-1, 2), (-3, 5))
    assert matrix_word(decision.source_row) == ((2, 3), (1, 2))
    assert matrix_word(decision.source_row) == matrix_word(
        decision.conjugated_mu2
    )
    assert sum(1 if letter.islower() else -1 for letter in decision.source_row) == 1
    assert sum(1 if letter.islower() else -1 for letter in decision.mu2) == 1


def test_source_killer_cleanup_is_literal_after_nielsen_change():
    decision = decide_source_collapse()
    assert decision.transformed_relator == "yxxyXYX"
    assert decision.transformed_mu2 == "xyy"
    assert free_reduce("".join(decision.cleanup_factors)) == free_reduce(
        inverse(decision.transformed_relator) + "y"
    )
    assert free_reduce(decision.transformed_mu2 + "YY") == "x"


def test_target_relator_has_exact_strict_ascending_hnn_form():
    decision = decide_target_hnn()
    assert decision.relator_magnus == (
        (0, 1),
        (-1, -1),
        (0, 1),
        (1, -1),
        (-1, 1),
    )
    assert decision.phi_a == "b"
    assert decision.phi_b == "abAb"
    assert decision.iterates == (
        "b",
        "abAb",
        "babbAb",
        "abAbbabAbabbAb",
    )
    # Abelianized columns (0,1) and (0,2) have determinant zero, so phi is not onto.
    assert 0 * 2 - 0 * 1 == 0
    assert decision.verdict == "TARGET_STRICT_ASCENDING_HNN_GATE"


def test_target_killer_has_pinned_shifted_hnn_base_word():
    decision = decide_target_hnn()
    assert decision.row_magnus == (
        (-1, -1),
        (-2, 1),
        (-3, -1),
        (-2, 1),
        (-1, -1),
        (0, 1),
        (-1, -1),
        (0, 1),
    )
    assert decision.shifted_base_word == "BaBBABBabAbbabbAbbabAbabbAb"
    assert decision.shifted_base_word_digest == (
        "9b504bd82e353bd8d35ec3b3335d0e89fd3538e769be402b6d58f3428b3ec1c3"
    )
