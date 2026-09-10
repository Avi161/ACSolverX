"""Time a small sample of atlas runs at several budgets, to choose the atlas budget B.

Sample: the identity and the last radius-2 image of a few panel rows spanning the levels
(3, 4, 5, 9, originals), both arms, at each budget in ``--budgets``.  Prints a markdown
table of seconds per run and pops/s, and projects the whole atlas (rows x images x arms)
at each budget in the worst case (every run censored) and scaled by the sample's solve
rate.  One worker, so the projection at ``--workers`` is a plain division.

    OMP_NUM_THREADS=1 NUMBA_NUM_THREADS=1 PYTHONPATH=. \\
        python3 -m research.autchoice_20260910.time_budget --budgets 5000 10000 20000
"""
import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('NUMBA_NUM_THREADS', '1')
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.autchoice_20260910.engine import CONFIGS, cost, warmup  # noqa: E402
from research.autchoice_20260910.orbit import ball  # noqa: E402

HERE = Path(__file__).resolve().parent
SAMPLE = ['ac19_20653', 'ms_636', 'ac19_58079', 'ac19_30155', 'ac19_15507', 'ac19_55019',
          'ac19x_19903', 'ac19x_101025', 'ac19x_41313', 'ac19_16286']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--budgets', type=int, nargs='+', default=[5000, 10000, 20000])
    ap.add_argument('--workers', type=int, default=2)
    ap.add_argument('--cap', type=int, default=48)
    ap.add_argument('--out', default=str(HERE / 'timing.json'))
    args = ap.parse_args()
    panel = {r['name']: r for r in csv.DictReader(open(HERE / 'panel.csv'))}
    rows = [panel[n] for n in SAMPLE if n in panel]
    n_rows = len(panel)
    n_pair = sum(1 for r in panel.values() if r['form'] == 'original' or r['level'] == '9')
    balls = {n: ball((r['r1'], r['r2']), 2, args.cap) for n, r in panel.items()}
    n_img = sum(len(b) for b in balls.values())
    n_img_pair = sum(len(balls[n]) for n, r in panel.items() if r['form'] == 'original' or r['level'] == '9')
    print(f'panel: {n_rows} rows, {n_img} radius-2 images; pair rows {n_pair} with {n_img_pair} images')
    print(f'runs per budget: s20 {n_img} + greedy {n_img_pair} = {n_img + n_img_pair}')
    warmup()
    records = []
    for row in rows:
        b = balls[row['name']]
        for node in (b[0], b[-1]):
            for arm, cfg in CONFIGS.items():
                for B in args.budgets:
                    t0 = time.perf_counter()
                    r = cost((node['r1'], node['r2']), B, args.cap, cfg)
                    dt = time.perf_counter() - t0
                    records.append({'name': row['name'], 'level': row['level'], 'depth': node['depth'],
                                    'arm': arm, 'budget': B, 'solved': r['solved'], 'nodes': r['nodes'],
                                    'seconds': round(dt, 3)})
                    print(f"{row['name']:>13} L{row['level']} d{node['depth']} {arm:>6} B={B:>6} "
                          f"solved={int(r['solved'])} nodes={r['nodes']:>6} {dt:6.2f}s", flush=True)
    print()
    print('| budget | runs | censored | s/run (censored) | pops/s (censored) | s/run (all) | worst-case atlas h @%dw | sample-rate atlas h @%dw |' % (args.workers, args.workers))
    print('|---:|---:|---:|---:|---:|---:|---:|---:|')
    proj = {}
    for B in args.budgets:
        rs = [r for r in records if r['budget'] == B]
        cen = [r for r in rs if not r['solved']]
        s_cen = sum(r['seconds'] for r in cen) / len(cen) if cen else float('nan')
        pps = sum(r['nodes'] for r in cen) / sum(r['seconds'] for r in cen) if cen else float('nan')
        s_all = sum(r['seconds'] for r in rs) / len(rs)
        n_runs = n_img + n_img_pair
        worst = n_runs * s_cen / args.workers / 3600
        typical = n_runs * s_all / args.workers / 3600
        proj[B] = {'runs': n_runs, 'sample_runs': len(rs), 'sample_censored': len(cen),
                   's_per_run_censored': s_cen, 'pops_per_s_censored': pps, 's_per_run_all': s_all,
                   'worst_case_hours': worst, 'sample_rate_hours': typical}
        print(f'| {B} | {n_runs} | {len(cen)}/{len(rs)} | {s_cen:.2f} | {pps:,.0f} | {s_all:.2f} | {worst:.2f} | {typical:.2f} |')
    json.dump({'workers': args.workers, 'sample': records, 'projection': proj,
               'panel_rows': n_rows, 'images': n_img, 'pair_images': n_img_pair}, open(args.out, 'w'), indent=1)


if __name__ == '__main__':
    main()
