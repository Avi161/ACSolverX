"""Read-only replay of the new root-metric pilot and its aca101 gain."""
import json
from pathlib import Path

import verify


HERE = Path(__file__).resolve().parent


def main():
    path = HERE / 'root_metric_pilot.json'
    report = json.loads(path.read_text())
    historical_verifier = None
    for source, expected in report['hashes'].items():
        actual = verify.sha(HERE.parent / source)
        if source.endswith('/verify.py'):
            historical_verifier = {'executed_sha256': expected, 'current_sha256': actual}
        else:
            verify.require(actual == expected, 'root metric pilot source changed: ' + source)
    verify.require(not report['seed_hashes'], 'root metric pilot unexpectedly seeded')
    baseline = verify.load_baseline()
    checked = []
    for row in report['rows']:
        result = verify.verify_record(row, baseline)
        verify.require(row['input_length'] == result['baseline_length'] and row['best_length'] == result['endpoint_length'] and row['best_rank'] == result['endpoint_rank'] and row['gain'] == result['endpoint_gain'], 'root metric row metrics differ')
        verify.require(sum(row['costs'].values()) == row['total_units'] <= row['budget'] == 1000, 'root metric row budget differs')
        checked.append(result)
    gain = next(row for row in checked if row['name'] == 'aca_101')
    verify.require(len(checked) == len({r['name'] for r in checked}) == 9 and [r['name'] for r in checked if r['endpoint_gain']] == ['aca_101'], 'root metric pilot denominator or gain set differs')
    verify.require([b['length'] for b in gain['boundaries']] == [21, 24, 20] and all(b['rank'] == 3 for b in gain['boundaries']), 'aca101 certified gain boundaries differ')
    source_row = next(row for row in report['rows'] if row['name'] == 'aca_101')
    verify.require([event['kind'] for event in source_row['events']] == ['ambient_automorphism', 'normal_product_substitution'], 'aca101 retained prefix kinds differ')
    verify.require(source_row['events'][0]['old_exponent'] == 7 and source_row['events'][0]['new_exponent'] == 4, 'aca101 helper denomination differs')
    summary = report['summary']
    verify.require(summary['rows'] == 9 and summary['gains'] == ['aca_101'] and summary['input_total'] - summary['best_total'] == 1, 'root metric summary differs')
    verify.require(summary['total_units'] == sum(row['total_units'] for row in report['rows']), 'root metric pilot work sum differs')
    result = {'status': 'PASS', 'rows': checked, 'new_gain_names': ['aca_101'], 'new_gain_total': 1,
              'new_probe_units': summary['total_units'], 'historical_seed_work': 0,
              'historical_verifier': historical_verifier, 'source_file_sha256': verify.sha(path),
              'script_sha256': verify.sha(Path(__file__)), 'census_searches': 0}
    (HERE / 'verification_root_metric_pilot.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'rows': 9, 'new_gain_names': ['aca_101'], 'boundaries': gain['boundaries'], 'new_probe_units': summary['total_units']}, indent=2))


if __name__ == '__main__':
    main()
