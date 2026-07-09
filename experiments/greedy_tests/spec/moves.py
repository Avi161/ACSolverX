"""The substitution (S-)move, generalised past two relators.

Definition 2.1 of the Two-Hump paper (``literature/txt/two_hump_paper.txt:229``)
parametrises a substitution by ``(i, j, k1, k2) in {1,2} x {-1,1} x Z x Z`` and
replaces ``r_i`` by ``rot_{k1}(r_i) . rot_{k2}(r_{3-i})^j``, keeping only seams
that cancel.

That definition does **not** survive a third relator: ``r_{3-i}`` means "the
other one", which is unique only when there are exactly two. The general move
must carry a real relator selector. Note the naming collision this creates --
the paper's and the codebase's ``j`` is the *invert exponent* (``+-1``); the
selector is a new index. Here the move is
``Move(i, j, s, k1, k2)`` with ``i`` the target, ``j != i`` the source, and
``s in {1,-1}`` the exponent:

    r_i <- rot_{k1}(r_i) . rot_{k2}(r_j ** s)

At ``n_rel == 2`` the enumeration order ``i -> j -> s -> k1 -> k2`` collapses to
``i -> s -> k1 -> k2``, which is exactly the order of
``get_neighbors_with_moves_nj`` and ``expand_node_nj``. The heap tie-breaks on
``depth``, which is fixed by first-visit order, so this order is load-bearing.
"""

from collections import namedtuple

from .presentation import Presentation
from .words import inverse, reduce_word, rotate

Move = namedtuple("Move", "i j s k1 k2")  # 0-based i, j


def source_word(relators, mv):
    return relators[mv.j] if mv.s == 1 else inverse(relators[mv.j])


def seam_cancels(relators, mv):
    """Definition 2.1's validity condition: the join must cancel."""
    ri = relators[mv.i]
    oj = source_word(relators, mv)
    if not ri or not oj:
        return False
    return rotate(ri, mv.k1)[-1] == -rotate(oj, mv.k2)[0]


def apply_move(relators, mv):
    """The raw (unreduced, uncanonicalised) child, exactly as the solver builds it."""
    piece = rotate(relators[mv.i], mv.k1) + rotate(source_word(relators, mv), mv.k2)
    out = list(relators)
    out[mv.i] = piece
    return tuple(out)


def enumerate_moves(pres):
    """Every ``(i, j, s, k1, k2)`` with a cancelling seam, in solver order."""
    rels = pres.relators
    for i in range(pres.n_rel):
        if not rels[i]:
            continue
        for j in range(pres.n_rel):
            if j == i:
                continue
            for s in (1, -1):
                oj = rels[j] if s == 1 else inverse(rels[j])
                if not oj:
                    continue
                for k1 in range(len(rels[i])):
                    for k2 in range(len(oj)):
                        mv = Move(i, j, s, k1, k2)
                        if seam_cancels(rels, mv):
                            yield mv


def neighbours(pres, cap, cyclic=True):
    """Canonical children surviving the per-relator length cap, in solver order.

    Over-cap children are dropped silently -- a no-op, never an error. This is
    the ``continue`` at ``expand_node_nj:557`` and the ``if len(...) <= cap``
    at ``GreedyBaselineSolver.solve:388``.
    """
    out = []
    for mv in enumerate_moves(pres):
        raw = apply_move(pres.relators, mv)
        red = tuple(reduce_word(r, cyclic) for r in raw)
        if any(len(r) > cap for r in red):
            continue
        out.append((Presentation(pres.n_gen, red).canonical(), mv))
    return out


def neighbour_set(pres, cap, cyclic=True):
    return {child.relators for child, _ in neighbours(pres, cap, cyclic)}


# -- interop with the 2-relator on-disk move encoding ------------------------


def move_to_legacy(mv, n_rel):
    """``Move`` -> the stored ``(target, jsign, k1, k2)``. Only defined at n_rel=2."""
    if n_rel != 2:
        raise ValueError("the stored move format cannot express n_rel != 2")
    return (mv.i + 1, mv.s, mv.k1, mv.k2)


def legacy_to_move(target, jsign, k1, k2):
    """``(target, jsign, k1, k2)`` -> ``Move``; the source is forced at n_rel=2."""
    i = target - 1
    return Move(i, 1 - i, jsign, k1, k2)
