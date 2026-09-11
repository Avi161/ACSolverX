"""Run the orbit-cost atlas: every radius-2 Aut-image of every panel row, searched.

For each row of ``panel.csv`` the radius-2 ball (``orbit.ball``, cap 48, relabel-deduped)
is enumerated and every image is searched with ``S20_MK2`` at one budget ``B``; the
images of the 73 *pair* rows (the 28 level-9 representatives and the 45 originals) are
also searched with the plain length-ordered greedy (``config=None``).  Smaller budgets are
read off afterwards (``solved and nodes <= b``); ``B`` was chosen from ``time_budget.py``.

Every claimed solve is replayed through ``words.replay_move`` from the image
(``engine.cost`` raises otherwise -- the record is then written with ``rejected`` set and
the case logged to ``atlas_rejects.log``) and, on top, through
``engine.verify_from_original`` from the *row's* pair via the elementary automorphism
sequence; ``verified`` is the conjunction.

One JSON line per (row, image): ``row, level, form, source, orbit, pair_id, image_index,
depth, seq, phi, r1, r2, rkey, is_identity, features, s20, greedy, budget, cap``.  Lines
are appended and flushed one at a time, so a crash loses at most the record in flight and
a restart skips every (row, image_index) already on disk.

    OMP_NUM_THREADS=1 NUMBA_NUM_THREADS=1 PYTHONPATH=. \\
        python3 -m research.autchoice_20260910.run_atlas --budget 20000 --workers auto

``--workers auto`` is 2 while a ``benchmark.ladder.run_ladder`` job is alive, 4 otherwise
(4 cores; the ladder jobs take 2 each).
"""
import argparse
import csv
import json
import multiprocessing as mp
import os
import subprocess
import sys
import time
from collections import OrderedDict
from pathlib import Path

os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('NUMBA_NUM_THREADS', '1')
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

HERE = Path(__file__).resolve().parent
PANEL_COLS = ('level', 'form', 'source', 'orbit', 'pair_id')

_ARGS = None


def _init_worker(budget, cap):
    global _ARGS
    _ARGS = (budget, cap)
    from research.autchoice_20260910.engine import warmup
    warmup()


def is_pair_row(row):
    return row['form'] == 'original' or row['level'] == '9'


def _run_task(task):
    """One (row, image) -> one record; runs in a worker."""
    from research.autchoice_20260910.engine import CONFIGS, ReplayError, cost, verify_from_original
    from research.autchoice_20260910.features import features
    budget, cap = _ARGS
    row, idx, node, arms = task
    rec = OrderedDict(row=row['name'])
    for k in PANEL_COLS:
        rec[k] = row[k]
    rec.update(image_index=idx, depth=node['depth'], seq=node['seq'], phi=node['phi'],
               r1=node['r1'], r2=node['r2'], rkey=list(node['rkey']), is_identity=(idx == 0),
               features=features(node['r1'], node['r2']), budget=budget, cap=cap)
    orig = (row['r1'], row['r2'])
    for arm in ('s20', 'greedy'):
        if arm not in arms:
            rec[arm] = None
            continue
        t0 = time.perf_counter()
        try:
            r = cost((node['r1'], node['r2']), budget, cap, CONFIGS[arm])
            rejected = False
        except ReplayError as e:
            r = {'solved': False, 'nodes': budget, 'path_moves': [], 'max_expanded': None}
            rejected = str(e)
        wall = time.perf_counter() - t0
        ok = bool(r['solved']) and not rejected and verify_from_original(orig, node['seq'], r['path_moves'])
        rec[arm] = OrderedDict(solved=bool(r['solved']) and not rejected, nodes=int(r['nodes']),
                               max_expanded=r['max_expanded'], verified=ok,
                               path_len=len(r['path_moves']) if r['solved'] else None,
                               wall=round(wall, 3), path_moves=r['path_moves'] if r['solved'] else None)
        if rejected:
            rec[arm]['rejected'] = rejected
    return rec


def ladder_jobs_alive():
    out = subprocess.run(['pgrep', '-fc', '^python3 -m benchmark.ladder.run_ladder'],
                         capture_output=True, text=True).stdout.strip()
    return int(out or 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--budget', type=int, default=20000)
    ap.add_argument('--cap', type=int, default=48)
    ap.add_argument('--radius', type=int, default=2)
    ap.add_argument('--workers', default='auto')
    ap.add_argument('--panel', default=str(HERE / 'panel.csv'))
    ap.add_argument('--out', default=str(HERE / 'atlas.jsonl'))
    ap.add_argument('--names', nargs='*', default=None)
    ap.add_argument('--limit', type=int, default=None)
    args = ap.parse_args()
    from research.autchoice_20260910.orbit import ball

    workers = (2 if ladder_jobs_alive() else 4) if args.workers == 'auto' else int(args.workers)
    rows = list(csv.DictReader(open(args.panel)))
    if args.names:
        rows = [r for r in rows if r['name'] in set(args.names)]
    if args.limit:
        rows = rows[:args.limit]
    out = Path(args.out)
    done = set()
    if out.exists():
        for line in open(out):
            if line.strip():
                d = json.loads(line)
                if d['budget'] == args.budget and d['cap'] == args.cap:
                    done.add((d['row'], d['image_index']))
    tasks = []
    n_images = 0
    for row in rows:
        nodes = ball((row['r1'], row['r2']), args.radius, args.cap)
        arms = ('s20', 'greedy') if is_pair_row(row) else ('s20',)
        for idx, node in enumerate(nodes):
            n_images += 1
            if (row['name'], idx) not in done:
                tasks.append((row, idx, node, arms))
    print(f'atlas: {len(rows)} rows, {n_images} images, {len(done)} already done, {len(tasks)} to run, '
          f'budget {args.budget}, cap {args.cap}, {workers} workers', flush=True)
    if not tasks:
        return
    t0 = time.time()
    n = 0
    rejects = open(HERE / 'atlas_rejects.log', 'a')
    with open(out, 'a') as f:
        ctx = mp.get_context('spawn')
        with ctx.Pool(workers, initializer=_init_worker, initargs=(args.budget, args.cap)) as pool:
            for rec in pool.imap_unordered(_run_task, tasks, chunksize=1):
                f.write(json.dumps(rec) + '\n')
                f.flush()
                n += 1
                for arm in ('s20', 'greedy'):
                    if rec[arm] and rec[arm].get('rejected'):
                        rejects.write(f"{rec['row']} image {rec['image_index']} {arm}: {rec[arm]['rejected']}\n")
                        rejects.flush()
                if n % 25 == 0 or n == len(tasks):
                    el = time.time() - t0
                    print(f'  {n}/{len(tasks)} records  {el / 60:.1f} min elapsed  '
                          f'ETA {(len(tasks) - n) * el / n / 60:.1f} min', flush=True)
    print(f'done: {n} records in {(time.time() - t0) / 60:.1f} min with {workers} workers', flush=True)


if __name__ == '__main__':
    main()
