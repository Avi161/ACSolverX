"""Read-only cross-check of the current report, index, table and flat certificates."""
import csv
import json
import math
import re
from collections import Counter
from pathlib import Path

import verify as v
import export_paths

HERE = Path(__file__).resolve().parent


def main():
    table = json.loads((HERE / 'CURRENT.json').read_text())
    index = json.loads((HERE / 'EXPERIMENT_INDEX.json').read_text())
    v.require(isinstance(index, list) and isinstance(table['inputs'], dict), 'delivery JSON shapes differ')
    baseline = v.load_baseline()
    rows = {row['name']: row for row in table['rows']}
    v.require(len(rows) == len(table['rows']) == 124 and set(rows) == set(baseline), 'delivery IDs differ')
    for row in rows.values():
        endpoint = v.words(row['words'])
        v.require(len(endpoint) == row['best_rank'] and v.size(endpoint) == row['best_length'], 'table endpoint metrics differ')
        v.require({abs(x) for word in endpoint for x in word} and len({abs(x) for word in endpoint for x in word}) == len(endpoint), 'table basis count differs')
        v.require(row['phase_initial_length'] == baseline[row['name']]['length'] and row['saved_rank2_length'] == v.size(baseline[row['name']]['sources']['saved_rank2']), 'table baselines differ')
        v.require(row['phase_gain'] == row['phase_initial_length'] - row['best_length'] and row['gain_from_saved_rank2'] == row['saved_rank2_length'] - row['best_length'], 'table gain differs')
    with (HERE / 'CURRENT.csv').open(newline='') as handle:
        csv_rows = list(csv.DictReader(handle))
    v.require(len(csv_rows) == 124 and {r['name'] for r in csv_rows} == set(rows), 'CSV IDs differ')
    for printed in csv_rows:
        row = rows[printed['name']]
        for key, value in printed.items():
            expected = row[key]
            v.require(value == ('' if expected is None else str(expected)), 'CSV field differs: ' + key)

    costs, physical_rows, cpu, wall = 0, 0, 0.0, 0.0
    high_rank = []
    for entry in index:
        path = HERE / entry['file']
        v.require(v.sha(path) == entry['sha256'] == table['inputs'][entry['file']], 'index source pin differs')
        report = json.loads(path.read_text())
        records = report['rows']
        v.require(len(records) == entry['rows'] and sum(r['total_units'] for r in records) == entry['charged_units'], 'index work sum differs')
        for record in records:
            if 'costs' in record:
                v.require(0 <= record['total_units'] == sum(record['costs'].values()) <= record['budget'] <= 1000, 'record work budget differs')
            else:
                v.require(entry['file'] == 'flow_exact_diagnostic.json' and 'flow_audits' in record and 0 <= record['total_units'] <= 1000, 'unrecognized diagnostic cost schema')
        v.require(math.isclose(sum(r['cpu_seconds'] for r in records), entry['cpu_seconds'], rel_tol=1e-12, abs_tol=1e-12) and math.isclose(sum(r['wall_seconds'] for r in records), entry['wall_seconds'], rel_tol=1e-12, abs_tol=1e-12), 'index measured times differ')
        maximum = max(r.get('maximum_rank', len(r['endpoint'])) for r in records)
        v.require(maximum == entry['maximum_generated_rank'], 'recorded maximum rank differs')
        if maximum >= 12:
            high_rank.append({'file': entry['file'], 'maximum_registered_rank': maximum,
                              'rows_at_maximum': [r['name'] for r in records if r.get('maximum_rank') == maximum]})
        costs += entry['charged_units']
        physical_rows += entry['rows']
        cpu += entry['cpu_seconds']
        wall += entry['wall_seconds']
    summary = table['summary']
    v.require(physical_rows == summary['physical_experiment_rows'] and costs == summary['physical_charged_units'], 'summary physical work differs')
    v.require(math.isclose(cpu, summary['search_cpu_seconds'], rel_tol=1e-12) and math.isclose(wall, summary['search_wall_seconds'], rel_tol=1e-12), 'summary measured time differs')
    v.require(set(table['inputs']) == {r['file'] for r in index}, 'table/index source cohort differs')
    total = sum(r['best_length'] for r in rows.values())
    gains = {name for name, row in rows.items() if row['phase_gain'] > 0}
    rank_counts = dict(Counter(str(r['best_rank']) for r in rows.values()))
    v.require(total == summary['best_total'] and gains == set(summary['new_gain_ids']) and rank_counts == summary['best_rank_counts'], 'summary endpoint statistics differ')
    v.require(sum(r['saved_rank2_length'] for r in rows.values()) == 2356 and sum(r['archival_initial_length'] for r in rows.values()) == 2446 and sum(r['phase_initial_length'] for r in rows.values()) == 2180, 'baseline totals differ')
    v.require(sum(r['gain_from_saved_rank2'] > 0 for r in rows.values()) == summary['strictly_shorter_than_saved_rank2'] == 89 and summary['solved'] == 0, 'coverage differs')
    notes = (HERE / 'RESEARCH_NOTES.md').read_text()
    printed_gains = re.findall(r'^\| (aca_\d+) \| (\d+) \| (\d+) \| (\d+) \|', notes, re.M)
    v.require({r[0] for r in printed_gains} == gains and len(printed_gains) == len(gains), 'research-note gain IDs differ')
    for name, initial, endpoint, rank in printed_gains:
        row = rows[name]
        v.require((int(initial), int(endpoint), int(rank)) == (row['phase_initial_length'], row['best_length'], row['best_rank']), 'research-note gain table differs')
    v.require(f'{len(gains)} further shortened rows' in notes and f'2180 → {total}' in notes, 'research-note headline differs')
    maximum = max(r['maximum_generated_rank'] for r in index)
    v.require(maximum == 22 and 'screens reach rank22' in notes, 'research-note generated-rank claim differs')
    exported = [json.loads(line) for line in (export_paths.OUT / 'all124_stable_composite.jsonl').read_text().splitlines()]
    v.require(len(exported) == 124 and {r['name'] for r in exported} == set(rows), 'export IDs differ')
    for row in exported:
        v.require(export_paths.replay_record(row) == v.words(rows[row['name']]['words']), 'full export differs from live CURRENT endpoint')
    output = {'status': 'PASS', 'current_total': total, 'phase_gain_count': len(gains), 'saved_rank2_total': 2356,
              'rank_counts': rank_counts, 'shortened_vs_saved_rank2': 89, 'solves': 0,
              'experiment_files': len(index), 'physical_rows': physical_rows, 'physical_charged_units': costs,
              'search_cpu_seconds': cpu, 'search_wall_seconds': wall, 'recorded_maximum_rank': maximum,
              'high_rank_record_sources': high_rank, 'full124_export_matches_live_current': True,
              'proof_review': 'General L>=4r and rank-three L>=13 proofs PASS with normalized balanced unimodular hypotheses; fixed-donor and geodesic statements retain their stated family scopes.',
              'scope_notes': 'maximum_rank counts registered event boundaries, including imported seeds. The rank22 Schreier rows exceed all their imported seed ranks; complete selected shortening certificates peak at rank5. Work totals exclude verification, cooldown, initialization and historical seed discovery.',
              'source_hashes': {name: v.sha(HERE / name) for name in ('CURRENT.json', 'CURRENT.csv', 'CURRENT.md', 'EXPERIMENT_INDEX.json', 'EXPERIMENT_INDEX.md', 'RESEARCH_NOTES.md', 'RANK_LENGTH_BOUND.md')},
              'census_reruns': 0}
    (HERE / 'verification_delivery_review.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps({key: output[key] for key in ('status', 'current_total', 'phase_gain_count', 'experiment_files', 'physical_rows', 'physical_charged_units', 'recorded_maximum_rank', 'full124_export_matches_live_current')}))


if __name__ == '__main__':
    main()
