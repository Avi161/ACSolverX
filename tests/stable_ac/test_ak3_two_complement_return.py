"""One two-complement candidate returns to AK3; no triviality is asserted."""


def inverse(word):
    return word[::-1].swapcase()


def reduce_word(*words):
    stack = []
    for word in words:
        for letter in word:
            if stack and stack[-1] == letter.swapcase():
                stack.pop()
            else:
                stack.append(letter)
    return "".join(stack)


def substitute(word, images):
    return reduce_word(*(images[letter] if letter.islower()
                         else inverse(images[letter.lower()]) for letter in word))


def conjugate(word, prefix):
    return reduce_word(prefix, word, inverse(prefix))


R, S = "xxxYYYY", "xyxYXY"
X0, Y0 = "tUs", "Ut"
W1 = reduce_word("r", inverse(substitute(R, {"x": X0, "y": Y0})))
W2 = reduce_word("u", inverse(reduce_word(X0, Y0, X0)))


def test_source_and_both_free_basis_maps():
    source = {"r": R, "s": S, "t": "xyxy", "u": "xyx"}
    assert substitute(X0, source) == "x"
    assert substitute(Y0, source) == "y"
    assert substitute(W1, source) == substitute(W2, source) == ""

    first_to_old = {"a": X0, "b": Y0, "r": "r", "u": "u"}
    old_to_first = {"r": "r", "u": "u", "t": "ub", "s": "uBUa"}
    for generator in "abru":
        assert substitute(substitute(generator, first_to_old), old_to_first) == generator
    for generator in "rstu":
        assert substitute(substitute(generator, old_to_first), first_to_old) == generator

    new_to_old = {"p": W1, "q": W2, "a": X0, "b": Y0}
    u_image = "qaba"
    old_to_new = {
        "r": reduce_word("p", substitute(R, {"x": "a", "y": "b"})),
        "u": u_image,
        "t": reduce_word(u_image, "b"),
        "s": reduce_word(u_image, "B", inverse(u_image), "a"),
    }
    for generator in "pqab":
        assert substitute(substitute(generator, new_to_old), old_to_new) == generator
    for generator in "rstu":
        assert substitute(substitute(generator, old_to_new), new_to_old) == generator


def test_projected_pair_and_actual_donor_return():
    projection = {"r": "", "s": "", "t": "t", "u": "u"}
    coordinates = {"t": "ab", "u": "b"}
    inverse_coordinates = {"a": "tU", "b": "u"}
    for generator in "tu":
        assert substitute(substitute(generator, coordinates), inverse_coordinates) == generator
    for generator in "ab":
        assert substitute(substitute(generator, inverse_coordinates), coordinates) == generator
    P = inverse(substitute(substitute(W1, projection), coordinates))
    Q = substitute(substitute(W2, projection), coordinates)
    assert (P, Q) == ("aaaBAAAAb", "bABAbA")

    shear = {"a": "a", "b": "caa"}
    inverse_shear = {"a": "a", "c": "bAA"}
    for generator in "ab":
        assert substitute(substitute(generator, shear), inverse_shear) == generator
    for generator in "ac":
        assert substitute(substitute(generator, inverse_shear), shear) == generator
    P, Q = substitute(P, shear), substitute(Q, shear)
    assert (P, Q) == ("aCAAAAcaa", "cACAca")
    rows = [P, Q]
    rows[1] = inverse(rows[1])
    rows[1] = conjugate(rows[1], "ca")
    S0 = "acaCAC"
    assert rows[1] == S0
    f0, g0 = "CAc", "aCA"
    assert reduce_word(f0, inverse(g0)) == conjugate(inverse(S0), "CA")
    rows[0] = conjugate(rows[0], "a")
    assert rows[0] == reduce_word("aa", f0 * 4, "a")
    wrong_sign = reduce_word(conjugate(inverse(rows[1]), "aaCA"), rows[0])
    assert wrong_sign != reduce_word("aa", g0, f0 * 3, "a")
    for index in range(4):
        prefix = reduce_word("aa", g0 * index, "CA")
        rows[1] = conjugate(rows[1], prefix)
        rows[0] = reduce_word(rows[1], rows[0])
        rows[1] = conjugate(rows[1], inverse(prefix))
        assert rows[1] == S0
        assert rows[0] == reduce_word("aa", g0 * (index + 1), f0 * (3 - index), "a")
    assert rows == ["aaaCCCC", S0]
