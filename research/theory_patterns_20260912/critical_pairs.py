"""Bounded one-donor overlap completion with free-group proof ledgers.

This is a sufficient rewrite engine, not a decision procedure for AC triviality.
Each equation carries lhs^-1 rhs as conjugated copies of the retained donor.
"""

from __future__ import annotations

from dataclasses import dataclass
from time import process_time

from .ac_words import (
    Factor, Trace, canon, conjugate_factors, expand_factors, inv,
    inverse_factors, red, replay, simplify_factors,
)


def order(word):
    return len(word), word


@dataclass(frozen=True)
class Rule:
    lhs: str
    rhs: str
    factors: tuple[Factor, ...]
    depth: int = 0


def orient(lhs, rhs, factors, depth=0):
    lhs, rhs = red(lhs), red(rhs)
    if lhs == rhs:
        return None
    prefix = 0
    while prefix < min(len(lhs), len(rhs)) and lhs[prefix] == rhs[prefix]:
        prefix += 1
    lhs, rhs = lhs[prefix:], rhs[prefix:]
    suffix = 0
    while suffix < min(len(lhs), len(rhs)) and lhs[-1 - suffix] == rhs[-1 - suffix]:
        suffix += 1
    if suffix:
        factors = conjugate_factors(factors, inv(lhs[-suffix:]))
        lhs, rhs = lhs[:-suffix], rhs[:-suffix]
    if order(lhs) < order(rhs):
        lhs, rhs = rhs, lhs
        factors = inverse_factors(factors)
    return Rule(lhs, rhs, simplify_factors(factors), depth)


def verify_rule(donor, rule):
    if not rule.lhs or order(rule.lhs) <= order(rule.rhs):
        raise ValueError("rule must strictly decrease shortlex order")
    if red(inv(rule.lhs) + rule.rhs) != expand_factors(donor, rule.factors):
        raise ValueError("invalid free-group rule proof")


def seed_rules(donor):
    found = {}
    n = len(donor)
    for sign in (1, -1):
        signed = donor if sign == 1 else inv(donor)
        for k in range(n):
            rotated = signed[k:] + signed[:k]
            for length in {n // 2, (n + 1) // 2, n}:
                rule = orient(inv(rotated[:length]), rotated[length:], (Factor(sign, signed[:k]),))
                if rule is not None:
                    verify_rule(donor, rule)
                    key = rule.lhs, rule.rhs
                    if key not in found or len(rule.factors) < len(found[key].factors):
                        found[key] = rule
    return sorted(found.values(), key=lambda r: (order(r.lhs), order(r.rhs)))


def normalize(word, rules, *, max_steps=256, max_factors=512):
    word = red(word)
    ledger = ()
    steps = 0
    while steps < max_steps:
        chosen = None
        for rule in rules:
            position = word.find(rule.lhs)
            if position >= 0:
                candidate = red(word[:position] + rule.rhs + word[position + len(rule.lhs):])
                if order(candidate) < order(word):
                    choice = (order(candidate), position, rule)
                    if chosen is None or choice[:2] < chosen[:2]:
                        chosen = choice
        if chosen is None:
            return word, ledger, steps, "normal"
        _, position, rule = chosen
        suffix = word[position + len(rule.lhs):]
        updated = simplify_factors(ledger + conjugate_factors(rule.factors, suffix))
        if len(updated) > max_factors:
            return word, ledger, steps, "factor_cap"
        word = red(word[:position] + rule.rhs + suffix)
        ledger = updated
        steps += 1
    return word, ledger, steps, "step_cap"


def critical_word(first, second, offset):
    overlap = min(len(first.lhs) - offset, len(second.lhs))
    if overlap <= 0 or first.lhs[offset:offset + overlap] != second.lhs[:overlap]:
        return None
    word = first.lhs + second.lhs[overlap:]
    if offset + len(second.lhs) < len(first.lhs):
        word = first.lhs
    u = red(first.rhs + word[len(first.lhs):])
    v = red(word[:offset] + second.rhs + word[offset + len(second.lhs):])
    a = conjugate_factors(first.factors, word[len(first.lhs):])
    b = conjugate_factors(second.factors, word[offset + len(second.lhs):])
    return word, u, v, a, b


def complete(donor, *, max_critical=500, max_rules=160, max_factors=24,
             max_word=64, cpu_seconds=1.0):
    donor = red(donor)
    rules = seed_rules(donor)
    initial_count = len(rules)
    seen = {(r.lhs, r.rhs) for r in rules}
    examined = matches = derived = reductions = 0
    started = process_time()
    reason = "exhausted"
    i = 0
    stop = False
    while i < len(rules) and not stop:
        j = 0
        while j <= i and not stop:
            orientations = [(rules[i], rules[j])]
            if i != j:
                orientations.append((rules[j], rules[i]))
            for first, second in orientations:
                for offset in range(len(first.lhs)):
                    if matches >= max_critical or len(rules) >= max_rules or process_time() - started >= cpu_seconds:
                        reason = ("critical_cap" if matches >= max_critical else
                                  "rule_cap" if len(rules) >= max_rules else "cpu_cap")
                        stop = True
                        break
                    examined += 1
                    critical = critical_word(first, second, offset)
                    if critical is None:
                        continue
                    _, u, v, a, b = critical
                    if u == v:
                        continue
                    matches += 1
                    U, c, su, _ = normalize(u, rules, max_factors=max_factors)
                    V, d, sv, _ = normalize(v, rules, max_factors=max_factors)
                    reductions += su + sv
                    ledger = inverse_factors(c) + inverse_factors(a) + b + d
                    rule = orient(U, V, ledger, max(first.depth, second.depth) + 1)
                    if rule is None or (rule.lhs, rule.rhs) in seen:
                        continue
                    if len(rule.lhs) > max_word or len(rule.factors) > max_factors:
                        continue
                    verify_rule(donor, rule)
                    rules.append(rule)
                    seen.add((rule.lhs, rule.rhs))
                    derived += 1
                if stop:
                    break
            j += 1
        i += 1
    return rules, {"initial_rules": initial_count, "derived_rules": derived,
                   "overlap_positions_checked": examined, "critical_pairs": matches,
                   "normalization_steps": reductions, "stop_reason": reason,
                   "cpu_seconds": process_time() - started}


def reduce_pair(pair, donor_index, rules, *, max_steps=256, max_factors=512):
    target = 1 - donor_index
    trace = Trace(pair)
    source = trace.pair[donor_index]
    trace.canonicalize(target)
    initial = trace.pair[target]
    result, factors, steps, reason = normalize(initial, rules, max_steps=max_steps, max_factors=max_factors)
    if red(inv(initial) + result) != expand_factors(source, factors):
        raise ValueError("invalid normalized-companion proof")
    trace.append_factors(target, factors)
    if trace.pair[target] != result:
        raise ValueError("emitted path differs from symbolic result")
    trace.canonicalize(target)
    if replay(pair, trace.moves) != trace.pair:
        raise ValueError("independent elementary replay failed")
    return {"pair": trace.pair, "moves": trace.moves, "normalization_steps": steps,
            "stop_reason": reason, "elementary_verified": True,
            "initial_total_length": sum(map(len, pair)),
            "total_length": sum(map(len, trace.pair)),
            "strict_reduction": sum(map(len, trace.pair)) < sum(map(len, pair)),
            "canonical_target": canon(trace.pair[target])}
