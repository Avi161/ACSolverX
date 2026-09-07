"""Literal descent checks for a designated defining tag at both edge endpoints."""


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


def conjugate(word, prefix):
    return reduce_word(prefix, word, inverse(prefix))


def signed(word, sign):
    assert sign in (-1, 1)
    return word if sign == 1 else inverse(word)


def image_blocks(word, c):
    return [inverse(c) if letter == "t" else c if letter == "T" else letter for letter in word]


def theta(word, c):
    return reduce_word(*image_blocks(word, c))


def check_right_edge(r, r_prime, donor, c, d, u, v, epsilon, eta, other):
    assert r == conjugate(signed(reduce_word("t", c), epsilon), u)
    assert r_prime == conjugate(signed(reduce_word("t", d), eta), v)
    assert reduce_word(r, donor) == r_prime
    k = reduce_word(inverse(c), d)
    old_donor, new_donor = theta(donor, c), theta(donor, d)
    a, b = theta(v, c), theta(u, d)
    assert old_donor == conjugate(signed(k, eta), a)
    assert new_donor == conjugate(signed(k, epsilon), b)

    live_donor = conjugate(old_donor, inverse(a))
    assert live_donor == signed(k, eta)
    if eta == -1:
        live_donor = inverse(live_donor)
    assert live_donor == k
    blocks = image_blocks(other, c)
    current = reduce_word(*blocks)
    assert current == theta(other, c)
    for index, letter in enumerate(other):
        if letter not in "tT":
            continue
        prefix = reduce_word(*blocks[:index])
        old_block = blocks[index]
        new_block = inverse(d) if letter == "t" else d
        defect = reduce_word(old_block, inverse(new_block))
        if letter == "t":
            assert defect == k
            correction = conjugate(inverse(live_donor), prefix)
        else:
            assert defect == conjugate(inverse(k), c)
            correction = conjugate(live_donor, reduce_word(prefix, c))
        before_donor = live_donor
        current = reduce_word(correction, current)
        blocks[index] = new_block
        assert current == reduce_word(*blocks)
        assert live_donor == before_donor == k
    assert current == theta(other, d)
    if epsilon == -1:
        live_donor = inverse(live_donor)
    live_donor = conjugate(live_donor, b)
    assert live_donor == new_donor
    return current, live_donor


def test_defining_tag_right_multiplication_descends_for_all_signs():
    c, d, u, v, other = "xy", "YXy", "tXT", "ytX", "txyTXtY"
    for epsilon in (-1, 1):
        for eta in (-1, 1):
            r = conjugate(signed(reduce_word("t", c), epsilon), u)
            r_prime = conjugate(signed(reduce_word("t", d), eta), v)
            donor = reduce_word(inverse(r), r_prime)
            assert check_right_edge(r, r_prime, donor, c, d, u, v, epsilon, eta, other) == (
                theta(other, d), theta(donor, d)
            )


def test_explicit_sign_flip_and_identity_kernel_element():
    c, d, r, r_prime, donor, other = "x", "y", "tx", "YT", "XTYT", "txT"
    assert check_right_edge(r, r_prime, donor, c, d, "", "", 1, -1, other) == (
        theta(other, d), theta(donor, d)
    )
    c = d = "xy"
    u, v = "tXT", "ytX"
    r = conjugate(reduce_word("t", c), u)
    r_prime = conjugate(inverse(reduce_word("t", d)), v)
    donor = reduce_word(inverse(r), r_prime)
    assert reduce_word(inverse(c), d) == ""
    assert check_right_edge(r, r_prime, donor, c, d, u, v, 1, -1, "txyTXtY") == (
        theta("txyTXtY", c), ""
    )


def test_left_product_and_inverse_donor_reduce_to_right_edges():
    c, d, u, v, other = "xy", "YXy", "tXT", "ytX", "txyTXtY"
    r = conjugate(reduce_word("t", c), u)
    r_prime = conjugate(inverse(reduce_word("t", d)), v)
    left_donor = reduce_word(r_prime, inverse(r))
    assert reduce_word(left_donor, r) == r_prime
    assert reduce_word(inverse(r), inverse(left_donor)) == inverse(r_prime)
    check_right_edge(inverse(r), inverse(r_prime), inverse(left_donor),
                     c, d, u, v, -1, 1, other)
    inverse_donor = reduce_word(inverse(r_prime), r)
    assert reduce_word(r, inverse(inverse_donor)) == r_prime
    assert reduce_word(r_prime, inverse_donor) == r
    check_right_edge(r_prime, r, inverse_donor, d, c, v, u, -1, 1, other)


def test_tag_inversion_conjugation_and_exponent_sum_premise_control():
    c, u, h = "xy", "tXT", "ytX"
    for epsilon in (-1, 1):
        r = conjugate(signed(reduce_word("t", c), epsilon), u)
        assert inverse(r) == conjugate(signed(reduce_word("t", c), -epsilon), u)
        assert conjugate(r, h) == conjugate(signed(reduce_word("t", c), epsilon), reduce_word(h, u))
        assert theta(r, c) == theta(inverse(r), c) == theta(conjugate(r, h), c) == ""
    control = "txTyt"
    assert reduce_word(control) == control
    assert control[0] != control[-1].swapcase()
    assert sum(letter.lower() == "t" for letter in control) == 3
    assert control.count("t") - control.count("T") == 1
