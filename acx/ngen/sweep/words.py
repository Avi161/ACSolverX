"""The word pool and the stabilised starts of the rank-n sweep.

A start is ``<x, y, z1..zk | r1, r2, Z1.w1, .., Zk.wk>`` for words ``w_i`` in ``x, y``.
"""
import hashlib
import itertools
import math
import operator
from collections.abc import Sequence
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


class Combinations(Sequence):
    """Word-index multisets in itertools order, without storing every combination.

    Iteration streams the starts; indexing un-ranks one start in O(extra * log(n_words)) steps. This lets the
    summary and verifier address a stored cell without allocating the entire rank-four/five combination table.
    """

    def __init__(self, n_words, extra):
        self.n_words, self.extra = n_words, extra
        self.size = math.comb(n_words + extra - 1, extra) if n_words else int(extra == 0)

    def __len__(self):
        return self.size

    def __iter__(self):
        return itertools.combinations_with_replacement(range(self.n_words), self.extra)

    def __getitem__(self, index):
        if isinstance(index, slice):
            return tuple(self[i] for i in range(*index.indices(len(self))))
        index = operator.index(index)
        if index < 0:
            index += len(self)
        if not 0 <= index < len(self):
            raise IndexError("combination index out of range")
        chosen, low = [], 0
        for remaining in range(self.extra, 0, -1):
            total = math.comb(self.n_words - low + remaining - 1, remaining)
            left, right = low, self.n_words - 1
            # Starts whose next index is below v: total - C(n_words-v+remaining-1, remaining).
            while left < right:
                mid = (left + right + 1) // 2
                skipped = total - math.comb(self.n_words - mid + remaining - 1, remaining)
                if skipped <= index:
                    left = mid
                else:
                    right = mid - 1
            index -= total - math.comb(self.n_words - left + remaining - 1, remaining)
            chosen.append(left)
            low = left
        return tuple(chosen)


def combos(n_words, extra):
    """A lazy, indexable sequence of every multiset of ``extra`` word indices (in the published cell order)."""
    return Combinations(n_words, extra)


def word_str(words):
    """``"x"`` for one word, ``"x,yX"`` for several."""
    return ",".join(fmt(w) for w in words)


def sampled(row_id, words, fraction):
    """Whether a solved start keeps its path: a fixed hash of ``row_id|words`` below ``fraction``."""
    digest = hashlib.md5(f"{row_id}|{words}".encode()).digest()
    return int.from_bytes(digest[:8], "big") / 2 ** 64 < fraction
