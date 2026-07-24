"""Exact normal forms for ``<x,t | x^3=t^4>`` recovery words.

The common element ``c=x^3=t^4`` is central.  A group element therefore
has a unique form

    c^k s_1 ... s_r,

where adjacent syllables alternate between the ``x`` and ``t`` factors,
an ``x`` syllable has exponent 1 or 2, and a ``t`` syllable has exponent
1, 2, or 3.
"""

from __future__ import annotations

from collections.abc import Iterator


NormalForm = tuple[int, tuple[tuple[str, int], ...]]

_ALPHABET = ("x", "X", "t", "T")
_INVERSE = {"x": "X", "X": "x", "t": "T", "T": "t"}
_MODULUS = {"x": 3, "t": 4}
_TARGET_T: NormalForm = (0, (("t", 1),))


def _append_letter(state: NormalForm, letter: str) -> NormalForm:
    generator = letter.lower()
    exponent = 1 if letter.islower() else -1
    central, syllable_tuple = state
    syllables = list(syllable_tuple)

    if syllables and syllables[-1][0] == generator:
        exponent += syllables.pop()[1]

    quotient, residue = divmod(exponent, _MODULUS[generator])
    central += quotient
    if residue:
        syllables.append((generator, residue))
    return central, tuple(syllables)


def normal_form(word: str) -> NormalForm:
    """Return the canonical amalgamated-product normal form of ``word``."""
    state: NormalForm = (0, ())
    for letter in word:
        if letter not in _INVERSE:
            raise ValueError(f"invalid recovery letter: {letter!r}")
        state = _append_letter(state, letter)
    return state


def equals_t(word: str) -> bool:
    """Whether ``word`` represents ``t`` modulo ``x^3=t^4``."""
    return normal_form(word) == _TARGET_T


def _abelianization_can_reach_t(
    x_sum: int,
    t_sum: int,
    remaining: int,
) -> bool:
    """Necessary endpoint test used only to prune impossible prefixes.

    If a word represents ``t``, its exponent sums have the form
    ``(3k, 1-4k)`` because the defining relator has vector ``(3,-4)``.
    """
    minimum_k = -((-(x_sum - remaining)) // 3)
    maximum_k = (x_sum + remaining) // 3
    for k in range(minimum_k, maximum_k + 1):
        distance = abs(3 * k - x_sum) + abs(1 - 4 * k - t_sum)
        if distance <= remaining and (remaining - distance) % 2 == 0:
            return True
    return False


def _recovery_words_of_length(
    length: int,
) -> Iterator[tuple[str, NormalForm]]:
    def visit(
        prefix: str,
        previous: str | None,
        state: NormalForm,
        x_sum: int,
        t_sum: int,
    ) -> Iterator[tuple[str, NormalForm]]:
        remaining = length - len(prefix)
        if not _abelianization_can_reach_t(
            x_sum,
            t_sum,
            remaining,
        ):
            return
        if len(prefix) == length:
            if state == _TARGET_T:
                yield prefix, state
            return
        for letter in _ALPHABET:
            if previous is not None and letter == _INVERSE[previous]:
                continue
            yield from visit(
                prefix + letter,
                letter,
                _append_letter(state, letter),
                x_sum
                + (1 if letter == "x" else -1 if letter == "X" else 0),
                t_sum
                + (1 if letter == "t" else -1 if letter == "T" else 0),
            )

    yield from visit("", None, (0, ()), 0, 0)


def recoveries_up_to(max_length: int) -> tuple[str, ...]:
    """Enumerate every freely reduced word of length at most ``max_length``
    that represents ``t`` in ``<x,t | x^3=t^4>``.
    """
    if max_length < 0:
        raise ValueError("max_length must be nonnegative")

    recoveries = []
    for length in range(1, max_length + 1):
        recoveries.extend(
            word
            for word, _ in _recovery_words_of_length(length)
        )
    return tuple(recoveries)
