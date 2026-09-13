"""Slow, obviously-correct reference for the cap-bounded AC closure BFS.

This module is the oracle: pure Python, words are tuples of signed ints
(``x = 1``, ``X = -1``, ``y = 2``, ``Y = -2``), every operation is written the
straightforward way and nothing is packed, cached or fused.  ``capbfs.py`` is
the fast numba implementation of *exactly* the same model, and
``test_capbfs.py`` pins the two together.

THE MODEL (see README.md for the mathematical justification)
------------------------------------------------------------
A state is an unordered pair ``{r1, r2}`` of nonempty cyclically reduced
*cyclic* words over ``F2 = F(x, y)``, each taken up to cyclic rotation and
inversion.  The canonical key of a relator is the minimum, under the fixed
letter order ``x < X < y < Y``, over all rotations of the word and all
rotations of its inverse; the canonical key of a state is the pair of relator
keys sorted by ``(length, letter order)``.

A move out of a state, given a cap ``c``:

  * pick ``i != j`` in ``{0, 1}`` (``r_i`` is replaced, ``r_j`` is kept),
  * pick a sign ``e`` in ``{+1, -1}``,
  * pick a rotation offset ``a`` of ``r_i`` and ``p`` of ``r_j**e``
    (rotation = ``w[k:] + w[:k]``, i.e. rotate LEFT by ``k``),
  * pick a connector ``w``: any freely reduced word (possibly empty) with
    ``len(w) <= (c - len(r_i) - len(r_j)) // 2``; when that bound is negative
    only the empty connector is tried,
  * form ``R = cyc_reduce(free_reduce(rot_a(r_i) . w . rot_p(r_j**e) . w**-1))``.

The move is allowed iff ``1 <= len(R) <= c``; the new state is ``{R, r_j}``.

BFS explores complete levels.  It stops when the frontier is empty (CLOSED),
when discovering one more state would exceed ``max_states`` (budget), or at the
end of the level in which the trivial state ``{x, y}`` is discovered (SOLVED).
Finishing the level makes the returned state set exactly a ball of some radius
around the start, hence independent of the order in which moves are
enumerated -- which is what lets the fast and the reference search be compared
as sets.
"""

from __future__ import annotations

import time
from collections import deque

# --------------------------------------------------------------------------
# alphabet
# --------------------------------------------------------------------------
INT_TO_CHAR = {1: "x", -1: "X", 2: "y", -2: "Y"}
CHAR_TO_INT = {v: k for k, v in INT_TO_CHAR.items()}

#: fixed letter order used by every canonicalisation here and in ``capbfs.py``
ORDER = {1: 0, -1: 1, 2: 2, -2: 3}

#: the connector alphabet, in the order both implementations enumerate it
ALPHABET = (1, -1, 2, -2)

TRIVIAL = ((1,), (2,))


def word_to_str(w):
    return "".join(INT_TO_CHAR[c] for c in w)


def str_to_word(s):
    return tuple(CHAR_TO_INT[c] for c in s)


def okey(w):
    """Sort key of a word under the fixed letter order ``x < X < y < Y``."""
    return tuple(ORDER[c] for c in w)


# --------------------------------------------------------------------------
# free group operations
# --------------------------------------------------------------------------
def inv_word(w):
    return tuple(-c for c in reversed(w))


def free_reduce(w):
    out = []
    for c in w:
        if out and out[-1] == -c:
            out.pop()
        else:
            out.append(c)
    return tuple(out)


def cyc_reduce(w):
    w = free_reduce(w)
    while len(w) >= 2 and w[0] == -w[-1]:
        w = w[1:-1]
    return w


def rot(w, k):
    """Rotate LEFT by ``k``: ``rot(w, k) = w[k:] + w[:k]``."""
    if not w:
        return w
    k %= len(w)
    return w[k:] + w[:k]


def canon_rel(w):
    """Lex-min over all rotations of ``w`` and of ``w**-1``.

    ``w`` must be a nonempty cyclically reduced word; the result has the same
    length and is again cyclically reduced.
    """
    if not w:
        raise ValueError("empty relator has no canonical form")
    best = None
    for u in (w, inv_word(w)):
        for k in range(len(u)):
            r = rot(u, k)
            kk = okey(r)
            if best is None or kk < best[0]:
                best = (kk, r)
    return best[1]


def canon_pair(r1, r2):
    """Canonical key of the unordered state ``{r1, r2}``."""
    a, b = canon_rel(cyc_reduce(r1)), canon_rel(cyc_reduce(r2))
    if (len(a), okey(a)) > (len(b), okey(b)):
        a, b = b, a
    return (a, b)


def pair_to_strs(pair):
    return [word_to_str(pair[0]), word_to_str(pair[1])]


# --------------------------------------------------------------------------
# connectors
# --------------------------------------------------------------------------
def connectors(max_len):
    """All freely reduced words of length ``<= max_len``, shortest first.

    Within a length they come in the order induced by extending the previous
    length's list on the right by ``x, X, y, Y``.  ``capbfs.py`` builds the
    identical list in the identical order, so move descriptors agree.
    """
    if max_len < 0:
        return [()]
    out = [()]
    frontier = [()]
    for _ in range(max_len):
        nxt = []
        for u in frontier:
            for c in ALPHABET:
                if u and u[-1] == -c:
                    continue
                nxt.append(u + (c,))
        out.extend(nxt)
        frontier = nxt
    return out


# --------------------------------------------------------------------------
# move generation
# --------------------------------------------------------------------------
def neighbours(state, cap):
    """Every allowed move out of ``state`` at cap ``cap``.

    Returns a list of ``(move, child)`` with ``move = (i, e, a, p, w)``: ``i``
    indexes the relator of ``state`` that is replaced, ``e`` is the sign on the
    other relator, ``a`` and ``p`` are left-rotation offsets and ``w`` is the
    connector (a tuple of signed ints).  ``child`` is the canonical key of the
    resulting state.  Duplicates are NOT removed.
    """
    r = state
    if not r[0] or not r[1]:
        raise ValueError("state contains an empty relator")
    budget = (cap - len(r[0]) - len(r[1])) // 2
    conns = connectors(budget)
    out = []
    for i in (0, 1):
        ri, rj = r[i], r[1 - i]
        for e in (1, -1):
            oj = rj if e == 1 else inv_word(rj)
            for a in range(len(ri)):
                ra = rot(ri, a)
                for p in range(len(oj)):
                    rp = rot(oj, p)
                    for w in conns:
                        prod = cyc_reduce(free_reduce(ra + w + rp + inv_word(w)))
                        if 1 <= len(prod) <= cap:
                            out.append(((i, e, a, p, w), canon_pair(prod, rj)))
    return out


def neighbour_set(state, cap):
    """The set of canonical children of ``state`` (no move labels)."""
    return {child for _, child in neighbours(state, cap)}


# --------------------------------------------------------------------------
# BFS
# --------------------------------------------------------------------------
def bfs(r1, r2, cap, max_states=1_000_000, stop_when_solved=True):
    """Reference cap-bounded BFS.  Returns the result dict documented above."""
    if isinstance(r1, str):
        r1 = str_to_word(r1)
    if isinstance(r2, str):
        r2 = str_to_word(r2)
    if not cyc_reduce(r1) or not cyc_reduce(r2):
        raise ValueError("initial presentation has an empty relator")
    start = canon_pair(r1, r2)
    if max(len(start[0]), len(start[1])) > cap:
        raise ValueError("initial presentation already exceeds the cap")

    t0 = time.perf_counter()
    seen = {start: (None, None)}          # state -> (parent, move)
    order = [start]
    frontier = deque([start])
    solved_state = start if start == TRIVIAL else None
    min_total = len(start[0]) + len(start[1])
    popped = 0
    closed = True
    budget_hit = False

    while frontier and not (stop_when_solved and solved_state is not None):
        level = list(frontier)
        frontier.clear()
        for state in level:
            popped += 1
            for move, child in neighbours(state, cap):
                if not child[0] or not child[1]:
                    raise ValueError("generated an empty relator")
                if child in seen:
                    continue
                if len(seen) >= max_states:
                    budget_hit = True
                    closed = False
                    break
                seen[child] = (state, move)
                order.append(child)
                frontier.append(child)
                min_total = min(min_total, len(child[0]) + len(child[1]))
                if child == TRIVIAL:
                    solved_state = child
            if budget_hit:
                break
        if budget_hit:
            break
    if frontier and not budget_hit:
        closed = False                    # stopped because we solved

    seconds = time.perf_counter() - t0
    res = {
        "initial": pair_to_strs(start),
        "cap": cap,
        "closed": closed and not budget_hit,
        "solved": solved_state is not None,
        "states": len(seen),
        "max_states": max_states,
        "min_total_length_seen": min_total,
        "frontier_size_at_stop": len(frontier),
        "seconds": seconds,
        "nodes_per_second": (popped / seconds) if seconds > 0 else 0.0,
        "popped": popped,
        "budget_exhausted": budget_hit,
        "engine": "reference",
    }
    if solved_state is not None:
        moves = []
        states = []
        cur = TRIVIAL
        while cur is not None:
            states.append(cur)
            parent, move = seen[cur]
            if parent is None:
                break
            moves.append(move)
            cur = parent
        states.reverse()
        moves.reverse()
        res["path"] = [
            {"i": m[0], "j": 1 - m[0], "e": m[1], "a": m[2], "p": m[3],
             "w": word_to_str(m[4])}
            for m in moves
        ]
        res["path_states"] = [pair_to_strs(s) for s in states]
    res["_states_set"] = seen           # not JSON; for the tests
    res["_order"] = order
    return res


def state_key_strings(result):
    """Sorted list of ``'r1,r2'`` strings for every discovered state."""
    return sorted(
        "%s,%s" % (word_to_str(s[0]), word_to_str(s[1]))
        for s in result["_states_set"]
    )
