from dataclasses import dataclass
from fractions import Fraction
from math import isqrt


Q = tuple[Fraction, Fraction, Fraction, Fraction]
Signature = tuple[int, int, int, int, int]


@dataclass(frozen=True)
class MetricCertificate:
    signature: Signature
    target_vector: tuple[int, int]
    parameters: tuple[Fraction, Fraction, Fraction, Fraction]
    source_a_scalar: Fraction
    source_b_scalar: Fraction
    target_scalar: Fraction
    source_a_tangent_square: Fraction
    source_b_tangent_square: Fraction
    source_angle_upper_bound: Fraction
    target_angle_lower_bound: Fraction
    margin: Fraction


REPRESENTATIONS = {
    "almost_parallel": (
        Fraction(8, 15),
        Fraction(5, 13),
        Fraction(312, 313),
        Fraction(25, 313),
    ),
    "negative_axis_a": (
        Fraction(1, 2),
        Fraction(7, 15),
        Fraction(-20, 101),
        Fraction(99, 101),
    ),
    "negative_axis_b": (
        Fraction(15, 26),
        Fraction(12, 29),
        Fraction(-28, 197),
        Fraction(195, 197),
    ),
}


REPRESENTATION_BY_SIGNATURE: dict[Signature, str] = {
    (7, 3, 4, -3, -4): "almost_parallel",
    (7, 3, 4, -3, -2): "negative_axis_a",
    (7, 3, 4, -1, 0): "negative_axis_b",
    (7, 3, 4, -1, 2): "negative_axis_a",
    (7, 4, 3, -4, -3): "almost_parallel",
    (7, 4, 3, -4, 3): "negative_axis_b",
    (7, 4, 3, -2, -1): "negative_axis_b",
    (7, 4, 3, -2, 1): "negative_axis_b",
    (7, 4, 3, -2, 3): "negative_axis_b",
    (7, 4, 3, 0, -1): "negative_axis_b",
    (8, 3, 5, -3, -5): "almost_parallel",
    (8, 3, 5, -3, -1): "negative_axis_a",
    (8, 3, 5, -1, -3): "negative_axis_a",
    (8, 3, 5, -1, 1): "negative_axis_a",
    (8, 5, 3, -5, -3): "almost_parallel",
    (8, 5, 3, -5, 3): "almost_parallel",
    (8, 5, 3, -3, -1): "negative_axis_b",
    (8, 5, 3, -1, -3): "negative_axis_b",
    (8, 5, 3, -1, 1): "negative_axis_b",
}


def circle_parameter(tangent_half_angle: Fraction) -> tuple[Fraction, Fraction]:
    denominator = 1 + tangent_half_angle * tangent_half_angle
    return (
        (1 - tangent_half_angle * tangent_half_angle) / denominator,
        2 * tangent_half_angle / denominator,
    )


def quaternion_multiply(left: Q, right: Q) -> Q:
    a, b, c, d = left
    e, f, g, h = right
    return (
        a * e - b * f - c * g - d * h,
        a * f + b * e + c * h - d * g,
        a * g - b * h + c * e + d * f,
        a * h + b * g - c * f + d * e,
    )


def quaternion_inverse(value: Q) -> Q:
    return (value[0], -value[1], -value[2], -value[3])


def evaluate(word: str, x: Q, y: Q) -> Q:
    images = {"x": x, "X": quaternion_inverse(x), "y": y, "Y": quaternion_inverse(y)}
    value = (Fraction(1), Fraction(0), Fraction(0), Fraction(0))
    for letter in word:
        value = quaternion_multiply(value, images[letter])
    return value


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


def quaternion_pair(
    parameters: tuple[Fraction, Fraction, Fraction, Fraction],
) -> tuple[Q, Q]:
    x_parameter, y_parameter, axis_dot_product, axis_x = parameters
    assert axis_dot_product * axis_dot_product + axis_x * axis_x == 1
    x_scalar, x_vector = circle_parameter(x_parameter)
    y_scalar, y_vector = circle_parameter(y_parameter)
    x = (x_scalar, Fraction(0), Fraction(0), x_vector)
    y = (
        y_scalar,
        y_vector * axis_x,
        Fraction(0),
        y_vector * axis_dot_product,
    )
    return x, y


def rational_sqrt_upper(value: Fraction, scale: int = 10**15) -> Fraction:
    scaled_square = value.numerator * scale * scale // value.denominator
    return Fraction(isqrt(scaled_square) + 1, scale)


def source_angle_upper(scalar: Fraction) -> tuple[Fraction, Fraction]:
    tangent_square = (1 - scalar * scalar) / (scalar * scalar)
    assert 0 <= tangent_square <= 1
    tangent_upper = rational_sqrt_upper(tangent_square)
    alternating_upper_factor = 1 - tangent_square / 3 + tangent_square**2 / 5
    return tangent_square, tangent_upper * alternating_upper_factor


def target_angle_lower(scalar: Fraction) -> Fraction:
    if scalar < 0:
        return Fraction(333, 212) - scalar
    tangent_square = scalar * scalar / (1 - scalar * scalar)
    return Fraction(333, 212) - rational_sqrt_upper(tangent_square)


def metric_certificates() -> tuple[MetricCertificate, ...]:
    certificates = []
    for signature, representation in REPRESENTATION_BY_SIGNATURE.items():
        parameters = REPRESENTATIONS[representation]
        _, source_a_count, source_b_count, source_a_coefficient, source_b_coefficient = (
            signature
        )
        target_vector = (
            3 * source_a_coefficient + source_b_coefficient,
            -4 * source_a_coefficient - source_b_coefficient,
        )
        x, y = quaternion_pair(parameters)
        source_a_scalar = evaluate("xxxYYYY", x, y)[0]
        source_b_scalar = evaluate("xyxYXY", x, y)[0]
        target_scalar = evaluate(christoffel(*target_vector), x, y)[0]
        assert source_a_scalar > 0
        assert source_b_scalar > 0
        assert -1 < target_scalar < 1

        source_a_tangent_square, source_a_upper = source_angle_upper(source_a_scalar)
        source_b_tangent_square, source_b_upper = source_angle_upper(source_b_scalar)
        source_upper = source_a_count * source_a_upper + source_b_count * source_b_upper
        target_lower = target_angle_lower(target_scalar)
        certificates.append(
            MetricCertificate(
                signature=signature,
                target_vector=target_vector,
                parameters=parameters,
                source_a_scalar=source_a_scalar,
                source_b_scalar=source_b_scalar,
                target_scalar=target_scalar,
                source_a_tangent_square=source_a_tangent_square,
                source_b_tangent_square=source_b_tangent_square,
                source_angle_upper_bound=source_upper,
                target_angle_lower_bound=target_lower,
                margin=target_lower - source_upper,
            )
        )
    return tuple(certificates)


if __name__ == "__main__":
    for certificate in metric_certificates():
        print(certificate.signature, certificate.margin)
