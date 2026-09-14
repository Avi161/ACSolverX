"""Complete the AC1M per-row AC-move table over all 1,136,154 rows.

The raw run skips rows whose canonical form (rotation, inversion, relator order --
what the solver applies before doing anything) already appeared in an earlier record
file.  Such a row gets the identical run, hence the identical certificate and the
identical AC-move cost, so its cost is carried over from the row it matched rather
than recomputed.  Output columns: name, r1, r2, length, solved, stage, units,
ac_moves, stable, source ('run' or the file the cost came from)."""
from __future__ import annotations

import argparse
import csv
import gzip
import json
from pathlib import Path


def rows(path):
    op = gzip.open if str(path).endswith('.gz') else open
    with op(path, 'rt') as f:
        yield from csv.DictReader(f)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--table', required=True, help='the raw run table (rows actually run)')
    ap.add_argument('--skipped', required=True, help='the run .skipped.csv.gz')
    ap.add_argument('--from-tables', nargs='+', required=True,
                    help='acmoves tables of the earlier runs the skips point into')
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    cost = {}
    for p in args.from_tables:
        for r in rows(p):
            cost[r['name']] = (r['ac_moves'], r['stable'], Path(p).name)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    opener = gzip.open if out.name.endswith('.gz') else open
    n_run = n_join = n_miss = 0
    with opener(out, 'wt', newline='') as f:
        w = csv.writer(f)
        w.writerow(['name', 'r1', 'r2', 'length', 'solved', 'stage', 'units',
                    'ac_moves', 'stable', 'source'])
        for r in rows(args.table):
            n_run += 1
            w.writerow([r['name'], r['r1'], r['r2'], r['length'], r['solved'], r['stage'],
                        r['units'], r['ac_moves'], int(r['dyn'] not in ('', '0')), 'run'])
        for r in rows(args.skipped):
            hit = cost.get(r['as'])
            if hit is None:
                n_miss += 1
                continue
            n_join += 1
            w.writerow([r['name'], r['r1'], r['r2'], len(r['r1']) + len(r['r2']),
                        r['solved'], 'carried', r['units'], hit[0], hit[1], hit[2]])
    print(json.dumps(dict(run=n_run, carried=n_join, unmatched=n_miss, total=n_run + n_join)))


if __name__ == '__main__':
    main()
