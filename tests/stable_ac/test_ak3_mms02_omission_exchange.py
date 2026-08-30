from __future__ import annotations

from itertools import permutations


def inverse(word: str) -> str:
    return word[::-1].swapcase()


def free_reduce(word: str) -> str:
    stack: list[str] = []
    for letter in word:
        if stack and stack[-1] == letter.swapcase():
            stack.pop()
        else:
            stack.append(letter)
    return "".join(stack)


def cyclic_reduce(word: str) -> str:
    word = free_reduce(word)
    while len(word) > 1 and word[0] == word[-1].swapcase():
        word = free_reduce(word[1:-1])
    return word


def token(index: int, positive: bool = True) -> str:
    return chr(ord("a") + index - 1) if positive else chr(ord("A") + index - 1)


def equation(index: int, rhs: str) -> str:
    return free_reduce(token(index) + inverse(rhs))


def substitute(word: str, generator: str, image: str) -> str:
    return free_reduce(
        "".join(
            image
            if letter == generator
            else inverse(image)
            if letter == generator.upper()
            else letter
            for letter in word
        )
    )


def solve_unique(relator: str, generator: str) -> str:
    positions = [
        index for index, letter in enumerate(relator) if letter.lower() == generator
    ]
    assert len(positions) == 1
    position = positions[0]
    prefix = relator[:position]
    letter = relator[position]
    suffix = relator[position + 1 :]
    return free_reduce(
        inverse(prefix) + inverse(suffix) if letter == generator else suffix + prefix
    )


def cyclic_class(word: str) -> str:
    word = cyclic_reduce(word)
    candidates = [
        oriented[index:] + oriented[:index]
        for oriented in (word, inverse(word))
        for index in range(len(word))
    ]
    return min(candidates) if candidates else ""


def eliminate(relators: list[str], generator: str) -> tuple[list[str], str]:
    candidates = [
        (len(relator), index, relator)
        for index, relator in enumerate(relators)
        if sum(letter.lower() == generator for letter in relator) == 1
    ]
    assert candidates
    _, index, defining = min(candidates)
    image = solve_unique(defining, generator)
    remaining = [
        cyclic_reduce(substitute(relator, generator, image))
        for other_index, relator in enumerate(relators)
        if other_index != index
    ]
    assert all(generator not in relator.lower() for relator in remaining)
    return remaining, image


def eliminate_equality(
    relators: list[str], generator: str, image: str
) -> list[str]:
    substituted = [cyclic_reduce(substitute(relator, generator, image)) for relator in relators]
    classes: dict[str, list[int]] = {}
    for index, relator in enumerate(substituted):
        classes.setdefault(cyclic_class(relator), []).append(index)
    if "" in classes:
        removed = classes[""][-1]
    else:
        removed = next(indices[-1] for indices in classes.values() if len(indices) > 1)
    return [relator for index, relator in enumerate(substituted) if index != removed]


def misprinted_relators() -> list[str]:
    x = token

    def X(index: int) -> str:
        return token(index, False)

    right_sides = (
        x(10) + x(14) + X(10),
        X(10) + x(1) + x(10),
        X(1) + x(2) + x(1),
        X(6) + x(3) + x(6),
        x(12) + x(4) + X(12),
        X(7) + x(5) + x(7),
        X(4) + x(6) + x(4),
        x(1) + x(7) + X(1),
        X(11) + x(8) + x(11),
        x(14) + x(9) + X(14),
        X(2) + x(10) + x(2),
        X(1) + x(11) + x(1),
        x(5) + x(12) + X(5),
        x(1) + x(13) + X(1),
    )
    return [equation(index, rhs) for index, rhs in enumerate(right_sides, start=1)]


def whitehead_maps(
    generators: tuple[str, ...] = ("x", "t", "z"),
) -> set[tuple[str, ...]]:
    signed = tuple(letter for generator in generators for letter in (generator, generator.upper()))
    maps: set[tuple[str, str, str]] = set()
    for multiplier in signed:
        others = tuple(
            letter
            for letter in signed
            if letter not in (multiplier, multiplier.swapcase())
        )
        for mask in range(1 << len(others)):
            subset = {multiplier}
            subset.update(letter for index, letter in enumerate(others) if mask & (1 << index))
            images: dict[str, str] = {}
            for generator in generators:
                if generator in (multiplier, multiplier.swapcase()):
                    images[generator] = generator
                elif generator in subset and generator.upper() not in subset:
                    images[generator] = generator + multiplier
                elif generator not in subset and generator.upper() in subset:
                    images[generator] = multiplier.swapcase() + generator
                elif generator in subset and generator.upper() in subset:
                    images[generator] = multiplier.swapcase() + generator + multiplier
                else:
                    images[generator] = generator
            maps.add(tuple(images[generator] for generator in generators))
    maps.discard(generators)
    return maps


def apply_map(word: str, images: tuple[str, str, str]) -> str:
    positive = dict(zip(("x", "t", "z"), images))
    return free_reduce(
        "".join(
            positive[letter]
            if letter.islower()
            else inverse(positive[letter.lower()])
            for letter in word
        )
    )


Permutation = tuple[int, ...]


def compose(left: Permutation, right: Permutation) -> Permutation:
    return tuple(left[right[index]] for index in range(len(left)))


def inverse_permutation(value: Permutation) -> Permutation:
    result = [0] * len(value)
    for index, image in enumerate(value):
        result[image] = index
    return tuple(result)


def evaluate(word: str, images: dict[str, Permutation]) -> Permutation:
    result = tuple(range(len(next(iter(images.values())))))
    inverses = {generator: inverse_permutation(value) for generator, value in images.items()}
    for letter in word:
        result = compose(result, images[letter] if letter.islower() else inverses[letter.lower()])
    return result


def cycle_type(value: Permutation) -> tuple[int, ...]:
    seen: set[int] = set()
    lengths: list[int] = []
    for start in range(len(value)):
        if start in seen:
            continue
        current = start
        length = 0
        while current not in seen:
            seen.add(current)
            current = value[current]
            length += 1
        if length > 1:
            lengths.append(length)
    return tuple(sorted(lengths, reverse=True))


def generated_subgroup(generators: tuple[Permutation, ...]) -> set[Permutation]:
    identity = tuple(range(len(generators[0])))
    subgroup = {identity}
    frontier = [identity]
    steps = generators + tuple(inverse_permutation(generator) for generator in generators)
    while frontier:
        current = frontier.pop()
        for step in steps:
            candidate = compose(current, step)
            if candidate not in subgroup:
                subgroup.add(candidate)
                frontier.append(candidate)
    return subgroup


def test_misprinted_omission_routes_have_exact_endpoints() -> None:
    rows = misprinted_relators()
    source = [row for index, row in enumerate(rows) if index != 11]
    for generator, image in (("n", "b"), ("k", "i"), ("i", "h")):
        source = eliminate_equality(source, generator, image)
    source_history = (
        ("m", "elE"),
        ("h", "agA"),
        ("d", "Fcf"),
        ("c", "Aba"),
        ("f", "Geg"),
        ("j", "bagAB"),
        ("b", "aelEA"),
        ("a", "elEgelEGeLE"),
    )
    for generator, expected in source_history:
        source, image = eliminate(source, generator)
        assert image == expected
    rename = str.maketrans("eglEGL", "xyzXYZ")
    assert tuple(word.translate(rename) for word in source) == (
        "xzYXyxZXYxyZ",
        "XyxZXYXyxzXYxy",
    )

    target = [row for index, row in enumerate(rows) if index != 13]
    target.append("Egl")
    target_history = (
        ("e", "gl"),
        ("f", "lg"),
        ("a", "jnJ"),
        ("b", "n"),
        ("h", "kiK"),
        ("i", "Njn"),
        ("j", "nkN"),
        ("l", "Gmg"),
        ("d", "GMgmmg"),
        ("c", "nkNKnknKN"),
        ("g", "nkNKNknknKN"),
        ("m", "nkNKNknknKN"),
        ("k", ""),
        ("n", ""),
    )
    for generator, expected in target_history:
        target, image = eliminate(target, generator)
        assert image == expected
    assert target == []


def test_common_core_reduces_to_one_relator_a5_separation() -> None:
    rows = misprinted_relators()
    probes = (rows[11], rows[13])
    common = [row for index, row in enumerate(rows) if index not in (11, 13)]
    common.append("Egl")
    common_history = (
        ("e", "gl"),
        ("f", "lg"),
        ("a", "jnJ"),
        ("b", "n"),
        ("h", "kiK"),
        ("i", "Njn"),
        ("j", "nkN"),
        ("l", "Gmg"),
        ("d", "GMgmmg"),
        ("c", "nkNKnknKN"),
        ("g", "nkNKNknknKN"),
    )
    for generator, expected in common_history:
        common, image = eliminate(common, generator)
        assert image == expected
        probes = tuple(cyclic_reduce(substitute(probe, generator, image)) for probe in probes)
    assert tuple(common) == (
        "MnkNKNknknKNmmnkNKNKnknKNMnkNKNkNKnknKNmnkNKNknknKN",
        "MMnkNKNKnknKNmnkNKNKnknKNMMnkNKNknknKNmmnkNKNknknKN",
    )
    assert probes == ("nkNKNKnknKNm", "nknKNMnkNK")

    rename = str.maketrans("kmnKMN", "xtzXTZ")
    transformed = [word.translate(rename) for word in (*common, *probes)]
    steps = (
        ("Zx", "t", "z"),
        ("x", "t", "Xzx"),
        ("x", "Ztz", "z"),
        ("x", "Xtx", "z"),
        ("xz", "Ztz", "z"),
    )
    complete_whitehead_set = whitehead_maps()
    assert len(complete_whitehead_set) == 90
    for step in steps:
        assert step in complete_whitehead_set
        transformed = [apply_map(word, step) for word in transformed]
    transformed = tuple(cyclic_reduce(word) for word in transformed)
    assert transformed == ("TxttXTxZXtx", "TTXtXTTxttx", "Xt", "Tz")

    z_image = solve_unique(transformed[0], "z")
    assert z_image == "XtxTxttXTx"
    relator = substitute(transformed[1], "z", z_image)
    probe_12 = substitute(transformed[2], "z", z_image)
    probe_14 = substitute(transformed[3], "z", z_image)
    assert (relator, probe_12, probe_14) == (
        "TTXtXTTxttx",
        "Xt",
        "TXtxTxttXTx",
    )

    x_image = (1, 2, 3, 4, 0)
    t_image = (1, 3, 0, 4, 2)
    images = {"x": x_image, "t": t_image}
    identity = tuple(range(5))
    assert evaluate(relator, images) == identity
    assert cycle_type(evaluate(probe_12, images)) == (3,)
    assert cycle_type(evaluate(probe_14, images)) == (5,)

    z_permutation = evaluate(z_image, images)
    full_images = {**images, "z": z_permutation}
    assert evaluate(transformed[0], full_images) == identity
    assert evaluate(transformed[1], full_images) == identity
    assert cycle_type(evaluate(transformed[2], full_images)) == (3,)
    assert cycle_type(evaluate(transformed[3], full_images)) == (5,)

    vacuous_control = {**images, "z": identity}
    assert evaluate(transformed[0], vacuous_control) != identity
    assert evaluate(transformed[1], vacuous_control) == identity
    assert cycle_type(evaluate(transformed[2], vacuous_control)) == (3,)
    assert cycle_type(evaluate(transformed[3], vacuous_control)) == (5,)

    subgroup = generated_subgroup((x_image, t_image))
    alternating = {
        value
        for value in permutations(range(5))
        if sum(
            value[left] > value[right]
            for left in range(5)
            for right in range(left + 1, 5)
        )
        % 2
        == 0
    }
    assert subgroup == alternating


def test_mms02_omission_exchange_exact_certificate() -> None:
    rows = misprinted_relators()
    common = [*rows[:11], "Egl"]
    probes = list(rows[11:14])
    history = (
        ("e", "gl"),
        ("f", "lg"),
        ("a", "jnJ"),
        ("b", "n"),
        ("h", "kiK"),
        ("i", "Njn"),
        ("j", "nkN"),
        ("d", "Lgll"),
        ("c", "lgLgllGL"),
        ("g", "nkNKNknknKN"),
    )
    for generator, expected in history:
        common, image = eliminate(common, generator)
        assert image == expected
        probes = [cyclic_reduce(substitute(probe, generator, image)) for probe in probes]
    assert common == [
        "lnkNKNknknKNLnkNKNknknKNllnkNKNKnknKNLnkNKNknKN",
        "nkNKNknknKNLLnkNKNKnknKNlnkNKNKnknKNLLnkNKNknknKNll",
    ]
    assert probes == [
        "lnkNKNKnknKN",
        "mnkNKNknknKNLnkNKNKnknKN",
        "nknKNMnkNK",
    ]

    rename = str.maketrans("klmnKLMN", "xtzqXTZQ")
    words = [word.translate(rename) for word in [*common, *probes]]

    def apply_rank_four_map(word: str, images: tuple[str, str, str, str]) -> str:
        positive = dict(zip(("x", "t", "z", "q"), images))
        return free_reduce(
            "".join(
                positive[letter]
                if letter.islower()
                else inverse(positive[letter.lower()])
                for letter in word
            )
        )

    maps = (
        ("Qx", "t", "Qz", "q"),
        ("x", "t", "Xz", "Xqx"),
        ("qxQ", "t", "qz", "q"),
        ("x", "Xtx", "Xz", "q"),
        ("qx", "t", "qz", "q"),
        ("Txt", "t", "Tz", "q"),
        ("x", "Xtx", "Xz", "q"),
        ("txT", "t", "tz", "q"),
        ("x", "Xtx", "Xz", "qx"),
        ("tx", "t", "tz", "tq"),
    )
    complete_rank_four_set = whitehead_maps(("x", "t", "z", "q"))
    assert len(complete_rank_four_set) == 504
    for images in maps:
        assert images in complete_rank_four_set
        words = [apply_rank_four_map(word, images) for word in words]
    words = [cyclic_reduce(word) for word in words]
    assert words[0] == "Q"
    assert cyclic_class(words[1]) == cyclic_class("xTTXXTTxttt")

    relator = cyclic_reduce(substitute(words[1], "q", ""))
    target_probe = substitute(words[2], "q", "")
    bad_probe = substitute(words[3], "q", "")
    probe_14 = substitute(words[4], "q", "")
    assert relator == "xTTXXTTxttt"
    assert target_probe == "X"
    assert bad_probe == "ttXTTXtxTTXTTXXTTXzXXTTXtxTTXXTxTXtxxttXTxttxx"
    assert probe_14 == "xZxttxxttxttXTxttxTTXXTTXtxxttXTxttx"

    prefix = "ttXTTXtxTTXTTXXTTX"
    suffix = "XXTTXtxTTXXTxTXtxxttXTxttxx"
    alpha_image = inverse(prefix) + "z" + inverse(suffix)
    assert substitute(relator, "z", alpha_image) == relator
    assert substitute(bad_probe, "z", alpha_image) == "z"
    assert substitute(substitute(probe_14, "z", alpha_image), "z", "") == (
        "XTTXtxTTXXTxTXtxxttxttXTxttx"
    )


def test_mms02_omission_exchange_trefoil_return() -> None:
    relator = "xTTXXTTxttt"
    h_long = "XTTXtxTTXXTxTXtxxttxttXTxttx"
    h0 = cyclic_reduce(h_long)
    assert h0 == "XTxTXtxxtt"
    conjugator = "XTTXtxTTX"
    assert h_long == conjugator + h0 + inverse(conjugator)

    donor = "TTXXTTxtttx"
    assert donor in tuple(relator[index:] + relator[:index] for index in range(len(relator)))
    assert free_reduce(h0 + donor) == "XTxTXTxtttx"
    companion = cyclic_reduce(h0 + donor)
    assert companion == "xTXTxtt"

    def apply_rank_two_map(word: str, images: tuple[str, str]) -> str:
        positive = dict(zip(("x", "t"), images))
        return free_reduce(
            "".join(
                positive[letter]
                if letter.islower()
                else inverse(positive[letter.lower()])
                for letter in word
            )
        )

    rows = [relator, companion]
    for _ in range(2):
        rows = [apply_rank_two_map(word, ("Tx", "t")) for word in rows]
    rows = [cyclic_reduce(word) for word in rows]
    assert rows == ["xTTXttXTTxt", "xTXTx"]
    assert cyclic_class(rows[1]) == cyclic_class("txtXX")
    rows[1] = "txtXX"

    rows = [apply_rank_two_map(word, ("x", "tX")) for word in rows]
    rows = [cyclic_reduce(word) for word in rows]
    assert rows == ["xTxTXtXtXTxTxt", "ttXXX"]
    relator_w, torus = rows

    def apply_ak3_map(word: str) -> str:
        positive = {"u": "Xt", "v": "Txx"}
        return free_reduce(
            "".join(
                positive[letter]
                if letter.islower()
                else inverse(positive[letter.lower()])
                for letter in word
            )
        )

    ak3_relator = apply_ak3_map("uuuVVVV")
    ak3_probe = apply_ak3_map("uvuVUV")
    assert ak3_relator == "XtXtXtXXtXXtXXtXXt"
    assert cyclic_class(ak3_probe) == cyclic_class(torus)

    def normal_form(word: str) -> tuple[int, tuple[tuple[str, int], ...]]:
        central = 0
        blocks: list[tuple[str, int]] = []
        moduli = {"x": 3, "t": 2}

        for letter in word:
            generator = letter.lower()
            exponent = 1 if letter.islower() else -1
            if blocks and blocks[-1][0] == generator:
                exponent += blocks.pop()[1]
            quotient, residue = divmod(exponent, moduli[generator])
            central += quotient
            if residue:
                blocks.append((generator, residue))
        return central, tuple(blocks)

    w_form = normal_form(relator_w)
    a_form = normal_form(ak3_relator)
    assert w_form[0] == a_form[0] == -7
    w_x_blocks = [residue for generator, residue in w_form[1] if generator == "x"]
    a_x_blocks = [residue for generator, residue in a_form[1] if generator == "x"]
    assert w_x_blocks == [1, 1, 2, 2, 2, 1, 1]
    assert a_x_blocks == [2, 2, 2, 1, 1, 1, 1]
    assert w_x_blocks == a_x_blocks[5:] + a_x_blocks[:5]

    torus_conjugator = "xxtxxtxxtxtxt"
    assert normal_form(
        inverse(torus_conjugator)
        + ak3_relator
        + torus_conjugator
        + inverse(relator_w)
    ) == (
        0,
        (),
    )
