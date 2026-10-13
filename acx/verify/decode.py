"""Decode a substitution (S-move) path into elementary AC moves (``decode``).

An S-move is expanded into conjugations that rotate the relators, one ``multiply`` (with ``invert`` and the undo
of the source's changes), and the canonical form of every relator again plus ``swap`` to sort them; the shortest
of the conjugator choices wins. Only ``cyclic=True`` S-moves are decoded. The JSON form of the result is in ``pack``.
"""
from ..core.moves import Move, Trace, is_elementary, step
from ..core.words import canonical_rels, canonical_word, inverse, reduce, rotate
from .replay import replay


def _rot_conjugators(w, k):
    """The words ``c`` with ``c^-1 w c = rotate(w, k)``: the prefix ``w[:n-k]`` and ``(w[n-k:])^-1``."""
    k %= len(w)
    return w[:len(w) - k], inverse(w[len(w) - k:])


def _oriented(w, sign):
    """``w`` for ``sign > 0``, its inverse otherwise."""
    return w if sign > 0 else inverse(w)


def _canonicalize_relator(tr, t):
    """Cyclically reduce ``r_t`` and bring it to ``canonical_word`` (cheapest orientation and rotation)."""
    w = tr.pres.rels[t]
    core = reduce(w)
    tr.conj(t, w[:(len(w) - len(core)) // 2])             # strip the free-reduction prefix
    if not core:
        return
    goal = canonical_word(core)
    plans = []                                            # (needs an inversion, shortest conjugator)
    for sign in (1, -1):
        oriented = _oriented(core, sign)
        for k in range(len(oriented)):
            if rotate(oriented, k) == goal:
                plans.append((sign < 0, min(_rot_conjugators(oriented, k), key=len)))
    flip, conjugator = min(plans, key=lambda plan: len(plan[1]) + plan[0])
    if flip:
        tr.invert(t)
    tr.conj(t, conjugator)


def _canonicalize(tr):
    """Every relator canonical, then sorted by swaps: ``canonical_rels``."""
    for t in range(len(tr.pres.rels)):
        _canonicalize_relator(tr, t)
    for p, goal in enumerate(canonical_rels(tr.pres.rels)):
        q = tr.pres.rels.index(goal, p)
        if q != p:
            tr.do({"op": "swap", "a": p + 1, "b": q + 1})


def _rotation_to(w, goal):
    """``(sign, k)`` with ``rotate(w ** sign, k) == goal``; literal, so ``w`` need not be cyclically reduced."""
    for sign in (1, -1):
        oriented = _oriented(w, sign)
        for k in range(len(oriented) or 1):
            if rotate(oriented, k) == goal:
                return sign, k
    raise ValueError(f"{w} is not a rotation of {goal} or its inverse")


def _frame(rels):
    """Per relator of ``canonical_rels(rels)`` (the words an S-move indexes): ``(t, sign, k)`` with
    ``rotate(rels[t] ** sign, k)`` equal to it."""
    unused = list(range(len(rels)))
    frame = []
    for goal in canonical_rels(rels):
        t = next(t for t in unused if canonical_word(rels[t]) == goal)
        unused.remove(t)
        frame.append((t, *_rotation_to(rels[t], goal)))
    return frame


def _expand_move(tr, m):
    """Append the shortest elementary expansion of the S-move ``m`` (ending canonical) to ``tr``.

    The move acts on ``canonical_rels(tr)``; ``_frame`` folds that rotation and inversion into the move's own
    rotations (``inverse(rotate(w, k)) = rotate(inverse(w), -k)``), so ``tr`` need not be canonical first.
    """
    frame = _frame(tr.pres.rels)
    (i, sign_i, k_i), (j, sign_j, k_j) = frame[m.i], frame[m.j]
    sign_j, k_j = sign_j * m.s, k_j * m.s
    target = _oriented(tr.pres.rels[i], sign_i)
    source = _oriented(tr.pres.rels[j], sign_j)
    best = None
    for c1 in _rot_conjugators(target, k_i + m.k1):
        for c2 in _rot_conjugators(source, k_j + m.k2):
            trial = tr.copy()
            if sign_i < 0:
                trial.invert(i)
            trial.conj(i, c1)
            trial.conjugated_multiply(i, j, sign_j, c2)
            _canonicalize(trial)
            if best is None or len(trial.moves) < len(best.moves):
                best = trial
    tr.pres, tr.moves = best.pres, best.moves


def decode(pres, path):
    """Elementary moves carrying ``pres`` along ``path`` (S-moves of a ``cyclic=True`` search; elementary or
    stable dict moves pass through unchanged).

    ``pres`` must be freely reduced. The result starts by bringing ``pres`` to the canonical form the search
    used, replays from ``pres`` with ``normalize=False`` and ends at the canonical trivial presentation.
    The S-move indexes ``canonical_rels`` of the current words and ``_frame`` locates those words in the
    decoder's state, so a path whose dict moves leave relators that are not cyclically reduced decodes too;
    each op is applied by ``elementary_step``, so the output is legal by construction. Raises ``ValueError`` on
    an illegal path and ``AssertionError`` if the decoded state ever differs from ``acx.core.moves.step``'s.
    """
    if any(reduce(r, cyclic=False) != r for r in pres.rels):
        raise ValueError(f"start must be freely reduced: {pres}")
    tr, expect = Trace(pres), pres.reduced().canonical()
    _canonicalize(tr)
    for mv in path:
        expect = step(expect, mv)
        if is_elementary(mv):
            tr.do(mv)
        else:
            _expand_move(tr, Move(*mv))
        if tr.pres != expect:
            raise AssertionError(f"decoder diverged at {mv!r}: {tr.pres} != {expect}")
    return tr.moves


def decode_and_replay(pres, path):
    """``(moves, states)``: the decoded moves and their replay on ``pres`` (raises ``ReplayError``)."""
    moves = decode(pres, path)
    return moves, replay(pres, moves, normalize=False)
