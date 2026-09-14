"""Merge verified witness prefixes without changing the frozen U124 census."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import io
import json
from pathlib import Path

import verify

HERE = Path(__file__).resolve().parent


def build(paths):
    baseline = verify.load_baseline()
    original = json.loads(verify.BASELINE_FILE.read_text())['rows']
    best, inputs = {}, {}
    for row in original:
        name = row['name']
        exact = baseline[name]
        best[name] = {'name': name, 'archival_initial_length': row['archival_initial_length'],
                      'saved_rank2_length': row['saved_rank2_length'], 'phase_initial_length': exact['length'],
                      'best_length': exact['length'], 'best_rank': exact['rank'], 'words': exact['words'],
                      'solved': False, 'witness_file': '../rank_unbounded_20260912/all124.json',
                      'witness_pointer': row['witness_pointer'], 'witness_prefix_events': None,
                      'certificate_kind': 'theorem_backed_stable_composite'}
    total_work, cpu, wall, count = 0, 0.0, 0.0, 0
    for path in paths:
        path = Path(path)
        report = json.loads(path.read_text())
        inputs[str(path.relative_to(HERE))] = verify.sha(path)
        rows = report['rows']
        if len({row['name'] for row in rows}) != len(rows):
            raise AssertionError('duplicate IDs in one experiment')
        for index, row in enumerate(rows):
            checked = verify.verify_record(row, baseline)
            count += 1
            total_work += row.get('total_units', 0)
            cpu += row.get('cpu_seconds', 0)
            wall += row.get('wall_seconds', 0)
            name = row['name']
            current = best[name]
            candidate = (checked['best_prefix_length'], checked['best_prefix_rank'])
            if candidate < (current['best_length'], current['best_rank']):
                current.update(best_length=candidate[0], best_rank=candidate[1],
                               words=checked['best_certified'], solved=checked['solved_at_certified_prefix'],
                               witness_file=str(path.relative_to(HERE)), witness_pointer=f'#/rows/{index}',
                               witness_prefix_events=checked['best_prefix_event_count'],
                               certificate_kind=checked['certificate_scope'])
    rows = list(best.values())
    for row in rows:
        row['phase_gain'] = row['phase_initial_length'] - row['best_length']
        row['gain_from_saved_rank2'] = row['saved_rank2_length'] - row['best_length']
        row['all_relators_counted'] = True
    summary = {'rows': len(rows), 'solved': sum(row['solved'] for row in rows),
               'archival_total': sum(r['archival_initial_length'] for r in rows),
               'saved_rank2_total': sum(r['saved_rank2_length'] for r in rows),
               'phase_initial_total': sum(r['phase_initial_length'] for r in rows),
               'best_total': sum(r['best_length'] for r in rows),
               'new_gain_ids': [r['name'] for r in rows if r['phase_gain'] > 0],
               'strictly_shorter_than_saved_rank2': sum(r['gain_from_saved_rank2'] > 0 for r in rows),
               'best_rank_counts': {str(k): v for k, v in sorted(Counter(r['best_rank'] for r in rows).items())},
               'physical_experiment_rows': count, 'physical_charged_units': total_work,
               'search_cpu_seconds': cpu, 'search_wall_seconds': wall,
               'work_scope': 'Sum of included executed probe records; prior seed discovery costs are historical and excluded.',
               'fully_expanded_stable_certificates': False}
    if summary['rows'] != 124 or summary['phase_initial_total'] != 2180:
        raise AssertionError('census baseline changed')
    return {'baseline_sha256': verify.BASELINE_SHA256, 'inputs': inputs,
            'summary': summary, 'rows': rows}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('inputs', nargs='+')
    parser.add_argument('--prefix', default='CURRENT')
    args = parser.parse_args()
    report = build([Path(p).resolve() for p in args.inputs])
    prefix = HERE / args.prefix
    destination = prefix.with_suffix('.json')
    serialized = json.dumps(report, indent=2) + '\n'
    destination.write_text(serialized)
    if json.loads(destination.read_text()) != json.loads(serialized):
        raise AssertionError('scoreboard read-back differs')
    columns = ['name', 'archival_initial_length', 'saved_rank2_length', 'phase_initial_length',
               'best_length', 'best_rank', 'phase_gain', 'solved', 'witness_file',
               'witness_pointer', 'witness_prefix_events']
    text = io.StringIO()
    writer = csv.DictWriter(text, fieldnames=columns, extrasaction='ignore', lineterminator='\n')
    writer.writeheader()
    writer.writerows(report['rows'])
    prefix.with_suffix('.csv').write_text(text.getvalue())
    summary = report['summary']
    lines = ['# Current verified U124 endpoints', '',
             f"Solved: **{summary['solved']}/124**. Total length: **{summary['best_total']}**, "
             f"from phase baseline2180 and saved rank2 baseline2356.", '',
             'Every defining relator is included. Witnesses use exact ordinary AC composites, '
             'ambient basis changes and theorem-backed Lemma11 additions/removals. '
             'They are not all expanded into individual stabilized elementary moves.', '',
             '| ID | Archival initial | Saved rank2 | Phase initial | Best total | Rank | Solved |',
             '|---|---:|---:|---:|---:|---:|:---:|']
    for row in report['rows']:
        values = [row['name'], row['archival_initial_length'], row['saved_rank2_length'],
                  row['phase_initial_length'], row['best_length'], row['best_rank'],
                  'yes' if row['solved'] else 'no']
        lines.append('| ' + ' | '.join(map(str, values)) + ' |')
    prefix.with_suffix('.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
