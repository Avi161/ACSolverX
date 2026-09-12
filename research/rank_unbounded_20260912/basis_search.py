"""Bounded mixed compression and whole-tuple basis descent, without a rank cap."""
from __future__ import annotations

import argparse
from collections import Counter
import heapq
import json
from pathlib import Path
import time

import search
import whitehead


def run_row(row, budget=1000):
    cpu, wall = time.process_time(), time.perf_counter()
    saved, mapping = search.parse_words(row['best_words'])
    old, old_mapping = search.parse_words(row['starting_words'])
    floor = search.length(saved)
    ceiling = max(floor + 2, search.length(old))
    work, seen, records = [], set(), []
    used, definitions, cuts, expanded = 0, 0, 0, 0
    winner = None
    maximum_rank = len(saved)
    for label, seed in (('saved_best', saved), ('saved_rank2', old)):
        current, path, charged, complete = whitehead.descend(seed, budget - used)
        cuts += charged
        used += charged
        if current in seen:
            continue
        seen.add(current)
        index = len(records)
        records.append({'words': current, 'parent': None, 'source': label,
                        'events': path, 'aut_minimal': complete})
        heapq.heappush(work, (search.length(current), len(current), index))
        if search.length(current) < floor:
            floor, winner = search.length(current), index
    while work and used < budget:
        _, _, parent = heapq.heappop(work)
        state = records[parent]['words']
        expanded += 1
        for defining in search.definitions(state):
            if used >= budget:
                break
            child, event = search.compress(state, defining)
            event['kind'] = 'defining_compression'
            used += 1
            definitions += 1
            # Price potentially useful temporary definitions before spending
            # multiple minimum cuts on them. The screen is deliberately bounded.
            if search.length(child) > ceiling or event['uses'] < 2:
                continue
            child, path, charged, complete = whitehead.descend(child, budget - used)
            cuts += charged
            used += charged
            maximum_rank = max(maximum_rank, len(child))
            if child in seen:
                continue
            seen.add(child)
            index = len(records)
            records.append({'words': child, 'parent': parent, 'source': records[parent]['source'],
                            'events': [event, *path], 'aut_minimal': complete})
            heapq.heappush(work, (search.length(child), len(child), index))
            if search.length(child) < floor:
                floor, winner = search.length(child), index
    endpoint = saved if winner is None else records[winner]['words']
    source = 'saved_best' if winner is None else records[winner]['source']
    events, index = [], winner
    while index is not None:
        events = records[index]['events'] + events
        index = records[index]['parent']
    if used != definitions + cuts or used > budget:
        raise AssertionError('shared budget exceeded')
    return {'name': row['name'], 'source_pointer': row['source_certificate_pointer'],
            'saved_best': saved, 'input_generator_map': mapping,
            'saved_rank2': old, 'rank2_generator_map': old_mapping,
            'input_length': search.length(saved), 'best': endpoint,
            'best_length': search.length(endpoint), 'best_rank': len(endpoint),
            'additional_gain': search.length(saved) - search.length(endpoint),
            'path_source': source, 'events': events,
            'total_units': used, 'definition_evaluations': definitions, 'minimum_cut_evaluations': cuts,
            'expanded_states': expanded, 'discovered_states': len(records),
            'rank_limit': None, 'maximum_accepted_rank': maximum_rank, 'ceiling': ceiling,
            'stop': 'candidate_budget' if used == budget else 'frontier_exhausted',
            'cpu_seconds': time.process_time() - cpu, 'wall_seconds': time.perf_counter() - wall,
            'fully_expanded_stable_certificate': False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ids', nargs='*')
    parser.add_argument('--output', required=True)
    parser.add_argument('--reuse')
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    source = here.parent / 'theory_patterns_20260912/u124_final_table.json'
    hashes = {p.name: search.sha(p) for p in (source, Path(__file__), here / 'search.py', here / 'whitehead.py')}
    previous = json.loads(Path(args.reuse).read_text()) if args.reuse else None
    if previous and previous['hashes'] != hashes:
        raise ValueError('preflight provenance changed')
    reuse = {r['name']: r for r in previous['rows']} if previous else {}
    records = []
    for row in json.loads(source.read_text())['rows']:
        if args.ids and row['name'] not in args.ids:
            continue
        result = reuse.get(row['name'])
        if result is None:
            result = run_row(row)
            time.sleep(0.05)
        records.append(result)
        print(row['name'], result['input_length'], result['best_length'], result['best_rank'], result['total_units'], flush=True)
    summary = {'rows': len(records), 'gain_ids': [r['name'] for r in records if r['additional_gain']],
               'input_total': sum(r['input_length'] for r in records),
               'best_total': sum(r['best_length'] for r in records),
               'cpu_seconds': sum(r['cpu_seconds'] for r in records),
               'wall_seconds': sum(r['wall_seconds'] for r in records),
               'total_units': sum(r['total_units'] for r in records),
               'definition_evaluations': sum(r['definition_evaluations'] for r in records),
               'minimum_cut_evaluations': sum(r['minimum_cut_evaluations'] for r in records),
               'best_ranks': dict(Counter(r['best_rank'] for r in records)),
               'maximum_accepted_rank': max(r['maximum_accepted_rank'] for r in records)}
    output = Path(args.output)
    if output.exists():
        raise ValueError('refusing to replace existing result')
    output.write_text(json.dumps({'hashes': hashes, 'rows': records, 'summary': summary}, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
