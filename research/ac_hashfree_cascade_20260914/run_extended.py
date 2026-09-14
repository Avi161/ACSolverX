"""Run the final hybrid solver over every row of `data/AC19_extended.txt` (156,762
presentations in their ORIGINAL spelling, not the Aut-minimal representatives) at a
fixed unit budget and verify every certificate.

Row format: 48 integers, two relators of 24 slots each, letters 1/-1/2/-2 = x/X/y/Y and
0 = padding.  Row i is recorded as `ext_i` (0-based line index, the same index the
`members` column of `data/AC19_extended_aut_min.csv` uses)."""
from __future__ import annotations

import argparse
import ast
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

EXTENDED = ROOT / 'data/AC19_extended.txt'
LETTER = {1: 'x', -1: 'X', 2: 'y', -2: 'Y'}


def row_to_pair(line):
    v = ast.literal_eval(line)
    assert len(v) == 48, len(v)
    r1 = ''.join(LETTER[t] for t in v[:24] if t)
    r2 = ''.join(LETTER[t] for t in v[24:] if t)
    return r1, r2


def load_rows(args):
    lines = [l.strip() for l in open(EXTENDED) if l.strip()]
    rows = [(i, line) for i, line in enumerate(lines)]
    if args.offset or args.limit:
        rows = rows[args.offset:args.offset + args.limit if args.limit else None]
    return rows


def job(arg):
    (index, line), params = arg
    pair = row_to_pair(line)
    t = time.perf_counter()
    res = hfhybrid.solve(pair, budget=params['budget'], penalty=params['penalty'], cap=params['cap'],
                         slack=params['slack'], dyn_max=params.get('dyn_max'), dyn_ratio=params.get('dyn_ratio'))
    seconds = time.perf_counter() - t
    rec = dict(name=f'ext_{index}', r1=pair[0], r2=pair[1], length=len(pair[0]) + len(pair[1]),
               solved=res['solved'], stage=res['stage'], units=res['units'], path_length=res.get('path_length'),
               max_rank=res.get('max_rank'), dyn_pops=res.get('dyn_pops'), explicit_rank2=res.get('explicit_rank2'),
               seconds=seconds)
    if res['solved']:
        try:
            hfhybrid.verify_hybrid(pair, res['steps'])
            rec['verified'] = True
        except (verify.Failure, hfhybrid.DV.Failure) as exc:
            rec['verified'] = False
            rec['failure'] = str(exc)
        rec['steps'] = res['steps']
    return rec


def main():
    ap = argparse.ArgumentParser(description=__doc__)
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
    ap.add_argument('--every', type=int, default=5000)
    args = ap.parse_args()
    rows = load_rows(args)
    params = dict(engine='hybrid', budget=args.budget, penalty=args.penalty, cap=args.cap, slack=args.slack,
                  dyn_max=args.dyn_max or None, dyn_ratio=args.dyn_ratio or None)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    opener = gzip.open if args.out.suffix == '.gz' else open
    t0 = time.perf_counter()
    solved = verified = 0
    unsolved = []
    with opener(args.out, 'wt') as out, mp.Pool(args.workers) as pool:
        for i, rec in enumerate(pool.imap(job, [(r, params) for r in rows], chunksize=16)):
            out.write(json.dumps(rec) + '\n')
            solved += rec['solved']
            verified += rec.get('verified', False)
            if not rec['solved']:
                unsolved.append(rec['name'])
            if (i + 1) % args.every == 0 or i + 1 == len(rows):
                print(json.dumps(dict(rows=i + 1, solved=solved, verified=verified, unsolved=len(unsolved),
                                      elapsed=round(time.perf_counter() - t0, 1))), flush=True)
    summary = dict(rows=len(rows), solved=solved, verified=verified, unsolved=unsolved, params=params,
                   elapsed=time.perf_counter() - t0)
    base = args.out.name[:-len('.jsonl.gz')] if args.out.name.endswith('.jsonl.gz') else args.out.stem
    (args.out.parent / (base + '.summary.json')).write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({k: v for k, v in summary.items() if k != 'unsolved'}), 'unsolved:', len(unsolved))


if __name__ == '__main__':
    main()
