"""Saved plateau records and one wrapping, signed, nonconsecutive-label control."""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
import json
from pathlib import Path

import verify


HERE = Path(__file__).resolve().parent
require = verify.require
word, words, free = verify.word, verify.words, verify.free
invert, normalized, size = verify.invert, verify.normalized, verify.size


def check_rule(event):
    if event['kind'] != 'normal_product_substitution' or 'rule' not in event:
        return
    before = words(event['before'])
    target = before[event['target']]
    rule = event['rule']
    left, right, cut = word(rule['left']), word(rule['right']), rule['target_cut']
    require(type(cut) is int and 0 <= cut < len(target), 'invalid circular target cut')
    rotated = target[cut:] + target[:cut]
    require(left and rotated[:len(left)] == left, 'circular rule does not match target')
    suffix, prefix = rotated[len(left):], target[:cut]
    expected = free(prefix + right + suffix + invert(prefix))
    require(expected == word(event['raw_target_after']), 'circular target frame was not restored')
    require(len(event['factors']) == 1, 'circular rule has unexpected factor count')
    factor = event['factors'][0]
    donor = before[factor['donor_index']]
    oriented_sign = -factor['sign']
    signed = donor if oriented_sign == 1 else invert(donor)
    orientation = left + invert(right)
    matches = []
    for donor_cut in range(len(signed)):
        if signed[donor_cut:] + signed[:donor_cut] == orientation:
            conjugator = free(signed[:donor_cut] + left + suffix + invert(prefix))
            if conjugator == word(factor['conjugator']):
                matches.append(donor_cut)
    require(matches, 'correction sign/conjugator does not match any exact donor rotation')


def saved_reports():
    baseline = verify.load_baseline()
    outputs, rewrite_ids = [], []
    for filename in ('plateau_pilot.json', 'plateau_whitehead_pilot.json', 'plateau_remainder.json'):
        report = json.loads((HERE / filename).read_text())
        require(report['script_sha256'] == verify.sha(HERE / 'plateau.py'), 'executed plateau source changed')
        rows = report['rows']
        require(len(rows) == len({r['name'] for r in rows}), 'duplicate pilot ID')
        if filename != 'plateau_whitehead_pilot.json':
            rewrite_ids.extend(r['name'] for r in rows)
        checks, counts = [], Counter()
        for row in rows:
            result = verify.verify_record(row, baseline)
            require(row['input_length'] == baseline[row['name']]['length'], 'reported input length wrong')
            require(row['best_length'] == result['endpoint_length'] and row['best_rank'] == result['endpoint_rank'], 'reported best endpoint wrong')
            require(row['gain'] == result['endpoint_gain'], 'reported gain wrong')
            require(row['total_units'] == sum(row['costs'].values()) <= row['budget'] <= 1000, 'reported shared budget wrong')
            require(row['rank_limit'] is None and row['length_limit'] is None, 'unexpected ceiling')
            require(row['fully_expanded_stable_certificate'] is False, 'unexpanded certificate mislabeled')
            require(not result['endpoint_misses_better_prefix'], 'saved endpoint omits a better prefix')
            for event in row['events']:
                check_rule(event)
                counts[event['kind']] += 1
            checks.append({'name': row['name'], 'status': 'PASS', 'initial_source': row['source_key'],
                           'baseline_length': result['baseline_length'], 'baseline_rank': result['baseline_rank'],
                           'endpoint_length': result['endpoint_length'], 'endpoint_rank': result['endpoint_rank'],
                           'gain': result['endpoint_gain'], 'same_length_rank_improvement': result['same_length_rank_improvement'],
                           'boundaries': result['boundaries']})
        summary = report['summary']
        require(summary['rows'] == len(rows), 'summary denominator wrong')
        require(summary['gains'] == [r['name'] for r in rows if r['gain'] > 0], 'summary gain IDs wrong')
        for total, key in (('input_total', 'input_length'), ('best_total', 'best_length'), ('total_units', 'total_units')):
            require(summary[total] == sum(r[key] for r in rows), 'summary total wrong: ' + total)
        outputs.append({'file': filename, 'sha256': verify.sha(HERE / filename), 'status': 'PASS',
                        'rows': checks, 'events': dict(counts), 'physical_work_units': summary['total_units']})
    require(len(rewrite_ids) == len(set(rewrite_ids)) == 124 and set(rewrite_ids) == set(baseline), 'pilot and remainder do not partition U124')
    gains = [r for report in outputs if report['file'] != 'plateau_whitehead_pilot.json' for r in report['rows'] if r['gain'] > 0]
    require([(r['name'], r['baseline_length'], r['endpoint_length']) for r in gains] == [('aca_75', 19, 18), ('aca_83', 20, 19), ('aca_84', 20, 19)], 'new gains differ')
    ranks = [r['name'] for report in outputs if report['file'] != 'plateau_whitehead_pilot.json' for r in report['rows'] if r['same_length_rank_improvement']]
    require(ranks == ['aca_109', 'aca_111'], 'same-length rank gains differ')
    return {'status': 'PASS', 'reports': outputs, 'distinct_rewrite_ids': 124,
            'length_gain_ids': [r['name'] for r in gains], 'new_total_from_rewrite': 2177,
            'same_length_rank_improvement_ids': ranks,
            'physical_rewrite_units': outputs[0]['physical_work_units'] + outputs[2]['physical_work_units'],
            'separate_whitehead_pilot_units': outputs[1]['physical_work_units']}


def planted():
    import plateau
    seed = ((5,), (2, 5, 5, 5, 5, 5), (-5, -5, 9, -5, -5))
    verify.independent.check_tuple(seed)
    # Singleton5 kills5; the second relator then kills2; the third kills9.
    first_projection = {2: (2,), 5: (), 9: (9,)}
    require(verify.image(seed[1], first_projection) == (2,), 'planted triviality projection failed')
    require(verify.image(seed[2], {2: (), 5: (), 9: (9,)}) == (9,), 'planted terminal projection failed')
    candidates, charged = plateau.rewrite_candidates(seed, 48)
    wrapped = []
    for endpoint, events in candidates:
        require(len(events) == 1, 'planted rewrite unexpectedly multi-event')
        event = events[0]
        require(verify.verify_event(event, known_trivial=True) == words(endpoint), 'planted candidate replay differs')
        check_rule(event)
        rule = event['rule']
        if event['target'] == 2 and rule['target_cut'] + len(rule['left']) > len(seed[2]):
            wrapped.append(event)
    require(len(candidates) == 10 and charged == 25 and len(wrapped) == 4, 'planted endpoint-rich enumeration changed')
    selected = next(e for e in wrapped if e['rule']['left'] == (-5, -5, -5, -5) and e['rule']['right'] == (2, 5))
    require(selected['factors'][0]['sign'] == 1 and selected['rule']['target_cut'] == 3, 'selected wrapping donor convention differs')
    require(selected['raw_target_after'] == (-5, -5, 9, 2, 5, 5, 5), 'selected wrapped raw endpoint differs')
    corrupted = deepcopy(selected)
    corrupted['factors'][0]['sign'] *= -1
    failures = 0
    try:
        verify.verify_event(corrupted, known_trivial=True)
    except AssertionError:
        failures += 1
    missing_frame = deepcopy(selected)
    target = seed[2]
    rule = selected['rule']
    rotated = target[rule['target_cut']:] + target[:rule['target_cut']]
    missing_frame['raw_target_after'] = free(rule['right'] + rotated[len(rule['left']):])
    try:
        verify.verify_event(missing_frame, known_trivial=True)
    except AssertionError:
        failures += 1
    require(failures == 2, 'corruption control accepted wrong sign or forgotten rotation frame')
    return {'status': 'PASS', 'initial': seed, 'initial_rank': 3,
            'generator_ids': [2, 5, 9], 'known_triviality_proof': 'Relator5 kills generator5, then donor kills2, then target kills9.',
            'matched_rewrites_evaluated': charged, 'distinct_endpoints_replayed': len(candidates),
            'wrapping_endpoints_replayed': len(wrapped), 'wrong_sign_and_unrestored_frame_rejected': failures,
            'selected_wrapping_event': selected, 'census_rows_searched': 0}


def main():
    result = {'status': 'PASS', 'saved_records': saved_reports(), 'planted_control': planted(),
              'plateau_sha256': verify.sha(HERE / 'plateau.py'), 'verifier_sha256': verify.sha(HERE / 'verify.py'),
              'audit_script_sha256': verify.sha(Path(__file__)), 'baseline_sha256': verify.BASELINE_SHA256,
              'scope': 'Independent algebra and saved-path replay; no census searches, no frontier completeness claim.'}
    (HERE / 'verification_plateau.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'length_gain_ids': result['saved_records']['length_gain_ids'],
                      'new_total': 2177, 'same_length_rank_improvement_ids': result['saved_records']['same_length_rank_improvement_ids'],
                      'planted_endpoints_replayed': result['planted_control']['distinct_endpoints_replayed']}, indent=2))


if __name__ == '__main__':
    main()
