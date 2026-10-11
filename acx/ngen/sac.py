"""The stable-AC (SAC) transform: a presentation becomes one whose relators all have length <= 3.

One *definition* adds a generator ``h`` with the relator ``d^-1 h`` for a cyclic
digram ``d = ab`` and rewrites every relator, replacing ``ab`` by ``h`` (and
``BA`` by ``H``) wherever that shortens it: the shortest rewriting over the
rotations of the relator, oriented as its canonical form (least rotation of it
or its inverse, int order), ties by the smaller word. Each definition shortens
some relator longer than 3, so repeating it terminates; the rank grows by one
per definition ("a new generator per extra letter", z = ab style). The digram
defined next has the most cyclic occurrences over all relators (ties: the most
inside relators longer than 3, then the smaller digram).

Port of ``triangulate`` / ``define`` / ``tokenize`` from ``origin/claude/
vigilant-babbage-nnbuj0:research/ac_dynamic_rank_20260913/dynrank.py`` (blob
901efc11, commit 61bc4ebc). Relators keep their positions here (the lift
tracks them) instead of being re-sorted, and the orientation rule above
reproduces the source's tie-breaks: the same digrams and the same root (up to
canonical form) on all of MS640, AC19 and 1190ms (``tests/test_ngen.py`` pins a
sample). The source's ``tri`` arm (25/60 bench60 against 34/60 at rank two)
also allowed eliminations during the search; ``acx.ngen.solve`` keeps the rank
fixed.

A definition is a stabilisation (generator ``h``, relator ``h``), the
automorphism ``h -> d^-1 h`` and AC moves (multiplying by conjugates of the
defining relator), so a solve of the root proves STABLE AC triviality of the
source; ``acx.ngen.lift`` writes those moves out as a replayable path.
"""
from collections import Counter
from dataclasses import dataclass

from ..core.words import Presentation, inverse

LIMIT = 3          # the relator length SAC aims for


def excess(rels):
    return sum(max(0, len(r) - LIMIT) for r in rels)


def digram(w, k):
    """The cyclic digram at ``k`` in the orientation shared with its inverse."""
    d = (w[k], w[(k + 1) % len(w)])
    return min(d, inverse(d))


def tokenize(w, d, h):
    """The shortest rewriting of the linear word ``w`` with ``d -> h`` and ``d^-1 -> -h`` (ties: smaller)."""
    di, n = inverse(d), len(w)
    best = [()] * (n + 1)
    for i in range(n - 1, -1, -1):
        cands = [(w[i],) + best[i + 1]]
        if w[i:i + 2] == d:
            cands.append((h,) + best[i + 2])
        if w[i:i + 2] == di:
            cands.append((-h,) + best[i + 2])
        best[i] = min(cands, key=lambda t: (len(t), t))
    return best[0]


def flips(w):
    """True when the source's canonical form of ``w`` is a rotation of ``w^-1`` (least rotation, int order)."""
    wi = inverse(w)
    return min(wi[k:] + wi[:k] for k in range(len(w))) < min(w[k:] + w[:k] for k in range(len(w)))


def rewrite(w, d, h):
    """``(flip, k, new)``: ``new`` is the shortest rewriting over ``k`` of the rotation ``o[k:] + o[:k]``,
    ``o = w^-1`` if ``flip`` else ``w``; ``o`` is oriented as the source's canonical form, so ties break alike."""
    if len(w) < 2:
        return False, 0, w
    flip = flips(w)
    o = inverse(w) if flip else w
    k, new = min(((k, tokenize(o[k:] + o[:k], d, h)) for k in range(len(o))),
                 key=lambda c: (len(c[1]), c[1], c[0]))
    return flip, k, new


def define(pres, d):
    """``<x.. | r..>`` -> ``<x.., h | r..[d -> h], d^-1 h>`` (the new relator is last)."""
    h = pres.n_gen + 1
    return Presentation(h, tuple(rewrite(r, d, h)[2] for r in pres.rels) + (inverse(d) + (h,),))


def next_digram(rels):
    """The digram to define next (see the module docstring)."""
    total, longs = Counter(), Counter()
    for w in rels:
        for k in range(len(w)) if len(w) > 1 else ():
            total[digram(w, k)] += 1
            if len(w) > LIMIT:
                longs[digram(w, k)] += 1
    return min(longs, key=lambda d: (-total[d], -longs[d], d))


@dataclass(frozen=True)
class Sac:
    """A definition sequence: ``source`` (cyclically reduced) -> ``root`` by ``digrams``, one generator each."""
    source: Presentation
    digrams: tuple
    root: Presentation

    @property
    def rank(self):
        return self.root.n_gen


def triangulate(pres):
    """Define digrams until every relator has length <= 3; return the ``Sac``."""
    source = pres.reduced()
    cur, ds = source, []
    while excess(cur.rels):
        d = next_digram(cur.rels)
        nxt = define(cur, d)
        if excess(nxt.rels) >= excess(cur.rels):
            raise RuntimeError(f"SAC definition of {d} did not shorten {cur}")
        cur = nxt
        ds.append(d)
    return Sac(source, tuple(ds), cur)


def check(sac):
    """Re-derive the root from the source and the digrams alone; True when it is ``sac.root``."""
    cur = sac.source
    for d in sac.digrams:
        cur = define(cur, d)
    return cur == sac.root and all(len(r) <= LIMIT for r in cur.rels)
