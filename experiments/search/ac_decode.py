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
``phi^-1`` need not cancel, so a decoded path uses the full move set. The
legacy ``decode`` function below represents these operations with
``(target, jsign, k1, k2)`` moves. ``decode_elementary`` instead expands them
into a JSON-safe stream of generator-level invert, swap, conjugate and multiply
operations, and ``replay_elementary`` verifies that stream without implicit
canonicalization.
"""
from __future__ import annotations

import heapq
from collections import deque

import numpy as np
from numba import njit

from experiments.equivalence_classes.lib.words import (
    SIGNED_PERMS, apply_hom, apply_pair, canon_pair, canon_rel, cyc_reduce,
    free_reduce, inv,
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


def _canonical_word_witness(word, target):
    """Return ``(sign, conjugator)`` with target = c^-1 word^sign c."""
    reduced = free_reduce(word)
    stripped = []
    while len(reduced) >= 2 and reduced[0] == reduced[-1].swapcase():
        stripped.append(reduced[0])
        reduced = reduced[1:-1]
    outer = "".join(stripped)
    if target != canon_rel(word):
        raise ValueError(f"{target!r} is not the canonical form of {word!r}")
    if not reduced:
        return 1, ""
    for sign, oriented in ((1, reduced), (-1, inv(reduced))):
        for cut in range(len(oriented)):
            if oriented[cut:] + oriented[:cut] != target:
                continue
            conjugator = free_reduce(outer + oriented[:cut])
            check = free_reduce(
                inv(conjugator) + (word if sign == 1 else inv(word)) + conjugator)
            if check == target:
                return sign, conjugator
    raise AssertionError(f"no canonicalization witness for {word!r} -> {target!r}")


class _ElementaryTrace:
    def __init__(self, pair):
        self.pair = [free_reduce(pair[0]), free_reduce(pair[1])]
        self.moves = []

    def _record(self, move):
        self.moves.append(move)

    def invert(self, target):
        if isinstance(target, bool) or target not in (1, 2):
            raise ValueError(f"target must be 1 or 2, got {target!r}")
        i = target - 1
        self.pair[i] = inv(self.pair[i])
        self._record({"op": "invert", "target": target})

    def swap(self):
        self.pair.reverse()
        self._record({"op": "swap"})

    def conjugate_letter(self, target, letter):
        if isinstance(target, bool) or target not in (1, 2):
            raise ValueError(f"target must be 1 or 2, got {target!r}")
        if len(letter) != 1 or letter not in "xXyY":
            raise ValueError(f"conjugation must use one generator letter: {letter!r}")
        i = target - 1
        self.pair[i] = free_reduce(inv(letter) + self.pair[i] + letter)
        self._record({"op": "conjugate", "target": target, "by": letter})

    def conjugate_word(self, target, word):
        if any(letter not in "xXyY" for letter in word):
            raise ValueError(f"conjugation word is outside F2: {word!r}")
        i = target - 1
        self.pair[i] = free_reduce(inv(word) + self.pair[i] + word)
        self.moves.extend(
            {"op": "conjugate", "target": target, "by": letter}
            for letter in word)

    def multiply(self, target, source):
        if (isinstance(target, bool) or isinstance(source, bool)
                or target not in (1, 2) or source not in (1, 2) or target == source):
            raise ValueError(
                f"multiply requires distinct target/source in 1,2; got {target!r}/{source!r}")
        i, j = target - 1, source - 1
        self.pair[i] = free_reduce(self.pair[i] + self.pair[j])
        self._record({"op": "multiply", "target": target, "source": source})

    def conjugated_multiply(self, target, source_sign, conjugator):
        source = 2 if target == 1 else 1
        if source_sign == -1:
            self.invert(source)
        self.conjugate_word(source, conjugator)
        self.multiply(target, source)
        self.conjugate_word(source, inv(conjugator))
        if source_sign == -1:
            self.invert(source)


def replay_elementary(pair, moves, keep_states=False):
    """Replay the elementary JSON move schema without canonicalization."""
    code = {"x": 1, "X": -1, "y": 2, "Y": -2}
    symbol_to_letter = {1: "x", -1: "X", 2: "y", -2: "Y"}
    current = [deque(code[c] for c in free_reduce(word)) for word in pair]

    def words():
        return ["".join(symbol_to_letter[c] for c in word) for word in current]

    def append_reduced(word, symbol):
        if word and word[-1] == -symbol:
            word.pop()
        else:
            word.append(symbol)

    states = [words()]
    for move in moves:
        op = move.get("op")
        if op == "invert":
            target = move["target"]
            if isinstance(target, bool) or target not in (1, 2):
                raise ValueError(f"target must be 1 or 2, got {target!r}")
            current[target - 1] = deque(-c for c in reversed(current[target - 1]))
        elif op == "swap":
            current.reverse()
        elif op == "conjugate":
            target = move["target"]
            letter = move["by"]
            if isinstance(target, bool) or target not in (1, 2):
                raise ValueError(f"target must be 1 or 2, got {target!r}")
            if len(letter) != 1 or letter not in "xXyY":
                raise ValueError(f"conjugation must use one generator letter: {letter!r}")
            i = target - 1
            symbol = code[letter]
            if current[i] and current[i][0] == symbol:
                current[i].popleft()
            else:
                current[i].appendleft(-symbol)
            append_reduced(current[i], symbol)
        elif op == "multiply":
            target, source = move["target"], move["source"]
            if (isinstance(target, bool) or isinstance(source, bool)
                    or target not in (1, 2) or source not in (1, 2)
                    or target == source):
                raise ValueError(
                    f"multiply requires distinct target/source in 1,2; "
                    f"got {target!r}/{source!r}")
            for symbol in current[source - 1]:
                append_reduced(current[target - 1], symbol)
        else:
            raise ValueError(f"unknown elementary AC operation: {op!r}")
        if keep_states:
            states.append(words())
    return states if keep_states else words()


def _emit_canonicalization(trace, raw_pair, target_pair, inverse_image):
    own = [canon_rel(raw_pair[0]), canon_rel(raw_pair[1])]
    for i in range(2):
        sign, conjugator = _canonical_word_witness(raw_pair[i], own[i])
        if sign == -1:
            trace.invert(i + 1)
        trace.conjugate_word(i + 1, apply_hom(conjugator, inverse_image))
    target = list(target_pair)
    if own == target:
        return
    if own[::-1] == target:
        trace.swap()
        return
    raise AssertionError(f"pair canonicalization mismatch: {own} -> {target}")


def _emit_signed_permutation(trace, image):
    x_image, y_image = image["x"], image["y"]
    if len(x_image) != 1 or len(y_image) != 1:
        raise ValueError(f"not a signed permutation: {image}")
    if x_image.lower() == "y":
        trace.swap()
    if x_image.isupper():
        trace.invert(1)
    if y_image.isupper():
        trace.invert(2)


def _emit_tuple_image(trace, image):
    for index, candidate in enumerate(NIELSEN):
        if image != candidate:
            continue
        target = 1 if index < 2 else 2
        sign = 1 if index % 2 == 0 else -1
        trace.conjugated_multiply(target, sign, "")
        return
    if image in [candidate for _, candidate in SIGNED_PERMS]:
        _emit_signed_permutation(trace, image)
        return
    raise ValueError(f"not an elementary automorphism: {image}")


def decode_elementary(pair, states, steps):
    if states is None:
        states = states_from_steps(pair, steps)
    """Convert a mixed certificate to generator-level elementary AC moves."""
    if len(states) != len(steps) + 1:
        raise ValueError("states must contain exactly one more entry than steps")
    if tuple(states[0]) != tuple(canon_pair(*pair)):
        raise ValueError("certificate root does not match the canonical input")

    trace = _ElementaryTrace(pair)
    inverse_image = dict(IDENTITY)
    applied = []
    _emit_canonicalization(trace, pair, states[0], inverse_image)
    if trace.pair != [apply_hom(w, inverse_image) for w in states[0]]:
        raise AssertionError("initial canonicalization frame mismatch")

    for index, step in enumerate(steps):
        current = tuple(states[index])
        target_state = tuple(states[index + 1])
        if step.get("kind") == "automorphism":
            image = step["images"]
            inverse_image = _compose(elementary_inverse(image), inverse_image)
            applied.append(image)
            raw = tuple(apply_hom(word, image) for word in current)
        elif step.get("kind") == "substitution":
            move = tuple(map(int, step["move"].split("_")))
            target, source_sign, conjugator = to_conjugator(current, move)
            transported = apply_hom(conjugator, inverse_image)
            trace.conjugated_multiply(target, source_sign, transported)
            source = current[2 - target]
            oriented = source if source_sign == 1 else inv(source)
            raw = list(current)
            raw[target - 1] = free_reduce(
                current[target - 1] + inv(conjugator) + oriented + conjugator)
            raw = tuple(raw)
        else:
            raise ValueError(f"unknown mixed step kind: {step.get('kind')!r}")

        _emit_canonicalization(trace, raw, target_state, inverse_image)
        expected = [apply_hom(word, inverse_image) for word in target_state]
        if trace.pair != expected:
            raise AssertionError(
                f"transport frame diverged at mixed step {index}: "
                f"got={trace.pair}, expected={expected}")

    terminal = list(states[-1])
    if not is_terminal(tuple(terminal)):
        raise ValueError(f"mixed certificate does not end at a basis: {terminal}")
    if terminal[0].lower() == "y":
        trace.swap()
        terminal.reverse()
    if terminal[0] == "X":
        trace.invert(1)
    if terminal[1] == "Y":
        trace.invert(2)
    for image in reversed(applied):
        _emit_tuple_image(trace, image)

    if trace.pair != ["x", "y"]:
        raise AssertionError(f"elementary replay ended at {trace.pair}, not ['x', 'y']")
    replayed = replay_elementary(pair, trace.moves)
    if replayed != ["x", "y"]:
        raise AssertionError(f"independent elementary replay ended at {replayed}")
    return trace.moves


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


def states_from_steps(pair, steps):
    """Rebuild the state sequence from the moves alone.

    States are redundant with the moves: a substitution replays through
    ``moves_to_states`` and a basis change through ``apply_pair``. Verified
    exact on 617/617 solved AC19 rows. That is what lets the persisted
    certificate be move-wise only -- 889 bytes a row against 1,278 with
    states and 10,440 with the elementary expansion -- while the elementary
    form stays available on demand.
    """
    from experiments.search.greedy_baseline import moves_to_states, str_to_move

    current = list(canon_pair(*pair))
    out = [list(current)]
    for step in steps:
        if step.get("kind") == "automorphism":
            current = list(apply_pair(current, step["images"]))
        else:
            current = list(moves_to_states(
                current[0], current[1], [str_to_move(step["move"])])[-1])
        out.append(list(current))
    return out


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
