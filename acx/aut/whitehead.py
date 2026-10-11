"""Whitehead's algorithm on F2: the Aut(F2)-canonical form of a presentation, with its witness.

An automorphism ``phi`` of F2 maps an AC-trivial presentation to an AC-trivial
one (AC moves are Aut-equivariant and ``phi(x), phi(y)`` is a basis), so a whole
Aut(F2)-orbit is one problem. ``aut_canon(pres)`` returns ``AutCanon(total, rep,
phi)`` with the certificate

    reduce + canonicalise(phi(pres)) == rep          (``check``)

``phi`` is a tuple of indices into ``AUTOS`` in application order (the first
index acts first); ``images(phi)`` composes it, ``invert(phi)`` inverts it.
Keeping the factors (not only the composed images) is what lets
``acx.aut.transport`` realise ``phi`` by AC moves.

The algorithm, two phases:

1. **Peak reduction** to the orbit's minimal total cyclic length: repeatedly
   apply the best of the 12 second-kind Whitehead automorphisms (``DESCENT``,
   list order, strict ``<``, ties to the earlier one). Lengths only, never a
   canonical form (that is the hot path).
2. **Level set**: DFS over all 20 ``AUTOS`` keeping the total fixed; every node
   is the reduced canonical form (``acx.core.words``: Booth order per relator,
   relators sorted by ``(length, Booth)``). ``rep`` is the least node in KEY
   order (``state_key``: ``X < Y < x < y``, the order of main's string pairs).
   The minimal level set is connected (peak reduction), so ``rep`` is a
   complete orbit invariant. A level set over ``level_cap`` raises: a partial
   set would give a silently wrong ``rep``.

Words are ``acx`` int tuples; two generators, any number of relators.

Sources: ``origin/main:experiments/equivalence_classes/lib/autcanon.py`` (the
witness-carrying ``aut_canon``; same autos, order and tie-breaks) and
``origin/main:experiments/analysis/whitehead.py`` (the witness-free original).
Both are identical on every later branch. On 3,000 AC19_extended rows this
module returns main's ``rep`` and main's ``phi`` images exactly.
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
    return {1: img[0], -1: inverse(img[0]), 2: img[1], -2: inverse(img[1])}


def apply_table(w, tab):
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


def _inverse_index(k):
    return next(j for j in range(len(AUTOS)) if images((k, j)) == IDENTITY)


INVERSE = tuple(_inverse_index(k) for k in range(len(AUTOS)))
TABLES = tuple(map(sub_table, AUTOS))


def invert(phi):
    """The factors of ``phi^-1``."""
    return tuple(INVERSE[k] for k in reversed(phi))


def apply_pres(pres, phi):
    tab = sub_table(images(phi))
    return Presentation(2, tuple(apply_table(r, tab) for r in pres.rels))


def _two_gen(pres):
    if pres.n_gen != 2:
        raise ValueError(f"Whitehead's algorithm here is for F2, got {pres.n_gen} generators")
    return pres


def _image(rels, k):
    return tuple(reduce(apply_table(r, TABLES[k])) for r in rels)


def peak_reduce(rels):
    """Phase 1: ``(total, cyclically reduced rels, factors)`` at the orbit's minimal total."""
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
    """Phase 2: ``(rep rels, factors from rels to rep)`` over the minimal level set of ``rels``."""
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
    """``AutCanon(total, rep, phi)``: the Aut-minimal canonical representative and its witness."""
    pres = _two_gen(pres)
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
    return automorphism(p, q, level_cap) is not None
