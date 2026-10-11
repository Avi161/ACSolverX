"""Decode a substitution (S-move) path into elementary AC moves.

An S-move ``Move(i, j, s, k1, k2)`` is one step of the search: ``r_i <- rot_k1(r_i) . rot_k2(r_j ** s)``,
reduced and canonicalised. The elementary schema (``acx.core.moves.elementary_step``) has only
``invert``, ``swap``, ``conjugate`` (by one generator letter) and ``multiply`` (free reduction only,
nothing is rotated, cyclically reduced or sorted for us), so one S-move expands into

1. conjugations that rotate the relators (``rot_k(w) = c^-1 w c`` for ``c = w[:n-k]`` or ``c = (w[n-k:])^-1``),
2. ``invert`` of the source when ``s = -1``, one ``multiply``, and the undo of the source's changes,
3. the canonical form of every relator again (strip the cyclic tail by conjugating, ``invert`` when the
   least element of the orbit is the inverse, rotate by conjugating) and ``swap`` to sort them.

Both conjugator choices of each side are tried and the shortest whole expansion wins. The source's single
"conjugated multiply" ``r_i . (c^-1 o_j c)`` with ``c = p u^-1`` (``r_i`` not rotated) is a valid plan too but
gives 6,302 elementary moves on the 60 test paths against 1,727 here, so it is not kept.
The S-move indexes ``canonical_rels`` of the current words; ``_frame`` locates those words in the decoder's
state (a literal rotation and inversion), so a path whose dict moves leave relators that are not cyclically
reduced decodes too. Because the decoder applies each op with ``elementary_step`` itself, the output is legal
by construction, and the state after every path element is checked against ``acx.core.moves.step``.

The decoded path starts at the raw (freely reduced) presentation, replays with ``normalize=False``, and
ends at the canonical trivial presentation. Elementary or stable dict moves inside the path are passed
through unchanged. Only ``cyclic=True`` S-moves are decoded: the search default. A Whitehead /
automorphism transport leg lives in ``acx.aut.transport``; this module does not know about it.

Port of ``origin/codex/ac-elementary-decoder:experiments/search/ac_decode.py`` (``decode_elementary``,
``_emit_canonicalization``, ``replay_elementary``) and ``decode_ac_jsonl.py`` (the packed ``I/S/C/M``
JSONL form: ``pack`` / ``unpack``), rewritten for n relators and the acx word and move types.
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


def _conjugated_multiply(tr, i, j, s, c):
    """``r_i <- r_i . (c^-1 r_j^s c)``; ``r_j`` is left as it was."""
    if s < 0:
        tr.invert(j)
    tr.conj(j, c)
    tr.multiply(i, j)
    tr.conj(j, inverse(c))
    if s < 0:
        tr.invert(j)


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
            _conjugated_multiply(t, i, j, sj, c2)
            _canonicalize(t)
            if best is None or len(t.moves) < len(best.moves):
                best = t
    tr.pres, tr.moves = best.pres, best.moves


def decode(pres, path):
    """Elementary moves carrying ``pres`` along ``path`` (S-moves of a ``cyclic=True`` search, dicts allowed).

    The result replays from ``pres`` with ``normalize=False`` and starts by bringing ``pres`` to the
    canonical form the search used. ``pres`` must be freely reduced. Raises ``ValueError`` on an illegal path.
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
    return [{"op": _OP[c], **dict(zip(_FIELDS[_OP[c]], args))} for c, *args in items]
