from fractions import Fraction
from itertools import permutations


INVERSES = str.maketrans(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
)


def inverse(word: str) -> str:
    return word.translate(INVERSES)[::-1]


def reduce(word: str) -> str:
    reduced: list[str] = []
    for letter in word:
        if reduced and reduced[-1] == letter.translate(INVERSES):
            reduced.pop()
        else:
            reduced.append(letter)
    return "".join(reduced)


def product(*words: str) -> str:
    return reduce("".join(words))


def conjugate(by: str, word: str) -> str:
    return product(by, word, inverse(by))


def commutator(left: str, right: str) -> str:
    return product(left, right, inverse(left), inverse(right))


def substitute(word: str, images: dict[str, str]) -> str:
    expanded = []
    for letter in word:
        image = images.get(letter.lower())
        if image is None:
            expanded.append(letter)
        elif letter.isupper():
            expanded.append(inverse(image))
        else:
            expanded.append(image)
    return product(*expanded)


def exponent_vector(word: str, generators: str) -> tuple[int, ...]:
    return tuple(
        sum(
            1 if letter == generator else -1 if letter == generator.upper() else 0
            for letter in word
        )
        for generator in generators
    )


def module_add(*vectors):
    result = {}
    for vector in vectors:
        for key, coefficient in vector.items():
            result[key] = result.get(key, 0) + coefficient
            if result[key] == 0:
                del result[key]
    return result


def module_negate(vector):
    return {key: -coefficient for key, coefficient in vector.items()}


def module_act(word, vector):
    return {
        (product(word, coset), basis): coefficient
        for (coset, basis), coefficient in vector.items()
    }


def test_generic_commutator_tag_macro_has_can_fail_control():
    def compose(left, right):
        return tuple(left[right[index]] for index in range(5))

    def perm_inverse(value):
        result = [0] * 5
        for index, image in enumerate(value):
            result[image] = index
        return tuple(result)

    def perm_commutator(left, right):
        return compose(
            compose(compose(left, right), perm_inverse(left)),
            perm_inverse(right),
        )

    identity = tuple(range(5))
    x = (1, 2, 0, 3, 4)
    r = (1, 3, 2, 0, 4)
    q = (1, 0, 3, 2, 4)
    assert perm_commutator(x, r) == q
    assert compose(q, q) == identity

    a5 = tuple(
        value
        for value in permutations(range(5))
        if sum(
            value[left] > value[right]
            for left in range(5)
            for right in range(left + 1, 5)
        )
        % 2
        == 0
    )
    conjugates = {
        compose(compose(g, q), perm_inverse(g))
        for g in a5
    }
    closure = {identity}
    while True:
        expanded = {
            compose(left, right)
            for left in closure
            for right in conjugates
        }
        next_closure = closure | expanded
        if next_closure == closure:
            break
        closure = next_closure
    assert len(a5) == len(closure) == 60
    assert compose(q, perm_inverse(perm_commutator(x, r))) == identity


def test_mms02_tagged_buffer_exact_word_replay():
    A = "xzYXyxZXYxyZ"
    B = "XyxZXYXyxzXYxy"
    r = "xyxZXY"
    q = "Xy"
    v = "Xyz"
    u = "zYX"
    C = "yxzXY"
    h = "YX"
    K = commutator(u, C)
    D = conjugate(h, commutator("X", r))

    assert product(r, C) == "x"
    assert product(q, u) == product(v, h)
    assert C == product(
        conjugate("x", q),
        conjugate("xx", inverse(q)),
        conjugate("xx", v),
        conjugate("x", inverse(q)),
    )
    assert inverse(K) == product(C, conjugate(u, inverse(C)))
    assert inverse(D) == product(
        conjugate(h, r),
        conjugate(product(h, "X"), inverse(r)),
    )

    s = product(r, "t")
    rt_commutator = commutator(r, "t")
    interchange_left = product(
        commutator("X", r),
        conjugate(r, commutator("X", "t")),
    )
    interchange_right = product(
        commutator("X", rt_commutator),
        conjugate(rt_commutator, commutator("X", "t")),
        conjugate(product(rt_commutator, "t"), commutator("X", r)),
    )
    assert interchange_left == interchange_right == commutator("X", s)
    assert rt_commutator == commutator(s, inverse(r))

    hall_witt = product(
        conjugate(
            inverse(r),
            commutator(inverse(commutator("x", r)), "T"),
        ),
        conjugate(
            "T",
            commutator(inverse(commutator(inverse(r), "t")), "x"),
        ),
        conjugate(
            "x",
            commutator(inverse(commutator("T", "X")), inverse(r)),
        ),
    )
    assert hall_witt == ""
    assert A == product(r, inverse(K))
    assert B == product(q, inverse(D))

    def Cfun(P: str) -> str:
        return product(
            conjugate("x", P),
            conjugate("xx", inverse(P)),
            conjugate("xx", v),
            conjugate("x", inverse(P)),
        )

    def Kfun(P: str) -> str:
        return commutator(u, Cfun(P))

    def Dfun(word: str) -> str:
        return conjugate(h, commutator("X", word))

    rt = product(r, "t")
    g = product(q, h, r)
    Bt = product(q, inverse(Dfun(rt)))
    Lt = conjugate(g, inverse(commutator("X", "t")))

    assert Dfun(rt) == product(
        D,
        conjugate(product(h, r), commutator("X", "t")),
    )
    assert Bt == product(Lt, B)

    Delta = Dfun(A)
    Theta = conjugate(product(h, A), commutator("X", K))
    W = product(K, "t")
    J = conjugate(product(h, A), commutator("X", W))
    Xi = conjugate(product(h, A, K), commutator("X", "t"))
    p_star = product(q, inverse(Theta))
    q0 = product(q, inverse(J))
    Lambda = conjugate(q, inverse(Xi))
    K0 = Kfun(q0)
    Omega = product(inverse(K0), Kfun(product(q0, J)))

    assert D == product(Delta, Theta)
    assert Dfun(rt) == product(Delta, J)
    assert J == product(Theta, Xi)
    assert rt == product(A, W)
    assert B == product(p_star, inverse(Delta))
    assert Bt == product(q0, inverse(Delta))
    assert q0 == product(Lambda, p_star)
    assert product(q0, inverse(B)) == product(Lambda, conjugate(p_star, Delta))
    assert Lambda == conjugate(g, inverse(commutator("X", "t"))) == Lt
    assert inverse(J) == product(
        conjugate(product(h, A), W),
        conjugate(product(h, A, "X"), inverse(W)),
    )
    assert product(q0, J) == q

    assert inverse(K0) == product(
        conjugate("x", q0),
        conjugate("xx", inverse(q0)),
        conjugate("xx", v),
        conjugate("x", inverse(q0)),
        conjugate(u, conjugate("x", q0)),
        conjugate(u, conjugate("xx", inverse(v))),
        conjugate(u, conjugate("xx", q0)),
        conjugate(u, conjugate("x", inverse(q0))),
    )
    assert K == product(K0, Omega)
    assert W == product(K0, Omega, "t")

    assert substitute(rt, {"t": inverse(r)}) == ""
    assert substitute(
        commutator("X", "t"),
        {"t": inverse(r)},
    ) == commutator("X", inverse(r))
    commutator_relation = product(
        commutator("X", "t"),
        inverse(conjugate(inverse(g), B)),
    )
    assert commutator_relation == conjugate(
        commutator("X", "t"),
        conjugate(inverse(g), inverse(Bt)),
    )

    assert substitute(v, {"z": "Yx"}) == ""
    assert product(q, h) == "XX"
    assert g == product("XX", r)
    w = substitute(product("x", conjugate(inverse(g), B)), {"z": "Yx"})
    expected_w = substitute(
        product(inverse(r), "xx", "y", "XX", r),
        {"z": "Yx"},
    )
    assert w == expected_w == "yxYYxyXyyXY"

    A_bar = substitute(A, {"z": "Yx"})
    B_bar = substitute(B, {"z": "Yx"})
    r_bar = substitute(r, {"z": "Yx"})
    E = substitute(product(inverse(D), q, D, inverse(B)), {"z": "Yx"})
    assert E == substitute(product(inverse(D), q, D, D, inverse(q)), {"z": "Yx"})
    assert exponent_vector(A_bar, "xy") == (0, 1)
    assert exponent_vector(r_bar, "xy") == (0, 1)
    assert exponent_vector(q, "xy") == (-1, 1)
    assert exponent_vector(B_bar, "xy") == (-1, 1)
    assert substitute(A_bar, {"y": ""}) == ""
    assert substitute(q, {"y": ""}) == "X"
    assert substitute(q, {"y": "x"}) == ""
    A_after_q = substitute(A_bar, {"y": "x"})
    r_after_q = substitute(r_bar, {"y": "x"})
    assert A_after_q == r_after_q == "x"
    assert substitute(B_bar, {"y": ""}) == "X"

    def evaluate(word: str) -> tuple[Fraction, int]:
        element = (Fraction(0), 0)
        generators = {
            "x": (Fraction(0), 1),
            "X": (Fraction(0), -1),
            "y": (Fraction(1), 0),
            "Y": (Fraction(-1), 0),
        }
        for letter in substitute(word, {"z": "Yx"}):
            module, power = element
            next_module, next_power = generators[letter]
            element = (
                module + Fraction(2) ** power * next_module,
                power + next_power,
            )
        return element

    assert evaluate(A_bar) == (Fraction(0), 0)
    assert evaluate("y") == (Fraction(1), 0)
    assert evaluate(r_bar) == (Fraction(3), 0)
    assert evaluate(D) == (Fraction(-3, 4), 0)
    assert evaluate(q) == (Fraction(1, 2), -1)
    assert evaluate(B_bar) == (Fraction(7, 8), -1)
    assert evaluate(conjugate(inverse(D), q)) == evaluate(B_bar)


def test_tagged_affine_updates_have_exact_free_group_ancestors():
    m, n, k = "m", "n", "k"
    u, v, g = "u", "v", "g"
    b, t = "b", "t"

    lifted_first = product(m, u)
    lifted_second = product(n, v)
    assert inverse(lifted_first) == product(
        conjugate(inverse(u), inverse(m)),
        inverse(u),
    )
    assert product(lifted_first, lifted_second) == product(
        m,
        conjugate(u, n),
        u,
        v,
    )

    quotient_conjugate = conjugate(g, u)
    conjugation_defect = product(
        k,
        conjugate(g, m),
        conjugate(quotient_conjugate, inverse(k)),
    )
    assert conjugate(product(k, g), lifted_first) == product(
        conjugation_defect,
        quotient_conjugate,
    )

    assert conjugate(k, b) == product(
        k,
        conjugate(b, inverse(k)),
        b,
    )
    assert conjugate(k, t) == product(
        k,
        conjugate(t, inverse(k)),
        t,
    )

    b_row = product(m, b)
    tag_row = product(n, t)
    b_transport = conjugate(inverse(b), m)
    first_loop_defect = product(
        b_transport,
        n,
        conjugate(t, inverse(b_transport)),
    )
    assert conjugate(inverse(b), conjugate(b_row, tag_row)) == product(
        first_loop_defect,
        t,
    )

    t_transport = conjugate(inverse(t), n)
    second_loop_defect = product(
        t_transport,
        m,
        conjugate(b, inverse(t_transport)),
    )
    assert conjugate(inverse(t), conjugate(tag_row, b_row)) == product(
        second_loop_defect,
        b,
    )


def test_identity_coset_covector_has_exact_vertical_loop_counterexample():
    lifted_first = "mb"
    lifted_second = "nt"
    product_word = product(lifted_first, lifted_second)
    vertical_word = conjugate("k", product_word)
    inverse_product_word = product(vertical_word, inverse(lifted_second))
    quotient = {"m": "", "n": "", "k": ""}
    assert substitute(lifted_first, quotient) == "b"
    assert substitute(lifted_second, quotient) == "t"
    assert substitute(product_word, quotient) == "bt"
    assert substitute(vertical_word, quotient) == "bt"
    assert substitute(inverse_product_word, quotient) == "b"

    e = {("", "E"): 1}
    n = {("", "N"): 1}
    k = module_act("T", e)

    after_product = module_add(e, module_act("b", n))
    vertical_defect = module_add(k, module_negate(module_act("bt", k)))
    after_vertical = module_add(after_product, vertical_defect)
    after_inverse_product = module_add(after_vertical, module_negate(module_act("b", n)))

    assert product("bt", "T") == "b"
    assert vertical_defect == {("T", "E"): 1, ("b", "E"): -1}
    assert after_inverse_product == {
        ("", "E"): 1,
        ("T", "E"): 1,
        ("b", "E"): -1,
    }

    root_vertical = {
        key: coefficient
        for key, coefficient in vertical_defect.items()
        if "t" not in key[0].lower()
    }
    root_final = {
        key: coefficient
        for key, coefficient in after_inverse_product.items()
        if "t" not in key[0].lower()
    }
    assert root_vertical == {("b", "E"): -1}
    assert root_final == {("", "E"): 1, ("b", "E"): -1}
    assert ("T", "E") in after_inverse_product


def test_restored_mms02_donors_replace_q_by_inverse_x():
    A, q, v, u = "xzYXyxZXYxyZ", "Xy", "Xyz", "zYX"
    k = product(u, "y", "x")
    kz = product(k, "z")
    assert product("x", conjugate(k, q)) == product(A, conjugate(kz, v))

    def replay(v_conjugator):
        rows = [A, q, v, "t"]
        rows[1] = conjugate(k, rows[1])
        rows[2] = inverse(rows[2])
        rows[2] = conjugate(v_conjugator, rows[2])
        rows[1] = product(rows[1], rows[2])
        rows[2] = conjugate(inverse(v_conjugator), rows[2])
        rows[2] = inverse(rows[2])
        assert rows[0] == A and rows[2:] == [v, "t"]
        rows[0] = inverse(rows[0])
        rows[1] = product(rows[1], rows[0])
        rows[0] = inverse(rows[0])
        assert rows[0] == A and rows[2:] == [v, "t"]
        return tuple(rows)

    assert replay(kz) == (A, "X", v, "t")
    wrong = replay(k)
    assert wrong != (A, "X", v, "t")
    assert wrong[1] != "X"
