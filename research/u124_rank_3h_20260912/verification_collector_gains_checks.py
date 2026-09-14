"""Read-only replay of new collector gains and their exact saved prefixes."""
import json
from pathlib import Path

import verify
from verification_collection_checks import replay_collection

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
require = verify.require


def main():
    path = HERE / 'collector_remaining113.json'
    report = json.loads(path.read_text())
    hashes = []
    for source, expected in report['hashes'].items():
        actual = verify.sha(HERE.parent / source)
        require(source.endswith('/verify.py') or actual == expected, 'collector source changed')
        hashes.append({'path': source, 'executed_sha256': expected, 'current_sha256': actual})
    seeds = []
    for source, expected in report['seed_hashes'].items():
        require(verify.sha(ROOT / source) == expected, 'collector imported seed changed')
        seeds += json.loads((ROOT / source).read_text())['rows']
    baseline = verify.load_baseline()
    rows, gains = [], []
    expected = {'aca_43': (17, 16), 'aca_67': (19, 18), 'aca_79': (18, 17),
                'aca_87': (19, 18), 'aca_88': (18, 17), 'aca_106': (20, 19)}
    for row in report['rows']:
        checked = verify.verify_record(row, baseline)
        require(row['best_length'] == checked['endpoint_length'] and row['best_rank'] == checked['endpoint_rank'], 'collector metrics differ')
        require(sum(row['costs'].values()) == row['total_units'] <= row['budget'] == 1000, 'collector work budget differs')
        imported = [s for s in seeds if s['name'] == row['name']]
        for seed in imported:
            verify.verify_record(seed, baseline)
        previous = min([baseline[row['name']]['length']] + [verify.size(e['after']) for s in imported for e in s['events']])
        delta = previous - checked['endpoint_length']
        output = {'name': row['name'], 'status': 'PASS', 'preprobe_best_length': previous,
                  'endpoint_length': checked['endpoint_length'], 'endpoint_rank': checked['endpoint_rank'],
                  'new_gain_beyond_seeds': delta, 'charged_units': row['total_units']}
        if delta:
            require(row['name'] in expected and (previous, checked['endpoint_length']) == expected[row['name']] and checked['endpoint_rank'] == 3, 'unexpected collector gain')
            start = next(i for i, e in enumerate(row['events']) if e.get('method') == 'iterated_commutator_collection_stage')
            stop = start
            while stop < len(row['events']) and row['events'][stop].get('method') == 'iterated_commutator_collection_stage':
                stop += 1
            section = row['events'][start:stop]
            _, cost = replay_collection(section[0]['before'], section, allow_prefix=True)
            output.update({'all_boundary_lengths': [verify.size(row['initial'])] + [verify.size(e['after']) for e in row['events']],
                           'all_boundary_ranks': [len(row['initial'])] + [len(e['after']) for e in row['events']],
                           'saved_collection_stages': len(section), 'planned_collection_stages': section[0]['collection_stages'],
                           'saved_collection_units_including_forecasts': cost,
                           'collection_direction_policy': section[0]['collection_direction_policy'],
                           'collection_row_directions': [r['direction'] for r in section[0]['collection_rewrites']],
                           'best_prefix_event_count': checked['best_prefix_event_count']})
            gains.append(output)
        rows.append(output)
    require({r['name'] for r in gains} == set(expected), 'missing new collector gain')
    pilot = json.loads((HERE / 'collector_pilot.json').read_text())
    require({r['name'] for r in report['rows']}.isdisjoint(r['name'] for r in pilot['rows']), 'collector cohorts overlap')
    require({r['name'] for r in report['rows']} | {r['name'] for r in pilot['rows']} == set(baseline), 'collector cohort union is not exact U124')
    result = {'status': 'PASS', 'file_sha256': verify.sha(path), 'source_hash_validation': hashes,
              'rows': rows, 'new_gains': gains, 'new_gain_count': 6, 'new_gain_total': 6,
              'exact_11_plus113_partition_of124': True, 'new_probe_units': sum(r['charged_units'] for r in rows),
              'seed_discovery_work_included_in_probe_budget': False,
              'verifier_sha256': verify.sha(HERE / 'verify.py'), 'script_sha256': verify.sha(Path(__file__)), 'census_reruns': 0}
    (HERE / 'verification_collector_gains.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(gains, indent=2))


if __name__ == '__main__':
    main()
