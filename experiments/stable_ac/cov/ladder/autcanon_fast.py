"""Numba twin of ``autcanon.aut_canon`` for the mu-ladder hot path.

``aut_min(pair)`` returns exactly ``aut_canon(pair)[:2]`` — the Aut-minimal
total and THE canonical orbit rep — without the witnessing automorphism the
ladder never uses. Same algorithm, same tie-breaks, ported statement by
statement:

  * phase 1 peak-reduces over ``DESCENT`` (the 12 second-kind Whitehead
    autos, scanned in list order, strict ``<`` improvement, best-of-12 per
    step) using only cyclically-reduced LENGTHS;
  * phase 2 BFS-closes the minimal level set over all 20 ``AUTOS`` under a
    ``len == t`` filter, canonicalising each node with ``canon_pair``'s exact
    semantics (per-relator Booth least rotation over w and w^-1 in the
    solver's Y < y < X < x order; pair ordered by (len, ord-lex)), and takes
    ``min(seen)`` under PYTHON STRING ORDER — two different orders coexist
    here exactly as in the original, and both are load-bearing.

The auto table is built at import from ``autcanon.AUTOS`` itself (single
source of truth); the per-move word math is ``@njit`` kernels on int8 letter
arrays (1=x, -1=X, 2=y, -2=Y) and the set-closure orchestration stays in
Python (lesson: numba-jit-split). ``relabel_min(pair)`` is
``words.relabel_key`` (the 8-signed-perm canonical) on the same kernels —
used by the ladder as a coarser, still-exact memo key: equal keys imply the
same Aut-orbit, hence the same ``aut_min``.

Equivalence with the pure-Python originals is pinned by
``tests/stable_ac/test_autcanon_fast.py`` (all 124 class reps, CoV hop
outputs, seeded fuzz, orbit invariance); ``verify_mu_ladder`` deliberately
keeps using slow ``aut_canon``, so every production row is a fast-vs-slow
cross-check.
"""

import numpy as np
from numba import njit

from experiments.equivalence_classes.lib.autcanon import AUTOS

_CHAR_TO_INT = {"x": 1, "X": -1, "y": 2, "Y": -2}
_INT_TO_CHAR = {1: "x", -1: "X", 2: "y", -2: "Y"}

# AUTOS as an int8 table: images of x and y, up to 3 letters each.
_AUTO_IMG = np.zeros((len(AUTOS), 2, 3), dtype=np.int8)
_AUTO_LEN = np.zeros((len(AUTOS), 2), dtype=np.int8)
for _k, _a in enumerate(AUTOS):
    for _g, _gen in enumerate(("x", "y")):
        _img = _a[_gen]
        _AUTO_LEN[_k, _g] = len(_img)
        for _i, _c in enumerate(_img):
            _AUTO_IMG[_k, _g, _i] = _CHAR_TO_INT[_c]
N_AUTOS = len(AUTOS)          # 20; DESCENT = autos 8..19
_LEVEL_CAP = 50_000           # mirrors aut_canon's default level_cap


# byte-level codecs: letter array <-> "xXyY" string, no per-char Python
_ENC = np.zeros(256, dtype=np.int8)
for _c, _v in _CHAR_TO_INT.items():
    _ENC[ord(_c)] = _v
_DEC = np.zeros(5, dtype=np.uint8)      # index = letter + 2 (values -2..2)
for _v, _c in _INT_TO_CHAR.items():
    _DEC[_v + 2] = ord(_c)


def _to_arr(w):
    if not w:
        return np.empty(0, dtype=np.int8)
    return _ENC[np.frombuffer(w.encode("ascii"), dtype=np.uint8)]


def _to_str(a):
    if a.shape[0] == 0:
        return ""
    return bytes(_DEC[a + 2]).decode("ascii")


@njit(cache=True)
def _free_reduce(a):
    out = np.empty(a.shape[0], dtype=np.int8)
    n = 0
    for i in range(a.shape[0]):
        c = a[i]
        if n > 0 and out[n - 1] == -c:
            n -= 1
        else:
            out[n] = c
            n += 1
    return out[:n].copy()


@njit(cache=True)
def _cyc_reduce(a):
    w = _free_reduce(a)
    i, j = 0, w.shape[0]
    while j - i >= 2 and w[i] == -w[j - 1]:
        i += 1
        j -= 1
    return w[i:j].copy()


@njit(cache=True)
def _apply_auto(a, k, img, lens):
    """apply_hom(w, AUTOS[k]) then free_reduce. Image of a negative letter is
    the reversed negation of the generator's image."""
    out = np.empty(3 * a.shape[0] + 1, dtype=np.int8)
    n = 0
    for i in range(a.shape[0]):
        c = a[i]
        g = 0 if (c == 1 or c == -1) else 1
        m = lens[k, g]
        if c > 0:
            for j in range(m):
                v = img[k, g, j]
                if n > 0 and out[n - 1] == -v:
                    n -= 1
                else:
                    out[n] = v
                    n += 1
        else:
            for j in range(m - 1, -1, -1):
                v = -img[k, g, j]
                if n > 0 and out[n - 1] == -v:
                    n -= 1
                else:
                    out[n] = v
                    n += 1
    return out[:n].copy()


@njit(cache=True)
def _ord3(c):
    """The solver's Y < y < X < x order (words.ORDER)."""
    if c == -2:
        return 0
    if c == 2:
        return 1
    if c == -1:
        return 2
    return 3


@njit(cache=True)
def _booth_start(a):
    """Booth's least-rotation start index of ``a`` under _ord3 — an
    index-for-index port of words._least_rotation."""
    n = a.shape[0]
    ss = np.empty(2 * n, dtype=np.int8)
    for i in range(n):
        v = np.int8(_ord3(a[i]))
        ss[i] = v
        ss[i + n] = v
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
    return k


@njit(cache=True)
def _rotate(a, k):
    n = a.shape[0]
    out = np.empty(n, dtype=np.int8)
    for i in range(n):
        out[i] = a[(k + i) % n]
    return out


@njit(cache=True)
def _ord_le(a, b):
    """a <= b under _ord3, equal lengths assumed."""
    for i in range(a.shape[0]):
        oa, ob = _ord3(a[i]), _ord3(b[i])
        if oa != ob:
            return oa < ob
    return True


@njit(cache=True)
def _canon_rel(w):
    """words.canon_rel: cyc_reduce, then lex-min over rotations of w and of
    w^-1 in _ord3 order."""
    w = _cyc_reduce(w)
    n = w.shape[0]
    if n == 0:
        return w
    inv = np.empty(n, dtype=np.int8)
    for i in range(n):
        inv[i] = -w[n - 1 - i]
    a = _rotate(w, _booth_start(w))
    b = _rotate(inv, _booth_start(inv))
    return a if _ord_le(a, b) else b


@njit(cache=True)
def _pair_gt(a, b):
    """(len, ord-lex) comparison a > b — words.canon_pair's swap test."""
    if a.shape[0] != b.shape[0]:
        return a.shape[0] > b.shape[0]
    for i in range(a.shape[0]):
        oa, ob = _ord3(a[i]), _ord3(b[i])
        if oa != ob:
            return oa > ob
    return False


@njit(cache=True)
def _canon_pair(r1, r2):
    a = _canon_rel(r1)
    b = _canon_rel(r2)
    if _pair_gt(a, b):
        return b, a
    return a, b


@njit(cache=True)
def _peak_reduce(r1, r2, img, lens):
    """Phase 1: best-of-the-12-DESCENT-autos descent on lengths only, strict
    improvement, ties to the earlier auto — autcanon.peak_reduce verbatim."""
    c1 = _cyc_reduce(r1)
    c2 = _cyc_reduce(r2)
    tot = c1.shape[0] + c2.shape[0]
    while True:
        best_t = tot
        best_k = -1
        for k in range(8, N_AUTOS):
            t1 = _cyc_reduce(_apply_auto(c1, k, img, lens))
            t2 = _cyc_reduce(_apply_auto(c2, k, img, lens))
            t = t1.shape[0] + t2.shape[0]
            if t < best_t:
                best_t = t
                best_k = k
        if best_k == -1:
            return tot, c1, c2
        c1 = _cyc_reduce(_apply_auto(c1, best_k, img, lens))
        c2 = _cyc_reduce(_apply_auto(c2, best_k, img, lens))
        tot = best_t


@njit(cache=True)
def _expand_level(r1, r2, t, img, lens):
    """Phase 2's per-node move: all 20 autos, keep length == t, canonicalise.
    Returns (buffer, lengths, valid) with one row per auto."""
    cap = t + 1     # at level t the reduced relators sum to t, so each <= t
    buf = np.empty((N_AUTOS, 2, cap), dtype=np.int8)
    ln = np.zeros((N_AUTOS, 2), dtype=np.int64)
    ok = np.zeros(N_AUTOS, dtype=np.uint8)
    for k in range(N_AUTOS):
        t1 = _cyc_reduce(_apply_auto(r1, k, img, lens))
        t2 = _cyc_reduce(_apply_auto(r2, k, img, lens))
        if t1.shape[0] + t2.shape[0] != t:
            continue
        a, b = _canon_pair(t1, t2)
        ok[k] = 1
        ln[k, 0] = a.shape[0]
        ln[k, 1] = b.shape[0]
        for i in range(a.shape[0]):
            buf[k, 0, i] = a[i]
        for i in range(b.shape[0]):
            buf[k, 1, i] = b[i]
    return buf, ln, ok


@njit(cache=True)
def _relabel8(r1, r2, img, lens):
    """All 8 signed-permutation images, canonicalised — words.relabel_key's
    candidate set (the min is taken in Python, in Python string order)."""
    cap = max(r1.shape[0], r2.shape[0]) + 1
    buf = np.zeros((8, 2, cap), dtype=np.int8)
    ln = np.zeros((8, 2), dtype=np.int64)
    for k in range(8):
        a, b = _canon_pair(_apply_auto(r1, k, img, lens),
                           _apply_auto(r2, k, img, lens))
        ln[k, 0] = a.shape[0]
        ln[k, 1] = b.shape[0]
        for i in range(a.shape[0]):
            buf[k, 0, i] = a[i]
        for i in range(b.shape[0]):
            buf[k, 1, i] = b[i]
    return buf, ln


def aut_min(pair, level_cap=_LEVEL_CAP):
    """(total, rep) == aut_canon(pair)[:2]. Phase-2 closure orchestrated in
    Python over string keys so ``min(seen)`` uses Python string order exactly
    like autcanon.level_min."""
    r1, r2 = _to_arr(pair[0]), _to_arr(pair[1])
    t, m1, m2 = _peak_reduce(r1, r2, _AUTO_IMG, _AUTO_LEN)
    a, b = _canon_pair(m1, m2)
    # dedup on cheap bytes keys (the \x00 separator keeps unequal splits from
    # colliding); strings are built ONCE per unique node, at the end, because
    # the level-set min must use Python string order like autcanon.level_min
    seen = {a.tobytes() + b"\x00" + b.tobytes(): (a, b)}
    stack = [(a, b)]
    while stack:
        if len(seen) > level_cap:
            raise RuntimeError(f"minimal level set exceeds "
                               f"level_cap={level_cap}; rep unreliable")
        n1, n2 = stack.pop()
        buf, ln, ok = _expand_level(n1, n2, t, _AUTO_IMG, _AUTO_LEN)
        for k in range(N_AUTOS):
            if not ok[k]:
                continue
            c1 = buf[k, 0, :ln[k, 0]].copy()
            c2 = buf[k, 1, :ln[k, 1]].copy()
            key = c1.tobytes() + b"\x00" + c2.tobytes()
            if key not in seen:
                seen[key] = (c1, c2)
                stack.append((c1, c2))
    return int(t), min((_to_str(a), _to_str(b)) for a, b in seen.values())


def relabel_min(pair):
    """words.relabel_key on the fast kernels: the canonical form under the 8
    signed permutations. Equal keys => same Aut-orbit => same aut_min."""
    buf, ln = _relabel8(_to_arr(pair[0]), _to_arr(pair[1]),
                        _AUTO_IMG, _AUTO_LEN)
    return min((_to_str(buf[k, 0, :ln[k, 0]]), _to_str(buf[k, 1, :ln[k, 1]]))
               for k in range(8))


def warm():
    """Compile every kernel once (disk-cached) so the first real class does
    not pay the JIT."""
    aut_min(("xyXY", "xxY"))
    relabel_min(("xy", "Yx"))
