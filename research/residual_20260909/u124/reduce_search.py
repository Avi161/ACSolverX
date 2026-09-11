"""Length-reduction probe for the 124 unsolved Miller-Schupp ACA classes.

Runs the census search (S20_MK2 ordering, uncapped expansion, cap-14
automorphism-closed backward ball as terminal) for a fixed budget and, unlike
``plain_search_ball.mixed_search``, keeps the parent map so the path to the
SHORTEST state reached can be reconstructed and replayed.  Every reported
reduction is therefore a certified sequence of engine moves (Definition 2.1
substitutions, plus the four Nielsen automorphisms for the ``aut_edges`` arm),
replayed with the pure-Python ``words.replay_move`` / ``words.apply_pair``.

Usage:
  PYTHONPATH=. python3 research/residual_20260909/u124/reduce_search.py \
      --panel data/ms_unsolved_reps/aca_124_best.csv --budget 10000 \
      --arms s20,aut_edges --table ball_cap14_aut --workers 2 \
      --out research/residual_20260909/u124/aca124_reduce_10000.jsonl
"""
import argparse
import csv
import heapq
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from experiments.equivalence_classes.lib.words import apply_pair, canon_pair, replay_move  # noqa: E402
from experiments.heuristic_search.core.hexpand import expand_and_score_h  # noqa: E402
from experiments.heuristic_search.core.hfast import _arrs, compile_config  # noqa: E402
from experiments.search.heuristic_1k import NIELSEN, pack, score_key, unpack  # noqa: E402

_TABLE = None


def _table(stem):
    global _TABLE
    if _TABLE is None:
        from research.residual_20260909.policies import ball_table_any
        _TABLE = ball_table_any(stem)
    return _TABLE


def _measure(key):
    separator = key.index(0)
    return len(key) - 1, max(separator, len(key) - separator - 1)


def search_best(pair, arm, budget, table, s_weight=20.0, mk_weight=2.0, w_weight=0.0,
                depth_switch=None, late_s=None, late_mk=None, segments=None, cap=None):
    """``segments``: list of (upto_total_length, S, MK) for length-dependent weights
    (kernel-side); ``depth_switch``/``late_s``/``late_mk``: after that search depth the
    S/MK weights change (recomputed per child with ``score_key``); ``w_weight``: the
    Whitehead-adjusted score of the ``whitehead2`` arm."""
    whitehead = w_weight != 0.0
    root = pack(canon_pair(*pair))
    priority = score_key(np.frombuffer(root, dtype=np.uint8), whitehead, w_weight, s_weight, mk_weight)
    heap = [(priority, 0, root, None, 0, ())]
    seen = {root}
    parent = {root: None}          # popped states only (plus the root)
    pending = {}                   # generated-but-not-popped children we may need a path to
    best, (best_total, best_max) = root, _measure(root)
    best_at = 0
    if segments:
        config = {'segments': [{'upto': up, 'w': {'L': 1.0, 'S': sw, 'MK': mk}} for up, sw, mk in segments]}
    else:
        config = {'segments': [{'upto': None, 'w': {'L': 1.0, 'S': s_weight, 'MK': mk_weight}}]}
    upto, weights, _ = compile_config(config)
    nodes = 0
    solved_key = None
    ball_depth = None

    def child_score(child, kernel_score, depth):
        if depth_switch is not None and depth >= depth_switch:
            return float(score_key(np.frombuffer(child, dtype=np.uint8), whitehead, w_weight,
                                   s_weight if late_s is None else late_s,
                                   mk_weight if late_mk is None else late_mk))
        if whitehead:
            return float(score_key(np.frombuffer(child, dtype=np.uint8), True, w_weight, s_weight, mk_weight))
        return float(kernel_score)

    def consider(child, key, kind, payload):
        """Register a new child; returns 'dup', 'hit' or 'new'."""
        nonlocal best, best_total, best_max, best_at, solved_key, ball_depth
        if child in seen:
            return 'dup'
        seen.add(child)
        total, mx = _measure(child)
        if (total, mx, child) < (best_total, best_max, best):
            if best in pending:
                del pending[best]
            best, best_total, best_max, best_at = child, total, mx, nodes
            pending[child] = (key, kind, payload)
        if table is not None and child in table:
            solved_key, ball_depth = child, table[child][0]
            pending[child] = (key, kind, payload)
            return 'hit'
        return 'new'

    if table is not None and root in table:
        solved_key, ball_depth = root, table[root][0]
    while solved_key is None and heap and nodes < budget:
        _, depth, key, pkey, pkind, ppayload = heapq.heappop(heap)
        nodes += 1
        if key not in parent:
            parent[key] = None if pkey is None else (pkey, pkind, ppayload)
            pending.pop(key, None)
        state = unpack(key)
        if len(state[0]) == len(state[1]) == 1 and state[0].lower() != state[1].lower():
            solved_key = key
            break
        a, b = _arrs(key)
        blob, offsets, lengths, segs, scores, _, _, moves, count = expand_and_score_h(
            a, b, cap if cap is not None else len(key) - 1, True, upto, weights, True, True)
        raw = blob.tobytes()
        hit = False
        for i in range(count):
            o = int(offsets[i])
            child = raw[o:o + int(lengths[i])]
            status = consider(child, key, 0, tuple(int(v) for v in moves[i]))
            if status == 'hit':
                hit = True
                break
            if status == 'dup':
                continue          # already generated: never re-push (the census kernel's rule)
            heapq.heappush(heap, (child_score(child, scores[i], depth + 1), depth + 1, child,
                                  key, 0, tuple(int(v) for v in moves[i])))
        if hit:
            break
        if arm == 'aut_edges':
            for transform in NIELSEN:
                nxt = apply_pair(state, transform)
                if cap is not None and max(map(len, nxt)) > cap:
                    continue
                child = pack(nxt)
                status = consider(child, key, 1, transform)
                if status == 'hit':
                    hit = True
                    break
                if status == 'new':
                    heapq.heappush(heap, (child_score(child, 0.0, depth + 1), depth + 1, child, key, 1, transform))
            if hit:
                break

    def path_to(key):
        states, steps = [], []
        cur = key
        while cur is not None:
            states.append(list(unpack(cur)))
            previous = parent[cur] if cur in parent else pending[cur]
            if previous is None:
                break
            cur, kind, payload = previous
            steps.append({'kind': 'substitution', 'move': list(payload)} if kind == 0
                         else {'kind': 'automorphism', 'images': dict(payload)})
        states.reverse()
        steps.reverse()
        return states, steps

    return dict(root=list(unpack(root)), nodes=nodes, solved=solved_key is not None, pops_to_best=best_at,
                ball_depth=ball_depth, best=path_to(best), best_total=best_total, best_max=best_max,
                solved_path=path_to(solved_key) if solved_key is not None else None)


def replay(states, steps):
    """Pure-Python replay of a mixed path; True iff each step reproduces the next state."""
    cur = tuple(states[0])
    for state, step in zip(states[1:], steps):
        if step['kind'] == 'substitution':
            cur = replay_move(cur, tuple(step['move']))
        else:
            cur = tuple(canon_pair(*apply_pair(cur, step['images'])))
        if tuple(state) != tuple(cur):
            return False
    return True


def run_row(args):
    row, arms, budget, stem, kw = args
    table = _table(stem)
    pair = (row['r1'], row['r2'])
    out = []
    for arm in arms:
        started = time.perf_counter()
        result = search_best(pair, arm, budget, table, **kw)
        states, steps = result['best']
        raw_total = len(row['r1']) + len(row['r2'])
        root_total = sum(map(len, result['root']))
        record = dict(name=row['name'], arm=arm, budget=budget, config=kw, r1=row['r1'], r2=row['r2'],
                      raw_total=raw_total, root=result['root'], root_total=root_total,
                      root_max=max(map(len, result['root'])),
                      best_pair=states[-1], best_total=result['best_total'], best_max=result['best_max'],
                      reduction=root_total - result['best_total'], pops_to_best=result['pops_to_best'],
                      path_moves=len(steps),
                      path_substitutions=sum(1 for s in steps if s['kind'] == 'substitution'),
                      path_automorphisms=sum(1 for s in steps if s['kind'] == 'automorphism'),
                      path_replayed=replay(states, steps), solved=result['solved'],
                      ball_depth=result['ball_depth'], nodes=result['nodes'],
                      wall=time.perf_counter() - started,
                      best_states=states, best_steps=steps)
        if result['solved']:
            s_states, s_steps = result['solved_path']
            record.update(solved_states=s_states, solved_steps=s_steps, solved_replayed=replay(s_states, s_steps))
        out.append(record)
    return out


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--panel', required=True)
    parser.add_argument('--budget', type=int, default=10000)
    parser.add_argument('--arms', default='s20,aut_edges')
    parser.add_argument('--table', default='ball_cap14_aut')
    parser.add_argument('--workers', type=int, default=2)
    parser.add_argument('--out', required=True)
    parser.add_argument('--cap', type=int, default=None, help='per-relator length cap (None = parent total length, the census default)')
    parser.add_argument('--s-weight', type=float, default=20.0)
    parser.add_argument('--mk-weight', type=float, default=2.0)
    parser.add_argument('--w-weight', type=float, default=0.0)
    parser.add_argument('--depth-switch', type=int, default=None)
    parser.add_argument('--late-s', type=float, default=None)
    parser.add_argument('--late-mk', type=float, default=None)
    parser.add_argument('--segments', default=None,
                        help='length-dependent weights: "upto:S:MK,upto:S:MK,..." (last upto may be none)')
    args = parser.parse_args(argv)
    segments = None
    if args.segments:
        segments = []
        for part in args.segments.split(','):
            up, sw, mk = part.split(':')
            segments.append((None if up == 'none' else float(up), float(sw), float(mk)))
    kw = dict(s_weight=args.s_weight, mk_weight=args.mk_weight, w_weight=args.w_weight,
              depth_switch=args.depth_switch, late_s=args.late_s, late_mk=args.late_mk, segments=segments, cap=args.cap)
    with open(args.panel, newline='') as stream:
        rows = list(csv.DictReader(stream))
    arms = args.arms.split(',')
    jobs = [(row, arms, args.budget, args.table, kw) for row in rows]
    out = Path(args.out)
    partial = out.with_suffix(out.suffix + '.partial')
    started = time.perf_counter()
    records = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool, open(partial, 'w') as stream:
        for batch in pool.map(run_row, jobs):
            for record in batch:
                stream.write(json.dumps(record) + '\n')
                records.append(record)
            stream.flush()
    partial.rename(out)
    summary = {}
    for arm in arms:
        rs = [r for r in records if r['arm'] == arm]
        summary[arm] = dict(rows=len(rs), solved=sum(r['solved'] for r in rs),
                            reduced=sum(r['reduction'] > 0 for r in rs),
                            replay_failures=sum(not r['path_replayed'] for r in rs),
                            total_length_before=sum(r['root_total'] for r in rs),
                            total_length_after=sum(r['best_total'] for r in rs),
                            max_relator_reduced=sum(r['best_max'] < r['root_max'] for r in rs),
                            nodes=sum(r['nodes'] for r in rs), wall=sum(r['wall'] for r in rs))
    summary['wall_total'] = time.perf_counter() - started
    out.with_suffix('.summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
