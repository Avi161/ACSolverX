INVERSE = {
    "x": "X", "X": "x",
    "y": "Y", "Y": "y",
    "z": "Z", "Z": "z",
    "r": "R", "R": "r",
}


def inverse(word: str) -> str:
    return "".join(INVERSE[letter] for letter in reversed(word))


def reduce_word(word: str) -> str:
    stack: list[str] = []
    for letter in word:
        if stack and INVERSE[letter] == stack[-1]:
            stack.pop()
        else:
            stack.append(letter)
    return "".join(stack)


def cyclic_reduce(word: str) -> str:
    reduced = reduce_word(word)
    while len(reduced) > 1 and INVERSE[reduced[0]] == reduced[-1]:
        reduced = reduce_word(reduced[1:-1])
    return reduced


def cyclic_factors(word: str, length: int) -> set[str]:
    assert 0 < length <= len(word)
    wrapped = word + word[:length - 1]
    return {wrapped[index:index + length] for index in range(len(word))}


def cyclic_rotations(word: str) -> tuple[str, ...]:
    return tuple(word[index:] + word[:index] for index in range(len(word)))


def longest_common_cyclic_factor(left: str, right: str) -> int:
    for length in range(min(len(left), len(right)), 0, -1):
        if cyclic_factors(left, length) & cyclic_factors(right, length):
            return length
    return 0


def substitute(word: str, generator: str, image: str) -> str:
    inverse_generator = INVERSE[generator]
    return reduce_word("".join(
        image if letter == generator
        else inverse(image) if letter == inverse_generator
        else letter
        for letter in word
    ))


def compose(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(left[right[index]] for index in range(len(left)))


def permutation_inverse(permutation: tuple[int, ...]) -> tuple[int, ...]:
    result = [0] * len(permutation)
    for source, target in enumerate(permutation):
        result[target] = source
    return tuple(result)


def evaluate_permutation_word(
    word: str,
    x_image: tuple[int, ...],
    y_image: tuple[int, ...],
) -> tuple[int, ...]:
    identity = tuple(range(len(x_image)))
    images = {
        "x": x_image,
        "X": permutation_inverse(x_image),
        "y": y_image,
        "Y": permutation_inverse(y_image),
    }
    result = identity
    for letter in word:
        result = compose(result, images[letter])
    return result


def generated_subgroup(
    generators: tuple[tuple[int, ...], ...],
) -> set[tuple[int, ...]]:
    identity = tuple(range(len(generators[0])))
    steps = generators + tuple(permutation_inverse(item) for item in generators)
    subgroup = {identity}
    frontier = [identity]
    while frontier:
        current = frontier.pop()
        for step in steps:
            candidate = compose(current, step)
            if candidate not in subgroup:
                subgroup.add(candidate)
                frontier.append(candidate)
    return subgroup


def test_primitive_syllable_six_relator_realizes_the_embedding() -> None:
    primitive = "ZrxrXR"
    z_solution = "rxrXR"

    assert primitive.count("z") + primitive.count("Z") == 1
    assert substitute(primitive, "z", z_solution) == ""
    assert z_solution.replace("r", "y").replace("R", "Y") == "yxyXY"

    old_a = "xxxZZZZ"
    old_b = "xzxZXZ"
    endpoint = (
        substitute(old_a, "z", z_solution),
        substitute(old_b, "z", z_solution),
    )

    assert all("z" not in word and "Z" not in word for word in endpoint)


def test_both_torus_coefficient_images_are_proper_in_finite_quotients() -> None:
    x_s4 = (0, 2, 3, 1)
    y_s4 = (1, 0, 2, 3)
    u_s4 = evaluate_permutation_word("yxyXY", x_s4, y_s4)
    identity_s4 = tuple(range(4))

    assert u_s4 == (0, 2, 1, 3)
    assert compose(compose(x_s4, x_s4), x_s4) == identity_s4
    assert compose(compose(compose(u_s4, u_s4), u_s4), u_s4) == identity_s4
    assert y_s4 not in generated_subgroup((x_s4, u_s4))

    x_s3 = (0, 2, 1)
    y_s3 = (1, 0, 2)
    u_s3 = evaluate_permutation_word("yxyXY", x_s3, y_s3)

    assert u_s3 == x_s3
    assert evaluate_permutation_word("xyxYXY", x_s3, u_s3) == tuple(range(3))
    assert y_s3 not in generated_subgroup((x_s3, u_s3))


def test_first_proper_corridor_has_an_ambient_conjugator_length_gap() -> None:
    old_a = "xxxYYYY"
    old_b = "xyxYXY"
    u = "yxyXY"
    image_a = cyclic_reduce(substitute(old_a, "y", u))
    image_b = cyclic_reduce(substitute(old_b, "y", u))

    assert image_a == "xxxyxYYYYXY"
    assert image_b == "xyxyXYxyxYXYXyxYXY"
    assert len(image_a) == 11
    assert len(image_b) == 18

    positive_overlap = longest_common_cyclic_factor(image_a, inverse(image_b))
    negative_overlap = longest_common_cyclic_factor(image_a, image_b)

    assert positive_overlap == 3
    assert cyclic_factors(image_a, 4).isdisjoint(
        cyclic_factors(inverse(image_b), 4)
    )
    assert negative_overlap == 4
    assert cyclic_factors(image_a, 5).isdisjoint(cyclic_factors(image_b, 5))

    assert len(image_a) + len(image_b) - 2 * positive_overlap == 23
    assert len(image_a) + len(image_b) - 2 * negative_overlap == 21

    positive_rotation_minimum = min(
        len(cyclic_reduce(left + right))
        for left in cyclic_rotations(image_a)
        for right in cyclic_rotations(image_b)
    )
    negative_rotation_minimum = min(
        len(cyclic_reduce(left + right))
        for left in cyclic_rotations(image_a)
        for right in cyclic_rotations(inverse(image_b))
    )

    assert positive_rotation_minimum == 23
    assert negative_rotation_minimum == 21


def test_all_shortest_normalized_proper_corridors_clear_the_boundary_case() -> None:
    old_a = "xxxYYYY"
    old_b = "xyxYXY"

    for conjugator in ("yx", "yX", "Yx", "YX"):
        u = conjugator + "y" + inverse(conjugator)
        image_a = cyclic_reduce(substitute(old_a, "y", u))
        image_b = cyclic_reduce(substitute(old_b, "y", u))

        assert len(image_a) == 11
        assert len(image_b) == 18

        positive_minimum = min(
            len(cyclic_reduce(left + right))
            for left in cyclic_rotations(image_a)
            for right in cyclic_rotations(image_b)
        )
        negative_minimum = min(
            len(cyclic_reduce(left + right))
            for left in cyclic_rotations(image_a)
            for right in cyclic_rotations(inverse(image_b))
        )

        assert positive_minimum == 23
        assert negative_minimum == 21


def test_first_image_off_diagonal_core_overlap_is_exactly_two() -> None:
    transitions = {
        (0, "x"): 0,
        (0, "X"): 0,
        (0, "y"): 1,
        (1, "Y"): 0,
        (1, "x"): 2,
        (2, "X"): 1,
        (2, "y"): 2,
        (2, "Y"): 2,
    }

    def endpoint(start: int, word: str) -> int | None:
        vertex = start
        for letter in word:
            if (vertex, letter) not in transitions:
                return None
            vertex = transitions[vertex, letter]
        return vertex

    reduced_length_three = (
        first + second + third
        for first in "xXyY"
        for second in "xXyY"
        if second != INVERSE[first]
        for third in "xXyY"
        if third != INVERSE[second]
    )
    for word in reduced_length_three:
        starts = [vertex for vertex in range(3) if endpoint(vertex, word) is not None]
        assert len(starts) <= 1

    assert endpoint(0, "xy") is not None
    assert endpoint(1, "xy") is not None
    assert endpoint(1, "YX") is not None
    assert endpoint(2, "YX") is not None


def test_external_double_coset_minimum_has_exact_witnesses() -> None:
    image_a = "xxxyxYYYYXY"
    image_b = "xyxyXYxyxYXYXyxYXY"

    positive_conjugator = "y"
    negative_conjugator = "xxYX"
    positive = cyclic_reduce(
        image_a + positive_conjugator + image_b + inverse(positive_conjugator)
    )
    negative = cyclic_reduce(
        image_a + negative_conjugator + inverse(image_b)
        + inverse(negative_conjugator)
    )

    assert len(positive) == 25
    assert len(negative) == 25

    transitions = {
        (0, "x"): 0,
        (0, "X"): 0,
        (0, "y"): 1,
        (1, "Y"): 0,
        (1, "x"): 2,
        (2, "X"): 1,
        (2, "y"): 2,
        (2, "Y"): 2,
    }

    for conjugator in (positive_conjugator, negative_conjugator):
        vertex = 0
        readable = True
        for letter in conjugator:
            if (vertex, letter) not in transitions:
                readable = False
                break
            vertex = transitions[vertex, letter]
        assert not readable or vertex != 0
