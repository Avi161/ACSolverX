"""Independent sequential Schreier stages and one exact U124 detour."""
from copy import deepcopy
import json
from pathlib import Path

import exchange_schreier as schreier
import lemma11
import verify


HERE = Path(__file__).resolve().parent


def replay_stages(initial, events):
    current = verify.words(initial)
    labels = [('original', i) for i in range(len(current))]
    definitions, rewrites, staged_count, charged = None, None, 0, 0
    for event in events:
        verify.require(verify.words(event['before']) == current, 'Schreier path discontinuity')
        if event.get('method') == 'triangular_schreier_dictionary_stage':
            staged_count += 1
            if definitions is None:
                definitions = [(g, verify.word(w)) for g, w in event['schreier_triangular_definitions']]
                rewrites = event['schreier_rewrites']
            verify.require(event['schreier_stage'] == staged_count and event['schreier_stages'] == len(definitions), 'Schreier chain stage sequence differs')
            verify.require((event['helpers'][0], verify.word(event['defining_words'][0])) == definitions[staged_count - 1], 'Schreier stage does not use the planned triangular definition')
            verify.require([tuple(row['schreier_row_label']) for row in event['rows']] == labels, 'Schreier original/definition labels lost during sorting')
            raw_labels = [('definition', event['helpers'][0])] + labels
            labels = [raw_labels[row['input_index']] for row in event['normalization']]
            charged += event['charged_units']
        current = verify.verify_event(event, known_trivial=True)
        if staged_count and staged_count == len(definitions) and event.get('method') == 'triangular_schreier_dictionary_stage':
            for value, label in zip(current, labels):
                if label[0] == 'original':
                    verify.require(value == verify.independent.representative(verify.word(rewrites[label[1]]['template'])), 'final original row differs from full Schreier template')
    verify.require(staged_count == len(definitions), 'Schreier chain incomplete')
    r, h = len(initial), len(definitions)
    expected_charge = 1 + 3 * verify.size(initial) + r + h * (r + 1) + h * (h - 1) // 2
    verify.require(charged == expected_charge, 'Schreier total stage cost differs')
    return current, charged


def main():
    source = HERE / 'exchange_schreier_control.json'
    saved = json.loads(source.read_text())
    verify.require(saved['source_sha256'] == verify.sha(HERE / 'exchange_schreier.py'), 'saved Schreier control source changed')
    checked = []
    for row in saved['controls']:
        endpoint, charged = replay_stages(row['before'], row['events'])
        verify.require(endpoint == verify.words(row['after']) and [len(row['before']), len(row['dictionary']), len(endpoint)] == row['ranks'], 'saved Schreier control endpoint/ranks differ')
        verify.require([verify.size(row['before']), verify.size(row['dictionary']), verify.size(endpoint)] == row['lengths'], 'saved Schreier control lengths differ')
        verify.require(charged == row['metadata']['required_dictionary_units'], 'saved Schreier dictionary work differs')
        if row['family'] == 'all_heights' and row['index'] == 10:
            first_stage = row['events'][0]
            emitted = {abs(x) for rewrite in first_stage['schreier_rewrites'] for step in rewrite['steps'] for x in step['emitted']}
            verify.require({g for g, _ in first_stage['schreier_triangular_definitions']} <= emitted, 'dense index10 control does not use every helper')
        checked.append({'family': row['family'], 'index': row['index'], 'ranks': row['ranks'], 'lengths': row['lengths'], 'dictionary_units': charged, 'status': 'PASS'})
    first = saved['controls'][0]['events'][0]
    corruptions = []
    altered = deepcopy(first)
    altered['schreier_rewrites'][0]['steps'][0]['coset_after'] += 1
    corruptions.append(altered)
    altered = deepcopy(first)
    altered['schreier_full_images'][str(first['helpers'][0])] = [first['schreier_axis']]
    corruptions.append(altered)
    altered = deepcopy(first)
    altered['schreier_rewrites'][0]['negative_residue_carry'] = not altered['schreier_rewrites'][0]['negative_residue_carry']
    corruptions.append(altered)
    rejected = 0
    for altered in corruptions:
        try:
            verify.verify_event(altered, known_trivial=True)
        except AssertionError:
            rejected += 1
    verify.require(rejected == 3, 'corrupted Schreier transition metadata accepted')
    signed_residue_checks = 0
    for index in (2, 3, 10):
        power_helper, definitions, cosets, raw_images = schreier.dictionary((101, 307), 101, index)
        images = {101: (101,), 307: (307,)}
        for helper, defining in definitions:
            images[helper] = verify.image(defining, images)
        verify.require(images == raw_images, 'signed-residue dictionary full images differ')
        for sign in (-1, 1):
            original = (sign * 101,) * (index + 1) + (307,) + (-sign * 101,) * index
            template, rewrite = schreier.rewrite(original, 101, index, power_helper, cosets, raw_images)
            verify.require(verify.image(template, images) == original and rewrite['signed_residue'] == sign and sum(abs(x) == 101 for x in template) == 1, 'signed residual singleton identity differs')
            for step in rewrite['steps']:
                left = verify.free((101,) * step['coset_before'] + (step['letter'],))
                right = verify.free(verify.image(step['emitted'], images) + (101,) * step['coset_after'])
                verify.require(left == right, 'signed local Schreier transition differs')
            signed_residue_checks += 1
    high = verify.normalized(((101, 307), (307,), (10**20,)))
    high_after, high_events, high_charge, high_metadata = schreier.build(high, 101, 3, 1000)
    verify.require(replay_stages(high, high_events)[0] == high_after and len(high_after) == 8, 'large-label rank3 Schreier chain differs')
    blocked = schreier.build(high, 101, 10**20, 1000)
    verify.require(blocked[:3] == (None, [], 1), 'large-index budget preflight allocates or mischarges')
    baseline = verify.load_baseline()
    initial = verify.normalized(baseline['aca_0']['words'])
    dictionary, events, charged, metadata = schreier.build(initial, 1, 10, 1000)
    verify.require(charged == 132 and len(dictionary) == 12, 'real U124 dictionary rank/work differs')
    target = next(i for i, word in enumerate(dictionary) if sum(abs(x) == 1 for x in word) == 1)
    endpoint, removal = lemma11.remove_one(dictionary, target, 1)
    events = events + [removal]
    verify.require(replay_stages(initial, events)[0] == endpoint and len(endpoint) == 11, 'real U124 rank11 detour differs')
    record = {'name': 'aca_0', 'baseline_sha256': verify.BASELINE_SHA256, 'source_key': 'current_best',
              'source_pointer': baseline['aca_0']['source_pointers']['current_best'], 'initial': initial,
              'events': events, 'endpoint': endpoint, 'dictionary_units': charged, 'removal_units': 1,
              'work_scope': 'One exact requested dictionary construction and removal; no presentation search.'}
    verification = verify.verify_record(record, baseline)
    (HERE / 'verification_schreier_aca0_witness.json').write_text(json.dumps(record, indent=2) + '\n')
    result = {'status': 'PASS', 'saved_control_replays': checked, 'rejected_corruptions': rejected,
              'signed_residual_singletons_checked': signed_residue_checks, 'dense_index10_all_helpers_used': True,
              'high_label_chain': {'input_rank': 3, 'dictionary_rank': 8, 'dictionary_units': high_charge},
              'huge_index_preflight_units': 1, 'real_U124_detour': verification,
              'real_dictionary_units': charged, 'real_removal_units': 1,
              'source_control_sha256': verify.sha(source), 'source_sha256': verify.sha(HERE / 'exchange_schreier.py'),
              'verifier_sha256': verify.sha(HERE / 'verify.py'), 'script_sha256': verify.sha(Path(__file__)), 'census_searches': 0}
    (HERE / 'verification_schreier.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'saved_controls': checked, 'real_U124_final_rank': len(endpoint), 'real_U124_final_length': verify.size(endpoint), 'real_dictionary_units': charged, 'rejected_corruptions': rejected}, indent=2))


if __name__ == '__main__':
    main()
