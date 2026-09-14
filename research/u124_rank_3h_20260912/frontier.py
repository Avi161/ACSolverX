"""Shared bounded frontier for independently certified algebraic macro probes."""
from __future__ import annotations

import argparse
from collections import Counter
import heapq
import importlib
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


def run_row(row, probe, budget=1000, allowance=250, seed_records=()):
    cpu, wall = time.process_time(), time.perf_counter()
    records, indices, heap, costs = [], {}, [], Counter()

    def register_initial(words, source):
        if words in indices:
            return
        i = len(records)
        indices[words] = i
        records.append((words, None, None, source))
        heapq.heappush(heap, (search.length(words), len(words), i))

    def register_events(events):
        for event in events:
            before = tuple(tuple(w) for w in event['before'])
            after = tuple(tuple(w) for w in event['after'])
            parent = indices[before]
            if after not in indices:
                i = len(records)
                indices[after] = i
                records.append((after, parent, event, records[parent][3]))
                heapq.heappush(heap, (search.length(after), len(after), i))

    def remaining():
        return budget - sum(costs.values())

    for source in ('current_best', 'saved_rank2'):
        register_initial(search.normalize(row['sources'][source]), source)
    for seed in seed_records:
        if seed['name'] == row['name']:
            register_initial(search.normalize(row['sources'][seed['source_key']]), seed['source_key'])
            register_events(seed['events'])
    expanded = 0
    while heap and remaining() > 0:
        _, _, index = heapq.heappop(heap)
        words = records[index][0]
        expanded += 1
        _, events, charged, _ = whitehead.descend(words, min(24, remaining()))
        costs['minimum_cuts'] += charged
        register_events(events)
        candidates, charged = lemma11.generate_removals(words, min(8, remaining()), expose_primitives=False)
        costs['lemma11_checks'] += charged
        for _, events in candidates:
            register_events(events)
        candidates, charged = probe(words, min(allowance, remaining()))
        if type(charged) is not int or charged < 0 or charged > min(allowance, remaining()):
            raise AssertionError('macro probe returned an invalid work charge')
        costs['macro_probe_units'] += charged
        for _, events in candidates:
            register_events(events)
    best = min(range(len(records)), key=lambda i: (search.length(records[i][0]), len(records[i][0]), i))
    endpoint, _, _, source = records[best]
    events, cursor = [], best
    while records[cursor][1] is not None:
        events.append(records[cursor][2])
        cursor = records[cursor][1]
    return {'name': row['name'], 'baseline_sha256': row['baseline_sha256'], 'source_key': source,
            'initial': records[cursor][0], 'events': events[::-1], 'endpoint': endpoint,
            'input_length': row['length'], 'best_length': search.length(endpoint), 'best_rank': len(endpoint),
            'gain': row['length'] - search.length(endpoint), 'costs': dict(costs),
            'total_units': sum(costs.values()), 'budget': budget, 'probe_allowance': allowance,
            'rank_limit': None, 'length_limit': None, 'expanded_states': expanded,
            'discovered_states': len(records), 'maximum_rank': max(len(r[0]) for r in records),
            'cpu_seconds': time.process_time() - cpu, 'wall_seconds': time.perf_counter() - wall,
            'certificate_kind': 'theorem_backed_stable_composite', 'fully_expanded_stable_certificate': False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--module', required=True)
    parser.add_argument('--budget', type=int, default=1000)
    parser.add_argument('--allowance', type=int, default=250)
    parser.add_argument('--ids', nargs='*')
    parser.add_argument('--seeds', nargs='*', default=[])
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    if not 1 <= args.budget <= 1000 or not 1 <= args.allowance <= 1000:
        raise ValueError('local work limits must be1..1000')
    output = Path(args.output)
    if output.exists():
        raise ValueError('refusing to overwrite results')
    module = importlib.import_module(args.module)
    baseline = verify.load_baseline()
    names = args.ids or list(baseline)
    if len(names) != len(set(names)) or set(names) - set(baseline):
        raise ValueError('unknown or duplicated ID')
    seeds = []
    for path in args.seeds:
        for record in json.loads(Path(path).read_text())['rows']:
            verify.verify_record(record, baseline)
            seeds.append(record)
    rows = []
    for name in names:
        result = run_row(baseline[name], module.probe, args.budget, args.allowance, seeds)
        result['verification'] = verify.verify_record(result, baseline)
        rows.append(result)
        print(name, result['input_length'], '->', result['best_length'], 'rank', result['best_rank'], flush=True)
        time.sleep(0.05)
    summary = {'rows': len(rows), 'gains': [r['name'] for r in rows if r['gain'] > 0],
               'input_total': sum(r['input_length'] for r in rows), 'best_total': sum(r['best_length'] for r in rows),
               'cpu_seconds': sum(r['cpu_seconds'] for r in rows), 'wall_seconds': sum(r['wall_seconds'] for r in rows),
               'total_units': sum(r['total_units'] for r in rows)}
    paths = [Path(__file__), Path(module.__file__), HERE / 'verify.py',
             HERE.parent / 'rank_unbounded_20260912/search.py',
             HERE.parent / 'rank_unbounded_20260912/whitehead.py',
             HERE.parent / 'rank_unbounded_20260912/lemma11.py']
    output.write_text(json.dumps({'hashes': {str(p.relative_to(HERE.parent)): search.sha(p) for p in paths},
                                 'seed_hashes': {p: search.sha(Path(p)) for p in args.seeds},
                                 'module': args.module, 'rows': rows, 'summary': summary}, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
