"""Coupled row aliases scored by complete-tuple Whitehead min-cuts."""
from __future__ import annotations

from collections import Counter
import heapq

import exchange_collect
import exchange_collect_prefix as prefix
import exchange_templates
import lemma11
import rank_peeling
import search
import whitehead


def catalog(words, axis, other, remaining):
    words = tuple(tuple(w) for w in words)
    basis = {abs(x) for w in words for x in w}
    if search.normalize(words) != words or len(basis) != len(words):
        raise ValueError('normalized balanced input required')
    if type(axis) is not int or type(other) is not int or abs(axis) not in basis or abs(other) not in basis or abs(axis) == abs(other):
        raise ValueError('distinct signed old generators required')
    required = 2 + 4 * len(words)
    if remaining < required:
        return None, int(remaining > 0)
    helper, defining = max(basis) + 1, (axis, other, -axis, -other)
    images = {g: (g,) for g in basis}
    images[helper] = defining
    aliases = []
    for index, word in enumerate(words):
        unique = {}
        for side in ('right', 'left'):
            oriented, sign, conjugator = exchange_collect.orientation(word, abs(axis), side)
            exponent = sum(1 if t == axis else -1 if t == -axis else 0 for t in oriented)
            height, letters = 0, []
            for letter in oriented:
                if abs(letter) == abs(axis):
                    height += 1 if letter == axis else -1
                else:
                    letters.append((height - (exponent if side == 'left' else 0), letter))
            for mode in ('one_direction', 'all_heights'):
                chunks = [{'letter': letter, 'height': h,
                           'template': prefix.conjugate(letter, h, axis, other, helper, mode=mode)}
                          for h, letter in letters]
                body = search.reduced(t for chunk in chunks for t in chunk['template'])
                template = search.reduced(prefix.power(axis, exponent) + body if side == 'left'
                                          else body + prefix.power(axis, exponent))
                expanded = exchange_templates._expand(template, images)
                if expanded != oriented:
                    raise AssertionError('coupled alias expansion differs')
                canonical = search.canonical(template)
                row = {'input_index': index, 'before': word, 'sign': sign, 'conjugator': conjugator,
                       'oriented': oriented, 'template': template, 'expanded': expanded,
                       'prefix_direction': side, 'prefix_axis_exponent': exponent, 'prefix_mode': mode,
                       'prefix_chunks': chunks, 'alias_canonical': canonical}
                unique.setdefault(canonical, row)
        aliases.append(sorted(unique.values(), key=lambda row: (len(row['alias_canonical']),
                       sum(abs(t) != helper for t in row['alias_canonical']), row['alias_canonical'])))
    return {'before': words, 'axis': axis, 'other': other, 'helper': helper, 'defining': defining,
            'rows': aliases, 'charged_units': required,
            'independent_minimum_length': 5 + sum(len(rows[0]['alias_canonical']) for rows in aliases)}, required


def combinations(plan):
    sizes = tuple(len(rows) for rows in plan['rows'])
    initial = (0,) * len(sizes)
    queue, seen = [(0, initial)], {initial}
    while queue:
        _, indices = heapq.heappop(queue)
        yield indices
        for row, size in enumerate(sizes):
            if indices[row] + 1 == size:
                continue
            neighbor = indices[:row] + (indices[row] + 1,) + indices[row + 1:]
            if neighbor not in seen:
                seen.add(neighbor)
                heapq.heappush(queue, (sum(neighbor), neighbor))


def assemble(plan, indices):
    before, helper = plan['before'], plan['helper']
    rows = [options[index] for options, index in zip(plan['rows'], indices)]
    templates = tuple(row['template'] for row in rows)
    images = {abs(t): (abs(t),) for word in before for t in word}
    images[helper] = plan['defining']
    for row in rows:
        if exchange_templates._expand(row['template'], images) != row['oriented']:
            raise AssertionError('assembled mixed alias expansion differs')
    donor = (-helper,) + plan['defining']
    raw_after = (donor,) + templates
    after, normalization = lemma11.normalize_witness(raw_after)
    counts = {'definitions': 1, 'template_expansions': len(before)}
    event = {'kind': 'defining_template_compression', 'before': before,
             'certificate_kind': 'theorem_backed_stable_composite',
             'required_hypothesis': 'known balanced presentation of the trivial group',
             'helpers': (helper,), 'defining_words': (plan['defining'],), 'defining_relators': (donor,),
             'rows': rows, 'templates': templates, 'raw_after': raw_after,
             'normalization': normalization, 'after': after,
             'helper_uses': {helper: sum(sum(abs(t) == helper for t in w) for w in templates)},
             'length_change': search.length(after) - search.length(before),
             'method': 'commutator_prefix_alias_collection', 'prefix_axis': plan['axis'],
             'prefix_other': plan['other'], 'prefix_mode': 'per_row', 'prefix_direction_policy': 'per_row',
             'alias_indices': indices, 'alias_catalog_sizes': tuple(len(rows) for rows in plan['rows']),
             'independent_minimum_length': plan['independent_minimum_length'],
             'work_counts': counts, 'charged_units': sum(counts.values()),
             'fully_expanded_elementary_certificate': False}
    exchange_templates.replay(event)
    return after, event


def score(words):
    edges = whitehead.graph(words)
    vertices = sorted({v for edge in edges for v in edge})
    best, tested = None, []
    for multiplier in vertices:
        capacity, side = whitehead.minimum_cut(edges, multiplier)
        degree = sum(n for edge, n in edges.items() if multiplier in edge)
        delta = capacity - degree
        tested.append({'multiplier': multiplier, 'side': tuple(sorted(side)),
                       'capacity': capacity, 'degree': degree, 'delta': delta})
        candidate = (delta, multiplier, tuple(sorted(side)))
        if delta < 0 and (best is None or candidate < best):
            best = candidate
    if best is None:
        after, events, delta = words, [], 0
    else:
        delta, multiplier, side = best
        after, event = whitehead.transform(words, multiplier, side)
        if search.length(after) != search.length(words) + delta:
            raise AssertionError('coupled Whitehead prediction differs')
        event['length_change'] = delta
        events = [event]
    return after, events, len(vertices), {'complete': True, 'signed_multipliers': tested,
                                        'raw_length': search.length(words),
                                        'one_step_length': search.length(after)}


def probe(words, remaining, *, postprocess_reserve=400, maximum_definitions=2, maximum_candidates=3):
    if type(remaining) is not int or not 0 <= remaining <= 1000:
        raise ValueError('remaining must be in 0..1000')
    if type(postprocess_reserve) is not int or postprocess_reserve < 0:
        raise ValueError('postprocess reserve must be nonnegative')
    if any(type(n) is not int or n < 1 for n in (maximum_definitions, maximum_candidates)):
        raise ValueError('candidate and definition counts must be positive')
    before = tuple(tuple(w) for w in words)
    current, normalization = lemma11.normalize_witness(before)
    basis = sorted({abs(t) for word in current for t in word})
    if len(basis) != len(current):
        raise ValueError('balanced input on its occurring basis required')
    start_events = [] if current == before else [{'kind': 'relator_normalization', 'before': before,
                                                 'after': current, 'normalization': normalization}]
    reserve = min(postprocess_reserve, remaining // 2)
    planning_limit = remaining - reserve
    catalog_limit = 3 * planning_limit // 5
    charged, catalogs = 0, []
    plans = ((s * g, t * h) for g in basis for h in basis if h != g for s in (1, -1) for t in (1, -1))
    for axis, other in plans:
        if charged == catalog_limit:
            break
        plan, used = catalog(current, axis, other, catalog_limit - charged)
        charged += used
        if plan is None:
            break
        catalogs.append(plan)
    chosen = sorted(catalogs, key=lambda p: (p['independent_minimum_length'], p['axis'], p['other']))[:maximum_definitions]
    active = [(plan, iter(combinations(plan))) for plan in chosen]
    assembled, seen, evaluations = [], set(), 0
    while active and charged + 3 * (len(current) + 1) <= planning_limit:
        following = []
        for plan, iterator in active:
            if charged + 3 * (len(current) + 1) > planning_limit:
                break
            indices = next(iterator, None)
            if indices is None:
                continue
            following.append((plan, iterator))
            after, event = assemble(plan, indices)
            charged += len(current) + 1
            if after in seen:
                continue
            seen.add(after)
            endpoint, tail, used, metric = score(after)
            charged += used
            evaluations += 1
            event['coupled_whitehead_score'] = metric
            assembled.append((endpoint, start_events + [event] + tail))
        active = following
    selected = sorted(assembled, key=lambda pair: (search.length(pair[0]), len(pair[0]), pair[0]))[:maximum_candidates]
    candidates = []
    for index, (start, path) in enumerate(selected):
        allowance = (remaining - charged) // (len(selected) - index)
        after, tail, used = start, [], 0
        candidates.append((start, path))
        while after and used < allowance:
            previous = after
            after, events, work, whitehead_complete = whitehead.descend(after, max(1, (allowance - used) // 2))
            tail.extend(events)
            used += work
            after, events, work, peeling_complete = rank_peeling.descend(after, allowance - used)
            tail.extend(events)
            used += work
            if after == previous or (whitehead_complete and peeling_complete and not events):
                break
        charged += used
        defining = next(e for e in path if e['kind'] == 'defining_template_compression')
        defining['alias_probe_accounting'] = {'catalogs': len(catalogs), 'selected_definitions': len(chosen),
                                              'scored_tuples': evaluations, 'descent_allowance': allowance,
                                              'descent_charged_units': used}
        candidates.append((after, path + tail))
    if charged > remaining:
        raise AssertionError('coupled alias probe exceeded budget')
    return sorted(candidates, key=lambda pair: (search.length(pair[0]), len(pair[0]), pair[0])), charged
