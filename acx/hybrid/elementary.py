"""A hybrid certificate written out as elementary (and stable) AC moves on the presentation itself.

The certificate (``HybridResult.steps``) mixes S-moves, automorphisms of F2 and higher-rank events (``dynrank``).
``certify`` replays each on a ``Frame`` (see ``frame.py``): an S-move conjugates and multiplies, an automorphism acts
on ``E`` only, a product, definition, elimination or transvection is spelled out below, and the tail destabilises
to ``<x, y | x, y>``. The path is long but deterministic, and ``acx.verify.replay`` checks it before it is returned.
"""
from ..core.moves import seam_cancels
from ..core.words import canonical_rels, conjugate, free, inverse, reduce, rotate, rotate_left, substitute_generator
from ..verify.replay import replay
from . import dynrank as D
from .frame import Frame
from .steps import Aut, aut_child, is_terminal, move_child


def _product(fr, words, ev):
    """Conjugate ``E_i`` into the rotation, multiply by the conjugate of ``E_j^s`` that is the second factor."""
    i, j, k1, k2 = ev["i"], ev["j"], ev["k1"], ev["k2"]
    target = words[i]
    base = words[j] if ev["sign"] == 1 else inverse(words[j])
    fr.set_word(i, rotate_left(target, k1))
    fr.cmul(i, j, rotate_left(base, k2))
    result = D.dcanon(rotate_left(target, k1) + rotate_left(base, k2))
    if result != tuple(ev["result"]):
        raise ValueError("product result differs")
    return D.normalize(words[:i] + (result,) + words[i + 1:])


def _define(fr, words, ev):
    """Stabilise (or reuse a parked unit relator), turn it into ``h^-1 a b``, then rewrite each ``a b`` of the relators
    as ``h`` by multiplying with a conjugate of that relator."""
    n, d = len(words), tuple(ev["digram"])
    h, a, b = n + 1, d[0], d[1]
    if ev["h"] != h or len(d) != 2 or any(abs(x) > n or x == 0 for x in d):
        raise ValueError("bad definition")
    if len(fr.E) == n:
        fr.stabilize()
    if fr.E[n] != (h,):
        raise AssertionError("no unit relator for the new generator")
    fr.transvect(h, abs(b), 1 if b > 0 else -1)
    fr.transvect(h, abs(a), 1 if a > 0 else -1)
    fr.permute({h: h}, {h: -1})                              # E_n = h^-1 a b
    expand = {h: d, -h: inverse(d)}
    for i, t in enumerate(ev["templates"]):
        t = tuple(t)
        fr.set_word(i, free(y for x in t for y in expand.get(x, (x,))))
        for p in reversed(range(len(t))):
            if abs(t[p]) == h:
                q, de = t[p + 1:], (d if t[p] > 0 else inverse(d))
                fr.cmul(i, n, conjugate(inverse(de) + (t[p],), q))
        if fr.E[i] != t:
            raise ValueError(f"template {t} does not expand to relator {words[i]}")
    return D.normalize(((-h,) + d,) + tuple(map(tuple, ev["templates"])))


def _eliminate(fr, words, ev):
    """Replace every ``g`` of the other relators by its image, make ``R_i`` the unit relator ``g`` (transvections),
    renumber so ``g`` is the last generator of the state, and park it."""
    i, g, n = ev["i"], ev["g"], len(words)
    raw, mine = D.eliminate(words, i, g)
    image = mine["image"]
    if image != tuple(ev["image"]):
        raise ValueError("elimination image differs")
    for k, w in enumerate(words):
        if k == i:
            continue
        for p in reversed(range(len(w))):
            if abs(w[p]) == g:
                f = 1 if w[p] > 0 else -1
                s = substitute_generator(w[p + 1:], g, image)
                fr.cmul(k, i, conjugate((-f * g,) + (image if f > 0 else inverse(image)), s))
        if fr.E[k] != substitute_generator(w, g, image):
            raise AssertionError("substitution differs")
    fr.set_word(i, (g,) + inverse(image))
    for x in reversed(image):                                # g -> g . image
        fr.transvect(g, abs(x), 1 if x > 0 else -1)
    fr.permute({x: (n if x == g else x - 1) for x in range(g, n + 1)}, {x: 1 for x in range(g, n + 1)})
    fr.swap(i, n - 1)                                        # park the unit relator x_n
    return D.normalize(raw)


def _transvection(fr, words, ev):
    """The Nielsen event ``x_i -> x_i x_j^s``: an automorphism of ``E`` only."""
    i, j, s = ev["i"], ev["j"], ev["sign"]
    if not (1 <= i <= len(words) and 1 <= j <= len(words) and i != j and s in (1, -1)):
        raise ValueError("bad transvection")
    fr.transvect(i, j, s)
    return D.normalize(D.transvection(w, i, j, s) for w in words)


EVENTS = {"product": _product, "define": _define, "eliminate": _eliminate, "nielsen": _transvection}


def certify(pres, steps):
    """Elementary moves taking ``pres`` to its trivial presentation along ``steps``; replayed before they are returned."""
    fr = Frame(pres)
    cur, dyn = canonical_rels(tuple(reduce(r) for r in pres.rels)), None
    for st in steps:
        if isinstance(st, dict):
            words = D.normalize(cur) if dyn is None else dyn
            fr.align(words)
            try:
                child = EVENTS[st["event"]["kind"]](fr, words, st["event"])
                rl = st["relabel"]
                if rl is not None:
                    fr.permute(rl["perm"], rl["signs"])
                    child = D.apply_relabel(child, rl["perm"], rl["signs"])
                stored = tuple(map(tuple, st["after"]))
            except (KeyError, IndexError, TypeError, AttributeError) as e:    # a field is missing or of the wrong kind
                raise ValueError(f"malformed higher-rank step: {e!r}") from e
            if child != stored:
                raise ValueError("replayed state differs from the stored state")
            cur, dyn = (canonical_rels(child), None) if len(child) == 2 else (cur, child)
        elif dyn is not None:
            raise ValueError(f"rank-two step {st} at rank {len(dyn)}")
        elif isinstance(st, Aut):
            fr.aut(st.k)
            cur = aut_child(cur, st.k)
        else:
            if not seam_cancels(cur, st):
                raise ValueError(f"S-move {st} does not cancel at the seam of {cur}")
            fr.align(cur)
            fr.set_word(st.i, rotate(cur[st.i], st.k1))
            src = cur[st.j] if st.s == 1 else inverse(cur[st.j])
            fr.cmul(st.i, st.j, rotate(src, st.k2))
            cur = move_child(cur, st)
    if dyn is not None or not is_terminal(cur):
        raise ValueError("the certificate does not end at a trivial pair")
    fr.finish(pres.n_gen)
    replay(pres, fr.w.ops, normalize=False)
    return fr.w.ops
