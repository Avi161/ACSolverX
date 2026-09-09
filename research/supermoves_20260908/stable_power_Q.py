"""Proof-carrying collapse for the stable-power Q_(k,N) family."""
from __future__ import annotations

from experiments.equivalence_classes.lib.words import (
    canon_pair, canon_rel, cyc_reduce, free_reduce, inv, replay_move, rot,
)


class _Limit(Exception):
    pass


def _power(letter_or_word, exponent):
    return letter_or_word * exponent if exponent >= 0 else inv(letter_or_word) * (-exponent)


def _exponent(word, letter):
    return word.count(letter) - word.count(inv(letter))


def _recognize(pair):
    matches = []
    for donor_index, donor in enumerate(pair):
        if len(donor) < 5 or len(donor) % 2 != 1:
            continue
        k = (len(donor) - 3) // 2
        for a in "xXyY":
            for b in "xXyY":
                if a.lower() == b.lower():
                    continue
                relation = inv(a) * 2 + inv(b) * k + a + b * k
                if canon_rel(relation) != donor:
                    continue
                companion = pair[1 - donor_index]
                for oriented_companion in (companion, inv(companion)):
                    n = -_exponent(oriented_companion, a) - 1
                    q = _power(inv(a), n) + b * (k - 1) + inv(a) + inv(b) * k
                    if canon_rel(q) == companion:
                        match = (donor_index, a, b, k, n, relation, q)
                        if match not in matches:
                            matches.append(match)
    return matches


def collapse(pair, budget=1000, intermediate_cap=256):
    """Collapse a signed/cyclic/inverse/swapped Q_(k,N) presentation.

    The returned path contains ordinary substitution-codec moves only.  The
    root is charged, so a certificate with ``r`` rewrites needs budget at
    least ``r+1``.
    """
    if isinstance(budget, bool) or not isinstance(budget, int) or not 1 <= budget <= 1000:
        raise ValueError("budget must be an integer in 1..1000")
    if intermediate_cap is not None and (
        isinstance(intermediate_cap, bool)
        or not isinstance(intermediate_cap, int)
        or intermediate_cap < 1
    ):
        raise ValueError("intermediate_cap must be None or a positive integer")
    if len(pair) != 2 or any(
        not isinstance(word, str) or set(word) - set("xXyY") for word in pair
    ):
        raise ValueError("expected two words over xXyY")

    state = canon_pair(*pair)
    states = [list(state)]
    steps = []
    peak = max(map(len, state))
    raw_peak = peak
    pattern = None

    def result(solved, reason, applicable):
        return dict(
            solved=solved,
            applicable=applicable,
            recognized=applicable,
            reason=reason,
            nodes_explored=len(steps) + 1,
            rewrites=len(steps),
            states=states,
            steps=steps,
            path_moves=[step["move"] for step in steps],
            max_intermediate_relator_length=peak,
            max_relator_length=peak,
            max_raw_product_length=raw_peak,
            intermediate_cap=intermediate_cap,
            pattern=pattern,
        )

    def rewrite(word, donor, lhs, rhs, position):
        nonlocal state, peak, raw_peak
        if len(steps) + 1 >= budget:
            raise _Limit("budget")
        if word[position : position + len(lhs)] != lhs:
            raise AssertionError("rewrite does not match the oriented word")
        raw_desired = word[:position] + rhs + word[position + len(lhs) :]
        desired_word = cyc_reduce(free_reduce(raw_desired))
        desired_pair = canon_pair(desired_word, donor)
        if intermediate_cap is not None and max(map(len, desired_pair)) > intermediate_cap:
            raise _Limit("intermediate_cap")

        target_word = canon_rel(word)
        donor_word = canon_rel(donor)
        candidates = [i for i in (0, 1) if state[i] == target_word and state[1 - i] == donor_word]
        if not candidates:
            raise AssertionError("tracked words do not match the current state")
        target = candidates[0]
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

        needed = free_reduce(inv(local_lhs) + local_rhs)
        donor_move = None
        for sign in (1, -1):
            oriented = state[1 - target] if sign == 1 else inv(state[1 - target])
            for cut in range(len(oriented)):
                if rot(oriented, cut) == needed:
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
        raw_peak = max(raw_peak, len(actual) + len(state[1 - target]), len(raw_desired))
        state = child
        peak = max(peak, max(map(len, state)))
        steps.append({"kind": "substitution", "move": "_".join(map(str, move))})
        states.append(list(state))

    if intermediate_cap is not None and peak > intermediate_cap:
        return result(False, "input_cap", False)
    if all(len(word) == 1 for word in state) and state[0].lower() != state[1].lower():
        return result(True, "terminal", True)

    matches = _recognize(state)
    if not matches:
        return result(False, "not_recognized", False)

    for donor_index, a, b, k, n, relation, q in matches:
        pattern = {"donor_index": donor_index, "a": a, "b": b, "k": k, "N": n}
        try:
            if k == 1:
                # Here Q freely collapses to a^(-(N+1)) B and is already
                # primitive.  This branch is necessary when N<0 because the
                # cancelled terminal a-letter cannot be addressed by the
                # substitution codec.
                primitive = free_reduce(q)
                word = relation
                for _ in range(2):
                    position = next(
                        i for i, letter in enumerate(word) if letter.lower() == b.lower()
                    )
                    lhs = word[position]
                    rhs = _power(a, -(n + 1) if lhs == b else n + 1)
                    rewrite(word, primitive, lhs, rhs, position)
                    word = free_reduce(word[:position] + rhs + word[position + 1 :])
                generator = inv(a)
                if canon_rel(word) != canon_rel(generator):
                    raise AssertionError("k=1 elimination did not yield a generator")
                word = primitive
                while any(letter.lower() == a.lower() for letter in word):
                    position = next(
                        i for i, letter in enumerate(word) if letter.lower() == a.lower()
                    )
                    lhs = word[position]
                    rewrite(word, generator, lhs, "", position)
                    word = free_reduce(word[:position] + word[position + 1 :])
                solved = all(
                    len(final_word) == 1 for final_word in state
                ) and state[0].lower() != state[1].lower()
                if not solved:
                    raise AssertionError("completed k=1 rewrites are not terminal")
                return result(True, "collapsed", True)

            u = b * k + a + inv(b) * k
            relation_prime = inv(u) * 2 + a

            sign_n = 1 if n >= 0 else -1
            for j in range(abs(n)):
                prefix = u + b + _power(u, 2 * j * sign_n)
                remaining = n - j * sign_n
                word = free_reduce(prefix + _power(a, remaining))
                lhs = a if sign_n == 1 else inv(a)
                rhs = _power(u, 2 * sign_n)
                position = len(word) - abs(remaining)
                rewrite(word, relation_prime, lhs, rhs, position)

            m = 2 * n + 1
            primitive = b + _power(a, m)
            if canon_rel(primitive) not in state:
                raise AssertionError("power phase did not produce the primitive companion")

            word = cyc_reduce(relation)
            stable_rewrites = 0
            while any(letter.lower() == b.lower() for letter in word):
                if stable_rewrites >= 2 * k:
                    raise AssertionError("stable-letter elimination exceeded its proof bound")
                position = next((i for i, letter in enumerate(word) if letter.lower() == b.lower()), -1)
                if position < 0:
                    raise AssertionError("stable-letter elimination ended early")
                lhs = word[position]
                rhs = _power(a, -m if lhs == b else m)
                rewrite(word, primitive, lhs, rhs, position)
                word = word[:position] + rhs + word[position + 1 :]
                word = cyc_reduce(free_reduce(word))
                stable_rewrites += 1

            generator = inv(a)
            if canon_rel(word) != canon_rel(generator):
                raise AssertionError("stable-letter elimination did not yield a generator")

            word = primitive
            for _ in range(abs(m)):
                position = next((i for i, letter in enumerate(word) if letter.lower() == a.lower()), -1)
                if position < 0:
                    raise AssertionError("base-letter cleanup ended early")
                lhs = word[position]
                rewrite(word, generator, lhs, "", position)
                word = free_reduce(word[:position] + word[position + 1 :])
        except _Limit as exc:
            return result(False, str(exc), True)

        solved = all(len(word) == 1 for word in state) and state[0].lower() != state[1].lower()
        if not solved:
            raise AssertionError("completed Q_(k,N) rewrites are not terminal")
        return result(True, "collapsed", True)

    return result(False, "recognized_but_failed", True)
