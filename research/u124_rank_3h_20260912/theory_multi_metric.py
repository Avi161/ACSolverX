"""Certified triangular two-power metrics for rank-three BS corridors."""
from __future__ import annotations

import theory_corridor as corridor
import theory_flow_exact as exact
import theory_root_metric as single
from theory_corridor import lemma11
from search import inverse, length, reduced


class Metric:
    def __init__(self, base, lower, upper, small, large):
        self.base, self.lower, self.upper = base, lower, upper
        self.small, self.large = small, large
        self.root = corridor.Root(-1, lower, base, small, [])
        self.cache = {}

    def spell(self, exponent):
        if exponent in self.cache:
            return self.cache[exponent]
        incumbent = corridor.shortest_power(exponent, self.root)
        for count in range(-len(incumbent), len(incumbent) + 1):
            tail = corridor.power(self.upper, count)
            rest = corridor.shortest_power(exponent - self.large * count, self.root)
            for word in (rest + tail, tail + rest):
                if (len(word), word) < (len(incumbent), incumbent):
                    incumbent = word
        self.cache[exponent] = incumbent
        return incumbent


def _flow(signs, exponents, metric, model, ceiling, available):
    bounding_root = corridor.Root(-1, metric.upper, metric.base, metric.large, [])
    bounds = exact.flow_bounds(signs, exponents, bounding_root, model, ceiling)
    if bounds is None:
        return None, 0, False, {'reason': 'singular_flow_matrix'}
    values = [(e, len(metric.spell(e))) for e in range(-metric.large * ceiling,
                                                    metric.large * ceiling + 1)]
    values.sort(key=lambda pair: (pair[1], abs(pair[0]), pair[0]))
    allowed = {c: [(e, cost) for e, cost in values if cost <= c] for c in range(ceiling + 1)}
    a = [model['m'] if s > 0 else model['n'] for s in signs]
    b = [model['n'] if s > 0 else model['m'] for s in signs]
    used, best = 0, None
    audit = {'cost_ceiling': ceiling, 'mathematically_sufficient_flow_bounds': bounds,
             'denominations': [1, metric.small, metric.large]}
    for first in exact._centered(bounds[0]):
        states = {first: (0, (first,))}
        for i in range(len(signs) - 1):
            following = {}
            for previous, (cost, path) in states.items():
                for exponent, added in allowed[ceiling - cost]:
                    if used == available:
                        return None if best is None else best[-1], used, False, audit
                    used += 1
                    numerator = exponent - exponents[i] + b[i] * previous
                    if numerator % a[i + 1]:
                        continue
                    q = numerator // a[i + 1]
                    if abs(q) > bounds[i + 1]:
                        continue
                    option = cost + added, path + (q,)
                    key = lambda item: (item[0], sum(map(abs, item[1])), item[1])
                    if q not in following or key(option) < key(following[q]):
                        following[q] = option
            states = following
            if not states:
                break
        for last, (cost, path) in states.items():
            if used == available:
                return None if best is None else best[-1], used, False, audit
            used += 1
            exponent = exponents[-1] - b[-1] * last + a[0] * first
            option = cost + len(metric.spell(exponent)), sum(map(abs, path)), path
            if option[0] <= ceiling and (best is None or option < best):
                best = option
    return None if best is None else best[-1], used, True, audit


def _add(words, base, exponent):
    helper = max(abs(x) for w in words for x in w) + 1
    defining = corridor.power(base, exponent)
    raw = ((-helper,) + defining,) + words
    after, normalization = lemma11.normalize_witness(raw)
    positions = {row['input_index']: i for i, row in enumerate(normalization)}
    event = {'kind': 'defining_compression', 'before': words, 'defining': defining,
             'helper': helper, 'cuts': [0] * len(words), 'templates': words,
             'raw_after': raw, 'after': after, 'uses': 0, 'literal_length': length(raw),
             'final_length': length(after), 'normalization': normalization}
    root = next(r for r in corridor.roots(after) if r.helper == helper and
                r.donor == positions[0] and r.base == base and r.exponent == exponent)
    return after, root, positions, event


def _upper_root(words, donor, helper, lower):
    expanded, factors = corridor.expand_helper(words[donor], lower)
    root = next(r for r in corridor.roots((expanded,)) if r.helper == helper)
    expression = [{'donor_index': donor, 'sign': 1, 'conjugator': ()}] + factors
    isolation = root.factors[0]
    if isolation['sign'] < 0:
        expression = corridor.invert_factors(expression)
    expression = corridor.conjugate_factors(expression, isolation['conjugator'])
    root = corridor.Root(donor, helper, root.base, root.exponent, expression)
    if corridor.evaluate(words, expression) != (-helper,) + corridor.power(root.base, root.exponent):
        raise AssertionError('triangular upper power identity failed')
    return root


def _pack(words, target, lower, upper, metric):
    expanded, factors = corridor.expand_helper(words[target], upper)
    expanded, more = corridor.expand_helper(expanded, lower)
    factors += more
    core, witness = lemma11.canonical_witness(expanded)
    packed, i = (), 0
    while i < len(core):
        if abs(core[i]) != metric.base:
            packed += core[i:i + 1]
            i += 1
            continue
        j, exponent = i, 0
        while j < len(core) and abs(core[j]) == metric.base:
            exponent += 1 if core[j] > 0 else -1
            j += 1
        packed += metric.spell(exponent)
        i = j
    c, sign = witness['conjugator'], witness['sign']
    raw = reduced(c + (packed if sign > 0 else inverse(packed)) + inverse(c))
    unpacked, unpack = corridor.expand_helper(raw, upper)
    unpacked, more = corridor.expand_helper(unpacked, lower)
    unpack += more
    if unpacked != expanded:
        raise AssertionError('two-power metric changes expanded word')
    return corridor._event(words, target, raw, factors + corridor.invert_factors(unpack),
                          {'macro': 'triangular_two_power_repacking',
                           'denominations': [1, metric.small, metric.large]})


def compile_metric(words, root, model, target, choices, small, large):
    current, event = corridor.compile_flow(words, target, root, model, choices)
    events = [event]
    root, model, target = exact._remap(root, model, target, event)
    current, root, event = single._shear(current, root, large)
    events.append(event)
    positions = {row['input_index']: i for i, row in enumerate(event['normalization'])}
    donor, target = positions[model['donor']], positions[target]
    current, lower, positions, event = _add(current, root.base, small)
    events.append(event)
    upper_donor = positions[root.donor + 1]
    pending = [positions[donor + 1], positions[target + 1]]
    current, event = corridor.collect_root(current, upper_donor, lower)
    events.append(event)
    positions = {row['input_index']: i for i, row in enumerate(event['normalization'])}
    pending = [positions[i] for i in pending]
    lower = next(r for r in corridor.roots(current) if r.helper == lower.helper and
                 r.donor == positions[lower.donor] and r.base == root.base)
    upper = _upper_root(current, positions[upper_donor], root.helper, lower)
    metric = Metric(root.base, lower.helper, upper.helper, small, large)
    while pending:
        target = pending.pop(0)
        current, event = _pack(current, target, lower, upper, metric)
        events.append(event)
        positions = {row['input_index']: i for i, row in enumerate(event['normalization'])}
        pending = [positions[i] for i in pending]
        lower = corridor.Root(positions[lower.donor], lower.helper, lower.base, lower.exponent,
                              [dict(f, donor_index=positions[f['donor_index']]) for f in lower.factors])
        upper = corridor.Root(positions[upper.donor], upper.helper, upper.base, upper.exponent,
                              [dict(f, donor_index=positions[f['donor_index']]) for f in upper.factors])
    return current, events


def probe(words, remaining, *, audits=None):
    """Return candidates and charged model/pinch/pair/DP/reconstruction work."""
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
            pinch, switches = False, 0
            for i, sign in enumerate(signs):
                if used == remaining:
                    return candidates, used
                used += 1
                if signs[(i + 1) % len(signs)] == -sign:
                    switches += 1
                    divisor = model['n'] if sign > 0 else model['m']
                    pinch |= exponents[i] % divisor == 0
            if pinch:
                if audits is not None:
                    audits.append({'reason': 'requires_cyclic_britton_prefix'})
                continue
            for small in range(2, length(current) - len(signs) - switches - 8):
                depth = length(current) - len(signs) - switches - small - 7
                for large in range(small + 1, small * depth + 1):
                    if used == remaining:
                        return candidates, used
                    used += 1
                    metric = Metric(root.base, max(abs(x) for w in current for x in w) + 1,
                                    root.helper, small, large)
                    definition_cost = small + 2 + len(corridor.shortest_power(large, metric.root))
                    donor_cost = 2 + len(metric.spell(model['m'])) + len(metric.spell(model['n']))
                    ceiling = length(current) - 1 - definition_cost - donor_cost - len(signs)
                    if ceiling < switches:
                        continue
                    choices, cost, complete, audit = _flow(signs, exponents, metric, model,
                                                          ceiling, max(0, remaining - used - 1))
                    used += cost
                    if audits is not None:
                        audits.append({'root_donor': root.donor, 'bs_donor': donor,
                            'flow_complete': complete, 'found_flow': choices, 'flow_units': cost, **audit})
                    if choices is None:
                        continue
                    if used == remaining:
                        return candidates, used
                    used += 1
                    after, events = compile_metric(current, root, model, target, choices, small, large)
                    if length(after) >= length(current):
                        raise AssertionError('predicted two-power gain did not materialize')
                    events[-1].update({'two_power_flow_audit': audit, 'two_power_flow_complete': complete})
                    candidates.append((after, prefix + events))
    candidates.sort(key=lambda item: (length(item[0]), item[0]))
    return candidates, used
