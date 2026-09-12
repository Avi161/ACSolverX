"""Pin this research deliverable without changing Git or frozen census files."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DESTINATION = HERE / 'DELIVERY_MANIFEST.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def files():
    return sorted(path for path in HERE.rglob('*') if path.is_file()
                  and path != DESTINATION and '__pycache__' not in path.parts
                  and path.suffix != '.pyc' and not path.name.endswith('.partial'))


def check(report):
    expected = {str(path.relative_to(HERE)) for path in files()}
    if set(report['artifacts']) != expected:
        raise AssertionError('deliverable file set changed')
    for name, metadata in report['artifacts'].items():
        path = HERE / name
        if digest(path) != metadata['sha256'] or path.stat().st_size != metadata['bytes']:
            raise AssertionError(f'deliverable changed: {name}')
    current = json.loads((HERE / 'CURRENT.json').read_text())
    if current['summary'] != report['current_summary']:
        raise AssertionError('summary differs from current table')
    print(json.dumps({'status': 'PASS', 'files': len(expected),
                      'rows': current['summary']['rows'], 'best_total': current['summary']['best_total'],
                      'solved': current['summary']['solved']}, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.check:
        check(json.loads(DESTINATION.read_text()))
        return
    current = json.loads((HERE / 'CURRENT.json').read_text())
    report = {'schema': 'u124_three_hour_delivery_v1',
              'checkpoint_utc': datetime.now(timezone.utc).isoformat(),
              'requested_window_utc': ['2026-09-12T12:59:28Z', '2026-09-12T15:59:28Z'],
              'worktree_branch': 'codex/theory-patterns-3h',
              'publication': 'Local research files; this phase has not been committed or pushed.',
              'current_summary': current['summary'],
              'retained_high_rank_summary': json.loads((HERE / 'HIGH_RANK_TRIANGLES.json').read_text())['summary'],
              'retained_rank_flip_summary': json.loads((HERE / 'HIGH_RANK_FLIPS.json').read_text())['summary'],
              'certificate_scope': 'Theorem-backed stable composites, not fully expanded elementary stabilized paths.',
              'artifacts': {str(path.relative_to(HERE)): {'sha256': digest(path), 'bytes': path.stat().st_size}
                            for path in files()}}
    DESTINATION.write_text(json.dumps(report, indent=2) + '\n')
    check(json.loads(DESTINATION.read_text()))


if __name__ == '__main__':
    main()
