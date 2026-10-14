"""Numba kernels of the hybrid's higher-rank moves (backend ``"fast"`` of ``acx.hybrid.dynrank``): the pure Python,
compiled.

Every function here has the signature and the return value of its namesake in ``dynrank`` (tuples of int tuples,
event dicts, children in the same order), bit for bit: the search's tie-breaks depend on both. ``dynrank.backend``
hands them to the search (backend ``"fast"``), with the batched ``make_keys`` and ``children_lazy`` (cut products left
as arrays, ``Cuts``) the search uses in place of ``make_key`` one by one and ``children``.

A state goes to a kernel as one int64 array ``[n, len_1 .. len_n, letters ..]`` (``encode``). Words compare as Python
tuples (int order ``-2 < -1 < 1 < 2``, a proper prefix first), which is the order ``dynrank`` sorts and canonicalises in.
"""
from itertools import chain, repeat

import numpy as np
from numba import njit

from ..core.priority import length

I64 = np.int64


def encode(words):
    """``[n, len_1 .. len_n, letters ..]`` as int64: the layout every kernel here reads."""
    return np.array([len(words), *map(len, words), *chain.from_iterable(words)], I64)


# ---------------------------------------------------------------- words
@njit(cache=True)
def _parse(enc):
    """``(n, off, flat)``: word ``w`` is ``flat[off[w]:off[w + 1]]``."""
    n = enc[0]
    off = np.empty(n + 1, I64)
    off[0] = 0
    for w in range(n):
        off[w + 1] = off[w] + enc[1 + w]
    return n, off, enc[1 + n:]


@njit(cache=True)
def _wcmp(a, ao, al, b, bo, bl):
    """-1, 0 or 1: ``a[ao:ao+al]`` against ``b[bo:bo+bl]`` as Python tuples."""
    m = al if al < bl else bl
    for t in range(m):
        x = a[ao + t]
        y = b[bo + t]
        if x != y:
            return -1 if x < y else 1
    if al == bl:
        return 0
    return -1 if al < bl else 1


@njit(cache=True)
def _reduce(buf, lo, m):
    """``words.reduce`` of ``buf[lo:lo+m]`` in place; the result is ``buf[s:s+k]``, returned as ``(s, k)``."""
    n = 0
    for t in range(m):
        c = buf[lo + t]
        if n > 0 and buf[lo + n - 1] == -c:
            n -= 1
        else:
            buf[lo + n] = c
            n += 1
    s = 0
    if n > 1 and buf[lo] == -buf[lo + n - 1]:
        s = 1
        while 2 * s < n and buf[lo + s] == -buf[lo + n - 1 - s]:
            s += 1
        n -= 2 * s
    return lo + s, n


@njit(cache=True)
def _ring(w, lo, m, inv, t):
    """Letter ``t`` (``0 <= t < 2m``) of ``w[lo:lo+m]`` read as a ring, or of its inverse word."""
    if t >= m:
        t -= m
    if inv:
        return -w[lo + m - 1 - t]
    return w[lo + t]


@njit(cache=True)
def _least_start(w, lo, m, inv):
    """Start of the least rotation (int order) of the word or its inverse: the two-pointer minimum-rotation scan."""
    i, j, k = 0, 1, 0
    while i < m and j < m and k < m:
        x = _ring(w, lo, m, inv, i + k)
        y = _ring(w, lo, m, inv, j + k)
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


@njit(cache=True)
def _canon_to(w, lo, m, out, o):
    """``dynrank._least_rotation`` of the reduced ``w[lo:lo+m]`` (least rotation of it or its inverse) to ``out[o:]``;
    ``out`` must not overlap the word."""
    if m == 0:
        return
    a = _least_start(w, lo, m, False)
    b = _least_start(w, lo, m, True)
    inv = False
    for t in range(m):
        x = _ring(w, lo, m, False, a + t)
        y = _ring(w, lo, m, True, b + t)
        if x != y:
            inv = y < x
            break
    st = b if inv else a
    for t in range(m):
        out[o + t] = _ring(w, lo, m, inv, st + t)


@njit(cache=True)
def _dcanon_to(buf, lo, m, out, o):
    """``dynrank.dcanon`` of ``buf[lo:lo+m]`` (reduced in place, so ``buf`` is scratch) to ``out[o:]``; its length."""
    s, k = _reduce(buf, lo, m)
    _canon_to(buf, s, k, out, o)
    return k


@njit(cache=True)
def _sort_words(buf, st, ln, k, order):
    """``order[:k]``: the indices of the words ``buf[st[i]:st[i]+ln[i]]`` in Python tuple order (insertion sort)."""
    for a in range(k):
        order[a] = a
    for a in range(1, k):
        x = order[a]
        b = a - 1
        while b >= 0 and _wcmp(buf, st[order[b]], ln[order[b]], buf, st[x], ln[x]) > 0:
            order[b + 1] = order[b]
            b -= 1
        order[b + 1] = x


@njit(cache=True)
def _emit_sorted(buf, st, ln, k, order, let, p, lens, q):
    """Append the ``k`` words ``buf[st[i]:st[i]+ln[i]]`` sorted to ``let[p:]``/``lens[q:]``; the new ``(p, q)``."""
    _sort_words(buf, st, ln, k, order)
    for a in range(k):
        x = order[a]
        for t in range(ln[x]):
            let[p + t] = buf[st[x] + t]
        p += ln[x]
        lens[q] = ln[x]
        q += 1
    return p, q


@njit(cache=True)
def _pack(let, p, lens, q, head):
    """``[head .., lens[:q] .., let[:p] ..]`` as one array."""
    h = len(head)
    out = np.empty(h + q + p, I64)
    out[:h] = head
    out[h:h + q] = lens[:q]
    out[h + q:] = let[:p]
    return out


@njit(cache=True)
def dcanon_kernel(enc):
    """``dynrank.dcanon`` of the one word ``enc[1:]`` (``enc[0]`` its length)."""
    m = enc[0]
    buf = enc[1:1 + m].copy()
    out = np.empty(m, I64)
    k = _dcanon_to(buf, 0, m, out, 0)
    return out[:k]


@njit(cache=True)
def normalize_kernel(enc):
    """``dynrank.normalize`` of an encoded state: ``[lens .., letters ..]``."""
    n, off, flat = _parse(enc)
    buf = flat.copy()
    out = np.empty(len(flat), I64)
    st = np.empty(n, I64)
    ln = np.empty(n, I64)
    for w in range(n):
        st[w] = off[w]
        ln[w] = _dcanon_to(buf, off[w], off[w + 1] - off[w], out, off[w])
    let = np.empty(len(flat), I64)
    lens = np.empty(n, I64)
    order = np.empty(n, I64)
    p, q = _emit_sorted(out, st, ln, n, order, let, 0, lens, 0)
    return _pack(let, p, lens, q, np.empty(0, I64))


# ---------------------------------------------------------------- generator relabelling
@njit(cache=True)
def _isort(a, lo, k):
    """Sort ``a[lo:lo+k]`` in place (insertion sort, short rows)."""
    for x in range(lo + 1, lo + k):
        v = a[x]
        y = x - 1
        while y >= lo and a[y] > v:
            a[y + 1] = a[y]
            y -= 1
        a[y + 1] = v


@njit(cache=True)
def _sig_cmp(head, rows, nrow, g, h):
    """Compare the signatures ``(head[g], rows[g, :nrow[g]])`` and ``(head[h], ..)`` as Python tuples."""
    if head[g] != head[h]:
        return -1 if head[g] < head[h] else 1
    return _wcmp(rows[g], 0, nrow[g], rows[h], 0, nrow[h])


@njit(cache=True)
def _rank(head, rows, nrow, n, order, out):
    """``out[g]`` (``g`` in ``1..n``): the index of ``g``'s signature among the distinct ones, sorted; the count of
    distinct signatures."""
    for a in range(n):
        order[a] = a + 1
    for a in range(1, n):
        x = order[a]
        b = a - 1
        while b >= 0 and _sig_cmp(head, rows, nrow, order[b], x) > 0:
            order[b + 1] = order[b]
            b -= 1
        order[b + 1] = x
    c = 0
    for a in range(n):
        if a and _sig_cmp(head, rows, nrow, order[a - 1], order[a]) != 0:
            c += 1
        out[order[a]] = c
    return c + 1 if n else 0


@njit(cache=True)
def _initial_colour(flat, off, n, colour, order):
    """``dynrank._initial_colour``: per generator its count and the sorted ``(len(w), count in w)`` of the words it is in."""
    longest = 0
    for w in range(n):
        longest = max(longest, off[w + 1] - off[w])
    occ = np.zeros((n, n + 1), I64)
    for w in range(n):
        for t in range(off[w], off[w + 1]):
            occ[w, abs(flat[t])] += 1
    head = np.zeros(n + 1, I64)
    rows = np.zeros((n + 1, max(n, 1)), I64)
    nrow = np.zeros(n + 1, I64)
    for g in range(1, n + 1):
        for w in range(n):
            if occ[w, g]:
                rows[g, nrow[g]] = (off[w + 1] - off[w]) * (longest + 1) + occ[w, g]   # (len, count), lexicographic
                nrow[g] += 1
                head[g] += occ[w, g]
        _isort(rows[g], 0, nrow[g])
    _rank(head, rows, nrow, n, order, colour)


@njit(cache=True)
def _distinct(colour, n, mark):
    """How many distinct values ``colour[1..n]`` takes (``mark`` scratch, longer than the largest value)."""
    c = 0
    for g in range(1, n + 1):
        if not mark[colour[g]]:
            mark[colour[g]] = True
            c += 1
    for g in range(1, n + 1):
        mark[colour[g]] = False
    return c


@njit(cache=True)
def _refine(flat, off, n, colour, out, nb, deg, order, mark):
    """``dynrank._refine`` of ``colour`` into ``out``: colour refinement by sign-blind cyclic adjacency."""
    old = _distinct(colour, n, mark)
    cur = colour.copy()
    while True:
        deg[:] = 0
        for w in range(n):
            m = off[w + 1] - off[w]
            if m < 2:
                continue
            for k in range(m):
                a = abs(flat[off[w] + k])
                b = abs(flat[off[w] + (k + 1) % m])
                nb[a, deg[a]] = cur[b]
                deg[a] += 1
                nb[b, deg[b]] = cur[a]
                deg[b] += 1
        for g in range(1, n + 1):
            _isort(nb[g], 0, deg[g])
        new = _rank(cur, nb, deg, n, order, out)
        if new == old:
            return
        old = new
        cur[:] = out


@njit(cache=True)
def _leaf(flat, off, n, colour, perm, buf, canon, st, ln, order, let, lens):
    """The normalized relabelling of the words by ``perm[g] = colour[g] + 1`` into ``let``/``lens``; its letter count."""
    for g in range(1, n + 1):
        perm[g] = colour[g] + 1
    for t in range(off[n]):
        x = flat[t]
        buf[t] = perm[x] if x > 0 else -perm[-x]
    for w in range(n):
        st[w] = off[w]
        ln[w] = _dcanon_to(buf, off[w], off[w + 1] - off[w], canon, off[w])
    return _emit_sorted(canon, st, ln, n, order, let, 0, lens, 0)[0]


@njit(cache=True)
def _state_cmp(a, alens, b, blens, n):
    """Compare two states of ``n`` words (letters and lengths) as tuples of tuples."""
    pa = pb = 0
    for w in range(n):
        c = _wcmp(a, pa, alens[w], b, pb, blens[w])
        if c:
            return c
        pa += alens[w]
        pb += blens[w]
    return 0


@njit(cache=True)
def _relabel_into(flat, off, n, limit, out, o):
    """``dynrank.relabel_canonical`` of one state into ``out[o:]`` as ``[status, perm_1 .. perm_n, lens .., letters ..]``;
    ``status`` is -1 for a letter outside ``1..n`` and -2 past ``limit`` leaves (perm and lens 0, no letters), else the
    leaf count. Returns the end of the record."""
    T = off[n]
    out[o + 1:o + 1 + 2 * n] = 0
    for t in range(T):
        if flat[t] == 0 or abs(flat[t]) > n:
            out[o] = -1
            return o + 1 + 2 * n
    order = np.empty(max(n, 1), I64)
    colour = np.zeros(n + 1, I64)
    _initial_colour(flat, off, n, colour, order)
    nb = np.empty((n + 1, max(2 * T, 1)), I64)
    deg = np.zeros(n + 1, I64)
    mark = np.zeros(2 * n + 2, np.bool_)
    count = np.zeros(2 * n + 2, I64)
    stk = np.empty((n + 1, n + 1), I64)          # the refined colouring at each depth of the search
    stk_c = np.empty(n + 1, I64)                 # the colour class split at that depth
    stk_g = np.empty(n + 1, I64)                 # the next member of that class to individualise
    work = np.empty(n + 1, I64)
    ref = np.empty(n + 1, I64)
    perm = np.zeros(n + 1, I64)
    best_perm = np.zeros(n + 1, I64)
    buf = np.empty(max(T, 1), I64)
    canon = np.empty(max(T, 1), I64)
    st = np.empty(max(n, 1), I64)
    ln = np.empty(max(n, 1), I64)
    let = np.empty(max(T, 1), I64)
    lens = np.empty(max(n, 1), I64)
    best = np.empty(max(T, 1), I64)
    best_lens = np.empty(max(n, 1), I64)
    leaves = best_p = 0
    depth = 0
    _refine(flat, off, n, colour, ref, nb, deg, order, mark)
    while True:
        # ``ref`` is a refined colouring: a leaf if discrete, else a new level splitting its least multi-member class
        for g in range(1, n + 1):
            count[ref[g]] += 1
        split = -1
        for c in range(n):
            if count[c] > 1:
                split = c
                break
        for g in range(1, n + 1):
            count[ref[g]] = 0
        if split < 0:
            leaves += 1
            if leaves > limit:
                out[o] = -2
                return o + 1 + 2 * n
            p = _leaf(flat, off, n, ref, perm, buf, canon, st, ln, order, let, lens)
            if leaves == 1 or _state_cmp(let, lens, best, best_lens, n) < 0:
                best_p = p
                best[:p] = let[:p]
                best_lens[:n] = lens[:n]
                best_perm[:] = perm
        else:
            stk[depth, :] = ref
            stk_c[depth] = split
            stk_g[depth] = 1
            depth += 1
        found = False
        while depth > 0 and not found:
            top = depth - 1
            c = stk_c[top]
            g = stk_g[top]
            while g <= n and stk[top, g] != c:
                g += 1
            if g > n:
                depth -= 1
                continue
            stk_g[top] = g + 1
            for h in range(1, n + 1):
                ch = stk[top, h]
                work[h] = 2 * ch + (1 if (ch == c and h != g) else 0)
            _refine(flat, off, n, work, ref, nb, deg, order, mark)
            found = True
        if not found:
            break
    out[o] = leaves
    out[o + 1:o + 1 + n] = best_perm[1:]
    out[o + 1 + n:o + 1 + 2 * n] = best_lens[:n]
    out[o + 1 + 2 * n:o + 1 + 2 * n + best_p] = best[:best_p]
    return o + 1 + 2 * n + best_p


@njit(cache=True)
def relabel_kernel(enc, limit):
    """``dynrank.relabel_canonical`` of an encoded state, as ``_relabel_into`` writes it."""
    n, off, flat = _parse(enc)
    out = np.empty(1 + 2 * n + off[n], I64)
    return out[:_relabel_into(flat, off, n, limit, out, 0)]


@njit(cache=True)
def relabel_batch_kernel(encs, limit):
    """``relabel_kernel`` of each of the states ``encs = [count, state, state, ..]`` (each as ``encode`` writes it), the
    records one after another."""
    size = 0
    pos = 1
    for _ in range(encs[0]):
        n = encs[pos]
        T = 0
        for w in range(n):
            T += encs[pos + 1 + w]
        size += 1 + 2 * n + T
        pos += 1 + n + T
    out = np.empty(size, I64)
    o = 0
    pos = 1
    for _ in range(encs[0]):
        n, off, flat = _parse(encs[pos:])
        T = off[n]
        o = _relabel_into(flat[:T], off, n, limit, out, o)
        pos += 1 + n + T
    return out[:o]


# ---------------------------------------------------------------- products
@njit(cache=True)
def products_kernel(enc, cap):
    """``dynrank.products``: ``(meta, offs, letters, cut i, cut total, cut size, cut offs, cut letters, sorted)``. Child
    ``c`` is ``meta[6c:6c+6] = (i, j, sign, k1, k2, pos)`` with the canonical product ``letters[offs[c]:offs[c+1]]``,
    ``pos`` its place among the other words (when ``sorted``, the words are in order and that place gives the child's
    sorted key); a cut one ``(i, total, size)`` and its reduced product. ``cap`` -1 is no cap."""
    n, off, flat = _parse(enc)
    T = off[n]
    longest = 0
    for w in range(n):
        longest = max(longest, off[w + 1] - off[w])
    ordered = True
    for w in range(1, n):
        if _wcmp(flat, off[w - 1], off[w] - off[w - 1], flat, off[w], off[w + 1] - off[w]) > 0:
            ordered = False
    grp = np.empty(n, I64)                       # the first relator equal to each: a key is (its value, product)
    for i in range(n):
        grp[i] = i
        for a in range(i):
            if _wcmp(flat, off[a], off[a + 1] - off[a], flat, off[i], off[i + 1] - off[i]) == 0:
                grp[i] = a
                break
    C = 0
    for i in range(n):
        for j in range(n):
            if i != j:
                C += 2 * (off[i + 1] - off[i]) * (off[j + 1] - off[j])
    W = 2 * longest + 1
    meta = np.empty(6 * C, I64)                  # preallocated: arrays reassigned in the loop run twice as slow
    offs = np.zeros(C + 1, I64)
    plet = np.empty(C * W + 1, I64)
    ci = np.empty(C, I64)
    ctot = np.empty(C, I64)
    csize = np.empty(C, I64)
    coffs = np.zeros(C + 1, I64)
    clet = np.empty(C * W + 1, I64)
    size = 4
    while size < 2 * C + 2:
        size *= 2
    table = np.full(size, -1, I64)
    buf = np.empty(W, I64)
    can = np.empty(W, I64)
    kept = cut = 0
    for i in range(n):
        ti, lt = off[i], off[i + 1] - off[i]
        if lt == 0:
            continue
        for j in range(n):
            tj, lb = off[j], off[j + 1] - off[j]
            if i == j or lb == 0:
                continue
            for sign in (1, -1):
                for k1 in range(lt):
                    for k2 in range(lb):
                        for t in range(lt):
                            buf[t] = flat[ti + (k1 + t) % lt]
                        for t in range(lb):
                            q = (k2 + t) % lb
                            buf[lt + t] = flat[tj + q] if sign == 1 else -flat[tj + lb - 1 - q]
                        s, m = _reduce(buf, 0, lt + lb)
                        if m == 0:
                            continue
                        if cap >= 0 and m > cap:
                            back = False
                            if m == lt:
                                _canon_to(buf, s, m, can, 0)
                                back = _wcmp(can, 0, m, flat, ti, lt) == 0
                            if not back:
                                o = coffs[cut]
                                ci[cut] = i
                                ctot[cut] = T - lt + m
                                csize[cut] = m
                                for t in range(m):
                                    clet[o + t] = buf[s + t]
                                coffs[cut + 1] = o + m
                                cut += 1
                            continue
                        _canon_to(buf, s, m, can, 0)
                        if m == lt and _wcmp(can, 0, m, flat, ti, lt) == 0:
                            continue
                        h = grp[i] * 1000003 + m
                        for t in range(m):
                            h = h * 31 + can[t] + 17
                        slot = h & (size - 1)
                        dup = False
                        while table[slot] >= 0:
                            c = table[slot]
                            if grp[meta[6 * c]] == grp[i] and _wcmp(plet, offs[c], offs[c + 1] - offs[c], can, 0, m) == 0:
                                dup = True
                                break
                            slot = (slot + 1) & (size - 1)
                        if dup:
                            continue
                        table[slot] = kept
                        pos = 0
                        for w in range(n):
                            if w != i and _wcmp(flat, off[w], off[w + 1] - off[w], can, 0, m) < 0:
                                pos += 1
                        o = offs[kept]
                        meta[6 * kept] = i
                        meta[6 * kept + 1] = j
                        meta[6 * kept + 2] = sign
                        meta[6 * kept + 3] = k1
                        meta[6 * kept + 4] = k2
                        meta[6 * kept + 5] = pos
                        for t in range(m):
                            plet[o + t] = can[t]
                        offs[kept + 1] = o + m
                        kept += 1
    return (meta[:6 * kept], offs[:kept + 1], plet[:offs[kept]], ci[:cut], ctot[:cut], csize[:cut], coffs[:cut + 1],
            clet[:coffs[cut]], ordered)


# ---------------------------------------------------------------- definitions
@njit(cache=True)
def _opt_less(la, fa, na, lb, fb, nb, tl, tf, tn):
    """Is the option ``(fa,) + shortest[na]`` (length ``la``) before ``(fb,) + shortest[nb]`` by ``(len, tuple)``?"""
    if la != lb:
        return la < lb
    if fa != fb:
        return fa < fb
    for _ in range(la - 1):
        if na == nb:
            return False
        if tf[na] != tf[nb]:
            return tf[na] < tf[nb]
        na = tn[na]
        nb = tn[nb]
    return False


@njit(cache=True)
def _tokenize(u, L, d0, d1, e0, e1, h, tl, tf, tn):
    """``digrams.tokenize`` of the linear word ``u[:L]`` as a chain: ``shortest[i]`` is ``tf[i]`` then ``shortest[tn[i]]``,
    ``tl[i]`` letters; the result is ``shortest[0]``."""
    tl[L] = 0
    for i in range(L - 1, -1, -1):
        bl, bf, bn = 1 + tl[i + 1], u[i], i + 1
        if i + 1 < L and u[i] == d0 and u[i + 1] == d1:
            if _opt_less(1 + tl[i + 2], h, i + 2, bl, bf, bn, tl, tf, tn):
                bl, bf, bn = 1 + tl[i + 2], h, i + 2
        if i + 1 < L and u[i] == e0 and u[i + 1] == e1:
            if _opt_less(1 + tl[i + 2], -h, i + 2, bl, bf, bn, tl, tf, tn):
                bl, bf, bn = 1 + tl[i + 2], -h, i + 2
        tl[i] = bl
        tf[i] = bf
        tn[i] = bn


@njit(cache=True)
def _digram(a, b):
    """``digrams.digram``: the lesser of ``(a, b)`` and its inverse ``(-b, -a)``."""
    if a < -b or (a == -b and b <= -a):
        return a, b
    return -b, -a


@njit(cache=True)
def _digram_list(flat, off, n):
    """The cyclic digrams in order of first occurrence and their counts (``digrams.digram_counts``)."""
    T = off[n]
    N = 1
    for t in range(T):
        N = max(N, abs(flat[t]))
    R = 2 * N + 1
    cnt = np.zeros(R * R, I64)
    first = np.empty(max(T, 1), I64)
    nd = 0
    for w in range(n):
        m = off[w + 1] - off[w]
        if m < 2:
            continue
        for k in range(m):
            a, b = _digram(flat[off[w] + k], flat[off[w] + (k + 1) % m])
            x = (a + N) * R + (b + N)
            if cnt[x] == 0:
                first[nd] = x
                nd += 1
            cnt[x] += 1
    ds = np.empty((nd, 3), I64)
    for k in range(nd):
        ds[k, 0] = first[k] // R - N
        ds[k, 1] = first[k] % R - N
        ds[k, 2] = cnt[first[k]]
    return ds


@njit(cache=True)
def most_uses_kernel(enc):
    """``dynrank.most_uses``: the largest count of ``_digram_list`` (0 if there is no digram)."""
    n, off, flat = _parse(enc)
    ds = _digram_list(flat, off, n)
    best = 0
    for k in range(len(ds)):
        best = max(best, ds[k, 2])
    return best


@njit(cache=True)
def defines_kernel(enc, min_uses):
    """``dynrank.defines``: rows ``(d0, d1, uses)``, the ``n`` templates of each, the normalized child of each
    (``n + 1`` words), as ``(meta, template lens, template letters, child lens, child letters)``."""
    n, off, flat = _parse(enc)
    T = off[n]
    h = n + 1
    longest = 0
    for w in range(n):
        longest = max(longest, off[w + 1] - off[w])
    ds = _digram_list(flat, off, n)
    nd = len(ds)
    meta = np.empty((nd, 3), I64)
    tlet = np.empty(max(nd * T, 1), I64)
    tlens = np.empty(max(nd * n, 1), I64)
    clet = np.empty(max(nd * (T + 3), 1), I64)
    clens = np.empty(max(nd * (n + 1), 1), I64)
    u = np.empty(longest + 1, I64)
    tl = np.empty(longest + 2, I64)
    tf = np.empty(longest + 2, I64)
    tn = np.empty(longest + 2, I64)
    cand = np.empty(longest + 1, I64)
    raw = np.empty(T + 3, I64)                   # the child before normalizing: (-h, d0, d1), then the templates
    st = np.empty(n + 1, I64)
    ln = np.empty(n + 1, I64)
    canon = np.empty(T + 3, I64)
    order = np.empty(n + 1, I64)
    kept = tp = tq = cp = cq = 0
    for k in range(nd):
        d0, d1 = ds[k, 0], ds[k, 1]
        if ds[k, 2] < min_uses:
            continue
        e0, e1 = -d1, -d0
        raw[0], raw[1], raw[2] = -h, d0, d1
        st[0], ln[0] = 0, 3
        p = 3
        uses = 0
        for w in range(n):
            m = off[w + 1] - off[w]
            st[w + 1] = p
            if m < 2:
                for t in range(m):
                    raw[p + t] = flat[off[w] + t]
                    if abs(raw[p + t]) == h:
                        uses += 1
                ln[w + 1] = m
                p += m
                continue
            best = -1
            for r in range(m):
                for t in range(m):
                    u[t] = flat[off[w] + (r + t) % m]
                _tokenize(u, m, d0, d1, e0, e1, h, tl, tf, tn)
                L = tl[0]
                x = 0
                for t in range(L):
                    cand[t] = tf[x]
                    x = tn[x]
                if best < 0 or L < best or (L == best and _wcmp(cand, 0, L, raw, p, best) < 0):
                    best = L
                    for t in range(L):
                        raw[p + t] = cand[t]
            ln[w + 1] = best
            for t in range(best):
                if abs(raw[p + t]) == h:
                    uses += 1
            p += best
        if uses < min_uses:
            continue
        meta[kept, 0], meta[kept, 1], meta[kept, 2] = d0, d1, uses
        for w in range(n):
            for t in range(ln[w + 1]):
                tlet[tp + t] = raw[st[w + 1] + t]
            tp += ln[w + 1]
            tlens[tq] = ln[w + 1]
            tq += 1
        for w in range(n + 1):
            ln[w] = _dcanon_to(raw, st[w], ln[w], canon, st[w])
        cp, cq = _emit_sorted(canon, st, ln, n + 1, order, clet, cp, clens, cq)
        kept += 1
    return meta[:kept], tlens[:tq], tlet[:tp], clens[:cq], clet[:cp]


# ---------------------------------------------------------------- eliminations and transvections
@njit(cache=True)
def eliminations_kernel(enc):
    """``dynrank.eliminations``: rows ``(i, g)``, the image of each, its normalized child (``n - 1`` words), as
    ``(meta, image lens, image letters, child lens, child letters)``."""
    n, off, flat = _parse(enc)
    T = off[n]
    longest = 0
    for w in range(n):
        longest = max(longest, off[w + 1] - off[w])
    big = T * max(longest, 1) + 1                # a child's letters before reduction, at most
    meta = np.empty((max(T, 1), 2), I64)
    ilet = np.empty(max(T * longest, 1), I64)
    ilens = np.empty(max(T, 1), I64)
    clet = np.empty(max(T * big, 1), I64)
    clens = np.empty(max(T * n, 1), I64)
    image = np.empty(max(longest, 1), I64)
    raw = np.empty(big, I64)
    canon = np.empty(big, I64)
    st = np.empty(max(n, 1), I64)
    ln = np.empty(max(n, 1), I64)
    order = np.empty(max(n, 1), I64)
    kept = ip = cp = cq = 0
    for i in range(n):
        ri, m = off[i], off[i + 1] - off[i]
        for k in range(m):
            g = abs(flat[ri + k])
            c = 0
            for t in range(m):
                if abs(flat[ri + t]) == g:
                    c += 1
            if c != 1:
                continue
            L = m - 1                            # rot = r[k:] + r[:k]; image = rot[1:], inverted when rot[0] > 0
            for t in range(L):
                image[t] = flat[ri + (k + 1 + t) % m]
            if flat[ri + k] > 0:
                for t in range(L // 2):
                    image[t], image[L - 1 - t] = -image[L - 1 - t], -image[t]
                if L % 2:
                    image[L // 2] = -image[L // 2]
            p = 0
            nw = 0
            for w in range(n):
                if w == i:
                    continue
                st[nw] = p
                for t in range(off[w], off[w + 1]):
                    x = flat[t]
                    if x == g:
                        for y in range(L):
                            raw[p] = image[y]
                            p += 1
                    elif x == -g:
                        for y in range(L - 1, -1, -1):
                            raw[p] = -image[y]
                            p += 1
                    else:
                        raw[p] = x
                        p += 1
                for t in range(st[nw], p):       # renumber: the generators above g move down by one
                    if raw[t] > g:
                        raw[t] -= 1
                    elif raw[t] < -g:
                        raw[t] += 1
                ln[nw] = p - st[nw]
                nw += 1
            for w in range(nw):
                ln[w] = _dcanon_to(raw, st[w], ln[w], canon, st[w])
            cp, cq = _emit_sorted(canon, st, ln, nw, order, clet, cp, clens, cq)
            meta[kept, 0], meta[kept, 1] = i, g
            for t in range(L):
                ilet[ip + t] = image[t]
            ip += L
            ilens[kept] = L
            kept += 1
    return meta[:kept], ilens[:kept], ilet[:ip], clens[:cq], clet[:cp]


@njit(cache=True)
def nielsen_kernel(enc):
    """``dynrank.nielsen_children``: the normalized children (``n`` words each) of ``x_i -> x_i x_j^s`` for ``i``, ``j``,
    ``s`` in that order, as ``(lens, letters)``."""
    n, off, flat = _parse(enc)
    T = off[n]
    count = 2 * n * (n - 1)
    clet = np.empty(max(count * 2 * T, 1), I64)
    clens = np.empty(max(count * n, 1), I64)
    raw = np.empty(2 * T + 1, I64)
    canon = np.empty(2 * T + 1, I64)
    st = np.empty(max(n, 1), I64)
    ln = np.empty(max(n, 1), I64)
    order = np.empty(max(n, 1), I64)
    cp = cq = 0
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            if i == j:
                continue
            for s in (1, -1):
                p = 0
                for w in range(n):
                    st[w] = p
                    for t in range(off[w], off[w + 1]):
                        x = flat[t]
                        if x == i:
                            raw[p] = i
                            raw[p + 1] = s * j
                            p += 2
                        elif x == -i:
                            raw[p] = -s * j
                            raw[p + 1] = -i
                            p += 2
                        else:
                            raw[p] = x
                            p += 1
                    ln[w] = p - st[w]
                for w in range(n):
                    ln[w] = _dcanon_to(raw, st[w], ln[w], canon, st[w])
                cp, cq = _emit_sorted(canon, st, ln, n, order, clet, cp, clens, cq)
    return clens[:cq], clet[:cp]


# ---------------------------------------------------------------- the Python entries (``dynrank``'s signatures)
def _words(lens, let):
    """The words of ``lens``/``let`` as int tuples."""
    L, out, p = let.tolist(), [], 0
    for m in lens.tolist():
        out.append(tuple(L[p:p + m]))
        p += m
    return out


def _states(lens, let, k):
    """The states of ``k`` words each in ``lens``/``let``."""
    ws = _words(lens, let)
    return [tuple(ws[c:c + k]) for c in range(0, len(ws), k)]


def dcanon(w):
    """``dynrank.dcanon``."""
    w = tuple(w)
    return tuple(dcanon_kernel(np.array((len(w),) + w, I64)).tolist())


def normalize(words):
    """``dynrank.normalize``."""
    words = tuple(words)
    n = len(words)
    out = normalize_kernel(encode(words)).tolist()
    canon, p = [], n
    for m in out[:n]:
        canon.append(tuple(out[p:p + m]))
        p += m
    return tuple(canon)


def relabel_canonical(words, limit=20000):
    """``dynrank.relabel_canonical``."""
    n = len(words)
    out = relabel_kernel(encode(words), limit).tolist()
    if out[0] == -1:
        raise ValueError("letters must lie in 1..rank")
    if out[0] == -2:
        raise RuntimeError("relabel_canonical leaf limit exceeded")
    canon, p = [], 1 + 2 * n
    for m in out[1 + n:1 + 2 * n]:
        canon.append(tuple(out[p:p + m]))
        p += m
    return tuple(canon), dict(zip(range(1, n + 1), out[1:1 + n])), dict.fromkeys(range(1, n + 1), 1)


def make_key(words):
    """``dynrank.make_key``."""
    canon, perm, signs = relabel_canonical(words)
    return canon, {"perm": perm, "signs": signs}


def make_keys(states):
    """``make_key`` of each state in one kernel call; None for a state on which ``make_key`` raises (the caller calls
    it there, so the error comes where it would have)."""
    if not states:
        return []
    enc = np.array([len(states), *chain.from_iterable(chain((len(w),), map(len, w), chain.from_iterable(w))
                                                      for w in states)], I64)
    out = relabel_batch_kernel(enc, 20000).tolist()
    keys, o = [], 0
    for w in states:
        n = len(w)
        p = o + 1 + 2 * n
        if out[o] < 0:
            keys.append(None)
            o = p
            continue
        canon = []
        for m in out[o + 1 + n:p]:
            canon.append(tuple(out[p:p + m]))
            p += m
        keys.append((tuple(canon), {"perm": dict(zip(range(1, n + 1), out[o + 1:o + 1 + n])),
                                    "signs": dict.fromkeys(range(1, n + 1), 1)}))
        o = p
    return keys


def _products(words, enc, cap, lazy=False):
    """``dynrank.products``; with ``lazy`` the cut ones as ``Cuts`` (its ``elims`` empty)."""
    meta, offs, let, ci, ctot, csize, coffs, clet, ordered = products_kernel(enc, -1 if cap is None else cap)
    n, L, O, M = len(words), let.tolist(), offs.tolist(), meta.tolist()
    out = []
    for c in range(len(O) - 1):
        i, j, sign, k1, k2, pos = M[6 * c:6 * c + 6]
        p = tuple(L[O[c]:O[c + 1]])
        if ordered:
            rest = words[:i] + words[i + 1:]
            key = rest[:pos] + (p,) + rest[pos:]
        else:
            key = tuple(sorted(words[:i] + (p,) + words[i + 1:]))
        out.append((key, {"kind": "product", "i": i, "j": j, "sign": sign, "k1": k1, "k2": k2, "result": p}))
    if lazy:
        return out, Cuts(n, ci, ctot, csize, coffs, clet, [])
    L, O = clet.tolist(), coffs.tolist()
    words_cut = zip(ci.tolist(), map(tuple, map(L.__getitem__, map(slice, O, O[1:]))))
    return out, list(zip(ctot.tolist(), csize.tolist(), repeat(n), words_cut))


class Cuts:
    """What ``dynrank.children`` cuts, the products left as the kernel's arrays: the items ``(total, size, rank,
    (i, product))`` of the cut products, then ``elims``, the cut eliminations as items. The search reads it through
    ``capwatch.lazy_cut_entries``, which builds an item only when a pool bar reaches it (one in a hundred on a hard row)."""

    __slots__ = ("rank", "i", "total", "size", "offs", "letters", "elims")

    def __init__(self, rank, i, total, size, offs, letters, elims):
        self.rank, self.i, self.total, self.size, self.offs, self.letters, self.elims = (
            rank, i, total, size, offs, letters, elims)

    def __len__(self):
        return len(self.total) + len(self.elims)

    def products(self):
        """How many cut products come first."""
        return len(self.total)

    def item(self, k):
        """Item ``k`` (the products, then ``elims``)."""
        if k >= len(self.total):
            return self.elims[k - len(self.total)]
        product = tuple(self.letters[self.offs[k]:self.offs[k + 1]].tolist())
        return int(self.total[k]), int(self.size[k]), self.rank, (int(self.i[k]), product)

    def items(self):
        """The list ``dynrank.children`` gives."""
        return [self.item(k) for k in range(len(self))]

    def min_total(self):
        """The least total of an item."""
        least = min((t[0] for t in self.elims), default=None)
        if len(self.total):
            low = int(self.total.min())
            least = low if least is None or low < least else least
        return least

    def above(self, rank):
        """The items of rank above ``rank`` (``rank`` below the products')."""
        return Cuts(self.rank, self.i, self.total, self.size, self.offs, self.letters,
                    [t for t in self.elims if t[2] > rank])


def products(words, cap):
    """``dynrank.products``."""
    return _products(words, encode(words), cap)


def _defines(words, enc, min_uses):
    meta, tlens, tlet, clens, clet = defines_kernel(enc, min_uses)
    n, h = len(words), len(words) + 1
    templates = _states(tlens, tlet, n) if n else [()] * len(meta)
    kids = _states(clens, clet, n + 1)
    return [(kid, {"kind": "define", "digram": (d0, d1), "h": h, "uses": uses, "templates": t})
            for (d0, d1, uses), t, kid in zip(meta.tolist(), templates, kids)]


def defines(words, min_uses=2):
    """``dynrank.defines``."""
    return _defines(words, encode(words), min_uses)


def _eliminations(words, enc):
    meta, ilens, ilet, clens, clet = eliminations_kernel(enc)
    n = len(words)
    kids = _states(clens, clet, n - 1) if n > 1 else [()] * len(meta)
    return [(kid, {"kind": "eliminate", "i": i, "g": g, "image": image})
            for (i, g), image, kid in zip(meta.tolist(), _words(ilens, ilet), kids)]


def eliminations(words):
    """``dynrank.eliminations``."""
    return _eliminations(words, encode(words))


def _nielsen(words, enc):
    n = len(words)
    if n < 2:
        return []
    kids = _states(*nielsen_kernel(enc), n)
    events = [{"kind": "nielsen", "i": i, "j": j, "sign": s}
              for i in range(1, n + 1) for j in range(1, n + 1) if i != j for s in (1, -1)]
    return list(zip(kids, events))


def nielsen_children(words):
    """``dynrank.nielsen_children``."""
    return _nielsen(words, encode(words))


def children(words, cap, ceiling, min_uses=2, lazy=False):
    """``dynrank.children``; with ``lazy`` (and rank three or more) ``cut`` is a ``Cuts``, the same items."""
    lazy = lazy and len(words) > 2
    enc = encode(words)
    prods, cut = _products(words, enc, cap, lazy)
    kept, cut_elims = [], cut.elims if lazy else cut
    for k, e in _eliminations(words, enc):
        longest = max(map(len, k), default=0)
        if cap is None or longest <= cap:
            kept.append((k, e))
        else:
            cut_elims.append((length(k), longest, len(k), k))
    out, over = [], []
    for k, e in prods + _defines(words, enc, min_uses) + kept + _nielsen(words, enc):
        total = length(k)
        if total <= ceiling:
            out.append((k, e))
        else:
            over.append((total, total, len(k), k))
    return out, cut, over


def children_lazy(words, cap, ceiling, min_uses=2):
    """``children`` with the cut products left as arrays (``Cuts``) at rank three or more."""
    return children(words, cap, ceiling, min_uses, lazy=True)


def most_uses(words):
    """``dynrank.most_uses``."""
    return int(most_uses_kernel(encode(words)))


_WARM = ((1, 2, -1, -2), (1, 1, 2), (2, 3, -2, -3, 3))      # rank three: every kernel above has work on it


_warmed = False


def warm():
    """Load every kernel here (from numba's cache, or compile it) once per process, so that the first search to
    need one is not charged for it (about 0.3 s with the cache)."""
    global _warmed
    if _warmed:
        return
    children_lazy(_WARM, 6, 30)
    make_keys([_WARM])
    make_key(_WARM)
    dcanon(_WARM[0])
    normalize(_WARM)
    most_uses(_WARM)
    _warmed = True
