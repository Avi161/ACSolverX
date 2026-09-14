"""Cyclic Britton reduction and cost-bounded complete BS corridor flows."""
from __future__ import annotations

from fractions import Fraction

import theory_corridor as corridor
from theory_corridor import lemma11
from search import length


def inverse_flow_matrix(signs, model):
    count = len(signs)
    a = [model['m'] if s > 0 else model['n'] for s in signs]
    b = [model['n'] if s > 0 else model['m'] for s in signs]
    rows = []
    for start in range(count):
        weight, coefficients = Fraction(1), [Fraction(0) for _ in signs]
        for step in range(count - 1, -1, -1):
            i = (start + step) % count
            following = (i + 1) % count
            coefficients[i] = weight / a[following]
            weight *= Fraction(b[i], a[following])
        if weight == 1:
            return None
        rows.append([value / (1 - weight) for value in coefficients])
    for i, row in enumerate(rows):
        for j in range(count):
            value = -b[j] * row[j] + a[j] * row[(j - 1) % count]
            if value != int(i == j):
                raise AssertionError('rational height-walk inverse does not replay')
    return rows


def flow_bounds(signs, exponents, root, model, cost_ceiling):
    inverse = inverse_flow_matrix(signs, model)
    if inverse is None:
        return None
    bounds = []
    for row in inverse:
        constant = abs(sum(value * e for value, e in zip(row, exponents)))
        bound = constant + max(1, abs(root.exponent)) * cost_ceiling * max(map(abs, row))
        bounds.append(bound.numerator // bound.denominator)
    return bounds


def _centered(bound):
    yield 0
    for value in range(1, bound + 1):
        yield -value
        yield value


def exact_flow(signs, exponents, root, model, cost_ceiling, available):
    """Find the least root cost below the ceiling, with explicit completeness."""
    bounds = flow_bounds(signs, exponents, root, model, cost_ceiling)
    if bounds is None:
        return None, 0, False, {'reason': 'singular_flow_matrix'}
    k = max(1, abs(root.exponent))
    values = sorted(((e, len(corridor.shortest_power(e, root)))
                     for e in range(-k * cost_ceiling, k * cost_ceiling + 1)),
                    key=lambda pair: (pair[1], abs(pair[0]), pair[0]))
    values = [(e, cost) for e, cost in values if cost <= cost_ceiling]
    allowed = {ceiling: [(e, cost) for e, cost in values if cost <= ceiling]
               for ceiling in range(cost_ceiling + 1)}
    a = [model['m'] if s > 0 else model['n'] for s in signs]
    b = [model['n'] if s > 0 else model['m'] for s in signs]
    count, charged, best = len(signs), 0, None
    metadata = {'cost_ceiling': cost_ceiling, 'mathematically_sufficient_flow_bounds': bounds,
                'finite_box_reason': 'exact_rational_height_walk_and_total_root_cost'}
    for first in _centered(bounds[0]):
        states = {first: (0, (first,))}
        for i in range(count - 1):
            following = {}
            for previous, (cost, path) in states.items():
                for exponent, added in allowed[cost_ceiling - cost]:
                    if charged == available:
                        return None if best is None else best[-1], charged, False, metadata
                    charged += 1
                    numerator = exponent - exponents[i] + b[i] * previous
                    if numerator % a[i + 1]:
                        continue
                    q = numerator // a[i + 1]
                    if abs(q) > bounds[i + 1]:
                        continue
                    option = (cost + added, path + (q,))
                    if q not in following or (option[0], sum(map(abs, option[1])), option[1]) < (
                            following[q][0], sum(map(abs, following[q][1])), following[q][1]):
                        following[q] = option
            states = following
            if not states:
                break
        for last, (cost, path) in states.items():
            if charged == available:
                return None if best is None else best[-1], charged, False, metadata
            charged += 1
            exponent = exponents[-1] - b[-1] * last + a[0] * first
            option = (cost + len(corridor.shortest_power(exponent, root)), sum(map(abs, path)), path)
            if option[0] <= cost_ceiling and (best is None or option < best):
                best = option
    return None if best is None else best[-1], charged, True, metadata


def _remap(root, model, target, event):
    positions = {row['input_index']: i for i, row in enumerate(event['normalization'])}

    def factors(items):
        return [dict(f, donor_index=positions[f['donor_index']]) for f in items]

    root = corridor.Root(positions[root.donor], root.helper, root.base, root.exponent, factors(root.factors))
    model = dict(model, donor=positions[model['donor']], factors=factors(model['factors']))
    return root, model, positions[target]


def pinch_prefix(words, root, model, target, available):
    current, events, charged = words, [], 0
    while True:
        expanded, _ = corridor.expand_helper(current[target], root)
        data = corridor._cyclic_corridor(expanded, root, model['stable'])
        if data is None:
            return current, root, model, target, events, charged, True
        signs, exponents, _ = data
        selected = None
        for i, (sign, exponent) in enumerate(zip(signs, exponents)):
            if charged == available:
                return current, root, model, target, events, charged, False
            charged += 1
            divisor = model['n'] if sign > 0 else model['m']
            if signs[(i + 1) % len(signs)] == -sign and exponent % divisor == 0:
                selected = i, exponent // divisor
                break
        if selected is None:
            return current, root, model, target, events, charged, True
        choices = [0] * len(signs)
        choices[selected[0]] = selected[1]
        after, event = corridor.compile_flow(current, target, root, model, choices)
        event.update({'phase': 'complete_cyclic_britton_prefix', 'pinch_index': selected[0],
                      'pinch_exponent': exponents[selected[0]], 'pinch_flow': selected[1]})
        root, model, target = _remap(root, model, target, event)
        new_expanded, _ = corridor.expand_helper(after[target], root)
        if sum(abs(x) == model['stable'] for x in new_expanded) >= len(signs):
            raise AssertionError('certified Britton pinch did not remove stable letters')
        current = after
        events.append(event)


def probe(words, remaining, *, audits=None):
    """Return ``(candidates, charged)``; completeness is per returned flow audit.

    One unit per donor-model attempt, relative collection, tested cyclic pinch,
    and sparse DP transition. Partial computations are retained only when they
    have already produced an independently replayable candidate. Every failed
    branch still consumes its work; no rank/length ceiling is imposed.
    """
    if type(remaining) is not int or not 0 <= remaining <= 1000:
        raise ValueError('remaining must be an integer in 0..1000')
    before = tuple(tuple(w) for w in words)
    current, witnesses = lemma11.normalize_witness(before)
    prefix = [] if before == current else [{'kind': 'relator_normalization',
        'before': before, 'after': current, 'normalization': witnesses}]
    candidates, charged = [], 0
    for root in corridor.roots(current):
        for target in range(len(current)):
            if target == root.donor:
                continue
            if charged == remaining:
                return candidates, charged
            charged += 1
            after, event = corridor.collect_root(current, target, root)
            if after != current:
                candidates.append((after, prefix + [event]))
        for donor in range(len(current)):
            if donor == root.donor:
                continue
            if charged == remaining:
                return candidates, charged
            charged += 1
            model = corridor.bs_model(current, root, donor)
            if model is None:
                continue
            for target in range(len(current)):
                if target in (root.donor, donor):
                    continue
                outcome = pinch_prefix(current, root, model, target, remaining - charged)
                after, new_root, new_model, new_target, events, cost, britton_complete = outcome
                charged += cost
                if events:
                    candidates.append((after, prefix + events))
                if not britton_complete:
                    if audits is not None:
                        audits.append({'root_donor': root.donor, 'bs_donor': donor,
                                       'target': target, 'reason': 'incomplete_britton_prefix'})
                    continue
                expanded, _ = corridor.expand_helper(after[new_target], new_root)
                data = corridor._cyclic_corridor(expanded, new_root, new_model['stable'])
                if data is None:
                    continue
                signs, exponents, _ = data
                ceiling = sum(len(corridor.shortest_power(e, new_root)) for e in exponents) - 1
                if ceiling < 0:
                    continue
                choices, cost, complete, metadata = exact_flow(signs, exponents, new_root,
                    new_model, ceiling, remaining - charged)
                charged += cost
                if audits is not None:
                    audits.append({'root_donor': root.donor, 'bs_donor': donor, 'target': target,
                                   'bs_m': new_model['m'], 'bs_n': new_model['n'],
                                   'stable_letters': signs, 'initial_exponents': exponents,
                                   'britton_prefix_events': len(events), 'flow_units': cost,
                                   'flow_complete': complete, 'found_flow': choices, **metadata})
                if choices is not None:
                    final, event = corridor.compile_flow(after, new_target, new_root, new_model, choices)
                    if length(final) >= length(after):
                        raise AssertionError('a strict root-cost flow failed to shorten the tuple')
                    event.update({'phase': 'cost_bounded_complete_corridor', 'flow_audit': metadata,
                                  'complete_flow_search': complete, 'cyclically_britton_reduced': True})
                    candidates.append((final, prefix + events + [event]))
    candidates.sort(key=lambda item: (length(item[0]), item[0]))
    return candidates, charged
