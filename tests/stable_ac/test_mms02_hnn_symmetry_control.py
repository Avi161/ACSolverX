"""Literal HNN symmetry and defining-elimination controls, without a search."""


def reduce_word(*words):
    stack = []
    for word in words:
        for letter in word:
            if stack and stack[-1] == letter.swapcase():
                stack.pop()
            else:
                stack.append(letter)
    return "".join(stack)


def inverse(word):
    return word[::-1].swapcase()


def substitute(word, images):
    return reduce_word(*(images[letter.lower()] if letter.islower()
                         else inverse(images[letter.lower()]) for letter in word))


def conjugate(word, prefix):
    return reduce_word(prefix, word, inverse(prefix))


SIGMA = {"a": "Ab", "b": "b", "x": "baBx"}
SIGMA_INVERSE = {"a": "bA", "b": "b", "x": "baBBx"}
PHI = {"a": "b", "b": "bbAbaB"}
ALPHA = {"a": "Ab", "b": "b"}
Z = "baB"
R1 = "xaXB"
R2 = reduce_word("xbX", inverse(PHI["b"]))
S = "XbAB"


def test_literal_hnn_symmetry_has_inverse_and_intertwines_monodromy():
    assert substitute("X", SIGMA) == S
    for generator in "abx":
        assert substitute(substitute(generator, SIGMA), SIGMA_INVERSE) == generator
        assert substitute(substitute(generator, SIGMA_INVERSE), SIGMA) == generator
    for generator in "ab":
        assert substitute(PHI[generator], ALPHA) == conjugate(substitute(ALPHA[generator], PHI), Z)
    assert substitute(R1, SIGMA) == conjugate(reduce_word(inverse(R1), R2), reduce_word(Z, "B"))
    assert substitute(R2, SIGMA) == conjugate(R2, Z)


def test_symmetry_relators_restore_with_unchanged_killer_donor():
    rows = (substitute(R1, SIGMA), substitute(R2, SIGMA), S)
    rows = (rows[0], conjugate(rows[1], inverse(Z)), rows[2])
    assert rows[1:] == (R2, S)
    rows = (conjugate(rows[0], inverse(reduce_word(Z, "B"))), rows[1], rows[2])
    assert rows == (reduce_word(inverse(R1), R2), R2, S)
    rows = (reduce_word(rows[0], inverse(rows[1])), rows[1], rows[2])
    assert rows == (inverse(R1), R2, S)
    rows = (inverse(rows[0]), rows[1], rows[2])
    assert rows == (R1, R2, S)


def test_defining_elimination_and_literal_wrong_target_control():
    """Check substitutions; do not present variable elimination as an AC replay."""
    elimination = {"a": "a", "b": "b", "x": "bAB"}
    assert substitute(S, elimination) == ""
    assert substitute(R2, elimination) == "B"
    assert substitute(substitute(R1, elimination), {"a": "a", "b": ""}) == "a"
    target = "abX"
    assert substitute(target, elimination) != ""


def test_single_hnn_comparison_has_exact_second_derived_fox_coefficient():
    h, c0 = "abX", "a" * 7
    assert S == "XbAB"
    assert inverse(h) == "xBA"
    e = reduce_word("b" * 8, "AB", "A" * 7, inverse(PHI["b"]), "B")
    assert e == reduce_word(substitute(c0, PHI), "bAB", inverse(c0), substitute("BA", PHI))
    zeta = substitute(e, PHI)
    assert (e.count("a") - e.count("A"), e.count("b") - e.count("B")) == (-8, 4)
    assert (zeta.count("a") - zeta.count("A"), zeta.count("b") - zeta.count("B")) == (0, 0)

    def fox(word):
        derivatives = [{}, {}]
        prefix = [0, 0]
        for letter in word:
            assert letter in "aAbB"
            index = 0 if letter.lower() == "a" else 1
            sign = 1 if letter.islower() else -1
            if sign == -1:
                prefix[index] -= 1
            exponent = tuple(prefix)
            derivatives[index][exponent] = derivatives[index].get(exponent, 0) + sign
            if sign == 1:
                prefix[index] += 1
        return tuple({exponent: coefficient for exponent, coefficient in row.items() if coefficient}
                     for row in derivatives)

    def multiply(left, right):
        result = {}
        for (a, b), coefficient in left.items():
            for (c, d), other in right.items():
                exponent = (a + c, b + d)
                result[exponent] = result.get(exponent, 0) + coefficient * other
        return {exponent: coefficient for exponent, coefficient in result.items() if coefficient}

    f = {(-1, 7): 1, (-1, 8): -2, (-1, 10): -1, (-1, 12): -1,
         (-1, 14): -1, (-1, 15): 1, (-1, 16): -1}
    assert fox(zeta) == (
        multiply(f, {(0, 0): 1, (0, 1): -1}),
        multiply(f, {(1, 0): 1, (0, 0): -1}),
    )


def test_single_hnn_comparison_coefficient_functional_at_four_scales():
    """Finite nonnegative-monomial controls do not prove all-scale annihilation."""
    for p in (2, 4, 8, 16):
        def operator(polynomial):
            result = {}
            for exponent, coefficient in polynomial.items():
                for power, sign in ((exponent + 2 * p, 1), (2 * exponent, -1), (2 * exponent + p, 1)):
                    result[power] = result.get(power, 0) + sign * coefficient
            return {exponent: coefficient for exponent, coefficient in result.items() if coefficient}

        def functional(polynomial):
            return (4 * polynomial.get(0, 0) + 2 * polynomial.get(p, 0)
                    + 2 * polynomial.get(2 * p, 0) + polynomial.get(3 * p, 0)
                    + polynomial.get(4 * p, 0))

        for exponent in range(4 * p + 1):
            assert functional(operator({exponent: 1})) == 0
        target = {0: 1, p: -2, 3 * p: -1, 5 * p: -1, 7 * p: -1, 8 * p: 1, 9 * p: -1}
        assert functional(target) == -1
        positive = operator({0: 1})
        assert positive == {0: -1, p: 1, 2 * p: 1}
        assert functional(positive) == 0
        outside_domain = operator({-p: 1})
        assert outside_domain == {p: 1, -2 * p: -1, -p: 1}
        assert functional(outside_domain) == 2


def test_hnn_symmetry_square_is_inner_only_modulo_the_relator():
    square = {generator: substitute(substitute(generator, SIGMA), SIGMA) for generator in "abx"}
    for generator in "ab":
        assert square[generator] == conjugate(generator, "B")
    assert square["x"] == reduce_word("bAb", "aBx")
    inner_x = conjugate("x", "B")
    defect = reduce_word(square["x"], inverse(inner_x))
    assert defect == conjugate(inverse(R2), "B")
    assert square["x"] != inner_x
    assert defect != ""


def test_positive_hnn_coordinates_and_live_row_replay():
    old_to_new = {"a": "q", "b": "qp", "x": "qpu"}
    new_to_old = {"p": "Ab", "q": "a", "u": "Bx"}
    for generator in "abx":
        assert substitute(substitute(generator, old_to_new), new_to_old) == generator
    for generator in "pqu":
        assert substitute(substitute(generator, new_to_old), old_to_new) == generator

    c, C = "qp", "PQ"
    sq, sp, k = "uqUPQ", "upUQP", "PqpU"
    assert inverse(c) == C
    rows = tuple(substitute(word, old_to_new) for word in (R1, R2, "abX"))
    assert rows[0] == reduce_word(c, sq, C)
    assert rows[1] == reduce_word(c, sq, c, sp, C, C)
    assert rows[2] == "qqpUPQ" == reduce_word(c, k, C)

    rows = tuple(conjugate(row, C) for row in rows)
    assert rows == (sq, reduce_word(sq, c, sp, C), k)
    rows = (rows[0], reduce_word(inverse(rows[0]), rows[1]), rows[2])
    assert rows == (sq, reduce_word(c, sp, C), k)
    rows = (rows[0], conjugate(rows[1], C), rows[2])
    assert rows == (sq, sp, k)


def test_positive_rose_map_has_no_allowed_turn_cancellation():
    images = {"p": "pq", "q": "qp", "P": "QP", "Q": "PQ"}
    assert len({word[0] for word in images.values()}) == 4
    for letter in "pq":
        assert images[letter.swapcase()] == inverse(images[letter])
        word = images[letter]
        assert (word.count("p") - word.count("P"),
                word.count("q") - word.count("Q")) == (1, 1)
    for left in images:
        for right in images:
            if right != left.swapcase():
                assert reduce_word(images[left], images[right]) == images[left] + images[right]


def test_positive_hnn_killer_elimination_is_only_a_control():
    """Defining substitutions alone prove neither nonconjugacy nor AK3."""
    sq, sp, k = "uqUPQ", "upUQP", "PqpU"
    elimination = {"p": "p", "q": "q", "u": "q"}
    assert substitute("qU", elimination) == ""
    projected_sq = substitute(sq, elimination)
    assert projected_sq == "qPQ" == conjugate("P", "q")
    projected_sp = substitute(sp, elimination)
    assert substitute(projected_sp, {"p": "", "q": "q"}) == "Q"
    assert substitute(k, elimination) == "PqpQ" != ""


def test_positive_hnn_coupled_strip_returns_to_ak3():
    """The coupled strip returns to AK3; it does not trivialize the tuple."""
    sq, sp, k = "uqUPQ", "upUQP", "PqpU"
    k0 = conjugate(k, "p")
    assert k0 == "qpUP"
    defining = reduce_word(sq, k0)
    assert defining == "uqUUP"
    elimination = {"p": "uqUU", "q": "q", "u": "u"}
    assert substitute(defining, elimination) == ""
    braid = substitute(k0, elimination)
    assert braid == "quqUQU"
    current = substitute(sp, elimination)
    assert current == "uuqUUUQuuQU"
    current = conjugate(current, "U")
    assert current == "uqUUUQuuQ"
    assert reduce_word("qUQ", inverse("UQu")) == conjugate(braid, "UQ")

    rows = (braid, current)
    for prefix in ("Q", "QQ", "QQQ"):
        rows = (inverse(rows[0]), rows[1])
        rows = (conjugate(rows[0], prefix), rows[1])
        rows = (rows[0], reduce_word(rows[0], rows[1]))
        rows = (conjugate(rows[0], inverse(prefix)), rows[1])
        rows = (inverse(rows[0]), rows[1])
        assert rows[0] == braid
    assert rows == (braid, "QQQuuuQ")
    rows = (rows[0], conjugate(rows[1], "qqq"))
    assert rows == (braid, "uuuQQQQ")
    rows = (inverse(rows[0]), rows[1])
    rows = (rows[1], rows[0])
    assert rows == ("uuuQQQQ", "uquQUQ")
