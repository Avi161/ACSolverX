"""Word operations on Booth-symbol buffers: free and cyclic reduction, canonical form, relator order."""
import numpy as np
from numba import njit

_ALL_ONES = np.uint64(0xFFFFFFFFFFFFFFFF)


@njit(inline="always")
def reduce_buf(buf, m, cyclic):
    """Reduce ``buf[:m]`` in place (``acx.core.words.reduce``); the result is ``buf[lo:lo+n]``, returned as ``(lo, n)``.

    Free reduction cancels adjacent inverse pairs with a stack. If ``cyclic``, the ends then cancel too, and ``lo``
    is how many letters were stripped from the front (and from the back).
    """
    n = 0
    for t in range(m):
        c = buf[t]
        if n > 0 and buf[n - 1] == c ^ 1:
            n -= 1
        else:
            buf[n] = c
            n += 1
    lo = 0
    if cyclic and n > 1 and buf[0] == buf[n - 1] ^ 1:
        lo = 1
        while 2 * lo < n and buf[lo] == buf[n - 1 - lo] ^ 1:
            lo += 1
        n -= 2 * lo
    return lo, n


@njit(inline="always")
def _letter(w, lo, m, inverse, t):
    """Letter ``t`` of ``w[lo:lo+m]``, or of its inverse word."""
    return w[lo + m - 1 - t] ^ 1 if inverse else w[lo + t]


@njit(inline="always")
def _ring_letter(w, lo, m, inverse, t):
    """Like ``_letter`` for ``0 <= t < 2m``: the word read as a ring."""
    return _letter(w, lo, m, inverse, t - m if t >= m else t)


@njit(inline="always")
def _least_rotation(w, lo, m, inverse):
    """Start of the least rotation of the word (the two-pointer minimum-rotation scan)."""
    i, j, k = 0, 1, 0
    while i < m and j < m and k < m:
        x = _ring_letter(w, lo, m, inverse, i + k)
        y = _ring_letter(w, lo, m, inverse, j + k)
        if x == y:
            k += 1
            continue
        if x > y:
            i += k + 1
        else:
            j += k + 1
        if i == j:
            j += 1
        k = 0
    return min(i, j)


@njit(inline="always")
def _canon_booth(w, lo, m, out):
    """The smaller (Booth order) of the least rotation of ``w[lo:lo+m]`` and of its inverse, written to ``out[:m]``."""
    start = _least_rotation(w, lo, m, False)
    inv_start = _least_rotation(w, lo, m, True)
    use_inverse = False
    for t in range(m):
        x = _ring_letter(w, lo, m, False, start + t)
        y = _ring_letter(w, lo, m, True, inv_start + t)
        if x != y:
            use_inverse = y < x
            break
    first = inv_start if use_inverse else start
    for t in range(m):
        out[t] = _ring_letter(w, lo, m, use_inverse, first + t)


@njit(inline="always")
def _symbol_bits(w, lo, m):
    """The bits that hold every symbol of the word and of its inverse (``b ^ 1``): at least 1."""
    seen = 0
    for t in range(m):
        seen |= w[lo + t]
    bits = 1
    while seen >> bits:
        bits += 1
    return bits


@njit(inline="always")
def _least_packed(w, lo, m, inverse, bits):
    """The least rotation of the word (or its inverse), ``bits`` a symbol in one uint64, the first symbol highest.

    For ``bits * m <= 64``. Packed words of one length compare like their strings. Each step moves the first symbol
    to the end, with shifts of ``bits`` and ``bits * (m - 1)``, both below 64.
    """
    b = np.uint64(bits)
    rest = np.uint64(bits * (m - 1))
    mask = _ALL_ONES >> np.uint64(64 - bits * m)
    v = np.uint64(0)
    for t in range(m):
        v = (v << b) | np.uint64(_letter(w, lo, m, inverse, t))
    least = v
    for _ in range(m - 1):
        v = ((v << b) | (v >> rest)) & mask
        least = min(least, v)
    return least


@njit(inline="always")
def _canon_packed(w, lo, m, out, bits):
    """``_canon_booth`` for ``bits * m <= 64``: the lesser packed word, unpacked to ``out[:m]``."""
    least = min(_least_packed(w, lo, m, False, bits), _least_packed(w, lo, m, True, bits))
    symbol = (np.uint64(1) << np.uint64(bits)) - np.uint64(1)
    for t in range(m):
        out[t] = (least >> np.uint64(bits * (m - 1 - t))) & symbol


@njit(inline="always")
def canon_buf(w, lo, m, out):
    """Write the canonical form of ``w[lo:lo+m]`` to ``out[:m]``, the string ``acx.core.words.canonical_word`` gives.

    A word of ``m`` symbols with ``b * m <= 64``, ``b`` the bit length of its largest symbol, is canonicalised packed
    in one integer (any word of up to 32 letters at two generators, 21 at three or four, 16 at five to eight), a
    longer one by Booth's scan.
    """
    if m == 0:
        return
    bits = _symbol_bits(w, lo, m)
    if bits * m <= 64:
        _canon_packed(w, lo, m, out, bits)
    else:
        _canon_booth(w, lo, m, out)


@njit(inline="always")
def rel_less(a, la, b, lb):
    """``(len, Booth order)``: the relator order of ``sort_rels``."""
    if la != lb:
        return la < lb
    for t in range(la):
        if a[t] != b[t]:
            return a[t] < b[t]
    return False
