from __future__ import annotations

from itertools import permutations, product

from mms02_wirtinger_repair_checker import (
    rename_xyz,
    three_generator_descendant,
)


Permutation = tuple[int, ...]
LaurentPolynomial = dict[int, int]


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


def generated_subgroup(generators: tuple[Permutation, ...]) -> set[Permutation]:
    identity = tuple(range(len(generators[0])))
    subgroup = {identity}
    frontier = [identity]
    steps = generators + tuple(inverse(generator) for generator in generators)
    while frontier:
        current = frontier.pop()
        for step in steps:
            child = compose(current, step)
            if child not in subgroup:
                subgroup.add(child)
                frontier.append(child)
    return subgroup


def parity(permutation: Permutation) -> int:
    return sum(
        permutation[left] > permutation[right]
        for left in range(len(permutation))
        for right in range(left + 1, len(permutation))
    ) % 2


def conjugacy_class(element: Permutation, group: set[Permutation]) -> set[Permutation]:
    return {
        compose(compose(conjugator, element), inverse(conjugator))
        for conjugator in group
    }


def fox_abelianized(word: str, generator: str) -> LaurentPolynomial:
    derivative: LaurentPolynomial = {}
    exponent = 0
    for letter in word:
        if letter == generator:
            derivative[exponent] = derivative.get(exponent, 0) + 1
        elif letter == generator.upper():
            derivative[exponent - 1] = derivative.get(exponent - 1, 0) - 1
        exponent += 1 if letter.islower() else -1
    return {power: coefficient for power, coefficient in derivative.items() if coefficient}


def multiply(left: LaurentPolynomial, right: LaurentPolynomial) -> LaurentPolynomial:
    result: LaurentPolynomial = {}
    for left_power, left_coefficient in left.items():
        for right_power, right_coefficient in right.items():
            power = left_power + right_power
            result[power] = result.get(power, 0) + left_coefficient * right_coefficient
    return {power: coefficient for power, coefficient in result.items() if coefficient}


def subtract(left: LaurentPolynomial, right: LaurentPolynomial) -> LaurentPolynomial:
    result = dict(left)
    for power, coefficient in right.items():
        result[power] = result.get(power, 0) - coefficient
    return {power: coefficient for power, coefficient in result.items() if coefficient}


def normalized_coefficients(polynomial: LaurentPolynomial) -> tuple[int, ...]:
    minimum = min(polynomial)
    maximum = max(polynomial)
    coefficients = tuple(polynomial.get(power, 0) for power in range(minimum, maximum + 1))
    return coefficients if coefficients[-1] > 0 else tuple(-value for value in coefficients)


def main() -> None:
    raw_relators, _ = three_generator_descendant(corrected=False)
    relators = tuple(rename_xyz(relator) for relator in raw_relators)
    fox_matrix = tuple(
        tuple(fox_abelianized(relator, generator) for generator in "xyz")
        for relator in relators
    )
    minors = tuple(
        subtract(
            multiply(fox_matrix[0][left], fox_matrix[1][right]),
            multiply(fox_matrix[0][right], fox_matrix[1][left]),
        )
        for left, right in ((0, 1), (0, 2), (1, 2))
    )
    alexander = (1, -3, 5, -3, 1)
    assert all(normalized_coefficients(minor) == alexander for minor in minors)
    print("Alexander_polynomial", "t^4-3t^3+5t^2-3t+1")

    corrected_raw_relators, _ = three_generator_descendant(corrected=True)
    corrected_relators = tuple(rename_xyz(relator) for relator in corrected_raw_relators)
    corrected_fox_matrix = tuple(
        tuple(fox_abelianized(relator, generator) for generator in "xyz")
        for relator in corrected_relators
    )
    corrected_minors = tuple(
        subtract(
            multiply(corrected_fox_matrix[0][left], corrected_fox_matrix[1][right]),
            multiply(corrected_fox_matrix[0][right], corrected_fox_matrix[1][left]),
        )
        for left, right in ((0, 1), (0, 2), (1, 2))
    )
    assert all(normalized_coefficients(minor) == (1,) for minor in corrected_minors)
    print("corrected_Alexander_polynomial", "1")

    for degree in range(2, 6):
        identity = tuple(range(degree))
        symmetric_group = tuple(permutations(range(degree)))
        for x_image, y_image, z_image in product(symmetric_group, repeat=3):
            images = {"x": x_image, "y": y_image, "z": z_image}
            if not all(evaluate(relator, images) == identity for relator in relators):
                continue
            image = generated_subgroup((x_image, y_image, z_image))
            if any(compose(left, right) != compose(right, left) for left in image for right in image):
                alternating_group = {
                    permutation
                    for permutation in symmetric_group
                    if parity(permutation) == 0
                }
                assert image == alternating_group
                kill_word = evaluate("Xyz", images)
                short_word = evaluate("zYX", images)
                assert short_word not in conjugacy_class(kill_word, image)
                assert short_word not in conjugacy_class(inverse(kill_word), image)
                print("PASS: nonabelian quotient of the exact misprinted group")
                print("relators", relators)
                print("degree", degree, "image_group", "A5", "order", len(image))
                print("x", x_image)
                print("y", y_image)
                print("z", z_image)
                print("w=Xyz", kill_word)
                print("w=zYX", short_word)
                print("kill_words_not_conjugate_or_inverse_conjugate")
                return
        print("degree", degree, "no_nonabelian_image")
    raise AssertionError("no nonabelian permutation image through degree five")


if __name__ == "__main__":
    main()
