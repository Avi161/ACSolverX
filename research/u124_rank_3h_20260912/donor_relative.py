"""Find short ordinary-AC replacements using retained donors as dictionary tokens."""
from collections import Counter

import exchange_v2_geodesic as geodesic
import lemma11
import search


class RelativeDictionary(geodesic.DictionaryGeodesic):
    def token_cost(self, tokens):
        return sum(abs(x) in self.basis for x in tokens), len(tokens)


def compile_template(words, target, engine, tokens, donor_tokens, metadata):
    if engine.expand(tokens) != words[target]:
        raise AssertionError('relative template must expand exactly to its target')
    factors = []
    for index, token in enumerate(tokens):
        if abs(token) not in donor_tokens:
            continue
        suffix = engine.expand(tokens[index + 1:])
        factors.append({'donor_index': donor_tokens[abs(token)], 'sign': -1 if token > 0 else 1,
                        'conjugator': suffix})
    raw_target = search.reduced(token for token in tokens if abs(token) in engine.basis)
    replay = words[target]
    for factor in factors:
        donor = words[factor['donor_index']]
        if factor['sign'] == -1:
            donor = search.inverse(donor)
        c = factor['conjugator']
        replay = search.reduced(replay + search.inverse(c) + donor + c)
    if replay != raw_target:
        raise AssertionError('deleting relative donor tokens failed exact replay')
    raw = words[:target] + (raw_target,) + words[target + 1:]
    after, normalization = lemma11.normalize_witness(raw)
    return after, {'kind': 'normal_product_substitution', 'before': words, 'target': target,
                   'factors': factors, 'raw_target_after': raw_target, 'raw_after': raw,
                   'after': after, 'normalization': normalization,
                   'length_change': search.length(after) - search.length(words),
                   'macro': 'retained_donor_relative_dictionary',
                   'virtual_donor_tokens': donor_tokens, 'relative_template': tokens,
                   'virtual_token_images': engine.images, **metadata}


def probe(words, remaining):
    if type(remaining) is not int or not 0 <= remaining <= 1000:
        raise ValueError('local probe budget must be0..1000')
    words = tuple(tuple(w) for w in words)
    if search.normalize(words) != words:
        raise ValueError('relative donor probe requires normalized input')
    basis = sorted({abs(x) for w in words for x in w})
    if len(words) < 2:
        return [], 0
    candidates, charged = [], 0
    order = sorted(range(len(words)), key=lambda i: (-len(words[i]), i))
    for position, target in enumerate(order):
        allowance = (remaining - charged) // (len(order) - position)
        if allowance == 0:
            break
        first = max(basis) + 1
        donor_tokens = {first + j: i for j, i in enumerate(i for i in range(len(words)) if i != target)}
        definitions = {token: words[index] for token, index in donor_tokens.items()}
        engine = RelativeDictionary(basis, definitions)
        saturation = geodesic.Meter(allowance * 3 // 5)
        engine.saturate(saturation)
        query = geodesic.Meter(allowance - saturation.used)
        tokens, complete = engine.shortest(words[target], query)
        cost = saturation.used + query.used
        charged += cost
        if not any(abs(t) in donor_tokens for t in tokens):
            continue
        counts = Counter(saturation.counts)
        counts.update(query.counts)
        after, event = compile_template(words, target, engine, tokens, donor_tokens,
                                       {'relative_objective': 'old_letter_token_count_then_total_token_count',
                                        'relative_template_cost': engine.token_cost(tokens),
                                        'complete_fixed_dictionary_geodesic': complete,
                                        'saturation_complete': engine.saturation_complete,
                                        'work_counts': dict(counts), 'charged_units': cost})
        if after != words:
            candidates.append((after, [event]))
    return candidates, charged
