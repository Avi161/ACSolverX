from __future__ import annotations

from itertools import permutations

from mms02_wirtinger_repair_checker import exchange_quotient


Permutation = tuple[int, ...]


def compose(left: Permutation, right: Permutation) -> Permutation:
    return tuple(left[right[index]] for index in range(len(left)))


def inverse(permutation: Permutation) -> Permutation:
    result = [0] * len(permutation)
    for index, image in enumerate(permutation):
        result[image] = index
    return tuple(result)


def evaluate(word: str, images: dict[str, Permutation]) -> Permutation:
    result = tuple(range(len(next(iter(images.values())))))
    for letter in word:
        image = images[letter.lower()]
        result = compose(result, image if letter.islower() else inverse(image))
    return result


def cycle_type(permutation: Permutation) -> tuple[int, ...]:
    seen: set[int] = set()
    lengths: list[int] = []
    for start in range(len(permutation)):
        if start in seen:
            continue
        current = start
        length = 0
        while current not in seen:
            seen.add(current)
            current = permutation[current]
            length += 1
        if length > 1:
            lengths.append(length)
    return tuple(sorted(lengths, reverse=True))


def parity(permutation: Permutation) -> int:
    inversions = sum(
        permutation[left] > permutation[right]
        for left in range(len(permutation))
        for right in range(left + 1, len(permutation))
    )
    return inversions % 2


def generated_subgroup(generators: tuple[Permutation, ...]) -> set[Permutation]:
    identity = tuple(range(len(generators[0])))
    subgroup = {identity}
    frontier = [identity]
    steps = generators + tuple(inverse(generator) for generator in generators)
    while frontier:
        current = frontier.pop()
        for step in steps:
            candidate = compose(current, step)
            if candidate not in subgroup:
                subgroup.add(candidate)
                frontier.append(candidate)
    return subgroup


def main() -> None:
    relators, probes, _ = exchange_quotient()
    k_image = (1, 2, 3, 4, 0)
    n_image = (2, 0, 4, 1, 3)
    images = {"k": k_image, "n": n_image, "l": inverse(n_image)}
    identity = tuple(range(5))

    assert all(evaluate(relator, images) == identity for relator in relators)
    corrected_image, misprinted_image = (
        evaluate(probe, images) for probe in probes
    )
    assert cycle_type(corrected_image) == (3,)
    assert cycle_type(misprinted_image) == (5,)

    subgroup = generated_subgroup((k_image, n_image))
    alternating_group = {
        permutation for permutation in permutations(range(5)) if parity(permutation) == 0
    }
    assert subgroup == alternating_group

    print("PASS: exact exchange-quotient A5 certificate")
    print("common_relators", len(relators), "both_identity")
    print("corrected_probe", probes[0], cycle_type(corrected_image))
    print("misprinted_probe", probes[1], cycle_type(misprinted_image))
    print("image_group", "A5", "order", len(subgroup))


if __name__ == "__main__":
    main()
