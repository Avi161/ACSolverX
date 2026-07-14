"""Level-set expansion: close the ONE stated incompleteness of ``aut_search``.

``aut_search`` expands a single representative per Aut-class -- its Whitehead-minimal form --
and says so in its own docstring: ``children(phi(P)) != phi(children(P))`` for a general phi,
so one representative yields a SUBSET of the class's true out-edges.

This module expands **every member of the minimal level set** instead.

Soundness. A level-set member ``q`` satisfies ``q = psi(P)`` for some ``psi`` in Aut(F2), so
``P`` and ``q`` are the same problem. An edge ``P --psi--> q --move--> Q`` is therefore still an
ACA edge, exactly the kind ``aut_search`` already emits. It carries one extra automorphism in
its certificate.

Cost control. For a class whose minimal level set is exactly its signed-permutation orbit,
expanding the other members is **provably redundant**: a signed permutation is length-preserving,
hence commutes with rotation, inversion and free reduction, hence with every Definition 2.1 move,
so ``children(sigma P) == sigma(children(P))`` and every child lands in the same Aut-class.
Measured on the 126 class reps, that covers 122 of them -- so the expensive path fires on 4.
"""
from experiments.equivalence_classes.lib.acmoves import children
from experiments.equivalence_classes.lib.autcanon import AUTOS, peak_reduce
from experiments.equivalence_classes.lib.words import (
    SIGNED_PERMS, apply_hom, canon_pair, cyc_reduce,
)

_LVL = {}
_EXTRA = {}

stats = {"nodes": 0, "cheap": 0, "expanded": 0, "extra_members": 0}


def minimal_level_set(pair):
    """Every Aut-minimal-length member of the Aut(F2)-orbit of ``pair`` (memoised)."""
    _, red, _ = peak_reduce(pair)
    start = canon_pair(*red)
    hit = _LVL.get(start)
    if hit is not None:
        return hit
    total = len(start[0]) + len(start[1])
    seen = {start}
    stack = [start]
    while stack:
        node = stack.pop()
        for a in AUTOS:
            a1 = cyc_reduce(apply_hom(node[0], a))
            a2 = cyc_reduce(apply_hom(node[1], a))
            if len(a1) + len(a2) != total:
                continue
            nxt = canon_pair(a1, a2)
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    out = frozenset(seen)
    _LVL[start] = out
    return out


def extra_members(pair):
    """Level-set members no signed permutation of ``pair`` already produces.

    Empty when the level set IS the signed-permutation orbit -- the provably-redundant case.
    """
    key = canon_pair(*pair)
    hit = _EXTRA.get(key)
    if hit is not None:
        return hit
    orbit = set()
    for _, sigma in SIGNED_PERMS:
        orbit.add(canon_pair(apply_hom(key[0], sigma), apply_hom(key[1], sigma)))
    out = tuple(sorted(minimal_level_set(key) - orbit))
    _EXTRA[key] = out
    return out


def levelset_children(r1s, r2s, cap=48, cyclic=True, seam_only=False):
    """Drop-in replacement for ``acmoves.children`` that expands the whole level set."""
    stats["nodes"] += 1
    out = children(r1s, r2s, cap=cap, cyclic=cyclic, seam_only=seam_only)
    extra = extra_members((r1s, r2s))
    if not extra:
        stats["cheap"] += 1
        return out
    stats["expanded"] += 1
    stats["extra_members"] += len(extra)
    for member in extra:
        for child, mv in children(member[0], member[1], cap=cap, cyclic=cyclic,
                                  seam_only=seam_only).items():
            out.setdefault(child, mv)
    return out
