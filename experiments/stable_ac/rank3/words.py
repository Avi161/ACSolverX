"""z-word families for the rank-3 brute-force baseline.

The search target is ``<x, y, z | r1, r2, Z.w>`` with ``w`` a word in x, y.
Two families:

* ``words_of_length(n)``: EVERY freely reduced word of length n over
  {x, y, X, Y}, one representative per ``{w, w^-1}``. Renaming z -> z^-1 maps
  ``Z.w`` to a rotation of ``(Z.w^-1)^-1``, so w and w^-1 give isomorphic
  search graphs (node counts can differ only through heap ties, measured by the
  ``inv`` side of the sweep). There are ``4 * 3**(n-1)`` reduced words of
  length n, hence ``2 * 3**(n-1)`` representatives, ``3**L - 1`` up to length L.
  Nothing else is folded: a rotation or a conjugate of w is a different start.
* ``relator_subwords(r1, r2)``: every cyclic subword of a relator, the word set
  of the CoV sweep (``cov_all.subwords``) plus the full rotations, with the
  same ``max(w, w^-1)`` representative so the two sweeps join on the word.

The order of ``words_of_length(n)`` is fixed (depth-first over ``LETTERS``);
the sweep stores results by index into it.
"""

from functools import lru_cache

LETTERS = (1, 2, -1, -2)   # x, y, X, Y
BLOCK = 2187               # words per task (3**7)


def inverse(w):
    return tuple(-g for g in reversed(w))


def fold(w):
    """The representative of ``{w, w^-1}``: the larger int tuple (as cov_all)."""
    w = tuple(w)
    return max(w, inverse(w))


@lru_cache(maxsize=None)
def words_of_length(n):
    out = []

    def rec(prefix):
        if len(prefix) == n:
            if prefix > inverse(prefix):
                out.append(prefix)
            return
        for g in LETTERS:
            if prefix and prefix[-1] == -g:
                continue
            rec(prefix + (g,))

    rec(())
    return tuple(out)


def n_words(n):
    return 2 * 3 ** (n - 1)


def n_blocks(n):
    return -(-n_words(n) // BLOCK)


def block_slice(n, block):
    lo = block * BLOCK
    return lo, min(lo + BLOCK, n_words(n))


def relator_subwords(r1, r2):
    """``[(w, is_proper)]``: cyclic subwords of r1/r2, 2 <= |w| <= |r|.

    ``is_proper`` marks the CoV family ``suballpxyb8`` (|w| <= |r| - 1 and not a
    whole rotation of a relator); the rest are the full rotations, where
    ``Z.w`` is one S-move from the null stabilization ``Z``.
    """
    from experiments.stable_ac.cov import cov_all
    proper = set(cov_all.subwords(r1, r2))
    return [(w, w in proper) for w in cov_all.subwords(r1, r2, proper=False)]
