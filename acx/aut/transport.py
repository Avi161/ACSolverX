"""Certificate transport: a solve of an automorphic image becomes an AC path on the original row.

``transport(pres, phi, path, start)``: ``path`` solves ``start`` (it replays
from ``start`` under ``acx.verify.replay``), and ``start``'s relators are those
of ``phi(pres)`` up to conjugating, inverting and reordering (for example
``start = aut_canon(pres).rep``). The result is a list of elementary AC moves
(``invert``, ``swap``, ``conjugate`` by a letter, ``multiply``: the dict schema
of ``acx.core.moves``) that takes ``pres``'s own words to ``<x, y | x, y>``; it
is replayed with ``replay(pres, moves, normalize=False)`` before it is returned.
No new move type is needed.

Why it works. Let ``psi = phi^-1``. We keep the invariant that the current
words are exactly ``psi`` of the current state of ``path`` (freely reduced):

* **Align**: words that are ``psi`` of the state up to conjugation, inversion
  and order are brought to it exactly by ``swap``, ``invert`` and conjugation
  (a word, letter by letter). This absorbs the search's reduce/canonicalise.
* **S-move** ``r_i <- rot_k1(r_i) . rot_k2(r_j^s)``: since ``rot_k(w) =
  u^-1 w u`` with ``u`` the length ``|w|-k`` prefix, the child is conjugate to
  ``r_i . c^-1 r_j^s c`` with ``c = p u^-1`` (``p`` the prefix of ``r_j^s``).
  AC moves are Aut-equivariant, so in the original frame it is
  ``w_i <- w_i . psi(c)^-1 w_j^s psi(c)``: conjugate ``w_j``, multiply,
  conjugate back. An elementary dict move maps to itself (``conjugate`` by
  ``g`` becomes conjugation by the word ``psi(g)``).
* **Tail**: the path ends at single letters, so the words end at the basis
  ``(psi(x), psi(y))``. Precomposing a tuple with an elementary automorphism
  ``a`` (``T -> T o a``) is a Nielsen move, i.e. AC moves; doing it for the
  factors of ``phi`` last-first gives ``psi o phi = id``: the words ``x, y``.

The path is long in letters (each conjugation is one move per letter), but
deterministic: nothing here searches.

Sources: ``origin/claude/ac19-leftover-solver-notebook-6yan6d:experiments/
search/transport_ac19_orig.py`` (transport of an original's path onto its
representative, equivariance argument) and ``origin/codex/ac-elementary-
decoder:experiments/search/ac_decode.py`` (the elementary move schema and the
conjugator form ``c = p u^-1`` of an S-move). The Nielsen tail there was a
best-first search (``reduce_basis``); here it is read off ``phi``'s factors.
"""
from ..core.config import SearchConfig
from ..core.moves import Move, elementary_step
from ..core.words import canonical_rels, canonical_word, fmt, inverse, parse, reduce
from ..verify.replay import replay
from .whitehead import AUTOS, _apply, _table, aut_canon, images, invert


def _strip(w):
    """``w = a C a^-1`` with ``C`` cyclically reduced: return ``(a, C)``."""
    w = reduce(w, cyclic=False)
    c = reduce(w)
    return w[:(len(w) - len(c)) // 2], c


def _witness(w, t):
    """``(sign, c)`` with ``c^-1 w^sign c == t`` after free reduction."""
    a, cw = _strip(w)
    b, ct = _strip(t)
    for sign, cs in ((1, cw), (-1, inverse(cw))):
        for k in range(max(len(cs), 1)):
            if cs[k:] + cs[:k] == ct:
                return sign, reduce(a + cs[:k] + inverse(b), cyclic=False)
    raise ValueError(f"{fmt(w)} is not conjugate to {fmt(t)} or its inverse")


class _Emitter:
    """The current words and the elementary moves that produced them (applied by ``elementary_step``)."""

    def __init__(self, pres):
        self.pres, self.ops = pres, []

    def op(self, **mv):
        self.pres = elementary_step(self.pres, mv)
        self.ops.append(mv)

    def conj(self, t, word):
        for g in word:
            self.op(op="conjugate", target=t + 1, by=fmt((g,)))

    def invert(self, t):
        self.op(op="invert", target=t + 1)

    def multiply(self, t, s, e=1):
        """``w_t <- w_t w_s^e``."""
        if e < 0:
            self.invert(s)
        self.op(op="multiply", target=t + 1, source=s + 1)
        if e < 0:
            self.invert(s)

    def align(self, target):
        """Make the words exactly ``target`` (each conjugate to a target word or its inverse)."""
        key = [canonical_word(reduce(w)) for w in self.pres.rels]
        for m, t in enumerate(target):
            want = canonical_word(reduce(t))
            src = next((l for l in range(m, len(key)) if key[l] == want), None)
            if src is None:
                raise ValueError(f"no relator of {self.pres} matches {fmt(t)}")
            if src != m:
                self.op(op="swap", a=m + 1, b=src + 1)
                key[m], key[src] = key[src], key[m]
            if self.pres.rels[m] == t:
                continue
            sign, c = _witness(self.pres.rels[m], t)
            if sign < 0:
                self.invert(m)
            self.conj(m, c)

    def s_move(self, rels, m, tab):
        """The S-move ``m`` on canonical ``rels``, transported by the substitution table ``tab``."""
        o = rels[m.j] if m.s == 1 else inverse(rels[m.j])
        c = _apply(reduce(o[:len(o) - m.k2] + inverse(rels[m.i][:len(rels[m.i]) - m.k1]), cyclic=False), tab)
        if m.s < 0:
            self.invert(m.j)
        self.conj(m.j, c)
        self.multiply(m.i, m.j)
        self.conj(m.j, inverse(c))
        if m.s < 0:
            self.invert(m.j)

    def dict_move(self, mv, tab):
        if mv["op"] in ("stabilize", "destabilize"):
            raise ValueError("transport through Aut(F2) cannot carry stable moves")
        if mv["op"] == "conjugate":
            return self.conj(mv["target"] - 1, _apply(parse(mv["by"]), tab))
        self.op(**mv)

    def precompose(self, a):
        """``T -> T o a`` for a Whitehead automorphism ``a`` (tuple Nielsen moves)."""
        if all(len(img) == 1 for img in a):                      # signed permutation
            if abs(a[0][0]) == 2:
                self.op(op="swap")
            for t in (0, 1):
                if a[t][0] < 0:
                    self.invert(t)
            return
        t = next(t for t in (0, 1) if len(a[t]) > 1)            # a[t] = L . gen_t . R
        img, o = a[t], 1 - t
        at = img.index(t + 1)
        for g in img[:at]:                                       # w_t <- w_o^e w_t
            self.invert(t)
            self.multiply(t, o, -1 if g > 0 else 1)
            self.invert(t)
        for g in img[at + 1:]:                                   # w_t <- w_t w_o^e
            self.multiply(t, o, 1 if g > 0 else -1)


def transport(pres, phi, path, start, cyclic=True):
    """Elementary AC moves solving ``pres``, from ``path`` solving ``start`` ~ ``phi(pres)``."""
    if pres.n_gen != 2 or start.n_gen != 2:
        raise ValueError("transport through Aut(F2) needs two generators")
    psi = images(invert(phi))
    tab = _table(psi)
    em = _Emitter(pres)
    states = replay(start, path, cyclic=cyclic)
    for s, mv in zip(states, path):
        if isinstance(mv, dict):
            em.align(tuple(_apply(r, tab) for r in s.rels))
            em.dict_move(mv, tab)
        else:
            rels = canonical_rels(s.rels)
            em.align(tuple(_apply(r, tab) for r in rels))
            em.s_move(rels, Move(*mv), tab)
    em.align(psi)                                              # the basis (psi(x), psi(y))
    for k in reversed(phi):
        em.precompose(AUTOS[k])
    replay(pres, em.ops, cyclic=cyclic, normalize=False)
    return em.ops


def solve_via_aut_min(pres, cfg=None, **overrides):
    """Search the Aut-minimal representative of ``pres``; return ``(result, elementary path or None)``.

    The representative's path is transported to ``pres`` and replayed there;
    only then does the solve count for ``pres``.
    """
    from ..search import search
    cfg = (cfg or SearchConfig()).replace(**overrides)
    ac = aut_canon(pres)
    res = search(ac.rep, cfg)
    return res, None if res.path is None else transport(pres, ac.phi, res.path, res.start, cfg.cyclic)
