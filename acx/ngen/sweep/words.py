"""The word pool and the stabilised starts of the rank-n sweep.

A start is ``<x, y, z1..zk | r1, r2, Z1.w1, .., Zk.wk>`` for words ``w_i`` in ``x, y``.
"""
import hashlib
import itertools
from functools import lru_cache

from ...core.words import Presentation, fmt, inverse

LETTERS = (1, 2, -1, -2)                    # x, y, X, Y


@lru_cache(maxsize=None)
def reduced_words(length):
    """Freely reduced words of ``length`` over x, y, X, Y; of each pair ``{w, w^-1}`` the larger, depth-first."""
    found = []

    def extend(prefix):
        if len(prefix) == length:
            if prefix > inverse(prefix):
                found.append(prefix)
            return
        for letter in LETTERS:
            if not prefix or prefix[-1] != -letter:
                extend(prefix + (letter,))

    extend(())
    return tuple(found)


def start(r1, r2, words):
    """``<x, y, z1..zk | r1, r2, Z1.w1, .., Zk.wk>``; empty words give the null stabilisation."""
    new_relators = tuple((-(3 + i),) + tuple(w) for i, w in enumerate(words))
    return Presentation(2 + len(words), (tuple(r1), tuple(r2)) + new_relators)


@lru_cache(maxsize=None)
def pool(min_len, max_len, inverted):
    """The words of lengths ``min_len..max_len`` (each word's inverse when ``inverted``), in ``reduced_words`` order."""
    words = tuple(w for n in range(min_len, max_len + 1) for w in reduced_words(n))
    return tuple(inverse(w) for w in words) if inverted else words


@lru_cache(maxsize=None)
def combos(n_words, extra):
    """Index tuples of the starts: every multiset of ``extra`` pool words (one word each for ``extra = 1``)."""
    return tuple(itertools.combinations_with_replacement(range(n_words), extra))


def word_str(words):
    """``"x"`` for one word, ``"x,yX"`` for several."""
    return ",".join(fmt(w) for w in words)


def sampled(row_id, words, fraction):
    """Whether a solved start keeps its path: a fixed hash of ``row_id|words`` below ``fraction``."""
    digest = hashlib.md5(f"{row_id}|{words}".encode()).digest()
    return int.from_bytes(digest[:8], "big") / 2 ** 64 < fraction
