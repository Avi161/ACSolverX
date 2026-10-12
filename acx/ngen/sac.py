"""The stable-AC (SAC) transform: define generators until every relator has length <= 3.

``triangulate(pres) -> Sac`` records the source, the digrams defined and the root; ``check`` re-derives the root.
``tokenize`` is shared with ``acx.hybrid``. The definition and the tie-breaks: ``docs/RANK3.md``.
"""
from collections import Counter
from dataclasses import dataclass

from ..core.words import Presentation, inverse

LIMIT = 3          # the relator length SAC aims for


def excess(rels):
    """Total length above ``LIMIT`` over the relators; 0 when every relator is short."""
    return sum(max(0, len(r) - LIMIT) for r in rels)


def digram(w, k):
    """The cyclic digram of ``w`` at ``k``, in the orientation shared with its inverse."""
    d = (w[k], w[(k + 1) % len(w)])
    return min(d, inverse(d))


def tokenize(w, d, h):
    """The shortest rewriting of the linear word ``w`` with ``d -> h`` and ``d^-1 -> -h`` (ties: the smaller word)."""
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


def _least_rotation(w):
    return min(w[k:] + w[:k] for k in range(len(w)))


def rewrite(w, d, h):
    """``(flip, k, new)``: ``new`` is the shortest rewriting of a rotation (over ``k``) of ``w``, or of ``w^-1`` when
    ``flip``, oriented as the source's canonical form (the least rotation in int order), so ties break alike."""
    if len(w) < 2:
        return False, 0, w
    flip = _least_rotation(inverse(w)) < _least_rotation(w)
    o = inverse(w) if flip else w
    k, new = min(((k, tokenize(o[k:] + o[:k], d, h)) for k in range(len(o))),
                 key=lambda c: (len(c[1]), c[1], c[0]))
    return flip, k, new


def define(pres, d):
    """Define the digram ``d``: ``<x.. | r..>`` becomes ``<x.., h | r..[d -> h], d^-1 h>``; the new relator comes last."""
    h = pres.n_gen + 1
    return Presentation(h, tuple(rewrite(r, d, h)[2] for r in pres.rels) + (inverse(d) + (h,),))


def next_digram(rels):
    """The digram to define next: most cyclic occurrences, then most inside relators longer than ``LIMIT``, then smallest."""
    total, longs = Counter(), Counter()
    for w in rels:
        for k in range(len(w)) if len(w) > 1 else ():
            total[digram(w, k)] += 1
            if len(w) > LIMIT:
                longs[digram(w, k)] += 1
    return min(longs, key=lambda d: (-total[d], -longs[d], d))


@dataclass(frozen=True)
class Sac:
    """A definition sequence: ``source`` (cyclically reduced) becomes ``root`` by ``digrams``, one generator each."""
    source: Presentation
    digrams: tuple
    root: Presentation

    @property
    def rank(self):
        """Generators of the root."""
        return self.root.n_gen


def triangulate(pres):
    """Define digrams until every relator has length <= ``LIMIT``; return the ``Sac``."""
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
    """True when re-deriving the root from the source and the digrams alone gives ``sac.root``, with short relators."""
    cur = sac.source
    for d in sac.digrams:
        cur = define(cur, d)
    return cur == sac.root and all(len(r) <= LIMIT for r in cur.rels)
