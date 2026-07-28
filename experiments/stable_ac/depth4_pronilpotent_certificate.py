from __future__ import annotations

from dataclasses import dataclass


SOURCE_A_KERNEL = ((0, -1), (4, -1), (7, -1), (11, -1), (10, 1), (6, 1))
SOURCE_B_KERNEL = ((0, -1), (4, -1), (8, -1), (7, 1), (4, 1))


Word = tuple[int, ...]
Vector = tuple[int, int]
ClassTwoCoordinate = tuple[int, int, int]
LaurentPolynomial = tuple[tuple[int, int], ...]


def laurent(values: dict[int, int]) -> LaurentPolynomial:
    return tuple(sorted((exponent, coefficient) for exponent, coefficient in values.items() if coefficient))


def add_laurent(
    left: LaurentPolynomial,
    right: LaurentPolynomial,
) -> LaurentPolynomial:
    values = dict(left)
    for exponent, coefficient in right:
        values[exponent] = values.get(exponent, 0) + coefficient
    return laurent(values)


def scale_laurent(value: LaurentPolynomial, coefficient: int) -> LaurentPolynomial:
    return laurent({exponent: coefficient * entry for exponent, entry in value})


def shift_laurent(value: LaurentPolynomial, amount: int) -> LaurentPolynomial:
    return tuple((exponent + amount, coefficient) for exponent, coefficient in value)


def kernel_laurent(kernel_word: tuple[tuple[int, int], ...]) -> LaurentPolynomial:
    values: dict[int, int] = {}
    for exponent, coefficient in kernel_word:
        values[exponent] = values.get(exponent, 0) + coefficient
    return laurent(values)


def multiply_by_one_minus_x(value: LaurentPolynomial) -> LaurentPolynomial:
    return add_laurent(value, scale_laurent(shift_laurent(value, 1), -1))


def divide_by_one_minus_x(value: LaurentPolynomial) -> LaurentPolynomial:
    assert sum(coefficient for _, coefficient in value) == 0
    coefficients = dict(value)
    running = 0
    quotient: dict[int, int] = {}
    for exponent in range(min(coefficients) - 1, max(coefficients) + 1):
        running += coefficients.get(exponent, 0)
        if running:
            quotient[exponent] = running
    assert running == 0
    result = laurent(quotient)
    assert multiply_by_one_minus_x(result) == value
    return result


def reduce_word(word: Word) -> Word:
    reduced: list[int] = []
    for letter in word:
        if reduced and reduced[-1] == -letter:
            reduced.pop()
        else:
            reduced.append(letter)
    return tuple(reduced)


def inverse(word: Word) -> Word:
    return tuple(-letter for letter in reversed(word))


def shift(word: Word) -> Word:
    return tuple((2 if abs(letter) == 1 else 1) * (1 if letter > 0 else -1) for letter in word)


def multiply(*words: Word) -> Word:
    return reduce_word(tuple(letter for word in words for letter in word))


def period_two_image(kernel_word: tuple[tuple[int, int], ...]) -> Word:
    return reduce_word(
        tuple(
            (1 if index % 2 == 0 else 2) * sign
            for index, sign in kernel_word
        )
    )


def abelian_vector(word: Word) -> Vector:
    return (
        sum(1 if letter == 1 else -1 if letter == -1 else 0 for letter in word),
        sum(1 if letter == 2 else -1 if letter == -2 else 0 for letter in word),
    )


def class_two_coordinate(word: Word) -> ClassTwoCoordinate:
    p_exponent = 0
    q_exponent = 0
    commutator_exponent = 0
    for letter in word:
        next_p = 1 if letter == 1 else -1 if letter == -1 else 0
        next_q = 1 if letter == 2 else -1 if letter == -2 else 0
        commutator_exponent -= next_p * q_exponent
        p_exponent += next_p
        q_exponent += next_q
    return p_exponent, q_exponent, commutator_exponent


@dataclass(frozen=True)
class PronilpotentBaseCertificate:
    source_a_laurent: LaurentPolynomial
    source_b_laurent: LaurentPolynomial
    h3_laurent: LaurentPolynomial
    laurent_augmentations: tuple[int, int, int, int, int, int]
    laurent_target: LaurentPolynomial
    source_a_word: Word
    source_b_word: Word
    source_a_vector: Vector
    source_b_vector: Vector
    g0_vector: Vector
    r_vector: Vector
    s_vector: Vector
    u_vector: Vector
    z_vector: Vector
    z_class_two_coordinate: ClassTwoCoordinate
    class_two_target_coordinate: ClassTwoCoordinate


def pronilpotent_base_certificate(target_index: int = 0) -> PronilpotentBaseCertificate:
    source_a_laurent = kernel_laurent(SOURCE_A_KERNEL)
    source_b_laurent = kernel_laurent(SOURCE_B_KERNEL)
    rho = add_laurent(
        source_a_laurent,
        scale_laurent(shift_laurent(source_b_laurent, 2), -1),
    )
    eta = add_laurent(
        source_b_laurent,
        scale_laurent(shift_laurent(rho, 1), -1),
    )
    upsilon = add_laurent(rho, scale_laurent(shift_laurent(eta, 1), -1))
    f0 = add_laurent(
        scale_laurent(shift_laurent(upsilon, -1), -1),
        shift_laurent(eta, -1),
    )
    target_laurent = ((target_index, 1),)
    numerator = add_laurent(target_laurent, scale_laurent(f0, -1))
    h3_laurent = divide_by_one_minus_x(numerator)
    laurent_target = add_laurent(f0, multiply_by_one_minus_x(h3_laurent))

    source_a = period_two_image(SOURCE_A_KERNEL)
    source_b = period_two_image(SOURCE_B_KERNEL)
    g0 = (-1, 2)

    r = multiply(source_a, g0, inverse(source_b), shift(inverse(g0)))
    s = multiply(source_b, shift(inverse(r)))
    u = multiply(r, shift(inverse(s)))
    z = multiply(shift(inverse(u)), shift(s))
    target_conjugator = (-2, -2, -2, -2)
    class_two_target = multiply(
        target_conjugator,
        (1,),
        inverse(target_conjugator),
    )

    certificate = PronilpotentBaseCertificate(
        source_a_laurent=source_a_laurent,
        source_b_laurent=source_b_laurent,
        h3_laurent=h3_laurent,
        laurent_augmentations=tuple(
            sum(coefficient for _, coefficient in value)
            for value in (source_a_laurent, source_b_laurent, rho, eta, upsilon, f0)
        ),
        laurent_target=laurent_target,
        source_a_word=source_a,
        source_b_word=source_b,
        source_a_vector=abelian_vector(source_a),
        source_b_vector=abelian_vector(source_b),
        g0_vector=abelian_vector(g0),
        r_vector=abelian_vector(r),
        s_vector=abelian_vector(s),
        u_vector=abelian_vector(u),
        z_vector=abelian_vector(z),
        z_class_two_coordinate=class_two_coordinate(z),
        class_two_target_coordinate=class_two_coordinate(class_two_target),
    )
    assert certificate.laurent_target == target_laurent
    assert certificate.z_vector == (1, 0)
    return certificate


if __name__ == "__main__":
    print(pronilpotent_base_certificate())
