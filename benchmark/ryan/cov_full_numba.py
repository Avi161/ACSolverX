"""Numba kernel of cov_full.search (mode ``full``): Ryan's CoV-gate search with every CoV image as the CoV move.

The same search as cov_full.py, compiled: Ryan's substitution moves, store and heap come from cov_gates_numba.py, and
the CoV step is a compiled port of ``acx.cov.states.cov_states`` (family ``suballpxyb8``, no length limit): the same
images in the same order, one per class up to relator order, rotation, inversion and the 8 signed relabellings.
check_full_numba.py compares it with the Python, image by image and search by search.

Only the path is rebuilt in Python, from the stored child indices: a substitution by Ryan's action code, an image by
its index in ``cov_states`` of the parent. The record is the one cov_full.search writes (``img_seconds`` is None:
the images are not timed apart from the search here).
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
from numba import njit

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))
import cov_full as F  # noqa: E402
import cov_gates_cpu as C  # noqa: E402
from cov_gates_numba import (GATE_CODE, _emit, _free_reduce, _grow, _hash, _lookup, _ordv, _pop, _push,  # noqa: E402
                             _strip_ends, _word_less, apply_sub, canonical_word, decode_action)

Z = 3
SIGNED = np.array([[1, 2], [1, -2], [-1, 2], [-1, -2], [2, 1], [2, -1], [-2, 1], [-2, -1]], np.int8)


# ------------------------------------------------------------------ words
@njit(cache=True)
def _cyc(src, n, dst):
    """free then cyclic reduction of src[:n] into dst; returns the length (dst[:len])"""
    m = _free_reduce(src, n, dst)
    s, k = _strip_ends(dst, m)
    for t in range(k):
        dst[t] = dst[s + t]
    return k


@njit(cache=True)
def _tuple_less(a, b, n):
    """Python tuple order of two int words of equal length n (signed values)"""
    for i in range(n):
        if a[i] != b[i]:
            return a[i] < b[i]
    return False


# ------------------------------------------------------------------ the words w (family.proper_subwords)
@njit(cache=True)
def _row_less(W, L, i, j):
    """(len, word) order of candidate rows i, j"""
    if L[i] != L[j]:
        return L[i] < L[j]
    for t in range(L[i]):
        if W[i, t] != W[j, t]:
            return W[i, t] < W[j, t]
    return False


@njit(cache=True)
def _row_eq(W, L, i, j):
    if L[i] != L[j]:
        return False
    for t in range(L[i]):
        if W[i, t] != W[j, t]:
            return False
    return True


@njit(cache=True)
def _sort_rows(W, L, idx):
    """merge sort of the row indices idx by _row_less (stable)"""
    n = idx.shape[0]
    tmp = np.empty(n, np.int64)
    width = 1
    while width < n:
        for lo in range(0, n, 2 * width):
            mid = min(lo + width, n)
            hi = min(lo + 2 * width, n)
            a, b, k = lo, mid, lo
            while a < mid and b < hi:
                if _row_less(W, L, idx[b], idx[a]):
                    tmp[k] = idx[b]
                    b += 1
                else:
                    tmp[k] = idx[a]
                    a += 1
                k += 1
            while a < mid:
                tmp[k] = idx[a]
                a += 1
                k += 1
            while b < hi:
                tmp[k] = idx[b]
                b += 1
                k += 1
        for t in range(n):
            idx[t] = tmp[t]
        width *= 2


@njit(cache=True)
def proper_subwords(r1, n1, r2, n2):
    """(W, L, order): the cyclic subwords of length 2..n as max(w, w^-1), without the whole relators, sorted"""
    M = max(n1, n2)
    cap = max(1, n1 * max(n1 - 1, 0) + n2 * max(n2 - 1, 0))
    W = np.zeros((cap, M), np.int8)
    L = np.zeros(cap, np.int64)
    whole = np.zeros(cap, np.bool_)
    w = np.empty(M, np.int8)
    wi = np.empty(M, np.int8)
    c = 0
    for k in range(2):
        rel = r1 if k == 0 else r2
        n = n1 if k == 0 else n2
        for m in range(2, n + 1):
            for i in range(n):
                for t in range(m):
                    w[t] = rel[(i + t) % n]
                for t in range(m):
                    wi[t] = -w[m - 1 - t]
                use = wi if _tuple_less(w, wi, m) else w
                for t in range(m):
                    W[c, t] = use[t]
                L[c] = m
                whole[c] = m == n
                c += 1
    idx = np.arange(c)
    _sort_rows(W, L, idx)
    keep = np.empty(c, np.int64)
    nk = 0
    g = 0
    while g < c:
        h = g
        bad = False
        while h < c and _row_eq(W, L, idx[g], idx[h]):
            bad = bad or whole[idx[h]]
            h += 1
        if not bad:
            keep[nk] = idx[g]
            nk += 1
        g = h
    return W, L, keep[:nk]


# ------------------------------------------------------------------ occurrences and patterns (substitution.py)
@njit(cache=True)
def occurrences(cyc, n, w, m, starts, letters):
    """windows of the cyclic word spelling w (letter Z) or w^-1 (letter -Z); returns the count"""
    if m > n:
        return 0
    k = 0
    for i in range(n):
        eq = True
        for t in range(m):
            if cyc[(i + t) % n] != w[t]:
                eq = False
                break
        if eq:
            starts[k] = i
            letters[k] = Z
            k += 1
            continue
        eq = True
        for t in range(m):
            if cyc[(i + t) % n] != -w[m - 1 - t]:
                eq = False
                break
        if eq:
            starts[k] = i
            letters[k] = -Z
            k += 1
    return k


@njit(cache=True)
def patterns(starts, K, n, m):
    """every set of pairwise disjoint occurrences, in the order of substitution.patterns (each left out before it
    is taken): (flat occurrence indices, offsets) with offsets[p]:offsets[p+1] the p-th set"""
    flat = np.empty(16, np.int64)
    offs = np.empty(16, np.int64)
    nf = 0
    npat = 0
    offs[0] = 0
    dec = np.full(K + 1, -1, np.int64)
    used = np.zeros(n, np.bool_)
    k = 0
    while k >= 0:
        if k == K:
            if npat + 2 > offs.shape[0]:
                offs = _grow(offs, npat + 2)
            cnt = 0
            for t in range(K):
                if dec[t] == 1:
                    cnt += 1
            if nf + cnt > flat.shape[0]:
                flat = _grow(flat, nf + cnt)
            for t in range(K):
                if dec[t] == 1:
                    flat[nf] = t
                    nf += 1
            npat += 1
            offs[npat] = nf
            k -= 1
            continue
        if dec[k] == -1:
            dec[k] = 0
            k += 1
        elif dec[k] == 0:
            free = True
            for j in range(m):
                if used[(starts[k] + j) % n]:
                    free = False
                    break
            if free:
                for j in range(m):
                    used[(starts[k] + j) % n] = True
                dec[k] = 1
                k += 1
            else:
                dec[k] = -1
                k -= 1
        else:
            for j in range(m):
                used[(starts[k] + j) % n] = False
            dec[k] = -1
            k -= 1
    return flat[:nf], offs[:npat + 1]


@njit(cache=True)
def substitute_pattern(cyc, n, m, starts, letters, flat, a, b, out, scratch):
    """cyc with the chosen occurrences flat[a:b] replaced by their letters, freely reduced into out; returns length"""
    if a == b:
        for t in range(n):
            out[t] = cyc[t]
        return n
    base = starts[flat[a]]
    q = a
    k = 0
    i = 0
    while i < n:
        if q < b and (starts[flat[q]] - base) % n == i:
            scratch[k] = letters[flat[q]]
            k += 1
            i += m
            q += 1
        else:
            scratch[k] = cyc[(base + i) % n]
            k += 1
            i += 1
    return _free_reduce(scratch, k, out)


# ------------------------------------------------------------------ one image (images.branches)
@njit(cache=True)
def _isolate(rel, nrel, g, cyc, expr):
    """expr with g = expr from rel (exactly one g^+-1 and some z once cyclically reduced); returns len or -1"""
    nc = _cyc(rel, nrel, cyc)
    at = -1
    cnt = 0
    hasz = False
    for i in range(nc):
        if abs(cyc[i]) == g:
            cnt += 1
            at = i
        elif abs(cyc[i]) == Z:
            hasz = True
    if cnt != 1 or not hasz:
        return -1
    first = cyc[at]
    ne = nc - 1
    for t in range(ne):
        expr[t] = cyc[(at + 1 + t) % nc]
    if first == g:                       # g s = 1 -> g = s^-1
        for t in range(ne // 2):
            x = expr[t]
            expr[t] = -expr[ne - 1 - t]
            expr[ne - 1 - t] = -x
        if ne % 2 == 1:
            expr[ne // 2] = -expr[ne // 2]
    return ne


@njit(cache=True)
def _sub_renumber(word, n, g, expr, ne, tmp, out):
    """renumber(substitute_generator(word, g, expr), g), then cyclically reduced into out; returns length"""
    k = 0
    for i in range(n):
        c = word[i]
        if c == g:
            for t in range(ne):
                tmp[k] = expr[t]
                k += 1
        elif c == -g:
            for t in range(ne):
                tmp[k] = -expr[ne - 1 - t]
                k += 1
        else:
            tmp[k] = c
            k += 1
    for t in range(k):
        a = abs(tmp[t])
        if a > g:
            tmp[t] = (a - 1) if tmp[t] > 0 else -(a - 1)
    return _cyc(tmp, k, out)


@njit(cache=True)
def _class_rep(a, na, b, nb, rep, pa, pb, w1, w2, inv, best):
    """the class of <x, y | a, b> up to order, rotation, inversion and the 8 signed relabellings, written to rep
    as (n0 | letters): the least over the 8 relabellings of the Ryan-canonical pair; returns n0"""
    have = False
    bn0 = 0
    for s in range(8):
        for t in range(na):
            c = a[t]
            v = SIGNED[s, abs(c) - 1]
            pa[t] = v if c > 0 else -v
        for t in range(nb):
            c = b[t]
            v = SIGNED[s, abs(c) - 1]
            pb[t] = v if c > 0 else -v
        n0 = _emit(pa, na, False, pb, nb, False, best, w1, w2, inv)
        less = False
        if not have:
            less = True
        elif n0 != bn0:
            less = n0 < bn0
        else:
            for t in range(na + nb):
                x = _ordv(best[t])
                y = _ordv(rep[t])
                if x != y:
                    less = x < y
                    break
        if less:
            for t in range(na + nb):
                rep[t] = best[t]
            bn0 = n0
            have = True
    return bn0


# ------------------------------------------------------------------ all images of a state (states.cov_states)
@njit(cache=True)
def cov_children(ra, la, rb, lb):
    """the CoV children of the canonical state (ra | rb): Ryan-canonical keys of the cov_states images, in order.
    Returns (n, buf, offs, n0s, ntots)."""
    M = max(la, lb)
    big = 2 * (la + lb + 2) * (la + lb + 2) + 16
    W, L, order = proper_subwords(ra, la, rb, lb)
    starts1 = np.empty(la + 1, np.int64)
    lets1 = np.empty(la + 1, np.int8)
    starts2 = np.empty(lb + 1, np.int64)
    lets2 = np.empty(lb + 1, np.int8)
    s1 = np.empty(big, np.int8)
    s2 = np.empty(big, np.int8)
    scratch = np.empty(big, np.int8)
    cyc = np.empty(big, np.int8)
    expr = np.empty(big, np.int8)
    tmp = np.empty(big * 2, np.int8)
    o1 = np.empty(big * 2, np.int8)
    o2 = np.empty(big * 2, np.int8)
    dfn = np.empty(M + 2, np.int8)
    pa = np.empty(big * 2, np.int8)
    pb = np.empty(big * 2, np.int8)
    w1 = np.empty(big * 4, np.int8)
    w2 = np.empty(big * 4, np.int8)
    inv = np.empty(big * 4, np.int8)
    cand = np.empty(big * 4, np.int8)
    rep = np.empty(big * 4, np.int8)
    # seen classes: hash, n0, ntot, offset into seen_buf
    seen_h = np.empty(64, np.uint64)
    seen_n0 = np.empty(64, np.int64)
    seen_nt = np.empty(64, np.int64)
    seen_o = np.empty(64, np.int64)
    seen_buf = np.empty(1024, np.int8)
    ns = 0
    nsb = 0
    out_buf = np.empty(1024, np.int8)
    out_o = np.empty(64, np.int64)
    out_n0 = np.empty(64, np.int64)
    out_nt = np.empty(64, np.int64)
    nout = 0
    nob = 0
    # the state's own class first
    n0 = _class_rep(ra, la, rb, lb, rep, pa, pb, w1, w2, inv, cand)
    seen_h[0] = _hash(rep, n0, la + lb)
    seen_n0[0] = n0
    seen_nt[0] = la + lb
    seen_o[0] = 0
    for t in range(la + lb):
        seen_buf[t] = rep[t]
    ns = 1
    nsb = la + lb
    for oi in range(order.shape[0]):
        row = order[oi]
        m = L[row]
        w = W[row, :m]
        dfn[0] = -Z
        for t in range(m):
            dfn[1 + t] = w[t]
        K1 = occurrences(ra, la, w, m, starts1, lets1)
        K2 = occurrences(rb, lb, w, m, starts2, lets2)
        f1, p1 = patterns(starts1, K1, la, m)
        f2, p2 = patterns(starts2, K2, lb, m)
        for i1 in range(p1.shape[0] - 1):
            n1s = substitute_pattern(ra, la, m, starts1, lets1, f1, p1[i1], p1[i1 + 1], s1, scratch)
            for i2 in range(p2.shape[0] - 1):
                if p1[i1] == p1[i1 + 1] and p2[i2] == p2[i2 + 1]:
                    continue
                n2s = substitute_pattern(rb, lb, m, starts2, lets2, f2, p2[i2], p2[i2 + 1], s2, scratch)
                for g in range(1, 3):
                    for iso in range(2):
                        if iso == 0:
                            ne = _isolate(s1, n1s, g, cyc, expr)
                        else:
                            ne = _isolate(s2, n2s, g, cyc, expr)
                        if ne < 0:
                            continue
                        if iso == 0:
                            na = _sub_renumber(s2, n2s, g, expr, ne, tmp, o1)
                        else:
                            na = _sub_renumber(s1, n1s, g, expr, ne, tmp, o1)
                        nb = _sub_renumber(dfn, m + 1, g, expr, ne, tmp, o2)
                        if na == 0 or nb == 0:
                            continue
                        c0 = _class_rep(o1, na, o2, nb, rep, pa, pb, w1, w2, inv, cand)
                        nt = na + nb
                        hv = _hash(rep, c0, nt)
                        dup = False
                        for q in range(ns):
                            if seen_h[q] == hv and seen_n0[q] == c0 and seen_nt[q] == nt:
                                so = seen_o[q]
                                same = True
                                for t in range(nt):
                                    if seen_buf[so + t] != rep[t]:
                                        same = False
                                        break
                                if same:
                                    dup = True
                                    break
                        if dup:
                            continue
                        if ns + 1 > seen_h.shape[0]:
                            seen_h = _grow(seen_h, ns + 1)
                            seen_n0 = _grow(seen_n0, ns + 1)
                            seen_nt = _grow(seen_nt, ns + 1)
                            seen_o = _grow(seen_o, ns + 1)
                        if nsb + nt > seen_buf.shape[0]:
                            seen_buf = _grow(seen_buf, nsb + nt)
                        seen_h[ns] = hv
                        seen_n0[ns] = c0
                        seen_nt[ns] = nt
                        seen_o[ns] = nsb
                        for t in range(nt):
                            seen_buf[nsb + t] = rep[t]
                        nsb += nt
                        ns += 1
                        # the child: the image in Ryan's canonical form
                        k0 = _emit(o1, na, False, o2, nb, False, cand, w1, w2, inv)
                        if nout + 1 > out_o.shape[0]:
                            out_o = _grow(out_o, nout + 1)
                            out_n0 = _grow(out_n0, nout + 1)
                            out_nt = _grow(out_nt, nout + 1)
                        if nob + nt > out_buf.shape[0]:
                            out_buf = _grow(out_buf, nob + nt)
                        out_o[nout] = nob
                        out_n0[nout] = k0
                        out_nt[nout] = nt
                        for t in range(nt):
                            out_buf[nob + t] = cand[t]
                        nob += nt
                        nout += 1
    return nout, out_buf, out_o, out_n0, out_nt


# ------------------------------------------------------------------ search
@njit(cache=True)
def run_search(root, n0_root, gate, max_units, charge):
    """cov_full.search, mode full. Returns (stats int64[16], arena, off, l0s, l1s, parent, action, final_id);
    action >= 0 is Ryan's substitution code, action < 0 the image -(j + 1)."""
    cap = 1 << 15
    arena = np.empty(1 << 20, np.int8)
    off = np.empty(cap, np.int64)
    l0s = np.empty(cap, np.int32)
    l1s = np.empty(cap, np.int32)
    par = np.empty(cap, np.int64)
    act = np.empty(cap, np.int64)
    th = np.empty(1 << 16, np.uint64)
    tv = np.full(1 << 16, -1, np.int64)
    h1 = np.empty(cap, np.int64)
    h2 = np.empty(cap, np.int64)
    hn = 0
    ntot_root = root.shape[0]
    for t in range(ntot_root):
        arena[t] = root[t]
    alen = ntot_root
    off[0] = 0
    l0s[0] = n0_root
    l1s[0] = ntot_root - n0_root
    par[0] = -1
    act[0] = -1
    hr = _hash(root, n0_root, ntot_root)
    i = _lookup(th, tv, arena, off, l0s, l1s, hr, root, n0_root, ntot_root)
    th[i] = hr
    tv[i] = 0
    hn = _push(h1, h2, hn, np.int64(ntot_root) << 24, 0)

    seq = 0
    pops = 0
    units = 0
    openings = 0
    n_sub = 0
    n_img = 0
    img_new = 0
    best_length = ntot_root
    last_improved = 0
    final_id = -1
    max_rel_seen = max(n0_root, ntot_root - n0_root)
    while hn > 0 and units < max_units:
        k1, sid, hn = _pop(h1, h2, hn)
        length = k1 >> 24
        depth = k1 & ((1 << 24) - 1)
        pops += 1
        units += 1
        la = l0s[sid]
        lb = l1s[sid]
        o = off[sid]
        ra = arena[o:o + la].copy()
        rb = arena[o + la:o + la + lb].copy()
        if la == 1 and lb == 1 and abs(ra[0]) != abs(rb[0]):
            final_id = sid
            break
        if length < best_length:
            best_length = length
            last_improved = pops
        M = la if la > lb else lb
        big = 2 * M * M + la + lb + 8
        out = np.empty(big, np.int8)
        rel1 = np.empty(M + 1, np.int8)
        rel2 = np.empty(M + 1, np.int8)
        word = np.empty(la + lb + 1, np.int8)
        w1 = np.empty(big, np.int8)
        w2 = np.empty(big, np.int8)
        inv = np.empty(big, np.int8)
        sub_shortens = False
        for family in range(2):
            if family == 1:
                mn = la if la < lb else lb
                mx = la if la > lb else lb
                if gate == 0:
                    op = not sub_shortens
                elif gate == 1:
                    op = mn <= 3
                elif gate == 2:
                    op = mx >= 2 * mn
                elif gate == 3:
                    op = length >= 16
                elif gate == 4:
                    op = pops - last_improved >= 100
                else:
                    op = pops % 10 == 0
                if not op:
                    break
                openings += 1
                if charge:
                    units += 1
                ncov, cbuf, coff, cn0, cnt = cov_children(ra, la, rb, lb)
                nchild = ncov
            else:
                nchild = la * lb * 4 if (la > 0 and lb > 0) else 0
                ncov = 0
                cbuf = out
                coff = np.empty(1, np.int64)
                cn0 = np.empty(1, np.int64)
                cnt = np.empty(1, np.int64)
            for ci in range(nchild):
                if family == 0:
                    tp = ci // (lb * 4)
                    rem = ci % (lb * 4)
                    sp = rem // 4
                    e = rem % 4
                    tc = ra[tp]
                    sc = rb[sp]
                    case = e // 2
                    br = e % 2
                    if case == 0 and tc != -sc:
                        continue
                    if case == 1 and tc != sc:
                        continue
                    kk2 = sp if case == 0 else -sp - 1
                    ok, n0, n1 = apply_sub(ra, la, rb, lb, br, case, tp + 1, kk2, 1 << 60, out,
                                           rel1, rel2, word, w1, w2, inv)
                    if not ok:
                        continue
                    child = out
                    ntot = n0 + n1
                    code = (br << 24) | (case << 16) | ((tp + 1) << 8) | (kk2 + 64)
                else:
                    child = cbuf[coff[ci]:coff[ci] + cnt[ci]]
                    n0 = cn0[ci]
                    ntot = cnt[ci]
                    n1 = ntot - n0
                    code = -(ci + 1)
                if n0 == la and ntot == la + lb:
                    eq = True
                    for t in range(ntot):
                        if child[t] != arena[o + t]:
                            eq = False
                            break
                    if eq:
                        continue
                if family == 0:
                    n_sub += 1
                    if ntot < length:
                        sub_shortens = True
                else:
                    n_img += 1
                hv = _hash(child, n0, ntot)
                slot = _lookup(th, tv, arena, off, l0s, l1s, hv, child, n0, ntot)
                if tv[slot] >= 0:
                    continue
                if family == 1:
                    img_new += 1
                seq += 1
                if seq + 1 > off.shape[0]:
                    off = _grow(off, seq + 1)
                    l0s = _grow(l0s, seq + 1)
                    l1s = _grow(l1s, seq + 1)
                    par = _grow(par, seq + 1)
                    act = _grow(act, seq + 1)
                if alen + ntot > arena.shape[0]:
                    arena = _grow(arena, alen + ntot)
                for t in range(ntot):
                    arena[alen + t] = child[t]
                off[seq] = alen
                alen += ntot
                l0s[seq] = n0
                l1s[seq] = n1
                par[seq] = sid
                act[seq] = code
                th[slot] = hv
                tv[slot] = seq
                if n0 > max_rel_seen:
                    max_rel_seen = n0
                if n1 > max_rel_seen:
                    max_rel_seen = n1
                if hn + 1 > h1.shape[0]:
                    h1 = _grow(h1, hn + 1)
                    h2 = _grow(h2, hn + 1)
                hn = _push(h1, h2, hn, (np.int64(ntot) << 24) | (depth + 1), seq)
                if 2 * (seq + 1) > tv.shape[0]:
                    nsz = tv.shape[0] * 2
                    nth = np.empty(nsz, np.uint64)
                    ntv = np.full(nsz, -1, np.int64)
                    for s_ in range(seq + 1):
                        o_ = off[s_]
                        tot_ = l0s[s_] + l1s[s_]
                        hh = _hash(arena[o_:o_ + tot_], l0s[s_], tot_)
                        j = _lookup(nth, ntv, arena, off, l0s, l1s, hh, arena[o_:o_ + tot_], l0s[s_], tot_)
                        nth[j] = hh
                        ntv[j] = s_
                    th = nth
                    tv = ntv
    stats = np.zeros(16, np.int64)
    stats[0] = 1 if final_id >= 0 else 0
    stats[1] = pops
    stats[2] = seq + 1
    stats[3] = openings
    stats[4] = units
    stats[5] = n_sub
    stats[6] = n_img
    stats[7] = img_new
    stats[8] = best_length
    stats[9] = hn
    stats[10] = max_rel_seen
    stats[11] = alen
    return stats, arena, off, l0s, l1s, par, act, final_id


# ------------------------------------------------------------------ python side
def children_of(key):
    """cov_children of a canonical key, as a list of canonical keys (for checks)."""
    a, b = key[1]
    n, buf, offs, n0s, nts = cov_children(np.array(a, np.int8), len(a), np.array(b, np.int8), len(b))
    out = []
    for j in range(n):
        seg = [int(x) for x in buf[offs[j]:offs[j] + nts[j]]]
        out.append((2, (tuple(seg[:n0s[j]]), tuple(seg[n0s[j]:]))))
    return out


def search(start, gate, max_units, mode="full", charge=True):
    """Same arguments and record as cov_full.search (only mode ``full``)."""
    if mode != "full":
        raise ValueError("the numba kernel runs mode 'full' only")
    t0 = time.monotonic()
    a, b = start[1]
    root = np.array(list(a) + list(b), np.int8)
    stats, arena, off, l0s, l1s, par, act, fid = run_search(root, len(a), GATE_CODE[gate], int(max_units),
                                                            bool(charge))
    solved = bool(stats[0])
    d = dict(pops=int(stats[1]), openings=int(stats[3]), units=int(stats[4]), states=int(stats[2]),
             n_sub=int(stats[5]), n_cov=0, n_img=int(stats[6]), img_new=int(stats[7]), img_seconds=None,
             best=int(stats[8]), max_gen_rel=int(stats[10]), t0=t0)
    if not solved:
        return F._record(False, "budget" if stats[9] > 0 else "frontier_exhausted", d, None)
    chain = []
    cur = int(fid)
    while cur != -1:
        o, n0, n1 = int(off[cur]), int(l0s[cur]), int(l1s[cur])
        seg = [int(x) for x in arena[o:o + n0 + n1]]
        chain.append(((2, (tuple(seg[:n0]), tuple(seg[n0:]))), int(act[cur])))
        cur = int(par[cur])
    chain.reverse()
    path = [{"state": C._payload(chain[0][0])}]
    for (pkey, _), (ckey, code) in zip(chain, chain[1:]):
        if code >= 0:
            action = decode_action(code)
            got = C.apply_substitution(pkey, action)
            step = {"kind": "sub", "state": C._payload(ckey), "action": list(action)}
        else:
            image = F.cov_states(*pkey[1])[-code - 1]
            got = C.canonical_key(*image.pres.rels)
            step = {"kind": "img", "state": C._payload(ckey),
                    "cov": {"steps": [F._jsonable(s) for s in image.steps], "tag": image.tag,
                            "n_subs": image.n_subs, "automorphic": F.automorphic(pkey, ckey)}}
        if got != ckey:
            raise RuntimeError(f"path step does not re-derive: {step['kind']} {code}")
        path.append(step)
    return F._record(True, "solved", d, path)
