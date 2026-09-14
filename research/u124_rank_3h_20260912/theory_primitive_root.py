"""Expose proper-power roots while retaining the helper and every relator."""
from __future__ import annotations

import theory_corridor as corridor
from theory_corridor import lemma11
import whitehead
from search import inverse, length, reduced


def isolate(word, helper):
    places = [i for i, x in enumerate(word) if abs(x) == helper]
    if len(places) != 1:
        raise ValueError('helper must occur exactly once in its defining relator')
    i = places[0]
    return reduced(word[i + 1:] + word[:i]) if word[i] < 0 else reduced(
        inverse(word[:i]) + inverse(word[i + 1:]))


def proper_root(word):
    for size in range(1, len(word) // 2 + 1):
        if len(word) % size == 0 and word[:size] * (len(word) // size) == word:
            return word[:size], len(word) // size
    return None


def _identity_basis(words):
    return {g: (g,) for g in sorted({abs(x) for word in words for x in word})}


def _canonicalize_definition(words, donor, helper):
    defining = isolate(words[donor], helper)
    canonical, witness = lemma11.canonical_witness(defining)
    sign, c = witness['sign'], witness['conjugator']
    forward, backward = _identity_basis(words), _identity_basis(words)
    forward[helper] = reduced(c + ((helper,) if sign > 0 else (-helper,)) + inverse(c))
    backward[helper] = reduced(inverse(c) + ((helper,) if sign > 0 else (-helper,)) + c)
    if forward[helper] == (helper,):
        if canonical != defining:
            raise AssertionError('identity helper frame did not canonicalize its definition')
        return words, donor, canonical, None
    for g in forward:
        if whitehead.apply(forward[g], backward) != (g,) or whitehead.apply(backward[g], forward) != (g,):
            raise AssertionError('helper frame inverse failed')
    raw = tuple(whitehead.apply(word, forward) for word in words)
    after, normalization = lemma11.normalize_witness(raw)
    new_donor = next(i for i, row in enumerate(normalization) if row['input_index'] == donor)
    if isolate(after[new_donor], helper) != canonical:
        raise AssertionError('helper frame did not carry the exact defining word')
    event = {'kind': 'ambient_automorphism', 'before': words, 'after': after,
             'images': forward, 'inverse_images': backward, 'raw_after': raw,
             'normalization': normalization, 'length_change': length(after) - length(words),
             'objective': 'canonicalize_retained_helper_definition',
             'defining_relator_before': donor, 'defining_relator_after': new_donor,
             'helper': helper, 'definition_before': defining, 'definition_after': canonical,
             'definition_canonical_witness': witness}
    return after, new_donor, canonical, event


def _expose(words, donor, helper, available):
    current, events, charged = words, [], 0
    defining = isolate(current[donor], helper)
    canonical, witness = lemma11.canonical_witness(defining)
    decomposition = proper_root(canonical)
    if decomposition is None:
        return [], charged
    root, exponent = decomposition
    while True:
        if witness['sign'] != 1 or witness['conjugator']:
            if charged == available:
                break
            charged += 1
            current, donor, canonical, event = _canonicalize_definition(current, donor, helper)
            if event is not None:
                event.update({'power_exponent': exponent, 'selected_root': root})
                events.append(event)
        if isolate(current[donor], helper) != canonical:
            raise AssertionError('root exposure lost its defining relation')
        decomposition = proper_root(canonical)
        if decomposition is None or decomposition[1] != exponent:
            raise AssertionError('ambient automorphism changed the maximal power exponent')
        root = decomposition[0]
        if len(root) == 1 or charged == available:
            break
        edges = whitehead.graph((root,))
        vertices = sorted({x for edge in edges for x in edge})
        options, scanned = [], 0
        for multiplier in vertices:
            if charged == available:
                break
            capacity, side = whitehead.minimum_cut(edges, multiplier)
            charged += 1
            scanned += 1
            degree = sum(n for edge, n in edges.items() if multiplier in edge)
            if capacity < degree:
                options.append((capacity - degree, multiplier, tuple(sorted(side))))
        if not options:
            break
        delta, multiplier, side = min(options)
        after, event = whitehead.transform(current, multiplier, set(side))
        if event['images'][helper] != (helper,) or event['inverse_images'][helper] != (helper,):
            raise AssertionError('relative root Whitehead step moved the helper')
        checked, normalization = lemma11.normalize_witness(event['raw_after'])
        if checked != after:
            raise AssertionError('whole tuple root-step normalization differs')
        new_donor = next(i for i, row in enumerate(normalization) if row['input_index'] == donor)
        raw_root = whitehead.apply(root, event['images'])
        canonical_root, _ = lemma11.canonical_witness(raw_root)
        if len(canonical_root) - len(root) != delta:
            raise AssertionError('selected root cut formula differs')
        event.update({'objective': 'minimize_retained_definition_root', 'helper': helper,
                      'defining_relator_before': donor, 'defining_relator_after': new_donor,
                      'power_exponent': exponent, 'selected_root_before': root,
                      'raw_root_after': raw_root, 'canonical_root_after': canonical_root,
                      'root_length_change': delta, 'length_change': length(after) - length(current),
                      'normalization': normalization, 'cut_evaluations_this_pass': scanned,
                      'complete_cut_pass': scanned == len(vertices)})
        events.append(event)
        current, donor = after, new_donor
        defining = isolate(current[donor], helper)
        canonical, witness = lemma11.canonical_witness(defining)
    if not events:
        return [], charged
    exact = isolate(current[donor], helper)
    pure = len({abs(x) for x in exact}) == 1
    events[-1].update({'proper_power_root_exposed': pure,
                      'root_exposure_finished': pure or charged < available,
                      'final_defining_relator': donor, 'final_definition': exact})
    return [(current, events)], charged


def probe(words, remaining):
    """Return `(candidates, charged)` with no rank or total-length ceiling.

    One unit per candidate defining-row/helper pair, actual helper-frame map,
    and minimum cut, including failed checks. Partial selected-root descents
    remain valid candidates but do not assert a primitive-root recognition.
    """
    if type(remaining) is not int or not 0 <= remaining <= 1000:
        raise ValueError('remaining must be an integer in 0..1000')
    before = tuple(tuple(word) for word in words)
    current, normalization = lemma11.normalize_witness(before)
    prefix = [] if before == current else [{'kind': 'relator_normalization',
        'before': before, 'after': current, 'normalization': normalization}]
    candidates, charged = [], 0
    for donor, word in enumerate(current):
        for helper in lemma11.single_occurrences(word):
            if charged == remaining:
                return candidates, charged
            charged += 1
            defining = isolate(word, helper)
            if len({abs(x) for x in defining}) <= 1:
                continue
            canonical, _ = lemma11.canonical_witness(defining)
            if proper_root(canonical) is None:
                continue
            found, cost = _expose(current, donor, helper, remaining - charged)
            charged += cost
            candidates.extend((after, prefix + events) for after, events in found if after != current)
    candidates.sort(key=lambda item: (length(item[0]), item[0]))
    return candidates, charged
