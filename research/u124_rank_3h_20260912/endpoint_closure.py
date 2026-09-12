"""Check current endpoints to completion under Whitehead descent and rank peeling."""
import json
from pathlib import Path
import time

import rank_peeling
from rank_peeling import search
import verify
import whitehead

HERE = Path(__file__).resolve().parent


def main():
    output = HERE / 'endpoint_closure_all124.json'
    if output.exists():
        raise ValueError('refusing to overwrite a saved closure check')
    table_file = HERE / 'CURRENT.json'
    current = {row['name']: row for row in json.loads(table_file.read_text())['rows']}
    baseline = verify.load_baseline()
    rows, seed_hashes = [], {}
    for name, source in current.items():
        state = search.normalize(source['words'])
        source_key = 'current_best'
        initial = search.normalize(baseline[name]['sources'][source_key])
        events = []
        if not source['witness_file'].startswith('../'):
            witness_file = HERE / source['witness_file']
            seed_hashes[str(witness_file.relative_to(HERE.parent.parent))] = verify.sha(witness_file)
            index = int(source['witness_pointer'].split('/')[-1])
            witness = json.loads(witness_file.read_text())['rows'][index]
            source_key, initial = witness['source_key'], witness['initial']
            events = witness['events'][:source['witness_prefix_events']]
        seed_event_count = len(events)
        boundary = events[-1]['after'] if events else initial
        assert state == tuple(tuple(word) for word in boundary)
        cpu, wall = time.process_time(), time.perf_counter()
        cuts, pivots, complete = 0, 0, False
        while cuts + pivots < 1000:
            before = state
            state, tail, used, aut_complete = whitehead.descend(state, 1000 - cuts - pivots)
            cuts += used
            events.extend(tail)
            state, tail, used, peel_complete = rank_peeling.descend(state, 1000 - cuts - pivots)
            pivots += used
            events.extend(tail)
            if state == before and aut_complete and peel_complete:
                complete = True
                break
        row = {'name': name, 'baseline_sha256': baseline[name]['baseline_sha256'],
               'source_key': source_key, 'initial': initial, 'events': events,
               'endpoint': state, 'input_length': baseline[name]['length'],
               'best_length': search.length(state), 'best_rank': len(state),
               'gain': baseline[name]['length'] - search.length(state),
               'seed_length': source['best_length'], 'additional_events': len(events) - seed_event_count,
               'costs': {'minimum_cuts': cuts, 'peeling_attempts': pivots},
               'total_units': cuts + pivots, 'budget': 1000,
               'cpu_seconds': time.process_time() - cpu, 'wall_seconds': time.perf_counter() - wall,
               'closure_complete': complete, 'certificate_kind': 'theorem_backed_stable_composite',
               'fully_expanded_stable_certificate': False}
        row['verification'] = verify.verify_record(row, baseline)
        rows.append(row)
        time.sleep(0.05)
    report = {'module': 'endpoint_closure', 'current_sha256': verify.sha(table_file),
              'seed_hashes': seed_hashes, 'script_sha256': verify.sha(Path(__file__)),
              'scope': 'Only new closure work is charged; full imported certificate discovery is historical.',
              'rows': rows, 'summary': {'rows': len(rows),
                  'additional_gain_ids': [row['name'] for row in rows if row['best_length'] < row['seed_length']],
                  'all_complete': all(row['closure_complete'] for row in rows),
                  'total_units': sum(row['total_units'] for row in rows),
                  'cpu_seconds': sum(row['cpu_seconds'] for row in rows)}}
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report['summary'], indent=2))


if __name__ == '__main__':
    main()
