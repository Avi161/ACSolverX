"""The fast engine's packed state rows: each relator ``bits`` a Booth symbol, the first symbol in the high bits.

``bits`` is the least power of two that holds the ``2 n_gen`` symbols (1, 2, 4 or 8), so no symbol straddles two
bytes; the rest of a relator's last byte is 0. Two generators take a quarter of a byte per letter. The dedup table and
the heap read the packed bytes; a state is unpacked only when it is popped or reported.
"""
from numba import njit


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
def pack_state(row, rlen, bits, dst):
    """Pack the relators ``row[r, :rlen[r]]`` into ``dst[r]``."""
    per = 8 // bits
    for r in range(len(rlen)):
        n = rlen[r]
        for k in range(used_bytes(n, bits)):
            v = 0
            for t in range(k * per, (k + 1) * per):
                v = (v << bits) | (row[r, t] if t < n else 0)
            dst[r, k] = v


@njit(inline="always")
def unpack_state(src, rlen, bits, dst):
    """The inverse of ``pack_state``: the symbols of ``src[r]`` into ``dst[r, :rlen[r]]``."""
    for r in range(len(rlen)):
        for t in range(rlen[r]):
            dst[r, t] = symbol(src[r], t, bits)
