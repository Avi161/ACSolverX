"""``Frame``: the certificate's presentation ``E`` mirrored move for move on the real presentation ``W``.

Invariant ``W = psi(E)`` letter for letter, ``psi`` an automorphism of the free group; every move on ``E`` is
written on ``W`` with its conjugating words replaced by their ``psi`` images. ``certify`` drives it.
"""
from ..aut.whitehead import AUTOS, apply_table
from ..core.words import canonical_word, conjugators, free, inverse, reduce, to_char


class RealPresentation:
    """The real presentation ``W`` and the elementary moves applied to it (``acx.core.moves``' dict schema).

    Not an ``acx.core.moves.Trace``: words are plain tuples (the path is checked once, by
    ``acx.verify.replay``), and stabilisations and lazy conjugations are its own. Conjugations are
    held back per relator and merged (a conjugation commutes with inverting and swapping), so
    ``c`` then ``c^-1`` on one relator costs nothing; they are written out before a multiply that
    reads the relator and at the end."""

    def __init__(self, pres):
        self.rels, self.n_gen, self.ops = list(pres.rels), pres.n_gen, []
        self.pend = [()] * len(self.rels)

    def conj(self, t, c):
        """Conjugate relator ``t`` by the word ``c`` (held back, see the class docstring)."""
        self.pend[t] = free(self.pend[t] + tuple(c))

    def flush(self, t):
        """Write out the held-back conjugation of relator ``t``."""
        c, self.pend[t] = self.pend[t], ()
        self.ops.extend({"op": "conjugate", "target": t + 1, "by": to_char(g)} for g in c)
        self.rels[t] = free(inverse(c) + self.rels[t] + c)

    def invert(self, t):
        """Invert relator ``t``."""
        self.ops.append({"op": "invert", "target": t + 1})
        self.rels[t] = inverse(self.rels[t])

    def swap(self, a, b):
        """Swap relators ``a`` and ``b``."""
        self.ops.append({"op": "swap", "a": a + 1, "b": b + 1})
        self.rels[a], self.rels[b] = self.rels[b], self.rels[a]
        self.pend[a], self.pend[b] = self.pend[b], self.pend[a]

    def multiply(self, t, s, e=1):
        """``w_t <- w_t w_s^e``."""
        self.flush(t)
        self.flush(s)
        if e < 0:
            self.invert(s)
        self.ops.append({"op": "multiply", "target": t + 1, "source": s + 1})
        self.rels[t] = free(self.rels[t] + self.rels[s])
        if e < 0:
            self.invert(s)

    def stabilize(self):
        """Add a generator and its unit relator."""
        self.ops.append({"op": "stabilize"})
        self.n_gen += 1
        self.rels.append((self.n_gen,))
        self.pend.append(())

    def destabilize(self):
        """Drop the last generator and its unit relator."""
        if self.rels[-1] != (self.n_gen,) or self.pend[-1]:
            raise AssertionError("the last relator is not the last generator")
        self.ops.append({"op": "destabilize"})
        self.n_gen -= 1
        self.rels.pop()
        self.pend.pop()

    def words(self):
        """The relators with every held-back conjugation written out."""
        for t in range(len(self.rels)):
            self.flush(t)
        return self.rels


class Frame:
    """``E`` and ``W = psi(E)``. ``E`` is the certificate's state with one unit relator ``x_g`` for every generator
    outside it (parked); ``psi`` is kept as a table, ``factors`` records the automorphisms applied to ``E``."""

    def __init__(self, pres):
        self.w, self.E = RealPresentation(pres), [free(r) for r in pres.rels]
        self.tab = {s * g: (s * g,) for g in range(1, pres.n_gen + 1) for s in (1, -1)}     # psi
        self.factors = []

    # moves on E, mirrored on W
    def conj(self, i, c):
        """Conjugate ``E_i`` by ``c``."""
        c = free(c)
        if c:
            self.E[i] = free(inverse(c) + self.E[i] + c)
            self.w.conj(i, apply_table(c, self.tab))

    def invert(self, i):
        """Invert ``E_i``."""
        self.E[i] = inverse(self.E[i])
        self.w.invert(i)

    def swap(self, a, b):
        """Swap ``E_a`` and ``E_b``."""
        if a != b:
            self.E[a], self.E[b] = self.E[b], self.E[a]
            self.w.swap(a, b)

    def witness(self, w, t):
        """The ``(sign, c)`` of ``conjugators`` whose ``psi(c)`` is shortest."""
        found = list(conjugators(w, t))
        if not found:
            raise ValueError(f"{w} is not conjugate to {t} or its inverse")
        return min(found, key=lambda sc: len(apply_table(sc[1], self.tab)))

    def cmul(self, i, j, m):
        """``E_i <- E_i . m`` for a word ``m`` conjugate to ``E_j`` or its inverse."""
        s, c = self.witness(self.E[j], m)
        if s < 0:
            self.invert(j)
        self.conj(j, c)
        self.E[i] = free(self.E[i] + self.E[j])
        self.w.multiply(i, j)
        self.conj(j, inverse(c))
        if s < 0:
            self.invert(j)

    def set_word(self, i, t):
        """Conjugate (and invert) ``E_i`` into exactly the word ``t``."""
        s, c = self.witness(self.E[i], t)
        if s < 0:
            self.invert(i)
        self.conj(i, c)
        if self.E[i] != t:
            raise AssertionError(f"relator {i} is {self.E[i]}, not {t}")

    def align(self, targets):
        """The first ``len(targets)`` relators become exactly ``targets`` (each conjugate to one of them
        or its inverse)."""
        keys = [canonical_word(reduce(w)) for w in self.E[:len(targets)]]
        for m, t in enumerate(targets):
            want = canonical_word(reduce(t))
            src = next((k for k in range(m, len(targets)) if keys[k] == want), None)
            if src is None:
                raise ValueError(f"no relator of {self.E} matches {t}")
            self.swap(m, src)
            keys[m], keys[src] = keys[src], keys[m]
            if self.E[m] != t:
                self.set_word(m, t)

    def stabilize(self):
        """Add the generator ``len(E) + 1`` with its unit relator."""
        g = len(self.E) + 1
        self.w.stabilize()
        self.E.append((g,))
        self.tab[g], self.tab[-g] = (g,), (-g,)

    # automorphisms of E: psi <- psi o a^-1
    def transvect(self, i, j, e):
        """``x_i -> x_i x_j^e``."""
        f = {i: (i, e * j), -i: (-e * j, -i)}
        self.E = [free(y for x in w for y in f.get(x, (x,))) for w in self.E]
        self.tab[i] = free(self.tab[i] + self.tab[-e * j])
        self.tab[-i] = inverse(self.tab[i])
        self.factors.append(("tv", i, j, e))

    def permute(self, perm, signs):
        """``x_g -> x_perm[g] ** signs[g]`` for ``g`` in ``perm``; other generators fixed."""
        f = {s * g: s * signs[g] * p for g, p in perm.items() for s in (1, -1)}
        self.E = [tuple(f.get(x, x) for x in w) for w in self.E]
        new = dict(self.tab)
        for g, p in perm.items():
            new[p] = self.tab[signs[g] * g]
            new[-p] = self.tab[-signs[g] * g]
        self.tab = new
        self.factors.append(("perm", dict(perm), dict(signs)))

    def aut(self, k):
        """``AUTOS[k]`` at rank two: a signed permutation or a single transvection (the Nielsen maps)."""
        img = AUTOS[k]
        if all(len(w) == 1 for w in img):
            self.permute({1: abs(img[0][0]), 2: abs(img[1][0])}, {1: img[0][0] // abs(img[0][0]),
                                                                  2: img[1][0] // abs(img[1][0])})
            return
        i = next(t for t in (1, 2) if len(img[t - 1]) > 1)
        w = img[i - 1]
        if len(w) != 2 or w[0] != i or img[2 - i] != (3 - i,):
            raise ValueError(f"AUTOS[{k}] is not a right transvection")
        self.transvect(i, abs(w[1]), 1 if w[1] > 0 else -1)

    # the tail
    def finish(self, n_gen):
        """``E`` is all unit relators: bring ``W`` to ``x_1..x_m`` and destabilise to ``n_gen`` generators."""
        m = len(self.E)
        self.align(tuple((g,) for g in range(1, m + 1)))
        w = self.w
        if w.words() != [self.tab[g] for g in range(1, m + 1)]:
            raise AssertionError("W is not psi of the unit relators")
        for f in reversed(self.factors):                      # T -> T o a
            if f[0] == "tv":
                w.multiply(f[1] - 1, f[2] - 1, f[3])
                continue
            _, perm, signs = f
            want = {g - 1: p - 1 for g, p in perm.items()}   # new w_g = old w_perm[g] ** signs[g]
            content = list(range(m))                         # content[pos]: which old w sits at pos
            for g in sorted(want):
                src = content.index(want[g])
                if src != g:
                    w.swap(g, src)
                    content[g], content[src] = content[src], content[g]
            for g in want:
                if signs[g + 1] < 0:
                    w.invert(g)
        while w.n_gen > n_gen:
            w.destabilize()
