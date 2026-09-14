"""Shortest dictionary templates with an additive preference for helper tokens."""
from __future__ import annotations

from collections import Counter

import exchange_templates
from exchange_v2_geodesic import DictionaryGeodesic, Meter
from exchange_v2_probe import _orientation
import lemma11
import search


class AliasGeodesic(DictionaryGeodesic):
    def token_cost(self, tokens):
        return len(tokens), sum(abs(x) in self.basis for x in tokens)


def solve(word, definitions, remaining=1000):
    basis = {abs(x) for x in word}
    basis.update(abs(x) for w in definitions.values() for x in w)
    engine = AliasGeodesic(basis, definitions)
    meter = Meter(remaining)
    engine.saturate(meter)
    template, complete = engine.shortest(tuple(word), meter)
    return {'target': tuple(word), 'template': template, 'template_cost': engine.token_cost(template),
            'definitions': definitions, 'complete_geodesic': complete,
            'saturation_complete': engine.saturation_complete,
            'objective': 'token_length_then_old_token_count', 'charged_units': meter.used,
            'work_counts': dict(meter.counts)}


def compress(words, definitions, remaining):
    """Bounded geodesics with objective (token length, old-generator tokens)."""
    if type(remaining) is not int or remaining < 0:
        raise ValueError('remaining must be a nonnegative integer')
    words = tuple(tuple(w) for w in words)
    if search.normalize(words) != words:
        raise ValueError('normalized words are required')
    basis = sorted({abs(x) for w in words for x in w})
    definitions = tuple(tuple(w) for w in definitions)
    reserve = len(words) + len(definitions)
    if not definitions or remaining < reserve:
        return None, None, 0
    helpers = tuple(max(basis, default=0) + 1 + i for i in range(len(definitions)))
    engine = AliasGeodesic(basis, dict(zip(helpers, definitions)))
    saturation = Meter((remaining - reserve) // 3)
    engine.saturate(saturation)
    counts, charged = Counter(saturation.counts), saturation.used
    rows, templates = [], []
    for index, word in enumerate(words):
        oriented, sign, conjugator = _orientation(word, definitions, helpers, None)
        allowance = (remaining - reserve - charged) // (len(words) - index)
        meter = Meter(allowance)
        template, complete = engine.shortest(oriented, meter)
        charged += meter.used
        counts.update(meter.counts)
        literal = oriented
        for defining, helper in zip(definitions, helpers):
            literal = search.tokenize(literal, defining, helper)
        if engine.token_cost(literal) < engine.token_cost(template):
            if complete:
                raise AssertionError('completed geodesic lost to literal template')
            template = literal
        if engine.expand(template) != oriented:
            raise AssertionError('neutral alias expansion differs')
        templates.append(template)
        rows.append({'input_index': index, 'before': word, 'sign': sign, 'conjugator': conjugator,
                     'oriented': oriented, 'template': template, 'expanded': oriented,
                     'complete_geodesic': complete, 'template_cost': engine.token_cost(template)})
    defining_relators = tuple((-g,) + word for g, word in zip(helpers, definitions))
    raw_after = defining_relators + tuple(templates)
    after, normalization = lemma11.normalize_witness(raw_after)
    counts.update({'definitions': len(definitions), 'template_expansions': len(words)})
    charged += reserve
    event = {'kind': 'defining_template_compression', 'before': words,
             'certificate_kind': 'theorem_backed_stable_composite',
             'required_hypothesis': 'known balanced presentation of the trivial group',
             'helpers': helpers, 'defining_words': definitions, 'defining_relators': defining_relators,
             'rows': rows, 'templates': tuple(templates), 'raw_after': raw_after,
             'normalization': normalization, 'after': after,
             'helper_uses': {g: sum(sum(abs(x) == g for x in w) for w in templates) for g in helpers},
             'length_change': search.length(after) - search.length(words),
             'method': 'weighted_neutral_alias_preference',
             'objective': 'token_length_then_old_token_count',
             'orientation_selection': 'literal_score_then_dictionary_prefix_overlap',
             'saturation_complete': engine.saturation_complete,
             'complete_all_exact_word_geodesics': all(row['complete_geodesic'] for row in rows),
             'work_counts': dict(counts), 'charged_units': charged,
             'fully_expanded_elementary_certificate': False}
    exchange_templates.replay(event)
    if charged > remaining:
        raise AssertionError('neutral alias compression exceeded budget')
    return after, event, charged


def plans(words, maximum):
    basis = sorted({abs(x) for w in words for x in w})
    candidates = [((a, b, -a, -b),) for i, a in enumerate(basis) for positive in basis[i + 1:]
                  for b in (positive, -positive)]
    candidates.extend(exchange_templates.plans(words, maximum))
    unique = []
    for plan in candidates:
        if plan not in unique:
            unique.append(plan)
    return unique[:maximum]


def probe(words, remaining, *, maximum_plans=1):
    """Test commutator-first alias plans; finite work is shared by all attempts."""
    if type(remaining) is not int or not 0 <= remaining <= 1000:
        raise ValueError('remaining must lie in 0..1000')
    if type(maximum_plans) is not int or maximum_plans <= 0:
        raise ValueError('maximum_plans must be positive')
    before = tuple(tuple(w) for w in words)
    current, normalization = lemma11.normalize_witness(before)
    prefix = [] if before == current else [{'kind': 'relator_normalization', 'before': before,
                                           'after': current, 'normalization': normalization}]
    choices, candidates, charged = plans(current, maximum_plans), [], 0
    for index, definitions in enumerate(choices):
        allowance = (remaining - charged) // (len(choices) - index)
        after, event, cost = compress(current, definitions, max(0, allowance - max(1, len(current))))
        charged += cost
        if event is None or not any(event['helper_uses'].values()):
            continue
        events = prefix + [event]
        candidates.append((after, events))
        removals, cost = lemma11.generate_removals(after, allowance - cost)
        charged += cost
        candidates.extend((endpoint, events + tail) for endpoint, tail in removals)
    return sorted(candidates, key=lambda item: (search.length(item[0]), len(item[0]), item[0])), charged
