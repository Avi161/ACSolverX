"""Replay the saved new aca95 path without discovery work."""
import json
from pathlib import Path

import verify


HERE = Path(__file__).resolve().parent


def main():
    source = HERE / 'templates_remainder.json'
    report = json.loads(source.read_text())
    row = next(row for row in report['rows'] if row['name'] == 'aca_95')
    result = verify.verify_record(row)
    verify.require(result['source_key'] == 'saved_rank2', 'aca95 source differs')
    verify.require([b['length'] for b in result['boundaries']] == [19, 18, 17], 'aca95 length path differs')
    verify.require([b['rank'] for b in result['boundaries']] == [2, 3, 3], 'aca95 rank path differs')
    verify.require(result['baseline_length'] == 18 and result['endpoint_gain'] == 1, 'aca95 baseline gain differs')
    verify.require([e['kind'] for e in row['events']] == ['defining_template_compression', 'ambient_whitehead'], 'aca95 event kinds differ')
    result.update({'source_file': source.name, 'source_sha256': verify.sha(source),
                   'baseline_sha256': verify.BASELINE_SHA256,
                   'event_kinds': [e['kind'] for e in row['events']],
                   'verifier_sha256': verify.sha(HERE / 'verify.py'),
                   'script_sha256': verify.sha(Path(__file__)), 'census_searches': 0,
                   'comparison_with_literal_definition_selection': 'Not performed; parent owns this independent comparison.'})
    (HERE / 'verification_templates_gain95.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('status', 'name', 'source_key', 'baseline_length', 'endpoint_length', 'endpoint_rank', 'endpoint_gain', 'boundaries')}, indent=2))


if __name__ == '__main__':
    main()
