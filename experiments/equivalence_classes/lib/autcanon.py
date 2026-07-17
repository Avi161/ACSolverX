"""Whitehead canonical form of an Aut(F2)-orbit, **carrying the witnessing automorphism**.

``aut_canon(P)`` returns ``(total, rep, phi)`` with the guarantee

    canon_pair(phi(P))  ==  rep

so every claim this module makes ships its own proof: the verifier checks it by pure
substitution, without trusting peak reduction, the level-set BFS, or anything else in here.
``experiments/analysis/whitehead.py`` computes the same canonical form by the same theory but
without a witness; the two are cross-checked against each other in the tests.

Whitehead's algorithm, in two phases:
  1. **peak-reduce** to the orbit's minimal total length (a descent),
  2. **BFS the minimal level set** and take its lex-min -- a *complete* invariant of the orbit.

Performance note (this is what makes the sweep possible at all). Phase 1 only ever needs the
cyclically-reduced *length* of a candidate, never its canonical form, so it must not call
``canon_pair`` -- that is an O(n^2) rotation scan, and calling it for all 20 Whitehead
automorphisms on every descent step cost 11 ms per state, which is 16 h over the sweep.
Reducing instead of canonicalising inside the descent brings it to well under 1 ms.
Phase 2 does need ``canon_pair``, but only on the (small) minimal level set, and callers skip
phase 2 entirely for states whose phase-1 length already exceeds the search cap.
"""
from experiments.equivalence_classes.lib.words import (
    abelian_det, apply_hom, canon_pair, cyc_reduce, free_reduce,
)

ID = {"x": "x", "y": "y"}


def compose(f, g):
    """The automorphism ``x -> f(g(x))`` -- apply g first, then f."""
    return {"x": apply_hom(g["x"], f), "y": apply_hom(g["y"], f)}


def _whitehead_autos():
    """The 8 first-kind (signed permutations) + 12 second-kind Whitehead automorphisms of F2."""
    autos = []
    for fx in ("x", "X", "y", "Y"):
        for fy in ("x", "X", "y", "Y"):
            if fx.lower() == fy.lower():
                continue
            autos.append({"x": fx, "y": fy})
    autos.extend([
        {"x": "x", "y": "yx"}, {"x": "x", "y": "Xy"}, {"x": "x", "y": "Xyx"},
        {"x": "x", "y": "yX"}, {"x": "x", "y": "xy"}, {"x": "x", "y": "xyX"},
        {"x": "xy", "y": "y"}, {"x": "Yx", "y": "y"}, {"x": "Yxy", "y": "y"},
        {"x": "xY", "y": "y"}, {"x": "yx", "y": "y"}, {"x": "yxY", "y": "y"},
    ])
    return autos


AUTOS = _whitehead_autos()
# The 12 second-kind autos are the only ones that can change total length; the 8 signed
# permutations are length-preserving, so the descent never needs to try them.
DESCENT = AUTOS[8:]


def _reduce_pair(pair, a):
    r1 = cyc_reduce(apply_hom(pair[0], a))
    r2 = cyc_reduce(apply_hom(pair[1], a))
    return (r1, r2)


def peak_reduce(pair):
    """Descend to the orbit's minimal total length. Returns (total, pair, phi)."""
    cur = (cyc_reduce(pair[0]), cyc_reduce(pair[1]))
    tot = len(cur[0]) + len(cur[1])
    phi = dict(ID)
    while True:
        best = None
        best_t = tot
        for a in DESCENT:
            nxt = _reduce_pair(cur, a)
            t = len(nxt[0]) + len(nxt[1])
            if t < best_t:
                best, best_t = (nxt, a), t
        if best is None:
            return tot, cur, phi
        cur, a = best
        tot = best_t
        phi = compose(a, phi)


def level_min(pair, phi, level_cap=50_000):
    """Lex-min of the minimal level set containing ``pair``. Returns (rep, phi_to_rep).

    ``pair`` must already be peak-reduced. BFS over automorphisms that PRESERVE the total
    length; the resulting set is the orbit's minimal level set, and its lex-min (under Python's
    default string order) is a complete invariant of the Aut(F2)-orbit. Raises if the set
    exceeds ``level_cap`` -- a partial ``rep`` would be a silently wrong invariant.
    """
    start = canon_pair(*pair)
    t = len(start[0]) + len(start[1])
    seen = {start: phi}
    stack = [(start, phi)]
    while stack:
        if len(seen) > level_cap:
            raise RuntimeError(f"minimal level set exceeds level_cap={level_cap}; rep unreliable")
        node, nphi = stack.pop()
        for a in AUTOS:
            r1 = cyc_reduce(apply_hom(node[0], a))
            r2 = cyc_reduce(apply_hom(node[1], a))
            if len(r1) + len(r2) != t:
                continue
            nxt = canon_pair(r1, r2)
            if nxt not in seen:
                cphi = compose(a, nphi)
                seen[nxt] = cphi
                stack.append((nxt, cphi))
    rep = min(seen)
    return rep, seen[rep]


def aut_canon(pair, level_cap=50_000):
    """(total, rep, phi) with canon_pair(phi(pair)) == rep. ``rep`` is Aut-minimal."""
    t, red, phi = peak_reduce(pair)
    rep, phi = level_min(red, phi, level_cap)
    return t, rep, phi


def aut_min_len(pair):
    """Just the Aut-minimal total length -- the cheap phase-1-only pre-filter."""
    return peak_reduce(pair)[0]


def check(pair, rep, phi):
    """The certificate check, by pure substitution. Trusts nothing above."""
    return canon_pair(apply_hom(pair[0], phi), apply_hom(pair[1], phi)) == rep


def phi_str(phi):
    return f"x->{phi['x']}, y->{phi['y']}"


def is_automorphism(phi):
    x, y = free_reduce(phi["x"]), free_reduce(phi["y"])
    return abelian_det(x, y) in (1, -1) and peak_reduce((x, y))[0] == 2
