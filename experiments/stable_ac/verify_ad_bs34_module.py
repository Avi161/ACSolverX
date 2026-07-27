"""Replay the universal A--D quotient and its evaluated Fox row.

The quotient uses only ``qx^3q^-1 = t^4`` and ``zxz^-1 = t``.  The
four-state calculation is formal: it checks that the displayed module
relations annihilate the evaluated row for an arbitrary element ``g``.
"""

from __future__ import annotations

from dataclasses import dataclass
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


SymbolicModuleTerm = tuple[str, str]
SymbolicModuleVector = dict[SymbolicModuleTerm, int]


@dataclass(frozen=True)
class ExactRelationCertificate:
    """An integral relation and the exact combination that derives it."""

    target: SymbolicModuleVector
    expansion: SymbolicModuleVector


def _module_add_term(
    vector: SymbolicModuleVector,
    term: SymbolicModuleTerm,
    coefficient: int,
) -> None:
    vector[term] = vector.get(term, 0) + coefficient
    if not vector[term]:
        del vector[term]


def _module_vector(*terms: tuple[int, str]) -> SymbolicModuleVector:
    vector: SymbolicModuleVector = {}
    for coefficient, word in terms:
        _module_add_term(vector, ("v", free_reduce(word)), coefficient)
    return vector


def _module_add(*vectors: SymbolicModuleVector) -> SymbolicModuleVector:
    result: SymbolicModuleVector = {}
    for vector in vectors:
        for term, coefficient in vector.items():
            _module_add_term(result, term, coefficient)
    return result


def _module_scale(
    vector: SymbolicModuleVector,
    coefficient: int,
) -> SymbolicModuleVector:
    return {
        term: coefficient * value
        for term, value in vector.items()
        if coefficient * value
    }


def _module_right_word(
    vector: SymbolicModuleVector,
    word: str,
) -> SymbolicModuleVector:
    return _module_vector(
        *((coefficient, base_word + word) for (_, base_word), coefficient in vector.items())
    )


def _reduce_trailing_power(word: str, generator: str, n: int) -> str:
    power = len(word) - len(word.rstrip(generator))
    return word[:-power] + generator * (power % n) if power else word


def _module_cyclic_right_power(
    vector: SymbolicModuleVector,
    generator: str,
    power: int,
    n: int,
) -> SymbolicModuleVector:
    acted = _module_right_word(vector, generator * power)
    reduced: SymbolicModuleVector = {}
    for (base, word), coefficient in acted.items():
        _module_add_term(
            reduced,
            (base, _reduce_trailing_power(word, generator, n)),
            coefficient,
        )
    return reduced


def _cyclic_step_expansion(
    relation: SymbolicModuleVector,
    generator: str,
    step: int,
    n: int,
) -> SymbolicModuleVector:
    inverse = pow(step, -1, n)
    return _module_add(
        *(
            _module_cyclic_right_power(relation, generator, step * index, n)
            for index in range(inverse)
        )
    )


def finite_module_replay(
    n: int,
    *,
    three: int = 3,
    four: int = 4,
) -> dict[str, ExactRelationCertificate]:
    """Replay Result 57 by integral symbolic right-action certificates.

    ``three`` and ``four`` parameterize the two BS indices so tests can
    pressure-test the literal coefficients.  Targets remain the canonical
    Result 57 identities; every expansion is built from the displayed group
    and module relations, integer combinations, and right multiplication.
    """
    if not finite_bs34_order_compatible(n):
        raise ValueError("n is incompatible with the BS(3,4) conjugacy relation")
    if gcd(n, three * four) != 1:
        raise ValueError("the replay indices must be invertible modulo n")

    trace: dict[str, ExactRelationCertificate] = {}

    vt_four_relation = _module_vector((1, "t" * four), (-1, ""))
    vt_expansion = _cyclic_step_expansion(vt_four_relation, "t", four, n)
    trace["vt4_implies_vt"] = ExactRelationCertificate(
        _module_vector((1, "t"), (-1, "")),
        vt_expansion,
    )

    wx_target = _module_vector((1, "zx"), (-1, "z"))
    zx_equals_tz = _module_vector((1, "zx"), (-1, "tz"))
    vt_equals_v_right_z = _module_right_word(vt_expansion, "z")
    wx_expansion = _module_add(zx_equals_tz, vt_equals_v_right_z)
    trace["wx_equals_w"] = ExactRelationCertificate(wx_target, wx_expansion)

    wyx_three_target = _module_vector((1, "zyxxx"), (-1, "zy"))
    bs_relation = _module_vector(
        (1, "zy" + "x" * three),
        (-1, "z" + "x" * four + "y"),
    )
    wx_four_equals_w = _module_add(
        *(
            _module_right_word(wx_expansion, "x" * power + "y")
            for power in range(four)
        )
    )
    wyx_three_expansion = _module_add(bs_relation, wx_four_equals_w)
    trace["wyx3_equals_wy"] = ExactRelationCertificate(
        wyx_three_target,
        wyx_three_expansion,
    )

    wyx_expansion = _cyclic_step_expansion(
        wyx_three_expansion,
        "x",
        three,
        n,
    )
    trace["wyx_equals_wy"] = ExactRelationCertificate(
        _module_vector((1, "zyx"), (-1, "zy")),
        wyx_expansion,
    )

    module_relation = _module_add(
        _module_vector(
            *((1, "zy" + "x" * power) for power in range(three))
        ),
        _module_vector(
            *((-1, "t" * power + "z") for power in range(four))
        ),
    )
    collapse_x_terms = _module_scale(
        _module_add(
            *(
                _module_add(
                    *(
                        _module_right_word(wyx_expansion, "x" * shift)
                        for shift in range(power)
                    )
                )
                for power in range(1, three)
            )
        ),
        -1,
    )
    collapse_t_terms = _module_add(
        *(
            _module_add(
                *(
                    _module_right_word(vt_expansion, "t" * shift + "z")
                    for shift in range(power)
                )
            )
            for power in range(1, four)
        )
    )
    index_gap_expansion = _module_add(
        module_relation,
        collapse_x_terms,
        collapse_t_terms,
    )
    trace["three_wy_equals_four_w"] = ExactRelationCertificate(
        _module_vector((3, "zy"), (-4, "z")),
        index_gap_expansion,
    )

    h_gap_expansion = _module_add(
        _module_right_word(index_gap_expansion, "Z"),
        _module_vector((three, "qZ"), (-three, "zyZ")),
    )
    trace["three_vh_equals_four_v"] = ExactRelationCertificate(
        _module_vector((3, "qZ"), (-4, "")),
        h_gap_expansion,
    )

    s_collapse = _module_add(
        *(
            _module_add(
                *(
                    _module_right_word(vt_expansion, "t" * shift)
                    for shift in range(power)
                )
            )
            for power in range(1, four)
        )
    )

    def collapsed_g_relation(sigma: int, g: str) -> SymbolicModuleVector:
        original = _module_add(
            _module_vector((1, g)),
            _module_vector(
                *((sigma, "t" * power) for power in range(four))
            ),
        )
        return _module_add(original, _module_scale(s_collapse, -sigma))

    h = "qZ"
    h_inverse = "zQ"
    positive_h_relation = collapsed_g_relation(1, h)
    trace["positive_h_vg_equals_minus_four_v"] = ExactRelationCertificate(
        _module_vector((1, h), (4, "")),
        positive_h_relation,
    )
    positive_h_scalar = _module_add(
        _module_scale(positive_h_relation, three),
        _module_scale(h_gap_expansion, -1),
    )
    trace["positive_h_sixteen_v"] = ExactRelationCertificate(
        _module_vector((16, "")),
        positive_h_scalar,
    )
    positive_h_four_vh = _module_add(
        _module_scale(positive_h_relation, four),
        _module_scale(positive_h_scalar, -1),
    )
    trace["positive_h_four_vh"] = ExactRelationCertificate(
        _module_vector((4, h)),
        positive_h_four_vh,
    )
    positive_h_four_v = _module_right_word(positive_h_four_vh, h_inverse)
    trace["positive_h_four_v"] = ExactRelationCertificate(
        _module_vector((4, "")),
        positive_h_four_v,
    )
    positive_h_vh = _module_add(
        positive_h_relation,
        _module_scale(positive_h_four_v, -1),
    )
    positive_h_v = _module_right_word(positive_h_vh, h_inverse)
    trace["positive_h_v_equals_zero"] = ExactRelationCertificate(
        _module_vector((1, "")),
        positive_h_v,
    )

    negative_one_relation = collapsed_g_relation(-1, "")
    trace["negative_one_vg_equals_four_v"] = ExactRelationCertificate(
        _module_vector((-3, "")),
        negative_one_relation,
    )
    negative_one_three_v = _module_scale(negative_one_relation, -1)
    trace["negative_one_three_v"] = ExactRelationCertificate(
        _module_vector((3, "")),
        negative_one_three_v,
    )
    negative_one_three_vh = _module_right_word(negative_one_three_v, h)
    negative_one_four_v = _module_add(
        negative_one_three_vh,
        _module_scale(h_gap_expansion, -1),
    )
    trace["negative_one_four_v"] = ExactRelationCertificate(
        _module_vector((4, "")),
        negative_one_four_v,
    )
    negative_one_v = _module_add(
        negative_one_four_v,
        _module_scale(negative_one_three_v, -1),
    )
    trace["negative_one_v_equals_zero"] = ExactRelationCertificate(
        _module_vector((1, "")),
        negative_one_v,
    )

    negative_h_relation = collapsed_g_relation(-1, h)
    trace["negative_h_vg_equals_four_v"] = ExactRelationCertificate(
        _module_vector((1, h), (-4, "")),
        negative_h_relation,
    )
    negative_h_eight_v = _module_add(
        h_gap_expansion,
        _module_scale(negative_h_relation, -three),
    )
    trace["negative_h_eight_v"] = ExactRelationCertificate(
        _module_vector((8, "")),
        negative_h_eight_v,
    )
    negative_h_two_vh = _module_add(
        _module_scale(negative_h_relation, three - 1),
        negative_h_eight_v,
    )
    trace["negative_h_two_vh"] = ExactRelationCertificate(
        _module_vector((2, h)),
        negative_h_two_vh,
    )
    negative_h_two_v = _module_right_word(negative_h_two_vh, h_inverse)
    trace["negative_h_two_v"] = ExactRelationCertificate(
        _module_vector((2, "")),
        negative_h_two_v,
    )
    negative_h_four_v = _module_scale(negative_h_two_v, 2)
    negative_h_vh = _module_add(negative_h_relation, negative_h_four_v)
    negative_h_v = _module_right_word(negative_h_vh, h_inverse)
    trace["negative_h_v_equals_zero"] = ExactRelationCertificate(
        _module_vector((1, "")),
        negative_h_v,
    )

    return trace


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
