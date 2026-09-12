"""Read-only replay and incremental accounting for the saved uphill screen."""
import json
from pathlib import Path
import verify as v

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def main():
    path = HERE / 'uphill_whitehead_all124.json'
    report = json.loads(path.read_text())
    for source, expected in report['hashes'].items():
        v.require(source.endswith('/verify.py') or v.sha(HERE.parent / source) == expected, 'uphill source changed')
    seeds = []
    for source, expected in report['seed_hashes'].items():
        v.require(v.sha(ROOT / source) == expected, 'uphill seed changed')
        seeds += json.loads((ROOT / source).read_text())['rows']
    baseline, checked, gains = v.load_baseline(), [], []
    expected_gains = {'aca_72': (17, 16), 'aca_80': (17, 16), 'aca_111': (21, 20)}
    for row in report['rows']:
        result = v.verify_record(row, baseline)
        v.require(row['total_units'] == sum(row['costs'].values()) <= row['budget'] == 1000, 'uphill costs differ')
        imported = [r for r in seeds if r['name'] == row['name']]
        for old in imported:
            v.verify_record(old, baseline)
        previous = min([baseline[row['name']]['length']] + [v.size(e['after']) for r in imported for e in r['events']])
        gain = previous - result['endpoint_length']
        record = {'name': row['name'], 'status': 'PASS', 'preprobe_best_length': previous,
                  'endpoint_length': result['endpoint_length'], 'endpoint_rank': result['endpoint_rank'],
                  'new_gain_beyond_seeds': gain}
        if gain:
            v.require(row['name'] in expected_gains and (previous, result['endpoint_length']) == expected_gains[row['name']], 'unexpected uphill gain')
            record.update(source_key=row['source_key'], boundary_lengths=[v.size(row['initial'])] + [v.size(e['after']) for e in row['events']],
                          boundary_ranks=[len(row['initial'])] + [len(e['after']) for e in row['events']],
                          event_kinds=[e['kind'] for e in row['events']])
            gains.append(record)
        checked.append(record)
    v.require(len(checked) == 124 and {r['name'] for r in checked} == set(baseline), 'uphill cohort differs')
    v.require({r['name'] for r in gains} == set(expected_gains) and sum(r['endpoint_length'] for r in checked) == 2162, 'uphill census metrics differ')
    output = {'status': 'PASS', 'rows': checked, 'new_gains': gains, 'new_probe_units': report['summary']['total_units'],
              'total_length': 2162, 'census_reruns': 0, 'file_sha256': v.sha(path),
              'source_sha256': v.sha(HERE / 'uphill_whitehead.py'), 'verifier_sha256': v.sha(HERE / 'verify.py'),
              'scope': 'Finite ordinary donor-growth candidates followed by whole-Whitehead descent and nonincreasing singleton peeling. Historical seed discovery costs are separate from the new 124000-unit screen.'}
    (HERE / 'verification_uphill.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps(gains, indent=2))


if __name__ == '__main__':
    main()
