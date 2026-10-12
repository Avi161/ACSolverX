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
    """The substitution table of ``beta``: it fixes the ``n`` source generators and sends each new ``h_k`` to
    ``beta(d_k) h_k``."""
    table = {sign * g: (sign * g,) for g in range(1, n + 1) for sign in (1, -1)}
    for k, digram in enumerate(digrams, 1):
        h = n + k
        table[h] = apply_table(digram, table) + (h,)
        table[-h] = inverse(table[h])
    return table


def _undefine(emitter, relators, defining, digram, h, table):
    """Undo one definition: rewrite ``relators[:defining]`` in place, using the defining relator ``relators[defining]``.

    Each relator is inverted and rotated as ``sac.rewrite`` chose; then every ``digram`` that became ``h`` (or its
    inverse that became ``H``) is produced by multiplying with a conjugate of the defining relator.
    """
    for i in range(defining):
        flip, rotation, rewritten = rewrite(relators[i], digram, h)
        if flip:
            emitter.invert(i)
        oriented = inverse(relators[i]) if flip else relators[i]
        emitter.conj(i, apply_table(oriented[:rotation], table))
        for j in reversed(range(len(rewritten))):
            if abs(rewritten[j]) == h:
                rest = rewritten[j + 1:] if rewritten[j] > 0 else inverse(digram) + rewritten[j + 1:]
                conjugator = apply_table(rest, table)
                emitter.conj(defining, conjugator)
                emitter.multiply(i, defining, 1 if rewritten[j] > 0 else -1)
                emitter.conj(defining, inverse(conjugator))
        relators[i] = rewritten


def _clean(emitter, n, n_defined):
    """Delete the letters before ``h_j`` from the relator ``beta(d_j) h_j`` of each defined generator.

    Each letter goes by multiplying with a conjugate of the unit relator of that letter.
    """
    for j in range(n + 1, n + n_defined + 1):
        while len(emitter.pres.rels[j - 1]) > 1:
            letter = emitter.pres.rels[j - 1][-2]
            emitter.conj(abs(letter) - 1, (j,))
            emitter.multiply(j - 1, abs(letter) - 1, -1 if letter > 0 else 1)
            emitter.conj(abs(letter) - 1, (-j,))


def lift(pres, sac, path, start, cyclic=True):
    """Elementary stable AC moves from ``pres`` to the trivial presentation, replayed before they are returned.

    ``path`` solves ``start`` (the canonical form of ``sac.root``); ``cyclic`` must be the search's setting.
    """
    n, n_defined = pres.n_gen, len(sac.digrams)
    table = beta_table(n, sac.digrams)
    emitter = Emitter(pres)
    for _ in range(n_defined):
        emitter.do({"op": "stabilize"})
    # T = the source plus the defining relators; beta maps T to the stabilised source.
    defining = [inverse(d) + (n + k,) for k, d in enumerate(sac.digrams, 1)]
    relators = list(sac.source.rels) + defining
    emitter.align(tuple(apply_table(w, table) for w in relators))
    for k, digram in enumerate(sac.digrams, 1):
        _undefine(emitter, relators, len(sac.source.rels) + k - 1, digram, n + k, table)
    for state, move in zip(replay(start, path, cyclic=cyclic), path):
        rels = canonical_rels(state.rels)
        emitter.align(tuple(apply_table(r, table) for r in rels))
        emitter.s_move(rels, Move(*move), table)
    emitter.align(tuple(table[g] for g in range(1, n + n_defined + 1)))
    _clean(emitter, n, n_defined)
    for _ in range(n_defined):
        emitter.do({"op": "destabilize"})
    replay(pres, emitter.moves, cyclic=cyclic, normalize=False)
    return emitter.moves
