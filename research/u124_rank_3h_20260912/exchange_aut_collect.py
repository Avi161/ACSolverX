"""A bounded neutral ambient prefix before coupled commutator aliases."""
from __future__ import annotations

from collections import Counter

import exchange_collect_aliases as aliases
import lemma11
import plateau
import rank_peeling
import search
import whitehead


def signed_pairs(words):
    degree = Counter(abs(x) for row in words for x in row)
    basis = sorted(degree, key=lambda g: (-degree[g], g))
    for axis_sign in (1, -1):
        for axis in basis:
            for other in basis:
                if other != axis:
                    for other_sign in (-1, 1):
                        yield axis_sign * axis, other_sign * other


def probe(words, remaining, *, postprocess_reserve=400, maximum_plans=3, maximum_candidates=3):
    if type(remaining) is not int or not 0 <= remaining <= 1000:
        raise ValueError('remaining must be in 0..1000')
    if type(postprocess_reserve) is not int or postprocess_reserve < 0:
        raise ValueError('postprocess reserve must be nonnegative')
    if any(type(n) is not int or n < 1 for n in (maximum_plans, maximum_candidates)):
        raise ValueError('plan and candidate counts must be positive')
    before = tuple(tuple(w) for w in words)
    current, normalization = lemma11.normalize_witness(before)
    basis = {abs(x) for row in current for x in row}
    if len(basis) != len(current):
        raise ValueError('balanced input on its occurring basis required')
    initial = [] if current == before else [{'kind': 'relator_normalization', 'before': before,
                                           'after': current, 'normalization': normalization}]
    neighbors, charged = plateau.neutral_whitehead(current, min(96, remaining // 8))
    if charged > remaining:
        raise AssertionError('neutral prefix exceeded budget')
    reserve = min(postprocess_reserve, remaining // 2)
    planning_limit = remaining - reserve
    catalog_limit = min(planning_limit, charged + remaining // 4)
    neutral_charges, catalog_charges = charged, 0
    candidates = [(state, initial + path) for state, path in neighbors if search.length(state) < search.length(current)]
    active = [(state, path, iter(signed_pairs(state))) for state, path in neighbors]
    plans = []
    catalog_cost = 2 + 4 * len(current)
    while active and charged + catalog_cost <= catalog_limit:
        following = []
        for state, path, iterator in active:
            if charged + catalog_cost > catalog_limit:
                break
            pair = next(iterator, None)
            if pair is None:
                continue
            following.append((state, path, iterator))
            plan, used = aliases.catalog(state, pair[0], pair[1], catalog_limit - charged)
            charged += used
            catalog_charges += used
            if plan is None:
                break
            plans.append((plan, initial + path))
        active = following
    selected_plans = sorted(plans, key=lambda item: (item[0]['independent_minimum_length'],
                            item[0]['axis'], item[0]['other'], item[0]['before']))[:maximum_plans]
    active = [(plan, path, iter(aliases.combinations(plan))) for plan, path in selected_plans]
    assembled, seen, scored, scoring_charges = [], set(), 0, 0
    per_score = 3 * (len(current) + 1)
    while active and charged + per_score <= planning_limit:
        following = []
        for plan, path, iterator in active:
            if charged + per_score > planning_limit:
                break
            choice = next(iterator, None)
            if choice is None:
                continue
            following.append((plan, path, iterator))
            after, event = aliases.assemble(plan, choice)
            charged += len(current) + 1
            scoring_charges += len(current) + 1
            if after in seen:
                continue
            seen.add(after)
            endpoint, tail, used, metric = aliases.score(after)
            charged += used
            scoring_charges += used
            scored += 1
            event['coupled_whitehead_score'] = metric
            event['neutral_ambient_prefix'] = {'source_length': search.length(current),
                                                'prefix_length': search.length(plan['before']),
                                                'prefix_moves': len(path) - len(initial),
                                                'orbit_exhaustive': False}
            assembled.append((endpoint, path + [event] + tail))
        active = following
    choices = sorted(assembled, key=lambda item: (search.length(item[0]), len(item[0]), item[0]))[:maximum_candidates]
    for index, (start, path) in enumerate(choices):
        allowance = (remaining - charged) // (len(choices) - index)
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
        defining = next(event for event in path if event['kind'] == 'defining_template_compression')
        defining['neutral_collect_accounting'] = {'neutral_cut_checks': neutral_charges,
                                                  'catalog_checks': catalog_charges,
                                                  'alias_assembly_and_cut_checks': scoring_charges,
                                                  'neutral_representatives': len(neighbors),
                                                  'catalogs': len(plans), 'selected_plans': len(selected_plans),
                                                  'scored_tuples': scored, 'descent_allowance': allowance,
                                                  'descent_charged_units': used}
        candidates.append((after, path + tail))
    if charged > remaining:
        raise AssertionError('neutral ambient collection exceeded budget')
    return sorted(candidates, key=lambda item: (search.length(item[0]), len(item[0]), item[0])), charged
