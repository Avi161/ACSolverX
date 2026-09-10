"""Phase 1: the radius-2 portfolio on every target -- B1's trick applied to the unsolved.

    OMP_NUM_THREADS=1 NUMBA_NUM_THREADS=1 PYTHONPATH=. \\
        python3 -m research.autchoice_20260910.applied.run_phase1 --budget 20000 --workers 3

For every row of ``targets.csv`` the radius-2 ball (``orbit.ball``, cap 48, relabel-deduped;
identity first) is enumerated and every image is searched with ``S20_MK2`` at ``--budget``
pops.  The engine is deterministic, so a pair that occurs in several balls (88 of the 124
classes have identical ``aca_initial`` / ``aca_best`` pairs) is searched **once** and its
result written under every (row, image) that carries it, flagged ``s20.shared``; the
per-row verification through ``engine.verify_from_original`` is done separately for each
row, from that row's own pair.

Every claimed solve is replayed from the image (``common.search``, pure-Python
``words.replay_move``; a rejected claim is written with ``rejected`` set and logged to
``phase1_rejects.log``) and from the row's pair through the elementary automorphism
sequence (``engine.verify_from_original``); ``s20.verified`` is the conjunction.  The
independent re-check in a fresh process is ``verify_applied.py``, run at the end.

One JSON line per (row, image) in ``phase1.jsonl`` (shape: ``common.make_record``), appended
and flushed one at a time, so a restart skips every (row, image_index, budget) already on
disk.  Forms run in the order ``aca_initial, ac19_level9_leftover, aca_best`` so that, if the
projection printed after the first ``--project-after`` searches exceeds ``--max-hours``, the
run can be stopped and restarted with ``--forms aca_initial ac19_level9_leftover``.
``phase1_run.json`` records workers, budget, wall and counts of the last invocation.
"""
import argparse
import json
import multiprocessing as mp
import subprocess
import sys
import time
from collections import OrderedDict

from research.autchoice_20260910.applied.common import (
    CAP, FORM_ORDER, HERE, PHASE1, done_keys, group_by_pair, load_targets, make_record,
    search, write_json,
)

_ARGS = None


def _init_worker(budget, cap):
    global _ARGS
    _ARGS = (budget, cap)
    from research.autchoice_20260910.engine import warmup
    warmup()


def _run_group(group):
    """One distinct pair -> one search -> one record per (target, image) carrying it."""
    budget, cap = _ARGS
    pair, items = group
    result = search(pair, budget, cap)
    recs = []
    for k, (target, idx, node) in enumerate(items):
        recs.append(make_record(target, idx, node, result, budget, cap, phase='1', radius=2,
                                shared=(k > 0)))
    return recs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--budget', type=int, default=20000)
    ap.add_argument('--cap', type=int, default=CAP)
    ap.add_argument('--radius', type=int, default=2)
    ap.add_argument('--workers', type=int, default=3)
    ap.add_argument('--forms', nargs='*', default=list(FORM_ORDER))
    ap.add_argument('--names', nargs='*', default=None)
    ap.add_argument('--limit-searches', type=int, default=None, help='stop after this many distinct pairs')
    ap.add_argument('--project-after', type=int, default=30)
    ap.add_argument('--max-hours', type=float, default=2.5)
    ap.add_argument('--out', default=str(PHASE1))
    ap.add_argument('--no-verify', action='store_true')
    args = ap.parse_args()
    from research.autchoice_20260910.orbit import ball

    targets = [t for t in load_targets() if t['form'] in set(args.forms)]
    targets.sort(key=lambda t: FORM_ORDER.index(t['form']))
    if args.names:
        targets = [t for t in targets if t['name'] in set(args.names)]
    done = done_keys(args.out)
    items, n_images = [], 0
    for t in targets:
        nodes = ball((t['r1'], t['r2']), args.radius, args.cap)
        for idx, node in enumerate(nodes):
            n_images += 1
            if (t['name'], idx, args.budget) not in done:
                items.append((t, idx, node))
    groups = list(group_by_pair(items).items())
    if args.limit_searches:
        groups = groups[:args.limit_searches]
    n_recs = sum(len(g[1]) for g in groups)
    print(f'phase1: {len(targets)} targets, {n_images} images, {len(done)} records already done, '
          f'{n_recs} to write from {len(groups)} distinct searches, budget {args.budget}, cap {args.cap}, '
          f'{args.workers} workers', flush=True)
    t0 = time.time()
    n_done, n_written, n_solved = 0, 0, 0
    if groups:
        rejects = open(HERE / 'phase1_rejects.log', 'a')
        with open(args.out, 'a') as f:
            ctx = mp.get_context('spawn')
            with ctx.Pool(args.workers, initializer=_init_worker, initargs=(args.budget, args.cap)) as pool:
                for recs in pool.imap_unordered(_run_group, groups, chunksize=1):
                    for rec in recs:
                        f.write(json.dumps(rec) + '\n')
                        n_written += 1
                        if rec['s20'].get('rejected'):
                            rejects.write(f"{rec['row']} image {rec['image_index']}: {rec['s20']['rejected']}\n")
                            rejects.flush()
                        if rec['s20']['solved'] and rec['s20']['verified']:
                            n_solved += 1
                            print(f"  SOLVED {rec['row']} image {rec['image_index']} depth {rec['depth']} "
                                  f"seq {rec['seq']} nodes {rec['s20']['nodes']} moves {rec['s20']['path_len']}",
                                  flush=True)
                    f.flush()
                    n_done += 1
                    el = time.time() - t0
                    if n_done == args.project_after:
                        proj = len(groups) * el / n_done / 3600
                        print(f'  projection after {n_done} searches: {proj:.2f} h for {len(groups)} '
                              f'(max {args.max_hours} h){"  ** OVER BUDGET: stop and drop aca_best **" if proj > args.max_hours else ""}',
                              flush=True)
                    if n_done % 50 == 0 or n_done == len(groups):
                        print(f'  {n_done}/{len(groups)} searches  {n_written} records  {n_solved} solved  '
                              f'{el / 60:.1f} min elapsed  ETA {(len(groups) - n_done) * el / n_done / 60:.1f} min',
                              flush=True)
    wall = time.time() - t0
    print(f'done: {n_done} searches, {n_written} records, {n_solved} verified solves in {wall / 60:.1f} min '
          f'with {args.workers} workers', flush=True)
    write_json(HERE / 'phase1_run.json', OrderedDict(
        budget=args.budget, cap=args.cap, radius=args.radius, workers=args.workers, forms=args.forms,
        targets=len(targets), images=n_images, searches_this_run=n_done, records_this_run=n_written,
        solved_this_run=n_solved, wall_seconds=round(wall, 1),
        started_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(t0)),
        finished_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())))
    if not args.no_verify:
        subprocess.run([sys.executable, '-m', 'research.autchoice_20260910.applied.verify_applied'],
                       cwd=HERE.parents[2], check=False)


if __name__ == '__main__':
    main()
