"""Time the hash-free cascade on the 640 solved Miller-Schupp presentations, serially."""
from __future__ import annotations

import argparse
import ast
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.ac_hashfree_cascade_20260914 import hfcascade, verify  # noqa: E402

SYMBOL = {1: 'x', -1: 'X', 2: 'y', -2: 'Y'}


def load_ms640():
    lines = [ast.literal_eval(line) for line in
             (ROOT / 'data/ms640_solved.txt').read_text().splitlines() if line.strip()]
    if len(lines) != 640 or any(len(row) != 48 for row in lines):
        raise ValueError('expected 640 rows of 48 integers')
    return [tuple(''.join(SYMBOL[n] for n in half if n) for half in (row[:24], row[24:])) for row in lines]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--budget', type=int, default=1000)
    ap.add_argument('--engine', default='fast')
    ap.add_argument('--score', default='length')
    ap.add_argument('--no-perms', action='store_true')
    ap.add_argument('--no-nielsen', action='store_true')
    args = ap.parse_args()
    try:
        import numba
        numba.set_num_threads(1)
    except Exception:
        pass
    params = dict(budget=args.budget, engine=args.engine, score=args.score, closed_set='sorted',
                  nielsen=not args.no_nielsen, perms=not args.no_perms)
    hfcascade.solve(('YYXyx', 'Yx'), **params)          # warm-up (numba compilation)
    pairs = load_ms640()
    records = []
    search_wall = search_cpu = 0.0
    batch = time.perf_counter()
    for i, pair in enumerate(pairs):
        w0, c0 = time.perf_counter(), time.process_time()
        res = hfcascade.solve(pair, **params)
        w, c = time.perf_counter() - w0, time.process_time() - c0
        search_wall += w
        search_cpu += c
        rec = dict(pres_id=i, r1=pair[0], r2=pair[1], solved=res['solved'], stage=res['stage'],
                   units=res['units'], path_length=res['path_length'], max_relator=res['max_relator'],
                   wall=w, cpu=c)
        if res['solved']:
            verify.replay(pair, res['steps'], res['states'])
            rec['verified'] = True
            rec['steps'] = res['steps']
        records.append(rec)
    batch = time.perf_counter() - batch
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('w') as f:
        for rec in records:
            f.write(json.dumps(rec) + '\n')
    solved = [r for r in records if r['solved']]
    summary = dict(rows=len(records), solved=len(solved), verified=sum(1 for r in solved if r.get('verified')),
                   search_wall=search_wall, search_cpu=search_cpu,
                   batch_wall_including_verification=batch,
                   max_units=max(r['units'] for r in records), total_units=sum(r['units'] for r in records),
                   max_wall_row=max(r['wall'] for r in records), params=params)
    args.out.with_suffix('.summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
