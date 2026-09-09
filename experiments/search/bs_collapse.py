"""Bounded, proof-carrying rewrites for a recognized conjugate-power relator."""
from __future__ import annotations

from experiments.equivalence_classes.lib.words import (
    canon_pair, canon_rel, cyc_reduce, free_reduce, inv, replay_move, rot,
)


class _Limit(Exception):
    pass


def _recognize(pair):
    for donor_index, donor in enumerate(pair):
        if len(donor) != 5:
            continue
        for a in "xXyY":
            for b in "xXyY":
                if a.lower() == b.lower():
                    continue
                relation = inv(b) + a + b + inv(a) * 2
                if canon_rel(relation) != donor:
                    continue
                companion = pair[1 - donor_index]
                exponent = companion.count(b) - companion.count(inv(b))
                if abs(exponent) == 1:
                    return a, b, relation, inv(companion) if exponent == 1 else companion
    return None


def _pinch(word, a, b):
    n = len(word)
    for reverse in (True, False):
        left, right = (b, inv(b)) if reverse else (inv(b), b)
        for i in range(n):
            if word[i] != left:
                continue
            oriented = word[i:] + word[:i]
            j = 1
            while j < n and oriented[j].lower() == a.lower():
                j += 1
            if j == 1 or j == n or oriented[j] != right:
                continue
            sign = oriented[1]
            if reverse:
                if (j - 1) % 2:
                    continue
                return oriented, b + sign * 2, sign + b
            return oriented, inv(b) + sign, sign * 2 + inv(b)
    return None


def bs_collapse(pair, budget=10_000, intermediate_cap=256):
    """Return a substitution-only path, charging the root and every rewrite.

    Recognizes any signed-generator version of b^-1 a b a^-2, up to
    cyclic rotation/inversion and relator swap. No basis normalization is
    performed here. A caller can prepend its separately verified basis path.
    """
    if isinstance(budget, bool) or not isinstance(budget, int) or not 1 <= budget <= 10_000:
        raise ValueError("budget must be an integer in 1..10000")
    if intermediate_cap is not None and (isinstance(intermediate_cap, bool)
            or not isinstance(intermediate_cap, int) or intermediate_cap < 1):
        raise ValueError("intermediate_cap must be None or a positive integer")
    if len(pair) != 2 or any(not isinstance(w, str) or set(w) - set("xXyY") for w in pair):
        raise ValueError("expected two words over xXyY")

    state = canon_pair(*pair)
    states = [list(state)]
    steps = []
    peak = max(map(len, state))
    raw_peak = peak
    pattern = None

    def result(solved, reason, applicable):
        return dict(solved=solved, applicable=applicable, recognized=applicable, reason=reason,
                    nodes_explored=len(steps) + 1, rewrites=len(steps),
                    states=states, steps=steps,
                    path_moves=[s["move"] for s in steps],
                    max_intermediate_relator_length=peak,
                    max_relator_length=peak,
                    max_raw_product_length=raw_peak,
                    intermediate_cap=intermediate_cap, pattern=pattern)

    def rewrite(word, donor, lhs, rhs, position=0):
        nonlocal state, peak, raw_peak
        if len(steps) + 1 >= budget:
            raise _Limit("budget")
        if word[position:position + len(lhs)] != lhs:
            raise AssertionError("rewrite does not match the oriented word")
        desired_word = cyc_reduce(free_reduce(word[:position] + rhs + word[position + len(lhs):]))
        desired_pair = canon_pair(desired_word, donor)
        if intermediate_cap is not None and max(map(len, desired_pair)) > intermediate_cap:
            raise _Limit("intermediate_cap")
        target_word = canon_rel(word)
        target = 0 if state[0] == target_word else 1
        if state[target] != target_word or state[1 - target] != canon_rel(donor):
            raise AssertionError("tracked words do not match the current state")

        actual = state[target]
        shift = (word + word).find(actual)
        local_lhs, local_rhs = lhs, rhs
        if 0 <= shift < len(word):
            start = (position - shift) % len(word)
        else:
            inverted = inv(word)
            shift = (inverted + inverted).find(actual)
            if not 0 <= shift < len(word):
                raise AssertionError("canonical target is not a rotation or inverse")
            start = (len(word) - position - len(lhs) - shift) % len(word)
            local_lhs, local_rhs = inv(lhs), inv(rhs)
        donor_needed = free_reduce(inv(local_lhs) + local_rhs)
        donor_move = None
        for sign in (1, -1):
            oriented = state[1 - target] if sign == 1 else inv(state[1 - target])
            for cut in range(len(oriented)):
                if rot(oriented, cut) == donor_needed:
                    donor_move = sign, cut
                    break
            if donor_move is not None:
                break
        if donor_move is None:
            raise AssertionError("replacement is not a cyclic donor substitution")
        sign, cut = donor_move
        target_cut = (-(start + len(local_lhs))) % len(actual)
        move = (target + 1, sign, target_cut, cut)
        child = replay_move(state, move)
        if child != desired_pair:
            raise AssertionError("substitution does not produce the intended rewrite")
        raw_peak = max(raw_peak, len(actual) + len(state[1 - target]))
        state = child
        peak = max(peak, max(map(len, state)))
        steps.append({"kind": "substitution", "move": "_".join(map(str, move))})
        states.append(list(state))
        return desired_word

    if intermediate_cap is not None and peak > intermediate_cap:
        return result(False, "input_cap", False)
    if all(len(w) == 1 for w in state) and state[0].lower() != state[1].lower():
        return result(True, "terminal", True)
    recognized = _recognize(state)
    if recognized is None:
        return result(False, "not_recognized", False)
    a, b, relation, companion = recognized
    pattern = {"a": a, "b": b, "power": 2}
    try:
        while sum(c.lower() == b.lower() for c in companion) > 1:
            pinch = _pinch(companion, a, b)
            if pinch is None:
                return result(False, "normal_form_stalled", True)
            companion, lhs, rhs = pinch
            companion = rewrite(companion, relation, lhs, rhs)

        index = companion.find(inv(b))
        if index < 0:
            raise AssertionError("companion lost its stable-letter exponent")
        companion = companion[index:] + companion[:index]
        power = companion[1:]
        if any(c.lower() != a.lower() for c in power):
            raise AssertionError("single-occurrence companion has another stable letter")
        while any(c.lower() == b.lower() for c in relation):
            index = next(i for i, c in enumerate(relation) if c.lower() == b.lower())
            letter = relation[index]
            relation = rewrite(relation, companion, letter,
                               power if letter == b else inv(power), index)
        if relation != inv(a):
            raise AssertionError("eliminating the stable letter did not yield the generator")
        while any(c.lower() == a.lower() for c in companion):
            index = next(i for i, c in enumerate(companion) if c.lower() == a.lower())
            companion = rewrite(companion, relation, companion[index], "", index)
    except _Limit as exc:
        return result(False, str(exc), True)
    solved = all(len(w) == 1 for w in state) and state[0].lower() != state[1].lower()
    if not solved:
        raise AssertionError("completed rewrites are not terminal")
    return result(True, "collapsed", True)


collapse = bs_collapse
