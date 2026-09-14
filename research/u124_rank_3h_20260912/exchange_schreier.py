"""Finite-index Schreier dictionaries as exact sequential stable definitions."""
from __future__ import annotations

from collections import Counter

import exchange_templates
import lemma11
import search


def _power(axis, exponent):
    return ((axis,) if exponent >= 0 else (-axis,)) * abs(exponent)


def orientation(word, axis):
    exponent = sum(1 if x == axis else -1 if x == -axis else 0 for x in word)
    sign = -1 if exponent < 0 else 1
    base = tuple(word) if sign == 1 else search.inverse(word)
    height, best_height, cut = 0, 0, 0
    for i, letter in enumerate(base[:-1]):
        height += 1 if letter == axis else -1 if letter == -axis else 0
        if height < best_height:
            best_height, cut = height, i + 1
    return base[cut:] + base[:cut], sign, base[:cut]


def dictionary(basis, axis, index):
    old = tuple(sorted(basis))
    if type(axis) is not int or axis not in old or type(index) is not int or index < 2:
        raise ValueError('invalid Schreier axis or index')
    fresh = max(old) + 1
    power_helper = fresh
    definitions = [(fresh, (axis,) * index)]
    full_images = {g: (g,) for g in old}
    full_images[fresh] = (axis,) * index
    coset_helpers = {(0, g): g for g in old if g != axis}
    for residue in range(1, index):
        for g in old:
            if g == axis:
                continue
            fresh += 1
            previous = coset_helpers[residue - 1, g]
            defining = (axis, previous, -axis)
            definitions.append((fresh, defining))
            full_images[fresh] = search.reduced((axis,) + full_images[previous] + (-axis,))
            coset_helpers[residue, g] = fresh
    return power_helper, definitions, coset_helpers, full_images


def rewrite(word, axis, index, power_helper, coset_helpers, full_images):
    state, emitted, steps, exponent = 0, [], [], 0
    for position, letter in enumerate(word):
        before = state
        if letter == axis:
            token = (power_helper,) if state == index - 1 else ()
            state = (state + 1) % index
            exponent += 1
        elif letter == -axis:
            token = (-power_helper,) if state == 0 else ()
            state = (state - 1) % index
            exponent -= 1
        else:
            helper = coset_helpers[state, abs(letter)]
            token = (helper if letter > 0 else -helper,)
        emitted.extend(token)
        expanded = exchange_templates._expand(token, full_images)
        if search.reduced(_power(axis, before) + (letter,)) != search.reduced(expanded + _power(axis, state)):
            raise AssertionError('Schreier letter transition differs')
        steps.append({'position': position, 'letter': letter, 'coset_before': before,
                      'coset_after': state, 'emitted': token})
    negative = 2 * state > index or (2 * state == index and exponent < 0)
    residue = state - index if negative else state
    subgroup = search.reduced(tuple(emitted) + ((power_helper,) if negative else ()))
    template = search.reduced(subgroup + _power(axis, residue))
    if exchange_templates._expand(template, full_images) != tuple(word):
        raise AssertionError('complete Schreier rewrite differs')
    return template, {'before': tuple(word), 'axis': axis, 'index': index, 'axis_exponent': exponent,
                      'steps': steps, 'unsigned_residue': state, 'signed_residue': residue,
                      'negative_residue_carry': negative, 'subgroup_template': subgroup,
                      'template': template}


def _partial(template, old, available, definitions):
    cache = {g: (g,) for g in old | available}

    def image(g):
        if g not in cache:
            cache[g] = search.reduced(x for token in definitions[g] for x in
                                      (image(token) if token > 0 else search.inverse(image(-token))))
        return cache[g]

    return search.reduced(x for token in template for x in
                          (image(token) if token > 0 else search.inverse(image(-token))))


def build(words, axis, index, remaining):
    """Return ``(after, events, charged, metadata)`` for a complete dictionary.

    A budget preflight costs one. If the complete staged dictionary cannot fit,
    return no events and do not allocate its potentially large helper inventory.
    This is a work restriction, not a rank or relator-length ceiling.
    """
    if type(remaining) is not int or remaining < 0:
        raise ValueError('remaining must be a nonnegative integer')
    words = tuple(tuple(w) for w in words)
    if search.normalize(words) != words:
        raise ValueError('normalized input is required')
    basis = {abs(x) for w in words for x in w}
    if len(basis) != len(words):
        raise ValueError('a balanced presentation on its occurring basis is required')
    if type(axis) is not int or axis not in basis or type(index) is not int or index < 2:
        raise ValueError('invalid Schreier axis or index')
    rank = len(words)
    helpers = 1 + (index - 1) * (rank - 1)
    required = 1 + 3 * search.length(words) + rank + helpers * (rank + 1) + helpers * (helpers - 1) // 2
    metadata = {'axis': axis, 'index': index, 'input_rank': rank,
                'helper_count': helpers, 'dictionary_rank': rank + helpers,
                'rank_after_one_removal': rank + helpers - 1,
                'required_dictionary_units': required}
    if remaining < required:
        return None, [], int(remaining > 0), {**metadata, 'status': 'work_budget_before_dictionary'}
    power_helper, ordered, coset_helpers, full_images = dictionary(basis, axis, index)
    triangular = dict(ordered)
    final_templates, rewrites, oriented_originals = [], [], []
    for word in words:
        oriented, sign, conjugator = orientation(word, axis)
        template, witness = rewrite(oriented, axis, index, power_helper, coset_helpers, full_images)
        witness.update({'input_before': word, 'orientation_sign': sign,
                        'orientation_conjugator': conjugator})
        final_templates.append(template)
        rewrites.append(witness)
        oriented_originals.append(oriented)
    current, labels, raw_originals = words, [('original', i) for i in range(rank)], oriented_originals
    events, available, charged = [], set(), 0
    for step, (helper, defining) in enumerate(ordered):
        available.add(helper)
        next_originals = [_partial(template, basis, available, triangular) for template in final_templates]
        rows, templates = [], []
        for i, (word, label) in enumerate(zip(current, labels)):
            if label[0] == 'original':
                original_index = label[1]
                oriented = raw_originals[original_index]
                canonical, witness = lemma11.canonical_witness(oriented)
                if canonical != word:
                    raise AssertionError('staged original-row identity was lost')
                sign, conjugator = witness['sign'], search.inverse(witness['conjugator'])
                template = next_originals[original_index]
            else:
                oriented, template, sign, conjugator = word, word, 1, ()
            images = {g: (g,) for g in {abs(x) for row in current for x in row}}
            images[helper] = defining
            expanded = exchange_templates._expand(template, images)
            if expanded != oriented:
                raise AssertionError('stage template does not expand to its previous original row')
            templates.append(template)
            rows.append({'input_index': i, 'before': word, 'sign': sign, 'conjugator': conjugator,
                         'oriented': oriented, 'template': template, 'expanded': expanded,
                         'schreier_row_label': label})
        defining_relator = (-helper,) + defining
        raw_after = (defining_relator,) + tuple(templates)
        after, normalization = lemma11.normalize_witness(raw_after)
        counts = {'definitions': 1, 'template_expansions': len(current)}
        if not step:
            counts.update({'schreier_plan_checks': 1, 'schreier_letter_transitions': search.length(words),
                           'schreier_orientation_letters': 2 * search.length(words),
                           'schreier_complete_row_expansions': rank})
        event = {'kind': 'defining_template_compression', 'before': current,
                 'certificate_kind': 'theorem_backed_stable_composite',
                 'required_hypothesis': 'known balanced presentation of the trivial group',
                 'helpers': (helper,), 'defining_words': (defining,),
                 'defining_relators': (defining_relator,), 'rows': rows, 'templates': tuple(templates),
                 'raw_after': raw_after, 'normalization': normalization, 'after': after,
                 'helper_uses': {helper: sum(sum(abs(x) == helper for x in row) for row in templates)},
                 'length_change': search.length(after) - search.length(current),
                 'method': 'triangular_schreier_dictionary_stage',
                 'schreier_axis': axis, 'schreier_index': index, 'schreier_stage': step + 1,
                 'schreier_stages': len(ordered), 'work_counts': counts,
                 'charged_units': sum(counts.values()), 'fully_expanded_elementary_certificate': False}
        if not step:
            event['schreier_rewrites'] = rewrites
            event['schreier_full_images'] = full_images
            event['schreier_triangular_definitions'] = ordered
        exchange_templates.replay(event)
        charged += event['charged_units']
        events.append(event)
        next_labels = [('definition', helper)] + labels
        labels = [next_labels[row['input_index']] for row in normalization]
        current, raw_originals = after, next_originals
    if charged != required or len(current) != rank + helpers:
        raise AssertionError('Schreier work or rank accounting differs')
    metadata.update({'status': 'complete_dictionary', 'original_row_labels': labels,
                     'signed_residues': [w['signed_residue'] for w in rewrites]})
    return current, events, charged, metadata


def probe(words, remaining, *, indices=(2, 3, 10)):
    if type(remaining) is not int or not 0 <= remaining <= 1000:
        raise ValueError('remaining must lie in 0..1000')
    if any(type(d) is not int or d < 2 for d in indices):
        raise ValueError('Schreier indices must be integers at least two')
    before = tuple(tuple(w) for w in words)
    current, normalization = lemma11.normalize_witness(before)
    prefix = [] if before == current else [{'kind': 'relator_normalization', 'before': before,
                                           'after': current, 'normalization': normalization}]
    basis = sorted({abs(x) for w in current for x in w})
    options = [(d, axis) for d in indices for axis in basis
               if any(sum(1 if x == axis else -1 if x == -axis else 0 for x in row) % d in (1, d - 1)
                      for row in current)]
    candidates, charged = [], 0
    for index, axis in options:
        if charged == remaining:
            break
        after, events, cost, metadata = build(current, axis, index, remaining - charged)
        charged += cost
        if not events:
            continue
        candidates.append((after, prefix + events))
        eligible = [(i, axis) for i, row in enumerate(after) if sum(abs(x) == axis for x in row) == 1]
        for target, generator in eligible:
            if charged == remaining:
                break
            endpoint, removal = lemma11.remove_one(after, target, generator)
            charged += 1
            removal['schreier_exchange'] = metadata
            if len(endpoint) != index * (len(current) - 1) + 1:
                raise AssertionError('Schreier exchange rank formula differs')
            candidates.append((endpoint, prefix + events + [removal]))
    if charged > remaining:
        raise AssertionError('Schreier probe exceeded budget')
    return sorted(candidates, key=lambda item: (search.length(item[0]), len(item[0]), item[0])), charged
