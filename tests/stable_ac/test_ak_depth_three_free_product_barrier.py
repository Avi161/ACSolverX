from collections import Counter
from itertools import product
from math import gcd


FREE_INVERSE = {
    "x": "X",
    "X": "x",
    "y": "Y",
    "Y": "y",
}


def invert_leaves(
    leaves: tuple[tuple[str, int], ...],
) -> tuple[tuple[str, int], ...]:
    return tuple((source, -sign) for source, sign in reversed(leaves))


def canonical_leaf_multiset(
    leaves: tuple[tuple[str, int], ...],
) -> tuple[tuple[str, int], ...]:
    direct = tuple(sorted(leaves))
    inverted = tuple(sorted(invert_leaves(leaves)))
    return min(direct, inverted)


def three_move_leaf_multisets() -> set[tuple[tuple[str, int], ...]]:
    states = {((("A", 1),), (("B", 1),))}
    for _ in range(3):
        next_states = set()
        for rows in states:
            for target in (0, 1):
                source = 1 - target
                for invert_target, invert_source in product((False, True), repeat=2):
                    next_rows = list(rows)
                    left = invert_leaves(rows[target]) if invert_target else rows[target]
                    right = invert_leaves(rows[source]) if invert_source else rows[source]
                    next_rows[target] = left + right
                    next_states.add(tuple(next_rows))
        states = next_states
    return {
        canonical_leaf_multiset(row)
        for rows in states
        for row in rows
        if len(row) > 3
    }


FreeProductWord = tuple[tuple[str, int], ...]


def free_product_multiply(
    left: FreeProductWord,
    right: FreeProductWord,
    orders: dict[str, int],
) -> FreeProductWord:
    reduced = list(left)
    for factor, exponent in right:
        exponent %= orders[factor]
        if not exponent:
            continue
        if reduced and reduced[-1][0] == factor:
            combined = (reduced[-1][1] + exponent) % orders[factor]
            reduced.pop()
            if combined:
                reduced.append((factor, combined))
        else:
            reduced.append((factor, exponent))
    return tuple(reduced)


def free_product_inverse(
    word: FreeProductWord,
    orders: dict[str, int],
) -> FreeProductWord:
    return tuple(
        (factor, (-exponent) % orders[factor])
        for factor, exponent in reversed(word)
    )


def evaluate_free_word(
    word: str,
    images: dict[str, FreeProductWord],
    orders: dict[str, int],
) -> FreeProductWord:
    result: FreeProductWord = ()
    for letter in word:
        image = images[letter.lower()]
        if letter.isupper():
            image = free_product_inverse(image, orders)
        result = free_product_multiply(result, image, orders)
    return result


def cyclic_reduce_free_product(
    word: FreeProductWord,
    orders: dict[str, int],
) -> FreeProductWord:
    reduced = word
    while len(reduced) > 1 and reduced[0][0] == reduced[-1][0]:
        factor = reduced[0][0]
        exponent = (reduced[-1][1] + reduced[0][1]) % orders[factor]
        prefix = ((factor, exponent),) if exponent else ()
        reduced = free_product_multiply(prefix, reduced[1:-1], orders)
    return reduced


def free_product_conjugate(
    left: FreeProductWord,
    right: FreeProductWord,
    orders: dict[str, int],
) -> bool:
    left = cyclic_reduce_free_product(left, orders)
    right = cyclic_reduce_free_product(right, orders)
    if len(left) != len(right):
        return False
    if len(left) < 2:
        return left == right
    return any(left == right[index:] + right[:index] for index in range(len(right)))


def cyclic_rotations(word: FreeProductWord) -> set[FreeProductWord]:
    return {word[index:] + word[:index] for index in range(len(word))}


def reduced_connectors(
    orders: dict[str, int],
    maximum_length: int,
) -> tuple[FreeProductWord, ...]:
    connectors: list[FreeProductWord] = [()]
    frontier: list[FreeProductWord] = [()]
    for _ in range(maximum_length):
        next_frontier = []
        for word in frontier:
            for factor, order in orders.items():
                if word and word[-1][0] == factor:
                    continue
                for exponent in range(1, order):
                    candidate = word + ((factor, exponent),)
                    connectors.append(candidate)
                    next_frontier.append(candidate)
        frontier = next_frontier
    return tuple(connectors)


def signed_christoffel_word(x_exponent: int, y_exponent: int) -> str:
    x_letter = "x" if x_exponent >= 0 else "X"
    y_letter = "y" if y_exponent >= 0 else "Y"
    x_count = abs(x_exponent)
    y_count = abs(y_exponent)
    length = x_count + y_count
    if not x_count:
        return y_letter
    if not y_count:
        return x_letter
    return "".join(
        x_letter
        if ((index + 1) * x_count) // length > (index * x_count) // length
        else y_letter
        for index in range(length)
    )


def test_depth_three_provenance_has_eighteen_new_signed_multisets() -> None:
    multisets = three_move_leaf_multisets()
    signatures = set()
    for leaves in multisets:
        counts = Counter(leaves)
        a_count = counts["A", 1] + counts["A", -1]
        b_count = counts["B", 1] + counts["B", -1]
        a_coefficient = counts["A", 1] - counts["A", -1]
        b_coefficient = counts["B", 1] - counts["B", -1]
        signatures.add((len(leaves), a_count, b_count, a_coefficient, b_coefficient))

    assert len(multisets) == 18
    assert signatures == {
        (4, 3, 1, -3, -1),
        (4, 3, 1, -3, 1),
        (4, 3, 1, -1, -1),
        (4, 3, 1, -1, 1),
        (4, 1, 3, -1, -3),
        (4, 1, 3, -1, -1),
        (4, 1, 3, -1, 1),
        (4, 1, 3, -1, 3),
        (5, 3, 2, -3, -2),
        (5, 3, 2, -3, 2),
        (5, 3, 2, -1, -2),
        (5, 3, 2, -1, 0),
        (5, 3, 2, -1, 2),
        (5, 2, 3, -2, -3),
        (5, 2, 3, -2, -1),
        (5, 2, 3, -2, 1),
        (5, 2, 3, -2, 3),
        (5, 2, 3, 0, -1),
    }


def depth_three_free_product_survivors(
    source_a: str,
    source_b: str,
) -> set[tuple[int, int, int, int, int]]:
    quotients = {
        "kill_a": (
            {"X": 3, "Y": 4},
            {"x": (("X", 1),), "y": (("Y", 1),)},
        ),
        "kill_b": (
            {"s": 2, "t": 3},
            {
                "x": (("t", 2), ("s", 1)),
                "y": (("s", 1), ("t", 2)),
            },
        ),
    }

    assert evaluate_free_word(source_a, *reversed(quotients["kill_a"])) == ()
    assert evaluate_free_word(source_b, *reversed(quotients["kill_b"])) == ()

    survivors = set()
    for leaves in three_move_leaf_multisets():
        counts = Counter(leaves)
        a_count = counts["A", 1] + counts["A", -1]
        b_count = counts["B", 1] + counts["B", -1]
        a_coefficient = counts["A", 1] - counts["A", -1]
        b_coefficient = counts["B", 1] - counts["B", -1]
        vector = (
            3 * a_coefficient + b_coefficient,
            -4 * a_coefficient - b_coefficient,
        )
        assert gcd(abs(vector[0]), abs(vector[1])) == 1
        primitive = signed_christoffel_word(*vector)

        quotient_name = "kill_a" if a_count > b_count else "kill_b"
        orders, images = quotients[quotient_name]
        minority_name = "B" if quotient_name == "kill_a" else "A"
        minority_word = source_b if minority_name == "B" else source_a
        minority_image = cyclic_reduce_free_product(
            evaluate_free_word(minority_word, images, orders),
            orders,
        )
        primitive_image = cyclic_reduce_free_product(
            evaluate_free_word(primitive, images, orders),
            orders,
        )
        minority_signs = [
            sign for source, sign in leaves if source == minority_name
        ]

        if len(leaves) == 4:
            assert len(minority_signs) == 1
            signed_minority = (
                minority_image
                if minority_signs[0] > 0
                else free_product_inverse(minority_image, orders)
            )
            if free_product_conjugate(signed_minority, primitive_image, orders):
                survivors.add(
                    (
                        len(leaves),
                        a_count,
                        b_count,
                        a_coefficient,
                        b_coefficient,
                    )
                )
            continue

        assert len(minority_signs) == 2
        left = (
            minority_image
            if minority_signs[0] > 0
            else free_product_inverse(minority_image, orders)
        )
        right = (
            minority_image
            if minority_signs[1] > 0
            else free_product_inverse(minority_image, orders)
        )
        source_length = len(minority_image)
        primitive_length = len(primitive_image)
        bridge_length = (
            (primitive_length - 2 * source_length) // 2
            if primitive_length >= 2 * source_length
            else 0
        )
        connector_bound = bridge_length + 2

        found = False
        for left_rotation in cyclic_rotations(left):
            for right_rotation in cyclic_rotations(right):
                for connector in reduced_connectors(orders, connector_bound):
                    product_word = free_product_multiply(
                        free_product_multiply(
                            free_product_multiply(
                                left_rotation,
                                connector,
                                orders,
                            ),
                            right_rotation,
                            orders,
                        ),
                        free_product_inverse(connector, orders),
                        orders,
                    )
                    if free_product_conjugate(product_word, primitive_image, orders):
                        found = True
                        break
                if found:
                    break
            if found:
                break
        if found:
            survivors.add(
                (
                    len(leaves),
                    a_count,
                    b_count,
                    a_coefficient,
                    b_coefficient,
                )
            )
    return survivors


def test_every_depth_three_ak_multiset_fails_in_a_free_product_quotient() -> None:
    assert not depth_three_free_product_survivors("xxxYYYY", "xyxYXY")


def test_first_image_depth_three_has_one_residue_after_a_finite_certificate() -> None:
    survivors = depth_three_free_product_survivors(
        "xxxyxYYYYXY",
        "xyxyXYxyxYXYXyxYXY",
    )
    four_leaf = (4, 1, 3, -1, 3)
    five_leaf = (5, 2, 3, 0, -1)
    assert survivors == {four_leaf, five_leaf}

    def compose(
        left: tuple[int, ...],
        right: tuple[int, ...],
    ) -> tuple[int, ...]:
        return tuple(left[right[index]] for index in range(len(left)))

    def inverse(permutation: tuple[int, ...]) -> tuple[int, ...]:
        result = [0] * len(permutation)
        for source, target in enumerate(permutation):
            result[target] = source
        return tuple(result)

    def evaluate(
        word: str,
        x_image: tuple[int, ...],
        y_image: tuple[int, ...],
    ) -> tuple[int, ...]:
        identity = tuple(range(len(x_image)))
        images = {
            "x": x_image,
            "X": inverse(x_image),
            "y": y_image,
            "Y": inverse(y_image),
        }
        result = identity
        for letter in word:
            result = compose(result, images[letter])
        return result

    def cycle_type(permutation: tuple[int, ...]) -> tuple[int, ...]:
        unseen = set(range(len(permutation)))
        lengths = []
        while unseen:
            start = next(iter(unseen))
            current = start
            length = 0
            while current in unseen:
                unseen.remove(current)
                current = permutation[current]
                length += 1
            if length > 1:
                lengths.append(length)
        return tuple(sorted(lengths, reverse=True)) or (1,)

    x_image = (1, 2, 3, 4, 0)
    y_image = (1, 3, 0, 4, 2)
    a_image = evaluate("xxxyxYYYYXY", x_image, y_image)
    b_image = evaluate("xyxyXYxyxYXYXyxYXY", x_image, y_image)
    primitive_image = evaluate("y", x_image, y_image)

    assert cycle_type(a_image) == (3,)
    assert cycle_type(b_image) == (1,)
    assert cycle_type(primitive_image) == (5,)
    survivors.remove(four_leaf)
    assert survivors == {five_leaf}


def test_explicit_target_commutator_does_not_transport_the_fixed_entry() -> None:
    def compose(
        left: tuple[int, ...],
        right: tuple[int, ...],
    ) -> tuple[int, ...]:
        return tuple(left[right[index]] for index in range(len(left)))

    def inverse(permutation: tuple[int, ...]) -> tuple[int, ...]:
        result = [0] * len(permutation)
        for source, target in enumerate(permutation):
            result[target] = source
        return tuple(result)

    def evaluate(
        word: str,
        x_image: tuple[int, ...],
        y_image: tuple[int, ...],
    ) -> tuple[int, ...]:
        images = {
            "x": x_image,
            "X": inverse(x_image),
            "y": y_image,
            "Y": inverse(y_image),
        }
        result = tuple(range(len(x_image)))
        for letter in word:
            result = compose(result, images[letter])
        return result

    def cycle_type(permutation: tuple[int, ...]) -> tuple[int, ...]:
        unseen = set(range(len(permutation)))
        lengths = []
        while unseen:
            current = next(iter(unseen))
            length = 0
            while current in unseen:
                unseen.remove(current)
                current = permutation[current]
                length += 1
            if length > 1:
                lengths.append(length)
        return tuple(sorted(lengths, reverse=True)) or (1,)

    x_image = (1, 2, 3, 0)
    y_image = (1, 3, 0, 2)
    u_image = evaluate("yxyXY", x_image, y_image)
    a_image = evaluate("xxxyxYYYYXY", x_image, y_image)
    b_image = evaluate("xyxyXYxyxYXYXyxYXY", x_image, y_image)
    r_image = evaluate("XyxYXYXyx", x_image, y_image)
    target_image = evaluate("yX", x_image, y_image)
    commutator_image = compose(
        compose(
            compose(inverse(r_image), x_image),
            r_image,
        ),
        inverse(x_image),
    )

    assert u_image == x_image
    assert b_image == tuple(range(4))
    assert commutator_image == target_image
    assert cycle_type(a_image) == (4,)
    assert cycle_type(r_image) == (2,)


def test_last_residue_cyclic_cover_has_rank_four_monodromy() -> None:
    def inverse(word: tuple[int, ...]) -> tuple[int, ...]:
        return tuple(-letter for letter in reversed(word))

    def reduce_word(word: tuple[int, ...]) -> tuple[int, ...]:
        reduced = []
        for letter in word:
            if reduced and reduced[-1] == -letter:
                reduced.pop()
            else:
                reduced.append(letter)
        return tuple(reduced)

    def substitute(
        word: tuple[int, ...],
        images: dict[int, tuple[int, ...]],
    ) -> tuple[int, ...]:
        result: tuple[int, ...] = ()
        for letter in word:
            image = images[abs(letter)]
            if letter < 0:
                image = inverse(image)
            result = reduce_word(result + image)
        return result

    def magnus_rewrite(word: str) -> tuple[tuple[int, ...], int]:
        height = 0
        kernel_word = []
        for letter in word:
            if letter == "x":
                height += 1
            elif letter == "X":
                height -= 1
            elif letter == "y":
                kernel_word.append(height)
                height += 1
            else:
                height -= 1
                kernel_word.append(-height - 1)
        return tuple(kernel_word), height

    relator, exponent = magnus_rewrite("xyxyXYxyxYXYXyxYXY")
    assert exponent == 0
    assert relator == (1, 3, -3, 3, -5, -3, 1, -3, -1)

    z4 = (-3, 2, -3, -1, 2, 4, -3, 4)
    z_minus_one = (1, 3, -2, 3, -4, -2, 1, -2)
    monodromy = {
        1: (2,),
        2: (3,),
        3: (4,),
        4: z4,
    }
    inverse_monodromy = {
        1: z_minus_one,
        2: (1,),
        3: (2,),
        4: (3,),
    }

    for generator in range(1, 5):
        assert substitute(substitute((generator,), monodromy), inverse_monodromy) == (
            generator,
        )
        assert substitute(substitute((generator,), inverse_monodromy), monodromy) == (
            generator,
        )

    a_rewrite, a_exponent = magnus_rewrite("xxxyxYYYYXY")
    assert a_exponent == -1
    z4_image = z4
    z_minus_one_image = z_minus_one
    q = reduce_word(
        (4,)
        + inverse(z4_image)
        + (-4, -3, -2)
        + inverse(z_minus_one_image)
    )
    assert a_rewrite == (3, -5, -4, -3, -2, 0)
    assert q == (3, -4, -2, 1, 3, -2, 3, -4, -3, -1, 2, 4, -3, 2, -3, -1)

    explicit_commutator_entry = (
        3,
        -4,
        -2,
        1,
        -2,
        -1,
        2,
        -1,
        2,
        4,
        -3,
        2,
        -3,
        -1,
    )
    explicit_commutator = reduce_word(
        substitute(inverse(explicit_commutator_entry), monodromy)
        + substitute(
            substitute(explicit_commutator_entry, monodromy),
            monodromy,
        )
    )
    assert explicit_commutator == (1,)
