from experiments.equivalence_classes.lib.words import (
    apply_hom,
    free_reduce as free_reduce_string,
    inv as inverse_string,
)
from experiments.stable_ac.mms02_terminal_fixed_row_class2_certificate import (
    ANNIHILATORS,
    BASE_CHANGE,
    C,
    D0,
    EXPECTED_AB_SOLUTION,
    EXPECTED_CLASS2_DEFECT,
    EXPECTED_E_SOURCE,
    EXPECTED_E_TARGET,
    EXPECTED_EXTERIOR_MATRIX,
    EXPECTED_MAGNUS_RELATOR,
    EXPECTED_PHI_MATRIX,
    EXPECTED_P_SOURCE,
    EXPECTED_P_TARGET,
    EXPECTED_R,
    EXPECTED_TRANSFORMED,
    EXPECTED_Y2_WORD,
    W,
    decide_terminal_fixed_row_class2,
)


def _inverse(word):
    return tuple(-letter for letter in reversed(word))


def _reduce(word):
    result = []
    for letter in word:
        if result and result[-1] == -letter:
            result.pop()
        else:
            result.append(letter)
    return tuple(result)


def _substitute(word, images):
    signed = dict(images)
    signed.update({-generator: _inverse(image) for generator, image in images.items()})
    return _reduce(tuple(letter for symbol in word for letter in signed[symbol]))


def _direct_magnus_degree_two(word):
    linear_letters = []
    diagonal = [[0] * 4 for _ in range(4)]
    for letter in word:
        index = abs(letter) - 1
        sign = 1 if letter > 0 else -1
        linear_letters.append((index, sign))
        if sign < 0:
            diagonal[index][index] += 1
    tensor = diagonal
    for left in range(len(linear_letters)):
        i, left_sign = linear_letters[left]
        for right in range(left + 1, len(linear_letters)):
            j, right_sign = linear_letters[right]
            tensor[i][j] += left_sign * right_sign
    linear = tuple(
        sum(sign for index, sign in linear_letters if index == generator)
        for generator in range(4)
    )
    return linear, tuple(tuple(row) for row in tensor)


def _exterior(word):
    linear, tensor = _direct_magnus_degree_two(word)
    assert linear == (0, 0, 0, 0)
    assert all(tensor[i][i] == 0 for i in range(4))
    assert all(tensor[i][j] == -tensor[j][i] for i in range(4) for j in range(4))
    return tuple(tensor[i][j] for i in range(4) for j in range(i + 1, 4))


def test_terminal_fixed_row_reduction_and_magnus_hnn_are_literal():
    rank_two_relator = free_reduce_string(D0 + "x" + inverse_string(D0) + inverse_string(W))
    source_row = free_reduce_string(inverse_string(D0) + "x")
    target_row = free_reduce_string(inverse_string(D0) + C)
    assert (rank_two_relator, source_row, target_row) == (
        EXPECTED_R,
        EXPECTED_E_SOURCE,
        EXPECTED_E_TARGET,
    )
    assert tuple(
        apply_hom(word, BASE_CHANGE)
        for word in (rank_two_relator, source_row, target_row)
    ) == EXPECTED_TRANSFORMED

    def occurrences(word):
        height = 0
        result = []
        for letter in word:
            if letter == "x":
                height += 1
            elif letter == "X":
                height -= 1
            else:
                generator = height + 3
                result.append(generator if letter == "y" else -generator)
        return tuple(result), height

    assert occurrences(EXPECTED_TRANSFORMED[0]) == (EXPECTED_MAGNUS_RELATOR, 0)
    assert occurrences(EXPECTED_TRANSFORMED[1]) == (EXPECTED_P_SOURCE, 1)
    assert occurrences(EXPECTED_TRANSFORMED[2]) == (EXPECTED_P_TARGET, 1)
    position = EXPECTED_MAGNUS_RELATOR.index(5)
    assert _reduce(
        _inverse(EXPECTED_MAGNUS_RELATOR[:position])
        + _inverse(EXPECTED_MAGNUS_RELATOR[position + 1 :])
    ) == EXPECTED_Y2_WORD


def test_terminal_fixed_row_class_two_obstruction_is_independent():
    phi_images = {1: (2,), 2: (3,), 3: (4,), 4: EXPECTED_Y2_WORD}
    matrix = tuple(
        tuple(
            sum(
                1 if letter == row + 1 else -1 if letter == -(row + 1) else 0
                for letter in phi_images[column + 1]
            )
            for column in range(4)
        )
        for row in range(4)
    )
    assert matrix == EXPECTED_PHI_MATRIX
    difference = tuple(
        sum(
            (matrix[row][column] - (row == column))
            * EXPECTED_AB_SOLUTION[column]
            for column in range(4)
        )
        for row in range(4)
    )
    assert difference == (0, 0, -1, 2)

    k0 = (1, -2, -2, 3, 3, 3, 3, -4)
    defect = _reduce(
        _inverse(k0)
        + EXPECTED_P_SOURCE
        + _substitute(k0, phi_images)
        + _inverse(EXPECTED_P_TARGET)
    )
    assert _exterior(defect) == EXPECTED_CLASS2_DEFECT

    pairs = tuple((i, j) for i in range(1, 5) for j in range(i + 1, 5))
    columns = []
    for i, j in pairs:
        commutator = (i, j, -i, -j)
        columns.append(
            _exterior(
                _reduce(_inverse(commutator) + _substitute(commutator, phi_images))
            )
        )
    correction_matrix = tuple(
        tuple(columns[column][row] for column in range(6))
        for row in range(6)
    )
    assert correction_matrix == EXPECTED_EXTERIOR_MATRIX
    for functional, value in zip(ANNIHILATORS, (-2, 3), strict=True):
        assert all(
            sum(functional[row] * correction_matrix[row][column] for row in range(6))
            == 0
            for column in range(6)
        )
        assert sum(
            functional[index] * EXPECTED_CLASS2_DEFECT[index]
            for index in range(6)
        ) == value

    decision = decide_terminal_fixed_row_class2()
    assert decision.phi_minus_identity_determinant == 1
    assert decision.obstruction_values == (-2, 3)
    assert decision.verdict == "NO_FIXED_R_RELATIVE_AC_PATH"
