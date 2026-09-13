"""Run the dynamic-rank search arms over the 60-row solved ladder and the 124 U124 rows.

Every solved record carries its full certificate, which is replayed by the
independent ``verify.replay`` before it is written (``verified`` field).

    python3 run_ladder.py --panel ladder --arms ctrl,dyn,dyn_norelabel --pops 2000 --out records/ladder.jsonl
    python3 run_ladder.py --panel u124   --arms dyn                    --pops 2000 --out records/u124.jsonl
"""
from __future__ import annotations

import argparse
import csv
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
import dynrank as D   # noqa: E402
import verify as V    # noqa: E402

LADDER = ROOT / 'benchmark/subsets/benchmark_subset_60.csv'
U124 = ROOT / 'data/ms_unsolved_reps/aca_124_best.csv'


def arm_params(arm, L):
    if arm == 'ctrl':          # rank two only: ordinary products, unit peeling as the solve test
        return dict(cap=24, ceiling=10 ** 9, allow_define=False, allow_eliminate=True,
                    elim_units_only=True, relabel=False)
    if arm == 'dyn':           # define + eliminate + products, renaming canonicalisation
        return dict(cap=8, ceiling=L + 8, allow_define=True, allow_eliminate=True, relabel=True)
    if arm == 'dyn_norelabel':
        return dict(cap=8, ceiling=L + 8, allow_define=True, allow_eliminate=True, relabel=False)
    if arm == 'dyn_c10s12':
        return dict(cap=10, ceiling=L + 12, allow_define=True, allow_eliminate=True, relabel=True)
    if arm == 'tri':           # start from the all-triangle root, fixed dictionary: no define, eliminate allowed
        return dict(cap=8, ceiling=L + 8, allow_define=False, allow_eliminate=True, relabel=True)
    raise ValueError(arm)


def load_panel(panel):
    rows = []
    if panel == 'ladder':
        for r in csv.DictReader(open(LADDER)):
            rows.append({'name': r['pres_id'], 'panel': 'ladder', 'bin': int(r['bin']), 'r1': r['r1'], 'r2': r['r2'],
                         'greedy_nodes_1M': int(r['nodes_1M']) if r['nodes_1M'] else None,
                         'greedy_path_1M': int(r['path_1M']) if r['path_1M'] else None})
    elif panel == 'u124':
        for r in csv.DictReader(open(U124)):
            rows.append({'name': r['name'], 'panel': 'u124', 'bin': None, 'r1': r['r1'], 'r2': r['r2'],
                         'n_members': int(r['n_members'])})
    else:
        raise ValueError(panel)
    return rows


def job(args):
    row, arm, pops = args
    root = (D.parse(row['r1']), D.parse(row['r2']))
    L = D.total_length(root)
    params = arm_params(arm, L)
    t0 = time.time()
    prefix = []
    start = root
    if arm == 'tri':
        start, prefix = D.triangulate(root)
    res = D.best_first(start, pops=pops, **params)
    rec = dict(row)
    rec.update({'arm': arm, 'root': [list(w) for w in root], 'root_length': L,
                'solved': res['solved'], 'pops': res['pops'], 'generated': res['generated'],
                'states': res['states'], 'min_total_length': res['min_total_length'],
                'max_rank': res['max_rank'], 'path_length': res['path_length'],
                'cpu_seconds': res['cpu_seconds'], 'wall_seconds': time.time() - t0,
                'params': res['params'], 'root_relabel': None if prefix else D.json_relabel(res['root_relabel']),
                'path': None, 'verified': None})
    if arm == 'tri':
        rec['tri_root'] = [list(w) for w in start]
        rec['tri_rank'] = len(start)
        rec['tri_defines'] = len(prefix)
    if res['path'] is not None:
        path = D.json_path(res['path'])
        if prefix:
            # replay from the rank-two root: the definitions, a renaming, then the search steps
            path = (D.json_path(prefix)
                    + [{'event': {'kind': 'rename'}, 'relabel': D.json_relabel(res['root_relabel']),
                        'after': [list(w) for w in res['root_key']]}]
                    + path)
        rec['path'] = path
    if res['solved']:
        path = json.loads(json.dumps(rec['path']))
        try:
            info = V.replay(rec['root'], path, rec['params']['min_uses'], rec['root_relabel'])
            rec['verified'] = True
            rec['certificate'] = info
        except V.Failure as e:
            rec['verified'] = False
            rec['certificate'] = {'error': str(e)}
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--panel', required=True)
    ap.add_argument('--arms', required=True)
    ap.add_argument('--pops', type=int, default=2000)
    ap.add_argument('--out', required=True)
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--names', default=None, help='comma-separated subset of row names')
    a = ap.parse_args()
    rows = load_panel(a.panel)
    if a.names:
        keep = set(a.names.split(','))
        rows = [r for r in rows if r['name'] in keep]
    arms = a.arms.split(',')
    jobs = [(r, arm, a.pops) for r in rows for arm in arms]
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    done = 0
    t0 = time.time()
    with open(out, 'w') as f, mp.Pool(a.workers) as pool:
        for rec in pool.imap_unordered(job, jobs):
            f.write(json.dumps(rec) + '\n')
            f.flush()
            done += 1
            print(f"[{done}/{len(jobs)} {time.time()-t0:7.0f}s] {rec['name']:>8} bin={rec['bin']} {rec['arm']:14s} "
                  f"solved={rec['solved']!s:5} verified={rec['verified']} pops={rec['pops']:5d} states={rec['states']:7d} "
                  f"minL={rec['min_total_length']:2d} maxrank={rec['max_rank']} path={rec['path_length']} "
                  f"cpu={rec['cpu_seconds']:6.1f}s", flush=True)


if __name__ == '__main__':
    main()
