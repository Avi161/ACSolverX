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


def _freely_reduced_words(
    length: int,
) -> Iterator[tuple[str, NormalForm]]:
    def visit(
        prefix: str,
        previous: str | None,
        state: NormalForm,
    ) -> Iterator[tuple[str, NormalForm]]:
        if len(prefix) == length:
            yield prefix, state
            return
        for letter in _ALPHABET:
            if previous is not None and letter == _INVERSE[previous]:
                continue
            yield from visit(
                prefix + letter,
                letter,
                _append_letter(state, letter),
            )

    yield from visit("", None, (0, ()))


def _inverse_word(word: str) -> str:
    return "".join(_INVERSE[letter] for letter in reversed(word))


def _recoveries_of_length(length: int) -> Iterator[str]:
    """Meet-in-the-middle enumeration of exact-length recoveries."""
    left_length = length // 2
    right_length = length - left_length

    right_by_state: dict[NormalForm, list[str]] = {}
    for word, state in _freely_reduced_words(right_length):
        right_by_state.setdefault(state, []).append(word)

    for left, _ in _freely_reduced_words(left_length):
        required = normal_form(_inverse_word(left) + "t")
        for right in right_by_state.get(required, ()):
            if left and right and right[0] == _INVERSE[left[-1]]:
                continue
            yield left + right


def recoveries_up_to(max_length: int) -> tuple[str, ...]:
    """Enumerate every freely reduced word of length at most ``max_length``
    that represents ``t`` in ``<x,t | x^3=t^4>``.
    """
    if max_length < 0:
        raise ValueError("max_length must be nonnegative")

    recoveries = []
    for length in range(1, max_length + 1):
        recoveries.extend(_recoveries_of_length(length))
    return tuple(recoveries)
