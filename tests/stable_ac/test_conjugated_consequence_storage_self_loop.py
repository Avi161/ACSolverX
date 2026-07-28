INVERSE = {
    "x": "X", "X": "x",
    "y": "Y", "Y": "y",
    "z": "Z", "Z": "z",
    "q": "Q", "Q": "q",
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


def solve_unique_q(word: str) -> str:
    return solve_unique_generator(word, "q")


def solve_unique_generator(word: str, generator: str) -> str:
    generator_inverse = INVERSE[generator]
    positions = [
        index
        for index, letter in enumerate(word)
        if letter in (generator, generator_inverse)
    ]
    assert len(positions) == 1
    index = positions[0]
    left = word[:index]
    right = word[index + 1:]
    if word[index] == generator:
        solution = inverse(left) + inverse(right)
    else:
        solution = right + left
    solution = reduce_word(solution)
    assert substitute_generator(word, generator, solution) == ""
    return solution


def substitute_q(word: str, q_solution: str) -> str:
    return substitute_generator(word, "q", q_solution)


def substitute_generator(word: str, generator: str, solution: str) -> str:
    generator_inverse = INVERSE[generator]
    expanded = "".join(
        solution if letter == generator
        else inverse(solution) if letter == generator_inverse
        else letter
        for letter in word
    )
    return reduce_word(expanded)


def test_universal_side_ordered_cancellation() -> None:
    examples = (
        ("xxyY", "yzX", "xyX"),
        ("xyz", "YZX", "zxy"),
        ("xxxYYYY", "yyyXXXX", "y"),
    )
    for a, c, g in examples:
        left = reduce_word(a + g)
        right = reduce_word(c + inverse(g))
        primitive = reduce_word(left + "q" + right)
        q_solution = reduce_word(inverse(left) + inverse(right))

        assert reduce_word(primitive.replace("q", q_solution)) == ""
        assert reduce_word(q_solution + c) == reduce_word(
            inverse(g) + inverse(a) + g
        )


def test_ak3_swapped_consequence_route_returns_to_power_relator() -> None:
    a = "xxxYYYY"
    c = "yyyXXXX"
    g = "y"
    left = reduce_word(a + g)
    right = reduce_word(c + inverse(g))
    primitive = reduce_word(left + "q" + right)
    q_solution = reduce_word(inverse(left) + inverse(right))

    assert primitive == "xxxYYYqyyyXXXXY"
    assert reduce_word(primitive.replace("q", q_solution)) == ""
    assert reduce_word(q_solution + c) == reduce_word(
        inverse(g) + inverse(a) + g
    )
    assert reduce_word(q_solution + c) == "yyyXXXy"


def test_braid_swap_identities_are_exact() -> None:
    braid = "xyxYXY"
    delta = "xyx"

    assert reduce_word(delta + "x" + inverse(delta) + "Y") == braid
    assert reduce_word(delta + "y" + inverse(delta)) == reduce_word(
        "x" + inverse(braid)
    )


def test_braid_source_is_standard_torus_relator_in_explicit_basis() -> None:
    braid = "xyxYXY"
    a = "xyx"
    b = "xy"
    x_in_ab = inverse(b) + a
    y_in_ab = inverse(a) + b + b

    assert reduce_word(x_in_ab) == "x"
    assert reduce_word(y_in_ab) == "y"
    assert reduce_word(a + inverse(b) * 3 + a) == braid
    assert reduce_word(a + braid + inverse(a)) == reduce_word(
        a + a + inverse(b) * 3
    )


def test_two_source_combination_and_length_two_exception_are_exact() -> None:
    a = "xxxYYYY"
    b = "xyxYXY"
    c = "xry"
    d = "RYx"

    for epsilon in (1, -1):
        a_power = a if epsilon == 1 else inverse(a)
        for eta in (1, -1):
            b_power = b if eta == 1 else inverse(b)
            target = reduce_word(
                "r" + c + a_power + inverse(c)
                + d + b_power + inverse(d)
            )
            relative = reduce_word(inverse(c) + d)
            combined_source = reduce_word(
                a_power + relative + b_power + inverse(relative)
            )

            assert target == reduce_word(
                "r" + c + combined_source + inverse(c)
            )

    apparent_two_location = reduce_word("r" + a + "r" + b + "R")
    unique_r_conjugate = reduce_word("R" + apparent_two_location + "r")

    assert unique_r_conjugate == a + "r" + b
    assert sum(letter in "rR" for letter in unique_r_conjugate) == 1


def test_two_storage_nontarget_moves_descend_to_survivor_moves() -> None:
    a = "xyX"
    c = "zY"
    g = "yx"
    r_word = "zyX"
    u = "xz"
    q_word = "q" + c

    for epsilon in (1, -1):
        q_power = q_word if epsilon == 1 else inverse(q_word)
        primitive = reduce_word(a + g + q_power + inverse(g))
        q_solution = solve_unique_q(primitive)
        k = reduce_word(
            inverse(g) + (inverse(a) if epsilon == 1 else a) + g
        )
        h_r = reduce_word(u + r_word + inverse(u))

        assert substitute_q(q_word, q_solution) == k
        assert substitute_q(q_word + h_r, q_solution) == reduce_word(k + h_r)
        assert substitute_q(h_r + q_word, q_solution) == reduce_word(h_r + k)

        h_q = reduce_word(u + q_word + inverse(u))
        assert substitute_q(r_word + h_q, q_solution) == reduce_word(
            r_word + u + k + inverse(u)
        )
        assert substitute_q(h_q + r_word, q_solution) == reduce_word(
            u + k + inverse(u) + r_word
        )


def test_two_storage_target_correction_is_peeled_by_surviving_row() -> None:
    a = "xyX"
    c = "zY"
    g = "yx"
    r_word = "zyX"
    u = "xz"
    q_word = "q" + c
    h_r = reduce_word(u + r_word + inverse(u))

    for epsilon in (1, -1):
        q_power = q_word if epsilon == 1 else inverse(q_word)
        primitive = reduce_word(a + g + q_power + inverse(g))
        k = reduce_word(
            inverse(g) + (inverse(a) if epsilon == 1 else a) + g
        )

        for changed_target in (
            reduce_word(primitive + h_r),
            reduce_word(h_r + primitive),
        ):
            q_solution = solve_unique_q(changed_target)
            survivor_q = substitute_q(q_word, q_solution)

            if epsilon == 1:
                correction = reduce_word(inverse(g) + inverse(h_r) + g)
                assert survivor_q == reduce_word(k + correction)
                assert reduce_word(
                    survivor_q + inverse(correction)
                ) == k
            else:
                correction = reduce_word(inverse(g) + h_r + g)
                assert survivor_q == reduce_word(correction + k)
                assert reduce_word(
                    inverse(correction) + survivor_q
                ) == k


def test_target_peeling_allows_a_q_dependent_conjugator() -> None:
    a = "x"
    c = "z"
    q_word = "q" + c
    primitive = a + q_word
    source = "X"
    conjugator = inverse(q_word)
    h = reduce_word(conjugator + source + inverse(conjugator))
    changed_target = reduce_word(primitive + h)

    assert changed_target == "qz"
    q_solution = solve_unique_q(changed_target)
    survivor_q = substitute_q(q_word, q_solution)
    h_image = substitute_q(h, q_solution)
    k = inverse(a)

    assert h_image == source
    assert survivor_q == reduce_word(k + inverse(h_image))
    assert reduce_word(survivor_q + h_image) == k


def test_q_bearing_source_cannot_leave_one_q_letter() -> None:
    q_word = "qz"
    primitive = reduce_word("xy" + q_word + "Y")

    for epsilon in (1, -1):
        q_source = q_word if epsilon == 1 else inverse(q_word)
        for conjugator in ("", "qX", "zQy"):
            h_q = reduce_word(
                conjugator + q_source + inverse(conjugator)
            )
            for changed_target in (
                reduce_word(primitive + h_q),
                reduce_word(h_q + primitive),
            ):
                q_count = sum(letter in "qQ" for letter in changed_target)
                assert q_count % 2 == 0
                assert q_count != 1


def test_changed_second_storage_source_cycle_recovers_the_old_row() -> None:
    a = "xyX"
    c = "zY"
    d = "Yx"
    g = "yx"
    q_word = "q" + c
    r_word = "r" + d

    for epsilon in (1, -1):
        q_power = q_word if epsilon == 1 else inverse(q_word)
        h_q_for_p = reduce_word(g + q_power + inverse(g))
        p = reduce_word(a + h_q_for_p)

        for delta in (1, -1):
            q_source = q_word if delta == 1 else inverse(q_word)
            h_q_for_r = reduce_word("xz" + q_source + "ZX")

            for r_prime in (
                reduce_word(r_word + h_q_for_r),
                reduce_word(h_q_for_r + r_word),
            ):
                for eta in (1, -1):
                    r_power = r_prime if eta == 1 else inverse(r_prime)
                    conjugator = "qX"
                    h_r = reduce_word(
                        conjugator + r_power + inverse(conjugator)
                    )

                    for eliminator in (
                        reduce_word(p + h_r),
                        reduce_word(h_r + p),
                    ):
                        r_solution = solve_unique_generator(eliminator, "r")
                        assert substitute_generator(
                            eliminator, "r", r_solution
                        ) == ""

                        survivor_r = substitute_generator(
                            r_prime, "r", r_solution
                        )
                        expected = reduce_word(
                            inverse(conjugator)
                            + (inverse(p) if eta == 1 else p)
                            + conjugator
                        )
                        assert survivor_r == expected

                        oriented = inverse(survivor_r) if eta == 1 else survivor_r
                        assert reduce_word(
                            conjugator + oriented + inverse(conjugator)
                        ) == p
                        assert reduce_word(p + inverse(h_q_for_p)) == a
                        assert reduce_word(q_word + inverse(c)) == "q"


def test_changed_source_cycle_allows_an_r_dependent_conjugator() -> None:
    p = "xq"
    r_prime = "r"
    conjugator = "R"
    h_r = reduce_word(
        conjugator + r_prime + inverse(conjugator)
    )
    eliminator = reduce_word(p + h_r)
    r_solution = solve_unique_generator(eliminator, "r")
    conjugator_image = substitute_generator(
        conjugator, "r", r_solution
    )
    survivor_r = substitute_generator(r_prime, "r", r_solution)

    assert h_r == "r"
    assert substitute_generator(eliminator, "r", r_solution) == ""
    assert survivor_r == reduce_word(
        inverse(conjugator_image) + inverse(p) + conjugator_image
    )
    assert survivor_r == inverse(p)


def test_zero_bridge_primitive_slot_traffic_reduces_to_unique_r() -> None:
    source = "xyX"
    old_conjugator = "zY"

    for exponent in range(-3, 4):
        r_power = "r" * exponent if exponent >= 0 else "R" * (-exponent)
        conjugator = r_power + old_conjugator

        for sign in (1, -1):
            source_power = source if sign == 1 else inverse(source)
            h = reduce_word(
                conjugator + source_power + inverse(conjugator)
            )
            right_target = reduce_word("r" + h)
            left_target = reduce_word(h + "r")

            left_as_right = reduce_word(
                inverse(h) + left_target + h
            )
            assert left_as_right == right_target

            normalized = reduce_word(
                inverse(r_power) + right_target + r_power
            )
            expected = reduce_word(
                "r"
                + old_conjugator
                + source_power
                + inverse(old_conjugator)
            )
            assert normalized == expected

            r_solution = solve_unique_generator(normalized, "r")
            assert substitute_generator(normalized, "r", r_solution) == ""
            assert "r" not in source.lower()
