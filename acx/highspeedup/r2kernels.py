"""Numba kernels of the hybrid's rank-two frontier beyond ``acx.hybrid.kernels`` (backend ``"fast"``).

``fast_orbit`` is ``frontier.orbit`` (the key and its seven images under the other signed permutations) in one call;
``fast_expand_groups`` is ``fast_expand`` in the layout of ``frontier.spec_expand_groups``, with
``cascade.gate_precheck_key`` of every child. Both give what the pure-Python forms give, in the same order.
"""
import numpy as np
from numba import njit

from ..aut.autos import SIGNED
from ..aut.fast import IMAGES, LENGTHS
from ..hybrid.kernels import _BOOTH, _split, _write, expand_key
from ..search.fast.kernels import canon_buf, reduce_buf, rel_less


@njit(cache=True)
def _image_into(codes, s, e, k, buf):
    """``image`` of the relator ``codes[s:e]`` (key codes) under ``AUTOS[k]`` into ``buf``, reduced: ``(lo, n)``."""
    n = 0
    for t in range(s, e):
        c = _BOOTH[codes[t]]
        g = 1 - (c >> 1)
        m = LENGTHS[k, g]
        for j in range(m):
            buf[n] = IMAGES[k, g, j] if c & 1 else IMAGES[k, g, m - 1 - j] ^ 1
            n += 1
    return reduce_buf(buf, n, True)


@njit(cache=True)
def orbit_key(codes, ks):
    """``transform_key`` of each of ``ks`` in turn, its scratch reused: ``(blob, offsets)``."""
    sep = _split(codes)
    width = 3 * max(sep, len(codes) - sep - 1) + 1
    wa = np.empty(width, dtype=np.uint8)
    wb = np.empty(width, dtype=np.uint8)
    ca = np.empty(width, dtype=np.uint8)
    cb = np.empty(width, dtype=np.uint8)
    offs = np.zeros(len(ks) + 1, dtype=np.int64)
    blob = np.empty(len(ks) * (3 * len(codes) + 1), dtype=np.uint8)
    for t in range(len(ks)):
        lo_a, na = _image_into(codes, 0, sep, ks[t], wa)
        lo_b, nb = _image_into(codes, sep + 1, len(codes), ks[t], wb)
        canon_buf(wa, lo_a, na, ca)
        canon_buf(wb, lo_b, nb, cb)
        o = offs[t]
        if rel_less(cb, nb, ca, na):             # canon_pair: the pair by (length, Booth)
            _write(blob, o, cb, nb)
            blob[o + nb] = 0
            _write(blob, o + nb + 1, ca, na)
        else:
            _write(blob, o, ca, na)
            blob[o + na] = 0
            _write(blob, o + na + 1, cb, nb)
        offs[t + 1] = o + na + nb + 1
    return blob[:offs[len(ks)]], offs


_SIGNED = np.array(SIGNED[1:], dtype=np.int64)


def fast_orbit(key):
    """``frontier.orbit(key, fast_transform)``: the key and its seven images under the other signed permutations."""
    blob, offs = orbit_key(np.frombuffer(key, dtype=np.uint8), _SIGNED)
    raw, o = blob.tobytes(), offs.tolist()
    return [key, *map(raw.__getitem__, map(slice, o, o[1:]))]


@njit(cache=True)
def _precheck(codes, s, e):
    """``cascade.gate_precheck_key`` on one relator ``codes[s:e]``: one letter, a generator once, four cyclic syllables."""
    n = e - s
    if n == 1:
        return True
    na = 0
    for t in range(s, e):
        na += codes[t] & 1                       # X=1 and x=3 are the first generator
    if na == 1 or n - na == 1:
        return True
    turns = 0
    for t in range(n):
        turns += (codes[s + t] ^ codes[s + (t + 1) % n]) & 1
    return turns == 4


@njit(cache=True)
def expand_groups_key(codes, cap):
    """``expand_key`` plus the children ``gate_precheck_key`` passes and the children grouped by key length (each group in
    order): ``(blob, offs, moves, flagged, order, group starts, rejected)``, group ``g`` being
    ``order[starts[g]:starts[g + 1]]``, the groups by increasing length."""
    blob, offs, mv, _, rejected = expand_key(codes, cap)
    count = len(mv)
    flagged = np.empty(count, np.int64)
    nf = 0
    longest = 0
    for c in range(count):
        s, e = offs[c], offs[c + 1]
        sep = s
        while blob[sep] != 0:
            sep += 1
        if _precheck(blob, s, sep) or _precheck(blob, sep + 1, e) or e - s == 3:
            flagged[nf] = c
            nf += 1
        longest = max(longest, e - s)
    tally = np.zeros(longest + 2, np.int64)
    for c in range(count):
        tally[offs[c + 1] - offs[c] + 1] += 1
    starts = np.empty(longest + 2, np.int64)
    ng = 0
    pos = 0
    for k in range(longest + 1):                 # tally[k + 1]: children of length k; starts of the nonempty groups
        if tally[k + 1]:
            starts[ng] = pos
            ng += 1
            pos += tally[k + 1]
        tally[k + 1] = pos - tally[k + 1]        # now the first slot of length k
    starts[ng] = pos
    order = np.empty(count, np.int64)
    for c in range(count):
        k = offs[c + 1] - offs[c] + 1
        order[tally[k]] = c
        tally[k] += 1
    return blob[:offs[count]], offs, mv, flagged[:nf], order, starts[:ng + 1], rejected


def fast_expand_groups(key, cap):
    """``frontier.spec_expand_groups`` on numba."""
    blob, offs, mv, flagged, order, starts, rejected = expand_groups_key(np.frombuffer(key, dtype=np.uint8),
                                                                         -1 if cap is None else cap)
    order, starts = order.tolist(), starts.tolist()
    return (blob.tobytes(), offs.tolist(), mv, flagged.tolist(), [order[a:b] for a, b in zip(starts, starts[1:])],
            int(rejected))
