from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import reduce


Quadratic = tuple[Fraction, Fraction]
Quaternion = tuple[Quadratic, Quadratic, Quadratic, Quadratic]


def quadratic(rational: int | Fraction = 0, root: int | Fraction = 0) -> Quadratic:
    return Fraction(rational), Fraction(root)


def add(left: Quadratic, right: Quadratic) -> Quadratic:
    return left[0] + right[0], left[1] + right[1]


def negative(value: Quadratic) -> Quadratic:
    return -value[0], -value[1]


def multiply_quadratic(left: Quadratic, right: Quadratic) -> Quadratic:
    return (
        left[0] * right[0] + 2 * left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def multiply(left: Quaternion, right: Quaternion) -> Quaternion:
    a, b, c, d = left
    e, f, g, h = right
    return (
        add(
            add(
                add(multiply_quadratic(a, e), negative(multiply_quadratic(b, f))),
                negative(multiply_quadratic(c, g)),
            ),
            negative(multiply_quadratic(d, h)),
        ),
        add(
            add(
                add(multiply_quadratic(a, f), multiply_quadratic(b, e)),
                multiply_quadratic(c, h),
            ),
            negative(multiply_quadratic(d, g)),
        ),
        add(
            add(
                add(multiply_quadratic(a, g), negative(multiply_quadratic(b, h))),
                multiply_quadratic(c, e),
            ),
            multiply_quadratic(d, f),
        ),
        add(
            add(
                add(multiply_quadratic(a, h), multiply_quadratic(b, g)),
                negative(multiply_quadratic(c, f)),
            ),
            multiply_quadratic(d, e),
        ),
    )


def inverse(value: Quaternion) -> Quaternion:
    return value[0], negative(value[1]), negative(value[2]), negative(value[3])


def power(value: Quaternion, exponent: int) -> Quaternion:
    if exponent < 0:
        return power(inverse(value), -exponent)
    return reduce(multiply, (value for _ in range(exponent)), IDENTITY)


def norm(value: Quaternion) -> Quadratic:
    result = quadratic()
    for coordinate in value:
        result = add(result, multiply_quadratic(coordinate, coordinate))
    return result


def rational_scalar_square(value: Quaternion) -> Fraction:
    square = multiply_quadratic(value[0], value[0])
    assert square[1] == 0
    return square[0]


ZERO = quadratic()
IDENTITY: Quaternion = (quadratic(1), ZERO, ZERO, ZERO)
CENTRAL_MINUS_ONE: Quaternion = (quadratic(-1), ZERO, ZERO, ZERO)
C_IMAGE: Quaternion = (ZERO, quadratic(1), ZERO, ZERO)
T_IMAGE: Quaternion = (
    quadratic(root=Fraction(1, 2)),
    quadratic(Fraction(1, 2)),
    quadratic(Fraction(1, 2)),
    ZERO,
)


@dataclass(frozen=True)
class PeriodTwoEllipticCertificate:
    c_square: Quaternion
    central_minus_one: Quaternion
    t_norm: Quadratic
    source_a: Quaternion
    source_b: Quaternion
    source_b_is_projective_identity: bool
    c_scalar_square: Fraction
    source_a_scalar_square: Fraction


def period_two_elliptic_certificate() -> PeriodTwoEllipticCertificate:
    source_a = reduce(
        multiply,
        (
            power(T_IMAGE, -2),
            C_IMAGE,
            power(T_IMAGE, -2),
            C_IMAGE,
            power(T_IMAGE, 2),
            C_IMAGE,
        ),
        IDENTITY,
    )
    source_b = reduce(
        multiply,
        (
            power(T_IMAGE, -3),
            C_IMAGE,
            T_IMAGE,
            C_IMAGE,
            T_IMAGE,
            C_IMAGE,
        ),
        IDENTITY,
    )
    certificate = PeriodTwoEllipticCertificate(
        c_square=multiply(C_IMAGE, C_IMAGE),
        central_minus_one=CENTRAL_MINUS_ONE,
        t_norm=norm(T_IMAGE),
        source_a=source_a,
        source_b=source_b,
        source_b_is_projective_identity=source_b in (IDENTITY, CENTRAL_MINUS_ONE),
        c_scalar_square=rational_scalar_square(C_IMAGE),
        source_a_scalar_square=rational_scalar_square(source_a),
    )
    assert certificate.c_square == CENTRAL_MINUS_ONE
    assert certificate.t_norm == quadratic(1)
    assert certificate.source_b == CENTRAL_MINUS_ONE
    assert certificate.source_a_scalar_square != certificate.c_scalar_square
    return certificate


if __name__ == "__main__":
    print(period_two_elliptic_certificate())
