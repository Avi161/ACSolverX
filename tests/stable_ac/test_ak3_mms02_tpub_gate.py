def _free_reduce(word: tuple[int, ...]) -> tuple[int, ...]:
    reduced: list[int] = []
    for letter in word:
        if reduced and reduced[-1] == -letter:
            reduced.pop()
        else:
            reduced.append(letter)
    return tuple(reduced)


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
