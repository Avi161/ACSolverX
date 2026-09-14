"""Run the dynamic-rank search (research/ac_dynamic_rank_20260913/dynrank.py) over AC19
aut-min rows and replay every solved certificate with its independent verifier."""
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

from research.ac_dynamic_rank_20260913 import dynrank as D  # noqa: E402
from research.ac_dynamic_rank_20260913 import verify as V  # noqa: E402

CENSUS = ROOT / 'data/AC19_extended_aut_min.csv'
UNSOLVED = ROOT / 'results/heuristic_search/ac19_final_policy_full_1k/unsolved.csv'


def load_rows(args):
    rows = list(csv.DictReader(open(CENSUS)))
    if args.names:
        wanted = set(args.names.split(','))
        rows = [r for r in rows if r['name'] in wanted]
    elif args.names_file:
        wanted = set(open(args.names_file).read().strip().split(','))
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
    row, params, pops = arg
    root = (D.parse(row['r1']), D.parse(row['r2']))
    L = D.total_length(root)
    kw = dict(params)
    kw['ceiling'] = L + kw.pop('slack')
    t = time.perf_counter()
    res = D.best_first(root, pops=pops, **kw)
    seconds = time.perf_counter() - t
    rec = dict(name=row['name'], r1=row['r1'], r2=row['r2'], solved=res['solved'], units=res['pops'],
               generated=res['generated'], path_length=res['path_length'], max_rank=res['max_rank'],
               min_total_length=res['min_total_length'], seconds=seconds, params=res['params'])
    if res['solved']:
        path = D.json_path(res['path'])
        root_relabel = D.json_relabel(res['root_relabel'])
        rec['path'] = path
        rec['root_relabel'] = root_relabel
        try:
            V.replay([list(w) for w in root], json.loads(json.dumps(path)), res['params']['min_uses'], root_relabel)
            rec['verified'] = True
        except V.Failure as exc:
            rec['verified'] = False
            rec['failure'] = str(exc)
        kinds = [s['event']['kind'] for s in path]
        rec['defines'] = kinds.count('define')
        rec['eliminates'] = kinds.count('eliminate')
        rec['products'] = kinds.count('product')
    return rec


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--names')
    ap.add_argument('--names-file')
    ap.add_argument('--unsolved', action='store_true')
    ap.add_argument('--sample', type=int, default=0)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--offset', type=int, default=0)
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--pops', type=int, default=1000)
    ap.add_argument('--cap', type=int, default=8)
    ap.add_argument('--slack', type=int, default=8)
    ap.add_argument('--priority', default='length')
    ap.add_argument('--no-relabel', action='store_true')
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--no-path', action='store_true')
    args = ap.parse_args()
    rows = load_rows(args)
    params = dict(cap=args.cap, slack=args.slack, priority=args.priority, relabel=not args.no_relabel,
                  allow_define=True, allow_eliminate=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    solved = verified = 0
    with args.out.open('w') as out, mp.Pool(args.workers) as pool:
        for i, rec in enumerate(pool.imap(job, [(r, params, args.pops) for r in rows], chunksize=2)):
            if args.no_path:
                rec.pop('path', None)
            out.write(json.dumps(rec) + '\n')
            solved += rec['solved']
            verified += rec.get('verified', False)
            if (i + 1) % 100 == 0 or i + 1 == len(rows):
                print(json.dumps(dict(rows=i + 1, solved=solved, verified=verified,
                                      elapsed=round(time.perf_counter() - t0, 1))), flush=True)
    summary = dict(rows=len(rows), solved=solved, verified=verified, params=params, pops=args.pops,
                   elapsed=time.perf_counter() - t0)
    args.out.with_suffix('.summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
