"""Numba kernel of Ryan Zang's MS640 CoV-gate best-first search (no JAX, no GPU), with no length limit by default.

The same algorithm as cov_gates_cpu.py (the pure-Python port, itself checked child by child and search by search
against Ryan's JAX code). Everything runs compiled: the moves, the canonical form, dedup (a hash table over states
stored as variable-length letter strings in one byte arena), the heap (length, depth, insertion seq) and the six
gates.

Relator length: Ryan's code caps relators at 24 letters and presentations at 48 in total. Here the caps are options:
`--max-length 24 --max-total 48` reproduces Ryan exactly (used by check_numba.py); the default is no cap at all, a
relator can grow as long as the search makes it. Each record reports the longest relator and total length the search
generated, so it is visible how far states actually went.

Usage (same output schema as cov_gates_cpu.py / ms640_cov_gates.py):
  python benchmark/ryan/cov_gates_numba.py --input data/ms640_solved.txt --output out.jsonl --gate periodic10 \\
      [--start 0 --end 640 --max-nodes 100000] [--max-length 24 --max-total 48]
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
from numba import njit

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cov_gates_cpu as C  # noqa: E402  (payloads, start keys, gate names)

GATE_CODE = {g: i for i, g in enumerate(C.GATES)}
UNBOUNDED = 1 << 60


# ------------------------------------------------------------------ words
@njit(cache=True)
def _ordv(c):
    # Y < y < X < x : -2 -> 0, 2 -> 1, -1 -> 2, 1 -> 3
    if c == -2:
        return 0
    if c == 2:
        return 1
    if c == -1:
        return 2
    return 3


@njit(cache=True)
def _min_rot_start(w, n):
    best = 0
    for s in range(1, n):
        for t in range(n):
            x = _ordv(w[(s + t) % n])
            y = _ordv(w[(best + t) % n])
            if x != y:
                if x < y:
                    best = s
                break
    return best


@njit(cache=True)
def canonical_word(w, n, out, inv):
    """w[:n] cyclically reduced -> out[:n]: the least rotation of w or w^-1 (order Y < y < X < x)"""
    if n == 0:
        return
    for i in range(n):
        inv[i] = -w[n - 1 - i]
    a = _min_rot_start(w, n)
    b = _min_rot_start(inv, n)
    use_inv = False
    for t in range(n):
        x = _ordv(w[(a + t) % n])
        y = _ordv(inv[(b + t) % n])
        if x != y:
            use_inv = y < x
            break
    if use_inv:
        for t in range(n):
            out[t] = inv[(b + t) % n]
    else:
        for t in range(n):
            out[t] = w[(a + t) % n]


@njit(cache=True)
def _word_less(a, na, b, nb):
    """(len, ordered letters): True if a < b strictly"""
    if na != nb:
        return na < nb
    for i in range(na):
        x = _ordv(a[i])
        y = _ordv(b[i])
        if x != y:
            return x < y
    return False


@njit(cache=True)
def _free_reduce(src, n, dst):
    m = 0
    for i in range(n):
        c = src[i]
        if c == 0:
            continue
        if m > 0 and dst[m - 1] == -c:
            m -= 1
        else:
            dst[m] = c
            m += 1
    return m


@njit(cache=True)
def _strip_ends(buf, m):
    """free-reduced buf[:m] -> cyclic reduction as (start, length)"""
    s = 0
    while m > 1 and buf[s] == -buf[s + m - 1]:
        s += 1
        m -= 2
    return s, m


# ------------------------------------------------------------------ the child: written to out[0:n0] + out[n0:n0+n1]
@njit(cache=True)
def _emit(a, na, a_canon, b, nb, b_canon, out, w1, w2, inv):
    """canonicalize both relators (a canonical one is copied) and write the ordered pair to out; returns n0"""
    if a_canon:
        for i in range(na):
            w1[i] = a[i]
    else:
        canonical_word(a, na, w1, inv)
    if b_canon:
        for i in range(nb):
            w2[i] = b[i]
    else:
        canonical_word(b, nb, w2, inv)
    if _word_less(w2, nb, w1, na):
        for i in range(nb):
            out[i] = w2[i]
        for i in range(na):
            out[nb + i] = w1[i]
        return nb
    for i in range(na):
        out[i] = w1[i]
    for i in range(nb):
        out[na + i] = w2[i]
    return na


@njit(cache=True)
def apply_sub(r0, l0, r1, l1, i, r, k1, k2, max_len, out, rel1, rel2, word, w1, w2, inv):
    """s_move. Returns (ok, n0, n1); the child is out[:n0+n1]."""
    s1 = k1 % l0
    for t in range(l0):
        rel1[t] = r0[(s1 + t) % l0]
    s2 = k2 % l1
    for t in range(l1):
        idx = (s2 + t) % l1
        rel2[t] = -r1[l1 - 1 - idx] if r == 1 else r1[idx]
    # seam cancellation: first j where rel2[j] != -rel1[l0-1-j] (positions past a word read 0); none -> 0
    nc = 0
    top = l0 if l0 > l1 else l1
    for j in range(top + 1):
        x = rel2[j] if j < l1 else 0
        y = rel1[l0 - 1 - j] if j < l0 else 0
        if x != -y:
            nc = j
            break
    L = l0 + l1 - 2 * nc
    if L > max_len:
        return False, 0, 0
    m = 0
    for t in range(l0 - nc):
        word[m] = rel1[t]
        m += 1
    for t in range(nc, l1):
        word[m] = rel2[t]
        m += 1
    c = L
    for j in range(L):
        if word[j] != -word[L - 1 - j]:
            c = j
            break
    nl = L - 2 * c
    if nl < 0:
        nl = 0
    if nl == l0:
        same = True
        for t in range(nl):
            if word[c + t] != rel1[t]:
                same = False
                break
        if same:
            return False, 0, 0
    newv = word[c:c + nl]
    if i == 0:
        n0 = _emit(newv, nl, False, r1, l1, True, out, w1, w2, inv)
    else:
        n0 = _emit(r0, l0, True, newv, nl, False, out, w1, w2, inv)
    return True, n0, nl + (l1 if i == 0 else l0) - n0


@njit(cache=True)
def _substitute(word, n, old, expr, ne, out, o0):
    m = o0
    for i in range(n):
        c = word[i]
        if c == old:
            for t in range(ne):
                out[m] = expr[t]
                m += 1
        elif c == -old:
            for t in range(ne):
                out[m] = -expr[ne - 1 - t]
                m += 1
        else:
            out[m] = c
            m += 1
    return m - o0


@njit(cache=True)
def apply_cov(rel_a, la, rel_b, lb, remove_gen, iso, z_inverse, z_start, z_len, max_len, out,
              rot, tmp, tmp2, expr, dfn, sub, w1, w2, inv):
    """_change_of_variables. Returns (ok, n0, n1); the child is out[:n0+n1]."""
    old = remove_gen + 1
    w = rel_a if iso == 0 else rel_b
    L = la if iso == 0 else lb
    o = rel_b if iso == 0 else rel_a
    lo = lb if iso == 0 else la
    if not (L > 1 and z_start < L and z_len < L):
        return False, 0, 0
    for t in range(L):
        rot[t] = w[(z_start + t) % L]
    cnt = 0
    p = -1
    for t in range(z_len, L):
        if abs(rot[t]) == old:
            cnt += 1
            p = t - z_len
    if cnt != 1:
        return False, 0, 0
    c0 = z_len
    clen = L - z_len
    token = rot[c0 + p]
    z_rhs = old if z_inverse == 1 else -old
    m = 0
    if token == old:
        for t in range(p - 1, -1, -1):
            tmp[m] = -rot[c0 + t]
            m += 1
        tmp[m] = z_rhs
        m += 1
        for t in range(clen - 1, p, -1):
            tmp[m] = -rot[c0 + t]
            m += 1
    else:
        for t in range(p + 1, clen):
            tmp[m] = rot[c0 + t]
            m += 1
        tmp[m] = -z_rhs
        m += 1
        for t in range(p):
            tmp[m] = rot[c0 + t]
            m += 1
    ne = _free_reduce(tmp, m, expr)
    if ne > max_len:
        return False, 0, 0
    # definition = [old] + substitute(inverse(z_word)); inverse(z_word) = inverse(window) or window
    for t in range(z_len):
        tmp2[t] = -rot[z_len - 1 - t] if z_inverse == 0 else rot[t]
    tmp[0] = old
    m = 1 + _substitute(tmp2, z_len, old, expr, ne, tmp, 1)
    md = _free_reduce(tmp, m, dfn)
    sd, nd = _strip_ends(dfn, md)
    if nd > max_len:
        return False, 0, 0
    ms = _substitute(o, lo, old, expr, ne, tmp, 0)
    mr = _free_reduce(tmp, ms, sub)
    ss, ns = _strip_ends(sub, mr)
    if ns > max_len:
        return False, 0, 0
    if iso == 0:
        n0 = _emit(dfn[sd:sd + nd], nd, False, sub[ss:ss + ns], ns, False, out, w1, w2, inv)
    else:
        n0 = _emit(sub[ss:ss + ns], ns, False, dfn[sd:sd + nd], nd, False, out, w1, w2, inv)
    return True, n0, nd + ns - n0


# ------------------------------------------------------------------ store: arena + hash table
@njit(cache=True)
def _hash(buf, n0, ntot):
    h = np.uint64(1469598103934665603) ^ np.uint64(n0 * 1000003 + ntot)
    for i in range(ntot):
        h ^= np.uint64(buf[i] + 3)
        h *= np.uint64(1099511628211)
    h ^= h >> np.uint64(31)
    h *= np.uint64(0x9E3779B97F4A7C15)
    h ^= h >> np.uint64(29)
    return h


@njit(cache=True)
def _grow(a, need):
    if need <= a.shape[0]:
        return a
    b = np.empty(max(need, 2 * a.shape[0]), a.dtype)
    b[:a.shape[0]] = a
    return b


@njit(cache=True)
def _lookup(th, tv, arena, off, l0s, l1s, h, buf, n0, ntot):
    """slot of the state buf (n0 | rest), or of the empty slot where it goes"""
    mask = np.uint64(th.shape[0] - 1)
    i = h & mask
    while True:
        sid = tv[i]
        if sid < 0:
            return i
        if th[i] == h and l0s[sid] == n0 and l0s[sid] + l1s[sid] == ntot:
            o = off[sid]
            eq = True
            for t in range(ntot):
                if arena[o + t] != buf[t]:
                    eq = False
                    break
            if eq:
                return i
        i = (i + np.uint64(1)) & mask


@njit(cache=True)
def _less(k1a, k2a, k1b, k2b):
    return k1a < k1b or (k1a == k1b and k2a < k2b)


@njit(cache=True)
def _push(h1, h2, n, a, b):
    i = n
    h1[i] = a
    h2[i] = b
    while i > 0:
        p = (i - 1) >> 1
        if not _less(h1[i], h2[i], h1[p], h2[p]):
            break
        h1[p], h1[i] = h1[i], h1[p]
        h2[p], h2[i] = h2[i], h2[p]
        i = p
    return n + 1


@njit(cache=True)
def _pop(h1, h2, n):
    a, b = h1[0], h2[0]
    n -= 1
    h1[0], h2[0] = h1[n], h2[n]
    i = 0
    while True:
        l = 2 * i + 1
        if l >= n:
            break
        c = l
        if l + 1 < n and _less(h1[l + 1], h2[l + 1], h1[l], h2[l]):
            c = l + 1
        if not _less(h1[c], h2[c], h1[i], h2[i]):
            break
        h1[i], h1[c] = h1[c], h1[i]
        h2[i], h2[c] = h2[c], h2[i]
        i = c
    return a, b, n


# ------------------------------------------------------------------ search
@njit(cache=True)
def run_search(root, n0_root, gate, max_nodes, max_len, max_total):
    """Ryan's search from the canonical root (root[:n0_root] | root[n0_root:]).
    Returns (stats int64[16], arena, off, l0s, l1s, parent, action, final_id)."""
    cap = 1 << 15
    arena = np.empty(1 << 20, np.int8)
    alen = 0
    off = np.empty(cap, np.int64)
    l0s = np.empty(cap, np.int32)
    l1s = np.empty(cap, np.int32)
    par = np.empty(cap, np.int64)
    act = np.empty(cap, np.int64)
    th = np.empty(1 << 16, np.uint64)
    tv = np.full(1 << 16, -1, np.int64)
    h1 = np.empty(cap, np.int64)   # (length << 24) | depth
    h2 = np.empty(cap, np.int64)   # seq
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
    visited = 0
    checks = 0
    openings = 0
    cov_enum = 0
    cov_changed = 0
    cov_shorter = 0
    cov_shorter_unique = 0
    openings_shorter = 0
    best_length = ntot_root
    last_improved = 0
    final_id = -1
    max_rel_seen = max(n0_root, ntot_root - n0_root)
    max_tot_seen = ntot_root

    ra = np.empty(1, np.int8)
    rb = np.empty(1, np.int8)
    while hn > 0 and visited < max_nodes:
        k1, sid, hn = _pop(h1, h2, hn)
        length = k1 >> 24
        depth = k1 & ((1 << 24) - 1)
        visited += 1
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
            last_improved = visited
        # scratch sized for this state (no fixed cap)
        M = la if la > lb else lb
        big = 2 * M * M + la + lb + 8   # a CoV child can be up to 2*M*M+1 letters
        out = np.empty(big, np.int8)
        rel1 = np.empty(M + 1, np.int8)
        rel2 = np.empty(M + 1, np.int8)
        word = np.empty(la + lb + 1, np.int8)
        rot = np.empty(M + 1, np.int8)
        tmp = np.empty(big, np.int8)
        tmp2 = np.empty(M + 1, np.int8)
        expr = np.empty(big, np.int8)
        dfn = np.empty(big, np.int8)
        subb = np.empty(big, np.int8)
        w1 = np.empty(big, np.int8)
        w2 = np.empty(big, np.int8)
        inv = np.empty(big, np.int8)
        sh_h = np.empty(64, np.uint64)
        sh_o = np.empty(64, np.int64)
        sh_n0 = np.empty(64, np.int64)
        sh_nt = np.empty(64, np.int64)
        sh_buf = np.empty(64 * 8, np.int8)
        rg = 0
        iso = 0
        Lw = 0
        inner = 0
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
                    op = visited - last_improved >= 100
                else:
                    op = visited % 10 == 0
                if not op:
                    break
                openings += 1
            nshort = 0
            sh_len = 0
            # one loop over Ryan's action list: substitutions (family 0) or CoV (family 1)
            if family == 0:
                total_acts = 0
                if la > 0 and lb > 0:
                    total_acts = la * lb * 2
            else:
                total_acts = 2 * 2 * (M * M) * 2
            # enumerate
            for tp in range(la if family == 0 else 4):
                if family == 0:
                    if la == 0 or lb == 0:
                        break
                    inner = lb
                else:
                    rg = tp // 2
                    iso = tp % 2
                    Lw = la if iso == 0 else lb
                    if Lw <= 1:
                        continue
                    inner = Lw * Lw
                for q in range(inner):
                    for e in range(4):
                        if family == 0:
                            sp = q
                            tc = ra[tp]
                            sc = rb[sp]
                            case = e // 2
                            br = e % 2
                            if case == 0 and tc != -sc:
                                continue
                            if case == 1 and tc != sc:
                                continue
                            rr = case
                            kk2 = sp if case == 0 else -sp - 1
                            ok, n0, n1 = apply_sub(ra, la, rb, lb, br, rr, tp + 1, kk2, max_len, out,
                                                   rel1, rel2, word, w1, w2, inv)
                            code = (br << 24) | (rr << 16) | ((tp + 1) << 8) | (kk2 + 64)
                        else:
                            if e >= 2:
                                break
                            z_start = q // Lw
                            z_len = q % Lw
                            if z_len == 0:
                                continue
                            if e == 0:
                                cnt = 0
                                wsrc = ra if iso == 0 else rb
                                for t in range(z_len, Lw):
                                    if abs(wsrc[(z_start + t) % Lw]) == rg + 1:
                                        cnt += 1
                                if cnt != 1:
                                    break
                            zi = e
                            cov_enum += 1
                            ok, n0, n1 = apply_cov(ra, la, rb, lb, rg, iso, zi, z_start, z_len, max_len, out,
                                                   rot, tmp, tmp2, expr, dfn, subb, w1, w2, inv)
                            code = ((2 + rg * 2 + iso) << 24) | (zi << 16) | (z_start << 8) | (z_len - 1 + 64)
                        if not ok:
                            continue
                        ntot = n0 + n1
                        # equal to the popped state?
                        if n0 == la and ntot == la + lb:
                            eq = True
                            for t in range(la):
                                if out[t] != ra[t]:
                                    eq = False
                                    break
                            if eq:
                                for t in range(lb):
                                    if out[la + t] != rb[t]:
                                        eq = False
                                        break
                            if eq:
                                continue
                        if ntot > max_total:
                            continue
                        hv = _hash(out, n0, ntot)
                        if family == 1:
                            cov_changed += 1
                        if ntot < length:
                            if family == 1:
                                cov_shorter += 1
                            # distinct shorter children (by hash and letters)
                            dup = False
                            for qq in range(nshort):
                                if sh_h[qq] == hv:
                                    s0 = sh_o[qq]
                                    if sh_n0[qq] == n0 and sh_nt[qq] == ntot:
                                        same = True
                                        for t in range(ntot):
                                            if sh_buf[s0 + t] != out[t]:
                                                same = False
                                                break
                                        if same:
                                            dup = True
                                            break
                            if not dup:
                                if nshort >= sh_h.shape[0]:
                                    sh_h = _grow(sh_h, nshort + 1)
                                    sh_o = _grow(sh_o, nshort + 1)
                                    sh_n0 = _grow(sh_n0, nshort + 1)
                                    sh_nt = _grow(sh_nt, nshort + 1)
                                if sh_len + ntot > sh_buf.shape[0]:
                                    sh_buf = _grow(sh_buf, sh_len + ntot)
                                sh_h[nshort] = hv
                                sh_o[nshort] = sh_len
                                sh_n0[nshort] = n0
                                sh_nt[nshort] = ntot
                                for t in range(ntot):
                                    sh_buf[sh_len + t] = out[t]
                                sh_len += ntot
                                nshort += 1
                        slot = _lookup(th, tv, arena, off, l0s, l1s, hv, out, n0, ntot)
                        if tv[slot] >= 0:
                            continue
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
                            arena[alen + t] = out[t]
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
                        if ntot > max_tot_seen:
                            max_tot_seen = ntot
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
            if family == 0:
                sub_shortens = nshort > 0
            else:
                cov_shorter_unique += nshort
                if nshort > 0:
                    openings_shorter += 1
        checks += 1

    stats = np.zeros(16, np.int64)
    stats[0] = 1 if final_id >= 0 else 0
    stats[1] = visited
    stats[2] = seq + 1
    stats[3] = checks
    stats[4] = openings
    stats[5] = cov_enum
    stats[6] = cov_changed
    stats[7] = cov_shorter
    stats[8] = cov_shorter_unique
    stats[9] = openings_shorter
    stats[10] = best_length
    stats[11] = hn
    stats[12] = max_rel_seen
    stats[13] = max_tot_seen
    stats[14] = alen
    return stats, arena, off, l0s, l1s, par, act, final_id


# ------------------------------------------------------------------ python side
def decode_action(v):
    v = int(v)
    return (v >> 24, (v >> 16) & 0xFF, (v >> 8) & 0xFF, (v & 0xFF) - 64)


def search(start_key, gate, max_nodes, max_len=None, max_total=None):
    t = time.monotonic()
    a, b = start_key[1]
    root = np.array(list(a) + list(b), np.int8)
    ml = UNBOUNDED if max_len is None else int(max_len)
    mt = UNBOUNDED if max_total is None else int(max_total)
    stats, arena, off, l0s, l1s, par, act, fid = run_search(root, len(a), GATE_CODE[gate], int(max_nodes), ml, mt)
    solved = bool(stats[0])
    keys, actions = [], []
    if solved:
        cur = int(fid)
        while cur != -1:
            o, n0, n1 = int(off[cur]), int(l0s[cur]), int(l1s[cur])
            seg = [int(x) for x in arena[o:o + n0 + n1]]
            keys.append((2, (tuple(seg[:n0]), tuple(seg[n0:]))))
            if act[cur] >= 0:
                actions.append(decode_action(act[cur]))
            cur = int(par[cur])
        keys.reverse()
        actions.reverse()
    reason = "solved" if solved else ("budget" if stats[11] > 0 else "frontier_exhausted")
    rec = C._result(solved, reason, int(stats[1]), int(stats[2]), int(stats[3]), int(stats[4]), int(stats[5]),
                    int(stats[6]), int(stats[7]), int(stats[8]), int(stats[9]), t, keys, actions, int(stats[10]))
    rec["max_relator_len_generated"] = int(stats[12])
    rec["max_total_len_generated"] = int(stats[13])
    return rec


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--gate", choices=C.GATES, required=True)
    p.add_argument("--start", type=int, default=0)
    p.add_argument("--end", type=int, default=None)
    p.add_argument("--max-nodes", type=int, default=100_000)
    p.add_argument("--max-length", type=int, default=None, help="per-relator cap; default none (Ryan: 24)")
    p.add_argument("--max-total", type=int, default=None, help="total-length cap; default none (Ryan: 48)")
    a = p.parse_args()
    lines = [l for l in Path(a.input).read_text().splitlines() if l.strip()]
    end = len(lines) if a.end is None else a.end
    config = {"dataset_sha256": hashlib.sha256(Path(a.input).read_bytes()).hexdigest(), "gate": a.gate,
              "max_nodes": a.max_nodes, "max_length": a.max_length, "max_total_length": a.max_total,
              "cov_window_min_length": 1, "cov_window_relator_margin": 1, "engine": "numba_port",
              "kernel_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    out = Path(a.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if out.exists():
        for line in out.read_text().splitlines():
            rec = json.loads(line)
            if rec["config"] != config:
                raise SystemExit(f"configuration mismatch in {out}; choose a new output file")
            done.add(rec["idx"])
    with out.open("a", buffering=1) as f:
        for idx in range(a.start, end):
            if idx in done:
                continue
            key = C.start_key_from_row(ast.literal_eval(lines[idx]))
            data = search(key, a.gate, a.max_nodes, a.max_length, a.max_total)
            data.update(idx=idx, config=config)
            f.write(json.dumps(data, separators=(",", ":")) + "\n")
            f.flush()
            os.fsync(f.fileno())


if __name__ == "__main__":
    main()
