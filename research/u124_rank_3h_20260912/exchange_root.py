"""Find hidden repeated-helper templates by exact free-group root extraction."""
from __future__ import annotations

from collections import Counter
from copy import deepcopy

import exchange_templates
import lemma11
import search


def roots(word):
    """All ``(root,power)`` with power>=2 and nonempty freely reduced word."""
    word = search.reduced(word)
    if not word:
        return []
    core, prefix = word, ()
    while len(core) > 1 and core[0] == -core[-1]:
        prefix += core[:1]
        core = core[1:-1]
    failure = [0] * len(core)
    for i in range(1, len(core)):
        j = failure[i - 1]
        while j and core[i] != core[j]:
            j = failure[j - 1]
        if core[i] == core[j]:
            j += 1
        failure[i] = j
    size = len(core) - failure[-1]
    if len(core) % size:
        size = len(core)
    multiplicity = len(core) // size
    out = []
    for power in range(2, multiplicity + 1):
        if multiplicity % power:
            continue
        root = prefix + core[:len(core) // power] + search.inverse(prefix)
        if search.reduced(root * power) != word:
            raise AssertionError('free-group root identity differs')
        out.append((root, power))
    return out


def _contexts(basis):
    return ((),) + tuple((x,) for g in basis for x in (g, -g))


def discover(words, remaining, *, contexts=None):
    """Return deduplicated defining-word plans and the number of actual root tests.

    Default contexts are empty or one signed old generator. Supplied contexts
    can be arbitrary reduced old words. Every power found by one root test is
    retained; inverse defining words share a plan, with signed helper witnesses.
    """
    if type(remaining) is not int or remaining < 0:
        raise ValueError('remaining must be a nonnegative integer')
    words = tuple(tuple(w) for w in words)
    if search.normalize(words) != words:
        raise ValueError('discover requires normalized input')
    basis = sorted({abs(x) for w in words for x in w})
    contexts = _contexts(basis) if contexts is None else tuple(tuple(w) for w in contexts)
    if any(search.reduced(w) != w or not {abs(x) for x in w} <= set(basis) for w in contexts):
        raise ValueError('contexts must be reduced old-generator words')
    pairs = sorted(((u, v) for u in contexts for v in contexts),
                   key=lambda pair: (len(pair[0]) + len(pair[1]), len(pair[1]), pair))
    orientations = [(i, oriented, sign, conjugator) for i, w in enumerate(words)
                    for oriented, sign, conjugator in exchange_templates._orientations(w)]
    helper = max(basis, default=0) + 1
    found, seen, used = {}, set(), 0
    for u, v in pairs:
        for index, oriented, sign, conjugator in orientations:
            if used == remaining:
                break
            used += 1
            test_word = search.reduced(oriented + search.inverse(v) + u)
            for root, power in roots(test_word):
                raw_definition = search.reduced(root + search.inverse(u))
                if len(raw_definition) < 2:
                    continue
                definition = min(raw_definition, search.inverse(raw_definition))
                token = helper if definition == raw_definition else -helper
                template = ((token,) + u) * (power - 1) + (token,) + v
                expanded = search.reduced((raw_definition + u) * (power - 1) + raw_definition + v)
                if expanded != oriented:
                    raise AssertionError('root-derived template does not expand to target')
                axes = sorted(g for g, count in Counter(map(abs, search.canonical(template))).items()
                              if g != helper and count == 1)
                key = definition, index, search.canonical(template)
                if key in seen:
                    continue
                seen.add(key)
                witness = {'input_index': index, 'before': words[index], 'oriented': oriented,
                           'sign': sign, 'conjugator': conjugator, 'context_u': u, 'context_v': v,
                           'test_word': test_word, 'root': root, 'power': power,
                           'raw_defining_word': raw_definition, 'defining_word': definition,
                           'helper': helper, 'helper_sign': 1 if token > 0 else -1,
                           'template': template, 'isolatable_old_generators': axes}
                found.setdefault(definition, []).append(witness)
        if used == remaining:
            break
    plans = []
    for definition, witnesses in found.items():
        witnesses.sort(key=lambda w: (not w['isolatable_old_generators'],
                                     len(search.canonical(w['template'])), -w['power'], w['input_index']))
        plans.append({'defining_word': definition, 'witnesses': witnesses})
    plans.sort(key=lambda plan: (not plan['witnesses'][0]['isolatable_old_generators'],
                                len(plan['defining_word']) + 1
                                + len(search.canonical(plan['witnesses'][0]['template']))
                                - len(plan['witnesses'][0]['before']),
                                -plan['witnesses'][0]['power'], plan['defining_word']))
    return plans, used


def compile_plan(words, plan, remaining, *, witness_index=0):
    """Retain the proven pivot template while dictionary-compressing all rows."""
    if type(remaining) is not int or remaining < 0:
        raise ValueError('remaining must be a nonnegative integer')
    if remaining < len(words) + 2:
        return None, None, 0
    after, event, charged = exchange_templates.compress_dictionary(
        words, (plan['defining_word'],), remaining - 1)
    if event is None:
        return None, None, charged
    witness = plan['witnesses'][witness_index]
    if witness['helper'] != event['helpers'][0] or tuple(witness['before']) != tuple(words[witness['input_index']]):
        raise ValueError('root plan was prepared for a different tuple')
    row = {'input_index': witness['input_index'], 'before': witness['before'],
           'sign': witness['sign'], 'conjugator': witness['conjugator'],
           'oriented': witness['oriented'], 'template': witness['template'],
           'expanded': witness['oriented']}
    event['rows'][witness['input_index']] = row
    event['templates'] = tuple(tuple(r['template']) for r in event['rows'])
    event['raw_after'] = tuple(event['defining_relators']) + event['templates']
    after, event['normalization'] = lemma11.normalize_witness(event['raw_after'])
    event.update({'after': after, 'method': 'root_derived_forced_pivot',
                  'root_template_witness': deepcopy(witness),
                  'length_change': search.length(after) - search.length(words),
                  'helper_uses': {g: sum(sum(abs(x) == g for x in w) for w in event['templates'])
                                  for g in event['helpers']}})
    event['work_counts']['forced_root_template_expansions'] = 1
    event['charged_units'] += 1
    charged += 1
    exchange_templates.replay(event)
    replay_root(witness)
    return after, event, charged


def replay_root(witness):
    oriented = tuple(witness['oriented'])
    root, u, v = (tuple(witness[key]) for key in ('root', 'context_u', 'context_v'))
    power = witness['power']
    if type(power) is not int or power < 2:
        raise AssertionError('invalid extracted power')
    h = search.reduced(oriented + search.inverse(v) + u)
    if h != tuple(witness['test_word']) or search.reduced(root * power) != h:
        raise AssertionError('root witness differs')
    raw = search.reduced(root + search.inverse(u))
    if raw != tuple(witness['raw_defining_word']):
        raise AssertionError('root definition differs')
    defining = tuple(witness['defining_word'])
    sign, helper = witness['helper_sign'], witness['helper']
    if type(sign) is not int or sign not in (-1, 1) or (defining if sign == 1 else search.inverse(defining)) != raw:
        raise AssertionError('signed root helper differs')
    template = ((sign * helper,) + u) * (power - 1) + (sign * helper,) + v
    if template != tuple(witness['template']) or search.reduced((raw + u) * (power - 1) + raw + v) != oriented:
        raise AssertionError('repeated-helper template differs')
    return True


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
        raise AssertionError('root exchange exceeded work budget')
    unique = {}
    for after, events in candidates:
        if after not in unique or len(events) < len(unique[after]):
            unique[after] = events
    return sorted(unique.items(), key=lambda item: (search.length(item[0]), len(item[0]), item[0])), charged
