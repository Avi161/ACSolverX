"""Stable dictionary exchanges using bounded exact geodesic saturation."""
from __future__ import annotations

from collections import Counter

import exchange_templates
from exchange_v2_geodesic import DictionaryGeodesic, Meter
import lemma11
import search


def _orientation(word, definitions, helpers, eliminate_generator):
    choices = []
    for oriented, sign, conjugator in exchange_templates._orientations(word):
        template = oriented
        for defining, helper in zip(definitions, helpers):
            template = search.tokenize(template, defining, helper)
        overlap = 0
        for defining in definitions:
            for image in (defining, search.inverse(defining)):
                count = 0
                for x, y in zip(oriented, image):
                    if x != y:
                        break
                    count += 1
                overlap = max(overlap, count)
        choices.append((sum(abs(x) == eliminate_generator for x in template), len(template),
                        -overlap, oriented, sign, conjugator))
    return min(choices)[3:]


def compress(words, definitions, remaining, *, eliminate_generator=None):
    """Build exact templates and a compatible defining_template_compression event."""
    if type(remaining) is not int or remaining < 0:
        raise ValueError('remaining must be a nonnegative integer')
    words = tuple(tuple(w) for w in words)
    if search.normalize(words) != words:
        raise ValueError('normalized words are required')
    basis = sorted({abs(x) for word in words for x in word})
    definitions = tuple(tuple(w) for w in definitions)
    reserve = len(words) + len(definitions)
    if not definitions or remaining < reserve:
        return None, None, 0
    helpers = tuple(max(basis, default=0) + 1 + i for i in range(len(definitions)))
    engine = DictionaryGeodesic(basis, dict(zip(helpers, definitions)),
                                eliminate_generator=eliminate_generator)
    saturation_budget = (remaining - reserve) // 2
    saturation = Meter(saturation_budget)
    engine.saturate(saturation)
    counts = Counter(saturation.counts)
    charged = saturation.used
    rows, templates = [], []
    for index, word in enumerate(words):
        oriented, sign, conjugator = _orientation(word, definitions, helpers, eliminate_generator)
        available = remaining - reserve - charged
        meter = Meter(available // (len(words) - index))
        template, complete = engine.shortest(oriented, meter)
        charged += meter.used
        counts.update(meter.counts)
        rows.append({'input_index': index, 'before': word, 'sign': sign,
                     'conjugator': conjugator, 'oriented': oriented, 'template': template,
                     'expanded': engine.expand(template), 'complete_geodesic': complete,
                     'template_cost': engine.token_cost(template)})
        templates.append(template)
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
             'method': 'weighted_free_reduction_saturation',
             'orientation_selection': 'literal_score_then_dictionary_prefix_overlap',
             'objective': 'length' if eliminate_generator is None else 'old_generator_count_then_length',
             'eliminate_generator': eliminate_generator,
             'saturation_complete': engine.saturation_complete,
             'complete_all_exact_word_geodesics': all(row['complete_geodesic'] for row in rows),
             'automaton_states': engine.states, 'automaton_edges': len(engine.edges),
             'work_counts': dict(counts), 'charged_units': charged,
             'fully_expanded_elementary_certificate': False}
    exchange_templates.replay(event)
    if charged > remaining:
        raise AssertionError('geodesic compression exceeded work budget')
    return after, event, charged


def probe(words, remaining, *, maximum_plans=4):
    """Return candidates and charged work, favoring old-generator elimination."""
    if type(remaining) is not int or not 0 <= remaining <= 1000:
        raise ValueError('remaining must lie in 0..1000')
    before = tuple(tuple(w) for w in words)
    current, normalization = lemma11.normalize_witness(before)
    prefix = [] if before == current else [{'kind': 'relator_normalization',
                                           'before': before, 'after': current,
                                           'normalization': normalization}]
    defining_plans = exchange_templates.plans(current, maximum_plans)
    options = []
    for definitions in defining_plans:
        axes = sorted({abs(x) for w in definitions for x in w}, key=lambda g:
                      (min(sum(abs(x) == g for x in row) for row in current
                           if any(abs(x) == g for x in row)), g))
        if axes:
            options.append((definitions, axes[0]))
    candidates, charged = [], 0
    for index, (definitions, axis) in enumerate(options):
        allowance = (remaining - charged) // (len(options) - index)
        dictionary_budget = max(0, allowance - max(1, len(current)))
        after, event, cost = compress(current, definitions, dictionary_budget, eliminate_generator=axis)
        charged += cost
        if event is None or not any(event['helper_uses'].values()):
            continue
        events = prefix + [event]
        candidates.append((after, events))
        available = allowance - cost
        removals, cost = lemma11.generate_removals(after, available)
        charged += cost
        candidates.extend((endpoint, events + suffix) for endpoint, suffix in removals)
    if charged > remaining:
        raise AssertionError('geodesic exchange exceeded work budget')
    unique = {}
    for after, events in candidates:
        if after not in unique or len(events) < len(unique[after]):
            unique[after] = events
    return sorted(unique.items(), key=lambda item: (search.length(item[0]), len(item[0]), item[0])), charged
