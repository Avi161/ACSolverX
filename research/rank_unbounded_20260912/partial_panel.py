"""Small selected follow-up for partial-basis exposure after the mixed screen."""
import json
from pathlib import Path
import time

import partial_basis
import search


def main():
    here = Path(__file__).resolve().parent
    source = here / 'mixed_all124.json'
    report = json.loads(source.read_text())
    selected = [r for r in report['rows'] if r['additional_gain'] or r['best_rank'] >= 4]
    output = here / 'partial_panel.json'
    if output.exists():
        raise ValueError('refusing to overwrite results')
    records = []
    for row in selected:
        words = tuple(tuple(w) for w in row['best'])
        cpu, wall = time.process_time(), time.perf_counter()
        candidates, charged = partial_basis.probe(words, 1000)
        best, path = words, []
        for _, events in candidates:
            for i, event in enumerate(events):
                after = tuple(tuple(w) for w in event['after'])
                if search.length(after) < search.length(best):
                    best, path = after, events[:i + 1]
        records.append({'name': row['name'], 'input': words, 'input_length': search.length(words),
                        'best': best, 'best_length': search.length(best), 'best_rank': len(best),
                        'additional_gain': search.length(words) - search.length(best),
                        'events': path, 'candidates': [{'after': after, 'events': events} for after, events in candidates],
                        'total_units': charged, 'budget': 1000,
                        'cpu_seconds': time.process_time() - cpu,
                        'wall_seconds': time.perf_counter() - wall})
        print(row['name'], search.length(words), '->', search.length(best), charged, flush=True)
        time.sleep(0.05)
    summary = {'rows': len(records), 'gain_ids': [r['name'] for r in records if r['additional_gain']],
               'total_units': sum(r['total_units'] for r in records),
               'cpu_seconds': sum(r['cpu_seconds'] for r in records),
               'wall_seconds': sum(r['wall_seconds'] for r in records)}
    hashes = {p.name: search.sha(p) for p in (source, Path(__file__), here / 'partial_basis.py',
                                            here / 'lemma11.py', here / 'whitehead.py', here / 'search.py')}
    output.write_text(json.dumps({'selection': 'All 11 new gains plus all retained rank4 endpoints (17 distinct rows); exploratory, no holdout.',
                                 'hashes': hashes, 'rows': records, 'summary': summary}, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
