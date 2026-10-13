"""Numba twin of ``whitehead.aut_canon`` without the witness: ``aut_min(pres) -> (total, rep)``.

Same algorithm and tie-breaks as the pure version: peak reduction over ``DESCENT`` (strict ``<``, ties to the earlier
auto), then a closure of the minimal level set over all 20 ``AUTOS``, every node canonicalised exactly like
``canonical_rels``, and the least node in ``state_key`` order is the representative. Words are the search kernels'
``uint8`` symbols (``Y < y < X < x`` = 0..3, inverse = ``^ 1``). Pairs on F2 only; reached through
``acx.aut.orbit_key(pres, "fast")`` and pinned to the pure version by ``tests/test_aut.py``.
"""
import numpy as np
from numba import njit

from ..core.words import Presentation, state_key
from ..search.fast.kernels import canon_buf, decode_word, encode, reduce_buf, rel_less
from .autos import AUTOS, DESCENT

N_AUTOS = len(AUTOS)
FIRST_SECOND_KIND = DESCENT.start                       # a plain int, which numba can freeze
IMAGES = np.stack([encode(a, 2, 3)[0] for a in AUTOS])  # (auto, generator, letter) symbols
LENGTHS = np.array([[len(w) for w in a] for a in AUTOS], dtype=np.int64)


@njit(cache=True)
def image(w, k, img, lens):
    """``w`` under ``AUTOS[k]``, freely then cyclically reduced (``AUTOS[0]`` is the identity: a plain reduction)."""
    out = np.empty(3 * w.shape[0], dtype=np.uint8)
    n = 0
    for c in w:
        g = 1 - (c >> 1)                                                  # symbols 2, 3 are x; 0, 1 are y
        m = lens[k, g]
        for j in range(m):
            out[n] = img[k, g, j] if c & 1 else img[k, g, m - 1 - j] ^ 1
            n += 1
    lo, n = reduce_buf(out, n, True)
    return out[lo:lo + n].copy()


@njit(cache=True)
def canon_pair(a, b):
    """Each word canonical, the pair ordered by ``(length, Booth)``."""
    ca, cb = np.empty_like(a), np.empty_like(b)
    canon_buf(a, 0, a.shape[0], ca)
    canon_buf(b, 0, b.shape[0], cb)
    return (cb, ca) if rel_less(cb, cb.shape[0], ca, ca.shape[0]) else (ca, cb)


@njit(cache=True)
def _peak_reduce(r1, r2, img, lens):
    """``(total, r1, r2)`` after descending by the second-kind autos (``DESCENT``) as long as the total drops."""
    c1, c2 = image(r1, 0, img, lens), image(r2, 0, img, lens)
    tot = c1.shape[0] + c2.shape[0]
    while True:
        best_t, best_k = tot, -1
        for k in range(FIRST_SECOND_KIND, N_AUTOS):
            t = image(c1, k, img, lens).shape[0] + image(c2, k, img, lens).shape[0]
            if t < best_t:
                best_t, best_k = t, k
        if best_k == -1:
            return tot, c1, c2
        c1, c2 = image(c1, best_k, img, lens), image(c2, best_k, img, lens)
        tot = best_t


@njit(cache=True)
def _expand_level(r1, r2, t, img, lens):
    """All 20 auto images of a level node; ``ok[k]`` when the total stays ``t``, canonicalised."""
    buf = np.zeros((N_AUTOS, 2, t + 1), dtype=np.uint8)
    ln = np.zeros((N_AUTOS, 2), dtype=np.int64)
    ok = np.zeros(N_AUTOS, dtype=np.uint8)
    for k in range(N_AUTOS):
        t1, t2 = image(r1, k, img, lens), image(r2, k, img, lens)
        if t1.shape[0] + t2.shape[0] != t:
            continue
        a, b = canon_pair(t1, t2)
        ok[k] = 1
        ln[k, 0], ln[k, 1] = a.shape[0], b.shape[0]
        buf[k, 0, :a.shape[0]] = a
        buf[k, 1, :b.shape[0]] = b
    return buf, ln, ok


def aut_min(pres, level_cap=50_000):
    """``(total, rep)`` equal to ``whitehead.aut_canon(pres)[:2]`` (pairs on F2 only)."""
    if pres.n_gen != 2 or len(pres.rels) != 2:
        raise ValueError(f"the fast Whitehead canon takes a pair on F2, got {pres}")
    syms, lens = encode(pres.rels, 2)
    t, m1, m2 = _peak_reduce(syms[0, :lens[0]].copy(), syms[1, :lens[1]].copy(), IMAGES, LENGTHS)
    a, b = canon_pair(m1, m2)
    seen = {a.tobytes() + b"\0" + b.tobytes(): (a, b)}
    stack = [(a, b)]
    while stack:
        if len(seen) > level_cap:
            raise RuntimeError(f"minimal level set exceeds level_cap={level_cap}; rep unreliable")
        buf, ln, ok = _expand_level(*stack.pop(), t, IMAGES, LENGTHS)
        for k in np.flatnonzero(ok):
            c1, c2 = buf[k, 0, :ln[k, 0]].copy(), buf[k, 1, :ln[k, 1]].copy()
            key = c1.tobytes() + b"\0" + c2.tobytes()
            if key not in seen:
                seen[key] = (c1, c2)
                stack.append((c1, c2))
    rep = min(((decode_word(c1, 2), decode_word(c2, 2)) for c1, c2 in seen.values()), key=state_key)
    return int(t), Presentation(2, rep)
