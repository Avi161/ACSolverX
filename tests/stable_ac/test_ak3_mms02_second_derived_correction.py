from collections import defaultdict
from fractions import Fraction


def clean(terms):
    return {key: value for key, value in terms.items() if value}


def add(*polynomials):
    result = defaultdict(int)
    for polynomial in polynomials:
        for exponent, coefficient in polynomial.items():
            result[exponent] += coefficient
    return clean(result)


def neg(polynomial):
    return {exponent: -coefficient for exponent, coefficient in polynomial.items()}


def mul(left, right):
    result = defaultdict(int)
    for (left_a, left_b), left_coefficient in left.items():
        for (right_a, right_b), right_coefficient in right.items():
            result[(left_a + right_a, left_b + right_b)] += left_coefficient * right_coefficient
    return clean(result)


def monomial(a_exponent, b_exponent, coefficient=1):
    return {} if coefficient == 0 else {(a_exponent, b_exponent): coefficient}


def red(word):
    inverse = {"a": "A", "A": "a", "b": "B", "B": "b"}
    stack = []
    for letter in word:
        if stack and inverse[letter] == stack[-1]:
            stack.pop()
        else:
            stack.append(letter)
    return "".join(stack)


def inv(word):
    return "".join(letter.swapcase() for letter in reversed(word))


def product(*words):
    return red("".join(words))


def free_red(word):
    stack = []
    for letter in word:
        if stack and stack[-1] == letter.swapcase():
            stack.pop()
        else:
            stack.append(letter)
    return "".join(stack)


def free_product(*words):
    return free_red("".join(words))


def free_conjugate(conjugator, word):
    return free_product(conjugator, word, inv(conjugator))


def magnus_scan(word):
    height = 0
    result = []
    for letter in free_red(word):
        if letter == "x":
            height += 1
        elif letter == "X":
            height -= 1
        elif letter == "y":
            result.append((height, 1))
        elif letter == "Y":
            result.append((height, -1))
        else:
            raise AssertionError(f"unexpected Magnus letter: {letter}")
    assert height == 0
    return tuple(result)


def exponent(word):
    return word.count("a") - word.count("A"), word.count("b") - word.count("B")


def fox(word):
    derivative_a, derivative_b = {}, {}
    a_exponent = b_exponent = 0
    for letter in red(word):
        prefix = monomial(a_exponent, b_exponent)
        if letter == "a":
            derivative_a = add(derivative_a, prefix)
            a_exponent += 1
        elif letter == "A":
            a_exponent -= 1
            derivative_a = add(derivative_a, neg(monomial(a_exponent, b_exponent)))
        elif letter == "b":
            derivative_b = add(derivative_b, prefix)
            b_exponent += 1
        else:
            b_exponent -= 1
            derivative_b = add(derivative_b, neg(monomial(a_exponent, b_exponent)))
    return derivative_a, derivative_b


def alpha(polynomial):
    result = defaultdict(int)
    for (a_exponent, b_exponent), coefficient in polynomial.items():
        result[(0, a_exponent + 2 * b_exponent)] += coefficient
    return clean(result)


def augmentation(polynomial):
    return sum(polynomial.values())


def poly_mul(left, right):
    result = defaultdict(int)
    for left_exponent, left_coefficient in left.items():
        for right_exponent, right_coefficient in right.items():
            result[left_exponent + right_exponent] += left_coefficient * right_coefficient
    return clean(result)


def P_q(q):
    result = {0: 1}
    for power in range(q.bit_length() - 2):
        result = poly_mul(result, {0: 1, 2**power: -1})
    return result


def coefficient_equation(degree, s):
    """Coefficient of the reduced Mahler equation as a linear form in h_i."""
    expression = defaultdict(int)
    if degree >= 3 * s:
        expression[(degree - 3 * s, "h")] += 1
    if degree % 2 == 0:
        expression[(degree // 2, "h")] -= 1
    if degree >= 2 * s and (degree - 2 * s) % 2 == 0:
        expression[((degree - 2 * s) // 2, "h")] += 1
    return clean(expression)


def substitute(expression, values):
    constant = 0
    remaining = {}
    for key, coefficient in expression.items():
        if key[1] == "h" and key[0] in values:
            constant += coefficient * values[key[0]]
        else:
            remaining[key] = coefficient
    return constant, clean(remaining)


def semidirect_multiply(left, right):
    left_coordinate, left_height = left
    right_coordinate, right_height = right
    return (
        left_coordinate + Fraction(2) ** left_height * right_coordinate,
        left_height + right_height,
    )


def semidirect_inverse(element):
    coordinate, height = element
    return -Fraction(2) ** (-height) * coordinate, -height


def semidirect_power(element, exponent_value):
    if exponent_value < 0:
        return semidirect_power(semidirect_inverse(element), -exponent_value)
    result = (Fraction(0), 0)
    base = element
    while exponent_value:
        if exponent_value & 1:
            result = semidirect_multiply(result, base)
        base = semidirect_multiply(base, base)
        exponent_value //= 2
    return result


def semidirect_conjugate(conjugator, element):
    return semidirect_multiply(
        semidirect_multiply(conjugator, element), semidirect_inverse(conjugator)
    )


def test_second_derived_fox_correction_and_direct_limit():
    d = "bbAbaB"
    d_inverse = inv(d)
    gate_a_defect = "YXyyXYxyxY"
    shifted_gate_a_defect = free_conjugate("xx", gate_a_defect)
    shifted_scan = magnus_scan(shifted_gate_a_defect)
    assert shifted_scan == (
        (2, -1),
        (1, 1),
        (1, 1),
        (0, -1),
        (1, 1),
        (2, -1),
    )
    base_letters = {0: "a", 1: "b", 2: "d"}
    shifted_base_word = "".join(
        base_letters[index] if sign > 0 else base_letters[index].upper()
        for index, sign in shifted_scan
    )
    assert shifted_base_word == "DbbAbD"
    delta = product(
        *(d_inverse if letter == "D" else letter for letter in shifted_base_word)
    )
    images = {"a": "b", "A": "B", "b": d, "B": inv(d)}

    def phi(word):
        return product(*(images[letter] for letter in word))

    assert phi("a") == "b"
    assert phi("b") == d
    assert delta == "bAbABaBB"

    q_word = "Xy"
    b_word = free_product(q_word, inv(gate_a_defect))
    e_word = free_product(
        inv(gate_a_defect),
        q_word,
        gate_a_defect,
        inv(b_word),
    )
    assert e_word == free_product(
        inv(gate_a_defect),
        q_word,
        gate_a_defect,
        gate_a_defect,
        inv(q_word),
    )
    shifted_q = free_conjugate("xx", q_word)
    shifted_e = free_conjugate("xx", e_word)
    assert shifted_q == free_product("xyX", "X")
    assert shifted_e == free_product(
        inv(shifted_gate_a_defect),
        shifted_q,
        shifted_gate_a_defect,
        shifted_gate_a_defect,
        inv(shifted_q),
    )

    epsilon = product(inv(phi(delta)), d, delta, delta, inv(d))
    zeta = phi(epsilon)
    assert exponent(epsilon) == (-2, 1)
    assert exponent(zeta) == (0, 0)

    f = {(-1, 10): -1, (-1, 12): 1, (-1, 14): -1}
    fox_a, fox_b = fox(zeta)
    assert fox_a == mul(f, {(0, 0): 1, (0, 1): -1})
    assert fox_b == mul(f, {(1, 0): 1, (0, 0): -1})

    phi_a = fox(phi("a"))
    phi_b = fox(phi("b"))
    determinant = add(mul(phi_a[0], phi_b[1]), neg(mul(phi_a[1], phi_b[0])))
    assert determinant == {(-1, 2): 1, (-1, 3): -1}
    assert augmentation(determinant) == 0
    phi_commutator_fox = fox(phi("abAB"))
    assert phi_commutator_fox == (
        mul(determinant, {(0, 0): 1, (0, 1): -1}),
        mul(determinant, {(1, 0): 1, (0, 0): -1}),
    )

    u = product(d, inv(delta))
    assert exponent(u) == (1, 3)
    for iteration in range(1, 7):
        u_image = monomial(1, 3)
        for _ in range(iteration):
            u_image = alpha(u_image)
        assert u_image == monomial(0, 7 * 2 ** (iteration - 1))

    alpha_f = alpha(f)
    assert alpha_f == {(0, 19): -1, (0, 23): 1, (0, 27): -1}
    direct_limit_image = f
    for _ in range(4):
        direct_limit_image = mul(determinant, alpha(direct_limit_image))
        assert direct_limit_image
    assert alpha(alpha_f) == {(0, 38): -1, (0, 46): 1, (0, 54): -1}


def test_reduced_mahler_coefficient_contradiction_at_four_scales():
    for q in (4, 8, 16, 32):
        s = q // 4
        p_q = P_q(q)
        # P_Q(z^2) = P_Q(z)(1-z^(Q/2))/(1-z), checked after multiplying by 1-z.
        p_q_at_z_squared = {2 * exponent: coefficient for exponent, coefficient in p_q.items()}
        assert poly_mul({0: 1, 1: -1}, p_q_at_z_squared) == poly_mul(
            p_q, {0: 1, q // 2: -1}
        )

        rhs = {0: -1, 4 * s: 1, 8 * s: -1}
        values = {}

        constant, remaining = substitute(coefficient_equation(0, s), values)
        assert (constant, remaining, rhs[0]) == (0, {(0, "h"): -1}, -1)
        values[0] = 1

        constant, remaining = substitute(coefficient_equation(2 * s, s), values)
        assert (constant, remaining, rhs.get(2 * s, 0)) == (1, {(s, "h"): -1}, 0)
        values[s] = 1

        constant, remaining = substitute(coefficient_equation(4 * s, s), values)
        assert (constant, remaining, rhs[4 * s]) == (2, {(2 * s, "h"): -1}, 1)
        values[2 * s] = 1

        constant, remaining = substitute(coefficient_equation(6 * s, s), values)
        assert (constant, remaining, rhs.get(6 * s, 0)) == (1, {}, 0)


def test_second_derived_fraction_semidirect_conjugator_family():
    q = (Fraction(1, 2), -1)
    D = (Fraction(-3, 4), 0)
    B = (Fraction(7, 8), -1)
    c0 = (Fraction(3, 4), 0)
    assert semidirect_inverse(D) == c0
    assert semidirect_conjugate(c0, q) == B

    for k in range(-12, 13):
        two_to_k = Fraction(2) ** k
        expected_m = 1 - two_to_k
        residual_at_zero = semidirect_multiply((Fraction(0), k), q)[0] - semidirect_multiply(
            q, (Fraction(0), k)
        )[0]
        residual_at_one = semidirect_multiply((Fraction(1), k), q)[0] - semidirect_multiply(
            q, (Fraction(1), k)
        )[0]
        slope = residual_at_one - residual_at_zero
        assert slope == Fraction(1, 2)
        assert -residual_at_zero / slope == expected_m
        left = semidirect_multiply((expected_m, k), q)
        right = semidirect_multiply(q, (expected_m, k))
        assert left == right
        assert semidirect_power(q, -k) == (expected_m, k)

    for power in range(-12, 13):
        conjugator = semidirect_multiply(c0, semidirect_power(q, power))
        assert semidirect_conjugate(conjugator, q) == B
