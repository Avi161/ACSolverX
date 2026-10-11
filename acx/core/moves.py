"""The move set: substitution (S-)moves, elementary AC moves, AC4/AC5.

S-move (Two-Hump paper, Def. 2.1), generalised past two relators::

    Move(i, j, s, k1, k2):   r_i <- rot_{k1}(r_i) . rot_{k2}(r_j ** s)     (0-based i != j)

valid only when the seam cancels: the last letter of ``rot_{k1}(r_i)`` is the
inverse of the first letter of ``rot_{k2}(r_j ** s)``. The child is then reduced
and canonicalised (``acx.core.words``). ``rotate`` follows main's ``np.roll``
convention, so at two relators ``Move(t-1, 2-t, jsign, k1, k2)`` is main's
stored ``(target, jsign, k1, k2)`` and the enumeration order
``i -> j -> s -> k1 -> k2`` is main's ``get_neighbors_with_moves_nj`` order,
which the heap's depth tie-break depends on.

Elementary AC moves (dicts, the schema of
``origin/codex/ac-elementary-decoder:experiments/search/ac_decode.py``,
1-based relator indices, free reduction only, no canonicalisation):
``{"op": "invert", "target": t}``, ``{"op": "swap"[, "a": a, "b": b]}``,
``{"op": "conjugate", "target": t, "by": "x"}`` (``r_t <- by^-1 r_t by``),
``{"op": "multiply", "target": t, "source": s}`` (``r_t <- r_t r_s``).
Stable moves: ``{"op": "stabilize"}`` (AC4: add generator ``n+1`` and relator
``(n+1,)``) and ``{"op": "destabilize"}`` (AC5, its inverse).

Sources: ``origin/test/greedy-test-suite:experiments/greedy_tests/spec/
{moves,presentation}.py``; ``origin/main:experiments/search/greedy_baseline.py``.
"""
from collections import namedtuple

from .words import Presentation, canonical_rels, inverse, parse, reduce, rotate

Move = namedtuple("Move", "i j s k1 k2")


def from_legacy(target, jsign, k1, k2):
    """Main's 2-relator ``(target, jsign, k1, k2)`` (1-based target) -> ``Move``."""
    return Move(target - 1, 2 - target, jsign, k1, k2)


def to_legacy(m):
    if {m.i, m.j} != {0, 1}:
        raise ValueError("the legacy move format holds two relators only")
    return (m.i + 1, m.s, m.k1, m.k2)


def source_word(rels, m):
    return rels[m.j] if m.s == 1 else inverse(rels[m.j])


def seam_cancels(rels, m):
    ri, oj = rels[m.i], source_word(rels, m)
    return bool(ri) and bool(oj) and rotate(ri, m.k1)[-1] == -rotate(oj, m.k2)[0]


def apply_raw(rels, m):
    """The unreduced child, exactly as the search builds it."""
    out = list(rels)
    out[m.i] = rotate(rels[m.i], m.k1) + rotate(source_word(rels, m), m.k2)
    return tuple(out)


def enumerate_moves(rels):
    """Every seam-cancelling ``Move`` of ``rels``, in search order."""
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
    """Apply an S-move to the canonical form of ``pres``; return the reduced canonical child.

    The move's rotations index ``canonical_rels(pres.rels)`` (a search state is
    already canonical, so for search paths this is the stored state itself).
    Raises ``ValueError`` when the move is out of range or its seam does not cancel.
    """
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


def _idx(pres, t):
    if isinstance(t, bool) or not isinstance(t, int) or not 1 <= t <= len(pres.rels):
        raise ValueError(f"relator index {t!r} out of range")
    return t - 1


def _free(w):
    return reduce(w, cyclic=False)


def elementary_step(pres, op):
    """Apply one elementary AC or stable move (dict schema above)."""
    rels = list(pres.rels)
    kind = op.get("op")
    if kind == "invert":
        i = _idx(pres, op["target"])
        rels[i] = inverse(rels[i])
    elif kind == "swap":
        a, b = _idx(pres, op.get("a", 1)), _idx(pres, op.get("b", 2))
        rels[a], rels[b] = rels[b], rels[a]
    elif kind == "conjugate":
        i = _idx(pres, op["target"])
        c = parse(op["by"])
        if len(c) != 1 or abs(c[0]) > pres.n_gen:
            raise ValueError(f"conjugate by one generator letter, got {op['by']!r}")
        rels[i] = _free(inverse(c) + rels[i] + c)
    elif kind == "multiply":
        i, j = _idx(pres, op["target"]), _idx(pres, op["source"])
        if i == j:
            raise ValueError("multiply needs distinct target and source")
        rels[i] = _free(rels[i] + rels[j])
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


def step(pres, mv, cyclic=True):
    """Apply one path element: a ``Move`` (S-move) or an elementary/stable dict."""
    return elementary_step(pres, mv) if isinstance(mv, dict) else s_step(pres, Move(*mv), cyclic)


def encode_path(path):
    """JSON form: an S-move is the list ``[i, j, s, k1, k2]``, any other move its dict."""
    return [m if isinstance(m, dict) else list(m) for m in path]


def decode_path(items):
    """Inverse of ``encode_path``; also reads main's ``'target_jsign_k1_k2'`` strings."""
    out = []
    for m in items:
        if isinstance(m, dict):
            out.append(m)
        elif isinstance(m, str):
            out.append(from_legacy(*map(int, m.split("_"))))
        else:
            out.append(Move(*m))
    return out

