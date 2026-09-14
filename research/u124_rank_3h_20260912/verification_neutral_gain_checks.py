"""Saved neutral-automorphism exchange witness and cohort audit."""
import json
from pathlib import Path

import verify
from verification_consequence_checks import pilot

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def main():
    path = HERE / 'neutral_aut_exchange_remaining107.json'
    report = json.loads(path.read_text())
    for source, expected in report['hashes'].items():
        verify.require(source.endswith('/verify.py') or verify.sha(HERE.parent / source) == expected, 'neutral exchange source changed')
    seeds = []
    for source, expected in report['seed_hashes'].items():
        verify.require(verify.sha(ROOT / source) == expected, 'neutral exchange seed changed')
        seeds += json.loads((ROOT / source).read_text())['rows']
    baseline, rows, gains = verify.load_baseline(), [], []
    for row in report['rows']:
        result = verify.verify_record(row, baseline)
        verify.require(row['best_length'] == result['endpoint_length'] and row['best_rank'] == result['endpoint_rank'], 'neutral exchange endpoint metrics differ')
        verify.require(row['total_units'] == sum(row['costs'].values()) <= row['budget'] == 1000, 'neutral exchange budget differs')
        imported = [r for r in seeds if r['name'] == row['name']]
        for old in imported:
            verify.verify_record(old, baseline)
        previous = min([baseline[row['name']]['length']] + [verify.size(e['after']) for r in imported for e in r['events']])
        gain = previous - row['best_length']
        checked = {'name': row['name'], 'status': 'PASS', 'preprobe_best_length': previous,
                   'endpoint_length': row['best_length'], 'endpoint_rank': row['best_rank'], 'new_gain_beyond_seeds': gain}
        if gain:
            verify.require(row['name'] == 'aca_99' and previous == 18 and row['best_length'] == 17 and row['best_rank'] == 3, 'unexpected neutral exchange gain')
            checked.update({'source_key': row['source_key'], 'boundary_lengths': [verify.size(row['initial'])] + [verify.size(e['after']) for e in row['events']],
                            'boundary_ranks': [len(row['initial'])] + [len(e['after']) for e in row['events']],
                            'event_kinds': [e['kind'] for e in row['events']]})
            gains.append(checked)
        rows.append(checked)
    verify.require(len(gains) == 1, 'missing aca99 gain')
    first = pilot('neutral_aut_exchange_pilot17.json')
    a, b = {r['name'] for r in first['rows']}, {r['name'] for r in rows}
    verify.require(not a & b and a | b == set(baseline), 'neutral exchange cohort partition differs')
    output = {'status': 'PASS', 'rows': rows, 'new_gain': gains[0], 'pilot': first,
              'exact17_plus107_partition': True, 'new_probe_units': report['summary']['total_units'],
              'file_sha256': verify.sha(path), 'source_sha256': verify.sha(HERE / 'neutral_aut_exchange.py'),
              'verifier_sha256': verify.sha(HERE / 'verify.py'), 'script_sha256': verify.sha(Path(__file__)),
              'scope': 'Composes previously audited whole-Whitehead, literal definition and Lemma11 events. Selected neutral neighbors and definitions are bounded heuristic candidates; no global completeness claim.', 'census_reruns': 0}
    (HERE / 'verification_neutral_gain.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps(gains[0], indent=2))


if __name__ == '__main__':
    main()
