"""Replay the universal A--D quotient and its evaluated Fox row.

The quotient uses only ``qx^3q^-1 = t^4`` and ``zxz^-1 = t``.  The
four-state calculation is formal: it checks that the displayed module
relations annihilate the evaluated row for an arbitrary element ``g``.
"""

from __future__ import annotations

from fractions import Fraction
from math import gcd


GroupRingElement = dict[str, int]

A = "qxxxQTTTT"
D = "TzxZ"

_INVERSES = str.maketrans("xtzqyXTZQY", "XTZQYxtzqy")
_GENERATORS = frozenset("xtzqyXTZQY")


def inverse_word(word: str) -> str:
    if set(word) - _GENERATORS:
        raise ValueError(f"word has generators outside x, t, z, q, y: {word!r}")
    return word.translate(_INVERSES)[::-1]


def free_reduce(word: str) -> str:
    if set(word) - _GENERATORS:
        raise ValueError(f"word has generators outside x, t, z, q, y: {word!r}")

    reduced: list[str] = []
    for letter in word:
        if reduced and reduced[-1] == letter.translate(_INVERSES):
            reduced.pop()
        else:
            reduced.append(letter)
    return "".join(reduced)


def substitute_word(word: str, forward: dict[str, str]) -> str:
    """Apply a substitution to a free word, deriving inverse images exactly."""
    if set(forward) != {"x", "t", "z", "q"}:
        raise ValueError("forward substitution must define x, t, z, and q")
    return free_reduce(
        "".join(
            forward[letter] if letter.islower() else inverse_word(forward[letter.lower()])
            for letter in word
        )
    )


def _add_term(element: GroupRingElement, word: str, coefficient: int) -> None:
    if not coefficient:
        return
    element[word] = element.get(word, 0) + coefficient
    if not element[word]:
        del element[word]


def _fox_derivative(word: str, generator: str) -> GroupRingElement:
    """Compute the left Fox derivative of a literal free word."""
    derivative: GroupRingElement = {}
    prefix = ""
    for letter in word:
        if letter == generator:
            _add_term(derivative, prefix, 1)
        elif letter == generator.upper():
            _add_term(derivative, free_reduce(prefix + letter), -1)
        prefix = free_reduce(prefix + letter)
    return derivative


def _impose_quotient_equalities(word: str) -> str:
    """Orient precisely the two quotient equalities used in this replay."""
    previous = None
    reduced = free_reduce(word)
    while reduced != previous:
        previous = reduced
        rewritten: list[str] = []
        index = 0
        while index < len(reduced):
            letter = reduced[index]
            if letter in "qz":
                middle = "x" if index + 1 < len(reduced) and reduced[index + 1] == "x" else "X"
                end = "Q" if letter == "q" else "Z"
                cursor = index + 1
                while cursor < len(reduced) and reduced[cursor] == middle:
                    cursor += 1
                power = cursor - index - 1
                divisor = 3 if letter == "q" else 1
                if power and power % divisor == 0 and cursor < len(reduced) and reduced[cursor] == end:
                    t_letter = "t" if middle == "x" else "T"
                    rewritten.append(t_letter * (4 * power // divisor if letter == "q" else power))
                    index = cursor + 1
                    continue
            rewritten.append(letter)
            index += 1
        reduced = "".join(rewritten)
        reduced = free_reduce(reduced)
    return reduced


def _evaluate(element: GroupRingElement) -> GroupRingElement:
    evaluated: GroupRingElement = {}
    for word, coefficient in element.items():
        _add_term(evaluated, _impose_quotient_equalities(word), coefficient)
    return evaluated


def evaluated_ad_rows() -> tuple[tuple[GroupRingElement, ...], tuple[GroupRingElement, ...]]:
    """Return the literal A and D Fox rows after the two quotient relations."""
    return (
        tuple(_evaluate(_fox_derivative(A, generator)) for generator in "xtzq"),
        tuple(_evaluate(_fox_derivative(D, generator)) for generator in "xtzq"),
    )


def _add_elements(*elements: GroupRingElement) -> GroupRingElement:
    result: GroupRingElement = {}
    for element in elements:
        for word, coefficient in element.items():
            _add_term(result, word, coefficient)
    return result


def _scale_element(element: GroupRingElement, coefficient: int) -> GroupRingElement:
    return {
        word: coefficient * value
        for word, value in element.items()
        if coefficient * value
    }


def _prefix_element(prefix: str, element: GroupRingElement) -> GroupRingElement:
    prefixed: GroupRingElement = {}
    for word, coefficient in element.items():
        _add_term(
            prefixed,
            _impose_quotient_equalities(prefix + word),
            coefficient,
        )
    return prefixed


def evaluated_relative_row(sigma: int, g: str) -> tuple[GroupRingElement, ...]:
    """Build ``A_row + sigma*g*D_row`` in the evaluated quotient group ring."""
    if sigma not in (1, -1):
        raise ValueError("sigma must be 1 or -1")
    evaluated_g = _impose_quotient_equalities(g)
    a_row, d_row = evaluated_ad_rows()
    return tuple(
        _add_elements(
            a_coordinate,
            _scale_element(_prefix_element(evaluated_g, d_coordinate), sigma),
        )
        for a_coordinate, d_coordinate in zip(a_row, d_row, strict=True)
    )


StateVector = dict[tuple[int, str], int]
SymbolicCoordinate = dict[tuple[bool, str], int]


def _symbolic_relative_row(sigma: int) -> tuple[SymbolicCoordinate, ...]:
    """Keep the two summands of ``A_row + sigma*g*D_row`` distinguishable."""
    a_row, d_row = evaluated_ad_rows()
    row: list[SymbolicCoordinate] = []
    for a_coordinate, d_coordinate in zip(a_row, d_row, strict=True):
        coordinate: SymbolicCoordinate = {}
        for word, coefficient in a_coordinate.items():
            coordinate[(False, word)] = coefficient
        for word, coefficient in d_coordinate.items():
            coordinate[(True, word)] = sigma * coefficient
        row.append(coordinate)
    return tuple(row)


def _project_symbolic_coordinate(
    coordinate: SymbolicCoordinate,
    g: str,
) -> GroupRingElement:
    projected: GroupRingElement = {}
    for (has_g_prefix, word), coefficient in coordinate.items():
        _add_term(
            projected,
            _impose_quotient_equalities((g if has_g_prefix else "") + word),
            coefficient,
        )
    return projected


def _symbolic_part(
    coordinate: SymbolicCoordinate,
    has_g_prefix: bool,
) -> GroupRingElement:
    return {
        word: coefficient
        for (is_prefixed, word), coefficient in coordinate.items()
        if is_prefixed == has_g_prefix
    }


def _state_add(*vectors: StateVector) -> StateVector:
    result: StateVector = {}
    for vector in vectors:
        for state, coefficient in vector.items():
            result[state] = result.get(state, 0) + coefficient
            if not result[state]:
                del result[state]
    return result


def _state_scale(vector: StateVector, coefficient: int) -> StateVector:
    return {
        state: coefficient * value
        for state, value in vector.items()
        if coefficient * value
    }


def _state_right_word(vector: StateVector, word: str) -> StateVector:
    """Apply a t/z word to a four-state vector from left to right."""
    result = vector
    for letter in word:
        if letter == "t":
            result = {
                ((power + 1) % 4, tail): coefficient
                for (power, tail), coefficient in result.items()
            }
        elif letter == "T":
            result = {
                ((power - 1) % 4, tail): coefficient
                for (power, tail), coefficient in result.items()
            }
        elif letter == "z":
            result = {
                (power, tail + "z"): coefficient
                for (power, tail), coefficient in result.items()
            }
        else:
            raise ValueError(f"four-state action cannot reduce {word!r}")
    return result


def _state_action(vector: StateVector, element: GroupRingElement) -> StateVector:
    result: StateVector = {}
    for word, coefficient in element.items():
        result = _state_add(
            result,
            _state_scale(_state_right_word(vector, word), coefficient),
        )
    return result


def _as_group_ring(vector: StateVector) -> GroupRingElement:
    return {
        "t" * power + suffix: coefficient
        for (power, suffix), coefficient in vector.items()
    }


def four_state_residuals(sigma: int, g: str) -> tuple[GroupRingElement, ...]:
    """Evaluate ``v(A_row + sigma*g*D_row)`` under the three module laws.

    States encode ``v, vt, vt^2, vt^3``; reducing their exponent modulo four
    is exactly ``vt^4 = v``.  The relation ``vg = -sigma*S`` eliminates the
    arbitrary word ``g`` as a whole, so no assumption about its spelling is
    made here.
    """
    if sigma not in (1, -1):
        raise ValueError("sigma must be 1 or -1")
    s: StateVector = {(power, ""): 1 for power in range(4)}
    v: StateVector = {(0, ""): 1}
    evaluated_g = _impose_quotient_equalities(g)
    symbolic_row = _symbolic_relative_row(sigma)
    relative_row = evaluated_relative_row(sigma, g)

    residuals: list[GroupRingElement] = []
    for index, (coordinate, concrete_coordinate) in enumerate(
        zip(symbolic_row, relative_row, strict=True)
    ):
        if _project_symbolic_coordinate(coordinate, evaluated_g) != concrete_coordinate:
            raise AssertionError("symbolic relative row does not match its group-ring row")
        a_coordinate = _symbolic_part(coordinate, has_g_prefix=False)
        g_d_coordinate = _symbolic_part(coordinate, has_g_prefix=True)
        if index == 0:
            if a_coordinate != {"q": 1, "qx": 1, "qxx": 1}:
                raise AssertionError("x-coordinate is not q(1+x+x^2)")
            a_action = _state_right_word(s, "z")
        else:
            a_action = _state_action(v, a_coordinate)

        g_d_action = _state_action(_state_scale(s, -sigma), g_d_coordinate)
        residuals.append(
            _as_group_ring(
                _state_add(a_action, g_d_action)
            )
        )
    return tuple(residuals)


def finite_bs34_order_compatible(n: int) -> bool:
    """Return whether order ``n`` survives conjugacy of ``x^3`` and ``x^4``."""
    if n < 1:
        raise ValueError("a finite group element must have positive order")
    return n // gcd(n, 3) == n // gcd(n, 4)


def finite_cyclic_collapse_certificate(n: int) -> tuple[int, int]:
    """Return inverses of 4 and 3 modulo a compatible finite order."""
    if not finite_bs34_order_compatible(n):
        raise ValueError("n is incompatible with the BS(3,4) conjugacy relation")
    return pow(4, -1, n), pow(3, -1, n)


AffineAction = tuple[Fraction, Fraction]
ArithmeticProgression = tuple[Fraction, Fraction]


def affine_word_action(word: str) -> AffineAction:
    """Return ``(scale, offset)`` for the right affine action of an x,y word."""
    if set(word) - set("xXyY"):
        raise ValueError(f"affine action only accepts x and y: {word!r}")

    scale = Fraction(1)
    offset = Fraction(0)
    for letter in word:
        if letter == "x":
            offset += 1
        elif letter == "X":
            offset -= 1
        elif letter == "y":
            scale *= Fraction(3, 4)
            offset *= Fraction(3, 4)
        else:
            scale *= Fraction(4, 3)
            offset *= Fraction(4, 3)
    return scale, offset


def progression_right_word(
    progression: ArithmeticProgression,
    word: str,
) -> ArithmeticProgression:
    """Map one rational arithmetic progression through the affine action."""
    step, start = progression
    if step <= 0:
        raise ValueError("progression step must be positive")
    scale, offset = affine_word_action(word)
    image_step = step * scale
    image_start = (start * scale + offset) % image_step
    return image_step, image_start


def integer_progression_partition(
    progressions: tuple[ArithmeticProgression, ...],
) -> bool:
    """Decide the displayed exact partition of Z by all residue classes."""
    if not progressions:
        return False
    step = progressions[0][0]
    if step.denominator != 1 or step <= 0:
        return False
    modulus = step.numerator
    return (
        len(progressions) == modulus
        and all(candidate_step == step for candidate_step, _ in progressions)
        and {
            start.numerator
            for _, start in progressions
            if start.denominator == 1
        }
        == set(range(modulus))
    )


def relative_free_u_action(
    sigma: int,
    vector: tuple[int, int],
) -> tuple[int, int]:
    """Apply the explicit U on coordinates in the basis (w, wR4)."""
    if sigma not in (1, -1):
        raise ValueError("sigma must be 1 or -1")
    w_coefficient, w_r4_coefficient = vector
    return w_r4_coefficient, -sigma * w_coefficient
