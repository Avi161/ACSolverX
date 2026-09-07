"""Turn an automorphism-assisted path into an ordinary AC certificate.

WHY THIS IS POSSIBLE
--------------------
`cascade_heuristics`' ``s40_gen`` arm pushes Nielsen images into the same
heap as AC substitutions, so a solved path can contain steps of kind
``automorphism``. Such a path is still an AC solve, for two reasons that
compose:

1. **AC moves are equivariant under ``Aut(F2)``.** Apply ``phi^-1`` to every
   word of ``r_i -> r_i r_j``, ``r_i -> r_i^-1`` or ``r_i -> w r_i w^-1`` and
   the result is the same move on the images. So pushing the accumulated
   basis change back through the path collapses every automorphism step into
   a no-op and leaves a pure AC path from the input to ``Phi^-1`` of wherever
   the search stopped.

2. **The search stops on a basis.** Its terminal is a pair of distinct single
   generators, so ``Phi^-1`` of it is a basis of ``F2``. By Nielsen's theorem
   any basis reaches ``(x, y)`` by tuple Nielsen moves -- swap, invert,
   multiply -- and those are themselves AC moves.

Measured on MS640, step 2 costs about two moves.

WHAT THE SEARCH'S OWN NEIGHBOUR SET DOES NOT COVER
--------------------------------------------------
``get_neighbors_with_moves_nj`` emits only moves whose seam CANCELS -- a
pruning the search uses for speed. The image of a cancelling-seam move under
``phi^-1`` need not cancel, so a decoded path uses the full move set. Every
move is still an ordinary ``(target, jsign, k1, k2)`` and ``moves_to_states``
replays it, so certificates stay in the format the rest of the repo reads.
"""
from __future__ import annotations

import heapq

import numpy as np
from numba import njit

from experiments.equivalence_classes.lib.words import (
    SIGNED_PERMS, apply_hom, apply_pair, canon_pair, cyc_reduce, free_reduce,
    inv,
)
from experiments.search.greedy_baseline import (
    canonical_pair_nj, inverse_relator_nj, moves_to_states, reduce_relator_nj,
    str_to_arr,
)
from experiments.search.heuristic_1k import NIELSEN

IDENTITY = {"x": "x", "y": "y"}
ELEMENTARY = tuple(NIELSEN) + tuple(img for _, img in SIGNED_PERMS)


def _compose(first, second):
    """The image of applying ``first`` and then ``second``."""
    return {g: apply_hom(first[g], second) for g in "xy"}


_INVERSE = {}
for _a in ELEMENTARY:
    for _b in ELEMENTARY:
        if _compose(_a, _b) == IDENTITY:
            _INVERSE[tuple(sorted(_a.items()))] = _b
            break


def elementary_inverse(image):
    """Inverse of one Nielsen image or signed permutation."""
    key = tuple(sorted(image.items()))
    if key not in _INVERSE:
        raise ValueError(f"not an elementary automorphism: {image}")
    return _INVERSE[key]


def to_conjugator(pair, move):
    """``(target, jsign, c)`` -- the move with its conjugator as a WORD.

    A stored move is ``(target, jsign, k1, k2)`` with ``k1``/``k2`` rotation
    offsets into the current relators, and an offset means nothing once a
    basis change has rewritten the words. The conjugator it stands for does:
    ``rot_k(r) = u^-1 r u`` where ``u`` is the length ``len(r) - k`` prefix,
    so the move is ``(u^-1 r_i u)(p^-1 r_j^s p)``.

    One word is enough for both. Since
    ``(u^-1 r_i u)(p^-1 o_j p) = u^-1 [ r_i . (u p^-1 o_j p u^-1) ] u`` and the
    canonical form absorbs the outer conjugation, rotating ``r_i`` is the same
    as conjugating the other factor. So every AC move is
    ``r_i <- r_i . (c^-1 r_j^s c)`` for a single ``c = p . u^-1``, and under a
    basis change ``psi`` it is simply ``c -> psi(c)``. Verified against
    ``moves_to_states`` on 1,096 moves.

    NOTE: the pair is canonicalised first, exactly as the engine does. Reading
    the offsets off the raw pair is wrong and was a real bug -- ``('xyX',...)``
    cyclically reduces to ``('y',...)``, so the offsets index a different word.
    """
    pair = tuple(canon_pair(*pair))
    target, jsign, k1, k2 = move
    ri = pair[target - 1]
    rj = pair[2 - target]
    oj = rj if jsign == 1 else inv(rj)
    u = ri[:len(ri) - k1]
    p = oj[:len(oj) - k2]
    return target, jsign, free_reduce(p + inv(u))


def apply_conjugator(pair, target, jsign, c):
    """Apply a word-form move. Inverse of :func:`to_conjugator`."""
    pair = tuple(canon_pair(*pair))
    ri = pair[target - 1]
    rj = pair[2 - target]
    oj = rj if jsign == 1 else inv(rj)
    out = list(pair)
    out[target - 1] = cyc_reduce(free_reduce(ri + inv(c) + oj + c))
    return tuple(canon_pair(*out))


def is_terminal(pair):
    return (len(pair[0]) == len(pair[1]) == 1
            and pair[0].lower() != pair[1].lower())


@njit(cache=True)
def _match_move(r1, r2, t1, t2):
    """First ``(target, jsign, k1, k2)`` carrying ``(r1, r2)`` to ``(t1, t2)``.

    Returns ``(-1, 0, 0, 0)`` when no single move does. Unlike the search's
    enumeration this does not require the seam to cancel.
    """
    for target in range(1, 3):
        ri = r1 if target == 1 else r2
        rj = r2 if target == 1 else r1
        if len(ri) == 0:
            continue
        for si in range(2):
            jsign = 1 if si == 0 else -1
            oj = rj if jsign == 1 else inverse_relator_nj(rj)
            if len(oj) == 0:
                continue
            for k1 in range(len(ri)):
                rot_i = np.roll(ri, 2 * k1)
                for k2 in range(len(oj)):
                    piece = np.concatenate((rot_i, np.roll(oj, 2 * k2)))
                    if target == 1:
                        c1, c2 = reduce_relator_nj(piece, True), r2
                    else:
                        c1, c2 = r1, reduce_relator_nj(piece, True)
                    a, b = canonical_pair_nj(c1, c2)
                    if len(a) != len(t1) or len(b) != len(t2):
                        continue
                    same = True
                    for i in range(len(a)):
                        if a[i, 0] != t1[i, 0] or a[i, 1] != t1[i, 1]:
                            same = False
                            break
                    if same:
                        for i in range(len(b)):
                            if b[i, 0] != t2[i, 0] or b[i, 1] != t2[i, 1]:
                                same = False
                                break
                    if same:
                        return target, jsign, k1, k2
    return -1, 0, 0, 0


def find_move(source, target):
    """The AC move from ``source`` to ``target``, or ``None``."""
    got = _match_move(str_to_arr(source[0]), str_to_arr(source[1]),
                      str_to_arr(target[0]), str_to_arr(target[1]))
    return None if int(got[0]) < 0 else tuple(int(v) for v in got)


def push_back(pair, states, steps):
    """The path with every basis change pushed back to the start.

    ``t_k = Phi_k^-1(s_k)`` where ``Phi_k`` is the composite of the
    automorphisms applied up to step ``k``. An automorphism step leaves
    ``t`` unchanged, so it drops out; every other step stays an AC move.
    Truncated at the first terminal, which the recorded path can overshoot.
    """
    applied = []
    out = [tuple(canon_pair(*pair))]
    for index, step in enumerate(steps):
        if step.get("kind") == "automorphism":
            applied.append(step["images"])
        state = list(states[index + 1])
        for image in reversed(applied):
            state = list(apply_pair(state, elementary_inverse(image)))
        state = tuple(canon_pair(*state))
        if state != out[-1]:
            out.append(state)
        if is_terminal(state):
            break
    return out


def reduce_basis(basis, budget=4000):
    """AC moves carrying a basis of F2 to a terminal pair, shortest first."""
    if is_terminal(basis):
        return []
    seen = {basis: None}
    queue = [(sum(map(len, basis)), basis)]
    popped = 0
    while queue and popped < budget:
        _, current = heapq.heappop(queue)
        popped += 1
        a, b = str_to_arr(current[0]), str_to_arr(current[1])
        for target in (1, 2):
            ri, rj = (a, b) if target == 1 else (b, a)
            if len(ri) == 0:
                continue
            for jsign in (1, -1):
                oj = rj if jsign == 1 else inverse_relator_nj(rj)
                if len(oj) == 0:
                    continue
                for k1 in range(len(ri)):
                    for k2 in range(len(oj)):
                        move = (target, jsign, k1, k2)
                        child = tuple(moves_to_states(
                            current[0], current[1], [move])[-1])
                        if child in seen:
                            continue
                        seen[child] = (current, move)
                        if is_terminal(child):
                            moves, node = [], child
                            while seen[node] is not None:
                                node, move = seen[node][0], seen[node][1]
                                moves.append(move)
                            return moves[::-1]
                        heapq.heappush(queue, (sum(map(len, child)), child))
    return None


def _children(pair):
    """Every ``(child, move)`` one encodable AC move reaches."""
    a, b = str_to_arr(pair[0]), str_to_arr(pair[1])
    out = {}
    for target in (1, 2):
        ri, rj = (a, b) if target == 1 else (b, a)
        if len(ri) == 0:
            continue
        for jsign in (1, -1):
            oj = rj if jsign == 1 else inverse_relator_nj(rj)
            if len(oj) == 0:
                continue
            for k1 in range(len(ri)):
                for k2 in range(len(oj)):
                    move = (target, jsign, k1, k2)
                    child = tuple(moves_to_states(pair[0], pair[1], [move])[-1])
                    out.setdefault(child, move)
    return out


def bridge(source, target, max_depth=3):
    """A short move sequence from ``source`` to ``target``, or ``None``.

    A pushed-back step can need a conjugated multiplication
    ``w r_i w^-1 r_j`` whose conjugator is not a rotation of ``r_i``. That is
    an ordinary AC move but the repo's ``(target, jsign, k1, k2)`` encoding
    builds only ``rot(r_i).rot(r_j^s)``, so it cannot say it in one step --
    the giveaway is a child longer than ``|r_i| + |r_j|``. Several encodable
    moves compose to the same thing, and this finds them.
    """
    if source == target:
        return []
    # Close with `find_move` rather than by walking into the target. A blind
    # BFS branches ~400 per node here, so depth 3 is ~35 minutes; closing the
    # last step with the matcher makes depth d cost d-1 expansions instead of
    # d, which is the difference between seconds and unusable.
    limit = sum(map(len, target)) + 2 * max(map(len, target))
    frontier = {source: []}
    seen = {source}
    for depth in range(1, max_depth + 1):
        for state, moves in frontier.items():
            move = find_move(state, target)
            if move is not None:
                return moves + [move]
        if depth == max_depth:
            return None
        nxt = {}
        for state, moves in frontier.items():
            for child, move in _children(state).items():
                if child in seen or sum(map(len, child)) > limit:
                    continue
                seen.add(child)
                nxt[child] = moves + [move]
        if not nxt:
            return None
        frontier = nxt
    return None


def decode(pair, states, steps, basis_budget=4000, bridge_depth=3):
    """``(moves, info)`` -- an AC certificate for ``pair``, or ``(None, info)``.

    Never returns moves it has not replayed: the last act is to run the whole
    sequence through ``moves_to_states`` from the original input and require
    a terminal pair.
    """
    info = {"basis_moves": 0, "bridged": 0, "reason": None}
    path = push_back(pair, states, steps)
    moves = []
    for source, target in zip(path, path[1:]):
        move = find_move(source, target)
        if move is not None:
            moves.append(move)
            continue
        span = bridge(source, target, bridge_depth)
        if span is None:
            info["reason"] = (f"no AC move sequence of depth <= {bridge_depth} "
                              f"from {source} to {target}")
            return None, info
        moves += span
        info["bridged"] += 1
    if not is_terminal(path[-1]):
        tail = reduce_basis(path[-1], basis_budget)
        if tail is None:
            info["reason"] = f"basis {path[-1]} not reduced within budget"
            return None, info
        moves += tail
        info["basis_moves"] = len(tail)
    replay = moves_to_states(pair[0], pair[1], moves)
    if not is_terminal(tuple(replay[-1])):
        info["reason"] = f"replay ended at {tuple(replay[-1])}, not terminal"
        return None, info
    info.update(moves=len(moves), path=[list(s) for s in replay],
                final=list(replay[-1]))
    return moves, info
