"""Whitehead's algorithm on F2: the Aut(F2)-canonical form of a presentation, with its witness.

``aut_canon(pres)`` gives ``AutCanon(total, rep, phi)``: the least canonical presentation of the Aut(F2)-orbit and
the factors ``phi`` (indices into ``AUTOS``, the first acts first) with ``canonical(phi(pres)) == rep`` (``check``).
Words are ``acx`` int tuples; two generators, any number of relators.
"""
from collections import namedtuple

from ..core.words import Presentation, canonical_rels, inverse, parse, reduce, state_key

AutCanon = namedtuple("AutCanon", "total rep phi")

_LETTERS = ("x", "X", "y", "Y")
_SECOND = (("x", "yx"), ("x", "Xy"), ("x", "Xyx"), ("x", "yX"), ("x", "xy"), ("x", "xyX"),
           ("xy", "y"), ("Yx", "y"), ("Yxy", "y"), ("xY", "y"), ("yx", "y"), ("yxY", "y"))
# 8 signed permutations (first kind), then the 12 second-kind autos: (image of x, image of y).
AUTOS = tuple((parse(a), parse(b)) for a, b in
              [(fx, fy) for fx in _LETTERS for fy in _LETTERS if fx.lower() != fy.lower()] + list(_SECOND))
DESCENT = range(8, len(AUTOS))       # only these change the length
IDENTITY = ((1,), (2,))


def sub_table(img):
    """The letter-to-word table of the endomorphism ``x -> img[0], y -> img[1]``."""
    return {1: img[0], -1: inverse(img[0]), 2: img[1], -2: inverse(img[1])}


def apply_table(w, tab):
    """``w`` with every letter replaced by its word in ``tab``, freely reduced."""
    out = []
    for g in w:
        for h in tab[g]:
            if out and out[-1] == -h:
                out.pop()
            else:
                out.append(h)
    return tuple(out)


def apply(w, img):
    """The image of word ``w`` under the endomorphism ``x -> img[0], y -> img[1]``, freely reduced."""
    return apply_table(w, sub_table(img))


def images(phi):
    """``(phi(x), phi(y))`` of a factor sequence (first factor acts first)."""
    img = IDENTITY
    for k in phi:
        img = (apply(img[0], AUTOS[k]), apply(img[1], AUTOS[k]))
    return img


INVERSE = tuple(next(j for j in range(len(AUTOS)) if images((k, j)) == IDENTITY) for k in range(len(AUTOS)))
TABLES = tuple(map(sub_table, AUTOS))


def invert(phi):
    """The factors of ``phi^-1``."""
    return tuple(INVERSE[k] for k in reversed(phi))


def apply_pres(pres, phi):
    """The presentation with every relator mapped by the automorphism ``phi`` (not reduced)."""
    tab = sub_table(images(phi))
    return Presentation(2, tuple(apply_table(r, tab) for r in pres.rels))


def _image(rels, k):
    """Every relator under ``AUTOS[k]``, cyclically reduced."""
    return tuple(reduce(apply_table(r, TABLES[k])) for r in rels)


def peak_reduce(rels):
    """Phase 1: ``(total, cyclically reduced rels, factors)`` at the orbit's minimal total cyclic length.

    Repeatedly applies the best of the 12 second-kind automorphisms (``DESCENT`` order, strict ``<``, ties to the
    earlier one), by lengths only: no canonical form is built on this hot path.
    """
    cur = tuple(reduce(r) for r in rels)
    tot = sum(map(len, cur))
    phi = []
    while True:
        best_k, best_t = None, tot
        for k in DESCENT:
            t = sum(map(len, _image(cur, k)))
            if t < best_t:
                best_k, best_t = k, t
        if best_k is None:
            return tot, cur, tuple(phi)
        cur, tot = _image(cur, best_k), best_t
        phi.append(best_k)


def level_min(rels, level_cap=50_000):
    """Phase 2: ``(rep rels, factors from rels to rep)`` over the minimal level set of ``rels``.

    Depth-first over all 20 ``AUTOS`` at a fixed total; each node is canonical (``canonical_rels``) and ``rep`` is the
    least in ``state_key`` order (``X < Y < x < y``). The level set of a peak-reduced presentation is connected, so
    ``rep`` is a complete orbit invariant; a set over ``level_cap`` raises, since a partial one gives a wrong ``rep``.
    """
    start = canonical_rels(rels)
    t = sum(map(len, start))
    seen = {start: None}                 # node -> (parent, auto index)
    stack = [start]
    while stack:
        if len(seen) > level_cap:
            raise RuntimeError(f"minimal level set exceeds level_cap={level_cap}; rep unreliable")
        node = stack.pop()
        for k in range(len(AUTOS)):
            nxt = _image(node, k)
            if sum(map(len, nxt)) != t:
                continue
            nxt = canonical_rels(nxt)
            if nxt not in seen:
                seen[nxt] = (node, k)
                stack.append(nxt)
    rep = min(seen, key=state_key)
    phi, node = [], rep
    while seen[node] is not None:
        node, k = seen[node]
        phi.append(k)
    return rep, tuple(reversed(phi))


def aut_canon(pres, level_cap=50_000):
    """``AutCanon(total, rep, phi)``: the Aut-minimal canonical representative and its witness.

    The factors (not only their composed images) are kept so that ``acx.aut.transport`` can realise ``phi`` by AC moves.
    """
    if pres.n_gen != 2:
        raise ValueError(f"Whitehead's algorithm here is for F2, got {pres.n_gen} generators")
    t, red, phi1 = peak_reduce(pres.rels)
    rep, phi2 = level_min(red, level_cap)
    return AutCanon(t, Presentation(2, rep), phi1 + phi2)


def check(pres, rep, phi):
    """The certificate, by substitution alone: canonical(phi(pres)) == rep."""
    return apply_pres(pres, phi).reduced().canonical() == rep


def automorphism(p, q, level_cap=50_000):
    """Factors ``phi`` with ``phi(p)`` equal to ``q`` up to conjugating, inverting and reordering relators, else None."""
    a, b = aut_canon(p, level_cap), aut_canon(q, level_cap)
    return a.phi + invert(b.phi) if a.rep == b.rep else None


def are_automorphic(p, q, level_cap=50_000):
    """``p`` and ``q`` lie in one Aut(F2)-orbit."""
    return automorphism(p, q, level_cap) is not None
