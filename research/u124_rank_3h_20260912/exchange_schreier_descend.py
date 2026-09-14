"""Select one Schreier exchange and reserve work for its immediate descent."""
from __future__ import annotations

from collections import Counter

import exchange_schreier as schreier
import lemma11
import rank_peeling
import search
import whitehead


def _profile(word, axis):
    oriented, sign, conjugator = schreier.orientation(word, axis)
    height, maximum, others = 0, 0, 0
    positive, negative = Counter(), Counter()
    for letter in oriented:
        if letter == axis:
            positive[height] += 1
            height += 1
        elif letter == -axis:
            negative[height] += 1
            height -= 1
        else:
            others += 1
        maximum = max(maximum, height)
    return {'exponent': height, 'maximum_height': maximum, 'nonaxis_letters': others,
            'positive_from': dict(positive), 'negative_from': dict(negative)}


def _forecast(profiles, rank, index):
    lengths, residues, wraps = [], [], []
    for profile in profiles:
        unsigned = profile['exponent'] % index
        carry = 2 * unsigned > index
        residue = unsigned - index if carry else unsigned
        crossing = sum(n for h, n in profile['positive_from'].items() if h % index == index - 1)
        crossing += sum(n for h, n in profile['negative_from'].items() if h % index == 0)
        lengths.append(profile['nonaxis_letters'] + crossing + int(carry) + abs(residue))
        residues.append(residue)
        wraps.append(crossing + int(carry))
    eligible = [i for i, residue in enumerate(residues) if abs(residue) == 1]
    if not eligible:
        return None
    degree = index + 2 * (index - 1) * (rank - 1) + sum(map(abs, residues))
    defining_length = index + 1 + 4 * (index - 1) * (rank - 1)
    total = defining_length + sum(lengths)
    pivot = min(eligible, key=lambda i: (lengths[i], i))
    estimated_change = (degree - 2) * (lengths[pivot] - 2) - 2
    return {'raw_dictionary_length': total, 'raw_template_lengths': lengths,
            'signed_residues': residues, 'power_helper_tokens': wraps,
            'raw_axis_degree': degree, 'forecast_pivot_row': pivot,
            'forecast_after_removal_length': total + estimated_change,
            'forecast_status': 'selection_score_only_not_certified_normalized_bound'}


def select(words, remaining, *, postprocess_reserve=400, indices=None, axis=None):
    if type(remaining) is not int or not 0 <= remaining <= 1000:
        raise ValueError('remaining must be an integer in 0..1000')
    if type(postprocess_reserve) is not int or postprocess_reserve < 0:
        raise ValueError('postprocess_reserve must be nonnegative')
    basis = sorted({abs(x) for word in words for x in word})
    if len(basis) != len(words):
        raise ValueError('balanced presentation on its occurring basis required')
    if axis is not None and (type(axis) is not int or axis not in basis):
        raise ValueError('axis must be an occurring positive generator')
    if indices is not None:
        indices = sorted(set(indices))
        if any(type(d) is not int or d < 2 for d in indices):
            raise ValueError('indices must be integers at least two')
    reserve = min(postprocess_reserve, remaining // 2)
    planning_limit = remaining - reserve
    charged, choices, counts = 0, [], Counter()
    rank, total_length = len(words), search.length(words)
    for candidate_axis in ([axis] if axis is not None else basis):
        if charged + rank > planning_limit:
            break
        profiles = [_profile(word, candidate_axis) for word in words]
        charged += rank
        counts['axis_row_height_profiles'] += rank
        threshold = max([2] + [p['maximum_height'] + 1 for p in profiles]
                        + [2 * p['exponent'] for p in profiles])
        proposed = indices if indices is not None else range(2, threshold + 1)
        for index in proposed:
            if charged == planning_limit:
                break
            charged += 1
            counts['index_forecasts'] += 1
            helpers = 1 + (index - 1) * (rank - 1)
            required = 1 + 3 * total_length + rank + helpers * (rank + 1) + helpers * (helpers - 1) // 2
            if charged + required > planning_limit:
                break
            forecast = _forecast(profiles, rank, index)
            if forecast is None:
                continue
            choices.append({'axis': candidate_axis, 'index': index, 'no_wrap_threshold': threshold,
                            'profiles': profiles, 'dictionary_required_units': required,
                            'postprocess_reserve': reserve, **forecast})
    # Later profile checks must not consume the chosen dictionary's reservation.
    choices = [p for p in choices if charged + p['dictionary_required_units'] <= planning_limit]
    if not choices:
        return None, charged
    best = min(choices, key=lambda p: (p['forecast_after_removal_length'], p['raw_dictionary_length'],
                                      p['dictionary_required_units'], p['index'], p['axis']))
    best.update({'planner_charged_units': charged, 'planner_work_counts': dict(counts),
                 'feasible_forecasts': len(choices), 'selection': 'raw_length_and_singleton_elimination_forecast'})
    return best, charged


def probe(words, remaining, *, postprocess_reserve=400, indices=None, axis=None):
    before = tuple(tuple(word) for word in words)
    current, normalization = lemma11.normalize_witness(before)
    prefix = [] if current == before else [{'kind': 'relator_normalization', 'before': before,
                                           'after': current, 'normalization': normalization}]
    if not current:
        return [], 0
    plan, charged = select(current, remaining, postprocess_reserve=postprocess_reserve,
                           indices=indices, axis=axis)
    if plan is None:
        return [], charged
    after, events, cost, metadata = schreier.build(current, plan['axis'], plan['index'],
                                                   remaining - charged - plan['postprocess_reserve'])
    if not events:
        raise AssertionError('selected dictionary reservation was lost')
    events[0]['schreier_selection'] = plan
    events[0]['work_counts'].update(plan['planner_work_counts'])
    events[0]['charged_units'] += charged
    charged += cost
    path = prefix + events
    choices = []
    for index, row in enumerate(after):
        if sum(abs(x) == plan['axis'] for x in row) != 1:
            continue
        if charged == remaining:
            break
        endpoint, event = lemma11.remove_one(after, index, plan['axis'])
        charged += 1
        choices.append((endpoint, event))
    if not choices:
        raise AssertionError('Schreier singleton forecast produced no removal')
    current, event = min(choices, key=lambda item: (search.length(item[0]), item[0]))
    event['schreier_exchange'] = metadata
    path.append(event)
    postprocess = {'reserved_units': plan['postprocess_reserve'], 'forced_removal_tests': len(choices),
                   'start_rank': len(current), 'start_length': search.length(current),
                   'whitehead_min_cuts': 0, 'peeling_attempts': 0}
    while current and charged < remaining:
        start = current
        allowance = max(1, (remaining - charged) // 2)
        current, tail, used, whitehead_complete = whitehead.descend(current, allowance)
        path.extend(tail)
        charged += used
        postprocess['whitehead_min_cuts'] += used
        current, tail, used, peeling_complete = rank_peeling.descend(current, remaining - charged)
        path.extend(tail)
        charged += used
        postprocess['peeling_attempts'] += used
        if current == start or (whitehead_complete and peeling_complete and not tail):
            break
    postprocess.update({'after_rank': len(current), 'after_length': search.length(current),
                        'total_probe_charged_units': charged})
    events[0]['schreier_immediate_descent'] = postprocess
    if charged > remaining:
        raise AssertionError('Schreier descent exceeded budget')
    return [(current, path)], charged
