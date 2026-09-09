"""Independent verification of a census result directory.

Recomputes everything from the shard JSONL files and the manifest rather than
trusting SUMMARY.json:

* the input file hash matches the manifest and the settled AC19 hash;
* the shards cover [0, population) exactly once, names are unique and equal,
  in order, to the input names;
* every charge is <= budget, every solved row is verified, no row has an error;
* totals (solved, verified, units, elementary moves, clocks) recomputed from
  the rows agree with SUMMARY.json;
* the manifest's source and table hashes match the files on disk now.

Usage: PYTHONPATH=. python3 -m research.residual_20260909.verify_bundle \
           --result-dir results/heuristic_search/<dir> [--input data/AC19_extended_aut_min.csv]
Exit status 0 only when every check passes.
"""
import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AC19_SHA256 = '7e220253bd0d950378d6ca6944be46ff4b77e49f30067b9ff6c6c6da82f64ae2'


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--result-dir', required=True)
    parser.add_argument('--input', default='data/AC19_extended_aut_min.csv')
    args = parser.parse_args(argv)
    out = ROOT / args.result_dir
    failures = []

    def check(cond, msg):
        if not cond:
            failures.append(msg)
        print(('ok   ' if cond else 'FAIL ') + msg)

    manifests = sorted(out.glob('manifest_*.json'))
    check(len(manifests) == 1, f'exactly one manifest ({len(manifests)} found)')
    manifest = json.loads(manifests[0].read_text())
    input_path = ROOT / args.input
    input_hash = sha256(input_path)
    check(input_hash == AC19_SHA256, 'input sha256 is the settled AC19 hash')
    check(manifest['input_sha256'] == input_hash, 'manifest input sha256 matches the input file')
    with open(input_path, newline='') as stream:
        names = [row['name'] for row in csv.DictReader(stream)]
    population = len(names)
    check(population == 72779 and len(set(names)) == population, 'input has 72,779 unique names')
    check(manifest['offset'] == 0 and manifest['end'] == population, 'manifest covers [0, population)')
    budget = manifest['budget']

    shards = sorted(out.glob('rows_*.jsonl'))
    check(not list(out.glob('*.partial')), 'no .partial shard left behind')
    covered = []
    rows = []
    for shard in shards:
        m = re.fullmatch(r'rows_(\d+)_(\d+)\.jsonl', shard.name)
        start, stop = int(m.group(1)), int(m.group(2))
        covered.append((start, stop))
        with open(shard) as stream:
            shard_rows = [json.loads(line) for line in stream]
        check(len(shard_rows) == stop - start, f'{shard.name}: {stop - start} rows')
        rows.extend(shard_rows)
    covered.sort()
    contiguous = covered and covered[0][0] == 0 and covered[-1][1] == population and all(
        covered[i][1] == covered[i + 1][0] for i in range(len(covered) - 1))
    check(contiguous, f'{len(covered)} shards tile [0, {population}) exactly once')
    check([r['name'] for r in rows] == names, 'row names equal the input names, in order')
    check(len({r['name'] for r in rows}) == len(rows), 'row names are unique')

    solved = sum(1 for r in rows if r.get('solved'))
    verified = sum(1 for r in rows if r.get('verified'))
    errors = sum(1 for r in rows if r.get('error'))
    units = sum(int(r['nodes_explored']) for r in rows)
    max_units = max(int(r['nodes_explored']) for r in rows)
    moves = sum(int(r.get('elementary_count') or 0) for r in rows)
    check(errors == 0, f'zero rows with an error ({errors})')
    check(max_units <= budget, f'max charge {max_units} <= budget {budget}')
    check(solved == verified, f'solved == verified ({solved} == {verified})')
    check(all(r.get('verified') for r in rows if r.get('solved')), 'every solved row carries an independent replay')
    check(all(int(r.get('elementary_count') or 0) > 0 for r in rows if r.get('solved')),
          'every solved row has a non-empty elementary certificate')
    unsolved = [r['name'] for r in rows if not r.get('solved')]
    print(f'     rows {len(rows)}  solved {solved}  unsolved {len(unsolved)}  units {units}  '
          f'max {max_units}  elementary moves {moves}')

    summary_path = out / 'SUMMARY.json'
    if summary_path.exists():
        summary = json.loads(summary_path.read_text())
        check(summary['rows'] == len(rows) and summary['solved'] == solved
              and summary['verified'] == verified and summary['nodes'] == units
              and summary['elementary_moves'] == moves and summary['max_nodes_explored'] == max_units,
              'SUMMARY.json totals equal the totals recomputed from the shards')
        for clock in ('search_wall', 'certificate_wall'):
            total = sum(float(r.get(clock) or 0) for r in rows)
            check(abs(total - summary['clocks'][clock]) < 1e-6 * max(1, total),
                  f'SUMMARY.json {clock} {summary["clocks"][clock]:.1f}s recomputed from rows')
    else:
        check(False, 'SUMMARY.json present')

    for group in ('source_sha256', 'table_sha256'):
        stale = [p for p, h in manifest[group].items() if not (ROOT / p).exists() or sha256(ROOT / p) != h]
        check(not stale, f'manifest {group}: {len(manifest[group])} files match the tree now'
              + (f' (stale: {stale})' if stale else ''))
    print('policy', manifest['policy'], 'budget', budget, 'git_head', manifest.get('git_head'))
    print('RESULT:', 'PASS' if not failures else f'FAIL ({len(failures)} checks)')
    return 0 if not failures else 1


if __name__ == '__main__':
    sys.exit(main())
