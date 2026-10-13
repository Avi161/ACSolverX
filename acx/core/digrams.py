"""Cyclic digrams (two cyclically adjacent letters of a relator, counted with their inverse) and the rewriting of a
word with a new generator for one: the SAC transform (``acx.ngen.sac``) and the hybrid's definitions
(``acx.hybrid.dynrank``) both use them."""
from collections import Counter

from .words import inverse


def digram(w, k):
    """The cyclic digram of ``w`` at ``k``, in the orientation shared with its inverse."""
    d = (w[k], w[(k + 1) % len(w)])
    return min(d, inverse(d))


def digram_counts(words):
    """How often each cyclic digram occurs, in order of first occurrence; a word of under two letters has none."""
    return Counter(digram(w, k) for w in words if len(w) > 1 for k in range(len(w)))


def tokenize(w, d, h):
    """The shortest rewriting of the linear word ``w`` with ``d -> h`` and ``d^-1 -> -h`` (ties: the smaller word)."""
    d_inverse = inverse(d)
    shortest = [()] * (len(w) + 1)              # shortest[i]: the best rewriting of the suffix w[i:]
    for i in range(len(w) - 1, -1, -1):
        options = [(w[i],) + shortest[i + 1]]
        if w[i:i + 2] == d:
            options.append((h,) + shortest[i + 2])
        if w[i:i + 2] == d_inverse:
            options.append((-h,) + shortest[i + 2])
        shortest[i] = min(options, key=lambda option: (len(option), option))
    return shortest[0]
