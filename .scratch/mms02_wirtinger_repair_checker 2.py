from __future__ import annotations

from dataclasses import dataclass


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


def token(index: int, positive: bool = True) -> str:
    return chr(ord("a") + index - 1) if positive else chr(ord("A") + index - 1)


def substitute(word: str, generator: str, image: str) -> str:
    positive = image
    negative = inverse(image)
    return free_reduce(
        "".join(
            positive if letter == generator else negative if letter == generator.upper() else letter
            for letter in word
        )
    )


def equation(index: int, rhs: str) -> str:
    return free_reduce(token(index) + inverse(rhs))


def solve_unique(relator: str, generator: str) -> str:
    positions = [i for i, letter in enumerate(relator) if letter.lower() == generator]
    assert len(positions) == 1, (generator, relator, positions)
    position = positions[0]
    prefix = relator[:position]
    letter = relator[position]
    suffix = relator[position + 1 :]
    if letter == generator:
        image = inverse(prefix) + inverse(suffix)
    else:
        image = suffix + prefix
    return free_reduce(image)


def cyclic_reduce(word: str) -> str:
    word = free_reduce(word)
    while len(word) >= 2 and word[0] == word[-1].swapcase():
        word = free_reduce(word[1:-1])
    return word


def cyclic_class(word: str) -> str:
    word = cyclic_reduce(word)
    if not word:
        return ""
    candidates: list[str] = []
    for oriented in (word, inverse(word)):
        candidates.extend(oriented[index:] + oriented[:index] for index in range(len(oriented)))
    return min(candidates)


@dataclass(frozen=True)
class Elimination:
    generator: str
    relator_index: int
    image: str
    before_count: int
    after_count: int


def eliminate(relators: list[str], generator: str) -> tuple[list[str], Elimination]:
    candidates = [
        (len(relator), index, relator)
        for index, relator in enumerate(relators)
        if sum(letter.lower() == generator for letter in relator) == 1
    ]
    assert candidates, (generator, relators)
    _, index, defining = min(candidates)
    image = solve_unique(defining, generator)
    remaining = [
        cyclic_reduce(substitute(relator, generator, image))
        for other_index, relator in enumerate(relators)
        if other_index != index
    ]
    assert all(generator not in relator.lower() for relator in remaining)
    return remaining, Elimination(generator, index, image, len(relators), len(remaining))


def eliminate_equality(
    relators: list[str], generator: str, image: str
) -> tuple[list[str], Elimination]:
    substituted = [cyclic_reduce(substitute(relator, generator, image)) for relator in relators]
    classes: dict[str, list[int]] = {}
    for index, relator in enumerate(substituted):
        classes.setdefault(cyclic_class(relator), []).append(index)
    if "" in classes:
        removed = classes[""][-1]
    else:
        duplicate = next(indices for indices in classes.values() if len(indices) >= 2)
        removed = duplicate[-1]
    remaining = [relator for index, relator in enumerate(substituted) if index != removed]
    assert all(generator not in relator.lower() for relator in remaining)
    return remaining, Elimination(generator, removed, image, len(relators), len(remaining))


def wirtinger_relators(*, corrected: bool) -> list[str]:
    def x(index: int) -> str:
        return token(index)

    def X(index: int) -> str:
        return token(index, False)

    rhs = [
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
        (x(4) + x(12) + X(4)) if corrected else (x(5) + x(12) + X(5)),
        x(1) + x(13) + X(1),
    ]
    return [equation(index, word) for index, word in enumerate(rhs, start=1)]


def three_generator_descendant(*, corrected: bool = True) -> tuple[list[str], list[Elimination]]:
    relators = wirtinger_relators(corrected=corrected)
    del relators[11]
    history: list[Elimination] = []
    # MMS02 p.10 leaves x5, x7, x12 after deleting r12.  Unique-occurrence
    # Tietze elimination is equivalent to its substitution-and-removal steps.
    for index, image_index in ((14, 2), (11, 9), (9, 8)):
        relators, record = eliminate_equality(relators, token(index), token(image_index))
        history.append(record)
    for index in (13, 8, 4, 3, 6, 10, 2, 1):
        relators, record = eliminate(relators, token(index))
        history.append(record)
    assert len(relators) == 2
    assert all(set(word.lower()) <= {token(5), token(7), token(12)} for word in relators)
    return relators, history


def rename_xyz(word: str) -> str:
    mapping = {
        token(5): "x",
        token(5, False): "X",
        token(7): "y",
        token(7, False): "Y",
        token(12): "z",
        token(12, False): "Z",
    }
    return "".join(mapping[letter] for letter in word)


def two_generator_descendant(*, corrected: bool = True) -> tuple[str, str]:
    relators, _ = three_generator_descendant(corrected=corrected)
    # The extra relator w=x^-1 y z solves z=y^-1 x.
    return tuple(
        substitute(rename_xyz(relator), "z", "Yx") for relator in relators
    )


def exchange_quotient() -> tuple[list[str], tuple[str, str], list[Elimination]]:
    corrected = wirtinger_relators(corrected=True)
    probes = (
        corrected[12],
        wirtinger_relators(corrected=False)[12],
    )
    relators = [
        relator for index, relator in enumerate(corrected) if index not in (11, 12)
    ]
    relators.append(token(5, False) + token(7) + token(12))
    alive = {token(index) for index in range(1, 15)}
    history: list[Elimination] = []
    while True:
        options: list[tuple[int, str]] = []
        for generator in sorted(alive, reverse=True):
            candidates = [
                len(relator)
                for relator in relators
                if sum(letter.lower() == generator for letter in relator) == 1
            ]
            if candidates:
                options.append((min(candidates), generator))
        if not options:
            break
        _, generator = min(options)
        relators, record = eliminate(relators, generator)
        probes = tuple(
            cyclic_reduce(substitute(probe, generator, record.image)) for probe in probes
        )
        alive.remove(generator)
        history.append(record)
    assert alive == {token(11), token(12), token(14)}
    assert relators == [
        "lnkNKNknknKNLnkNKNknknKNllnkNKNKnknKNLnkNKNknKN",
        "nkNKNknknKNLLnkNKNKnknKNlnkNKNKnknKNLLnkNKNknknKNll",
    ]
    assert probes == (
        "nkNKnknKNLnkNKNknknKNLnkNKNKnknKNl",
        "knKNLnkNKNKnkn",
    )
    return relators, probes, history


def main() -> None:
    relators, history = three_generator_descendant()
    print("corrected_three_generator")
    for relator in relators:
        print(rename_xyz(relator), len(relator))
    print("eliminations")
    for record in history:
        print(record)
    print("corrected_two_generator_w=Xyz")
    pair = two_generator_descendant()
    for relator in pair:
        print(relator, len(relator))
    print("total", sum(map(len, pair)))
    printed_pair = ("XYxYXyxYYxyXy", "YXyyXYxyxYYx")
    misprinted_pair = two_generator_descendant(corrected=False)
    assert sorted(map(cyclic_class, misprinted_pair)) == sorted(map(cyclic_class, printed_pair))
    print("misprint_replay_matches_mms02_P")
    for relator in misprinted_pair:
        print(relator, len(relator))
    quotient, probes, _ = exchange_quotient()
    print("fixed_relator_exchange_quotient")
    for relator in quotient:
        print(relator, len(relator))
    print("corrected_probe", probes[0], len(probes[0]))
    print("misprinted_probe", probes[1], len(probes[1]))


if __name__ == "__main__":
    main()
