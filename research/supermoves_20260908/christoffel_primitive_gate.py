"""Linear sufficient primitive-word gate for signed Christoffel words."""
from functools import lru_cache
from math import gcd


LETTERS = "xXyY"


def _inverse(word):
    return word[::-1].swapcase()


def _cyclic_reduce(word):
    stack = []
    for letter in word:
        if letter not in LETTERS:
            raise ValueError("word must use xXyY")
        if stack and stack[-1] == letter.swapcase():
            stack.pop()
        else:
            stack.append(letter)
    start, stop = 0, len(stack)
    while stop - start >= 2 and stack[start] == stack[stop - 1].swapcase():
        start += 1
        stop -= 1
    return "".join(stack[start:stop])


def mechanical_word(p, q, x_letter="x", y_letter="y"):
    if p < 0 or q < 0 or p + q == 0:
        raise ValueError("counts must be nonnegative and not both zero")
    if x_letter not in "xX" or y_letter not in "yY":
        raise ValueError("expected signed x and y letters")
    length = p + q
    return "".join(
        y_letter if ((index + 1) * q) // length != (index * q) // length else x_letter
        for index in range(length)
    )


def _rotation_index(word, candidate):
    if len(word) != len(candidate):
        return None
    if not word:
        return 0
    failure = [0] * len(candidate)
    matched = 0
    for index in range(1, len(candidate)):
        while matched and candidate[index] != candidate[matched]:
            matched = failure[matched - 1]
        if candidate[index] == candidate[matched]:
            matched += 1
            failure[index] = matched
    matched = 0
    for index, letter in enumerate(word + word[:-1]):
        while matched and letter != candidate[matched]:
            matched = failure[matched - 1]
        if letter == candidate[matched]:
            matched += 1
            if matched == len(candidate):
                start = index - len(candidate) + 1
                return start if start < len(word) else None
    return None


def euclidean_witness(p, q):
    steps = []
    while p and q:
        if p > q:
            steps.append("y->xy")
            p -= q
        else:
            steps.append("x->xy")
            q -= p
    return steps, (p, q)


@lru_cache(maxsize=16384)
def _recognize_reduced(word):
    if not word:
        return None
    x_signs = {letter for letter in word if letter.lower() == "x"}
    y_signs = {letter for letter in word if letter.lower() == "y"}
    if len(x_signs) > 1 or len(y_signs) > 1:
        return None
    p = sum(letter.lower() == "x" for letter in word)
    q = len(word) - p
    if p == 0 or q == 0:
        if len(word) != 1:
            return None
        return dict(
            p=p,
            q=q,
            x_letter=next(iter(x_signs), "x"),
            y_letter=next(iter(y_signs), "y"),
            inverse_match=False,
            cut=0,
            euclidean_steps=[],
        )
    if gcd(p, q) != 1:
        return None
    x_letter, y_letter = next(iter(x_signs)), next(iter(y_signs))
    candidate = mechanical_word(p, q, x_letter, y_letter)
    for inverse_match, oriented in ((False, candidate), (True, _inverse(candidate))):
        cut = _rotation_index(word, oriented)
        if cut is not None:
            steps, terminal = euclidean_witness(p, q)
            if terminal not in ((1, 0), (0, 1)):
                raise AssertionError("coprime Euclidean witness did not reach a generator")
            return dict(
                p=p,
                q=q,
                x_letter=x_letter,
                y_letter=y_letter,
                inverse_match=inverse_match,
                cut=cut,
                euclidean_steps=steps,
            )
    return None


def recognize_canonical(word):
    """Recognize an already freely and cyclically reduced canonical relator.

    Callers must supply the search engine's canonical relator representation.
    This deliberately skips reduction; use ``recognize`` for arbitrary words.
    """
    if not isinstance(word, str):
        raise ValueError("word must be a string")
    return _recognize_reduced(word)


def is_christoffel_primitive_canonical(word):
    """Boolean form of ``recognize_canonical`` for canonical search states."""
    return recognize_canonical(word) is not None


def recognize(word):
    """Return a constructive sufficient primitive witness, or None."""
    if not isinstance(word, str):
        raise ValueError("word must be a string")
    return _recognize_reduced(_cyclic_reduce(word))


def is_christoffel_primitive(word):
    return recognize(word) is not None

