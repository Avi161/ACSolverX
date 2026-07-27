"""Replay the universal A--D quotient and its evaluated Fox row.

The quotient uses only ``qx^3q^-1 = t^4`` and ``zxz^-1 = t``.  The
four-state calculation is formal: it checks that the displayed module
relations annihilate the evaluated row for an arbitrary element ``g``.
"""

from __future__ import annotations


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
        reduced = reduced.replace("qxxxQ", "tttt").replace("zxZ", "t")
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


StateVector = dict[tuple[int, str], int]


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


def _state_right_multiply(
    vector: StateVector,
    t_shift: int = 0,
    suffix: str = "",
) -> StateVector:
    return {
        ((power + t_shift) % 4, tail + suffix): coefficient
        for (power, tail), coefficient in vector.items()
    }


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
    free_reduce(g)

    s: StateVector = {(power, ""): 1 for power in range(4)}
    s_z = _state_right_multiply(s, suffix="z")

    # x: Sz + sigma(-sigma S)t^-1z; t: -S + sigma(-sigma S)(-t^-1).
    x_residual = _state_add(s_z, _state_scale(s_z, -1))
    t_residual = _state_add(_state_scale(s, -1), s)

    # z: sigma(-sigma S)(t^-1 - 1), using St^-1 = S; q: v(1-t^4).
    z_residual = _state_add(
        _state_scale(_state_right_multiply(s, t_shift=-1), -1),
        s,
    )
    q_residual: StateVector = {}

    return tuple(
        _as_group_ring(residual)
        for residual in (x_residual, t_residual, z_residual, q_residual)
    )
