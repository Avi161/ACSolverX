"""Replay exact free-product syllable reductions used by Result 59.

This module checks displayed normal-form calculations in finite fixtures.
The universal relative rank-one statement is proved in the accompanying
Markdown argument, not by these computations.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence


Syllable = tuple[str, int]
Word = tuple[Syllable, ...]
Orders = Mapping[str, int]


def _reduced_value(factor: str, value: int, orders: Orders | None) -> int:
    if not factor:
        raise ValueError("a factor name must be nonempty")
    if orders is None or factor not in orders:
        return value
    order = orders[factor]
    if order <= 0:
        raise ValueError("factor orders must be positive")
    return value % order


def reduce_syllables(
    word: Sequence[Syllable],
    orders: Orders | None = None,
) -> Word:
    """Reduce a word in a free product of cyclic fixture factors."""
    reduced: list[Syllable] = []
    for factor, raw_value in word:
        value = _reduced_value(factor, raw_value, orders)
        if not value:
            continue
        if reduced and reduced[-1][0] == factor:
            value = _reduced_value(factor, reduced[-1][1] + value, orders)
            reduced.pop()
            if value:
                reduced.append((factor, value))
        else:
            reduced.append((factor, value))
    return tuple(reduced)


def _inverse_syllables(
    word: Sequence[Syllable],
    orders: Orders | None = None,
) -> Word:
    return reduce_syllables(
        tuple((factor, -value) for factor, value in reversed(word)),
        orders=orders,
    )


def power_syllables(
    word: Sequence[Syllable],
    exponent: int,
    orders: Orders | None = None,
) -> Word:
    """Return the exact reduced fixture word raised to an integer power."""
    if not isinstance(exponent, int):
        raise TypeError("exponent must be an integer")
    base = reduce_syllables(word, orders=orders)
    if exponent < 0:
        base = _inverse_syllables(base, orders=orders)
    result: Word = ()
    for _ in range(abs(exponent)):
        result = reduce_syllables(result + base, orders=orders)
    return result


def trim_base_endpoints(
    word: Sequence[Syllable],
    base_factor: str = "A",
    orders: Orders | None = None,
) -> tuple[Syllable | None, Word, Syllable | None]:
    """Split a reduced word as an optional base syllable, core, base syllable."""
    core = list(reduce_syllables(word, orders=orders))
    left = core.pop(0) if core and core[0][0] == base_factor else None
    right = core.pop() if core and core[-1][0] == base_factor else None
    return left, tuple(core), right


def evaluate_relative_word(
    relative_word: Sequence[Syllable],
    u: Sequence[Syllable],
    orders: Orders | None = None,
    base_factor: str = "A",
    stable_factor: str = "S",
) -> Word:
    """Evaluate a word in ``A*<S>`` after substituting the ambient word ``u``."""
    relative_orders = (
        None
        if orders is None
        else {factor: order for factor, order in orders.items() if factor != stable_factor}
    )
    normalized = reduce_syllables(relative_word, orders=relative_orders)
    result: Word = ()
    for factor, exponent in normalized:
        if factor == base_factor:
            image = ((base_factor, exponent),)
        elif factor == stable_factor:
            image = power_syllables(u, exponent, orders=orders)
        else:
            raise ValueError(
                f"relative words may use only {base_factor!r} and {stable_factor!r}"
            )
        result = reduce_syllables(result + image, orders=orders)
    return result
