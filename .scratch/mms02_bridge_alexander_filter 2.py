from __future__ import annotations

from typing import Any

from mms02_wirtinger_repair_checker import (
    free_reduce,
    inverse,
    rename_xyz,
    three_generator_descendant,
)

LaurentPolynomial = dict[int, int]
DELTA = (1, -3, 5, -3, 1)


def add(left: LaurentPolynomial, right: LaurentPolynomial) -> LaurentPolynomial:
    result = dict(left)
    for power, coefficient in right.items():
        result[power] = result.get(power, 0) + coefficient
    return {power: coefficient for power, coefficient in result.items() if coefficient}


def multiply(left: LaurentPolynomial, right: LaurentPolynomial) -> LaurentPolynomial:
    result: LaurentPolynomial = {}
    for left_power, left_coefficient in left.items():
        for right_power, right_coefficient in right.items():
            power = left_power + right_power
            result[power] = result.get(power, 0) + left_coefficient * right_coefficient
    return {power: coefficient for power, coefficient in result.items() if coefficient}


def normalized_coefficients(polynomial: LaurentPolynomial) -> tuple[int, ...]:
    if not polynomial:
        return ()
    minimum = min(polynomial)
    maximum = max(polynomial)
    return tuple(polynomial.get(power, 0) for power in range(minimum, maximum + 1))


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


def exponent_sum(word: str) -> int:
    return sum(1 if letter.islower() else -1 for letter in word)


def apply_images(word: str, images: tuple[str, str, str]) -> str:
    positive = dict(zip("xyz", images))
    negative = {letter.upper(): inverse(image) for letter, image in positive.items()}
    mapping = positive | negative
    return free_reduce("".join(mapping[letter] for letter in word))


def module_coordinate(word: str, z_coordinate: LaurentPolynomial) -> LaurentPolynomial:
    return add(
        fox_abelianized(word, "y"),
        multiply(fox_abelianized(word, "z"), z_coordinate),
    )


def verify() -> dict[str, Any]:
    raw_relators, _ = three_generator_descendant(corrected=False)
    relators = tuple(rename_xyz(relator) for relator in raw_relators)
    assert relators == ("xzYXyxZXYxyZ", "XyxZXYXyxzXYxy")
    relator_a, relator_b = relators

    dy_a = fox_abelianized(relator_a, "y")
    dz_a = fox_abelianized(relator_a, "z")
    assert dz_a == {0: -1}

    z_coordinate = dy_a
    assert module_coordinate(relator_a, z_coordinate) == {}
    annihilator = module_coordinate(relator_b, z_coordinate)
    assert normalized_coefficients(annihilator) == DELTA

    cyclic_images = ("xY", "Y", "zy")
    cyclic_exponents = tuple(exponent_sum(image) for image in cyclic_images)
    assert cyclic_exponents == (0, -1, 2)

    module_images = ("y", "x", "zyX")
    assert tuple(exponent_sum(image) for image in module_images) == (1, 1, 1)
    psi_a = apply_images(relator_a, module_images)
    psi_b = apply_images(relator_b, module_images)
    assert exponent_sum(psi_a) == exponent_sum(psi_b) == 0

    psi_a_class = module_coordinate(psi_a, z_coordinate)
    psi_b_class = module_coordinate(psi_b, z_coordinate)
    psi_a_remainder = normalized_coefficients(psi_a_class)
    psi_b_remainder = normalized_coefficients(psi_b_class)
    assert psi_a_remainder == (2, -3, 1)
    assert psi_b_remainder == (-1, 1, 0, -1)
    assert len(psi_a_remainder) < len(DELTA)
    assert len(psi_b_remainder) < len(DELTA)

    return {
        "relators": relators,
        "module_generator_relation": z_coordinate,
        "alexander_polynomial": DELTA,
        "cyclic_failure": {
            "images": cyclic_images,
            "exponent_sums": cyclic_exponents,
        },
        "module_failure": {
            "images": module_images,
            "psi_A": psi_a,
            "psi_B": psi_b,
            "psi_A_remainder": psi_a_remainder,
            "psi_B_remainder": psi_b_remainder,
        },
    }


def main() -> None:
    result = verify()
    print("PASS: exact MMS02 bridge Alexander-module filter")
    print("relators", result["relators"])
    print("z_module_coordinate", result["module_generator_relation"])
    print("Delta", result["alexander_polynomial"])
    print("cyclic_failure", result["cyclic_failure"])
    print("module_failure", result["module_failure"])


if __name__ == "__main__":
    main()
