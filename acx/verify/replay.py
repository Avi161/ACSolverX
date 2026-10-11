"""Replay verifier: the authority on whether a path solves a presentation.

``replay(pres, path)`` re-applies every move from the start and raises
``ReplayError`` unless

* every move is legal: an S-move (``acx.core.moves.Move``) is in range and its
  seam cancels; an elementary/stable dict move is well formed (AC5 only drops a
  generator that occurs nowhere else);
* ``|det|`` of the exponent-sum matrix is 1 at the start and after every move.
  An S-move adds +-1 times one row to another, canonicalisation inverts rows
  (sign) and permutes them, AC4 borders the matrix with a unit row and column,
  so ``|det|`` is an AC invariant and every AC-trivial balanced presentation
  has ``|det| = 1``; a move that changes it is unsound;
* with ``cap``, no relator produced by a move is longer than ``cap``;
* the end is trivial: as many relators as generators, each cyclically reducing
  to one letter, all generators present.

``normalize=True`` (search paths) first replaces the start by its reduced
canonical form, exactly the start the search used; elementary paths that act
on the raw words pass ``normalize=False``.

Sources: ``origin/test/greedy-test-suite:experiments/greedy_tests/spec/
{invariants,search}.py`` (the |det| invariant, replay), and
``origin/codex/ac-elementary-decoder:experiments/search/ac_decode.py``
(``replay_elementary``).
"""
from ..core.moves import step


class ReplayError(ValueError):
    pass


def exponent_matrix(pres):
    m = [[0] * pres.n_gen for _ in pres.rels]
    for i, r in enumerate(pres.rels):
        for g in r:
            m[i][abs(g) - 1] += 1 if g > 0 else -1
    return m


def det(m):
    """Exact integer determinant (fraction-free Bareiss)."""
    n = len(m)
    a = [row[:] for row in m]
    sign, prev = 1, 1
    for k in range(n - 1):
        if a[k][k] == 0:
            sw = next((r for r in range(k + 1, n) if a[r][k]), None)
            if sw is None:
                return 0
            a[k], a[sw] = a[sw], a[k]
            sign = -sign
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                a[i][j] = (a[i][j] * a[k][k] - a[i][k] * a[k][j]) // prev
        prev = a[k][k]
    return sign * a[n - 1][n - 1] if n else 1


def abs_det(pres):
    if len(pres.rels) != pres.n_gen:
        raise ReplayError(f"unbalanced presentation {pres}")
    return abs(det(exponent_matrix(pres)))


def replay(pres, path, cyclic=True, cap=None, normalize=True, require_trivial=True):
    """Replay ``path`` from ``pres``; return the list of states (start first)."""
    cur = pres.reduced(cyclic).canonical() if normalize else pres
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
        if cap is not None and not isinstance(mv, dict) and max(map(len, cur.rels)) > cap:
            raise ReplayError(f"move {t} {mv!r} exceeds cap {cap}: {cur}")
        states.append(cur)
    if require_trivial and not cur.is_trivial():
        raise ReplayError(f"path ends at a non-trivial presentation {cur}")
    return states


def is_valid(pres, path, **kw):
    try:
        replay(pres, path, **kw)
        return True
    except ReplayError:
        return False
