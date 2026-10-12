"""Numba kernels of the rank-two frontier (backend ``"fast"`` of ``acx.hybrid.frontier``).

``fast_expand`` and ``fast_full`` run ``acx.search.fast.kernels.expand`` on a key and write the children back as keys
(same children, order, cut-shift skip and cap count as the pure-Python ``spec_expand``). ``fast_transform`` applies one
of the 20 ``AUTOS`` (images of at most three letters) to a key, reduced and canonical.
"""
import numpy as np
from numba import njit

from ..aut.fast import IMAGES, LENGTHS, canon_pair, image
from ..core.moves import Move
from ..search.fast.kernels import child_width, expand as _expand, max_children

_BOOTH = np.array([0, 2, 0, 3, 1], dtype=np.uint8)      # key code -> Booth symbol (Y=0 y=1 X=2 x=3)
_KEYC = np.array([2, 4, 1, 3], dtype=np.uint8)          # Booth symbol -> key code


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
    """The children of a key's pair: ``(blob, offsets, moves, first relator lengths, rejected count)``."""
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
def transform_key(codes, k):
    """Apply ``AUTOS[k]`` to a key's pair; reduced, canonical."""
    sep = _split(codes)
    a, b = canon_pair(image(_BOOTH[codes[:sep]], k, IMAGES, LENGTHS),
                      image(_BOOTH[codes[sep + 1:]], k, IMAGES, LENGTHS))
    out = np.empty(len(a) + len(b) + 1, dtype=np.uint8)
    _write(out, 0, a, len(a))
    out[len(a)] = 0
    _write(out, len(a) + 1, b, len(b))
    return out


def fast_expand(key, cap):
    """``(children, rejected)`` of ``key``, as ``frontier.spec_expand`` returns them."""
    blob, offs, mv, _, rejected = expand_key(np.frombuffer(key, dtype=np.uint8), -1 if cap is None else cap)
    raw, offs = blob.tobytes(), offs.tolist()
    return [(raw[offs[c]:offs[c + 1]], Move(*m)) for c, m in enumerate(mv.tolist())], int(rejected)


def fast_full(key):
    """Every child of ``key`` with no cap, as arrays: ``(raw, offsets, first relator lengths)``."""
    blob, offs, _, l0, _ = expand_key(np.frombuffer(key, dtype=np.uint8), -1)
    return blob.tobytes(), offs, l0.astype(np.int64)


def fast_transform(key, k):
    """The key after the automorphism ``AUTOS[k]``."""
    return transform_key(np.frombuffer(key, dtype=np.uint8), k).tobytes()
