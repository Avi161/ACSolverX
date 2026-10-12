"""Word operations on Booth-symbol buffers: free and cyclic reduction, canonical form, relator order."""
from numba import njit


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
def canon_buf(w, lo, m, out):
    """Write the canonical form of ``w[lo:lo+m]`` to ``out[:m]``.

    That is the smaller (Booth order) of the least rotation of the word and of its inverse, the same string as
    ``acx.core.words.canonical_word``.
    """
    if m == 0:
        return
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
def rel_less(a, la, b, lb):
    """``(len, Booth order)``: the relator order of ``sort_rels``."""
    if la != lb:
        return la < lb
    for t in range(la):
        if a[t] != b[t]:
            return a[t] < b[t]
    return False
