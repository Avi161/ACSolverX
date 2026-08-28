INVERSES = str.maketrans("xXyYzZtT", "XxYyZzTt")


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
    assert A == product(r, inverse(K))
    assert B == product(q, inverse(D))

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
