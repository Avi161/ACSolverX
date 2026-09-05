def free_inverse(word):
    return word[::-1].swapcase()


def free_reduce(word):
    stack = []
    for letter in word:
        if stack and stack[-1].swapcase() == letter:
            stack.pop()
        else:
            stack.append(letter)
    return "".join(stack)


def substitute(word, images):
    signed = images | {letter.upper(): free_inverse(value) for letter, value in images.items()}
    return free_reduce("".join(signed[letter] for letter in word))


def free_product_reduce(word, m, n):
    orders = {"x": m, "y": n}
    stack = []
    for letter in word:
        factor = letter.lower()
        residue = 1 if letter.islower() else -1
        if stack and stack[-1][0] == factor:
            residue += stack.pop()[1]
        residue %= orders[factor]
        if residue:
            stack.append((factor, residue))
    return tuple(stack)


def cyclic_syllable_normal_form(word, m, n):
    orders = {"x": m, "y": n}
    syllables = list(free_product_reduce(word, m, n))
    while len(syllables) > 1 and syllables[0][0] == syllables[-1][0]:
        factor, first = syllables.pop(0)
        _, last = syllables.pop()
        residue = (first + last) % orders[factor]
        if residue:
            syllables.insert(0, (factor, residue))
    if not syllables:
        return ()
    rotations = [tuple(syllables[index:] + syllables[:index]) for index in range(len(syllables))]
    return min(rotations)


def test_ak3_mixed_x_syllables_and_nonzero_candidate_blocks():
    b_row = "xyxYXY"
    normal = free_product_reduce(b_row, 3, 4)
    assert tuple(residue for factor, residue in normal if factor == "x") == (1, 1, 2)
    assert len(cyclic_syllable_normal_form(b_row, 3, 4)) == 6
    inverse_normal = cyclic_syllable_normal_form(free_inverse(b_row), 3, 4)
    assert sorted(residue for factor, residue in inverse_normal if factor == "x") == [1, 2, 2]
    for x_sign in (1, -1):
        for y_sign in (1, -1):
            for block in (1, 2):
                word = ("x" if x_sign > 0 else "X") + ("y" if y_sign > 0 else "Y") * block
                syllables = free_product_reduce(word, 3, 4)
                assert syllables == (("x", x_sign % 3), ("y", y_sign * block % 4))
                assert all(residue for _, residue in syllables)
    for k in (0, -1, 1):
        u, v = 1 + 3 * k, -1 - 4 * k
        assert 4 * u + 3 * v == 1
        if k:
            assert u * v < 0 and abs(u) < abs(v)
    assert free_product_reduce("xY", 3, 4) == (("x", 1), ("y", 3))
    assert free_product_reduce("xxxYYYY", 3, 4) == ()


def test_ak2_primitive_positive_control_matches_b_in_c2_free_c3():
    primitive, b_row = "xYYxYxY", "xyxYXY"
    assert free_product_reduce(primitive, 2, 3) == free_product_reduce(b_row, 2, 3)
    basis = {"a": "xY", "b": "Y"}
    inverse_basis = {"x": "aB", "y": "B"}
    for generator in "ab":
        assert substitute(substitute(generator, basis), inverse_basis) == generator
    for generator in "xy":
        assert substitute(substitute(generator, inverse_basis), basis) == generator
    assert substitute("abaa", basis) == primitive
    assert free_reduce("A" + "abaa" + "a") == "baaa"
    assert free_reduce(free_inverse("xY") + primitive + "xY") == substitute("baaa", basis)
    assert free_product_reduce("xxYYY", 2, 3) == ()


def matrix_multiply(left, right):
    a, b, c, d = left
    e, f, g, h = right
    return (a * e + b * g, a * f + b * h, c * e + d * g, c * f + d * h)


def matrix_inverse(matrix):
    a, b, c, d = matrix
    assert a * d - b * c == 1
    return (d, -b, -c, a)


def matrix_word(word, x, y):
    images = {"x": x, "X": matrix_inverse(x), "y": y, "Y": matrix_inverse(y)}
    value = (1, 0, 0, 1)
    for letter in word:
        value = matrix_multiply(value, images[letter])
    return value


def test_fixed_b_braid_representation_and_finite_primitive_trace_controls():
    x, y, identity = (1, 1, 0, 1), (1, 0, -1, 1), (1, 0, 0, 1)
    assert matrix_word("xyxYXY", x, y) == identity
    a_image = matrix_word("xxxYYYY", x, y)
    assert a_image[0] + a_image[3] == 14
    m = matrix_word("xY", x, y)
    assert m == (2, 1, 1, 1)
    assert matrix_multiply(m, m) == tuple(3 * entry - unit for entry, unit in zip(m, identity))
    candidates = tuple(matrix_word("xY" * k + "Y", x, y) for k in range(4))
    traces = tuple(value[0] + value[3] for value in candidates)
    assert traces == (2, 4, 10, 26)
    assert traces[2:] == tuple(3 * traces[index + 1] - traces[index] for index in range(2))
    delta = matrix_word("xyx", x, y)
    delta_inverse = matrix_inverse(delta)
    assert matrix_multiply(matrix_multiply(delta, x), delta_inverse) == y
    assert matrix_multiply(matrix_multiply(delta, y), delta_inverse) == x
    assert matrix_word("xyxYXY", x, (1, 0, 1, 1)) != identity
