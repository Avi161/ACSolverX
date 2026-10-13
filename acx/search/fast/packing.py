"""The fast engine's packed state rows: each relator ``bits`` a Booth symbol, the first symbol in the high bits.

``bits`` is the least power of two that holds the ``2 n_gen`` symbols (1, 2, 4 or 8), so no symbol straddles two
bytes; the rest of a relator's last byte is 0. Two generators take a quarter of a byte per letter. The dedup table and
the heap read the packed bytes; a state is unpacked only when it is popped or reported. Packing a state also returns
its dedup hash (FNV-1a over the lengths and packed bytes), folded in as each byte is made, so a child is read once.
"""
import numpy as np
from numba import njit

FNV_OFFSET = np.uint64(1469598103934665603)


@njit(inline="always")
def fnv(h, v):
    """One FNV-1a step: ``h`` with ``v`` folded in."""
    return (h ^ np.uint64(v)) * np.uint64(1099511628211)


@njit(inline="always")
def fnv_end(h):
    """The last step of the dedup hash: the high bits folded into the low ones, which pick the slot."""
    return h ^ (h >> np.uint64(29))


def field_bits(n_gen):
    """Bits a symbol of an ``n_gen``-generator state is stored in."""
    bits = 1
    while 1 << bits < 2 * n_gen:
        bits *= 2
    return bits


def packed_width(width, bits):
    """Bytes a relator of up to ``width`` symbols takes."""
    return (width * bits + 7) // 8


@njit(inline="always")
def used_bytes(n, bits):
    """Bytes that hold a relator of ``n`` symbols."""
    return (n * bits + 7) >> 3


@njit(inline="always")
def symbol(prow, t, bits):
    """Symbol ``t`` of the packed relator ``prow``: bits ``t * bits`` onwards, counted from the high end."""
    at = t * bits
    return (prow[at >> 3] >> (8 - bits - (at & 7))) & ((1 << bits) - 1)


@njit(inline="always")
def _last_byte(row, r, t0, n, bits):
    """The part-filled last byte of a relator: the symbols ``row[r, t0:n]`` from the high end, then 0."""
    v = 0
    for t in range(t0, n):
        v = (v << bits) | row[r, t]
    return v << (8 - bits * (n - t0))


@njit(inline="always", cache=True)     # cached for the calls from Python
def pack_state(row, rlen, bits, dst):
    """Pack the relators ``row[r, :rlen[r]]`` into ``dst[r]``; returns the dedup hash of the packed state.

    One loop for each symbol width fills the whole bytes (``t0`` symbols); ``_last_byte`` makes a part-filled one.
    """
    h = FNV_OFFSET
    for r in range(len(rlen)):
        n = rlen[r]
        h = fnv(h, n + 256)
        if bits == 2:
            whole, t0 = n >> 2, n & ~3
            for k in range(whole):
                t = 4 * k
                v = (row[r, t] << 6) | (row[r, t + 1] << 4) | (row[r, t + 2] << 2) | row[r, t + 3]
                dst[r, k] = v
                h = fnv(h, v)
        elif bits == 4:
            whole, t0 = n >> 1, n & ~1
            for k in range(whole):
                v = (row[r, 2 * k] << 4) | row[r, 2 * k + 1]
                dst[r, k] = v
                h = fnv(h, v)
        elif bits == 8:
            whole, t0 = n, n
            for t in range(n):
                dst[r, t] = row[r, t]
                h = fnv(h, row[r, t])
        else:
            whole, t0 = n >> 3, n & ~7
            for k in range(whole):
                v = 0
                for t in range(8 * k, 8 * k + 8):
                    v = (v << 1) | row[r, t]
                dst[r, k] = v
                h = fnv(h, v)
        if t0 < n:
            v = _last_byte(row, r, t0, n, bits)
            dst[r, whole] = v
            h = fnv(h, v)
    return fnv_end(h)


@njit(inline="always", cache=True)     # cached for the calls from Python
def unpack_state(src, rlen, bits, dst):
    """The inverse of ``pack_state``: the symbols of ``src[r]`` into ``dst[r, :rlen[r]]``."""
    for r in range(len(rlen)):
        for t in range(rlen[r]):
            dst[r, t] = symbol(src[r], t, bits)
