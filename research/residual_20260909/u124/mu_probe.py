"""mu-probe: does the census search reach any state whose Aut(F2)-orbit-minimal
total length (the mu-ladder's ``mu``, computed with the ladder's own
``autcanon_fast.aut_min``) is below the recorded floor of its ACA class?

Per row and arm: run the S20_MK2 search (uncapped expansion, cap-14
automorphism-closed table as terminal) for ``--budget`` pops, apply
``aut_min`` to every POPPED state and to every generated state whose raw total
length is at most root_total + ``--slack``, and keep the state of least mu
(ties: least raw total).  The path from the root to that state is a sequence of
Definition 2.1 engine moves (plus Nielsen automorphisms in the ``aut_edges``
arm) and is replayed with the pure-Python ``words`` functions; the final
Whitehead minimisation is the free Aut(F2) action the ACA classes are already
closed under, so a mu below the floor would be a genuine new floor for the class.

Usage:
  PYTHONPATH=. python3 research/residual_20260909/u124/mu_probe.py \
      --panel data/ms_unsolved_reps/aca_124_best.csv --budget 10000 \
      --arms s20,aut_edges --workers 2 --out research/residual_20260909/u124/aca124_mu_10000.jsonl
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

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from experiments.equivalence_classes.lib.words import apply_pair, canon_pair, replay_move  # noqa: E402
from experiments.heuristic_search.core.hexpand import expand_and_score_h  # noqa: E402
from experiments.heuristic_search.core.hfast import _arrs, compile_config  # noqa: E402
from experiments.search.heuristic_1k import NIELSEN, pack, score_key, unpack  # noqa: E402
import autcanon_fast  # noqa: E402

_TABLE = None


def _table(stem):
    global _TABLE
    if _TABLE is None and stem != 'none':
        from research.residual_20260909.policies import ball_table_any
        _TABLE = ball_table_any(stem)
    return _TABLE


def probe(pair, arm, budget, table, slack, s_weight=20.0, mk_weight=2.0):
    root = pack(canon_pair(*pair))
    root_total = len(root) - 1
    priority = score_key(np.frombuffer(root, dtype=np.uint8), False, 0.0, s_weight, mk_weight)
    heap = [(priority, 0, root)]
    parent = {root: None}
    config = {'segments': [{'upto': None, 'w': {'L': 1.0, 'S': s_weight, 'MK': mk_weight}}]}
    upto, weights, _ = compile_config(config)
    nodes = 0
    solved_key = None
    mu_evals = 0
    best_mu, best_key = autcanon_fast.aut_min(unpack(root))[0], root
    mu_evals += 1

    def evaluate(key):
        nonlocal best_mu, best_key, mu_evals
        mu_evals += 1
        mu = autcanon_fast.aut_min(unpack(key))[0]
        if (mu, len(key) - 1, key) < (best_mu, len(best_key) - 1, best_key):
            best_mu, best_key = mu, key

    def consider(child, key, kind, payload):
        nonlocal solved_key
        if child in parent:
            return False
        parent[child] = (key, kind, payload)
        if len(child) - 1 <= root_total + slack:
            evaluate(child)
        if table is not None and child in table:
            solved_key = child
            return True
        return False

    if table is not None and root in table:
        solved_key = root
    while solved_key is None and heap and nodes < budget:
        _, depth, key = heapq.heappop(heap)
        nodes += 1
        if len(key) - 1 > root_total + slack:
            evaluate(key)          # popped states are always evaluated
        state = unpack(key)
        if len(state[0]) == len(state[1]) == 1 and state[0].lower() != state[1].lower():
            solved_key = key
            break
        a, b = _arrs(key)
        blob, offsets, lengths, segs, scores, _, _, moves, count = expand_and_score_h(
            a, b, len(key) - 1, True, upto, weights, True, True)
        raw = blob.tobytes()
        hit = False
        for i in range(count):
            o = int(offsets[i])
            child = raw[o:o + int(lengths[i])]
            if consider(child, key, 0, tuple(int(v) for v in moves[i])):
                hit = True
                break
            heapq.heappush(heap, (float(scores[i]), depth + 1, child))
        if hit:
            break
        if arm == 'aut_edges':
            for transform in NIELSEN:
                child = pack(apply_pair(state, transform))
                if consider(child, key, 1, transform):
                    hit = True
                    break
                if parent[child] == (key, 1, transform):
                    score = score_key(np.frombuffer(child, dtype=np.uint8), False, 0.0, s_weight, mk_weight)
                    heapq.heappush(heap, (score, depth + 1, child))
            if hit:
                break

    def path_to(key):
        states, steps = [], []
        cur = key
        while cur is not None:
            states.append(list(unpack(cur)))
            previous = parent[cur]
            if previous is None:
                break
            cur, kind, payload = previous
            steps.append({'kind': 'substitution', 'move': list(payload)} if kind == 0
                         else {'kind': 'automorphism', 'images': dict(payload)})
        states.reverse()
        steps.reverse()
        return states, steps

    states, steps = path_to(best_key)
    mu, rep = autcanon_fast.aut_min(unpack(best_key))
    return dict(root=list(unpack(root)), root_total=root_total, nodes=nodes, mu_evals=mu_evals,
                solved=solved_key is not None, best_mu=int(mu), best_rep=list(rep),
                best_state=list(unpack(best_key)), best_states=states, best_steps=steps)


def replay(states, steps):
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
    row, arms, budget, stem, slack = args
    table = _table(stem)
    autcanon_fast.warm()
    out = []
    for arm in arms:
        started = time.perf_counter()
        r = probe((row['r1'], row['r2']), arm, budget, table, slack)
        floor = int(autcanon_fast.aut_min((row['r1'], row['r2']))[0])
        out.append(dict(name=row['name'], arm=arm, budget=budget, slack=slack, r1=row['r1'], r2=row['r2'],
                        floor_mu=floor, root_total=r['root_total'], best_mu=r['best_mu'],
                        mu_reduction=floor - r['best_mu'], best_rep=r['best_rep'], best_state=r['best_state'],
                        path_moves=len(r['best_steps']), path_replayed=replay(r['best_states'], r['best_steps']),
                        solved=r['solved'], nodes=r['nodes'], mu_evals=r['mu_evals'],
                        wall=time.perf_counter() - started, best_states=r['best_states'], best_steps=r['best_steps']))
    return out


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--panel', required=True)
    parser.add_argument('--budget', type=int, default=10000)
    parser.add_argument('--arms', default='s20,aut_edges')
    parser.add_argument('--table', default='ball_cap14_aut')
    parser.add_argument('--slack', type=int, default=2)
    parser.add_argument('--workers', type=int, default=2)
    parser.add_argument('--out', required=True)
    args = parser.parse_args(argv)
    rows = list(csv.DictReader(open(args.panel, newline='')))
    arms = args.arms.split(',')
    out = Path(args.out)
    partial = out.with_suffix(out.suffix + '.partial')
    started = time.perf_counter()
    records = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool, open(partial, 'w') as stream:
        for batch in pool.map(run_row, [(row, arms, args.budget, args.table, args.slack) for row in rows]):
            for record in batch:
                stream.write(json.dumps(record) + '\n')
                records.append(record)
            stream.flush()
    partial.rename(out)
    summary = {}
    for arm in arms:
        rs = [r for r in records if r['arm'] == arm]
        summary[arm] = dict(rows=len(rs), solved=sum(r['solved'] for r in rs),
                            mu_reduced=sum(r['mu_reduction'] > 0 for r in rs),
                            mu_letters_saved=sum(max(0, r['mu_reduction']) for r in rs),
                            replay_failures=sum(not r['path_replayed'] for r in rs),
                            mu_evals=sum(r['mu_evals'] for r in rs), nodes=sum(r['nodes'] for r in rs),
                            wall=sum(r['wall'] for r in rs))
    summary['wall_total'] = time.perf_counter() - started
    out.with_suffix('.summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
