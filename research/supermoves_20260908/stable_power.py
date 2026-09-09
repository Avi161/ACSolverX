"""Bounded stable-power pinches feeding the direct Q_(k,N) compiler."""
from __future__ import annotations

from functools import lru_cache

from experiments.equivalence_classes.lib.words import (
    canon_pair, canon_rel, cyc_reduce, free_reduce, inv, replay_move, rot,
)
from research.supermoves_20260908 import stable_power_Q


class _Limit(Exception):
    pass


@lru_cache(maxsize=16384)
def _orientations_for_key(key, length):
    if length < 5 or length % 2 != 1:
        return ()
    changes = 0
    for index, letter in enumerate(key):
        changes += letter != key[index - 1]
        if changes > 4:
            return ()
    if changes != 4:
        return ()
    k = (length - 3) // 2
    found = []
    for a in "xXyY":
        for b in "xXyY":
            if a.lower() == b.lower():
                continue
            relation = inv(a) * 2 + inv(b) * k + a + b * k
            if canon_rel(relation) == key:
                found.append((a, b, k, relation))
    return tuple(found)


def donor_gate(pair):
    """Return all signed stable-power donor orientations for a canonical pair."""
    state = canon_pair(*pair)
    return canonical_donor_gate(state)


def canonical_donor_gate(state):
    """Inspect already freely/cyclically reduced canonical relators."""
    matches = []
    for donor_index, word in enumerate(state):
        for a, b, k, relation in _orientations_for_key(word, len(word)):
            matches.append(
                dict(donor_index=donor_index, a=a, b=b, k=k, relation=relation)
            )
    return matches


def _pinches(word, a, b, k):
    candidates = []
    for inverse_flag, base in enumerate((word, inv(word))):
        doubled = base + base
        for cut in range(len(base)):
            oriented = doubled[cut : cut + len(base)]
            for direction in ("forward", "reverse"):
                left = inv(b) if direction == "forward" else b
                right = b if direction == "forward" else inv(b)
                if not oriented.startswith(left * k):
                    continue
                position = k
                if position >= len(oriented) or oriented[position].lower() != a.lower():
                    continue
                letter = oriented[position]
                end = position
                while end < len(oriented) and oriented[end] == letter:
                    end += 1
                run_length = end - position
                if oriented[end : end + k] != right * k:
                    continue
                if direction == "reverse" and run_length % 2:
                    continue
                r = run_length if letter == a else -run_length
                if direction == "reverse":
                    r //= 2
                tail = oriented[end + k :]
                endpoint = (
                    stable_power_Q._power(a, 2 * r) + tail
                    if direction == "forward"
                    else stable_power_Q._power(a, r) + tail
                )
                projected = len(cyc_reduce(free_reduce(endpoint)))
                candidates.append(
                    dict(
                        direction=direction,
                        inverse_flag=bool(inverse_flag),
                        cut=cut,
                        oriented=oriented,
                        r=r,
                        units=abs(r),
                        projected_length=projected,
                    )
                )
    candidates.sort(
        key=lambda item: (
            item["projected_length"],
            0 if item["direction"] == "reverse" else 1,
            item["inverse_flag"],
            item["cut"],
        )
    )
    return candidates


def collapse(
    pair,
    budget=1000,
    max_rewrites=16,
    intermediate_cap=256,
    max_matcher_tests=256,
):
    """Apply bounded certified pinches, then the direct general-Q collapse."""
    if isinstance(budget, bool) or not isinstance(budget, int) or not 1 <= budget <= 1000:
        raise ValueError("budget must be an integer in 1..1000")
    if (
        isinstance(max_rewrites, bool)
        or not isinstance(max_rewrites, int)
        or max_rewrites < 0
    ):
        raise ValueError("max_rewrites must be a nonnegative integer")
    if (
        isinstance(max_matcher_tests, bool)
        or not isinstance(max_matcher_tests, int)
        or max_matcher_tests < 0
    ):
        raise ValueError("max_matcher_tests must be a nonnegative integer")
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
    completed_pinches = 0
    ledger = []
    pattern = None
    matcher_candidate_tests = 0

    def result(solved, reason, applicable, q_match=False, partial=None):
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
            prepass_rewrites=sum(len(item["unit_moves"]) for item in ledger),
            completed_pinches=completed_pinches,
            partial_pinch=partial,
            Q_match_after_pinch=q_match,
            pinch_ledger=ledger,
            matcher_candidate_tests=matcher_candidate_tests,
            compute_units=len(steps) + 1 + matcher_candidate_tests,
        )

    def append_q(q_result):
        nonlocal state, peak, raw_peak
        if tuple(q_result["states"][0]) != state:
            raise AssertionError("direct Q suffix root differs from prepass endpoint")
        for child, step in zip(q_result["states"][1:], q_result["steps"]):
            state = tuple(child)
            states.append(list(state))
            steps.append(step)
        peak = max(peak, q_result["max_intermediate_relator_length"])
        raw_peak = max(raw_peak, q_result.get("max_raw_product_length", peak))

    def try_q(after_pinch):
        remaining = budget - (len(steps) + 1 + matcher_candidate_tests)
        q_result = stable_power_Q.collapse(
            state,
            budget=min(1000, remaining + 1),
            intermediate_cap=intermediate_cap,
        )
        if not q_result["applicable"]:
            return None
        append_q(q_result)
        return result(
            q_result["solved"],
            "stable_power_Q" if q_result["solved"] else q_result["reason"],
            True,
            q_match=after_pinch,
        )

    def rewrite(word, donor, lhs, rhs, position):
        nonlocal state, peak, raw_peak, matcher_candidate_tests
        if len(steps) + 1 + matcher_candidate_tests >= budget:
            raise _Limit("budget_mid_pinch")
        raw_desired = word[:position] + rhs + word[position + len(lhs) :]
        desired_word = cyc_reduce(free_reduce(raw_desired))
        desired_pair = canon_pair(desired_word, donor)
        if intermediate_cap is not None and max(map(len, desired_pair)) > intermediate_cap:
            raise _Limit("intermediate_cap")
        target_key, donor_key = canon_rel(word), canon_rel(donor)
        targets = [i for i in (0, 1) if state[i] == target_key and state[1 - i] == donor_key]
        if not targets:
            raise AssertionError("tracked pinch words differ from current state")
        target = targets[0]
        actual = state[target]
        reduced_word = cyc_reduce(free_reduce(word))
        if reduced_word == word:
            shift = (word + word).find(actual)
            local_lhs, local_rhs = lhs, rhs
            if 0 <= shift < len(word):
                start = (position - shift) % len(word)
            else:
                inverted = inv(word)
                shift = (inverted + inverted).find(actual)
                if not 0 <= shift < len(word):
                    raise AssertionError("cyclic pinch target has no rotation witness")
                start = (len(word) - position - len(lhs) - shift) % len(word)
                local_lhs, local_rhs = inv(lhs), inv(rhs)
            needed = free_reduce(inv(local_lhs) + local_rhs)
            donor_move = None
            for sign in (1, -1):
                oriented_donor = state[1 - target] if sign == 1 else inv(state[1 - target])
                for donor_cut in range(len(oriented_donor)):
                    if rot(oriented_donor, donor_cut) == needed:
                        donor_move = sign, donor_cut
                        break
                if donor_move is not None:
                    break
            if donor_move is None:
                raise AssertionError("cyclic pinch correction is not the donor")
            sign, donor_cut = donor_move
            move = (
                target + 1,
                sign,
                (-(start + len(local_lhs))) % len(actual),
                donor_cut,
            )
            child = replay_move(state, move)
            if child != desired_pair:
                raise AssertionError("algebraic pinch offset missed its proved endpoint")
        else:
            realized = None
            for target_cut in range(len(actual)):
                for sign in (1, -1):
                    oriented_donor = (
                        state[1 - target] if sign == 1 else inv(state[1 - target])
                    )
                    for donor_cut in range(len(oriented_donor)):
                        if matcher_candidate_tests >= max_matcher_tests:
                            raise _Limit("matcher_encoding_limit")
                        if len(steps) + 1 + matcher_candidate_tests >= budget:
                            raise _Limit("matcher_budget")
                        matcher_candidate_tests += 1
                        candidate_move = (target + 1, sign, target_cut, donor_cut)
                        candidate_child = replay_move(state, candidate_move)
                        if candidate_child == desired_pair:
                            realized = candidate_move, candidate_child
                            break
                    if realized is not None:
                        break
                if realized is not None:
                    break
            if realized is None:
                raise AssertionError(
                    "boundary-cancelled pinch has no single packed realization"
                )
            if len(steps) + 2 + matcher_candidate_tests > budget:
                raise _Limit("matcher_budget")
            move, child = realized
        state = child
        states.append(list(state))
        step = {"kind": "substitution", "move": "_".join(map(str, move))}
        steps.append(step)
        peak = max(peak, max(map(len, state)))
        raw_peak = max(raw_peak, len(raw_desired), len(actual) + len(state[1 - target]))
        # Keep the frozen raw stage for the next proof step. Canonical boundary
        # cancellation can make it neither a rotation nor an inverse of the
        # stored state, so the next packed move is resolved by its required
        # canonical endpoint rather than by reusing this raw offset in `state`.
        return step["move"], raw_desired

    if intermediate_cap is not None and peak > intermediate_cap:
        return result(False, "input_cap", False)
    direct = try_q(False)
    if direct is not None:
        return direct

    while True:
        orientations = canonical_donor_gate(state)
        if not orientations:
            return result(False, "donor_not_recognized", bool(steps))
        choices = []
        for orientation in orientations:
            companion = state[1 - orientation["donor_index"]]
            for candidate in _pinches(
                companion, orientation["a"], orientation["b"], orientation["k"]
            ):
                choices.append((candidate, orientation))
        if not choices:
            return result(False, "pinch_stalled", True)
        choices.sort(
            key=lambda item: (
                item[0]["projected_length"],
                0 if item[0]["direction"] == "reverse" else 1,
                item[0]["inverse_flag"],
                item[0]["cut"],
                item[1]["a"],
                item[1]["b"],
            )
        )
        candidate, orientation = choices[0]
        pattern = {
            "a": orientation["a"],
            "b": orientation["b"],
            "k": orientation["k"],
        }
        entry = {
            "direction": candidate["direction"],
            "r": candidate["r"],
            "cut": candidate["cut"],
            "inverse_flag": candidate["inverse_flag"],
            "unit_moves": [],
        }
        ledger.append(entry)
        allowed = min(max_rewrites - sum(len(item["unit_moves"]) for item in ledger), candidate["units"])
        if allowed <= 0:
            ledger.pop()
            return result(False, "prepass_limit", True)

        word = candidate["oriented"]
        a, b, k, relation = (
            orientation["a"],
            orientation["b"],
            orientation["k"],
            orientation["relation"],
        )
        epsilon = 1 if candidate["r"] > 0 else -1
        try:
            for unit in range(allowed):
                if candidate["direction"] == "forward":
                    position = 2 * unit
                    lhs = inv(b) * k + stable_power_Q._power(a, epsilon)
                    rhs = stable_power_Q._power(a, 2 * epsilon) + inv(b) * k
                else:
                    position = unit
                    lhs = b * k + stable_power_Q._power(a, 2 * epsilon)
                    rhs = stable_power_Q._power(a, epsilon) + b * k
                move, word = rewrite(word, relation, lhs, rhs, position)
                entry["unit_moves"].append(move)
        except _Limit as exc:
            return result(False, str(exc), True, partial=entry.copy())

        if allowed < candidate["units"]:
            return result(False, "prepass_limit_mid_pinch", True, partial=entry.copy())
        completed_pinches += 1
        q_result = try_q(True)
        if q_result is not None:
            return q_result
