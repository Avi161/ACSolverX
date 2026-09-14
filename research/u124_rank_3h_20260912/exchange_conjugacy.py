"""Opposite-sign helper templates from exact free-group conjugacy equations."""
from __future__ import annotations

from collections import Counter
from copy import deepcopy

import exchange_root
import exchange_templates
import lemma11
import search


def _cyclic(word):
    word = search.reduced(word)
    core, prefix = word, ()
    while len(core) > 1 and core[0] == -core[-1]:
        prefix += core[:1]
        core = core[1:-1]
    return core, prefix


def conjugator_coset(source, target):
    """Find all conjugators as ``base * primitive_root(source)^k``, k in Z."""
    source, target = search.reduced(source), search.reduced(target)
    if not source:
        raise ValueError('identity source has the whole free group as centralizer')
    source_core, source_prefix = _cyclic(source)
    target_core, target_prefix = _cyclic(target)
    if len(source_core) != len(target_core):
        return None
    cut = next((k for k in range(len(source_core))
                if source_core[k:] + source_core[:k] == target_core), None)
    if cut is None:
        return None
    base = search.reduced(target_prefix + search.inverse(source_core[:cut])
                          + search.inverse(source_prefix))
    powers = exchange_root.roots(source)
    centralizer = powers[-1][0] if powers else source
    exponent = powers[-1][1] if powers else 1
    if search.reduced(base + source + search.inverse(base)) != target:
        raise AssertionError('base conjugator identity differs')
    if search.reduced(centralizer + source + search.inverse(centralizer)) != source:
        raise AssertionError('primitive centralizer root does not commute')
    return {'source': source, 'target': target, 'source_core': source_core,
            'target_core': target_core, 'source_prefix': source_prefix,
            'target_prefix': target_prefix, 'rotation_cut': cut,
            'base_conjugator': base, 'centralizer_root': centralizer,
            'centralizer_exponent': exponent}


def _power(word, exponent):
    return search.reduced((word if exponent >= 0 else search.inverse(word)) * abs(exponent))


def discover(words, remaining, *, contexts=None, shifts=(0, 1, -1)):
    """Test finite contexts and centralizer shifts, counting every actual test."""
    if type(remaining) is not int or remaining < 0:
        raise ValueError('remaining must be a nonnegative integer')
    words = tuple(tuple(w) for w in words)
    if search.normalize(words) != words:
        raise ValueError('discover requires normalized input')
    basis = sorted({abs(x) for w in words for x in w})
    contexts = exchange_root._contexts(basis) if contexts is None else tuple(tuple(w) for w in contexts)
    if any(search.reduced(w) != w or not {abs(x) for x in w} <= set(basis) for w in contexts):
        raise ValueError('contexts must be reduced old-generator words')
    if any(type(k) is not int for k in shifts):
        raise ValueError('centralizer shifts must be integers')
    orientations = [(i, oriented, sign, conjugator) for i, w in enumerate(words)
                    for oriented, sign, conjugator in exchange_templates._orientations(w)]
    pairs = sorted(((u, v) for u in contexts if u for v in contexts),
                   key=lambda pair: (len(pair[0]) + len(pair[1]), len(pair[1]), pair))
    helper = max(basis, default=0) + 1
    found, seen, charged = {}, set(), 0
    for u, v in pairs:
        for index, oriented, sign, conjugator in orientations:
            if charged == remaining:
                break
            charged += 1
            target = search.reduced(oriented + search.inverse(v))
            coset = conjugator_coset(u, target)
            if coset is None:
                continue
            for shift in shifts:
                if charged == remaining:
                    break
                charged += 1
                raw_definition = search.reduced(coset['base_conjugator']
                                                + _power(coset['centralizer_root'], shift))
                if len(raw_definition) < 2:
                    continue
                definition = min(raw_definition, search.inverse(raw_definition))
                token = helper if definition == raw_definition else -helper
                template = (token,) + u + (-token,) + v
                if search.reduced(raw_definition + u + search.inverse(raw_definition) + v) != oriented:
                    raise AssertionError('conjugacy-derived template does not expand to target')
                axes = sorted(g for g, count in Counter(map(abs, search.canonical(template))).items()
                              if g != helper and count == 1)
                key = definition, index, search.canonical(template)
                if key in seen:
                    continue
                seen.add(key)
                witness = {'input_index': index, 'before': words[index], 'oriented': oriented,
                           'sign': sign, 'conjugator': conjugator, 'context_u': u, 'context_v': v,
                           'coset': coset, 'centralizer_shift': shift,
                           'raw_defining_word': raw_definition, 'defining_word': definition,
                           'helper': helper, 'helper_sign': 1 if token > 0 else -1,
                           'template': template, 'isolatable_old_generators': axes}
                found.setdefault(definition, []).append(witness)
        if charged == remaining:
            break
    plans = []
    for definition, witnesses in found.items():
        witnesses.sort(key=lambda w: (not w['isolatable_old_generators'],
                                     len(search.canonical(w['template'])), abs(w['centralizer_shift']),
                                     w['input_index']))
        plans.append({'defining_word': definition, 'witnesses': witnesses})
    plans.sort(key=lambda p: (not p['witnesses'][0]['isolatable_old_generators'],
                             len(p['defining_word']) + 1
                             + len(search.canonical(p['witnesses'][0]['template']))
                             - len(p['witnesses'][0]['before']), p['defining_word']))
    return plans, charged


def replay_conjugacy(witness):
    u, v, oriented = (tuple(witness[k]) for k in ('context_u', 'context_v', 'oriented'))
    coset = witness['coset']
    base, centralizer = tuple(coset['base_conjugator']), tuple(coset['centralizer_root'])
    target = search.reduced(oriented + search.inverse(v))
    if tuple(coset['source']) != u or tuple(coset['target']) != target:
        raise AssertionError('conjugacy equation differs')
    if search.reduced(base + u + search.inverse(base)) != target:
        raise AssertionError('base conjugator differs')
    if search.reduced(centralizer + u + search.inverse(centralizer)) != u:
        raise AssertionError('centralizer root differs')
    exponent = coset['centralizer_exponent']
    if not centralizer or type(exponent) is not int or exponent < 1 or exchange_root.roots(centralizer) or search.reduced(centralizer * exponent) != u:
        raise AssertionError('centralizer root is not the primitive root of the source')
    shift, sign, helper = witness['centralizer_shift'], witness['helper_sign'], witness['helper']
    if type(shift) is not int or type(sign) is not int or sign not in (-1, 1):
        raise AssertionError('invalid conjugacy shift or sign')
    raw = search.reduced(base + _power(centralizer, shift))
    defining = tuple(witness['defining_word'])
    if raw != tuple(witness['raw_defining_word']) or (defining if sign == 1 else search.inverse(defining)) != raw:
        raise AssertionError('conjugacy definition differs')
    template = (sign * helper,) + u + (-sign * helper,) + v
    if template != tuple(witness['template']) or search.reduced(raw + u + search.inverse(raw) + v) != oriented:
        raise AssertionError('opposite-sign helper template differs')
    return True


def compile_plan(words, plan, remaining, *, witness_index=0):
    if type(remaining) is not int or remaining < 0:
        raise ValueError('remaining must be a nonnegative integer')
    if remaining < len(words) + 2:
        return None, None, 0
    after, event, charged = exchange_templates.compress_dictionary(words, (plan['defining_word'],), remaining - 1)
    if event is None:
        return None, None, charged
    witness = plan['witnesses'][witness_index]
    if witness['helper'] != event['helpers'][0] or tuple(witness['before']) != tuple(words[witness['input_index']]):
        raise ValueError('conjugacy plan was prepared for a different tuple')
    event['rows'][witness['input_index']] = {'input_index': witness['input_index'], 'before': witness['before'],
        'sign': witness['sign'], 'conjugator': witness['conjugator'], 'oriented': witness['oriented'],
        'template': witness['template'], 'expanded': witness['oriented']}
    event['templates'] = tuple(tuple(r['template']) for r in event['rows'])
    event['raw_after'] = tuple(event['defining_relators']) + event['templates']
    after, event['normalization'] = lemma11.normalize_witness(event['raw_after'])
    event.update({'after': after, 'method': 'conjugacy_derived_forced_pivot',
                  'conjugacy_template_witness': deepcopy(witness),
                  'length_change': search.length(after) - search.length(words),
                  'helper_uses': {g: sum(sum(abs(x) == g for x in w) for w in event['templates'])
                                  for g in event['helpers']}})
    event['work_counts']['forced_conjugacy_template_expansions'] = 1
    event['charged_units'] += 1
    charged += 1
    exchange_templates.replay(event)
    replay_conjugacy(witness)
    return after, event, charged


def probe(words, remaining, *, maximum_plans=4):
    if type(remaining) is not int or not 0 <= remaining <= 1000:
        raise ValueError('remaining must lie in 0..1000')
    if type(maximum_plans) is not int or maximum_plans <= 0:
        raise ValueError('maximum_plans must be positive')
    before = tuple(tuple(w) for w in words)
    current, normalization = lemma11.normalize_witness(before)
    prefix = [] if before == current else [{'kind': 'relator_normalization', 'before': before,
                                           'after': current, 'normalization': normalization}]
    plans, charged = discover(current, remaining // 3)
    plans = plans[:maximum_plans]
    candidates = []
    for index, plan in enumerate(plans):
        allowance = (remaining - charged) // (len(plans) - index)
        after, event, cost = compile_plan(current, plan, max(0, allowance - max(2, len(current))))
        charged += cost
        if event is None:
            continue
        events = prefix + [event]
        candidates.append((after, events))
        removals, cost = lemma11.generate_removals(after, allowance - cost)
        charged += cost
        candidates.extend((endpoint, events + tail) for endpoint, tail in removals)
    if charged > remaining:
        raise AssertionError('conjugacy exchange exceeded work budget')
    unique = {}
    for after, events in candidates:
        if after not in unique or len(events) < len(unique[after]):
            unique[after] = events
    return sorted(unique.items(), key=lambda item: (search.length(item[0]), len(item[0]), item[0])), charged
