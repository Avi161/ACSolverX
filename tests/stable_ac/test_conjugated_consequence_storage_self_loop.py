INVERSE = {
    "x": "X", "X": "x",
    "y": "Y", "Y": "y",
    "z": "Z", "Z": "z",
    "q": "Q", "Q": "q",
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
    positions = [index for index, letter in enumerate(word) if letter in "qQ"]
    assert len(positions) == 1
    index = positions[0]
    left = word[:index]
    right = word[index + 1:]
    if word[index] == "q":
        solution = inverse(left) + inverse(right)
    else:
        solution = right + left
    solution = reduce_word(solution)
    assert substitute_q(word, solution) == ""
    return solution


def substitute_q(word: str, q_solution: str) -> str:
    expanded = "".join(
        q_solution if letter == "q"
        else inverse(q_solution) if letter == "Q"
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
