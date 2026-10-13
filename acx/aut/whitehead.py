"""Whitehead's algorithm on F2: the Aut(F2)-canonical form of a presentation, with its witness.

``aut_canon(pres)`` gives ``AutCanon(total, rep, phi)``: the least canonical presentation of the Aut(F2)-orbit and
the factors ``phi`` (indices into ``AUTOS``, the first acts first) with ``canonical(phi(pres)) == rep`` (``check``).
Words are ``acx`` int tuples; two generators, any number of relators. The automorphisms are in ``autos``.
"""
from collections import namedtuple

from ..core.priority import length
from ..core.words import Presentation, canonical_rels, reduce, state_key
from .autos import AUTOS, DESCENT, TABLES, apply_pres, apply_table, invert

AutCanon = namedtuple("AutCanon", "total rep phi")


def _image(rels, k):
    """Every relator under ``AUTOS[k]``, cyclically reduced."""
    return tuple(reduce(apply_table(r, TABLES[k])) for r in rels)


def peak_reduce(rels):
    """Phase 1: ``(total, cyclically reduced rels, factors)`` at the orbit's minimal total cyclic length.

    Repeatedly applies the best of the 12 second-kind automorphisms (``DESCENT`` order, strict ``<``, ties to the
    earlier one), by lengths only: no canonical form is built on this hot path.
    """
    cur = tuple(reduce(r) for r in rels)
    total = length(cur)
    phi = []
    while True:
        best_k, best_total = None, total
        for k in DESCENT:
            t = length(_image(cur, k))
            if t < best_total:
                best_k, best_total = k, t
        if best_k is None:
            return total, cur, tuple(phi)
        cur, total = _image(cur, best_k), best_total
        phi.append(best_k)


def level_min(rels, level_cap=50_000):
    """Phase 2: ``(rep rels, factors from rels to rep)`` over the minimal level set of ``rels``.

    Depth-first over all 20 ``AUTOS`` at a fixed total; each node is canonical (``canonical_rels``) and ``rep`` is the
    least in ``state_key`` order (``X < Y < x < y``). The level set of a peak-reduced presentation is connected, so
    ``rep`` is a complete orbit invariant; a set over ``level_cap`` raises, since a partial one gives a wrong ``rep``.
    """
    start = canonical_rels(rels)
    level_total = length(start)
    came_from = {start: None}            # node -> (parent node, auto index); the start has no parent
    stack = [start]
    while stack:
        if len(came_from) > level_cap:
            raise RuntimeError(f"minimal level set exceeds level_cap={level_cap}; rep unreliable")
        node = stack.pop()
        for k in range(len(AUTOS)):
            child = _image(node, k)
            if length(child) != level_total:
                continue
            child = canonical_rels(child)
            if child not in came_from:
                came_from[child] = (node, k)
                stack.append(child)
    rep = min(came_from, key=state_key)
    factors, node = [], rep
    while came_from[node] is not None:
        node, k = came_from[node]
        factors.append(k)
    return rep, tuple(reversed(factors))


def aut_canon(pres, level_cap=50_000):
    """``AutCanon(total, rep, phi)``: the Aut-minimal canonical representative and its witness.

    The factors (not only their composed images) are kept so that ``acx.aut.transport`` can realise ``phi`` by AC moves.
    """
    if pres.n_gen != 2:
        raise ValueError(f"Whitehead's algorithm here is for F2, got {pres.n_gen} generators")
    total, reduced, peak_phi = peak_reduce(pres.rels)
    rep, level_phi = level_min(reduced, level_cap)
    return AutCanon(total, Presentation(2, rep), peak_phi + level_phi)


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
