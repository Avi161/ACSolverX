def _free_reduce(word: tuple[int, ...]) -> tuple[int, ...]:
    reduced: list[int] = []
    for letter in word:
        if reduced and reduced[-1] == -letter:
            reduced.pop()
        else:
            reduced.append(letter)
    return tuple(reduced)


def _word_inverse(word: str) -> str:
    return word[::-1].swapcase()


def _word_product(*words: str) -> str:
    reduced: list[str] = []
    for letter in "".join(words):
        if reduced and reduced[-1] == letter.swapcase():
            reduced.pop()
        else:
            reduced.append(letter)
    return "".join(reduced)


def _word_commutator(left: str, right: str) -> str:
    return _word_product(left, right, _word_inverse(left), _word_inverse(right))


def _magnus_rewrite(word: str) -> tuple[tuple[int, int], ...]:
    height = 0
    output: list[tuple[int, int]] = []
    for letter in word:
        if letter == "x":
            height += 1
        elif letter == "X":
            height -= 1
        elif letter == "y":
            output.append((height, 1))
        elif letter == "Y":
            output.append((height, -1))
        else:
            raise AssertionError(f"unexpected letter {letter!r}")
    assert height == 0
    return tuple(output)


def _substitute_d_inverse(word: tuple[int, ...]) -> tuple[int, ...]:
    d_inverse = (2, -1, -2, 1, -2, -2)
    d = tuple(-letter for letter in reversed(d_inverse))
    expanded: list[int] = []
    for letter in word:
        if letter == -3:
            expanded.extend(d_inverse)
        elif letter == 3:
            expanded.extend(d)
        else:
            expanded.append(letter)
    return _free_reduce(tuple(expanded))


def _xy_to_at(word: str) -> tuple[int, ...]:
    images = {
        "x": (1, 2),
        "X": (-2, -1),
        "y": (2,),
        "Y": (-2,),
    }
    expanded = tuple(letter for value in word for letter in images[value])
    return _free_reduce(expanded)


def _stable_rewrite(word: tuple[int, ...]) -> tuple[tuple[int, int], ...]:
    height = 0
    output: list[tuple[int, int]] = []
    for letter in word:
        if abs(letter) == 2:
            height += 1 if letter > 0 else -1
        else:
            assert abs(letter) == 1
            output.append((height, 1 if letter > 0 else -1))
    assert height == 0
    return tuple(output)


def _substitute(
    word: tuple[int, ...],
    images: dict[int, tuple[int, ...]],
) -> tuple[int, ...]:
    expanded: list[int] = []
    for letter in word:
        image = images[abs(letter)]
        if letter < 0:
            image = tuple(-entry for entry in reversed(image))
        expanded.extend(image)
    return _free_reduce(tuple(expanded))


def test_gate_a_magnus_base_and_defect_normal_form() -> None:
    assert _magnus_rewrite("xYxYXyyXYxyXy") == (
        (1, -1),
        (2, -1),
        (1, 1),
        (1, 1),
        (0, -1),
        (1, 1),
        (0, 1),
    )
    assert _magnus_rewrite("YXyyXYxyxY") == (
        (0, -1),
        (-1, 1),
        (-1, 1),
        (-2, -1),
        (-1, 1),
        (0, -1),
    )

    base_relator = (-2, -3, 2, 2, -1, 2, 1)
    assert _substitute_d_inverse(base_relator) == ()

    shifted_defect = (-3, 2, 2, -1, 2, -3)
    reduced_defect = (2, -1, 2, -1, -2, 1, -2, -2)
    assert _substitute_d_inverse(shifted_defect) == reduced_defect
    assert _free_reduce(reduced_defect) == reduced_defect

    def a_exponent(word: tuple[int, ...]) -> int:
        return sum(1 if letter == 1 else -1 if letter == -1 else 0 for letter in word)

    delta = reduced_defect
    delta_squared = _free_reduce((*delta, *delta))
    d_inverse = (2, -1, -2, 1, -2, -2)
    d = tuple(-letter for letter in reversed(d_inverse))
    phi_a = (2,)
    phi_b = d
    assert a_exponent(delta) == -1
    assert a_exponent(delta_squared) == -2
    assert a_exponent(phi_a) == 0
    assert a_exponent(phi_b) == 0

    shifted_q_tokens = ["x", "x", "X", "a", "X", "X"]
    freely_reduced_tokens: list[str] = []
    for token in shifted_q_tokens:
        if freely_reduced_tokens and {freely_reduced_tokens[-1], token} == {"x", "X"}:
            freely_reduced_tokens.pop()
        else:
            freely_reduced_tokens.append(token)
    assert freely_reduced_tokens == ["x", "a", "X", "X"]
    assert freely_reduced_tokens[:3] == ["x", "a", "X"]
    hnn_reduced_tokens = ["b", *freely_reduced_tokens[3:]]
    assert hnn_reduced_tokens == ["b", "X"]
    shifted_q = ((2,), hnn_reduced_tokens[1])

    def inverse_hnn(word: tuple[tuple[int, ...] | str, ...]):
        inverse_word: list[tuple[int, ...] | str] = []
        for syllable in reversed(word):
            if isinstance(syllable, str):
                inverse_word.append(syllable.swapcase())
            else:
                inverse_word.append(tuple(-letter for letter in reversed(syllable)))
        return tuple(inverse_word)

    def product_hnn(*words: tuple[tuple[int, ...] | str, ...]):
        output: list[tuple[int, ...] | str] = []
        for word in words:
            for syllable in word:
                if output and isinstance(output[-1], tuple) and isinstance(syllable, tuple):
                    merged = _free_reduce((*output.pop(), *syllable))
                    if merged:
                        output.append(merged)
                else:
                    output.append(syllable)
        return tuple(output)

    shifted_d = (delta,)
    shifted_e = product_hnn(
        inverse_hnn(shifted_d),
        shifted_q,
        shifted_d,
        shifted_d,
        inverse_hnn(shifted_q),
    )
    assert shifted_e == (
        _free_reduce((*tuple(-letter for letter in reversed(delta)), 2)),
        "X",
        delta_squared,
        "x",
        (-2,),
    )


def test_gate_a_hall_witt_remainder_has_nonempty_magnus_base_form() -> None:
    r = "xyyXY"
    x_r = _word_commutator("X", r)
    remainder = _word_commutator(_word_inverse(r), x_r)
    conjugated_remainder = _word_product("YX", remainder, "xy")
    assert x_r == "yyXYxyxYYX"
    assert remainder == "yxYYXyyXYxxyyXYXyxYY"
    assert conjugated_remainder == "YXyxYYXyyXYxxyyXYXyxYYxy"

    scan = _magnus_rewrite(remainder)
    assert scan == (
        (0, 1),
        (1, -1),
        (1, -1),
        (0, 1),
        (0, 1),
        (-1, -1),
        (1, 1),
        (1, 1),
        (0, -1),
        (-1, 1),
        (0, -1),
        (0, -1),
    )
    shifted_base = tuple(sign * (index + 2) for index, sign in scan)
    assert shifted_base == (2, -3, -3, 2, 2, -1, 3, 3, -2, 1, -2, -2)
    reduced_base = _substitute_d_inverse(shifted_base)
    assert reduced_base == (
        2,
        2,
        -1,
        -2,
        1,
        -2,
        -1,
        2,
        -1,
        2,
        1,
        2,
        -1,
        2,
        1,
        -2,
        -2,
        1,
        -2,
        -2,
    )
    assert _free_reduce(reduced_base) == reduced_base


def test_gate_b_nielsen_magnus_base_and_defect_normal_form() -> None:
    relator_at = _xy_to_at("XyyXYXyxYYxy")
    defect_at = _xy_to_at("YxYXyxYYxyXyyyXY")
    assert relator_at == (-2, -1, 2, -1, -2, -2, -1, 2, 1, -2, 1, 2, 2)
    assert defect_at == (-2, 1, -2, -1, 2, 1, -2, 1, 2, -1, 2, 2, -1, -2)

    assert _stable_rewrite(relator_at) == (
        (-1, -1),
        (0, -1),
        (-2, -1),
        (-1, 1),
        (-2, 1),
    )
    assert _stable_rewrite(defect_at) == (
        (-1, 1),
        (-2, -1),
        (-1, 1),
        (-2, 1),
        (-1, -1),
        (1, -1),
    )

    d_inverse = (2, -1, -2, 1)
    base_relator = (-2, -3, -1, 2, 1)
    d = tuple(-entry for entry in reversed(d_inverse))
    assert _substitute(base_relator, {1: (1,), 2: (2,), 3: d}) == ()

    phi_d_inverse = _substitute(d_inverse, {1: (2,), 2: d})
    assert phi_d_inverse == (-1, 2, 1, -2, -1, -2, 1, 2)

    base_prefix = (2, -1, 2, 1, -2)
    reduced_defect = _free_reduce((*base_prefix, *phi_d_inverse))
    assert reduced_defect == (2, -1, 2, 1, -2, -1, 2, 1, -2, -1, -2, 1, 2)
