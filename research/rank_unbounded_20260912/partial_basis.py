"""Budgeted subtuple Whitehead exposure followed by witnessed Lemma 11 removal.

The caller must know that the balanced input presents the trivial group.
Exponent rank alone does not establish this hypothesis or any primitive gate.
"""
from __future__ import annotations

from itertools import combinations

import lemma11
import whitehead
from search import length


def _selections(words):
    rank = len(words)
    sizes = {2} if rank > 2 else set()
    if 2 <= rank <= 5:
        sizes.add(rank - 1)
    choices = [indices for size in sizes for indices in combinations(range(rank), size)]
    return sorted(choices, key=lambda indices:
                  (sum(len(words[i]) - 1 for i in indices), -len(indices), indices))


def _tracked_transform(words, indices, multiplier, side, delta, cuts, complete):
    after, event = whitehead.transform(words, multiplier, side)
    checked, rows = lemma11.normalize_witness(event['raw_after'])
    if checked != after:
        raise AssertionError('subtuple normalization differs')
    wanted = set(indices)
    next_indices = tuple(j for j, row in enumerate(rows) if row['input_index'] in wanted)
    change = sum(len(after[i]) for i in next_indices) - sum(len(words[i]) for i in indices)
    if len(next_indices) != len(indices) or change != delta:
        raise AssertionError('subtuple cut prediction or row tracking differs')
    event.update({'objective': 'partial_basis_subtuple_length',
                  'selected_indices_before': indices, 'selected_indices_after': next_indices,
                  'selected_length_change': delta,
                  'length_change': length(after) - length(words), 'normalization': rows,
                  'cut_evaluations_this_pass': cuts, 'complete_cut_pass': complete})
    return after, next_indices, event


def _surviving_indices(indices, event):
    survivors = [row['input_index'] for row in event['substitutions']]
    wanted = set(indices) - {event['defining_index']}
    return tuple(i for i, row in enumerate(event['normalization'])
                 if survivors[row['input_index']] in wanted)


def _cleanup(words, available, removal):
    if len(words) <= 1:
        removal.update({'cleanup_cut_evaluations': 0, 'cleanup_complete': True})
        return words, [], 0
    after, events, charged, complete = whitehead.descend(words, available)
    for event in events:
        checked, witnesses = lemma11.normalize_witness(event['raw_after'])
        if checked != event['after']:
            raise AssertionError('cleanup normalization differs')
        event.update({'objective': 'partial_basis_whole_tuple_cleanup',
                      'normalization': witnesses})
    removal.update({'cleanup_cut_evaluations': charged, 'cleanup_complete': complete})
    return after, events, charged


def _remove_group(words, indices, available):
    current, pending, events, charged = words, indices, [], 0
    while pending and charged < available and len(current) > 1:
        if any(len(current[i]) != 1 for i in pending) or len(
                {abs(current[i][0]) for i in pending}) != len(pending):
            raise AssertionError('distinct-singleton group gate was lost')
        target = pending[0]
        after, event = lemma11.remove_one(current, target, abs(current[target][0]))
        charged += 1
        next_indices = _surviving_indices(pending, event)
        event.update({'objective': 'partial_basis_distinct_singletons',
                      'partial_basis_gate': 'distinct_signed_singleton_relators',
                      'selected_indices_before': pending, 'selected_indices_after': next_indices})
        events.append(event)
        current, pending = after, next_indices
    if not events:
        return [], charged
    events[-1]['selected_group_complete'] = not pending
    after, cleanup, cost = _cleanup(current, available - charged, events[-1])
    return [(after, events + cleanup)], charged + cost


def _remove_isolators(words, indices, available):
    choices = [(i, g) for i in indices for g in lemma11.single_occurrences(words[i])]
    candidates, charged = [], 0
    for position, (i, g) in enumerate(choices):
        if charged == available:
            break
        allocation = max(1, (available - charged) // (len(choices) - position))
        after, event = lemma11.remove_one(words, i, g)
        event.update({'objective': 'partial_basis_one_occurrence',
                      'partial_basis_gate': 'exactly_one_letter_occurrence',
                      'selected_indices_before': indices,
                      'selected_indices_after': _surviving_indices(indices, event)})
        after, cleanup, cost = _cleanup(after, allocation - 1, event)
        charged += 1 + cost
        candidates.append((after, [event] + cleanup))
    return candidates, charged


def _expose(words, indices, available):
    current, selected, events, charged = words, indices, [], 0
    while charged < available:
        singletons = all(len(current[i]) == 1 for i in selected)
        distinct = singletons and len({abs(current[i][0]) for i in selected}) == len(selected)
        if distinct or charged + 1 >= available:
            break
        edges = whitehead.graph(tuple(current[i] for i in selected))
        vertices = sorted({x for edge in edges for x in edge})
        options, scanned = [], 0
        for multiplier in vertices:
            if charged + 1 == available:
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
        current, selected, event = _tracked_transform(
            current, selected, multiplier, set(side), delta, scanned, scanned == len(vertices))
        events.append(event)
    available -= charged
    if all(len(current[i]) == 1 for i in selected) and len(
            {abs(current[i][0]) for i in selected}) == len(selected):
        candidates, cost = _remove_group(current, selected, available)
    else:
        candidates, cost = _remove_isolators(current, selected, available)
    return [(after, events + suffix) for after, suffix in candidates], charged + cost


def probe(words, remaining):
    """Return ``(candidates, charged)``; candidates are ``[(after, events)]``.

    All pairs are eligible at rank three and above. At ranks two through five,
    also try subtuples of size rank-minus-one. Each plan starts from the input;
    unused work carries forward, with the remaining allowance shared among
    remaining plans. Every actual minimum cut and removal evaluation costs one,
    including failed cuts and duplicate endpoints. The total never exceeds the
    supplied integer allowance, which must be in 0..1000. No length/rank ceiling
    or generator relabeling is imposed. The returned stable paths are theorem-
    backed composites, not expanded elementary certificates or solve claims.
    """
    if type(remaining) is not int or not 0 <= remaining <= 1000:
        raise ValueError('remaining must be an integer from zero through 1000')
    before = tuple(tuple(w) for w in words)
    current, witnesses = lemma11.normalize_witness(before)
    prefix = [] if before == current else [{'kind': 'relator_normalization',
                                           'before': before, 'after': current,
                                           'normalization': witnesses}]
    plans, candidates, charged = _selections(current), [], 0
    for position, indices in enumerate(plans):
        if charged == remaining:
            break
        allocation = max(1, (remaining - charged) // (len(plans) - position))
        found, cost = _expose(current, indices, allocation)
        charged += cost
        candidates.extend((after, prefix + events) for after, events in found)
    if charged > remaining:
        raise AssertionError('partial-basis work budget exceeded')
    unique = {}
    for after, events in candidates:
        if after not in unique or len(events) < len(unique[after]):
            unique[after] = events
    result = sorted(unique.items(), key=lambda candidate:
                    (length(candidate[0]), len(candidate[0]), candidate[0], len(candidate[1])))
    return result, charged
