"""Run the hash-free cascade over AC19 aut-min rows (or a list) and verify every solve."""
from __future__ import annotations

import argparse
import csv
import json
import multiprocessing as mp
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.ac_hashfree_cascade_20260914 import hfcascade, verify  # noqa: E402

CENSUS = ROOT / 'data/AC19_extended_aut_min.csv'
UNSOLVED = ROOT / 'results/heuristic_search/ac19_final_policy_full_1k/unsolved.csv'


def load_rows(args):
    rows = list(csv.DictReader(open(CENSUS)))
    if args.names:
        wanted = set(args.names.split(','))
        rows = [r for r in rows if r['name'] in wanted]
    elif args.unsolved:
        wanted = {r['name'] for r in csv.DictReader(open(UNSOLVED))}
        rows = [r for r in rows if r['name'] in wanted]
    elif args.sample:
        rng = random.Random(args.seed)
        rows = rng.sample(rows, args.sample)
    if args.offset or args.limit:
        rows = rows[args.offset:args.offset + args.limit if args.limit else None]
    return rows


def job(arg):
    row, params = arg
    pair = (row['r1'], row['r2'])
    t = time.perf_counter()
    res = hfcascade.solve(pair, **params)
    seconds = time.perf_counter() - t
    rec = dict(name=row['name'], r1=row['r1'], r2=row['r2'], solved=res['solved'], stage=res['stage'],
               units=res['units'], units_raw=res['units_raw'], path_length=res['path_length'],
               max_relator=res['max_relator'], stages=res['stages'], seconds=seconds, params=params)
    if res['solved']:
        try:
            verify.replay(pair, res['steps'], res['states'])
            rec['verified'] = True
        except verify.Failure as exc:
            rec['verified'] = False
            rec['failure'] = str(exc)
        rec['steps'] = res['steps']
        rec['states'] = res['states']
    return rec


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--names')
    ap.add_argument('--unsolved', action='store_true', help='the 727 rows the census policy left')
    ap.add_argument('--sample', type=int, default=0)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--offset', type=int, default=0)
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--budget', type=int, default=1000)
    ap.add_argument('--width', type=int, default=8)
    ap.add_argument('--score', default='s20', choices=sorted(hfcascade.SCORES))
    ap.add_argument('--engine', default='beam', choices=('beam', 'bestfirst'))
    ap.add_argument('--ancestors', type=int, default=0)
    ap.add_argument('--closed-set', default='', choices=('', 'sorted', 'hash'), help="'sorted' = bisection array (no hashing); 'hash' = CONTROL")
    ap.add_argument('--frontier-dedup', action='store_true')
    ap.add_argument('--no-gates', action='store_true')
    ap.add_argument('--no-pair-descent', action='store_true')
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--no-states', action='store_true', help='drop states from the record (keep steps)')
    args = ap.parse_args()
    rows = load_rows(args)
    params = dict(budget=args.budget, width=args.width, score=args.score,
                  gates=not args.no_gates, pair_descent=not args.no_pair_descent,
                  engine=args.engine, ancestors=args.ancestors, closed_set=args.closed_set or False,
                  frontier_dedup=args.frontier_dedup)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    solved = verified = 0
    with args.out.open('w') as out, mp.Pool(args.workers) as pool:
        for i, rec in enumerate(pool.imap(job, [(r, params) for r in rows], chunksize=4)):
            if args.no_states:
                rec.pop('states', None)
            out.write(json.dumps(rec) + '\n')
            solved += rec['solved']
            verified += rec.get('verified', False)
            if (i + 1) % 500 == 0 or i + 1 == len(rows):
                print(json.dumps(dict(rows=i + 1, solved=solved, verified=verified,
                                      elapsed=round(time.perf_counter() - t0, 1))), flush=True)
    summary = dict(rows=len(rows), solved=solved, verified=verified, params=params,
                   elapsed=time.perf_counter() - t0)
    args.out.with_suffix('.summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
