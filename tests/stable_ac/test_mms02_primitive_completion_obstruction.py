def inverse(word):
    return word[::-1].swapcase()


def reduced(word):
    stack = []
    for letter in word:
        if stack and stack[-1] == letter.swapcase():
            stack.pop()
        else:
            stack.append(letter)
    return "".join(stack)


def power(word, exponent):
    return reduced((word if exponent >= 0 else inverse(word)) * abs(exponent))


def phi(word):
    images = {"a": "b", "A": "B", "b": "bbAbaB", "B": "bABaBB"}
    return reduced("".join(images[letter] for letter in word))


def fox_abelian(word, generator):
    exponents = {"a": 0, "b": 0}
    derivative = {}
    for letter in word:
        base = letter.lower()
        sign = 1 if letter.islower() else -1
        if base == generator and sign == 1:
            key = (exponents["a"], exponents["b"])
            derivative[key] = derivative.get(key, 0) + 1
        exponents[base] += sign
        if base == generator and sign == -1:
            key = (exponents["a"], exponents["b"])
            derivative[key] = derivative.get(key, 0) - 1
    return {key: value for key, value in derivative.items() if value}, (exponents["a"], exponents["b"])


def specialize(derivative):
    result = {}
    for (a_exponent, b_exponent), coefficient in derivative.items():
        exponent = a_exponent + 2 * b_exponent
        result[exponent] = result.get(exponent, 0) + coefficient
    return {key: value for key, value in result.items() if value}


def laurent_add(*polynomials):
    result = {}
    for polynomial in polynomials:
        for exponent, coefficient in polynomial.items():
            result[exponent] = result.get(exponent, 0) + coefficient
    return {key: value for key, value in result.items() if value}


def shift(polynomial, amount, scale=1):
    return {exponent + amount: coefficient * scale for exponent, coefficient in polynomial.items() if coefficient * scale}


def signed_sum(exponent):
    if exponent >= 0:
        return {index: 1 for index in range(exponent)}
    return {index: -1 for index in range(exponent, 0)}


def operator(g):
    doubled = {2 * exponent: coefficient for exponent, coefficient in g.items()}
    return laurent_add(shift(doubled, 2), shift(doubled, 0, -1), shift(g, 1), g)


def test_completion_normalizations_and_image_generators_are_literal_controls():
    d_word, delta = "bbAbaB", "bAbABaBB"
    u_word = reduced(d_word + inverse(delta))
    assert phi("b") == d_word
    assert u_word == reduced(d_word + d_word + "aB")
    assert reduced("bb" + "Aba" + "B") == d_word
    assert reduced("BB" + d_word + "b") == "Aba"
    for q_word in ("", "a", "b", "abAB", "Aba"):
        for m in (-3, 0, 1, 3, 5):
            ea = reduced(inverse(phi(q_word)) + "ab" + q_word + power("a", -m))
            p_word = reduced("BA" + phi(q_word))
            eb = reduced(inverse(phi(p_word)) + "ab" + p_word + power("b", -m))
            l_word = reduced("bA" + phi(p_word))
            e2 = reduced(inverse(phi(l_word)) + u_word + l_word + power(d_word, -m))
            assert eb == phi(ea)
            assert e2 == phi(phi(ea))


def test_direct_fox_residual_matches_independent_laurent_formula_on_controls():
    for m in range(-5, 8):
        for commutator in ("", "abAB", "aabAAB"):
            q_word = reduced(power("a", m - 1) + power("b", 2 - m) + commutator)
            residual = reduced(phi(q_word) + power("a", m) + inverse(q_word) + "BA")
            derivative, abelianization = fox_abelian(residual, "a")
            assert abelianization == (0, 0)
            q_derivative, q_abelianization = fox_abelian(q_word, "b")
            assert q_abelianization == (m - 1, 2 - m)
            g = specialize(q_derivative)
            equation_rhs = laurent_add(signed_sum(3 - 2 * m), {-3: 1})
            predicted = shift(laurent_add(operator(g), shift(equation_rhs, 0, -1)), 3)
            assert specialize(derivative) == predicted


def test_laurent_minimum_and_characteristic_two_controls_are_explicit():
    for m in range(-5, 8):
        equation_rhs = laurent_add(signed_sum(3 - 2 * m), {-3: 1})
        assert equation_rhs
        assert operator({}) == {}
        assert shift(equation_rhs, 3, -1)
        if m != 3:
            assert min(equation_rhs) < 0 and min(equation_rhs) % 2 == 1
        else:
            assert equation_rhs == {-2: -1, -1: -1}
    m3_rhs = laurent_add(signed_sum(-3), {-3: 1})
    difference = laurent_add(operator({-1: 1}), shift(m3_rhs, 0, -1))
    assert difference == {0: 2, -1: 2}
    assert {exponent: coefficient % 2 for exponent, coefficient in difference.items() if coefficient % 2} == {}
