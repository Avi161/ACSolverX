"""The family ``subnc2pxysb``: which words ``w`` may define ``z = w(x, y)``, and the limits on an image.

The tag names the rules, and changing one is a different experiment:

    sub   ``w`` is a cyclic subword of a relator, the seam included, of length >= 2 (``subwords``)
    nc2   ``w`` is dropped when substituting it brings a relator it occurs in below 3 letters (``subwords``)
    p     pure powers such as ``xx`` count (nothing filters them out)
    xy    both generators are tried as the one to eliminate (``cov.enumerate_images``)
    s     ``substitute`` also matches ``w`` across the seam of the written relator (``substitution.substitute``)
    b     every relator that isolates the generator gives its own image (``cov.branches``)
"""
from ..core.words import inverse, reduce
from .substitution import substitute

MIN_W_LEN = 2          # |w| < 2 would be a rename
MIN_TRANSFORMED = 3    # nc2: a relator shorter than this after substituting is a collapse
MAX_LEN = 239          # an image with a longer relator is not in the family; None = no limit


def _cyclic_subwords(rel):
    """Every cyclic subword of ``rel`` of length >= ``MIN_W_LEN``, as ``max(w, w^-1)`` (``w`` and ``w^-1`` are one member)."""
    cyc = reduce(rel)
    doubled = cyc + cyc
    windows = (doubled[i:i + m] for m in range(MIN_W_LEN, len(cyc) + 1) for i in range(len(cyc)))
    return {max(w, inverse(w)) for w in windows}


def _collapses(w, rels):
    """nc2: substituting ``w`` leaves some relator it occurs in with fewer than ``MIN_TRANSFORMED`` letters."""
    for rel in rels:
        image, n_subs = substitute(rel, w)
        if n_subs and len(image) < MIN_TRANSFORMED:
            return True
    return False


def subwords(r1, r2):
    """The words ``w`` of the family for ``(r1, r2)``, ordered by (length, word)."""
    found = _cyclic_subwords(r1) | _cyclic_subwords(r2)
    return sorted((w for w in found if not _collapses(w, (r1, r2))), key=lambda w: (len(w), w))
