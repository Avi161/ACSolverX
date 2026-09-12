"""Independent saved-prefix gain replay and exact 15+109 cohort join."""
import json
from pathlib import Path

import verify
from verification_consequence_checks import pilot

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def main():
    path = HERE / 'collector_prefix_remaining109.json'
    report = json.loads(path.read_text())
    for source, expected in report['hashes'].items():
        verify.require(source.endswith('/verify.py') or verify.sha(HERE.parent / source) == expected, 'prefix source hash differs')
    seeds = []
    for source, expected in report['seed_hashes'].items():
        verify.require(verify.sha(ROOT / source) == expected, 'prefix seed hash differs')
        seeds += json.loads((ROOT / source).read_text())['rows']
    baseline, rows, gains = verify.load_baseline(), [], []
    expected = {'aca_44': (17, 16), 'aca_56': (18, 17)}
    for row in report['rows']:
        checked = verify.verify_record(row, baseline)
        verify.require(checked['endpoint_length'] == row['best_length'] and checked['endpoint_rank'] == row['best_rank'], 'prefix saved metrics differ')
        verify.require(row['total_units'] == sum(row['costs'].values()) <= row['budget'] == 1000, 'prefix budget differs')
        imported = [r for r in seeds if r['name'] == row['name']]
        for seed in imported:
            verify.verify_record(seed, baseline)
        old = min([baseline[row['name']]['length']] + [verify.size(e['after']) for r in imported for e in r['events']])
        gain = old - checked['endpoint_length']
        result = {'name': row['name'], 'status': 'PASS', 'source_key': row['source_key'],
                  'preprobe_best_length': old, 'endpoint_length': row['best_length'], 'endpoint_rank': row['best_rank'],
                  'new_gain_beyond_seeds': gain, 'charged_units': row['total_units']}
        if gain:
            verify.require(row['name'] in expected and (old, row['best_length']) == expected[row['name']] and row['best_rank'] == 3, 'unexpected prefix gain')
            result.update({'boundary_lengths': [verify.size(row['initial'])] + [verify.size(e['after']) for e in row['events']],
                           'boundary_ranks': [len(row['initial'])] + [len(e['after']) for e in row['events']],
                           'events': [{'kind': e['kind'], 'method': e.get('method')} for e in row['events']]})
            gains.append(result)
        rows.append(result)
    verify.require({r['name'] for r in gains} == set(expected), 'missing prefix gain')
    first = pilot('collector_prefix_pilot.json')
    ids_first, ids_remaining = {r['name'] for r in first['rows']}, {r['name'] for r in rows}
    verify.require(not ids_first & ids_remaining and ids_first | ids_remaining == set(baseline), 'prefix cohorts do not partition exact124')
    output = {'status': 'PASS', 'file_sha256': verify.sha(path), 'rows': rows, 'new_gains': gains,
              'pilot': first, 'exact15_plus109_partition': True, 'new_strict_gain_count': 2,
              'new_probe_units': sum(r['charged_units'] for r in rows), 'census_reruns': 0,
              'verifier_sha256': verify.sha(HERE / 'verify.py'), 'script_sha256': verify.sha(Path(__file__))}
    (HERE / 'verification_prefix_gains.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps(gains, indent=2))


if __name__ == '__main__':
    main()
