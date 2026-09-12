"""Retain a two-sided stable spelling; enumerate exact finite power-cost balls."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import chain, product

import theory_corridor as corridor
import theory_flow_exact as exact
from theory_corridor import lemma11
from search import inverse, length, reduced


@dataclass
class Atom:
    donor: int
    helper: int
    stable: int
    left: int
    right: int
    replacement: tuple
    factors: list


def _ends(sign, bit, left, right):
    if not bit:
        return 0, 0
    return (left, right) if sign > 0 else (-right, -left)


def _adjust(signs, exponents, bits, left, right):
    ends = [_ends(s, b, left, right) for s, b in zip(signs, bits)]
    return [e - ends[i][1] - ends[(i + 1) % len(signs)][0]
            for i, e in enumerate(exponents)]


def _add(words, root, stable, left, right):
    helper = max(abs(x) for w in words for x in w) + 1
    defining = corridor.shortest_power(left, root) + (stable,) + corridor.shortest_power(right, root)
    raw = ((-helper,) + defining,) + words
    after, normalization = lemma11.normalize_witness(raw)
    positions = {row['input_index']: i for i, row in enumerate(normalization)}
    donor = positions[0]
    witness = normalization[donor]
    sign, c = witness['sign'], tuple(witness['conjugator'])
    factors = [{'donor_index': donor, 'sign': sign, 'conjugator': inverse(c)}]
    if corridor.evaluate(after, factors) != raw[0]:
        raise AssertionError('stable-spelling definition isolation failed')
    atom = Atom(donor, helper, stable, left, right, defining, factors)
    event = {'kind': 'defining_compression', 'before': words, 'defining': defining,
             'helper': helper, 'cuts': [0] * len(words), 'templates': words,
             'raw_after': raw, 'after': after, 'uses': 0, 'literal_length': length(raw),
             'final_length': length(after), 'normalization': normalization}
    return after, atom, positions, event


def _expand(word, atom):
    current, factors = reduced(word), []
    while any(abs(x) == atom.helper for x in current):
        i = next(i for i, x in enumerate(current) if abs(x) == atom.helper)
        letter, suffix = current[i], current[i + 1:]
        correction = atom.factors if letter > 0 else corridor.conjugate_factors(
            corridor.invert_factors(atom.factors), (-atom.helper,))
        factors.extend(corridor.conjugate_factors(correction, suffix))
        replacement = atom.replacement if letter > 0 else inverse(atom.replacement)
        current = reduced(current[:i] + replacement + suffix)
    return current, factors


def _best_bits(signs, exponents, root, atom):
    best = None
    for first in (0, 1):
        states = {first: (0, (first,))}
        for i in range(len(signs) - 1):
            following = {}
            for previous, (cost, path) in states.items():
                suffix = _ends(signs[i], previous, atom.left, atom.right)[1]
                for bit in (0, 1):
                    prefix = _ends(signs[i + 1], bit, atom.left, atom.right)[0]
                    option = cost + len(corridor.shortest_power(exponents[i] - suffix - prefix, root)), path + (bit,)
                    if bit not in following or option < following[bit]:
                        following[bit] = option
            states = following
        for previous, (cost, path) in states.items():
            suffix = _ends(signs[-1], previous, atom.left, atom.right)[1]
            prefix = _ends(signs[0], first, atom.left, atom.right)[0]
            option = cost + len(corridor.shortest_power(exponents[-1] - suffix - prefix, root)), path
            if best is None or option < best:
                best = option
    return best


def _pack(words, target, root, atom):
    expanded, factors = _expand(words[target], atom)
    expanded, more = corridor.expand_helper(expanded, root)
    factors += more
    core, witness = lemma11.canonical_witness(expanded)
    signs, exponents, frame = corridor._cyclic_corridor(core, root, atom.stable)
    cost, bits = _best_bits(signs, exponents, root, atom)
    gaps = _adjust(signs, exponents, bits, atom.left, atom.right)
    packed = tuple(x for s, b, e in zip(signs, bits, gaps) for x in
                   (((atom.helper if s > 0 else -atom.helper) if b else s,) +
                    corridor.shortest_power(e, root)))
    prefix = _ends(signs[0], bits[0], atom.left, atom.right)[0]
    frame = reduced(frame + corridor.power(root.base, -prefix))
    packed_core = reduced(frame + packed + inverse(frame))
    c, sign = tuple(witness['conjugator']), witness['sign']
    raw = reduced(c + (packed_core if sign > 0 else inverse(packed_core)) + inverse(c))
    unpacked, unpack = _expand(raw, atom)
    unpacked, more = corridor.expand_helper(unpacked, root)
    unpack += more
    if unpacked != expanded:
        raise AssertionError('retained stable spelling changes expanded target')
    return corridor._event(words, target, raw, factors + corridor.invert_factors(unpack),
        {'macro': 'retained_stable_spelling', 'atom_left': atom.left,
         'atom_right': atom.right, 'atom_bits': bits, 'power_cost': cost})


def compile_metric(words, root, model, target, choices, left, right):
    current, event = corridor.compile_flow(words, target, root, model, choices)
    events = [event]
    root, model, target = exact._remap(root, model, target, event)
    current, atom, positions, event = _add(current, root, model['stable'], left, right)
    events.append(event)
    root = corridor.Root(positions[root.donor + 1], root.helper, root.base, root.exponent,
                        [dict(f, donor_index=positions[f['donor_index'] + 1]) for f in root.factors])
    pending = [positions[model['donor'] + 1], positions[target + 1]]
    while pending:
        selected = pending.pop(0)
        current, event = _pack(current, selected, root, atom)
        events.append(event)
        positions = {row['input_index']: i for i, row in enumerate(event['normalization'])}
        pending = [positions[i] for i in pending]
        root = corridor.Root(positions[root.donor], root.helper, root.base, root.exponent,
                            [dict(f, donor_index=positions[f['donor_index']]) for f in root.factors])
        atom = Atom(positions[atom.donor], atom.helper, atom.stable, atom.left, atom.right,
                    atom.replacement, [dict(f, donor_index=positions[f['donor_index']]) for f in atom.factors])
    return current, events


def _coin_ball(root, ceiling, available):
    values, used = {}, 0
    for a in range(-ceiling, ceiling + 1):
        for b in range(-(ceiling - abs(a)), ceiling - abs(a) + 1):
            if used == available:
                return values, used, False
            used += 1
            exponent, cost = a + root.exponent * b, abs(a) + abs(b)
            values[exponent] = min(cost, values.get(exponent, cost))
    return values, used, True


def _parameters(root, model, values, ceiling):
    k, m, n = abs(root.exponent), model['m'], model['n']
    lefts = [-k, -(m - k), -(m - 1), -m, -(m + 1), -(m // 2), -1]
    rights = [n - 1, k, n - k, n, n + 1, n // 2, 1]
    priority = [(p, q) for p in lefts for q in rights]
    priority.extend((-p, -q) for p, q in tuple(priority))
    buckets = {cost: sorted(e for e, c in values.items() if c == cost)
               for cost in range(ceiling + 1)}
    complete = ((p, q) for cost in range(ceiling + 1)
                for first in range(cost + 1) for p in buckets[first]
                for q in buckets[cost - first])
    seen = set()
    for pair in chain(priority, complete):
        if pair != (0, 0) and all(e in values for e in pair) and \
                sum(values[e] for e in pair) <= ceiling and pair not in seen:
            seen.add(pair)
            yield pair


def probe(words, remaining, *, audits=None):
    """Charge BS models, pinches, signed atoms, bit patterns, flows and compilation."""
    if type(remaining) is not int or not 0 <= remaining <= 1000:
        raise ValueError('remaining must be an integer in 0..1000')
    before = tuple(tuple(w) for w in words)
    current, normalization = lemma11.normalize_witness(before)
    if len(current) != 3:
        return [], 0
    prefix = [] if before == current else [{'kind': 'relator_normalization',
        'before': before, 'after': current, 'normalization': normalization}]
    candidates, used = [], 0
    for root in corridor.roots(current):
        for donor in range(3):
            if donor == root.donor:
                continue
            if used == remaining:
                return candidates, used
            used += 1
            model = corridor.bs_model(current, root, donor)
            if model is None:
                continue
            target = next(i for i in range(3) if i not in (root.donor, donor))
            expanded, _ = corridor.expand_helper(current[target], root)
            data = corridor._cyclic_corridor(expanded, root, model['stable'])
            if data is None:
                continue
            signs, exponents, _ = data
            pinch = False
            for i, sign in enumerate(signs):
                if used == remaining:
                    return candidates, used
                used += 1
                divisor = model['n'] if sign > 0 else model['m']
                pinch |= signs[(i + 1) % len(signs)] == -sign and exponents[i] % divisor == 0
            if pinch:
                if audits is not None:
                    audits.append({'reason': 'requires_cyclic_britton_prefix'})
                continue
            max_cost = length(current) - abs(root.exponent) - len(signs) - 6
            if max_cost < 0:
                continue
            values, cost, complete = _coin_ball(root, max_cost, remaining - used)
            used += cost
            if not complete:
                return candidates, used
            if audits is not None:
                audits.append({'phase': 'exact_parameter_cost_ball', 'root_donor': root.donor,
                    'bs_donor': donor, 'max_power_cost': max_cost, 'coefficient_units': cost,
                    'exact_power_costs': sorted(values.items()), 'parameter_family_complete': False,
                    'all_tested_flows_complete': True})
                parameter_audit = audits[-1]
            else:
                parameter_audit = None
            for left, right in _parameters(root, model, values, max_cost):
                if used == remaining:
                    return candidates, used
                used += 1
                power_cost = values[left] + values[right]
                atom = Atom(-1, -1, model['stable'], left, right, (), [])
                donor_signs = [-model['stable'], model['stable']]
                donor_cost = 2 + _best_bits(donor_signs, [model['m'], -model['n']], root, atom)[0]
                definition_cost = 2 + power_cost
                ceiling = length(current) - 1 - (abs(root.exponent) + 1) - definition_cost - donor_cost - len(signs)
                if ceiling < 0:
                    continue
                if ceiling == 0 and any(signs[(i + 1) % len(signs)] == -s and
                        exponents[i] % (model['n'] if s > 0 else model['m']) not in
                        {value % (model['n'] if s > 0 else model['m']) for value in
                         ((right, -right) if s > 0 else (left, -left))}
                        for i, s in enumerate(signs)):
                    continue
                for bits in product((0, 1), repeat=len(signs)):
                    if used == remaining:
                        return candidates, used
                    used += 1
                    adjusted = _adjust(signs, exponents, bits, left, right)
                    if ceiling == 0 and any(signs[(i + 1) % len(signs)] == -s and
                            adjusted[i] % (model['n'] if s > 0 else model['m'])
                            for i, s in enumerate(signs)):
                        continue
                    if used == remaining:
                        return candidates, used
                    if ceiling == 0:
                        used += 1
                        matrix = exact.inverse_flow_matrix(signs, model)
                        rational = None if matrix is None else [-sum(h * e for h, e in zip(row, adjusted)) for row in matrix]
                        choices = None if rational is None or any(q.denominator != 1 for q in rational) else tuple(int(q) for q in rational)
                        complete, cost = matrix is not None, 1
                        audit = {'cost_ceiling': 0, 'reason': 'unique_rational_flow_solution',
                                 'rational_flow': None if rational is None else [str(q) for q in rational]}
                    else:
                        choices, cost, complete, audit = exact.exact_flow(signs, adjusted, root,
                            model, ceiling, max(0, remaining - used - 1))
                        used += cost
                    if audits is not None:
                        if not complete:
                            parameter_audit['all_tested_flows_complete'] = False
                        audits.append({'root_donor': root.donor, 'bs_donor': donor,
                            'atom_left': left, 'atom_right': right, 'atom_bits': bits,
                            'flow_complete': complete, 'found_flow': choices, 'flow_units': cost, **audit})
                    if choices is None:
                        continue
                    if used == remaining:
                        return candidates, used
                    used += 1
                    after, events = compile_metric(current, root, model, target, choices, left, right)
                    if length(after) >= length(current):
                        raise AssertionError('predicted stable-spelling gain did not materialize')
                    events[-1].update({'stable_atom_flow_audit': audit, 'stable_atom_flow_complete': complete})
                    candidates.append((after, prefix + events))
            if parameter_audit is not None:
                parameter_audit['parameter_pairs_enumerated'] = True
                parameter_audit['parameter_family_complete'] = parameter_audit['all_tested_flows_complete']
    candidates.sort(key=lambda item: (length(item[0]), item[0]))
    return candidates, used
