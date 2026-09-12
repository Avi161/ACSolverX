"""Rebuild the verified table and incremental experiment index from saved probes."""
import json
from pathlib import Path
import sys

import scoreboard
import verify

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RECORD_FIELDS = {'name', 'initial', 'events', 'endpoint', 'total_units', 'baseline_sha256'}


def reports():
    for path in sorted(HERE.glob('*.json')):
        data = json.loads(path.read_text())
        if not isinstance(data, dict):
            continue
        rows = data.get('rows')
        if isinstance(rows, list) and rows and all(
                isinstance(row, dict) and RECORD_FIELDS <= row.keys() for row in rows):
            yield path, data


def main():
    baseline = verify.load_baseline()
    experiments = list(reports())
    sys.argv = ['scoreboard.py', *[str(path) for path, _ in experiments]]
    scoreboard.main()
    index = []
    for path, report in experiments:
        incumbent = {name: row['length'] for name, row in baseline.items()}
        for seed, expected in report.get('seed_hashes', {}).items():
            source = ROOT / seed
            if verify.sha(source) != expected:
                raise AssertionError(f'seed hash changed: {seed}')
            for row in json.loads(source.read_text())['rows']:
                checked = verify.verify_record(row, baseline)
                incumbent[row['name']] = min(incumbent[row['name']], checked['best_prefix_length'])
        rows = report['rows']
        gains = {row['name']: incumbent[row['name']] - row['best_length']
                 for row in rows if row['best_length'] < incumbent[row['name']]}
        module = report.get('module')
        if module is None:
            module = 'plateau' if all('mode' in row for row in rows) else path.stem
            if path.name == 'flow_exact_diagnostic.json':
                module = 'flow_diagnostic / theory_flow_exact'
        index.append({'file': path.name, 'sha256': verify.sha(path),
                      'module': module, 'rows': len(rows),
                      'new_gains_beyond_imported_seeds': gains,
                      'charged_units': sum(row['total_units'] for row in rows),
                      'cpu_seconds': sum(row['cpu_seconds'] for row in rows),
                      'wall_seconds': sum(row['wall_seconds'] for row in rows),
                      'maximum_generated_rank': max(row.get('maximum_rank', len(row['endpoint'])) for row in rows)})
    (HERE / 'EXPERIMENT_INDEX.json').write_text(json.dumps(index, indent=2) + '\n')
    lines = ['# Executed bounded algebraic probes', '',
             'Gains below compare with the frozen phase baseline and every imported seed for that run. '
             'They are not necessarily first discoveries across separate runs. Each row receives at most '
             '1,000 newly charged algebraic checks; these are not equivalent to heap pops. '
             'Times exclude verification, cooldown and historical seed discovery.', '',
             'The separate `primitive_search_results_corrected.json` records two bounded S20 continuations '
             'and is excluded from this algebraic-probe index.', '',
             '| Result file | Rows | Gains beyond seeds | Units | CPU s | Wall s | Max generated rank |',
             '|---|---:|---|---:|---:|---:|---:|']
    for row in index:
        gains = ', '.join(f'{name} (+{gain})' for name, gain in row['new_gains_beyond_imported_seeds'].items()) or 'none'
        lines.append(f"| [{row['file']}]({row['file']}) | {row['rows']} | {gains} | "
                     f"{row['charged_units']} | {row['cpu_seconds']:.6f} | {row['wall_seconds']:.6f} | "
                     f"{row['maximum_generated_rank']} |")
    (HERE / 'EXPERIMENT_INDEX.md').write_text('\n'.join(lines) + '\n')
    print('Indexed', len(index), 'saved experiments; all seed hashes and certificates verified.')


if __name__ == '__main__':
    main()
