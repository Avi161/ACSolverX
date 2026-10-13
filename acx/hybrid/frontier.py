"""The hybrid's rank-two frontier on packed keys, on backend ``spec`` (pure Python) or ``fast`` (numba), same output.

A key is the canonical pair as bytes of key codes (``X=1 Y=2 x=3 y=4``), relators split by ``0``; byte order is
``acx.core.words.state_key`` order. A backend is ``(expand, full, transform)``: the children of the S-moves, every child
as arrays (for the cap counters), and one of the ``AUTOS`` applied to a key. ``over_cap`` picks the rejected ones.
"""
from collections import namedtuple

import numpy as np

from ..core.config import BACKENDS
from ..core.moves import Move
from ..core.words import canonical_rels, inverse, reduce, rotate
from .steps import aut_child

_CODE = {-1: 1, -2: 2, 1: 3, 2: 4}
_LETTER = (0, -1, -2, 1, 2)


def pack(rels):
    """The key of a canonical pair of relators."""
    return bytes(_CODE[g] for g in rels[0]) + b"\0" + bytes(_CODE[g] for g in rels[1])


def unpack(key):
    """The pair of relators of a key."""
    i = key.index(0)
    return tuple(map(_LETTER.__getitem__, key[:i])), tuple(map(_LETTER.__getitem__, key[i + 1:]))


def spec_expand(key, cap):
    """``(children, rejected)`` of ``key`` by the S-moves in pure Python: ``(child key, Move)`` pairs, and the count of moves a cap rejected."""
    rels = unpack(key)
    out, rejected = [], 0
    for i in (0, 1):
        ri, rj = rels[i], rels[1 - i]
        li = len(ri)
        for s in (1, -1):
            oj = rj if s == 1 else inverse(rj)
            lo = len(oj)
            if not (li and lo):
                continue
            if cap is not None and lo > cap:     # the untouched relator is over the cap: every move rejected
                rejected += sum(ri[li - 1 - k1] == -oj[(lo - k2) % lo] for k1 in range(li) for k2 in range(lo))
                continue
            marked = set()                       # moves whose child is in the stream (cut-shift skip)
            for k1 in range(li):
                last = ri[li - 1 - k1]
                for k2 in range(lo):
                    if oj[(lo - k2) % lo] != -last:
                        continue
                    if k1 and (k1 - 1, (k2 + 1) % lo) in marked:
                        marked.add((k1, k2))
                        continue
                    new = reduce(rotate(ri, k1) + rotate(oj, k2))
                    if cap is not None and len(new) > cap:
                        rejected += 1
                        continue
                    marked.add((k1, k2))
                    out.append((pack(canonical_rels((new, rj))), Move(i, 1 - i, s, k1, k2)))
    return out, rejected


def spec_transform(key, k):
    """The key after the automorphism ``AUTOS[k]``, in pure Python."""
    return pack(aut_child(unpack(key), k))


def spec_full(key):
    """Every child of ``key`` with no cap, as arrays: ``(raw, offsets, first relator lengths)``."""
    keys = [k for k, _ in spec_expand(key, None)[0]]
    return b"".join(keys), np.cumsum([0] + [len(k) for k in keys]), np.array([k.index(0) for k in keys], dtype=np.int64)


def backend(name):
    """``(expand, full, transform)`` of a backend; ``fast`` (numba) is imported only when asked for."""
    if name == "spec":
        return spec_expand, spec_full, spec_transform
    if name != "fast":
        raise ValueError(f"backend {name!r} not in {BACKENDS}")
    from .kernels import fast_expand, fast_full, fast_transform
    return fast_expand, fast_full, fast_transform


def orbit(key, transform):
    """The eight images of ``key`` under the signed permutations (``AUTOS[0..7]``, the identity first)."""
    return [key] + [transform(key, k) for k in range(1, 8)]


Drops = namedtuple("Drops", "raw pos before total longest start end flag")


def over_cap(full, cap):
    """The children in ``full`` (see ``backend``) that ``cap`` rejects, in search order, as ``Drops``: the key is
    ``raw[start:end]``, ``pos`` its place among all children (``before`` of them kept), ``flag`` whether ``gate_precheck_key`` passes
    (a one-letter relator, a generator occurring once, or four cyclic syllables in one relator)."""
    raw, offs, l0 = full
    start, end = offs[:-1], offs[1:]
    l1 = end - start - 1 - l0
    pos = np.flatnonzero(np.maximum(l0, l1) > cap)
    start, end, l0, l1 = start[pos], end[pos], l0[pos], l1[pos]
    codes = np.frombuffer(raw, np.uint8)
    isb = (codes % 2 == 0) & (codes > 0)                      # a letter of the second generator
    nb = np.concatenate(([0], np.cumsum(isb)))
    syl = np.concatenate(([0], np.cumsum(isb[:-1] != isb[1:])))
    flag = np.zeros(len(pos), dtype=bool)
    for s, e in ((start, start + l0), (start + l0 + 1, end)):
        n, b = e - s, nb[e] - nb[s]
        flag |= (n == 1) | (b == 1) | (n == b + 1) | (syl[e - 1] - syl[s] + (isb[e - 1] != isb[s]) == 4)
    return Drops(raw, pos, pos - np.arange(len(pos)), l0 + l1, np.maximum(l0, l1), start, end, flag)
