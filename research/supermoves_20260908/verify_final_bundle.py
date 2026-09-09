"""Verify the extracted snapshot hashes; optionally replay all final certificates."""
import argparse
import fnmatch
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--replay', action='store_true')
    args = parser.parse_args()
    manifest = json.loads((HERE / 'FINAL_BUNDLE_MANIFEST.json').read_text())
    for directory in manifest.get('directories', []):
        if not (ROOT / directory).is_dir():
            raise ValueError('missing structural directory: ' + directory)
    for name, entry in manifest['files'].items():
        path = (ROOT / name).resolve()
        if not path.is_relative_to(ROOT):
            raise ValueError('manifest path escapes snapshot')
        content = path.read_bytes()
        if len(content) != entry['bytes'] or hashlib.sha256(content).hexdigest() != entry['sha256']:
            raise ValueError('snapshot mismatch: ' + name)
    result = dict(hashes_verified=len(manifest['files']))
    if args.replay:
        from research.supermoves_20260908.certificate_decoder import replay_elementary
        groups = [('final_development*.jsonl', 200, 191),
                  ('final_holdout*.jsonl', 64, 59),
                  ('final_s20_control*.jsonl', 64, 18),
                  ('final_compact_development*.jsonl', 200, 191),
                  ('final_compact_holdout*.jsonl', 64, 59),
                  ('final_compact_s20*.jsonl', 64, 18)]
        result['cohorts'] = []
        for pattern, expected_rows, expected_solves in groups:
            seen = set()
            solved = elementary = 0
            paths = [ROOT / name for name in manifest['files'] if fnmatch.fnmatch(Path(name).name, pattern)]
            for path in sorted(paths):
                for line in path.open():
                    record = json.loads(line)
                    name = record['name']
                    if name in seen:
                        raise ValueError('duplicate final row: ' + name)
                    seen.add(name)
                    if record.get('solved', record.get('result', {}).get('solved')):
                        moves = record['elementary_moves']
                        if replay_elementary(record['pair'], moves) != ['x', 'y']:
                            raise ValueError('certificate failed: ' + name)
                        solved += 1
                        elementary += len(moves)
            if len(seen) != expected_rows or solved != expected_solves:
                raise ValueError('final cohort count mismatch: ' + pattern)
            result['cohorts'].append(dict(pattern=pattern, rows=len(seen), solved=solved, elementary_moves=elementary))
    print(json.dumps(result))


if __name__ == '__main__':
    main()
