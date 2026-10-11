"""Numba twin of ``whitehead.aut_canon`` without the witness: ``aut_min(pres) -> (total, rep)``.

Same algorithm, same tie-breaks, statement by statement: phase 1 descends over
``DESCENT`` on cyclically reduced lengths only (strict ``<``, ties to the earlier
auto); phase 2 closes the minimal level set over all 20 ``AUTOS`` under the
``total == t`` filter, canonicalising every node exactly like
``acx.core.words.canonical_rels`` (Booth least rotation of ``w`` and ``w^-1``
in ``Y < y < X < x`` order, the pair ordered by ``(length, Booth)``), and takes
the least node in KEY order (``state_key``, ``X < Y < x < y``). Two orders,
both load-bearing, exactly as in the pure version.

The word kernels are ``@njit`` on int8 letter arrays, which are the ``acx`` int
words themselves (``1 = x, -1 = X, 2 = y, -2 = Y``); the set closure stays in
Python. The auto table is built from ``whitehead.AUTOS`` (one source of truth).
Pairs only (two generators, two relators). It has no witness, so it serves
screening and orbit keys; ``acx.aut.orbit_key(pres, backend="fast")`` is the
only entry point and ``tests/test_aut.py`` pins it to the pure version.

Source: ``origin/research/w5/stable-ac-escape:experiments/stable_ac/cov/ladder/
autcanon_fast.py`` (unchanged on every later branch); string codecs replaced by
int words, ``relabel_min`` (the mu-ladder memo key) dropped.
"""
import numpy as np
from numba import njit

from ..core.words import Presentation, state_key
from .whitehead import AUTOS

N_AUTOS = len(AUTOS)
_IMG = np.zeros((N_AUTOS, 2, 3), dtype=np.int8)
_LEN = np.zeros((N_AUTOS, 2), dtype=np.int8)
for _k, _a in enumerate(AUTOS):
    for _g in range(2):
        _LEN[_k, _g] = len(_a[_g])
        _IMG[_k, _g, :len(_a[_g])] = _a[_g]


@njit(cache=True)
def _cyc_reduce(a):
    out = np.empty(a.shape[0], dtype=np.int8)
    n = 0
    for i in range(a.shape[0]):
        if n > 0 and out[n - 1] == -a[i]:
            n -= 1
        else:
            out[n] = a[i]
            n += 1
    i, j = 0, n
    while j - i >= 2 and out[i] == -out[j - 1]:
        i += 1
        j -= 1
    return out[i:j].copy()


@njit(cache=True)
def _apply(a, k, img, lens):
    """``whitehead.apply(a, AUTOS[k])``: the image of a negative letter is the reversed negated image."""
    out = np.empty(3 * a.shape[0] + 1, dtype=np.int8)
    n = 0
    for i in range(a.shape[0]):
        c = a[i]
        g = 0 if (c == 1 or c == -1) else 1
        m = lens[k, g]
        for jj in range(m):
            v = img[k, g, jj] if c > 0 else -img[k, g, m - 1 - jj]
            if n > 0 and out[n - 1] == -v:
                n -= 1
            else:
                out[n] = v
                n += 1
    return out[:n].copy()


@njit(cache=True)
def _booth(c):
    """Booth order ``Y < y < X < x`` as 0..3."""
    return 2 * (abs(c) == 1) + (c > 0)


@njit(cache=True)
def _least_rotation(a):
    """Booth's least rotation of ``a`` (index for index the pure ``_least_rotation`` of main)."""
    n = a.shape[0]
    ss = np.empty(2 * n, dtype=np.int8)
    for i in range(n):
        ss[i] = ss[i + n] = _booth(a[i])
    f = np.full(2 * n, -1, dtype=np.int64)
    k = 0
    for j in range(1, 2 * n):
        sj = ss[j]
        i = f[j - k - 1]
        while i != -1 and sj != ss[k + i + 1]:
            if sj < ss[k + i + 1]:
                k = j - i - 1
            i = f[i]
        if i == -1 and sj != ss[k]:
            if sj < ss[k]:
                k = j
            f[j - k] = -1
        else:
            f[j - k] = i + 1
    out = np.empty(n, dtype=np.int8)
    for i in range(n):
        out[i] = a[(k + i) % n]
    return out


@njit(cache=True)
def _booth_less(a, b, strict):
    """``(len, Booth)`` comparison: a < b (``strict``) or a <= b."""
    if a.shape[0] != b.shape[0]:
        return a.shape[0] < b.shape[0]
    for i in range(a.shape[0]):
        if _booth(a[i]) != _booth(b[i]):
            return _booth(a[i]) < _booth(b[i])
    return not strict


@njit(cache=True)
def _canon_word(w):
    n = w.shape[0]
    if n == 0:
        return w
    inv = np.empty(n, dtype=np.int8)
    for i in range(n):
        inv[i] = -w[n - 1 - i]
    a, b = _least_rotation(w), _least_rotation(inv)
    return a if _booth_less(a, b, False) else b


@njit(cache=True)
def _canon_pair(r1, r2):
    a, b = _canon_word(r1), _canon_word(r2)
    return (b, a) if _booth_less(b, a, True) else (a, b)


@njit(cache=True)
def _peak_reduce(r1, r2, img, lens):
    c1, c2 = _cyc_reduce(r1), _cyc_reduce(r2)
    tot = c1.shape[0] + c2.shape[0]
    while True:
        best_t, best_k = tot, -1
        for k in range(8, N_AUTOS):
            t = _cyc_reduce(_apply(c1, k, img, lens)).shape[0] + _cyc_reduce(_apply(c2, k, img, lens)).shape[0]
            if t < best_t:
                best_t, best_k = t, k
        if best_k == -1:
            return tot, c1, c2
        c1 = _cyc_reduce(_apply(c1, best_k, img, lens))
        c2 = _cyc_reduce(_apply(c2, best_k, img, lens))
        tot = best_t


@njit(cache=True)
def _expand_level(r1, r2, t, img, lens):
    """All 20 auto images of a level node; ``ok[k]`` when the total stays ``t``, canonicalised."""
    buf = np.zeros((N_AUTOS, 2, t + 1), dtype=np.int8)
    ln = np.zeros((N_AUTOS, 2), dtype=np.int64)
    ok = np.zeros(N_AUTOS, dtype=np.uint8)
    for k in range(N_AUTOS):
        t1 = _cyc_reduce(_apply(r1, k, img, lens))
        t2 = _cyc_reduce(_apply(r2, k, img, lens))
        if t1.shape[0] + t2.shape[0] != t:
            continue
        a, b = _canon_pair(t1, t2)
        ok[k] = 1
        ln[k, 0], ln[k, 1] = a.shape[0], b.shape[0]
        buf[k, 0, :a.shape[0]] = a
        buf[k, 1, :b.shape[0]] = b
    return buf, ln, ok


def aut_min(pres, level_cap=50_000):
    """``(total, rep)`` equal to ``whitehead.aut_canon(pres)[:2]`` (pairs on F2 only)."""
    if pres.n_gen != 2 or len(pres.rels) != 2:
        raise ValueError(f"the fast Whitehead canon takes a pair on F2, got {pres}")
    r1, r2 = (np.array(r, dtype=np.int8) for r in pres.rels)
    t, m1, m2 = _peak_reduce(r1, r2, _IMG, _LEN)
    a, b = _canon_pair(m1, m2)
    seen = {a.tobytes() + b"\0" + b.tobytes(): (a, b)}
    stack = [(a, b)]
    while stack:
        if len(seen) > level_cap:
            raise RuntimeError(f"minimal level set exceeds level_cap={level_cap}; rep unreliable")
        buf, ln, ok = _expand_level(*stack.pop(), t, _IMG, _LEN)
        for k in np.flatnonzero(ok):
            c1, c2 = buf[k, 0, :ln[k, 0]].copy(), buf[k, 1, :ln[k, 1]].copy()
            key = c1.tobytes() + b"\0" + c2.tobytes()
            if key not in seen:
                seen[key] = (c1, c2)
                stack.append((c1, c2))
    rep = min(((tuple(c1.tolist()), tuple(c2.tolist())) for c1, c2 in seen.values()), key=state_key)
    return int(t), Presentation(2, rep)
