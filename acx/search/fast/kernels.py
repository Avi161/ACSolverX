"""Numba kernels: reduce, canonicalise, expand and score one state, for any search.

Ported from ``hexpand.expand_children_h`` / ``expand_and_score_h``
(``origin/codex/ac-elementary-decoder:experiments/heuristic_search/core/hexpand.py``,
commit a8a6b3a4) and ``hfast._feats_nj``, generalised from two relators on main's
``(n, 2)`` bool arrays to any number of relators and generators.

ENCODING. A state is ``(syms, lens)``: ``syms`` a ``(R, W)`` uint8 array, row
``r`` holding relator ``r`` in its first ``lens[r]`` entries. A letter ``g`` of
an ``n``-generator word is the **Booth symbol** ``b = 2*(n - |g|) + (g > 0)``,
so integer order is ``acx.core.words``' Booth order (``Y=0 < y=1 < X=2 < x=3``
at ``n = 2``) and the inverse letter is ``b ^ 1``. ``key_code(b, n)`` maps a
symbol to the heap tie-break code (``X=1 < Y=2 < x=3 < y=4``).

``expand(syms, lens, n_gen, cap, cyclic, out, out_len, out_mv) -> (count, rejected)``
writes every new-relator child of the state, exactly as ``acx.search.spec``
builds them (``i -> j -> s -> k1 -> k2`` order; each relator reduced and
canonical, relators sorted by ``(length, Booth order)``), into ``out[c]`` /
``out_len[c]`` with its move ``(i, j, s, k1, k2)`` in ``out_mv[c]``. ``cap < 0``
means uncapped. ``rejected`` counts the legal moves whose child has a relator
over the cap (spec's ``cap_rejected``). The caller sizes ``out`` with
``max_children(lens)`` rows and at least ``child_width(lens)`` columns.

The one change to the child stream is hexpand's **cut-shift skip** (cyclic
reduction only). In a ``(i, j, s)`` block the child of ``(k1, k2)`` is a
conjugate of the child of ``(k1 - 1, k2 + 1)`` whenever that predecessor's seam
cancels, so both reduce to the same canonical relator and the later one is a
repeat the dedup table would drop anyway. A per-block bitmap marks a move when
its child is written or skipped; ``(k1, k2)`` is skipped only when its
predecessor is marked. A cap-rejected child is never marked, and the cyclically
reduced length is a conjugacy invariant, so the cap count is exact too. This
removes about half of the children before any per-child work.

Canonical form: the least rotation (two-pointer minimum-rotation scan) of the
word and of its inverse, the smaller of the two (Booth order, so the same
string as ``acx.core.words.canonical_word``). hexpand's 2-bit packed least
rotation is not ported: it holds two generators only, and canonicalisation is a
small share of a pop next to dedup and the heap.

``score(row, rlen, n_gen, prio)``: ``prio = LENGTH`` (0) gives the total length,
``S20_MK2`` (1) gives ``L + 20 S + 2 MK`` evaluated as
``acc = 0.0; acc += 1.0 L; acc += 2.0 MK; acc += 20.0 S``, bit-identical to
``acx.core.priority.s20_mk2`` (no fastmath anywhere, so no FMA contraction).
"""
import numpy as np
from numba import njit

LENGTH, S20_MK2 = 0, 1
PRIORITY_IDS = {"length": LENGTH, "s20_mk2": S20_MK2}


def encode(rels, n_gen, width=None):
    """Int-tuple relators -> ``(syms (R, width) uint8, lens (R,) int32)``."""
    lens = np.array([len(r) for r in rels], dtype=np.int32)
    syms = np.zeros((len(rels), max([width or 0, 1, *lens])), dtype=np.uint8)
    for r, w in enumerate(rels):
        syms[r, :len(w)] = [2 * (n_gen - abs(g)) + (g > 0) for g in w]
    return syms, lens


def decode(syms, lens, n_gen):
    """Inverse of ``encode``: a tuple of int-tuple relators."""
    return tuple(tuple((n_gen - (int(b) >> 1)) * (1 if b & 1 else -1) for b in syms[r, :lens[r]])
                 for r in range(len(lens)))


@njit(inline="always")
def key_code(b, n):
    g = n - (b >> 1)
    return n + g if b & 1 else g


@njit(cache=True)
def max_children(lens):
    """Upper bound on the legal moves of a state: ``sum_{i != j} 2 l_i l_j``."""
    s = q = 0
    for x in lens:
        s += x
        q += x * x
    return s * s - q


@njit(cache=True)
def child_width(lens):
    """Upper bound on any child relator's length: ``max_{i != j} l_i + l_j``."""
    a = b = 0
    for x in lens:
        if x > a:
            a, b = x, a
        elif x > b:
            b = x
    return a + b


@njit(inline="always")
def _reduce(buf, m, cyclic):
    """Free reduction of ``buf[:m]`` in place, then main's cyclic tail; the result is ``buf[lo:lo+n]``."""
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
def _at(w, lo, m, inv, t):
    """Letter ``t`` of ``w[lo:lo+m]``, or of its inverse."""
    return w[lo + m - 1 - t] ^ 1 if inv else w[lo + t]


@njit(inline="always")
def _least_start(w, lo, m, inv):
    """Start of the least rotation (two-pointer minimum-rotation scan)."""
    i, j, k = 0, 1, 0
    while i < m and j < m and k < m:
        a = i + k
        b = j + k
        x = _at(w, lo, m, inv, a - m if a >= m else a)
        y = _at(w, lo, m, inv, b - m if b >= m else b)
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
def _canon(w, lo, m, out):
    """Write the canonical form of ``w[lo:lo+m]`` to ``out[:m]``."""
    if m == 0:
        return
    a = _least_start(w, lo, m, False)
    b = _least_start(w, lo, m, True)
    inv = False
    for t in range(m):
        p, q = a + t, b + t
        x = _at(w, lo, m, False, p - m if p >= m else p)
        y = _at(w, lo, m, True, q - m if q >= m else q)
        if x != y:
            inv = y < x
            break
    s = b if inv else a
    for t in range(m):
        p = s + t
        out[t] = _at(w, lo, m, inv, p - m if p >= m else p)


@njit(inline="always")
def _rel_less(a, la, b, lb):
    """``(len, Booth order)``: the relator order of ``sort_rels``."""
    if la != lb:
        return la < lb
    for t in range(la):
        if a[t] != b[t]:
            return a[t] < b[t]
    return False


@njit(inline="always")
def _src(syms, j, lo, s, t):
    """Letter ``t`` of ``r_j ** s``."""
    return syms[j, t] if s == 1 else syms[j, lo - 1 - t] ^ 1


@njit(cache=True)
def expand(syms, lens, n_gen, cap, cyclic, out, out_len, out_mv):
    R = len(lens)
    mx = 1
    for r in range(R):
        mx = max(mx, lens[r])
    # the untouched relators, reduced and canonical (the identity on a cyclic search state)
    can = np.empty((R, mx), dtype=np.uint8)
    cl = np.empty(R, dtype=np.int64)
    buf = np.empty(2 * mx, dtype=np.uint8)
    for r in range(R):
        for t in range(lens[r]):
            buf[t] = syms[r, t]
        lo, m = _reduce(buf, lens[r], cyclic)
        _canon(buf, lo, m, can[r])
        cl[r] = m
    new = np.empty(2 * mx, dtype=np.uint8)
    seen = np.zeros(mx * mx, dtype=np.bool_)
    order = np.empty(R, dtype=np.int64)
    hist = np.zeros(2 * n_gen, dtype=np.int64)
    count = rejected = 0
    for i in range(R):
        li = lens[i]
        if li == 0:
            continue
        over = False
        if cap >= 0:
            for k in range(R):
                if k != i and cl[k] > cap:
                    over = True
        if over:   # every legal move of r_i is rejected: count them without building children
            hist[:] = 0
            for t in range(li):
                hist[syms[i, t]] += 1
        for j in range(R):
            lo = lens[j]
            if j == i or lo == 0:
                continue
            for s in (1, -1):
                if over:
                    for t in range(lo):
                        rejected += hist[_src(syms, j, lo, s, t) ^ 1]
                    continue
                if cyclic:
                    seen[:li * lo] = False
                for k1 in range(li):
                    last = syms[i, li - 1 - k1]                       # rotate(r_i, k1)[-1]
                    for k2 in range(lo):
                        if _src(syms, j, lo, s, lo - k2 if k2 else 0) != last ^ 1:
                            continue                                  # the seam does not cancel
                        if cyclic and k1 >= 1:
                            p = (k1 - 1) * lo + (k2 + 1 if k2 + 1 < lo else 0)
                            if seen[p]:                               # cut-shift repeat
                                seen[k1 * lo + k2] = True
                                continue
                        for t in range(li):
                            u = t - k1
                            buf[t] = syms[i, u + li if u < 0 else u]
                        for t in range(lo):
                            u = t - k2
                            buf[li + t] = _src(syms, j, lo, s, u + lo if u < 0 else u)
                        r0, m = _reduce(buf, li + lo, cyclic)
                        if cap >= 0 and m > cap:
                            rejected += 1
                            continue
                        if cyclic:
                            seen[k1 * lo + k2] = True
                        _canon(buf, r0, m, new)
                        # insertion sort of the R relators (the new one stands at index i)
                        for a in range(R):
                            order[a] = a
                            b = a
                            while b > 0:
                                x, y = order[b - 1], order[b]
                                xa = new if x == i else can[x]
                                ya = new if y == i else can[y]
                                if _rel_less(ya, m if y == i else cl[y], xa, m if x == i else cl[x]):
                                    order[b - 1], order[b] = y, x
                                    b -= 1
                                else:
                                    break
                        for a in range(R):
                            x = order[a]
                            n = m if x == i else cl[x]
                            src = new if x == i else can[x]
                            for t in range(n):
                                out[count, a, t] = src[t]
                            out_len[count, a] = n
                        out_mv[count, 0] = i
                        out_mv[count, 1] = j
                        out_mv[count, 2] = s
                        out_mv[count, 3] = k1
                        out_mv[count, 4] = k2
                        count += 1
    return count, rejected


@njit(cache=True)
def score(row, rlen, n_gen, prio):
    """Heap priority of one state (``LENGTH`` or ``S20_MK2``; the latter at two generators)."""
    L = 0
    for r in range(len(rlen)):
        L += rlen[r]
    if prio == LENGTH:
        return float(L)
    mk = nx = ny = sx = sy = 0
    for r in range(len(rlen)):
        m = rlen[r]
        bx = by = 0
        for t in range(m):
            g = n_gen - (row[r, t] >> 1)
            if t == 0 or g != n_gen - (row[r, t - 1] >> 1):
                if g == 1:
                    bx += 1
                else:
                    by += 1
            if g == 1:
                sx += 1
            else:
                sy += 1
        if bx + by > 1 and (row[r, 0] >> 1) == (row[r, m - 1] >> 1):   # a run wraps the seam
            if n_gen - (row[r, 0] >> 1) == 1:
                bx -= 1
            else:
                by -= 1
        if bx > 0 and by > 0:
            mk = max(mk, max(bx, by))
        nx += bx
        ny += by
    mxv = sx / nx if nx else 0.0
    myv = sy / ny if ny else 0.0
    if nx == 0 or ny == 0:
        sv = myv if mxv == 0.0 else mxv
    else:
        sv = mxv if mxv < myv else myv
    acc = 0.0
    acc += 1.0 * L
    acc += 2.0 * mk
    acc += 20.0 * sv
    return acc


def children(rels, n_gen=2, cap=24, cyclic=True, priority="length"):
    """Python entry for other searches: the scored children of one canonical state.

    Returns ``(syms, lens, moves, scores, rejected)``; child ``c`` is
    ``decode(syms[c], lens[c], n_gen)``, reached by ``Move(*moves[c])``.
    """
    syms, lens = encode(rels, n_gen)
    mc, w = max_children(lens), max(child_width(lens), syms.shape[1])
    out = np.zeros((max(mc, 1), len(lens), w), dtype=np.uint8)
    out_len = np.zeros((max(mc, 1), len(lens)), dtype=np.int32)
    out_mv = np.zeros((max(mc, 1), 5), dtype=np.int32)
    count, rejected = expand(syms, lens, n_gen, -1 if cap is None else cap, cyclic, out, out_len, out_mv)
    pid = PRIORITY_IDS[priority]
    scores = np.array([score(out[c], out_len[c], n_gen, pid) for c in range(count)])
    return out[:count], out_len[:count], out_mv[:count], scores, rejected
