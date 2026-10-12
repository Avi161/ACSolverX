"""``Emitter``: writes the elementary AC moves that carry a search's moves over an automorphism."""
from ..core.moves import Trace, source_word
from ..core.words import canonical_word, conjugators, fmt, inverse, parse, reduce
from .autos import apply_table


class Emitter(Trace):
    """A ``Trace`` that also aligns words, transports S-moves and precomposes automorphisms."""

    def align(self, target):
        """Make the words exactly ``target`` (each conjugate to a target word or its inverse)."""
        keys = [canonical_word(reduce(w)) for w in self.pres.rels]
        for m, want_word in enumerate(target):
            want = canonical_word(reduce(want_word))
            src = next((l for l in range(m, len(keys)) if keys[l] == want), None)
            if src is None:
                raise ValueError(f"no relator of {self.pres} matches {fmt(want_word)}")
            if src != m:
                self.do({"op": "swap", "a": m + 1, "b": src + 1})
                keys[m], keys[src] = keys[src], keys[m]
            if self.pres.rels[m] == want_word:
                continue
            sign, c = next(conjugators(self.pres.rels[m], want_word), (None, None))
            if sign is None:
                raise ValueError(f"{fmt(self.pres.rels[m])} is not conjugate to {fmt(want_word)} or its inverse")
            if sign < 0:
                self.invert(m)
            self.conj(m, c)

    def s_move(self, rels, m, tab):
        """The S-move ``m`` on canonical ``rels``, transported by the substitution table ``tab``.

        The child ``rot_k1(r_i) . rot_k2(r_j ** s)`` is conjugate to ``r_i . c^-1 (r_j ** s) c``, where
        ``c = u . p^-1`` and ``p``, ``u`` are the prefixes that rotate ``r_i`` and ``r_j ** s``. The move is that
        conjugated product, with ``c`` carried over by ``tab``.
        """
        ri, source = rels[m.i], source_word(rels, m)
        p = ri[:len(ri) - m.k1]
        u = source[:len(source) - m.k2]
        c = apply_table(reduce(u + inverse(p), cyclic=False), tab)
        self.conjugated_multiply(m.i, m.j, m.s, c)

    def dict_move(self, mv, tab):
        """An elementary move of the path, carried by the substitution table ``tab``."""
        if mv["op"] in ("stabilize", "destabilize"):
            raise ValueError("transport through Aut(F2) cannot carry stable moves")
        if mv["op"] == "conjugate":
            self.conj(mv["target"] - 1, apply_table(parse(mv["by"]), tab))
        else:
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
        img, other = a[t], 1 - t
        at = img.index(t + 1)
        for g in img[:at]:                                       # w_t <- w_o^e w_t
            self.invert(t)
            self.multiply(t, other, -1 if g > 0 else 1)
            self.invert(t)
        for g in img[at + 1:]:                                   # w_t <- w_t w_o^e
            self.multiply(t, other, 1 if g > 0 else -1)
