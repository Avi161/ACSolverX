from collections import defaultdict


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


def test_second_derived_fox_correction_and_direct_limit():
    d = "bbAbaB"
    delta = "bAbABaBB"
    images = {"a": "b", "A": "B", "b": d, "B": inv(d)}

    def phi(word):
        return product(*(images[letter] for letter in word))

    assert phi("a") == "b"
    assert phi("b") == d
    assert delta == "bAbABaBB"

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
