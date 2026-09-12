"""First-commutator collection using exact linear conjugate templates."""
from __future__ import annotations

import exchange_collect
import exchange_templates
import lemma11
import rank_peeling
import search
import whitehead


def power(letter, exponent):
    return ((letter,) if exponent >= 0 else (-letter,)) * abs(exponent)


def conjugate(letter, height, axis, other, helper, *, mode='all_heights'):
    """Expand an axis conjugate through c=[axis,other], retaining exact order."""
    if abs(letter) != abs(other) or (mode == 'one_direction' and height < 0):
        return search.reduced(power(axis, height) + (letter,) + power(axis, -height))
    if height > 0:
        template = power(axis, height - 1) + (helper,) + (-axis, helper) * (height - 1) + (other,)
    elif height < 0:
        template = power(axis, height) + (-helper,) + (axis, -helper) * (-height - 1) + (axis, other)
    else:
        template = (other,)
    return template if letter == other else search.inverse(template)


def compress(words, axis, other, remaining, *, mode='all_heights', direction='best'):
    if mode not in ('all_heights', 'one_direction') or direction not in ('left', 'right', 'best'):
        raise ValueError('invalid prefix collection mode or direction')
    if type(remaining) is not int or remaining < 0:
        raise ValueError('remaining must be nonnegative')
    words = tuple(tuple(w) for w in words)
    basis = {abs(x) for w in words for x in w}
    if search.normalize(words) != words or len(basis) != len(words):
        raise ValueError('normalized balanced input on its occurring basis required')
    if type(axis) is not int or type(other) is not int or abs(axis) not in basis or abs(other) not in basis or abs(axis) == abs(other):
        raise ValueError('two distinct signed occurring generators required')
    frames = ('right', 'left') if direction == 'best' else (direction,)
    required = 2 + (len(frames) + 1) * len(words)
    if remaining < required:
        return None, None, int(remaining > 0)
    helper = max(basis) + 1
    defining = (axis, other, -axis, -other)
    images = {g: (g,) for g in basis}
    images[helper] = defining
    rows, templates = [], []
    for index, word in enumerate(words):
        choices = []
        for side in frames:
            oriented, sign, conjugator = exchange_collect.orientation(word, abs(axis), side)
            exponent = sum(1 if t == axis else -1 if t == -axis else 0 for t in oriented)
            height, letters = 0, []
            for letter in oriented:
                if abs(letter) == abs(axis):
                    height += 1 if letter == axis else -1
                else:
                    letters.append((height, letter))
            chunks = []
            for h, letter in letters:
                shifted = h - (exponent if side == 'left' else 0)
                template = conjugate(letter, shifted, axis, other, helper, mode=mode)
                chunks.append({'letter': letter, 'height': shifted, 'template': template})
            body = search.reduced(t for chunk in chunks for t in chunk['template'])
            template = search.reduced(power(axis, exponent) + body if side == 'left' else body + power(axis, exponent))
            expanded = exchange_templates._expand(template, images)
            if expanded != oriented:
                raise AssertionError('linear commutator-prefix expansion differs')
            cyclic = search.canonical(template)
            row = {'input_index': index, 'before': word, 'sign': sign, 'conjugator': conjugator,
                   'oriented': oriented, 'template': template, 'expanded': expanded,
                   'prefix_direction': side, 'prefix_axis_exponent': exponent, 'prefix_chunks': chunks}
            choices.append(((len(cyclic), sum(abs(t) != helper for t in cyclic), cyclic, side), row))
        _, row = min(choices, key=lambda choice: choice[0])
        rows.append(row)
        templates.append(row['template'])
    donor = (-helper,) + defining
    raw_after = (donor,) + tuple(templates)
    after, normalization = lemma11.normalize_witness(raw_after)
    counts = {'definitions': 1, 'template_expansions': len(words),
              'prefix_plan_checks': 1, 'prefix_row_frame_checks': len(frames) * len(words)}
    event = {'kind': 'defining_template_compression', 'before': words,
             'certificate_kind': 'theorem_backed_stable_composite',
             'required_hypothesis': 'known balanced presentation of the trivial group',
             'helpers': (helper,), 'defining_words': (defining,), 'defining_relators': (donor,),
             'rows': rows, 'templates': tuple(templates), 'raw_after': raw_after,
             'normalization': normalization, 'after': after,
             'helper_uses': {helper: sum(sum(abs(t) == helper for t in w) for w in templates)},
             'length_change': search.length(after) - search.length(words),
             'method': 'commutator_prefix_collection', 'prefix_axis': axis, 'prefix_other': other,
             'prefix_mode': mode, 'prefix_direction_policy': direction,
             'work_counts': counts, 'charged_units': required,
             'fully_expanded_elementary_certificate': False}
    exchange_templates.replay(event)
    return after, event, required


def probe(words, remaining, *, postprocess_reserve=400, maximum_candidates=3, axis=None):
    if type(remaining) is not int or not 0 <= remaining <= 1000:
        raise ValueError('remaining must be in 0..1000')
    if type(postprocess_reserve) is not int or postprocess_reserve < 0:
        raise ValueError('postprocess_reserve must be nonnegative')
    if type(maximum_candidates) is not int or maximum_candidates < 1:
        raise ValueError('maximum_candidates must be positive')
    before = tuple(tuple(w) for w in words)
    current, normalization = lemma11.normalize_witness(before)
    basis = sorted({abs(x) for w in current for x in w})
    if len(basis) != len(current):
        raise ValueError('balanced input on its occurring basis required')
    if axis is not None and (type(axis) is not int or abs(axis) not in basis):
        raise ValueError('axis must be an occurring signed generator')
    prefix = [] if current == before else [{'kind': 'relator_normalization', 'before': before,
                                           'after': current, 'normalization': normalization}]
    reserve, charged, choices = min(postprocess_reserve, remaining // 2), 0, {}
    axes = [axis] if axis is not None else [sign * g for g in basis for sign in (1, -1)]
    plans = ((g, sign * h, mode) for mode in ('one_direction', 'all_heights') for g in axes
             for h in basis if h != abs(g) for sign in (1, -1))
    for g, h, mode in plans:
        if charged == remaining - reserve:
            break
        after, event, used = compress(current, g, h, remaining - reserve - charged, mode=mode)
        charged += used
        if event is None:
            break
        if not event['helper_uses'][event['helpers'][0]]:
            continue
        choices.setdefault(after, event)
    selected = sorted(choices.items(), key=lambda item: (search.length(item[0]), item[0]))[:maximum_candidates]
    candidates = []
    for index, (start, event) in enumerate(selected):
        allowance = (remaining - charged) // (len(selected) - index)
        used, after, tail = 0, start, []
        candidates.append((start, prefix + [event]))
        while after and used < allowance:
            previous = after
            after, path, work, whitehead_complete = whitehead.descend(after, max(1, (allowance - used) // 2))
            tail.extend(path)
            used += work
            after, path, work, peeling_complete = rank_peeling.descend(after, allowance - used)
            tail.extend(path)
            used += work
            if after == previous or (whitehead_complete and peeling_complete and not path):
                break
        charged += used
        event['prefix_immediate_descent'] = {'allowance': allowance, 'charged_units': used,
                                            'before_rank': len(start), 'before_length': search.length(start),
                                            'after_rank': len(after), 'after_length': search.length(after)}
        candidates.append((after, prefix + [event] + tail))
    if charged > remaining:
        raise AssertionError('commutator-prefix probe exceeded budget')
    return sorted(candidates, key=lambda pair: (search.length(pair[0]), len(pair[0]), pair[0])), charged
