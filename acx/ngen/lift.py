"""Lift a solve of the SAC root to elementary stable AC moves on the source, replayed before they are returned.

``lift(pres, sac, path, start)`` takes the S-moves of a solve of ``sac.root`` to moves on ``pres`` that reach the
trivial presentation, so ``acx.verify.replay`` checks the claim. The construction is in ``docs/RANK3.md``.
"""
from ..aut.transport import Emitter
from ..aut.whitehead import apply_table
from ..core.moves import Move
from ..core.words import canonical_rels, inverse
from ..verify.replay import replay
from .sac import rewrite


def beta_table(n, digrams):
    """The substitution table of ``beta`` (fixes the source generators, sends each new ``h_k`` to ``beta(d_k) h_k``)."""
    tab = {s * g: (s * g,) for g in range(1, n + 1) for s in (1, -1)}
    for k, d in enumerate(digrams, 1):
        h = n + k
        tab[h] = apply_table(d, tab) + (h,)
        tab[-h] = inverse(tab[h])
    return tab


def _undefine(em, virt, src, d, h, tab):
    """Undo one definition: rewrite ``virt[:src]`` in place with the emitter, using the defining relator ``virt[src]``."""
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
    """Elementary stable AC moves from ``pres`` to the trivial presentation, replayed before they are returned.

    ``path`` solves ``start`` (the canonical form of ``sac.root``); ``cyclic`` must be the search's setting.
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
