"""One exact symbolic trace checkpoint over Z[s,s^-1,d]."""

import json

ZERO = {}
ONE = {(0, 0): 1}
S = {(1, 0): 1}
S_INVERSE = {(-1, 0): 1}
D = {(0, 1): 1}
A_BAR = "xYxYXyyXYxyXy"
B_BAR = "XyyXYXyxYYxy"


def add(*polynomials):
    result = {}
    for polynomial in polynomials:
        for exponent, coefficient in polynomial.items():
            result[exponent] = result.get(exponent, 0) + coefficient
    return {exponent: coefficient for exponent, coefficient in result.items() if coefficient}


def negate(polynomial):
    return {exponent: -coefficient for exponent, coefficient in polynomial.items() if coefficient}


def multiply(left, right):
    result = {}
    for (left_s, left_d), left_coefficient in left.items():
        for (right_s, right_d), right_coefficient in right.items():
            exponent = (left_s + right_s, left_d + right_d)
            result[exponent] = result.get(exponent, 0) + left_coefficient * right_coefficient
    return {exponent: coefficient for exponent, coefficient in result.items() if coefficient}


def matrix_multiply(left, right):
    a, b, c, d = left
    e, f, g, h = right
    return (add(multiply(a, e), multiply(b, g)), add(multiply(a, f), multiply(b, h)),
            add(multiply(c, e), multiply(d, g)), add(multiply(c, f), multiply(d, h)))


def matrix_inverse(matrix):
    a, b, c, d = matrix
    return d, negate(b), negate(c), a


def determinant(matrix):
    a, b, c, d = matrix
    return add(multiply(a, d), negate(multiply(b, c)))


def word_matrix(word, x, y):
    images = {"x": x, "y": y, "X": matrix_inverse(x), "Y": matrix_inverse(y)}
    value = (ONE, ZERO, ZERO, ONE)
    for letter in word:
        value = matrix_multiply(value, images[letter])
    return value


def coefficients(polynomial):
    return [[s_exponent, d_exponent, coefficient]
            for (s_exponent, d_exponent), coefficient in sorted(polynomial.items())]


def data():
    s_squared = multiply(S, S)
    x = (S, ZERO, ZERO, S_INVERSE)
    y = (add(ONE, negate(multiply(s_squared, D))), ONE,
         add(multiply(D, add(ONE, negate(s_squared))), negate(multiply(s_squared, multiply(D, D)))),
         add(ONE, D))
    a_matrix, b_matrix = word_matrix(A_BAR, x, y), word_matrix(B_BAR, x, y)
    inverse_x_y = word_matrix("Xy", x, y)
    identity = (ONE, ZERO, ZERO, ONE)
    return {
        "ring": "Z[s,s^-1,d]",
        "coefficient_entry_order": ["s_exponent", "d_exponent", "coefficient"],
        "matrix_entry_order": ["00", "01", "10", "11"],
        "words": {"Abar": A_BAR, "Bbar": B_BAR},
        "Abar_minus_identity": [coefficients(add(entry, negate(unit))) for entry, unit in zip(a_matrix, identity, strict=True)],
        "trace_Bbar": coefficients(add(b_matrix[0], b_matrix[3])),
        "determinant_y_minus_one": coefficients(add(determinant(y), negate(ONE))),
        "trace_Xy_minus_trace_x": coefficients(add(inverse_x_y[0], inverse_x_y[3], negate(x[0]), negate(x[3]))),
    }


if __name__ == "__main__":
    print(json.dumps(data(), sort_keys=True))
