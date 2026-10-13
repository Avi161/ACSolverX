"""The 20 Whitehead automorphisms of F2 and how they act on words.

Each automorphism is the pair ``(image of x, image of y)`` of int words (``x = 1``, ``y = 2``, inverse = negative).
``AUTOS[0:8]`` are the signed permutations (``SIGNED``: they never change a length); ``AUTOS[8:20]`` are the
second-kind automorphisms, the only ones a descent step uses (``DESCENT``). A sequence of indices into ``AUTOS`` is a
``phi``: the first index acts first.
"""
from ..core.words import Presentation, inverse, parse, reduce

_LETTERS = ("x", "X", "y", "Y")

# First kind: x and y go to letters of different generators.
_SIGNED_PERMUTATIONS = [(fx, fy) for fx in _LETTERS for fy in _LETTERS if fx.lower() != fy.lower()]

# Second kind: one generator is fixed and the other is multiplied by it, or conjugated by it.
_SECOND_KIND = [
    ("x", "yx"), ("x", "Xy"), ("x", "Xyx"), ("x", "yX"), ("x", "xy"), ("x", "xyX"),    # x fixed, y changes
    ("xy", "y"), ("Yx", "y"), ("Yxy", "y"), ("xY", "y"), ("yx", "y"), ("yxY", "y"),    # y fixed, x changes
]

AUTOS = tuple((parse(fx), parse(fy)) for fx, fy in _SIGNED_PERMUTATIONS + _SECOND_KIND)
SIGNED = range(len(_SIGNED_PERMUTATIONS))
DESCENT = range(len(_SIGNED_PERMUTATIONS), len(AUTOS))
IDENTITY = ((1,), (2,))


def sub_table(img):
    """The letter-to-word table of the endomorphism ``x -> img[0], y -> img[1]``."""
    return {1: img[0], -1: inverse(img[0]), 2: img[1], -2: inverse(img[1])}


def apply_table(w, tab):
    """``w`` with every letter replaced by its word in ``tab``, freely reduced."""
    out = []
    for g in w:
        for h in tab[g]:
            if out and out[-1] == -h:
                out.pop()
            else:
                out.append(h)
    return tuple(out)


def apply(w, img):
    """The image of word ``w`` under the endomorphism ``x -> img[0], y -> img[1]``, freely reduced."""
    return apply_table(w, sub_table(img))


def images(phi):
    """``(phi(x), phi(y))`` of a factor sequence (first factor acts first)."""
    img = IDENTITY
    for k in phi:
        img = (apply(img[0], AUTOS[k]), apply(img[1], AUTOS[k]))
    return img


def _inverse_index(k):
    """The index ``j`` with ``AUTOS[k]`` followed by ``AUTOS[j]`` the identity."""
    return next(j for j in range(len(AUTOS)) if images((k, j)) == IDENTITY)


INVERSE = tuple(_inverse_index(k) for k in range(len(AUTOS)))
TABLES = tuple(map(sub_table, AUTOS))


def image(w, k):
    """The word ``w`` under ``AUTOS[k]``, then cyclically reduced (``apply`` only freely reduces; ``images`` gives the
    generators' images)."""
    return reduce(apply_table(w, TABLES[k]))


def invert(phi):
    """The factors of ``phi^-1``."""
    return tuple(INVERSE[k] for k in reversed(phi))


def apply_pres(pres, phi):
    """The presentation with every relator mapped by the automorphism ``phi`` (not reduced)."""
    tab = sub_table(images(phi))
    return Presentation(2, tuple(apply_table(r, tab) for r in pres.rels))
