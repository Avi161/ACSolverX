# Research snapshot of codex/ac-elementary-decoder ea0b3e16 core, with terminal-tail transport.
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


def decode_elementary(pair, states, steps, elementary_tail=None):
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
        elif step.get("kind") == "elementary":
            raw = tuple(replay_elementary(current, step["moves"]))
            for move in step["moves"]:
                op = move["op"]
                if op == "conjugate":
                    trace.conjugate_word(move["target"], apply_hom(move["by"], inverse_image))
                elif op == "invert":
                    trace.invert(move["target"])
                elif op == "multiply":
                    trace.multiply(move["target"], move["source"])
                elif op == "swap":
                    trace.swap()
                else:
                    raise ValueError(f"unknown elementary block operation: {op!r}")
            if trace.pair != [apply_hom(word, inverse_image) for word in raw]:
                raise AssertionError("elementary block transport mismatch")
        else:
            raise ValueError(f"unknown mixed step kind: {step.get('kind')!r}")

        _emit_canonicalization(trace, raw, target_state, inverse_image)
        expected = [apply_hom(word, inverse_image) for word in target_state]
        if trace.pair != expected:
            raise AssertionError(
                f"transport frame diverged at mixed step {index}: "
                f"got={trace.pair}, expected={expected}")

    if elementary_tail is not None:
        from research.supermoves_20260908.two_block import replay as replay_packed
        if replay_packed(states[-1], elementary_tail) != ["x", "y"]:
            raise ValueError("elementary tail is not terminal from mixed endpoint")
        for move in elementary_tail:
            if move[0] == "I":
                trace.invert(move[1])
            elif move[0] == "S":
                trace.swap()
            elif move[0] == "M":
                trace.multiply(move[1], move[2])
            elif move[0] == "C":
                trace.conjugate_word(move[1], apply_hom(move[2], inverse_image))
            else:
                raise ValueError("unknown elementary tail operation")
        terminal = ["x", "y"]
    else:
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

