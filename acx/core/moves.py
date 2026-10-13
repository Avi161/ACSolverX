"""The moves: S-moves (``Move``) of the search and the elementary AC / stable moves (dicts) of certificates.

S-move ``Move(i, j, s, k1, k2)``: ``r_i <- rot_k1(r_i) . rot_k2(r_j ** s)`` (0-based, ``i != j``), legal when the
seam cancels; the child is reduced and canonicalised. Elementary moves are the dicts of ``elementary_step``.
"""
from collections import namedtuple

from .words import Presentation, canonical_rels, conjugate, free, inverse, parse, reduce, rotate, to_char

Move = namedtuple("Move", "i j s k1 k2")


def from_legacy(target, jsign, k1, k2):
    """The baseline's two-relator move ``(target, jsign, k1, k2)`` (1-based target) as a ``Move``."""
    return Move(target - 1, 2 - target, jsign, k1, k2)


def source_word(rels, m):
    """``r_j ** s`` of move ``m``."""
    return rels[m.j] if m.s == 1 else inverse(rels[m.j])


def seam_cancels(rels, m):
    """True when the last letter of ``rot_k1(r_i)`` is the inverse of the first of ``rot_k2(r_j ** s)``."""
    ri, oj = rels[m.i], source_word(rels, m)
    return bool(ri) and bool(oj) and rotate(ri, m.k1)[-1] == -rotate(oj, m.k2)[0]


def apply_raw(rels, m):
    """The unreduced child of move ``m``: ``rels`` with ``r_i`` replaced by ``rot_k1(r_i) . rot_k2(r_j ** s)``."""
    out = list(rels)
    out[m.i] = rotate(rels[m.i], m.k1) + rotate(source_word(rels, m), m.k2)
    return tuple(out)


def enumerate_moves(rels):
    """Every seam-cancelling ``Move`` of ``rels`` in search order ``i -> j -> s -> k1 -> k2`` (the heap's depth
    tie-break depends on it)."""
    n = len(rels)
    for i in range(n):
        ri = rels[i]
        if not ri:
            continue
        for j in range(n):
            if j == i or not rels[j]:
                continue
            for s in (1, -1):
                oj = rels[j] if s == 1 else inverse(rels[j])
                lo = len(oj)
                for k1 in range(len(ri)):
                    last = ri[(len(ri) - 1 - k1) % len(ri)]       # rotate(ri, k1)[-1]
                    for k2 in range(lo):
                        if oj[(-k2) % lo] == -last:               # rotate(oj, k2)[0]
                            yield Move(i, j, s, k1, k2)


def s_step(pres, m, cyclic=True):
    """Apply the S-move ``m`` to ``canonical_rels(pres.rels)`` (a search state is already canonical) and return the
    reduced canonical child; ``ValueError`` when the move is out of range or its seam does not cancel."""
    rels = canonical_rels(pres.rels)
    n = len(rels)
    if not (0 <= m.i < n and 0 <= m.j < n and m.i != m.j and m.s in (1, -1)):
        raise ValueError(f"bad relator indices in {m}")
    if not (0 <= m.k1 < len(rels[m.i]) and 0 <= m.k2 < len(rels[m.j])):
        raise ValueError(f"rotation out of range in {m}")
    if not seam_cancels(rels, m):
        raise ValueError(f"seam does not cancel: {m}")
    raw = apply_raw(rels, m)
    return Presentation(pres.n_gen, canonical_rels(tuple(reduce(r, cyclic) for r in raw)))


def _relator_index(pres, t):
    """Relator number ``t`` (1-based) as a list index."""
    if isinstance(t, bool) or not isinstance(t, int) or not 1 <= t <= len(pres.rels):
        raise ValueError(f"relator index {t!r} out of range")
    return t - 1


def _field(op, key):
    """``op[key]``; a move missing a field it needs is a ``ValueError`` that names it."""
    if key not in op:
        raise ValueError(f"{op.get('op')} needs {key!r}: {op!r}")
    return op[key]


def elementary_step(pres, op):
    """Apply one elementary AC or stable move to ``pres`` (1-based relator numbers, free reduction only):

    ``{"op": "invert", "target": t}``; ``{"op": "swap"[, "a": a, "b": b]}`` (default 1 and 2);
    ``{"op": "conjugate", "target": t, "by": "x"}`` (``r_t <- by^-1 r_t by``);
    ``{"op": "multiply", "target": t, "source": s}`` (``r_t <- r_t r_s``); ``{"op": "stabilize"}`` (AC4) and
    ``{"op": "destabilize"}`` (AC5). ``ValueError`` on anything malformed.
    """
    rels = list(pres.rels)
    kind = op.get("op")
    if kind == "invert":
        i = _relator_index(pres, _field(op, "target"))
        rels[i] = inverse(rels[i])
    elif kind == "swap":
        a, b = _relator_index(pres, op.get("a", 1)), _relator_index(pres, op.get("b", 2))
        rels[a], rels[b] = rels[b], rels[a]
    elif kind == "conjugate":
        i = _relator_index(pres, _field(op, "target"))
        c = parse(_field(op, "by"))
        if len(c) != 1 or abs(c[0]) > pres.n_gen:
            raise ValueError(f"conjugate by one generator letter, got {op['by']!r}")
        rels[i] = conjugate(rels[i], c)
    elif kind == "multiply":
        i = _relator_index(pres, _field(op, "target"))
        j = _relator_index(pres, _field(op, "source"))
        if i == j:
            raise ValueError("multiply needs distinct target and source")
        rels[i] = free(rels[i] + rels[j])
    elif kind == "stabilize":
        return stabilize(pres)
    elif kind == "destabilize":
        return destabilize(pres)
    else:
        raise ValueError(f"unknown move {op!r}")
    return Presentation(pres.n_gen, tuple(rels))


def stabilize(pres):
    """AC4: ``<x.. | r..>`` -> ``<x.., z | r.., z>``."""
    z = pres.n_gen + 1
    return Presentation(z, pres.rels + ((z,),))


def destabilize(pres):
    """AC5: drop the last generator ``z`` and one relator equal to ``z^{+-1}``; ``z`` may occur nowhere else."""
    z = pres.n_gen
    idx = [i for i, r in enumerate(pres.rels) if r in ((z,), (-z,))]
    if not idx:
        raise ValueError(f"no relator equal to generator {z}")
    keep = pres.rels[:idx[0]] + pres.rels[idx[0] + 1:]
    if any(abs(g) == z for r in keep for g in r):
        raise ValueError(f"generator {z} still occurs")
    return Presentation(z - 1, keep)


def is_elementary(mv):
    """A path element that is an elementary or stable move (a dict), not an S-move (a ``Move`` or its list)."""
    return isinstance(mv, dict)


def step(pres, mv, cyclic=True):
    """Apply one path element, a ``Move`` or an elementary/stable dict, to ``pres``."""
    return elementary_step(pres, mv) if is_elementary(mv) else s_step(pres, Move(*mv), cyclic)


class Trace:
    """A presentation and the elementary moves that produced it, each applied by ``elementary_step``
    (the emitter of ``acx.verify.decode``, ``acx.aut.transport`` and ``acx.ngen.lift``; ``t`` is 0-based)."""

    def __init__(self, pres, moves=()):
        self.pres, self.moves = pres, list(moves)

    def copy(self):
        """An independent trace at the same state."""
        return type(self)(self.pres, self.moves)

    def do(self, op):
        """Apply the elementary move ``op`` and record it."""
        self.pres = elementary_step(self.pres, op)
        self.moves.append(op)

    def conj(self, t, word):
        """``r_t <- c^-1 r_t c`` for the word ``c``, one generator letter at a time."""
        for g in word:
            self.do({"op": "conjugate", "target": t + 1, "by": to_char(g)})

    def invert(self, t):
        """``r_t <- r_t^-1``."""
        self.do({"op": "invert", "target": t + 1})

    def multiply(self, t, s, e=1):
        """``r_t <- r_t r_s^e``."""
        if e < 0:
            self.invert(s)
        self.do({"op": "multiply", "target": t + 1, "source": s + 1})
        if e < 0:
            self.invert(s)

    def conjugated_multiply(self, i, j, s, c):
        """``r_i <- r_i . (c^-1 r_j^s c)`` by inverting, conjugating and multiplying; ``r_j`` is left as it was."""
        if s < 0:
            self.invert(j)
        self.conj(j, c)
        self.multiply(i, j)
        self.conj(j, inverse(c))
        if s < 0:
            self.invert(j)


def encode_path(path):
    """JSON form: an S-move is the list ``[i, j, s, k1, k2]``, any other move its dict."""
    return [m if is_elementary(m) else list(m) for m in path]


def decode_path(items):
    """Inverse of ``encode_path``; also reads the baseline's ``'target_jsign_k1_k2'`` strings and the rank-n
    baseline's ``'i_j_s_k1_k2'`` strings."""
    out = []
    for m in items:
        if is_elementary(m):
            out.append(m)
        elif isinstance(m, str):
            fields = tuple(map(int, m.split("_")))
            if len(fields) not in (4, 5):
                raise ValueError(f"a path string has 4 or 5 fields, got {len(fields)}: {m!r}")
            out.append(Move(*fields) if len(fields) == 5 else from_legacy(*fields))
        else:
            out.append(Move(*m))
    return out

