"""Lift a solve of the SAC root to a replayable stable AC path on the source presentation.

A solve of ``sac.root`` is a path of S-moves on a presentation that is only
*stably* related to the source. This module expands it into elementary moves
(``acx.core.moves``: stabilize, conjugate by a letter, multiply, invert, swap,
destabilize) that take the source's own words to the trivial presentation, so
the claim needs no trust in the transform: ``acx.verify.replay``
checks it. The method is ``acx.aut.transport``'s, with an automorphism of the
free group on all ``n + m`` generators in place of one of F2.

Notation: ``t_k = d_k^-1 h_k`` is the k-th defining relator, ``U = (r.., h_1..h_m)``
the source after ``m`` stabilizations and ``T = (r.., t_1..t_m)``. Let ``beta``
fix the source generators and send ``h_k`` to ``beta(d_k) h_k``; it is an
automorphism and ``beta(t_k) = h_k``, so ``beta(T) = U`` exactly. AC moves are
equivariant under it (a conjugation by ``g`` becomes one by the word
``beta(g)``), so a path from ``T`` becomes a path from ``U`` with the same
shape. The path from ``T`` is:

1. **undefine**, definition by definition (``k = 1..m``): in every relator of
   the current state, invert and rotate as ``sac.rewrite`` chose, then turn
   each ``d`` into ``h_k`` by multiplying with ``Q^-1 t_k Q``, where ``Q`` is the
   rest of the word, and each ``d^-1`` into ``H_k`` by multiplying with
   ``Q^-1 d h_k^-1 Q``, the conjugate of ``t_k^-1`` by ``d^-1 Q``; this reaches
   ``sac.root`` from ``T``;
2. **solve** the root with the search's S-moves, each expanded as in
   ``transport`` (align to the canonical form, conjugate the source, multiply,
   conjugate back); the end is the basis ``(x, y, h_1, .., h_m)`` up to ``beta``;
3. **clean**: the relator of ``h_j`` is ``beta(d_j) h_j``; its letters before
   ``h_j`` are deleted one at a time by multiplying with a conjugate of the unit
   relator of that letter (all earlier relators are already units);
4. **destabilize** ``m`` times.

The length is large (a conjugation costs one move per letter and ``beta(h_k)``
grows with the nesting of the definitions) but deterministic; nothing searches.
"""
from ..aut.transport import Emitter
from ..aut.whitehead import apply_table
from ..core.moves import Move
from ..core.words import canonical_rels, inverse
from ..verify.replay import replay
from .sac import rewrite


def beta_table(n, digrams):
    """The substitution table of ``beta``: letter -> word, for all ``n + len(digrams)`` generators."""
    tab = {s * g: (s * g,) for g in range(1, n + 1) for s in (1, -1)}
    for k, d in enumerate(digrams, 1):
        h = n + k
        tab[h] = apply_table(d, tab) + (h,)
        tab[-h] = inverse(tab[h])
    return tab


def _undefine(em, virt, src, d, h, tab):
    """Step 1 for one definition: rewrite ``virt[:src]`` (in place), using the defining relator ``virt[src]``."""
    for i in range(src):
        flip, c, new = rewrite(virt[i], d, h)
        if flip:
            em.invert(i)
        w = inverse(virt[i]) if flip else virt[i]
        em.conj(i, apply_table(w[:c], tab))                    # rotate: conjugate by the prefix
        for j in reversed(range(len(new))):
            if abs(new[j]) == h:
                q = apply_table(new[j + 1:] if new[j] > 0 else inverse(d) + new[j + 1:], tab)
                em.conj(src, q)
                em.multiply(i, src, 1 if new[j] > 0 else -1)
                em.conj(src, inverse(q))
        virt[i] = new


def lift(pres, sac, path, start, cyclic=True):
    """Elementary stable AC moves from ``pres`` to ``<x_1..x_n | x_1..x_n>``, replayed before they are returned.

    ``path`` solves ``start`` (the canonical form of ``sac.root``) under ``acx.verify.replay``.
    """
    n, m = pres.n_gen, len(sac.digrams)
    tab = beta_table(n, sac.digrams)
    em = Emitter(pres)
    for _ in range(m):
        em.do({"op": "stabilize"})
    defs = [inverse(d) + (n + k,) for k, d in enumerate(sac.digrams, 1)]
    virt = list(sac.source.rels) + defs                   # T, mapped to U by beta
    em.align(tuple(apply_table(w, tab) for w in virt))
    for k, d in enumerate(sac.digrams, 1):
        _undefine(em, virt, len(sac.source.rels) + k - 1, d, n + k, tab)
    for s, mv in zip(replay(start, path, cyclic=cyclic), path):
        rels = canonical_rels(s.rels)
        em.align(tuple(apply_table(r, tab) for r in rels))
        em.s_move(rels, Move(*mv), tab)
    em.align(tuple(tab[g] for g in range(1, n + m + 1)))
    for j in range(n + 1, n + m + 1):
        while len(em.pres.rels[j - 1]) > 1:
            a = em.pres.rels[j - 1][-2]
            em.conj(abs(a) - 1, (j,))
            em.multiply(j - 1, abs(a) - 1, -1 if a > 0 else 1)
            em.conj(abs(a) - 1, (-j,))
    for _ in range(m):
        em.do({"op": "destabilize"})
    replay(pres, em.moves, cyclic=cyclic, normalize=False)
    return em.moves
