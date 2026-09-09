"""One-splice sufficient family followed by consecutive-BS collapse."""
from __future__ import annotations

from functools import lru_cache

from experiments.equivalence_classes.lib.words import (
    canon_pair, canon_rel, cyc_reduce, free_reduce, inv, replay_move, rot,
)
from research.supermoves_20260908.consecutive_bs import collapse as consecutive_collapse


def _power(word, exponent):
    return word * exponent if exponent >= 0 else inv(word) * (-exponent)


@lru_cache(maxsize=16384)
def _donor_orientations(key, length):
    expected_runs = 2 if length == 3 else 6
    changes = 0
    for index, letter in enumerate(key):
        changes += letter != key[index - 1]
        if changes > expected_runs:
            return ()
    if changes != expected_runs:
        return ()
    if length == 3:
        hs = (0,)
    elif length < 5:
        return ()
    else:
        magnitude = length - 5
        hs = (0,) if magnitude == 0 else (magnitude, -magnitude)
    found = []
    for a in "xXyY":
        for b in "xXyY":
            if a.lower() == b.lower():
                continue
            for h in hs:
                donor = _power(inv(a), h) + inv(b) + inv(a) + b + inv(a) + b
                if canon_rel(donor) == key:
                    found.append((a, b, h, donor))
    return tuple(found)


def family_gate(pair):
    """Return every exact signed `(donor, companion, p, h, m)` match."""
    state = canon_pair(*pair)
    return canonical_family_gate(state)


def canonical_family_gate(state):
    """Inspect a canonical pair without repeating its canonicalization."""
    matches = []
    for donor_index, donor_key in enumerate(state):
        companion_key = state[1 - donor_index]
        for a, b, h, donor in _donor_orientations(donor_key, len(donor_key)):
            for p in range(1, len(companion_key) + 1):
                if h % p:
                    continue
                companion = (
                    inv(a) * (p + 2)
                    + b
                    + _power(inv(a), h - p)
                    + inv(b)
                    + inv(a)
                    + b
                )
                if canon_rel(companion) != companion_key:
                    continue
                match = dict(
                    donor_index=donor_index,
                    a=a,
                    b=b,
                    p=p,
                    h=h,
                    m=h // p,
                    donor=donor,
                    companion=companion,
                )
                signature = (donor_index, a, b, p, h)
                if all(
                    (item["donor_index"], item["a"], item["b"], item["p"], item["h"])
                    != signature
                    for item in matches
                ):
                    matches.append(match)
    return matches


def collapse(pair, budget=1000, intermediate_cap=256):
    """Collapse an exact member of the sufficient one-splice family.

    This emits only ordinary substitution-codec moves.  It is a bounded
    lookahead through moves already present in the ordinary AC graph.
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
    splice_rotation_checks = 0

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
            splice_rewrites=1 if steps else 0,
            splice_rotation_checks=splice_rotation_checks,
        )

    if intermediate_cap is not None and peak > intermediate_cap:
        return result(False, "input_cap", False)
    matches = canonical_family_gate(state)
    if not matches:
        return result(False, "not_recognized", False)
    match = matches[0]
    pattern = {key: match[key] for key in ("a", "b", "p", "h", "m", "donor_index")}
    if budget < 2:
        return result(False, "budget", True)

    a, b, h = match["a"], match["b"], match["h"]
    donor, companion = match["donor"], match["companion"]
    expected_donor = inv(a) * (match["p"] + 1) + b + a * match["p"] + inv(b)

    target_key, donor_key = canon_rel(companion), canon_rel(donor)
    targets = [i for i in (0, 1) if state[i] == target_key and state[1 - i] == donor_key]
    if not targets:
        raise AssertionError("recognized orientations differ from current state")
    target = targets[0]
    actual = state[target]
    canonical_new = canon_rel(expected_donor)
    expected_pair = canon_pair(donor, canonical_new)
    oriented_target = free_reduce(companion)
    if cyc_reduce(oriented_target) != oriented_target:
        raise AssertionError("family companion is not cyclically reduced")
    oriented_source = free_reduce(
        inv(b) + a + b + _power(a, h) + inv(b) + a
    )
    if canon_rel(oriented_source) != donor_key:
        raise AssertionError("proved source is not a donor orientation")

    splice = None
    for target_word, source_word in (
        (oriented_target, oriented_source),
        (inv(oriented_target), inv(oriented_source)),
    ):
        target_cut = None
        for cut in range(len(actual)):
            splice_rotation_checks += 1
            if rot(actual, cut) == target_word:
                target_cut = cut
                break
        if target_cut is None:
            continue
        source_match = None
        for sign in (1, -1):
            signed_source = state[1 - target] if sign == 1 else inv(state[1 - target])
            for cut in range(len(signed_source)):
                splice_rotation_checks += 1
                if rot(signed_source, cut) == source_word:
                    source_match = sign, cut
                    break
            if source_match is not None:
                break
        if source_match is None:
            raise AssertionError("stored donor has no proof-derived source rotation")
        sign, source_cut = source_match
        move = (target + 1, sign, target_cut, source_cut)
        child = replay_move(state, move)
        splice = move, child
        break
    if splice is None:
        raise AssertionError("stored target has no proof-derived family orientation")
    move, child = splice
    if child != expected_pair:
        raise AssertionError("proof-derived splice replay missed the consecutive endpoint")
    if intermediate_cap is not None and max(map(len, child)) > intermediate_cap:
        return result(False, "intermediate_cap", True)
    raw_peak = max(raw_peak, len(actual) + len(state[1 - target]))
    state = child
    states.append(list(state))
    steps.append({"kind": "substitution", "move": "_".join(map(str, move))})
    peak = max(peak, max(map(len, state)))

    suffix = consecutive_collapse(
        state,
        budget=budget - len(steps),
        intermediate_cap=intermediate_cap,
    )
    if not suffix["applicable"]:
        raise AssertionError("proved splice endpoint was not recognized by consecutive collapse")
    if tuple(suffix["states"][0]) != state:
        raise AssertionError("consecutive suffix root differs from splice endpoint")
    for suffix_child, suffix_step in zip(suffix["states"][1:], suffix["steps"]):
        state = tuple(suffix_child)
        states.append(list(state))
        steps.append(suffix_step)
    peak = max(peak, suffix["max_intermediate_relator_length"])
    raw_peak = max(raw_peak, suffix.get("max_raw_product_length", peak))
    return result(
        suffix["solved"],
        "splice_power_family" if suffix["solved"] else suffix["reason"],
        True,
    )
