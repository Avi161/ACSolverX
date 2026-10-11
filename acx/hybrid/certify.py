"""A hybrid certificate written out as elementary (and stable) AC moves on the presentation itself.

The certificate (``HybridResult.steps``) mixes S-moves, automorphisms of F2
(Nielsen maps, signed permutations) and higher-rank events (``dynrank``:
products, definitions, eliminations, transvections, relabellings). None but the
S-moves are AC moves of the presentation as given, so ``certify`` keeps two
presentations:

* ``E``: the certificate's own words (its state, spelled exactly), plus one unit
  relator ``x_g`` for every generator that is not in the state (``parked``);
* ``W``: the real presentation, changed only by elementary moves
  (``acx.core.moves``: invert, swap, conjugate by a letter, multiply, stabilize,
  destabilize), with the invariant ``W = psi(E)`` letter for letter, ``psi`` an
  automorphism of the free group on all generators.

An elementary move on ``E`` is mirrored on ``W`` with every conjugating word
``c`` replaced by ``psi(c)`` (AC moves are Aut-equivariant). An automorphism
``a`` of the certificate acts on ``E`` only and sets ``psi <- psi o a^-1``; it is
always a product of factors ``x_i -> x_i x_j^e`` (transvections) and signed
permutations, recorded in order. The events:

* **S-move / product**: conjugate ``E_i`` into the rotation, multiply by the
  conjugate of ``E_j^s`` that is the second factor, the canonical form is
  reached by the next alignment (conjugations, inversions, swaps).
* **define** ``h -> d``: stabilise ``W`` (or reuse a parked unit relator ``x_h``),
  apply ``h -> h b``, ``h -> h a``, ``h -> h^-1`` to turn ``x_h`` into
  ``h^-1 a b``, then turn every ``d^+-1`` of each relator into ``h^+-1`` by
  multiplying with a conjugate of that relator.
* **eliminate** ``g`` with ``R_i = g^e u``: replace every ``g^+-1`` of the other
  relators by ``image^+-1`` (one multiplication by a conjugate of ``R_i`` each),
  write ``R_i`` as ``g . image^-1``, apply ``g -> g . image`` (transvections) so
  ``R_i = g``, renumber the generators so ``g`` is the last of the state's, and
  park it.
* **end**: the state is two letters, ``E`` is all unit relators; then
  ``W = psi(x_1..x_m)``, and precomposing that tuple with the recorded factors
  last-first (``T -> T o a``: one multiply, swap or invert each) gives
  ``x_1..x_m``; ``m - 2`` destabilisations end at ``<x, y | x, y>``.

The path is long (each conjugation costs one move per letter of ``psi(c)``) but
deterministic. ``certify`` replays it with ``acx.verify.replay(pres, path,
normalize=False)`` before returning it; a certificate with higher-rank steps
gives a stable AC path (AC4/AC5 moves included), one without gives an AC path.

The method is ``acx.aut.transport``'s (Aut-equivariance, the Nielsen tail) and
``acx.ngen.lift``'s (definitions undone by conjugate multiplications), extended
to interleaved automorphisms, stabilisations and eliminations of any rank. The
source (``hfhybrid.verify_hybrid``, ``origin/claude/vigilant-babbage-nnbuj0``)
replayed the mixed steps directly and took ``define``/``eliminate`` as Lemma-11
composites without writing them out.
"""
from ..aut.whitehead import AUTOS, apply_table
from ..core.moves import seam_cancels
from ..core.words import canonical_rels, canonical_word, conjugators, free, inverse, reduce, rotate, to_char
from ..verify.replay import replay
from . import dynrank as D
from .cascade import Aut, aut_child, is_terminal, move_child


class _Real:
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
        self.pend[t] = free(self.pend[t] + tuple(c))

    def flush(self, t):
        c, self.pend[t] = self.pend[t], ()
        self.ops.extend({"op": "conjugate", "target": t + 1, "by": to_char(g)} for g in c)
        self.rels[t] = free(inverse(c) + self.rels[t] + c)

    def invert(self, t):
        self.ops.append({"op": "invert", "target": t + 1})
        self.rels[t] = inverse(self.rels[t])

    def swap(self, a, b):
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
        self.ops.append({"op": "stabilize"})
        self.n_gen += 1
        self.rels.append((self.n_gen,))
        self.pend.append(())

    def destabilize(self):
        if self.rels[-1] != (self.n_gen,) or self.pend[-1]:
            raise AssertionError("the last relator is not the last generator")
        self.ops.append({"op": "destabilize"})
        self.n_gen -= 1
        self.rels.pop()
        self.pend.pop()

    def words(self):
        for t in range(len(self.rels)):
            self.flush(t)
        return self.rels


class Frame:
    """``E`` and ``W = psi(E)``; relator ``p`` past the certificate's state is the parked unit ``x_(p+1)``."""

    def __init__(self, pres):
        self.w, self.E = _Real(pres), list(pres.rels)
        self.tab = {s * g: (s * g,) for g in range(1, pres.n_gen + 1) for s in (1, -1)}     # psi
        self.factors = []

    # moves on E, mirrored on W
    def conj(self, i, c):
        c = free(c)
        if c:
            self.E[i] = free(inverse(c) + self.E[i] + c)
            self.w.conj(i, apply_table(c, self.tab))

    def invert(self, i):
        self.E[i] = inverse(self.E[i])
        self.w.invert(i)

    def swap(self, a, b):
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


def _product(fr, words, ev):
    i, j, k1, k2 = ev["i"], ev["j"], ev["k1"], ev["k2"]
    target = words[i]
    base = words[j] if ev["sign"] == 1 else inverse(words[j])
    fr.set_word(i, target[k1:] + target[:k1])
    fr.cmul(i, j, base[k2:] + base[:k2])
    result = D.dcanon(target[k1:] + target[:k1] + base[k2:] + base[:k2])
    if result != tuple(ev["result"]):
        raise ValueError("product result differs")
    return D.normalize(words[:i] + (result,) + words[i + 1:])


def _define(fr, words, ev):
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
                fr.cmul(i, n, free(inverse(q) + inverse(de) + (t[p],) + q))
        if fr.E[i] != t:
            raise ValueError(f"template {t} does not expand to relator {words[i]}")
    return D.normalize(((-h,) + d,) + tuple(map(tuple, ev["templates"])))


def _eliminate(fr, words, ev):
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
                s = D.substitute(w[p + 1:], g, image)
                fr.cmul(k, i, free(inverse(s) + (-f * g,) + (image if f > 0 else inverse(image)) + s))
        if fr.E[k] != D.substitute(w, g, image):
            raise AssertionError("substitution differs")
    fr.set_word(i, (g,) + inverse(image))
    for x in reversed(image):                                # g -> g . image
        fr.transvect(g, abs(x), 1 if x > 0 else -1)
    fr.permute({x: (n if x == g else x - 1) for x in range(g, n + 1)}, {x: 1 for x in range(g, n + 1)})
    fr.swap(i, n - 1)                                        # park the unit relator x_n
    return D.normalize(raw)


def _transvection(fr, words, ev):
    i, j, s = ev["i"], ev["j"], ev["sign"]
    if not (1 <= i <= len(words) and 1 <= j <= len(words) and i != j and s in (1, -1)):
        raise ValueError("bad transvection")
    fr.transvect(i, j, s)
    return D.normalize(D.transvection(w, i, j, s) for w in words)


EVENTS = {"product": _product, "define": _define, "eliminate": _eliminate, "nielsen": _transvection}


def certify(pres, steps):
    """Elementary moves taking ``pres`` to its trivial presentation along ``steps``; replayed before return."""
    fr = Frame(pres)
    cur, dyn = canonical_rels(tuple(reduce(r) for r in pres.rels)), None
    for st in steps:
        if isinstance(st, dict):
            words = D.normalize(cur) if dyn is None else dyn
            fr.align(words)
            child = EVENTS[st["event"]["kind"]](fr, words, st["event"])
            rl = st["relabel"]
            if rl is not None:
                fr.permute(rl["perm"], rl["signs"])
                child = D.apply_relabel(child, rl["perm"], rl["signs"])
            if child != tuple(map(tuple, st["after"])):
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
