from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import isqrt

Signature = tuple[int, int, int, int, int]


def christoffel(x_exponent: int, y_exponent: int) -> str:
    x_letter = "x" if x_exponent >= 0 else "X"
    y_letter = "y" if y_exponent >= 0 else "Y"
    x_count = abs(x_exponent)
    y_count = abs(y_exponent)
    length = x_count + y_count
    return "".join(
        x_letter
        if ((index + 1) * x_count) // length > (index * x_count) // length
        else y_letter
        for index in range(length)
    )


@dataclass(frozen=True)
class RationalInterval:
    lower: Fraction
    upper: Fraction

    def __post_init__(self) -> None:
        assert self.lower <= self.upper

    @classmethod
    def exact(cls, value: int | Fraction) -> "RationalInterval":
        rational = Fraction(value)
        return cls(rational, rational)

    def __neg__(self) -> "RationalInterval":
        return RationalInterval(-self.upper, -self.lower)

    def __add__(self, other: object) -> "RationalInterval":
        right = as_interval(other)
        return RationalInterval(self.lower + right.lower, self.upper + right.upper)

    def __radd__(self, other: object) -> "RationalInterval":
        return self + other

    def __sub__(self, other: object) -> "RationalInterval":
        return self + (-as_interval(other))

    def __rsub__(self, other: object) -> "RationalInterval":
        return as_interval(other) - self

    def __mul__(self, other: object) -> "RationalInterval":
        right = as_interval(other)
        products = (
            self.lower * right.lower,
            self.lower * right.upper,
            self.upper * right.lower,
            self.upper * right.upper,
        )
        return RationalInterval(min(products), max(products))

    def __rmul__(self, other: object) -> "RationalInterval":
        return self * other


def as_interval(value: object) -> RationalInterval:
    if isinstance(value, RationalInterval):
        return value
    if isinstance(value, (int, Fraction)):
        return RationalInterval.exact(value)
    return NotImplemented


def sqrt_interval(value: Fraction, scale: int = 10**30) -> RationalInterval:
    scaled_square = value.numerator * scale * scale // value.denominator
    root_floor = isqrt(scaled_square)
    lower = Fraction(root_floor, scale)
    if lower * lower == value:
        return RationalInterval.exact(lower)
    return RationalInterval(lower, Fraction(root_floor + 1, scale))


IntervalQuaternion = tuple[
    RationalInterval,
    RationalInterval,
    RationalInterval,
    RationalInterval,
]


def quaternion_multiply(
    left: IntervalQuaternion,
    right: IntervalQuaternion,
) -> IntervalQuaternion:
    a, b, c, d = left
    e, f, g, h = right
    return (
        a * e - b * f - c * g - d * h,
        a * f + b * e + c * h - d * g,
        a * g - b * h + c * e + d * f,
        a * h + b * g - c * f + d * e,
    )


def quaternion_inverse(value: IntervalQuaternion) -> IntervalQuaternion:
    return (value[0], -value[1], -value[2], -value[3])


def evaluate(word: str, x: IntervalQuaternion, y: IntervalQuaternion) -> IntervalQuaternion:
    images = {"x": x, "X": quaternion_inverse(x), "y": y, "Y": quaternion_inverse(y)}
    zero = RationalInterval.exact(0)
    value = (RationalInterval.exact(1), zero, zero, zero)
    for letter in word:
        value = quaternion_multiply(value, images[letter])
    return value


def braid_killing_representation() -> tuple[IntervalQuaternion, IntervalQuaternion]:
    scalar = sqrt_interval(Fraction(37, 50))
    vector_length = sqrt_interval(Fraction(13, 50))
    zero = RationalInterval.exact(0)
    x = (scalar, zero, zero, vector_length)
    y = (
        scalar,
        Fraction(5, 13) * vector_length,
        zero,
        Fraction(12, 13) * vector_length,
    )
    assert (Fraction(37, 50) - Fraction(1, 2)) / Fraction(13, 50) == Fraction(12, 13)
    return x, y


def power_killing_representation(
    axis_dot_product: Fraction,
) -> tuple[IntervalQuaternion, IntervalQuaternion]:
    zero = RationalInterval.exact(0)
    x = (
        RationalInterval.exact(Fraction(1, 2)),
        zero,
        zero,
        Fraction(1, 2) * sqrt_interval(Fraction(3)),
    )
    root_half = sqrt_interval(Fraction(1, 2))
    if axis_dot_product == Fraction(-1, 3):
        y_axis_x = RationalInterval.exact(Fraction(2, 3))
    elif axis_dot_product == Fraction(4, 5):
        y_axis_x = Fraction(3, 5) * root_half
    else:
        raise ValueError(axis_dot_product)
    y = (root_half, y_axis_x, zero, axis_dot_product * root_half)
    return x, y


REPRESENTATIONS = {
    "kill_b_37_50": braid_killing_representation(),
    "kill_a_minus_1_3": power_killing_representation(Fraction(-1, 3)),
    "kill_a_4_5": power_killing_representation(Fraction(4, 5)),
}


REPRESENTATION_BY_SIGNATURE: dict[Signature, str] = {
    (7, 3, 4, -3, 2): "kill_b_37_50",
    (7, 3, 4, -3, 4): "kill_b_37_50",
    (7, 4, 3, -2, -3): "kill_a_minus_1_3",
    (8, 3, 5, -3, 1): "kill_b_37_50",
    (8, 5, 3, -3, 1): "kill_a_4_5",
}


@dataclass(frozen=True)
class ThreeClassCertificate:
    signature: Signature
    target_vector: tuple[int, int]
    representation: str
    source_scalar: RationalInterval
    target_scalar: RationalInterval
    cubic_scalar: RationalInterval
    margin: RationalInterval


def three_class_certificates() -> tuple[ThreeClassCertificate, ...]:
    certificates = []
    for signature, representation in REPRESENTATION_BY_SIGNATURE.items():
        _, source_a_count, source_b_count, source_a_coefficient, source_b_coefficient = (
            signature
        )
        target_vector = (
            3 * source_a_coefficient + source_b_coefficient,
            -4 * source_a_coefficient - source_b_coefficient,
        )
        x, y = REPRESENTATIONS[representation]
        if source_a_count < source_b_count:
            source_word = "xxxYYYY"
        else:
            source_word = "xyxYXY"
        source_scalar = evaluate(source_word, x, y)[0]
        target_scalar = evaluate(christoffel(*target_vector), x, y)[0]
        cubic_scalar = 4 * source_scalar * source_scalar * source_scalar - 3 * source_scalar
        margin = cubic_scalar - target_scalar
        certificates.append(
            ThreeClassCertificate(
                signature=signature,
                target_vector=target_vector,
                representation=representation,
                source_scalar=source_scalar,
                target_scalar=target_scalar,
                cubic_scalar=cubic_scalar,
                margin=margin,
            )
        )
    return tuple(certificates)


if __name__ == "__main__":
    for certificate in three_class_certificates():
        print(certificate.signature, certificate.margin.lower)
