"""Numba kernels of the hybrid's rank-two frontier (backend ``"fast"`` of ``acx.hybrid.frontier``).

``fast_expand`` decodes a key into the Booth-symbol layout of
``acx.search.fast.kernels`` and runs its ``expand`` (the same children, order,
cut-shift skip and cap count as the pure-Python ``spec_expand``), then writes the
children back as keys in one buffer. ``fast_transform`` applies one of the 20
``AUTOS`` (images of at most three letters) to a key, reduces and canonicalises
with the same kernel helpers. The source used ``hexpand.expand_and_score_h`` and
``basis_moves._apply_transform_nj`` (``origin/claude/vigilant-babbage-nnbuj0``),
which these replace.
"""
import numpy as np
from numba import njit

from ..aut.whitehead import AUTOS
from ..core.moves import Move
from ..core.words import inverse
from ..search.fast.kernels import canon_buf, reduce_buf, rel_less, child_width, expand as _expand, max_children

_BOOTH = np.array([0, 2, 0, 3, 1], dtype=np.uint8)      # key code -> Booth symbol (Y=0 y=1 X=2 x=3)
_KEYC = np.array([2, 4, 1, 3], dtype=np.uint8)          # Booth symbol -> key code


def _image_tables():
    tab = np.zeros((len(AUTOS), 4, 3), dtype=np.uint8)
    tlen = np.zeros((len(AUTOS), 4), dtype=np.int64)
    for k, img in enumerate(AUTOS):
        for g in (1, -1, 2, -2):
            w = img[abs(g) - 1] if g > 0 else inverse(img[abs(g) - 1])
            b = 2 * (2 - abs(g)) + (g > 0)
            tlen[k, b] = len(w)
            tab[k, b, :len(w)] = [2 * (2 - abs(x)) + (x > 0) for x in w]
    return tab, tlen


_TAB, _TLEN = _image_tables()


@njit(cache=True)
def _split(codes):
    sep = 0
    while codes[sep] != 0:
        sep += 1
    return sep


@njit(cache=True)
def _write(blob, o, row, n):
    for t in range(n):
        blob[o + t] = _KEYC[row[t]]


@njit(cache=True)
def expand_key(codes, cap):
    sep = _split(codes)
    lens = np.array([sep, len(codes) - sep - 1], dtype=np.int32)
    syms = np.zeros((2, max(lens[0], lens[1], 1)), dtype=np.uint8)
    for t in range(lens[0]):
        syms[0, t] = _BOOTH[codes[t]]
    for t in range(lens[1]):
        syms[1, t] = _BOOTH[codes[sep + 1 + t]]
    mc = max(max_children(lens), 1)
    out = np.zeros((mc, 2, max(child_width(lens), 1)), dtype=np.uint8)
    out_len = np.zeros((mc, 2), dtype=np.int32)
    out_mv = np.zeros((mc, 5), dtype=np.int32)
    count, rejected = _expand(syms, lens, 2, cap, True, out, out_len, out_mv)
    offs = np.empty(count + 1, dtype=np.int64)
    pos = 0
    for c in range(count):
        offs[c] = pos
        pos += out_len[c, 0] + out_len[c, 1] + 1
    offs[count] = pos
    blob = np.empty(max(pos, 1), dtype=np.uint8)
    for c in range(count):
        o, a = offs[c], out_len[c, 0]
        _write(blob, o, out[c, 0], a)
        blob[o + a] = 0
        _write(blob, o + a + 1, out[c, 1], out_len[c, 1])
    return blob, offs, out_mv[:count], out_len[:count, 0], rejected


@njit(cache=True)
def transform_key(codes, tab, tlen):
    sep = _split(codes)
    n = len(codes) - 1
    buf = np.empty(3 * n + 1, dtype=np.uint8)
    can = np.zeros((2, 3 * n + 1), dtype=np.uint8)
    cl = np.zeros(2, dtype=np.int64)
    for w in range(2):
        m = 0
        for t in range(0 if w == 0 else sep + 1, sep if w == 0 else len(codes)):
            b = _BOOTH[codes[t]]
            for u in range(tlen[b]):
                buf[m] = tab[b, u]
                m += 1
        lo, size = reduce_buf(buf, m, True)
        canon_buf(buf, lo, size, can[w])
        cl[w] = size
    first = 1 if rel_less(can[1], cl[1], can[0], cl[0]) else 0
    out = np.empty(cl[0] + cl[1] + 1, dtype=np.uint8)
    _write(out, 0, can[first], cl[first])
    out[cl[first]] = 0
    _write(out, cl[first] + 1, can[1 - first], cl[1 - first])
    return out


def fast_expand(key, cap):
    blob, offs, mv, _, rejected = expand_key(np.frombuffer(key, dtype=np.uint8), -1 if cap is None else cap)
    raw, offs = blob.tobytes(), offs.tolist()
    return [(raw[offs[c]:offs[c + 1]], Move(*m)) for c, m in enumerate(mv.tolist())], int(rejected)


def fast_full(key):
    """Every child of ``key`` with no cap, as arrays: ``(raw, offsets, first relator lengths)``."""
    blob, offs, _, l0, _ = expand_key(np.frombuffer(key, dtype=np.uint8), -1)
    return blob.tobytes(), offs, l0.astype(np.int64)


def fast_transform(key, k):
    return transform_key(np.frombuffer(key, dtype=np.uint8), _TAB[k], _TLEN[k]).tobytes()
