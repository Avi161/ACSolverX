"""Mutation controls and exact CSV/CURRENT joins for the flat certificate export."""
from copy import deepcopy
import csv
import json
from pathlib import Path

import export_paths as export
import verify

HERE = Path(__file__).resolve().parent


def rejected(action):
    try:
        action()
    except AssertionError:
        return True
    return False


def main():
    path = export.OUT / 'all124_stable_composite.jsonl'
    manifest = json.loads((export.OUT / 'manifest.json').read_text())
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    snapshot = json.loads((export.OUT / manifest['current_snapshot']).read_text())
    verify.require(verify.sha(path) == manifest['certificate_sha256'] and verify.sha(export.OUT / manifest['current_snapshot']) == manifest['current_snapshot_sha256'], 'export file/snapshot hash differs')
    with (export.ROOT / 'data/ms_unsolved_reps/aca_124_best.csv').open(newline='') as handle:
        starts = {r['name']: verify.parse_saved_strings([r['r1'], r['r2']]) for r in csv.DictReader(handle)}
    targets = {r['name']: r for r in snapshot['rows']}
    verify.require({r['name'] for r in rows} == set(starts) == set(targets) and len(rows) == 124, 'export source/target IDs differ')
    checked_segments = 0
    for row in rows:
        verify.require(verify.words(row['initial']) == starts[row['name']], 'export initial words differ from exact saved CSV')
        verify.require(export.replay_record(row) == verify.words(targets[row['name']]['words']), 'export target words differ from pinned CURRENT')
        for segment in row['lineage_segments']:
            first, stop = segment['first_event_index'], segment['past_last_event_index']
            before = row['initial'] if first == 0 else row['events'][first - 1]['after']
            after = row['initial'] if stop == 0 else row['events'][stop - 1]['after']
            verify.require(segment['boundary_before'] == before and segment['boundary_after'] == after, 'lineage segment boundary index differs')
            verify.require(manifest['sources'][segment['source_file']]['sha256'] == segment['source_sha256'], 'lineage segment source hash differs')
            checked_segments += 1
    events = [e for r in rows for e in r['events']]
    mutations = []
    defining = next(e for e in events if e['kind'] == 'export_defining_template_composite' and 'literal_cuts' in e)
    value = deepcopy(defining); value['after'] = value['after'][1:]
    mutations.append(('omitted_defining_relator', lambda e=value: export.replay_event(e)))
    value = deepcopy(defining); value['rows'][0]['template'][0] *= -1
    mutations.append(('wrong_template_sign', lambda e=value: export.replay_event(e)))
    value = deepcopy(defining); value['literal_cuts'][0] = len(value['before'][0])
    mutations.append(('invalid_rotation_cut', lambda e=value: export.replay_event(e)))
    value = deepcopy(defining); value['required_hypothesis'] = 'determinant one only'
    mutations.append(('determinant_in_place_of_triviality', lambda e=value: export.replay_event(e)))
    equivalent = next(e for e in events if e['kind'] == 'export_relator_equivalence')
    value = deepcopy(equivalent); value['rows'][1]['input_index'] = value['rows'][0]['input_index']
    mutations.append(('duplicated_relator_in_equivalence', lambda e=value: export.replay_event(e)))
    basis = next(e for e in events if e['kind'] == 'export_basis_map_composite')
    value = deepcopy(basis); next(iter(value['inverse_images'].values()))[0] *= -1
    mutations.append(('corrupted_basis_inverse', lambda e=value: export.replay_event(e)))
    elementary = next(e for e in events if e['kind'] == 'export_ordinary_elementary' and e['move']['op'] == 'AC2')
    value = deepcopy(elementary); value['move']['donor'] = value['move']['target']
    mutations.append(('self_donor_elementary_move', lambda e=value: export.replay_event(e)))
    value = deepcopy(next(r for r in rows if len(r['events']) > 1)); value['events'][1]['before'][0][0] *= -1
    mutations.append(('discontinuous_saved_suffix', lambda r=value: export.replay_record(r)))
    value = deepcopy(rows[0]); value['endpoint'][0][0] *= -1
    mutations.append(('wrong_final_boundary', lambda r=value: export.replay_record(r)))
    result = []
    for label, action in mutations:
        verify.require(rejected(action), 'export corruption was accepted: ' + label)
        result.append(label)
    source_check = export.Exporter(export.OUT / manifest['current_snapshot'])
    chosen = next(r for r in source_check.table['rows'] if r['name'] == 'aca_7')
    original = source_check.prior_witnesses['aca_7']['source_pointer']
    source_check.prior_witnesses['aca_7']['source_pointer'] = 'data/ms_unsolved_reps/aca_124_best.csv#name=aca_0'
    verify.require(rejected(lambda: source_check.export_row(chosen)), 'stale prior source pointer was accepted')
    source_check.prior_witnesses['aca_7']['source_pointer'] = original
    output = {'status': 'PASS', 'rows_joined_to_exact_saved_rank2_and_CURRENT_words': 124,
              'lineage_segments_checked': checked_segments, 'rejected_corruptions': result + ['stale_prior_source_pointer'],
              'flat_events_replayed': len(events), 'source_total': sum(r['initial_length'] for r in rows),
              'endpoint_total': sum(r['endpoint_length'] for r in rows),
              'certificate_sha256': verify.sha(path), 'manifest_sha256': verify.sha(export.OUT / 'manifest.json'),
              'script_sha256': verify.sha(Path(__file__)), 'exporter_sha256': verify.sha(HERE / 'export_paths.py'),
              'census_searches': 0}
    (HERE / 'verification_export_checks.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
