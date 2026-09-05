from fractions import Fraction

from experiments.stable_ac.mms02_primitive_trace_probe import data


def matrix_product(left, right):
    return [[sum(left[row][index] * right[index][column] for index in range(2))
             for column in range(2)] for row in range(2)]


def determinant(matrix):
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def matrix_inverse(matrix):
    value = determinant(matrix)
    return [[matrix[1][1] / value, -matrix[0][1] / value],
            [-matrix[1][0] / value, matrix[0][0] / value]]


def evaluate_word(word, x, y):
    images = {"x": x, "X": matrix_inverse(x), "y": y, "Y": matrix_inverse(y)}
    value = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)]]
    for letter in word:
        value = matrix_product(value, images[letter])
    return value


def test_trace_probe_coefficients_match_independent_rational_matrices():
    checkpoint = data()
    assert checkpoint["words"] == {"Abar": "xYxYXyyXYxyXy", "Bbar": "XyyXYXyxYYxy"}
    assert checkpoint["determinant_y_minus_one"] == []
    assert checkpoint["trace_Xy_minus_trace_x"] == []
    for s_value, d_value in ((2, 0), (2, 1), (3, -1)):
        s, d = Fraction(s_value), Fraction(d_value)
        x = [[s, Fraction(0)], [Fraction(0), 1 / s]]
        y = [[1 - s * s * d, Fraction(1)], [d * (1 - s * s) - s * s * d * d, 1 + d]]

        def coefficients_value(terms):
            return sum((coefficient * s ** s_exponent * d ** d_exponent
                        for s_exponent, d_exponent, coefficient in terms), Fraction(0))

        a_matrix = evaluate_word("xYxYXyyXYxyXy", x, y)
        b_matrix = evaluate_word("XyyXYXyxYYxy", x, y)
        direct_difference = [a_matrix[row][column] - int(row == column)
                             for row in range(2) for column in range(2)]
        assert [coefficients_value(terms) for terms in checkpoint["Abar_minus_identity"]] == direct_difference
        assert coefficients_value(checkpoint["trace_Bbar"]) == b_matrix[0][0] + b_matrix[1][1]
        assert determinant(x) == determinant(y) == 1
        assert coefficients_value(checkpoint["determinant_y_minus_one"]) == determinant(y) - 1 == 0
        initial = evaluate_word("Xy", x, y)
        difference = initial[0][0] + initial[1][1] - x[0][0] - x[1][1]
        assert coefficients_value(checkpoint["trace_Xy_minus_trace_x"]) == difference == 0
        if (s_value, d_value) == (2, 0):
            assert any(direct_difference)
            assert a_matrix != [[1, 0], [0, 1]]


def test_trace_constraint_has_exact_integer_coefficient_factorization():
    def add(*values):
        coefficients = [0] * max(map(len, values))
        for value in values:
            for index, coefficient in enumerate(value):
                coefficients[index] += coefficient
        while len(coefficients) > 1 and coefficients[-1] == 0:
            coefficients.pop()
        return coefficients

    def multiply(left, right):
        coefficients = [0] * (len(left) + len(right) - 1)
        for i, a in enumerate(left):
            for j, b in enumerate(right):
                coefficients[i + j] += a * b
        return coefficients

    z, z_squared, c = [0, 1], [0, 0, 1], [0, -1, 1]
    expression = add(z_squared, multiply(c, c), [-entry for entry in multiply(z_squared, c)], z, [-2])
    factored = [-entry for entry in multiply(multiply([-2, 1], [-1, 1]), [1, 1])]
    assert expression == factored == [-2, 1, 2, -1]


def test_hnn_trace_words_are_cyclically_equal_not_freely_equal():
    def reduced(word):
        stack = []
        for letter in word:
            if stack and stack[-1].swapcase() == letter:
                stack.pop()
            else:
                stack.append(letter)
        return "".join(stack)

    def cyclic_peel(word):
        word = reduced(word)
        while len(word) > 1 and word[0].swapcase() == word[-1]:
            word = word[1:-1]
        return word

    phi_b = "bbAbaB"
    phi_ab = "b" + phi_b
    assert reduced(phi_b) == "bbAbaB" != "bAba"
    assert reduced(phi_ab) == "bbbAbaB" != "bbAba"
    assert cyclic_peel(phi_b) == "bAba"
    assert cyclic_peel(phi_ab) == "bbAba"
    assert reduced("B" + phi_b + "b") == "bAba"
    assert reduced("B" + phi_ab + "b") == "bbAba"
