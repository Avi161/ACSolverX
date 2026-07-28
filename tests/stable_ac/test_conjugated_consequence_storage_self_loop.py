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
