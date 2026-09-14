"""Capture inspected macro boundaries while replaying an unchanged search policy."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import time

import lemma11
import mixed_search
import search
import whitehead


def observe(row, reference):
    saved, _ = search.parse_words(row['best_words'])
    old, _ = search.parse_words(row['starting_words'])
    states = {}
    for source, words in (('saved_best', saved), ('saved_rank2', old)):
        state = search.normalize(words)
        states.setdefault(state, {'source': source, 'parent': None, 'event': None})

    def capture(event):
        before = tuple(tuple(w) for w in event['before'])
        after = tuple(tuple(w) for w in event['after'])
        if before not in states:
            raise AssertionError('observed transition has no recorded parent')
        states.setdefault(after, {'source': states[before]['source'], 'parent': before,
                                  'event': dict(event)})

    compression, transform = search.compress, whitehead.transform
    remove, ac = lemma11.remove_one, mixed_search.ac_descents

    def wrapped_compress(*args, **kwargs):
        after, event = compression(*args, **kwargs)
        event['kind'] = 'defining_compression'
        capture(event)
        return after, event

    def wrapped_transform(*args, **kwargs):
        after, event = transform(*args, **kwargs)
        event['length_change'] = search.length(after) - search.length(event['before'])
        capture(event)
        return after, event

    def wrapped_remove(*args, **kwargs):
        after, event = remove(*args, **kwargs)
        capture(event)
        return after, event

    def wrapped_ac(*args, **kwargs):
        candidates, charged = ac(*args, **kwargs)
        for _, events in candidates:
            for event in events:
                capture(event)
        return candidates, charged

    search.compress = wrapped_compress
    whitehead.transform = lemma11.transform = wrapped_transform
    lemma11.remove_one = wrapped_remove
    mixed_search.ac_descents = wrapped_ac
    try:
        result = mixed_search.run_row(row, mode=reference['mode'])
    finally:
        search.compress = compression
        whitehead.transform = lemma11.transform = transform
        lemma11.remove_one = remove
        mixed_search.ac_descents = ac
    for key in ('best', 'best_length', 'costs', 'total_units', 'maximum_accepted_rank'):
        if json.dumps(result[key]) != json.dumps(reference[key]):
            raise AssertionError('observation changed search outcome: ' + key)

    def witness(state):
        endpoint, source = state, states[state]['source']
        events = []
        while states[state]['parent'] is not None:
            events.append(states[state]['event'])
            state = states[state]['parent']
        return {'source': source, 'initial': state, 'endpoint': endpoint,
                'rank': len(endpoint), 'total_length': search.length(endpoint),
                'events': events[::-1]}

    best = min(states, key=lambda w: (search.length(w), len(w), w))
    high = min(states, key=lambda w: (-len(w), search.length(w), w))
    rank_curve = {r: min(search.length(w) for w in states if len(w) == r)
                  for r in sorted({len(w) for w in states})}
    return {'name': row['name'], 'mode': reference['mode'], 'input_length': search.length(saved),
            'reference_best_length': reference['best_length'], 'best_length': search.length(best),
            'additional_gain': search.length(saved) - search.length(best),
            'new_gain_from_boundary_capture': reference['best_length'] - search.length(best),
            'best_witness': witness(best), 'maximum_rank_witness': witness(high),
            'maximum_inspected_rank': len(high), 'inspected_rank_length_curve': rank_curve,
            'inspected_states': len(states), 'total_units': result['total_units'],
            'cpu_seconds': result['cpu_seconds'], 'wall_seconds': result['wall_seconds'],
            'original_search_decisions_reproduced': True,
            'certificate_kind': 'theorem_backed_stable_composite'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--reference', required=True)
    parser.add_argument('--ids', nargs='*')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    table_file = here.parent / 'theory_patterns_20260912/u124_final_table.json'
    source = {r['name']: r for r in json.loads(table_file.read_text())['rows']}
    reference_path = Path(args.reference)
    prior = json.loads(reference_path.read_text())
    for name, checksum in prior['hashes'].items():
        path = table_file if name == table_file.name else here / name
        if search.sha(path) != checksum:
            raise AssertionError('executed reference source changed: ' + name)
    records = []
    for row in prior['rows']:
        if args.ids and row['name'] not in args.ids:
            continue
        result = observe(source[row['name']], row)
        records.append(result)
        print(result['name'], result['reference_best_length'], '->', result['best_length'],
              'observed rank', result['maximum_inspected_rank'], flush=True)
        time.sleep(0.05)
    summary = {'rows': len(records), 'gain_ids': [r['name'] for r in records if r['additional_gain']],
               'boundary_capture_gains': [r['name'] for r in records if r['new_gain_from_boundary_capture']],
               'input_total': sum(r['input_length'] for r in records),
               'best_total': sum(r['best_length'] for r in records),
               'cpu_seconds': sum(r['cpu_seconds'] for r in records),
               'wall_seconds': sum(r['wall_seconds'] for r in records),
               'physical_replayed_work_units': sum(r['total_units'] for r in records),
               'maximum_inspected_rank': max(r['maximum_inspected_rank'] for r in records)}
    output = Path(args.output)
    if output.exists():
        raise ValueError('refusing to overwrite results')
    output.write_text(json.dumps({'reference': str(reference_path), 'reference_sha256': search.sha(reference_path),
                                 'script_sha256': search.sha(Path(__file__)), 'rows': records,
                                 'summary': summary}, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
