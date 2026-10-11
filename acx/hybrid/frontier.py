"""The hybrid's rank-two frontier on packed keys, on either backend (identical output).

A rank-two state is a **key**: the canonical pair (``acx.core.words.canonical_rels``)
as bytes of key codes (``X=1, Y=2, x=3, y=4``), the relators separated by ``0``.
Byte order on keys is ``acx.core.words.state_key`` order. Two operations:

* ``expand(key, cap)``: every child of the S-moves, in the search order
  (``i -> j -> s -> k1 -> k2``) with the kernel's cut-shift skip (a child that
  is a conjugate of the previous move's child in the same block is left out:
  ``acx.search.fast.kernels``), as ``(children, rejected)``; ``children`` is a
  list of ``(child key, Move)`` and ``rejected`` counts the legal moves whose
  new relator is longer than ``cap``.
* ``transform(key, k)``: the key of ``AUTOS[k]`` applied to the state.

``"spec"`` is pure Python on ``acx`` words (here); ``"fast"`` is
``acx.hybrid.kernels`` (numba). ``tests/test_hybrid.py`` checks they agree
child for child, and the whole hybrid run on both.
"""
from ..core.moves import Move
from ..core.words import canonical_rels, inverse, reduce, rotate
from .cascade import aut_child

_CODE = {-1: 1, -2: 2, 1: 3, 2: 4}
_LETTER = (0, -1, -2, 1, 2)


def pack(rels):
    return bytes(_CODE[g] for g in rels[0]) + b"\0" + bytes(_CODE[g] for g in rels[1])


def unpack(key):
    i = key.index(0)
    return tuple(_LETTER[c] for c in key[:i]), tuple(_LETTER[c] for c in key[i + 1:])


def spec_expand(key, cap):
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
    return pack(aut_child(unpack(key), k))


BACKENDS = ("spec", "fast")


def backend(name):
    """``(expand, transform)`` of a backend; ``fast`` (numba) is imported only when asked for."""
    if name == "spec":
        return spec_expand, spec_transform
    if name != "fast":
        raise ValueError(f"backend {name!r} not in {BACKENDS}")
    from .kernels import fast_expand, fast_transform
    return fast_expand, fast_transform


def perm_min(key, transform):
    """The least key over the eight signed permutations (``AUTOS[0..7]``) and its index (0 = identity)."""
    best, best_k = key, 0
    for k in range(1, 8):
        cand = transform(key, k)
        if cand < best:
            best, best_k = cand, k
    return best, best_k
