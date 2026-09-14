"""Exact axis collection using retained iterated commutator definitions."""
from __future__ import annotations

from collections import Counter

import exchange_schreier
import exchange_templates
import lemma11
import rank_peeling
import search
import whitehead


def orientation(word, axis, side):
    exponent = sum(1 if x == axis else -1 if x == -axis else 0 for x in word)
    sign = -1 if exponent < 0 else 1
    base = tuple(word) if sign == 1 else search.inverse(word)
    height, minimum, cut = 0, 0, 0
    for i, letter in enumerate(base[:-1]):
        height += 1 if letter == axis else -1 if letter == -axis else 0
        if height < minimum or (side == 'left' and height == minimum):
            minimum, cut = height, i + 1
    return base[cut:] + base[:cut], sign, base[:cut]


def profile(words, axis, remaining, *, direction='cheapest'):
    if direction not in ('left', 'right', 'cheapest'):
        raise ValueError('direction must be left, right or cheapest')
    rows, maxima, swaps = [], {}, 0
    for word in words:
        options = []
        for side in (('right', 'left') if direction == 'cheapest' else (direction,)):
            oriented, sign, conjugator = orientation(word, axis, side)
            height, letters = 0, []
            for letter in oriented:
                if abs(letter) == axis:
                    height += 1 if letter > 0 else -1
                else:
                    letters.append((height, letter))
            shifted = [(h - (height if side == 'left' else 0), letter) for h, letter in letters]
            if any(abs(h) >= (remaining + 1).bit_length() for h, _ in shifted):
                continue
            cost = sum((1 << abs(h)) - 1 for h, _ in shifted)
            options.append((cost, side != 'right', side, shifted, oriented, sign, conjugator, height))
        if not options:
            return None
        cost, _, side, shifted, oriented, sign, conjugator, height = min(options)
        swaps += cost
        if swaps > remaining:
            return None
        for h, letter in shifted:
            if h:
                key = (1 if h > 0 else -1, abs(letter))
                maxima[key] = max(maxima.get(key, 0), abs(h))
        rows.append({'before': tuple(word), 'oriented': oriented, 'orientation_sign': sign,
                     'orientation_conjugator': conjugator, 'axis_exponent': height,
                     'direction': side, 'letters_at_heights': shifted, 'collection_swaps': cost})
    helpers = sum(maxima.values())
    rank, total = len(words), search.length(words)
    frames = 2 if direction == 'cheapest' else 1
    required = 1 + 3 * total * frames + swaps + rank + helpers * (rank + 1) + helpers * (helpers - 1) // 2
    return {'axis': axis, 'rows': rows, 'maxima': maxima, 'helper_count': helpers,
            'collection_swaps': swaps, 'required_units': required, 'direction_policy': direction,
            'tested_frames_per_row': frames}


def dictionary(basis, axis, maxima):
    fresh = max(basis)
    names, ordered = {}, []
    full = {g: (g,) for g in basis}
    for level in range(1, max(maxima.values(), default=0) + 1):
        for (sign, old), maximum in sorted(maxima.items()):
            if level > maximum:
                continue
            previous = old if level == 1 else names[sign, old, level - 1]
            fresh += 1
            names[sign, old, level] = fresh
            defining = (sign * axis, previous, -sign * axis, -previous)
            ordered.append((fresh, defining))
            full[fresh] = exchange_templates._expand(defining, full)
    return names, ordered, full


def conjugate_template(letter, height, names):
    old, sign = abs(letter), 1 if height >= 0 else -1
    levels = (0,)
    for _ in range(abs(height)):
        levels = tuple(j for level in levels for j in (level + 1, level))
    template = tuple(old if level == 0 else names[sign, old, level] for level in levels)
    return template if letter > 0 else search.inverse(template)


def build(words, axis, remaining, *, direction='cheapest'):
    if type(remaining) is not int or remaining < 0:
        raise ValueError('remaining must be nonnegative')
    words = tuple(tuple(w) for w in words)
    if search.normalize(words) != words:
        raise ValueError('normalized input is required')
    basis = {abs(x) for w in words for x in w}
    if len(basis) != len(words) or type(axis) is not int or axis not in basis:
        raise ValueError('balanced input and an occurring axis are required')
    plan = profile(words, axis, remaining, direction=direction)
    if plan is None or plan['required_units'] > remaining:
        return None, [], int(remaining > 0), {'status': 'work_budget_before_collection'}
    if not plan['helper_count']:
        return None, [], int(remaining > 0), {'status': 'no_commutator_needed'}
    names, ordered, full = dictionary(basis, axis, plan['maxima'])
    triangular = dict(ordered)
    templates, rewrites, oriented_rows = [], [], []
    for row in plan['rows']:
        chunks = []
        for height, letter in row['letters_at_heights']:
            template = conjugate_template(letter, height, names)
            expanded = exchange_templates._expand(template, full)
            expected = search.reduced(exchange_schreier._power(axis, height) + (letter,)
                                      + exchange_schreier._power(axis, -height))
            if expanded != expected:
                raise AssertionError('commutator conjugate expansion differs')
            chunks.append({'letter': letter, 'height': height, 'template': template, 'expanded': expanded})
        body = search.reduced(t for chunk in chunks for t in chunk['template'])
        power = (axis,) * row['axis_exponent']
        template = search.reduced(power + body if row['direction'] == 'left' else body + power)
        if exchange_templates._expand(template, full) != row['oriented']:
            raise AssertionError('collected complete row expansion differs')
        templates.append(template)
        rewrites.append({**row, 'conjugate_chunks': chunks, 'template': template})
        oriented_rows.append(row['oriented'])
    current, labels, raw_rows = words, [('original', i) for i in range(len(words))], oriented_rows
    events, available, charged = [], set(), 0
    for stage, (helper, defining) in enumerate(ordered):
        available.add(helper)
        next_rows = [exchange_schreier._partial(t, basis, available, triangular) for t in templates]
        event_rows, stage_templates = [], []
        for i, (word, label) in enumerate(zip(current, labels)):
            if label[0] == 'original':
                oriented = raw_rows[label[1]]
                canonical, witness = lemma11.canonical_witness(oriented)
                if canonical != word:
                    raise AssertionError('collection stage lost original-row coordinates')
                sign, conjugator = witness['sign'], search.inverse(witness['conjugator'])
                template = next_rows[label[1]]
            else:
                oriented, template, sign, conjugator = word, word, 1, ()
            images = {g: (g,) for g in {abs(t) for w in current for t in w}}
            images[helper] = defining
            expanded = exchange_templates._expand(template, images)
            if expanded != oriented:
                raise AssertionError('collection stage does not expand to retained old row')
            stage_templates.append(template)
            event_rows.append({'input_index': i, 'before': word, 'sign': sign, 'conjugator': conjugator,
                               'oriented': oriented, 'template': template, 'expanded': expanded,
                               'collection_row_label': label})
        donor = (-helper,) + defining
        raw_after = (donor,) + tuple(stage_templates)
        after, normalization = lemma11.normalize_witness(raw_after)
        counts = {'definitions': 1, 'template_expansions': len(current)}
        if not stage:
            frames = plan['tested_frames_per_row']
            counts.update({'collection_plan_checks': 1, 'collection_orientation_letters': 2 * search.length(words) * frames,
                           'collection_letter_transitions': search.length(words) * frames,
                           'collection_swap_steps': plan['collection_swaps'],
                           'collection_complete_row_expansions': len(words)})
        event = {'kind': 'defining_template_compression', 'before': current,
                 'certificate_kind': 'theorem_backed_stable_composite',
                 'required_hypothesis': 'known balanced presentation of the trivial group',
                 'helpers': (helper,), 'defining_words': (defining,), 'defining_relators': (donor,),
                 'rows': event_rows, 'templates': tuple(stage_templates), 'raw_after': raw_after,
                 'normalization': normalization, 'after': after,
                 'helper_uses': {helper: sum(sum(abs(t) == helper for t in w) for w in stage_templates)},
                 'length_change': search.length(after) - search.length(current),
                 'method': 'iterated_commutator_collection_stage', 'collection_axis': axis,
                 'collection_stage': stage + 1, 'collection_stages': len(ordered),
                 'work_counts': counts, 'charged_units': sum(counts.values()),
                 'fully_expanded_elementary_certificate': False}
        if not stage:
            event.update({'collection_rewrites': rewrites, 'collection_full_images': full,
                          'collection_definitions': ordered,
                          'collection_helper_names': [[*key, value] for key, value in names.items()],
                          'collection_direction_policy': direction})
        exchange_templates.replay(event)
        events.append(event)
        charged += event['charged_units']
        next_labels = [('definition', helper)] + labels
        labels = [next_labels[row['input_index']] for row in normalization]
        current, raw_rows = after, next_rows
    if charged != plan['required_units']:
        raise AssertionError('collection work accounting differs')
    return current, events, charged, {'status': 'complete_collection', 'axis': axis,
                                     'helper_count': len(ordered), 'dictionary_rank': len(current),
                                     'required_units': charged}


def probe(words, remaining, *, postprocess_reserve=400, axis=None, direction='cheapest'):
    if type(remaining) is not int or not 0 <= remaining <= 1000:
        raise ValueError('remaining must be in 0..1000')
    if type(postprocess_reserve) is not int or postprocess_reserve < 0:
        raise ValueError('postprocess_reserve must be nonnegative')
    before = tuple(tuple(w) for w in words)
    current, normalization = lemma11.normalize_witness(before)
    basis = sorted({abs(x) for w in current for x in w})
    if len(basis) != len(current):
        raise ValueError('balanced input on its occurring basis required')
    if axis is not None and (type(axis) is not int or axis not in basis):
        raise ValueError('axis must be an occurring generator')
    prefix = [] if before == current else [{'kind': 'relator_normalization', 'before': before,
                                           'after': current, 'normalization': normalization}]
    reserve, charged, choices = min(postprocess_reserve, remaining // 2), 0, []
    for candidate_axis in ([axis] if axis is not None else basis):
        if charged == remaining - reserve:
            break
        charged += 1
        plan = profile(current, candidate_axis, remaining - reserve - charged, direction=direction)
        if plan is None or not plan['helper_count'] or not any(r['axis_exponent'] == 1 for r in plan['rows']):
            continue
        if plan['required_units'] <= remaining - reserve - charged:
            raw = 5 * plan['helper_count']
            raw += sum(sum(1 << abs(h) for h, _ in r['letters_at_heights']) + r['axis_exponent']
                       for r in plan['rows'])
            choices.append((raw, plan['required_units'], candidate_axis))
    choices = [choice for choice in choices if choice[1] + charged <= remaining - reserve]
    if not choices:
        return [], charged
    _, _, chosen_axis = min(choices)
    after, events, used, metadata = build(current, chosen_axis, remaining - reserve - charged, direction=direction)
    if not events:
        raise AssertionError('selected collection reservation was lost')
    events[0]['work_counts']['collection_axis_forecasts'] = charged
    events[0]['charged_units'] += charged
    charged += used
    choices = []
    for index, word in enumerate(after):
        if sum(abs(t) == chosen_axis for t in word) != 1:
            continue
        if charged == remaining:
            break
        endpoint, event = lemma11.remove_one(after, index, chosen_axis)
        charged += 1
        choices.append((endpoint, event))
    if not choices:
        raise AssertionError('completed collector lost its singleton pivot')
    current, event = min(choices, key=lambda pair: (search.length(pair[0]), pair[0]))
    path = prefix + events + [event]
    post = {'reserved_units': reserve, 'forced_removal_tests': len(choices),
            'start_rank': len(current), 'start_length': search.length(current),
            'whitehead_min_cuts': 0, 'peeling_attempts': 0}
    while current and charged < remaining:
        previous = current
        current, tail, used, whitehead_complete = whitehead.descend(current, max(1, (remaining - charged) // 2))
        path.extend(tail)
        charged += used
        post['whitehead_min_cuts'] += used
        current, tail, used, peeling_complete = rank_peeling.descend(current, remaining - charged)
        path.extend(tail)
        charged += used
        post['peeling_attempts'] += used
        if current == previous or (whitehead_complete and peeling_complete and not tail):
            break
    post.update({'after_rank': len(current), 'after_length': search.length(current),
                 'total_probe_charged_units': charged})
    events[0]['collection_immediate_descent'] = post
    if charged > remaining:
        raise AssertionError('collection exceeded budget')
    return [(current, path)], charged
