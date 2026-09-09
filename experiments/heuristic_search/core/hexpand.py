"""``hcompact``'s expansion kernel: ``expand_node_topk_nj``'s children, minus the
duplicates a cut shift produces, canonicalised on 2-bit-packed words.

Only ``hcompact`` calls this. ``expand_node_topk_nj`` / ``expand_and_score_nj``
in ``greedy_baseline`` / ``hfast`` are untouched: the Python oracle
(``hsolve``), ``search_fast`` and the other engines keep them, and
``expand_node_topk_nj`` is also this module's reference (``tests/test_hexpand.py``
pins every child here against it on real popped states).

WHAT IS DIFFERENT, AND WHY EACH IS BIT-IDENTICAL FOR THE SEARCH
===============================================================

1. The cut-shift skip (pass 1). For one (target, sign) block write
   ``A = roll(r_i, k1)``, ``B = roll(o, k2)`` and the raw child ``W = A.B``.
   The move ``(k1 + 1, k2 - 1)`` (indices mod the lengths) builds
   ``W' = a.A[:-1] . B[1:].b`` with ``a = A[-1]``, ``b = B[0]``, because
   ``roll(r_i, k1 + 1) = a.A[:-1]`` and ``roll(o, k2 - 1) = B[1:].b``. When
   the seam of ``W`` cancels (``a = b^-1``, the condition every emitted child
   already satisfies) ``W = A[:-1].B[1:]`` as a group element and
   ``W' = a.(A[:-1].B[1:]).a^-1`` -- a CONJUGATE of ``W``. Two words are
   conjugate in a free group iff their cyclically reduced forms are cyclic
   permutations of each other; ``reduce_relator_nj(.., cyclic=True)``
   returns the cyclically reduced form of ANY input word (free reduction,
   then the trim of inverse pairs off the two ends until they no longer
   cancel or one symbol is left), and ``canonical_relator_nj`` (least
   rotation over the word and its inverse) is invariant under cyclic
   permutation. So the child of ``(k1 + 1, k2 - 1)`` is the child of
   ``(k1, k2)``: the same relator, and the same untouched partner. Read
   backwards: the child of ``(k1, k2)`` with ``k1 >= 1`` equals the child of
   its predecessor ``(k1 - 1, k2 + 1 mod n_o)`` in the same block whenever
   that predecessor's seam cancels, i.e. whenever ``A[0]`` and ``B[-1]`` are
   inverse -- and that condition is precisely the predecessor's own seam
   test (``_ridx(k1 - 1, n_i - 1, n_i) = _ridx(k1, 0, n_i)`` and
   ``_ridx(k2 + 1 mod n_o, 0, n_o) = _ridx(k2, n_o - 1, n_o)``).

   WHEN THE SKIP IS TAKEN. Leaving ``(k1, k2)`` out is exact only if the
   predecessor's child is actually in this pop's candidate stream AHEAD of
   it, so that its lookup or insert has already happened when this child's
   turn would come and the engine would discard this one as seen. The kernel
   does not infer that from the proof: it keeps, per (target, sign) block, a
   bitmap over ``(k1, k2)`` that is set when a child is emitted and when a
   child is skipped as a repeat, and skips ``(k1, k2)`` only when
   ``k1 >= 1`` and the predecessor's bit is set. A set bit means the
   predecessor passed its seam test (the conjugacy condition above) and is
   in the stream: emitted, or itself a skipped repeat of a child that is,
   by induction on ``k1`` (the first member of every chain has ``k1 = 0``
   or an unset predecessor bit, and is emitted if it passes the cap). The
   predecessor has the smaller ``k1``, so it precedes ``(k1, k2)`` in the
   ``target -> sign -> k1 -> k2`` enumeration, which the loops keep exactly.
   Whether the reference kernel would have emitted ``(k1, k2)`` or dropped
   it on the cap does not matter: emitted, it is a repeat the engine's
   table discards; dropped, it is absent either way. Hence the same set of
   states, the same discovery order, the same stored (parent, move) -- those
   are the first discovery's -- and the same scores. (The filters are in
   fact monotone along a chain: the predecessor's seam test IS the
   criterion, and the cyclically reduced length is a conjugacy-class
   invariant, so the cap decision is shared; that is why the bitmap and the
   bare criterion skip the same children, and the bitmap is kept because it
   makes the argument unconditional.) The skip holds only for
   ``cyclic=True`` (with linear reduction ``W'`` is two symbols longer than
   ``W``), so it is guarded on ``cyclic``; and only at ``topk = 0`` (a top-k
   selection over a list with a repeat removed is a different selection),
   which is the only way ``hcompact`` calls the kernel. Measured on
   ``aca_47`` at 300k pops it removes 48.9% of the children before any
   per-child work is spent on them (``perf_lab/EXPAND_SPLIT.md``).

2. Packed canonicalisation (pass 2). ``canonical_relator_nj`` is the least
   rotation of the word and of its inverse under the symbol order
   ``Y < y < X < x`` (``is_less_than``), then the smaller of the two
   (``lex_cmp_array``, which returns ``r_min`` unless ``r_min >= inv_min``;
   on equality the two are the same string). The least rotation of a word is
   a unique STRING, so any correct algorithm returns what Booth's returns.
   Here a word of ``m <= 32`` symbols is packed into one ``uint64`` as
   ``v(t) = 2*a0 + a1`` (``Y=0, y=1, X=2, x=3`` -- monotone in the order
   above) most-significant symbol first, so that for two words of the same
   length numeric order IS lexicographic order, and rotation ``k`` is
   ``((V << 2k) | (V >> (2m - 2k))) & mask``: the least rotation is a min
   over ``m`` shift-or-compare steps instead of Booth's failure-function walk
   over ``2m`` doubled symbols, twice. Words of ``33..64`` symbols use the
   same argument on a (hi, lo) pair of ``uint64`` read out of the packed
   doubled word; longer words (only reachable at ``cap > 64``) fall back to
   the Booth scratch path verbatim. The inverse's packed value is built in
   the same loop (symbol ``t`` of the word is symbol ``m-1-t`` of the
   inverse with its inversion bit flipped, i.e. ``v ^ 1`` at bit ``2t``).
   The pair normalisation (``canonical_pair_nj``'s swap on
   ``len(c1) > len(c2) or (equal and c1 >= c2)``) compares the same packed
   values, and the codes ``X=1, Y=2, x=3, y=4`` are read straight out of the
   chosen packed word. ``tests/test_hexpand.py`` pins the packed canonical
   form against ``canonical_relator_nj`` exhaustively on every word of up to
   8 symbols and on random words up to 64 (and past 64 for the fallback).

Everything else -- the seam test, ``_seam_reduced_len_nj``, the raw word by
``_ridx``, ``_reduce_into``, the hoisted inverses and the hoisted canonical
form of the untouched relator -- is the live kernel's code, imported.
"""
import os
import sys

import numpy as np
from numba import njit

_HERE = os.path.dirname(os.path.abspath(__file__))
_d = _HERE
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

from experiments.search.greedy_baseline import (                    # noqa: E402
    inverse_relator_nj, reduce_relator_nj, canonical_relator_nj, lex_cmp_array,
    _ridx, _inv_at, _seam_reduced_len_nj, _reduce_into, _canon_into,
)
from experiments.heuristic_search.core.hfast import _feats_nj, N_FEAT  # noqa: E402


# ---------------------------------------------------------------------------
# packed words: v = 2*a0 + a1 per symbol, most significant first.
# ---------------------------------------------------------------------------
_U0 = np.uint64(0)
_U1 = np.uint64(1)
_U2 = np.uint64(2)
_U3 = np.uint64(3)
_U64 = np.uint64(64)
_UALL = np.uint64(0xFFFFFFFFFFFFFFFF)


@njit(inline='always')
def _vsym(rel, t):
    """Order value of symbol ``t``: ``2*a0 + a1`` (Y=0 < y=1 < X=2 < x=3),
    the numeric image of ``is_less_than``'s order."""
    return np.uint64((np.int64(rel[t, 0]) << 1) | np.int64(rel[t, 1]))


@njit(inline='always')
def _code_of_v(v):
    """Order value -> engine code: Y(0)->2, y(1)->4, X(2)->1, x(3)->3,
    i.e. ``2 + 2*a1 - a0`` (the table ``expand_node_nj`` branches on)."""
    return np.uint8(np.int64(2) + np.int64(2) * np.int64(v & _U1)
                    - np.int64(v >> _U1))


@njit(inline='always')
def _pack32(rel, lo, m):
    """``(V, Vi)``: ``rel[lo:lo+m]`` (``m <= 32``) and its inverse as packed
    2m-bit words. Symbol ``t`` of the word is symbol ``m-1-t`` of the inverse
    with the inversion bit flipped, so it lands at bit ``2t`` as ``v ^ 1``."""
    V = _U0
    Vi = _U0
    for t in range(m):
        v = _vsym(rel, lo + t)
        V = (V << _U2) | v
        Vi = Vi | ((v ^ _U1) << np.uint64(2 * t))
    return V, Vi


@njit(inline='always')
def _least_rot32(V, m):
    """The least of the ``m`` rotations of the packed ``2m``-bit word ``V``
    (``m <= 32``). Rotation ``k`` moves symbol ``k`` to the front:
    ``((V << 2k) | (V >> (2m - 2k))) & mask``; both shifts lie in
    ``[2, 62]`` for ``1 <= k < m``, so no shift ever reaches the width."""
    if m <= 1:
        return V
    two_m = np.uint64(2 * m)
    if m < 32:
        mask = (_U1 << two_m) - _U1
    else:
        mask = _UALL
    best = V
    for k in range(1, m):
        s = np.uint64(2 * k)
        r = ((V << s) | (V >> (two_m - s))) & mask
        if r < best:
            best = r
    return best


@njit(inline='always')
def _fill_doubled(rel, lo, m, D, Di):
    """``D``: the doubled word ``w.w`` (``2m`` symbols) packed most
    significant first, 32 symbols a ``uint64``, zero beyond; ``Di`` the same
    for the inverse word. Five words cover ``2m <= 128`` symbols plus the
    one extra word ``_win`` may touch."""
    for e in range(5):
        D[e] = _U0
        Di[e] = _U0
    for t in range(m):
        v = _vsym(rel, lo + t)
        vi = v ^ _U1
        j = t
        D[j >> 5] |= v << np.uint64(62 - 2 * (j & 31))
        j = t + m
        D[j >> 5] |= v << np.uint64(62 - 2 * (j & 31))
        s = m - 1 - t
        Di[s >> 5] |= vi << np.uint64(62 - 2 * (s & 31))
        s = s + m
        Di[s >> 5] |= vi << np.uint64(62 - 2 * (s & 31))


@njit(inline='always')
def _win(D, p):
    """32 symbols of the packed doubled word starting at symbol ``p``."""
    e = p >> 5
    s = np.uint64(2 * (p & 31))
    if s == _U0:
        return D[e]
    return (D[e] << s) | (D[e + 1] >> (_U64 - s))


@njit(inline='always')
def _least_rot64(D, m):
    """Least rotation of a ``33..64``-symbol word from its packed doubled
    form, as ``(hi, lo)``: the first 32 symbols, then the remaining
    ``m - 32`` right-aligned. Equal lengths make the pair order the
    lexicographic order."""
    lsh = np.uint64(128 - 2 * m)
    bh = _win(D, 0)
    bl = _win(D, 32) >> lsh
    for k in range(1, m):
        h = _win(D, k)
        if h > bh:
            continue
        l = _win(D, k + 32) >> lsh
        if h < bh or l < bl:
            bh = h
            bl = l
    return bh, bl


@njit(inline='always')
def _canon_packed(rel, lo, m, D, Di):
    """``canonical_relator_nj(rel[lo:lo+m])`` for ``m <= 64`` as a packed
    ``(hi, lo)`` pair (``lo == 0`` when ``m <= 32``): the smaller of the
    least rotation of the word and of its inverse -- ``lex_cmp_array``
    returns the inverse's when ``r_min >= inv_min``, which is the minimum."""
    if m <= 32:
        V, Vi = _pack32(rel, lo, m)
        a = _least_rot32(V, m)
        b = _least_rot32(Vi, m)
        return (b if a >= b else a), _U0
    _fill_doubled(rel, lo, m, D, Di)
    ah, al = _least_rot64(D, m)
    bh, bl = _least_rot64(Di, m)
    if ah > bh or (ah == bh and al >= bl):
        return bh, bl
    return ah, al


@njit(inline='always')
def _encode_packed(hi, lo, m, out, o):
    """Write the ``m`` codes of the packed word at ``out[o:o+m]``."""
    if m <= 32:
        for t in range(m):
            out[o + t] = _code_of_v((hi >> np.uint64(2 * (m - 1 - t))) & _U3)
        return
    for t in range(32):
        out[o + t] = _code_of_v((hi >> np.uint64(2 * (31 - t))) & _U3)
    for t in range(32, m):
        out[o + t] = _code_of_v((lo >> np.uint64(2 * (m - 1 - t))) & _U3)


@njit(inline='always')
def _encode_bools(rel, n, out, o):
    """``expand_node_nj``'s code table on a bool-array word."""
    for t in range(n):
        v = 2 * rel[t, 0] + rel[t, 1]
        if v == 0:
            out[o + t] = 2
        elif v == 1:
            out[o + t] = 4
        elif v == 2:
            out[o + t] = 1
        else:
            out[o + t] = 3


@njit(inline='always')
def _packed_ge(ah, al, bh, bl):
    """``(ah, al) >= (bh, bl)``: ``lex_cmp_array`` on two packed words of the
    same length."""
    return ah > bh or (ah == bh and al >= bl)


@njit(cache=True)
def canon_packed_codes(rel):
    """Test hook: ``canonical_relator_nj(rel)`` as engine codes via the packed
    path (``len(rel) <= 64``)."""
    m = len(rel)
    D = np.empty(5, dtype=np.uint64)
    Di = np.empty(5, dtype=np.uint64)
    hi, lo = _canon_packed(rel, 0, m, D, Di)
    out = np.empty(m, dtype=np.uint8)
    _encode_packed(hi, lo, m, out, 0)
    return out


# ---------------------------------------------------------------------------
# the kernel
# ---------------------------------------------------------------------------
@njit(cache=True)
def expand_children_h(r1, r2, cap, cyclic, skip, packed):
    """``expand_node_topk_nj(r1, r2, cap, cyclic, 1, 0)``'s children with the
    cut-shift duplicates removed (``skip``, only honoured with ``cyclic``) and
    the canonical forms computed on packed words (``packed``, only honoured
    at ``cap <= 64``). Returns ``(cbuf, offs, lens, moves, count)``: child
    ``i``'s codes are ``cbuf[offs[i] : offs[i] + lens[i,0] + lens[i,1]]``,
    r1 then r2 back to back with no separator (the layout ``_feats_nj``
    reads), ``lens[i] = (la, lb)`` and ``moves[i] = (target, jsign, k1,
    k2)``. Every child emitted is one the reference emits, with the
    reference's codes, lengths and move, in the reference's relative order;
    every child the reference emits and this does not is an exact repeat of
    an earlier child of the same pop."""
    n1 = len(r1)
    n2 = len(r2)
    ub = 4 * (n1 + 1) * (n2 + 1)
    c_mv = np.empty((ub, 4), dtype=np.int32)
    c_tot = np.empty(ub, dtype=np.int64)
    cnt = 0
    do_skip = skip and cyclic
    do_pack = packed and cap <= 64

    inv1 = inverse_relator_nj(r1)
    inv2 = inverse_relator_nj(r2)

    # per-block "in the stream" bitmap over (k1, k2): set when a child is
    # emitted and when one is skipped as a repeat of a child already in the
    # stream; a skip requires the predecessor's bit (see the docstring)
    seen = np.zeros(n1 * n2 if n1 * n2 > 0 else 1, dtype=np.bool_)

    for target in range(1, 3):
        if target == 1:
            ri = r1
            rj = r2
            rj_inv = inv2
        else:
            ri = r2
            rj = r1
            rj_inv = inv1
        len_i = len(ri)
        if len_i == 0:
            continue
        oth = reduce_relator_nj(rj, cyclic)
        len_oth = len(oth)
        if len_oth > cap:
            continue
        for idx in range(2):
            oj = rj if idx == 0 else rj_inv
            jsign = 1 if idx == 0 else -1
            len_o = len(oj)
            if len_o == 0:
                continue
            for q in range(len_i * len_o):
                seen[q] = False
            for k1 in range(len_i):
                li = _ridx(k1, len_i - 1, len_i)      # A[-1]
                fi = _ridx(k1, 0, len_i)             # A[0]
                for k2 in range(len_o):
                    if not _inv_at(ri, li, oj, _ridx(k2, 0, len_o)):
                        continue
                    if do_skip and k1 >= 1:
                        # the cut shift: the predecessor (k1 - 1, k2 + 1)
                        # made this very child, earlier in this block, iff
                        # A[0] and B[-1] are inverse -- which is its seam
                        # test, so a set predecessor bit implies it; the
                        # explicit test is kept as the statement of the
                        # conjugacy condition
                        pk2 = k2 + 1
                        if pk2 == len_o:
                            pk2 = 0
                        if seen[(k1 - 1) * len_o + pk2] and _inv_at(
                                ri, fi, oj, _ridx(k2, len_o - 1, len_o)):
                            seen[k1 * len_o + k2] = True
                            continue
                    m = _seam_reduced_len_nj(ri, k1, oj, k2, cyclic)
                    if m > cap:
                        continue
                    seen[k1 * len_o + k2] = True
                    c_mv[cnt, 0] = target
                    c_mv[cnt, 1] = jsign
                    c_mv[cnt, 2] = k1
                    c_mv[cnt, 3] = k2
                    c_tot[cnt] = m + len_oth
                    cnt += 1

    count = cnt
    # each child's canonical pair is exactly m + len_oth codes long
    offs = np.empty(count + 1, dtype=np.int64)
    pos = 0
    for i in range(count):
        offs[i] = pos
        pos += c_tot[i]
    offs[count] = pos
    cbuf = np.empty(pos if pos > 0 else 1, dtype=np.uint8)
    lens = np.empty((count if count > 0 else 1, 2), dtype=np.int32)
    moves = np.empty((count if count > 0 else 1, 4), dtype=np.int32)

    cro_t1 = canonical_relator_nj(reduce_relator_nj(r2, cyclic))  # target==1
    cro_t2 = canonical_relator_nj(reduce_relator_nj(r1, cyclic))  # target==2
    lo_t1 = len(cro_t1)
    lo_t2 = len(cro_t2)

    nn = n1 + n2
    pbuf = np.empty((nn, 2), dtype=np.bool_)
    rbuf = np.empty((nn, 2), dtype=np.bool_)
    ibuf = np.empty((nn, 2), dtype=np.bool_)
    cbuf1 = np.empty((nn, 2), dtype=np.bool_)
    cbuf2 = np.empty((nn, 2), dtype=np.bool_)
    fbuf = np.empty(2 * nn, dtype=np.int32)
    D = np.empty(5, dtype=np.uint64)
    Di = np.empty(5, dtype=np.uint64)
    # the untouched relator's canonical form, packed once per pop
    o1h = _U0
    o1l = _U0
    o2h = _U0
    o2l = _U0
    if do_pack:
        o1h, o1l = _canon_packed(cro_t1, 0, lo_t1, D, Di)
        o2h, o2l = _canon_packed(cro_t2, 0, lo_t2, D, Di)

    for out in range(count):
        target = c_mv[out, 0]
        k1 = c_mv[out, 2]
        k2 = c_mv[out, 3]
        if target == 1:
            ri = r1
            oj = r2 if c_mv[out, 1] == 1 else inv2
        else:
            ri = r2
            oj = r1 if c_mv[out, 1] == 1 else inv1
        ni = len(ri)
        no = len(oj)
        for t in range(ni):
            src = _ridx(k1, t, ni)
            pbuf[t, 0] = ri[src, 0]
            pbuf[t, 1] = ri[src, 1]
        for t in range(no):
            src = _ridx(k2, t, no)
            pbuf[ni + t, 0] = oj[src, 0]
            pbuf[ni + t, 1] = oj[src, 1]
        lo, m = _reduce_into(pbuf, ni + no, cyclic, rbuf)
        o = offs[out]

        if do_pack:
            ph, pl = _canon_packed(rbuf, lo, m, D, Di)
            if target == 1:
                oh, ol, lo_o, oth_c = o1h, o1l, lo_t1, cro_t1
            else:
                oh, ol, lo_o, oth_c = o2h, o2l, lo_t2, cro_t2
            # canonical_pair_nj's swap: (c1, c2) = (piece, other) for
            # target 1 and (other, piece) for target 2; swap when
            # len(c1) > len(c2) or equal lengths and c1 >= c2.
            if target == 1:
                swap = m > lo_o or (m == lo_o and _packed_ge(ph, pl, oh, ol))
            else:
                swap = lo_o > m or (lo_o == m and _packed_ge(oh, ol, ph, pl))
            # after the swap ca is the piece iff (target == 1) != swap
            if (target == 1) != swap:
                _encode_packed(ph, pl, m, cbuf, o)
                _encode_packed(oh, ol, lo_o, cbuf, o + m)
                la = m
                lb = lo_o
            else:
                _encode_packed(oh, ol, lo_o, cbuf, o)
                _encode_packed(ph, pl, m, cbuf, o + lo_o)
                la = lo_o
                lb = m
        else:
            crp = _canon_into(rbuf[lo:lo + m], m, fbuf, ibuf, cbuf1, cbuf2)
            if target == 1:
                c1, c2 = crp, cro_t1
            else:
                c1, c2 = cro_t2, crp
            if len(c1) > len(c2) or (len(c1) == len(c2) and lex_cmp_array(c1, c2)):
                ca, cb = c2, c1
            else:
                ca, cb = c1, c2
            la = len(ca)
            lb = len(cb)
            _encode_bools(ca, la, cbuf, o)
            _encode_bools(cb, lb, cbuf, o + la)
        lens[out, 0] = la
        lens[out, 1] = lb
        moves[out, 0] = target
        moves[out, 1] = c_mv[out, 1]
        moves[out, 2] = k1
        moves[out, 3] = k2

    return cbuf, offs, lens, moves, count


@njit(cache=True)
def expand_and_score_h(r1, r2, cap, cyclic, seg_upto, seg_w, skip, packed):
    """``expand_and_score_nj(..., topk=0)`` on ``expand_children_h``'s
    children: the same nine-tuple, the blob, feature and score code copied
    verbatim so every surviving child's stored values are the reference's."""
    cbuf, coffs, lens, moves, count = expand_children_h(r1, r2, cap, cyclic,
                                                        skip, packed)

    offs = np.empty(count + 1, dtype=np.int64)
    klens = np.empty(count, dtype=np.int64)
    tots = np.empty(count, dtype=np.int64)
    knots = np.empty(count, dtype=np.int64)
    pos = 0
    for i in range(count):
        offs[i] = pos
        k = lens[i, 0] + lens[i, 1] + 1          # +1 for the separator byte
        klens[i] = k
        tots[i] = lens[i, 0] + lens[i, 1]
        pos += k
    offs[count] = pos

    blob = np.empty(pos if pos > 0 else 1, dtype=np.uint8)
    for i in range(count):
        la = lens[i, 0]
        lb = lens[i, 1]
        o = offs[i]
        c = coffs[i]
        for t in range(la):
            blob[o + t] = cbuf[c + t]
        blob[o + la] = 0
        for t in range(lb):
            blob[o + la + 1 + t] = cbuf[c + la + t]

    n_seg = len(seg_upto)
    seg_idx = np.empty(count, dtype=np.int64)
    score = np.empty(count, dtype=np.float64)
    f = np.empty(N_FEAT, dtype=np.float64)
    r_isx = np.empty(2 * cap + 2, dtype=np.bool_)
    r_len = np.empty(2 * cap + 2, dtype=np.int64)

    for i in range(count):
        _feats_nj(cbuf, coffs[i], lens[i, 0], lens[i, 1], r_isx, r_len, f)
        L = f[0]
        placed = False
        for s in range(n_seg):
            if L <= seg_upto[s]:
                acc = 0.0
                for d in range(N_FEAT):
                    w = seg_w[s, d]
                    if w != 0.0:
                        acc += w * f[d]
                seg_idx[i] = s
                score[i] = acc
                placed = True
                break
        if not placed:
            seg_idx[i] = n_seg
            score[i] = L
        knots[i] = int(f[4])

    return blob, offs, klens, seg_idx, score, tots, knots, moves, count
