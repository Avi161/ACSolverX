"""The replay verifier, the authority on whether a path solves a presentation.

``replay`` re-applies every move and raises ``ReplayError`` unless each move is legal, ``|det|`` of the exponent
matrix stays 1 (an AC invariant), no relator exceeds ``cap`` and the end is the trivial presentation.
"""
from ..core.moves import is_elementary, step


class ReplayError(ValueError):
    """A path is illegal, changes ``|det|``, breaks the cap or does not end trivial."""


def exponent_matrix(pres):
    """Row ``i`` holds the exponent sum of each generator in relator ``i``."""
    m = [[0] * pres.n_gen for _ in pres.rels]
    for i, r in enumerate(pres.rels):
        for g in r:
            m[i][abs(g) - 1] += 1 if g > 0 else -1
    return m


def det(m):
    """Exact integer determinant of the square integer matrix ``m`` (fraction-free Bareiss elimination)."""
    n = len(m)
    a = [row[:] for row in m]
    sign, prev_pivot = 1, 1
    for k in range(n - 1):
        if a[k][k] == 0:                                  # swap in a row with a nonzero pivot, or det is 0
            swap = next((r for r in range(k + 1, n) if a[r][k]), None)
            if swap is None:
                return 0
            a[k], a[swap] = a[swap], a[k]
            sign = -sign
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                a[i][j] = (a[i][j] * a[k][k] - a[i][k] * a[k][j]) // prev_pivot   # exact division
        prev_pivot = a[k][k]
    return sign * a[n - 1][n - 1] if n else 1


def abs_det(pres):
    """``|det|`` of the exponent matrix; ``ReplayError`` for an unbalanced presentation."""
    if len(pres.rels) != pres.n_gen:
        raise ReplayError(f"unbalanced presentation {pres}")
    return abs(det(exponent_matrix(pres)))


def replay(pres, path, cyclic=True, cap=None, normalize=True, require_trivial=True):
    """Replay ``path`` from ``pres`` and return the states (start first); raise ``ReplayError`` on any failure.

    Each move must be legal: an S-move (``acx.core.moves.Move``) in range with a cancelling seam, or a well-formed
    elementary or stable dict move (AC5 only drops a generator that occurs nowhere else). ``|det| = 1`` is checked
    at the start and after every move, and ``cap`` bounds the relators an S-move produces.

    ``normalize`` (search paths) starts from ``pres.normal(cyclic)``, the search's start; elementary paths on the
    raw words pass ``normalize=False``. ``require_trivial``: the end has as many relators as generators, each
    cyclically reducing to one letter.
    """
    cur = pres.normal(cyclic) if normalize else pres
    if abs_det(cur) != 1:
        raise ReplayError(f"start has |det| != 1: {cur}")
    states = [cur]
    for t, mv in enumerate(path):
        try:
            cur = step(cur, mv, cyclic)
        except (ValueError, KeyError, TypeError) as e:
            raise ReplayError(f"move {t} {mv!r} is illegal on {cur}: {e}") from e
        if abs_det(cur) != 1:
            raise ReplayError(f"move {t} {mv!r} changed |det|: {cur}")
        if cap is not None and not is_elementary(mv) and max(map(len, cur.rels)) > cap:
            raise ReplayError(f"move {t} {mv!r} exceeds cap {cap}: {cur}")
        states.append(cur)
    if require_trivial and not cur.is_trivial():
        raise ReplayError(f"path ends at a non-trivial presentation {cur}")
    return states
