"""Change a retained root denomination before optimizing its BS corridor."""
from __future__ import annotations

import theory_corridor as corridor
import theory_flow_exact as exact
from theory_corridor import lemma11
import whitehead
from search import inverse, length, reduced


def _shear(words, root, exponent):
    mapping = {g: (g,) for g in sorted({abs(x) for word in words for x in word})}
    backward = dict(mapping)
    mapping[root.helper] = corridor.power(root.base, root.exponent - exponent) + (root.helper,)
    backward[root.helper] = corridor.power(root.base, exponent - root.exponent) + (root.helper,)
    for g in mapping:
        if whitehead.apply(mapping[g], backward) != (g,) or whitehead.apply(backward[g], mapping) != (g,):
            raise AssertionError('root-denomination shear inverse failed')
    raw = tuple(whitehead.apply(word, mapping) for word in words)
    after, normalization = lemma11.normalize_witness(raw)
    positions = {row['input_index']: i for i, row in enumerate(normalization)}
    new_root = next(r for r in corridor.roots(after) if r.donor == positions[root.donor]
                    and r.helper == root.helper and r.base == root.base and r.exponent == exponent)
    event = {'kind': 'ambient_automorphism', 'before': words, 'after': after,
             'images': mapping, 'inverse_images': backward, 'raw_after': raw,
             'normalization': normalization, 'length_change': length(after) - length(words),
             'objective': 'change_retained_root_denomination', 'helper': root.helper,
             'root_base': root.base, 'old_exponent': root.exponent, 'new_exponent': exponent}
    return after, new_root, event


def _cyclic_pack(words, target, root):
    expanded, factors = corridor.expand_helper(words[target], root)
    core, witness = lemma11.canonical_witness(expanded)
    packed = corridor.pack_powers(core, root)
    c, sign = witness['conjugator'], witness['sign']
    raw = reduced(c + (packed if sign > 0 else inverse(packed)) + inverse(c))
    checked, unpack = corridor.expand_helper(raw, root)
    if checked != expanded:
        raise AssertionError('cyclic root repacking changed the expanded target')
    return corridor._event(words, target, raw, factors + corridor.invert_factors(unpack),
                           {'macro': 'cyclic_root_repacking', 'root_donor': root.donor,
                            'root_base': root.base, 'root_helper': root.helper,
                            'root_exponent': root.exponent, 'expanded_cyclic_witness': witness})


def compile_rebase(words, root, model, target, choices, exponent):
    current, event = corridor.compile_flow(words, target, root, model, choices)
    events = [event]
    root, model, target = exact._remap(root, model, target, event)
    current, root, event = _shear(current, root, exponent)
    events.append(event)
    positions = {row['input_index']: i for i, row in enumerate(event['normalization'])}
    pending = [positions[model['donor']], positions[target]]
    while pending:
        selected = pending.pop(0)
        after, event = _cyclic_pack(current, selected, root)
        positions = {row['input_index']: i for i, row in enumerate(event['normalization'])}
        pending = [positions[i] for i in pending]
        root = corridor.Root(positions[root.donor], root.helper, root.base, root.exponent,
                             [dict(f, donor_index=positions[f['donor_index']]) for f in root.factors])
        current = after
        events.append(event)
    return current, events


def _denominations(root, model, ceiling):
    priority = [model['m'] // 2, abs(model['n']) // 2, abs(root.exponent) - 1,
                abs(root.exponent) + 1, model['m'], abs(model['n']), 1]
    priority.extend(range(1, ceiling + 1))
    seen = {abs(root.exponent)}
    for value in priority:
        if 1 <= value <= ceiling and value not in seen:
            seen.add(value)
            yield value


def probe(words, remaining, *, audits=None):
    """Return `(candidates, charged)` for rank-three retained-root metric changes.

    One unit per tested BS donor, cyclic pinch, absolute denomination, sparse
    flow transition, and compiled signed rebase. Both denominator signs share
    one mathematically identical metric optimization. No intermediate length
    ceiling applies; the finite endpoint bound excludes only impossible gains.
    """
    if type(remaining) is not int or not 0 <= remaining <= 1000:
        raise ValueError('remaining must be an integer in 0..1000')
    before = tuple(tuple(w) for w in words)
    current, normalization = lemma11.normalize_witness(before)
    if len(current) != 3:
        return [], 0
    prefix = [] if before == current else [{'kind': 'relator_normalization',
        'before': before, 'after': current, 'normalization': normalization}]
    candidates, charged = [], 0
    for root in corridor.roots(current):
        for donor in range(3):
            if donor == root.donor:
                continue
            if charged == remaining:
                return candidates, charged
            charged += 1
            model = corridor.bs_model(current, root, donor)
            if model is None:
                continue
            target = next(i for i in range(3) if i not in (root.donor, donor))
            expanded, _ = corridor.expand_helper(current[target], root)
            data = corridor._cyclic_corridor(expanded, root, model['stable'])
            if data is None:
                continue
            signs, exponents, _ = data
            has_pinch = False
            for i, sign in enumerate(signs):
                if charged == remaining:
                    return candidates, charged
                charged += 1
                divisor = model['n'] if sign > 0 else model['m']
                if signs[(i + 1) % len(signs)] == -sign and exponents[i] % divisor == 0:
                    has_pinch = True
                    break
            if has_pinch:
                if audits is not None:
                    audits.append({'root_donor': root.donor, 'bs_donor': donor, 'target': target,
                                   'reason': 'requires_cyclic_britton_prefix'})
                continue
            for denomination in _denominations(root, model, length(current) - len(signs) - 4):
                if charged == remaining:
                    return candidates, charged
                charged += 1
                metric = corridor.Root(root.donor, root.helper, root.base, denomination, [])
                donor_cost = 2 + len(corridor.shortest_power(model['m'], metric)) + len(
                    corridor.shortest_power(model['n'], metric))
                ceiling = length(current) - 1 - (denomination + 1) - donor_cost - len(signs)
                if ceiling < 0:
                    continue
                choices, cost, complete, metadata = exact.exact_flow(signs, exponents, metric,
                    model, ceiling, max(0, remaining - charged - 1))
                charged += cost
                if audits is not None:
                    audits.append({'root_donor': root.donor, 'bs_donor': donor, 'target': target,
                                   'old_exponent': root.exponent, 'absolute_new_exponent': denomination,
                                   'cost_ceiling': ceiling, 'flow_complete': complete,
                                   'found_flow': choices, 'flow_units': cost, **metadata})
                if choices is None:
                    continue
                preferred = denomination if root.exponent > 0 else -denomination
                for exponent in (preferred, -preferred):
                    if charged == remaining:
                        return candidates, charged
                    charged += 1
                    after, events = compile_rebase(current, root, model, target, choices, exponent)
                    if length(after) >= length(current):
                        raise AssertionError('predicted root-metric gain did not materialize')
                    events[-1].update({'root_metric_flow_audit': metadata,
                                       'root_metric_flow_complete': complete})
                    candidates.append((after, prefix + events))
    candidates.sort(key=lambda item: (length(item[0]), item[0]))
    return candidates, charged
