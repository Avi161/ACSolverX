"""Run the final hybrid solver over an arbitrary presentation file or census at a fixed
unit budget and verify every certificate.

Sources: `--src` a flat integer file (one presentation per line, 2k slots, letters
1/-1/2/-2 = x/X/y/Y, 0 padding; `.gz` accepted), `--census` a CSV(.gz) with columns
name,r1,r2 (an Aut-minimal census), or `--pairs` a JSONL(.gz) of earlier records, of
which only the `name`, `r1` and `r2` fields are read (re-running a named subset at a
different budget).  Output: JSONL(.gz) records; with `--compact` the
per-row record drops the certificate unless the row is unsolved or needed at least
`--keep-above` units (the full certificate is still verified in-process before the row
is written)."""
from __future__ import annotations

import argparse
import collections
import csv
import gzip
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.ac_hashfree_cascade_20260914 import hfhybrid, verify  # noqa: E402
from research.ac_hashfree_cascade_20260914 import hfcascade  # noqa: E402
from research.ac_hashfree_cascade_20260914 import acmoves  # noqa: E402

LETTER = {1: 'x', -1: 'X', 2: 'y', -2: 'Y'}


def line_to_pair(line):
    v = [int(t) for t in line.strip().strip('()[]').split(',') if t.strip()]
    h = len(v) // 2
    assert 2 * h == len(v), len(v)
    return ''.join(LETTER[t] for t in v[:h] if t), ''.join(LETTER[t] for t in v[h:] if t)


def base_name(out):
    return out.name[:-len('.jsonl.gz')] if out.name.endswith('.jsonl.gz') else out.stem


def load_rows(args):
    if args.pairs:
        opener = gzip.open if args.pairs.suffix == '.gz' else open
        with opener(args.pairs, 'rt') as f:
            rows = [(r['name'], (r['r1'], r['r2'])) for r in (json.loads(l) for l in f if l.strip())]
    elif args.census:
        opener = gzip.open if args.census.suffix == '.gz' else open
        with opener(args.census, 'rt') as f:
            rows = [(r['name'], (r['r1'], r['r2'])) for r in csv.DictReader(f)]
    else:
        opener = gzip.open if args.src.suffix == '.gz' else open
        with opener(args.src, 'rt') as f:
            rows = [(f'{args.prefix}_{i}', line_to_pair(l)) for i, l in enumerate(x for x in f if x.strip())]
    if args.offset or args.limit:
        rows = rows[args.offset:args.offset + args.limit if args.limit else None]
    skipped = []
    if args.skip_from:
        # a row whose canonical form (rotation, inversion, relator order: what the solver
        # applies before doing anything) already appears in an earlier record file has
        # already been run, with the identical outcome; skip it and note where it was run
        seen = {}
        for path in args.skip_from:
            op = gzip.open if str(path).endswith('.gz') else open
            with op(path, 'rt') as f:
                for l in f:
                    r = json.loads(l)
                    seen.setdefault(hfcascade.canon_pair(r['r1'], r['r2']), (path.name, r['name'], r['solved'], r['units']))
        kept = []
        for name, pair in rows:
            hit = seen.get(hfcascade.canon_pair(*pair))
            if hit is None:
                kept.append((name, pair))
            else:
                skipped.append((name, pair[0], pair[1]) + hit)
        rows = kept
    return rows, skipped


def job(arg):
    (name, pair), params = arg
    t = time.perf_counter()
    res = hfhybrid.solve(pair, budget=params['budget'], penalty=params['penalty'], cap=params['cap'],
                         slack=params['slack'], dyn_max=params.get('dyn_max'), dyn_ratio=params.get('dyn_ratio'))
    seconds = time.perf_counter() - t
    rec = dict(name=name, r1=pair[0], r2=pair[1], length=len(pair[0]) + len(pair[1]),
               solved=res['solved'], stage=res['stage'], units=res['units'], path_length=res.get('path_length'),
               max_rank=res.get('max_rank'), dyn_pops=res.get('dyn_pops'), explicit_rank2=res.get('explicit_rank2'),
               seconds=seconds)
    if res['solved']:
        # the ordinary AC substitution cost of the certificate: one move per
        # substitution step, one per Nielsen image (transported to the terminal tail),
        # none for a signed permutation; None for a dyn (stable) certificate
        rec.update({k: v for k, v in acmoves.count(res['steps']).items()
                    if k in ('ac_moves', 'substitution', 'nielsen', 'perm', 'dyn')})
        try:
            hfhybrid.verify_hybrid(pair, res['steps'])
            rec['verified'] = True
        except (verify.Failure, hfhybrid.DV.Failure) as exc:
            rec['verified'] = False
            rec['failure'] = str(exc)
        if not params['compact'] or rec['units'] >= params['keep_above'] or not rec['verified']:
            rec['steps'] = res['steps']
    return rec


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--src', type=Path)
    g.add_argument('--census', type=Path)
    g.add_argument('--pairs', type=Path, help='JSONL(.gz) of records; name/r1/r2 are read')
    ap.add_argument('--prefix', default='row')
    ap.add_argument('--out', type=Path, required=True, help='.jsonl or .jsonl.gz')
    ap.add_argument('--offset', type=int, default=0)
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--budget', type=int, default=1000)
    ap.add_argument('--penalty', type=int, default=5)
    ap.add_argument('--dyn-max', type=int, default=0, help='0 = unlimited')
    ap.add_argument('--dyn-ratio', type=float, default=0.5, help='0 = unlimited')
    ap.add_argument('--cap', type=int, default=8)
    ap.add_argument('--slack', type=int, default=8)
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--every', type=int, default=10000)
    ap.add_argument('--compact', action='store_true')
    ap.add_argument('--keep-above', type=int, default=500)
    ap.add_argument('--skip-from', type=Path, nargs='*', default=[], help='earlier record files: rows already run there are skipped')
    ap.add_argument('--table', type=Path, help='also write a compact per-row CSV(.gz) with the AC-move counts')
    args = ap.parse_args()
    rows, skipped = load_rows(args)
    print(json.dumps(dict(rows_to_run=len(rows), skipped_already_run=len(skipped))), flush=True)
    params = dict(engine='hybrid', budget=args.budget, penalty=args.penalty, cap=args.cap, slack=args.slack,
                  dyn_max=args.dyn_max or None, dyn_ratio=args.dyn_ratio or None,
                  compact=args.compact, keep_above=args.keep_above)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    opener = gzip.open if args.out.suffix == '.gz' else open
    t0 = time.perf_counter()
    solved = verified = 0
    unsolved = []
    TABLE_COLS = ['name', 'r1', 'r2', 'length', 'solved', 'stage', 'units', 'path_length',
                  'max_rank', 'explicit_rank2', 'substitution', 'nielsen', 'perm', 'dyn',
                  'ac_moves', 'verified']
    table = tw = None
    if args.table:
        args.table.parent.mkdir(parents=True, exist_ok=True)
        table = (gzip.open if args.table.name.endswith('.gz') else open)(args.table, 'wt', newline='')
        tw = csv.writer(table)
        tw.writerow(TABLE_COLS)
    with opener(args.out, 'wt') as out, mp.Pool(args.workers) as pool:
        for i, rec in enumerate(pool.imap(job, [(r, params) for r in rows], chunksize=16)):
            out.write(json.dumps(rec) + '\n')
            if tw is not None:
                tw.writerow(['' if rec.get(c) is None else rec.get(c, '') for c in TABLE_COLS])
            solved += rec['solved']
            verified += rec.get('verified', False)
            if not rec['solved']:
                unsolved.append(rec['name'])
            if (i + 1) % args.every == 0 or i + 1 == len(rows):
                print(json.dumps(dict(rows=i + 1, solved=solved, verified=verified, unsolved=len(unsolved),
                                      elapsed=round(time.perf_counter() - t0, 1))), flush=True)
    summary = dict(source=str(args.pairs or args.census or args.src), rows=len(rows), solved=solved, verified=verified,
                   unsolved=unsolved, params=params, elapsed=time.perf_counter() - t0,
                   skipped_already_run=len(skipped),
                   skipped_solved_there=sum(1 for x in skipped if x[5]),
                   skipped_by_file=dict(collections.Counter(x[3] for x in skipped)))
    if skipped:
        with gzip.open(args.out.parent / (base_name(args.out) + '.skipped.csv.gz'), 'wt', newline='') as f:
            w = csv.writer(f)
            w.writerow(['name', 'r1', 'r2', 'run_in', 'as', 'solved', 'units'])
            w.writerows(skipped)
    if table is not None:
        table.close()
    base = base_name(args.out)
    (args.out.parent / (base + '.summary.json')).write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({k: v for k, v in summary.items() if k != 'unsolved'}), 'unsolved:', len(unsolved))


if __name__ == '__main__':
    main()
