"""Bounded cyclic donor rewrites, including equal-length changes of presentation."""
from __future__ import annotations

import argparse
from collections import Counter
import heapq
import itertools
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'rank_unbounded_20260912'))
import lemma11
import search
import whitehead
import verify


def rewrite_candidates(words, allowance, increase=0):
    rules = {}
    for donor_index, donor in enumerate(words):
        for sign in (1, -1):
            signed = donor if sign == 1 else search.inverse(donor)
            for donor_cut in range(len(signed)):
                oriented = signed[donor_cut:] + signed[:donor_cut]
                for size in range(max(1, (len(donor) - increase + 1) // 2), len(donor) + 1):
                    left, right = oriented[:size], search.inverse(oriented[size:])
                    if left != right:
                        rules.setdefault(left[0], []).append((len(right) - len(left), left, right,
                                                             donor_index, -sign, signed[:donor_cut]))
    for first in rules:
        rules[first].sort()
    used, seen = 0, set()
    candidates = []
    for target_index, target in enumerate(words):
        for cut in range(len(target)):
            oriented = target[cut:] + target[:cut]
            prefix = target[:cut]
            for _, left, right, donor_index, sign, donor_prefix in rules.get(oriented[0], ()):
                if donor_index == target_index or oriented[:len(left)] != left:
                    continue
                if used == allowance:
                    return candidates, used
                used += 1
                suffix = oriented[len(left):]
                conjugator = search.reduced(donor_prefix + left + suffix + search.inverse(prefix))
                raw_target = search.reduced(prefix + right + suffix + search.inverse(prefix))
                donor = words[donor_index] if sign == 1 else search.inverse(words[donor_index])
                if search.reduced(target + search.inverse(conjugator) + donor + conjugator) != raw_target:
                    raise AssertionError('cyclic donor correction failed exact free equality')
                raw = words[:target_index] + (raw_target,) + words[target_index + 1:]
                after = search.normalize(raw)
                if after == words or after in seen:
                    continue
                seen.add(after)
                event = {'kind': 'normal_product_substitution', 'before': words, 'target': target_index,
                         'raw_target_after': raw_target,
                         'factors': [{'donor_index': donor_index, 'sign': sign, 'conjugator': conjugator}],
                         'after': after,
                         'rule': {'left': left, 'right': right, 'target_cut': cut}}
                candidates.append((after, [event]))
    return candidates, used


def neutral_whitehead(words, allowance):
    edges = whitehead.graph(words)
    vertices = sorted({v for edge in edges for v in edge})
    used, seen, out = 0, {words}, []
    for subset_size in range(1, max(1, len(vertices) - 1)):
        for a in vertices:
            others = [x for x in vertices if abs(x) != abs(a)]
            degree = sum(n for edge, n in edges.items() if a in edge)
            for subset in itertools.combinations(others, subset_size):
                if used == allowance:
                    return out, used
                used += 1
                side = {a, *subset}
                delta = whitehead.cut_value(edges, side) - degree
                if delta > 0:
                    continue
                after, event = whitehead.transform(words, a, side)
                if search.length(after) - search.length(words) != delta:
                    raise AssertionError('cut prediction differs')
                if after not in seen:
                    seen.add(after)
                    out.append((after, [event]))
    return out, used


def run_row(row, budget=1000, mode='rewrite', increase=0):
    cpu, wall = time.process_time(), time.perf_counter()
    records, parents, heap = [], {}, []
    costs = Counter()

    def remaining():
        return budget - sum(costs.values())

    def register(state, parent, events, source):
        for event in events:
            before = tuple(tuple(w) for w in event['before'])
            after = tuple(tuple(w) for w in event['after'])
            if before not in parents:
                raise AssertionError('event before-state has no registered source')
            if after not in parents:
                index = len(records)
                records.append((after, parents[before], event, source))
                parents[after] = index
                heapq.heappush(heap, (search.length(after), len(after), index))
        if state not in parents:
            if parent is not None or events:
                raise AssertionError('candidate endpoint was not captured')
            index = len(records)
            records.append((state, None, None, source))
            parents[state] = index
            heapq.heappush(heap, (search.length(state), len(state), index))

    for source in ('current_best', 'saved_rank2'):
        state = search.normalize(row['sources'][source])
        register(state, None, [], source)
    expanded = 0
    while heap and remaining() > 0:
        _, _, parent = heapq.heappop(heap)
        words, _, _, source = records[parent]
        expanded += 1
        candidates, charge = rewrite_candidates(words, min(80, remaining()), increase)
        costs['matched_donor_rewrites'] += charge
        for after, events in candidates:
            register(after, parent, events, source)
        if mode == 'whitehead' and remaining() > 0:
            candidates, charge = neutral_whitehead(words, min(96, remaining()))
            costs['whitehead_cut_evaluations'] += charge
            for after, events in candidates:
                register(after, parent, events, source)
        if remaining() > 0:
            after, events, charge, _ = whitehead.descend(words, min(40, remaining()))
            costs['minimum_cuts'] += charge
            register(after, parent, events, source)
        if remaining() > 0:
            candidates, charge = lemma11.generate_removals(words, min(12, remaining()), expose_primitives=False)
            costs['lemma11_checks'] += charge
            for after, events in candidates:
                register(after, parent, events, source)
        if mode == 'mixed':
            for defining in search.definitions(words)[:4]:
                if remaining() <= 0:
                    break
                after, event = search.compress(words, defining)
                event['kind'] = 'defining_compression'
                costs['definitions'] += 1
                register(after, parent, [event], source)

    best = min(range(len(records)), key=lambda i: (search.length(records[i][0]), len(records[i][0]), i))
    endpoint, _, _, source = records[best]
    events = []
    cursor = best
    while records[cursor][1] is not None:
        events.append(records[cursor][2])
        cursor = records[cursor][1]
    initial = records[cursor][0]
    return {'name': row['name'], 'baseline_sha256': row['baseline_sha256'], 'source_key': source,
            'initial': initial, 'events': events[::-1], 'endpoint': endpoint,
            'input_length': row['length'], 'best_length': search.length(endpoint), 'best_rank': len(endpoint),
            'gain': row['length'] - search.length(endpoint), 'mode': mode, 'rewrite_increase': increase,
            'costs': dict(costs), 'total_units': sum(costs.values()), 'budget': budget,
            'rank_limit': None, 'length_limit': None, 'expanded_states': expanded,
            'discovered_states': len(records), 'maximum_rank': max(len(r[0]) for r in records),
            'cpu_seconds': time.process_time() - cpu, 'wall_seconds': time.perf_counter() - wall,
            'certificate_kind': 'theorem_backed_stable_composite', 'fully_expanded_stable_certificate': False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=('rewrite', 'whitehead', 'mixed'), default='rewrite')
    parser.add_argument('--increase', type=int, default=0)
    parser.add_argument('--budget', type=int, default=1000)
    parser.add_argument('--ids', nargs='*')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    if not 1 <= args.budget <= 1000:
        raise ValueError('local work budget must be1..1000')
    output = Path(args.output)
    if output.exists():
        raise ValueError('refusing to overwrite results')
    baseline = verify.load_baseline()
    names = args.ids or list(baseline)
    if len(names) != len(set(names)) or set(names) - set(baseline):
        raise ValueError('unknown or duplicated ID')
    rows = []
    for name in names:
        result = run_row(baseline[name], args.budget, args.mode, args.increase)
        result['verification'] = verify.verify_record(result, baseline)
        rows.append(result)
        print(name, result['input_length'], '->', result['best_length'], 'rank', result['best_rank'], flush=True)
        time.sleep(0.05)
    summary = {'rows': len(rows), 'gains': [r['name'] for r in rows if r['gain'] > 0],
               'input_total': sum(r['input_length'] for r in rows), 'best_total': sum(r['best_length'] for r in rows),
               'cpu_seconds': sum(r['cpu_seconds'] for r in rows), 'wall_seconds': sum(r['wall_seconds'] for r in rows),
               'total_units': sum(r['total_units'] for r in rows)}
    output.write_text(json.dumps({'script_sha256': search.sha(Path(__file__)), 'rows': rows, 'summary': summary}, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
