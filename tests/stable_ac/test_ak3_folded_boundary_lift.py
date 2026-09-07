"""Factorwise checks; never construct the total point-pushing lift."""


def multiply(*words):
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
    return multiply(*(images[letter] if letter.islower() else inverse(images[letter.lower()])
                      for letter in word))


def compose(*maps):
    result = dict(maps[-1])
    for mapping in reversed(maps[:-1]):
        result = {letter: substitute(word, mapping) for letter, word in result.items()}
    return result


def conjugate(word, prefix):
    return multiply(prefix, word, inverse(prefix))


def commutator(left, right):
    return multiply(left, right, inverse(left), inverse(right))


def identity(alphabet):
    return dict(zip(alphabet, alphabet))


def assert_inverse(forward, backward, alphabet):
    assert compose(forward, backward) == identity(alphabet)
    assert compose(backward, forward) == identity(alphabet)


H_ORIGINAL = multiply(commutator("p", "Q"), commutator("u", "v"))
H_STANDARD = multiply(commutator("r", "s"), commutator("l", "m"))
RHO = {"p": "p", "q": "q", "u": "Q", "v": "p"}
K0 = commutator("a", "c")
STANDARD_IN_ABCD = {
    "r": multiply("a", inverse(K0)),
    "s": multiply(K0, "bC", inverse(K0)),
    "l": conjugate("c", "a"),
    "m": "dA",
}
A = multiply("L", "r", "l")
C = conjugate("l", inverse(A))
K0_IN_STANDARD = commutator(A, C)
ABCD_IN_STANDARD = {
    "a": A,
    "b": multiply(inverse(K0_IN_STANDARD), "s", K0_IN_STANDARD, C),
    "c": C,
    "d": multiply("m", A),
}
ABCD_IN_ORIGINAL = {"a": "p", "b": "Q", "c": "u", "d": "v"}
ORIGINAL_IN_ABCD = {"p": "a", "q": "B", "u": "c", "v": "d"}
STANDARD_IN_ORIGINAL = compose(ABCD_IN_ORIGINAL, STANDARD_IN_ABCD)
ORIGINAL_IN_STANDARD = compose(ABCD_IN_STANDARD, ORIGINAL_IN_ABCD)
RHO_STANDARD = compose(RHO, STANDARD_IN_ORIGINAL)
K = commutator("l", "m")
L = multiply(inverse(K), "s")
T = {
    "r": multiply("r", K),
    "s": conjugate("s", inverse(K)),
    "l": conjugate("l", L),
    "m": conjugate("m", L),
}
T_INVERSE = {
    "r": multiply("rS", inverse(K), "s"),
    "s": multiply("S", K, "s", inverse(K), "s"),
    "l": multiply("S", K, "l", inverse(K), "s"),
    "m": multiply("S", K, "m", inverse(K), "s"),
}
TAU = {**identity("rslm"), "s": "sr"}
TAU_INVERSE = {**identity("rslm"), "s": "sR"}
J = commutator("r", "s")
S = {"r": "l", "s": "m", "l": conjugate("r", inverse(K)), "m": conjugate("s", inverse(K))}
S_INVERSE = {"r": conjugate("l", J), "s": conjugate("m", J), "l": "r", "m": "s"}
PHI0 = {"p": "q", "q": "Pq", "u": "uv", "v": "U"}
PHI0_INVERSE = {"p": "pQ", "q": "p", "u": "V", "v": "vu"}
PHI = {"p": "q", "q": "Pq"}
W_ORIGINAL = multiply("u", "p", "u", inverse("p"), inverse("u"), inverse("p"))
W_STANDARD = substitute(W_ORIGINAL, ORIGINAL_IN_STANDARD)
W_QUOTIENT = "QpQPqP"


def push_factors():
    f_r = compose(T, TAU, T_INVERSE, TAU_INVERSE)
    f_r_inverse = compose(TAU, T, TAU_INVERSE, T_INVERSE)
    f_l = compose(S, f_r, S_INVERSE)
    f_l_inverse = compose(S, f_r_inverse, S_INVERSE)
    return {"r": f_r, "R": f_r_inverse, "l": f_l, "L": f_l_inverse}


def test_free_word_operations_have_order_and_sign_controls():
    assert multiply("pQ", "qP") == ""
    assert inverse("pQ") == "qP"
    assert conjugate("q", "P") == "Pqp"
    assert conjugate("q", "p") != conjugate("q", "P")
    first = {"p": "pq", "q": "q"}
    second = {"p": "q", "q": "p"}
    assert compose(first, second)["p"] == "q"
    assert compose(first, second) != compose(second, first)


def test_folded_coordinates_preserve_boundary_and_exhibit_quotient_basis():
    assert compose(ABCD_IN_STANDARD, STANDARD_IN_ABCD) == identity("rslm")
    assert compose(STANDARD_IN_ABCD, ABCD_IN_STANDARD) == identity("abcd")
    assert compose(ORIGINAL_IN_STANDARD, STANDARD_IN_ORIGINAL) == identity("rslm")
    assert compose(STANDARD_IN_ORIGINAL, ORIGINAL_IN_STANDARD) == identity("pquv")
    assert substitute(H_STANDARD, STANDARD_IN_ORIGINAL) == H_ORIGINAL
    assert substitute(H_ORIGINAL, ORIGINAL_IN_STANDARD) == H_STANDARD
    assert RHO_STANDARD["s"] == RHO_STANDARD["m"] == ""
    quotient_rl = {"r": RHO_STANDARD["r"], "l": RHO_STANDARD["l"]}
    pq_in_rl = {"p": A, "q": inverse(C)}
    assert compose(quotient_rl, pq_in_rl) == identity("pq")
    assert compose(pq_in_rl, quotient_rl) == identity("rl")
    assert set(W_STANDARD.lower()) <= set("rl")
    assert substitute(W_ORIGINAL, RHO) == W_QUOTIENT
    assert substitute(W_STANDARD, RHO_STANDARD) == W_QUOTIENT


def test_boundary_automorphisms_and_their_displayed_inverses():
    for forward, backward in ((T, T_INVERSE), (TAU, TAU_INVERSE), (S, S_INVERSE)):
        assert_inverse(forward, backward, "rslm")
        assert substitute(H_STANDARD, forward) == H_STANDARD
        assert substitute(H_STANDARD, backward) == H_STANDARD


def test_each_push_factor_fixes_boundary_and_has_claimed_inner_projection():
    factors = push_factors()
    assert_inverse(factors["r"], factors["R"], "rslm")
    assert_inverse(factors["l"], factors["L"], "rslm")
    for letter, factor in factors.items():
        assert substitute(H_STANDARD, factor) == H_STANDARD
        prefix = inverse(substitute(letter, RHO_STANDARD))
        assert compose(RHO_STANDARD, factor) == {
            generator: conjugate(image, prefix) for generator, image in RHO_STANDARD.items()
        }
    wrong_order = compose(TAU_INVERSE, T_INVERSE, TAU, T)
    assert compose(RHO_STANDARD, wrong_order) != compose(RHO_STANDARD, factors["r"])
    wrong_sign = {
        generator: conjugate(image, RHO_STANDARD["r"])
        for generator, image in RHO_STANDARD.items()
    }
    assert compose(RHO_STANDARD, factors["r"]) != wrong_sign


def test_phi0_fixes_boundary_and_intertwines_base_automorphism():
    assert_inverse(PHI0, PHI0_INVERSE, "pquv")
    assert substitute(H_ORIGINAL, PHI0) == H_ORIGINAL
    assert substitute(H_ORIGINAL, PHI0_INVERSE) == H_ORIGINAL
    assert compose(RHO, PHI0) == compose(PHI, RHO)


def test_antihomomorphic_factor_order_gives_total_projected_lift():
    projected_factors = {}
    for letter in "rRlL":
        prefix = inverse(substitute(letter, RHO_STANDARD))
        projected_factors[letter] = {generator: conjugate(generator, prefix) for generator in "pq"}
    projected_push = identity("pq")
    for letter in W_STANDARD:
        projected_push = compose(projected_factors[letter], projected_push)
    expected_push = {generator: conjugate(generator, inverse(W_QUOTIENT)) for generator in "pq"}
    assert projected_push == expected_push
    projected_inverse = identity("pq")
    for letter in inverse(W_STANDARD):
        projected_inverse = compose(projected_factors[letter], projected_inverse)
    assert_inverse(projected_push, projected_inverse, "pq")
    psi = compose(expected_push, PHI)
    assert compose(projected_push, PHI, RHO) == compose(psi, RHO)
    assert compose(projected_factors["l"], projected_factors["r"]) != compose(
        projected_factors["r"], projected_factors["l"]
    )
    assert compose(PHI, projected_push) != psi


def test_capped_surface_substitution_is_distinct_from_free_group_innerness():
    j = commutator("r", "s")
    k_cap = inverse(j)
    l_cap = multiply(inverse(k_cap), "s")
    c = multiply("r", "s", inverse("r"))
    capped_t = {
        "r": multiply("r", k_cap),
        "s": conjugate("s", inverse(k_cap)),
        "l": conjugate("l", l_cap),
        "m": conjugate("m", l_cap),
    }
    inner_c = {generator: conjugate(generator, c) for generator in "rslm"}
    assert capped_t == inner_c
    assert multiply(c, substitute(inverse(c), TAU)) == multiply(j, inverse("r"))
    assert substitute(multiply(j, inverse("r")), S) == multiply(K, inverse("l"))
    assert T != inner_c
    assert H_STANDARD == multiply(j, K)
    assert H_STANDARD != ""
