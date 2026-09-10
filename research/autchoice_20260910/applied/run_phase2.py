"""Phase 2: radius 3 and a 200,000-pop escalation on the targets whose ball came closest.

    OMP_NUM_THREADS=1 NUMBA_NUM_THREADS=1 PYTHONPATH=. \\
        python3 -m research.autchoice_20260910.applied.run_phase2 --workers 3

Selection (from ``phase1.jsonl``; written to ``phase2_selection.json``): the two
``ac19_level9_leftover`` rows, plus up to ``--n-aca`` (10) unsolved ``aca_*`` targets ranked
by how close their radius-2 ball got -- smallest ``min_total_length_seen`` over the ball
(the engine's smallest discovered total relator length), then the most images whose
minimum went below the target's start length, then the most images whose minimum got back
down to the start length (a longer image whose search rediscovers a state as short as the
row), then the largest drop below the start, then the name; two rows with the identical pair
(``aca_N`` = ``acabest_N`` on 88 classes) count once.

Stage A (``phase='2a'``, budget ``--budget`` = 20,000): the radius-3 ball (``orbit.ball``,
cap 48).  Its first images are asserted to be the radius-2 ball in the same order, so only
the depth-3 images are new; a pair already searched at this budget (phase 1, or earlier
in this stage) is not searched again -- the engine is deterministic -- but re-recorded
under the new (row, image) with ``s20.shared`` set and its own ``verify_from_original``.

Stage B (``phase='2b'``, budget ``--big-budget`` = 200,000): the top ``--top`` (3) images of
each selected target's radius-3 ball, ranked by ``predictor/rank_images.py``'s
``rank(pair, radius=3)`` when that module exists and its output can be matched to the ball
(``ranker`` = ``predictor.rank_images``), else by the lowest ``h_s20mk2`` of
``features.py`` (``ranker`` = ``h_s20mk2``); ties by image index.  The identity is a
candidate like any other image.  ~2.6 GB per worker at 200k; ``--workers`` is lowered to 2
if less than 10 GB is free.

Both stages: every claimed solve replayed from the image and from the row's own pair
(``common.search``, ``engine.verify_from_original``); records appended to ``phase2.jsonl``
one at a time (resume key ``(row, image_index, budget)``); ``phase2_run.json`` holds the
walls, and ``verify_applied.py`` is run at the end in a fresh process.
"""
import argparse
import importlib
import json
import multiprocessing as mp
import subprocess
import sys
import time
from collections import OrderedDict

from research.autchoice_20260910.applied.common import (
    CAP, HERE, PHASE1, PHASE2, done_keys, group_by_pair, load_targets, make_record,
    read_jsonl, search, write_json,
)

_ARGS = None


def _init_worker(cap):
    global _ARGS
    _ARGS = cap
    from research.autchoice_20260910.engine import warmup
    warmup()


def _run_group(group):
    """One (pair, budget) -> one search -> one record per (target, image, phase, extra)."""
    cap = _ARGS
    (pair, budget), items = group
    result = search(pair, budget, cap)
    recs = []
    for k, (target, idx, node, phase, radius, extra) in enumerate(items):
        recs.append(make_record(target, idx, node, result, budget, cap, phase=phase, radius=radius,
                                shared=(k > 0), extra=extra))
    return recs


def free_gb():
    try:
        for line in open('/proc/meminfo'):
            if line.startswith('MemAvailable'):
                return int(line.split()[1]) / 1e6
    except OSError:
        pass
    return None


def phase1_summary(targets):
    """Per target: start_len, ball_min, n_below_start, solved -- from phase1.jsonl."""
    per = OrderedDict((t['name'], dict(start_len=len(t['r1']) + len(t['r2']), ball_min=None,
                                       n_below=0, n_at_or_below=0, images=0, solved=False, identity_min=None))
                      for t in targets)
    for d in read_jsonl(PHASE1):
        s = per.get(d['row'])
        if s is None:
            continue
        m = d['s20']['min_total_length_seen']
        s['images'] += 1
        s['ball_min'] = m if s['ball_min'] is None else min(s['ball_min'], m)
        s['n_below'] += int(m < s['start_len'])
        s['n_at_or_below'] += int(m <= s['start_len'])
        s['solved'] |= bool(d['s20']['solved'] and d['s20']['verified'])
        if d['image_index'] == 0:
            s['identity_min'] = m
    return per


def select(targets, n_aca):
    per = phase1_summary(targets)
    chosen = [t for t in targets if t['form'] == 'ac19_level9_leftover']
    seen_pairs = {(t['r1'], t['r2']) for t in chosen}
    aca = [t for t in targets if t['form'].startswith('aca') and per[t['name']]['images'] > 0
           and not per[t['name']]['solved']]
    aca.sort(key=lambda t: (per[t['name']]['ball_min'], -per[t['name']]['n_below'],
                            -per[t['name']]['n_at_or_below'],
                            per[t['name']]['ball_min'] - per[t['name']]['start_len'], t['name']))
    n_chosen_aca = 0
    for t in aca:
        if n_chosen_aca >= n_aca:
            break
        if (t['r1'], t['r2']) in seen_pairs:
            continue
        seen_pairs.add((t['r1'], t['r2']))
        chosen.append(t)
        n_chosen_aca += 1
    return chosen, per


def predictor_rank(pair, radius, nodes):
    """Try B2's ranker; returns (ordered node indices, ranker name, scores) or None."""
    try:
        mod = importlib.import_module('research.autchoice_20260910.predictor.rank_images')
    except Exception as e:  # noqa: BLE001
        print(f'  predictor.rank_images not importable ({e!r}); falling back to h_s20mk2', flush=True)
        return None
    try:
        ranked = mod.rank(pair, radius=radius)
        w = mod.load_weights() if hasattr(mod, 'load_weights') else None
        model = 'lowest_h' if w is None else str(w.get('model', 'learned'))
    except Exception as e:  # noqa: BLE001
        print(f'  predictor.rank_images.rank failed ({e!r}); falling back to h_s20mk2', flush=True)
        return None
    from experiments.equivalence_classes.lib.words import relabel_key
    by_key = {tuple(n['rkey']): i for i, n in enumerate(nodes)}
    order, scores = [], {}
    for item in ranked:
        cand = item
        score = None
        if isinstance(item, (tuple, list)) and len(item) == 2:
            a, b = item
            cand, score = (b, a) if isinstance(b, dict) else (a, b)
        if isinstance(cand, dict) and 'r1' in cand and 'r2' in cand:
            key = tuple(relabel_key((cand['r1'], cand['r2'])))
            score = cand.get('score', cand.get('pred', score))
        elif isinstance(cand, (tuple, list)) and len(cand) == 2 and all(isinstance(w, str) for w in cand):
            key = tuple(relabel_key((cand[0], cand[1])))
        else:
            print(f'  predictor.rank_images.rank returned an item I cannot read ({type(item)}); falling back',
                  flush=True)
            return None
        i = by_key.get(key)
        if i is None or i in order:
            continue
        order.append(i)
        scores[i] = score
    if len(order) < min(3, len(nodes)):
        print('  predictor ranking matched too few ball images; falling back to h_s20mk2', flush=True)
        return None
    return order, f'predictor.rank_images[{model}]', scores


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--budget', type=int, default=20000)
    ap.add_argument('--big-budget', type=int, default=200000)
    ap.add_argument('--cap', type=int, default=CAP)
    ap.add_argument('--radius', type=int, default=3)
    ap.add_argument('--top', type=int, default=3)
    ap.add_argument('--n-aca', type=int, default=10)
    ap.add_argument('--workers', type=int, default=3)
    ap.add_argument('--ranker', choices=('auto', 'h_s20mk2', 'predictor'), default='auto')
    ap.add_argument('--skip-b', action='store_true')
    ap.add_argument('--no-verify', action='store_true')
    args = ap.parse_args()
    from research.autchoice_20260910.orbit import ball
    from research.autchoice_20260910.features import h_s20mk2

    targets = load_targets()
    chosen, per = select(targets, args.n_aca)
    write_json(HERE / 'phase2_selection.json', OrderedDict(
        rule='2 leftovers + up to n_aca unsolved aca targets by (ball_min, -n_below_start, -n_at_or_below_start, ball_min-start_len, name), identical pairs once',
        n_aca=args.n_aca,
        selected=[OrderedDict(name=t['name'], form=t['form'], r1=t['r1'], r2=t['r2'], **per[t['name']]) for t in chosen]))
    print(f'phase2: {len(chosen)} targets selected: ' + ', '.join(t['name'] for t in chosen), flush=True)

    # known results at a budget: (r1, r2, budget) -> s20 dict, for pair reuse
    known = {}
    for path in (PHASE1, PHASE2):
        for d in read_jsonl(path):
            if d['cap'] == args.cap:
                known.setdefault((d['r1'], d['r2'], d['budget']), d['s20'])
    done = done_keys(PHASE2)
    t0 = time.time()
    walls = OrderedDict()
    counts = OrderedDict()

    balls = OrderedDict()
    for t in chosen:
        b2 = ball((t['r1'], t['r2']), 2, args.cap)
        b3 = ball((t['r1'], t['r2']), args.radius, args.cap)
        assert [(n['r1'], n['r2'], n['seq']) for n in b3[:len(b2)]] == [(n['r1'], n['r2'], n['seq']) for n in b2], t['name']
        balls[t['name']] = (b3, len(b2))

    def run_stage(stage, items, budget, workers):
        """items: (target, idx, node, phase, radius, extra); reuse known pairs, search the rest."""
        st = time.time()
        n_written = n_solved = n_search = 0
        pending = []
        with open(PHASE2, 'a') as f:
            def emit(rec):
                nonlocal n_written, n_solved
                f.write(json.dumps(rec) + '\n')
                f.flush()
                n_written += 1
                if rec['s20']['solved'] and rec['s20']['verified']:
                    n_solved += 1
                    print(f"  SOLVED {rec['row']} image {rec['image_index']} depth {rec['depth']} seq {rec['seq']} "
                          f"nodes {rec['s20']['nodes']} moves {rec['s20']['path_len']} (phase {rec['phase']})", flush=True)
            for it in items:
                target, idx, node, phase, radius, extra = it
                key = (node['r1'], node['r2'], budget)
                if key in known:
                    emit(make_record(target, idx, node, dict(known[key]), budget, args.cap, phase=phase,
                                     radius=radius, shared=True, extra=extra))
                else:
                    pending.append(it)
            groups = [((pair, budget), its) for pair, its in group_by_pair(pending).items()]
            print(f'  stage {stage}: {len(items)} records wanted, {n_written} reused, {len(groups)} searches at '
                  f'{budget} pops with {workers} workers', flush=True)
            if groups:
                ctx = mp.get_context('spawn')
                with ctx.Pool(workers, initializer=_init_worker, initargs=(args.cap,)) as pool:
                    for recs in pool.imap_unordered(_run_group, groups, chunksize=1):
                        n_search += 1
                        for rec in recs:
                            known.setdefault((rec['r1'], rec['r2'], budget), rec['s20'])
                            emit(rec)
                        el = time.time() - st
                        print(f'  stage {stage}: {n_search}/{len(groups)} searches  {n_written} records  '
                              f'{n_solved} solved  {el / 60:.1f} min  ETA {(len(groups) - n_search) * el / n_search / 60:.1f} min',
                              flush=True)
        walls[stage] = round(time.time() - st, 1)
        counts[stage] = OrderedDict(records=n_written, searches=n_search, solved=n_solved, workers=workers)

    # ---- stage A: depth-3 images at the phase-1 budget
    items = []
    for t in chosen:
        b3, n2 = balls[t['name']]
        for idx in range(n2, len(b3)):
            if (t['name'], idx, args.budget) not in done:
                items.append((t, idx, b3[idx], '2a', args.radius, None))
    run_stage('A', items, args.budget, args.workers)

    if not args.skip_b:
        # ---- stage B: top images by the ranker at the big budget
        for path in (PHASE2,):
            for d in read_jsonl(path):
                known.setdefault((d['r1'], d['r2'], d['budget']), d['s20'])
        done = done_keys(PHASE2)
        items, ranking = [], OrderedDict()
        for t in chosen:
            b3, _ = balls[t['name']]
            pair = (t['r1'], t['r2'])
            res = None
            if args.ranker in ('auto', 'predictor'):
                res = predictor_rank(pair, args.radius, b3)
            if res is None:
                hs = [h_s20mk2(n['r1'], n['r2']) for n in b3]
                order = sorted(range(len(b3)), key=lambda i: (hs[i], i))
                res = (order, 'h_s20mk2', {i: hs[i] for i in order})
            order, ranker, scores = res
            top = order[:args.top]
            ranking[t['name']] = OrderedDict(ranker=ranker, top=[OrderedDict(
                image_index=i, depth=b3[i]['depth'], seq=b3[i]['seq'], r1=b3[i]['r1'], r2=b3[i]['r2'],
                score=scores.get(i)) for i in top])
            for rank_pos, i in enumerate(top, 1):
                if (t['name'], i, args.big_budget) not in done:
                    items.append((t, i, b3[i], '2b', args.radius,
                                  OrderedDict(ranker=ranker, rank=rank_pos, rank_score=scores.get(i))))
        write_json(HERE / 'phase2_ranking.json', ranking)
        workers = args.workers
        fg = free_gb()
        if fg is not None and fg < 10 and workers > 2:
            print(f'  only {fg:.1f} GB free; stage B with 2 workers', flush=True)
            workers = 2
        run_stage('B', items, args.big_budget, workers)

    wall = time.time() - t0
    print(f'done: phase 2 in {wall / 60:.1f} min; stages {json.dumps(counts)}', flush=True)
    write_json(HERE / 'phase2_run.json', OrderedDict(
        budget=args.budget, big_budget=args.big_budget, cap=args.cap, radius=args.radius, top=args.top,
        n_aca=args.n_aca, workers=args.workers, selected=[t['name'] for t in chosen],
        stages=counts, stage_wall_seconds=walls, wall_seconds=round(wall, 1),
        started_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(t0)),
        finished_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())))
    if not args.no_verify:
        subprocess.run([sys.executable, '-m', 'research.autchoice_20260910.applied.verify_applied'],
                       cwd=HERE.parents[2], check=False)


if __name__ == '__main__':
    main()
