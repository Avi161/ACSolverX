"""Decode a substitution (S-move) path into elementary AC moves (``decode``) and pack them for JSON (``pack``).

An S-move is expanded into conjugations that rotate the relators, one ``multiply`` (with ``invert`` and the undo
of the source's changes), and the canonical form of every relator again plus ``swap`` to sort them; the shortest
of the conjugator choices wins. Only ``cyclic=True`` S-moves are decoded.
"""
from ..core.moves import Move, Trace, step
from ..core.words import canonical_rels, canonical_word, inverse, reduce, rotate
from .replay import replay


def _rot_conjugators(w, k):
    """The words ``c`` with ``c^-1 w c = rotate(w, k)``: the prefix ``w[:n-k]`` and ``(w[n-k:])^-1``."""
    k %= len(w)
    return w[:len(w) - k], inverse(w[len(w) - k:])


def _canonicalize_relator(tr, t):
    """Cyclically reduce ``r_t`` and bring it to ``canonical_word`` (cheapest orientation and rotation)."""
    w = tr.pres.rels[t]
    core = reduce(w)
    tr.conj(t, w[:(len(w) - len(core)) // 2])
    if not core:
        return
    goal = canonical_word(core)
    plans = [(sign < 0, min(_rot_conjugators(o, k), key=len))
             for sign, o in ((1, core), (-1, inverse(core)))
             for k in range(len(o)) if rotate(o, k) == goal]
    flip, c = min(plans, key=lambda p: len(p[1]) + p[0])
    if flip:
        tr.invert(t)
    tr.conj(t, c)


def _canonicalize(tr):
    """Every relator canonical, then sorted by swaps: ``canonical_rels``."""
    for t in range(len(tr.pres.rels)):
        _canonicalize_relator(tr, t)
    for p, g in enumerate(canonical_rels(tr.pres.rels)):
        q = tr.pres.rels.index(g, p)
        if q != p:
            tr.do({"op": "swap", "a": p + 1, "b": q + 1})


def _frame(rels):
    """Per relator of ``canonical_rels(rels)`` (the words an S-move indexes): ``(t, sign, k)`` with
    ``rotate(rels[t] ** sign, k)`` equal to it. Literal, so it holds for words that are not cyclically reduced."""
    free, out = list(range(len(rels))), []
    for u in canonical_rels(rels):
        t = next(t for t in free if canonical_word(rels[t]) == u)
        free.remove(t)
        out.append(next((t, sg, k) for sg, o in ((1, rels[t]), (-1, inverse(rels[t])))
                        for k in range(len(o) or 1) if rotate(o, k) == u))
    return out


def _expand_move(tr, m):
    """Append the shortest elementary expansion of the S-move ``m`` (ending canonical) to ``tr``.

    The move acts on ``canonical_rels(tr)``; ``_frame`` folds that rotation and inversion into the move's own
    rotations (``inverse(rotate(w, k)) = rotate(inverse(w), -k)``), so ``tr`` need not be canonical first.
    """
    fr = _frame(tr.pres.rels)
    (i, si, ki), (j, sj, kj) = fr[m.i], fr[m.j]
    sj, kj = sj * m.s, kj * m.s
    ri, oj = (w if sg > 0 else inverse(w) for w, sg in ((tr.pres.rels[i], si), (tr.pres.rels[j], sj)))
    best = None
    for c1 in _rot_conjugators(ri, ki + m.k1):
        for c2 in _rot_conjugators(oj, kj + m.k2):
            t = tr.copy()
            if si < 0:
                t.invert(i)
            t.conj(i, c1)
            t.conjugated_multiply(i, j, sj, c2)
            _canonicalize(t)
            if best is None or len(t.moves) < len(best.moves):
                best = t
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
        if isinstance(mv, dict):
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


_FIELDS = {"invert": ("target",), "swap": ("a", "b"), "conjugate": ("target", "by"),
           "multiply": ("target", "source"), "stabilize": (), "destabilize": ()}
_CODE = dict(zip(_FIELDS, "ISCMZD"))
_OP = {c: op for op, c in _CODE.items()}


def pack(moves):
    """Compact JSON form (``decode_ac_jsonl``'s): ``["I", t]``, ``["S", a, b]`` (``["S"]``: swap 1 and 2),
    ``["C", t, letter]``, ``["M", t, s]``, ``["Z"]``, ``["D"]``."""
    return [[_CODE[m["op"]], *(m[k] for k in _FIELDS[m["op"]] if k in m)] for m in moves]


def unpack(items):
    """Inverse of ``pack``."""
    return [{"op": _OP[c], **dict(zip(_FIELDS[_OP[c]], args))} for c, *args in items]
