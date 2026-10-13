"""The families: which words ``w`` may define ``z = w(x, y)``, and the limits on an image.

The tag names the rules, and changing one is a different experiment. The default ``subnc2pxysb``:

    sub   ``w`` is a cyclic subword of a relator, the seam included, of length >= 2 (``subwords``)
    nc2   ``w`` is dropped when substituting it brings a relator it occurs in below 3 letters (``subwords``)
    p     pure powers such as ``xx`` count (nothing filters them out)
    xy    both generators are tried as the one to eliminate (``images.enumerate_images``)
    s     ``substitute`` also matches ``w`` across the seam of the relator in its rotation (``substitution.substitute``)
    b     every relator that isolates the generator gives its own image (``images.branches``)

The exhaustive sweep's ``suballpxyb8`` keeps ``p``, ``xy`` and ``b`` and replaces the rest:

    sub   ``w`` is a cyclic subword of length 2 to |r| - 1, not a whole relator; no nc2 gate (``proper_subwords``)
    all   every set of non-overlapping occurrences is substituted; the seam is an ordinary place (``patterns``)
    8     one image per class: relator order, rotation, inversion, the 8 signed permutations (``images.class_key``)
"""
from ..core.words import inverse, reduce
from .substitution import substitute

FAMILIES = ("subnc2pxysb", "suballpxyb8")    # the default first
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
    """The words ``w`` of ``subnc2pxysb`` for ``(r1, r2)``, ordered by (length, word)."""
    found = _cyclic_subwords(r1) | _cyclic_subwords(r2)
    return sorted((w for w in found if not _collapses(w, (r1, r2))), key=lambda w: (len(w), w))


def proper_subwords(r1, r2):
    """The words ``w`` of ``suballpxyb8`` for ``(r1, r2)``: the cyclic subwords without the whole relators (a rotation
    of either relator or its inverse, even inside the other relator), ordered by (length, word)."""
    found, whole = set(), set()
    for rel in (r1, r2):
        words, n = _cyclic_subwords(rel), len(reduce(rel))
        found |= words
        whole |= {w for w in words if len(w) == n}
    return sorted(found - whole, key=lambda w: (len(w), w))
