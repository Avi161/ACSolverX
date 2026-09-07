"""Finite Laurent coefficient calculation for the saved folded lift factors."""

from pathlib import Path
import runpy


SUPPORT_CAP = 100_000
MAX_SUPPORT = 0


def check_support(polynomial):
    global MAX_SUPPORT
    size = len(polynomial)
    if size > SUPPORT_CAP:
        raise RuntimeError(f"Laurent support {size} exceeds cap {SUPPORT_CAP}")
    MAX_SUPPORT = max(MAX_SUPPORT, size)
    return polynomial


def accumulate(polynomial, exponent, coefficient):
    value = polynomial.get(exponent, 0) + coefficient
    if value:
        polynomial[exponent] = value
    else:
        polynomial.pop(exponent, None)
    check_support(polynomial)


def add(left, right, sign=1):
    result = dict(left)
    check_support(result)
    for exponent, coefficient in right.items():
        accumulate(result, exponent, sign * coefficient)
    return result


def multiply(left, right):
    result = {}
    for (r1, l1), a in left.items():
        for (r2, l2), b in right.items():
            accumulate(result, (r1 + r2, l1 + l2), a * b)
    return result


def matrix_identity():
    return [[{(0, 0): 1}, {}], [{}, {(0, 0): 1}]]


def matrix_multiply(left, right):
    return [[add(multiply(left[i][0], right[0][j]),
                 multiply(left[i][1], right[1][j]))
             for j in range(2)] for i in range(2)]


def direct_kernel_gradient(word):
    derivatives = [{}, {}]
    r = l = 0
    for letter in word:
        if letter in "rR":
            r += 1 if letter == "r" else -1
        elif letter in "lL":
            l += 1 if letter == "l" else -1
        elif letter in "sSmM":
            row = 0 if letter.lower() == "s" else 1
            accumulate(derivatives[row], (r, l), 1 if letter.islower() else -1)
        else:
            raise ValueError(f"Unknown folded generator: {letter!r}")
    return derivatives


def full_abelian_gradient(word):
    alphabet = "rslm"
    exponents = [0, 0, 0, 0]
    derivatives = [{}, {}, {}, {}]
    for letter in word:
        index = alphabet.index(letter.lower())
        if letter.isupper():
            exponents[index] -= 1
            exponent = tuple(exponents)
            coefficient = -1
        else:
            exponent = tuple(exponents)
            coefficient = 1
            exponents[index] += 1
        polynomial = derivatives[index]
        polynomial[exponent] = polynomial.get(exponent, 0) + coefficient
        if polynomial[exponent] == 0:
            del polynomial[exponent]
        check_support(polynomial)
    return derivatives


def specialize(polynomial):
    result = {}
    for (r, _s, l, _m), coefficient in polynomial.items():
        accumulate(result, (r, l), coefficient)
    return result


def kernel_matrix(mapping, substitute):
    """Rows are s,m derivatives; columns are the images of s,m."""
    erase = {"r": "r", "s": "", "l": "l", "m": ""}
    assert substitute(mapping["s"], erase) == ""
    assert substitute(mapping["m"], erase) == ""
    columns = []
    for generator in "sm":
        word = mapping[generator]
        direct = direct_kernel_gradient(word)
        full = full_abelian_gradient(word)
        assert direct == [specialize(full[1]), specialize(full[3])]
        columns.append(direct)
    return [[columns[j][i] for j in range(2)] for i in range(2)]


def quotient_exponents(word):
    return (word.count("r") - word.count("R"), word.count("l") - word.count("L"))


def fixed_point_determinant(matrix):
    unit = matrix_identity()
    difference = [[add(matrix[i][j], unit[i][j], -1) for j in range(2)] for i in range(2)]
    return add(multiply(difference[0][0], difference[1][1]),
               multiply(difference[0][1], difference[1][0]), -1)


def test_folded_fixed_point_kernel_replacement_has_nonunit_determinant():
    source = Path(__file__).with_name("test_ak3_folded_boundary_lift.py")
    saved = runpy.run_path(str(source))
    compose = saved["compose"]
    substitute = saved["substitute"]
    factors = saved["push_factors"]()
    assert saved["W_STANDARD"] == "LRlrlR"
    matrices = {}
    for letter, factor in factors.items():
        assert quotient_exponents(factor["r"]) == (1, 0)
        assert quotient_exponents(factor["l"]) == (0, 1)
        matrices[letter] = kernel_matrix(factor, substitute)
        boundary_vector = [{(1, 0): 1, (0, 0): -1}, {(0, 1): 1, (0, 0): -1}]
        assert [add(multiply(matrices[letter][i][0], boundary_vector[0]),
                    multiply(matrices[letter][i][1], boundary_vector[1]))
                for i in range(2)] == boundary_vector
    folded_phi0 = compose(saved["ORIGINAL_IN_STANDARD"], saved["PHI0"], saved["STANDARD_IN_ORIGINAL"])
    phi0_matrix = kernel_matrix(folded_phi0, substitute)
    assert matrices["r"] == [
        [{(0, 0): 1}, {}],
        [{(-1, 1): 1, (-1, 0): -1}, {(-1, 0): 1}],
    ]
    assert matrices["l"] == [
        [{(0, -1): 1}, {(1, -1): 1, (0, -1): -1}],
        [{}, {(0, 0): 1}],
    ]
    assert phi0_matrix == [
        [{(0, 0): 1}, {(0, -1): 1}],
        [{(0, 1): -1}, {}],
    ]
    for positive, negative in (("r", "R"), ("l", "L")):
        assert matrix_multiply(matrices[positive], matrices[negative]) == matrix_identity()
        assert matrix_multiply(matrices[negative], matrices[positive]) == matrix_identity()

    composed_pair = compose(factors["r"], factors["l"])
    assert kernel_matrix(composed_pair, substitute) == matrix_multiply(matrices["r"], matrices["l"])

    push_matrix = matrix_identity()
    for letter in saved["W_STANDARD"]:
        push_matrix = matrix_multiply(matrices[letter], push_matrix)
    total = matrix_multiply(push_matrix, phi0_matrix)
    determinant = fixed_point_determinant(total)
    assert determinant == {
        (0, -2): -1, (0, -1): 1, (0, 0): -1, (0, 1): 1,
        (1, -1): 1, (1, 1): -1, (2, 1): 1,
    }
    assert sum(determinant.values()) == 1
    assert len(determinant) == 7
    assert not (len(determinant) == 1 and abs(next(iter(determinant.values()))) == 1)
    assert fixed_point_determinant(phi0_matrix) == {(0, 0): 1}
