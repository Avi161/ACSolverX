"""The stable-AC (SAC) transform: define generators until every relator has length <= 3.

``triangulate(pres) -> Sac`` records the source, the digrams defined and the root; ``check`` re-derives the root.
The digram helpers are ``acx.core.digrams``. The definition and the tie-breaks: ``docs/RANK3.md``.
"""
from dataclasses import dataclass

from ..core.digrams import digram_counts, tokenize
from ..core.words import Presentation, inverse, rotate_left

LIMIT = 3          # the relator length SAC aims for


def excess(rels):
    """Total length above ``LIMIT`` over the relators; 0 when every relator is short."""
    return sum(max(0, len(r) - LIMIT) for r in rels)


def _least_rotation(w):
    """The smallest rotation of ``w`` in int order."""
    return min(rotate_left(w, k) for k in range(len(w)))


def rewrite(w, d, h):
    """``(flip, k, new)``: the shortest rewriting ``new`` of a rotation of ``w`` (by ``k``), or of ``w^-1`` if ``flip``.

    The word is oriented as the source's canonical form (the least rotation in int order), so ties break alike.
    """
    if len(w) < 2:
        return False, 0, w
    flip = _least_rotation(inverse(w)) < _least_rotation(w)
    oriented = inverse(w) if flip else w
    rotations = ((k, tokenize(rotate_left(oriented, k), d, h)) for k in range(len(oriented)))
    k, new = min(rotations, key=lambda rotation: (len(rotation[1]), rotation[1], rotation[0]))
    return flip, k, new


def define(pres, d):
    """Define the digram ``d``: ``<x.. | r..>`` becomes ``<x.., h | r..[d -> h], d^-1 h>`` (new relator last)."""
    h = pres.n_gen + 1
    return Presentation(h, tuple(rewrite(r, d, h)[2] for r in pres.rels) + (inverse(d) + (h,),))


def next_digram(rels):
    """The digram to define next: most cyclic occurrences, then most inside relators longer than ``LIMIT``, then
    the smallest."""
    total = digram_counts(rels)
    longs = digram_counts(w for w in rels if len(w) > LIMIT)
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
