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
from ..core.moves import Move, Trace
from ..core.words import canonical_rels, canonical_word, conjugators, fmt, inverse, parse, reduce
from ..verify.replay import replay
from .whitehead import AUTOS, apply_table, sub_table, aut_canon, images, invert


class Emitter(Trace):
    """A ``Trace`` that also aligns words, transports S-moves and precomposes automorphisms."""

    def align(self, target):
        """Make the words exactly ``target`` (each conjugate to a target word or its inverse)."""
        key = [canonical_word(reduce(w)) for w in self.pres.rels]
        for m, t in enumerate(target):
            want = canonical_word(reduce(t))
            src = next((l for l in range(m, len(key)) if key[l] == want), None)
            if src is None:
                raise ValueError(f"no relator of {self.pres} matches {fmt(t)}")
            if src != m:
                self.do({"op": "swap", "a": m + 1, "b": src + 1})
                key[m], key[src] = key[src], key[m]
            if self.pres.rels[m] == t:
                continue
            sign, c = next(conjugators(self.pres.rels[m], t), (None, None))
            if sign is None:
                raise ValueError(f"{fmt(self.pres.rels[m])} is not conjugate to {fmt(t)} or its inverse")
            if sign < 0:
                self.invert(m)
            self.conj(m, c)

    def s_move(self, rels, m, tab):
        """The S-move ``m`` on canonical ``rels``, transported by the substitution table ``tab``."""
        o = rels[m.j] if m.s == 1 else inverse(rels[m.j])
        c = apply_table(reduce(o[:len(o) - m.k2] + inverse(rels[m.i][:len(rels[m.i]) - m.k1]), cyclic=False), tab)
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
            return self.conj(mv["target"] - 1, apply_table(parse(mv["by"]), tab))
        self.do(mv)

    def precompose(self, a):
        """``T -> T o a`` for a Whitehead automorphism ``a`` (tuple Nielsen moves)."""
        if all(len(img) == 1 for img in a):                      # signed permutation
            if abs(a[0][0]) == 2:
                self.do({"op": "swap"})
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
    tab = sub_table(psi)
    em = Emitter(pres)
    states = replay(start, path, cyclic=cyclic)
    for s, mv in zip(states, path):
        if isinstance(mv, dict):
            em.align(tuple(apply_table(r, tab) for r in s.rels))
            em.dict_move(mv, tab)
        else:
            rels = canonical_rels(s.rels)
            em.align(tuple(apply_table(r, tab) for r in rels))
            em.s_move(rels, Move(*mv), tab)
    em.align(psi)                                              # the basis (psi(x), psi(y))
    for k in reversed(phi):
        em.precompose(AUTOS[k])
    replay(pres, em.moves, cyclic=cyclic, normalize=False)
    return em.moves


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
