from experiments.stable_ac.depth4_flat_fatgraph_certificate import verify_certificate


def test_flat_eight_class_problem_has_a_connected_planar_solution() -> None:
    certificate = verify_certificate()

    assert certificate.positions == 62
    assert certificate.edges == 31
    assert certificate.vertices == 24
    assert certificate.boundaries == 9
    assert certificate.euler_characteristic == -7
    assert certificate.genus == 0
    assert certificate.connected
    assert certificate.pair_sha256 == (
        "31cfe882040611148ae5061aedf04aab1d827fb1fe1e6e8b922260830a5e703a"
    )


def freely_reduce(word):
    reduced = []
    for letter in word:
        if reduced and reduced[-1] == -letter:
            reduced.pop()
        else:
            reduced.append(letter)
    return tuple(reduced)


def inverse(word):
    return tuple(-letter for letter in reversed(word))


def multiply(*words):
    return freely_reduce(letter for word in words for letter in word)


def evaluate(word, x_image, y_image):
    images = {"x": x_image, "X": inverse(x_image), "y": y_image, "Y": inverse(y_image)}
    value = ()
    for letter in word:
        value = multiply(value, images[letter])
    return value


def syllable_count(word):
    return sum(
        index == 0 or abs(letter) != abs(word[index - 1])
        for index, letter in enumerate(word)
    )


def test_hard_target_is_one_letter_in_an_exact_free_basis() -> None:
    original_x = (1,)
    original_y = (2,)
    basis_c = evaluate("yyX", original_x, original_y)
    basis_d = evaluate("yX", original_x, original_y)
    target = evaluate("yyXyyXyyXyX", original_x, original_y)

    assert multiply(basis_c, basis_c, basis_c, basis_d) == target
    assert multiply(basis_c, inverse(basis_d)) == original_y
    assert multiply(inverse(basis_d), basis_c, inverse(basis_d)) == original_x

    target_letter = (1,)
    c_letter = (2,)
    x_in_target_basis = multiply(
        inverse(target_letter),
        c_letter * 4,
        inverse(target_letter),
        c_letter * 3,
    )
    y_in_target_basis = multiply(c_letter, inverse(target_letter), c_letter * 3)
    source_a = evaluate("xxxYYYY", x_in_target_basis, y_in_target_basis)
    source_b = evaluate("xyxYXY", x_in_target_basis, y_in_target_basis)

    assert syllable_count(source_a) == 12
    assert syllable_count(source_b) == 10
