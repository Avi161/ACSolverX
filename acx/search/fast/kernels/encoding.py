"""Booth-symbol encoding of states for the numba kernels.

A state is ``(syms, lens)``: ``syms`` a ``(R, W)`` uint8 array whose row ``r`` holds relator ``r`` in its first
``lens[r]`` entries. A letter ``g`` of an ``n``-generator word is the Booth symbol ``b = 2 * (n - |g|) + (g > 0)``,
so integer order is Booth order (``Y=0 < y=1 < X=2 < x=3`` at two generators) and the inverse letter is ``b ^ 1``.
At most 127 generators fit a byte.
"""
import numpy as np
from numba import njit


def encode(rels, n_gen, width=None):
    """Int-tuple relators -> ``(syms (R, width) uint8, lens (R,) int32)``."""
    if n_gen > 127:
        raise ValueError(f"the fast backend holds at most 127 generators, got {n_gen}")
    lens = np.array([len(r) for r in rels], dtype=np.int32)
    syms = np.zeros((len(rels), max([width or 0, 1, *lens])), dtype=np.uint8)
    for r, word in enumerate(rels):
        syms[r, :len(word)] = [2 * (n_gen - abs(g)) + (g > 0) for g in word]
    return syms, lens


def decode(syms, lens, n_gen):
    """Inverse of ``encode``: a tuple of int-tuple relators."""
    def letter(b):
        return (n_gen - (int(b) >> 1)) * (1 if b & 1 else -1)

    return tuple(tuple(letter(b) for b in syms[r, :lens[r]]) for r in range(len(lens)))


@njit(inline="always")
def generator(b, n_gen):
    """The generator number (1 .. n) of Booth symbol ``b``."""
    return n_gen - (b >> 1)


@njit(inline="always")
def key_code(b, n_gen):
    """The heap tie-break code of Booth symbol ``b`` (``X=1 < Y=2 < x=3 < y=4`` at two generators)."""
    g = generator(b, n_gen)
    return n_gen + g if b & 1 else g


@njit(inline="always")
def tie_bytes(row, rlen, n_gen, buf, o):
    """Write the state's ``state_bytes`` (key codes, a 0 after each relator) at ``buf[o:]``; return the count."""
    k = o
    for r in range(len(rlen)):
        for t in range(rlen[r]):
            buf[k] = key_code(row[r, t], n_gen)
            k += 1
        buf[k] = 0
        k += 1
    return k - o
