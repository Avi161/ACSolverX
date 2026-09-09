"""Orbit search: AC moves between Aut(F2)-orbit representatives.

The ACA classes are closed under Aut(F2), so a search may re-root at the
Whitehead-minimal representative (``autcanon_fast.aut_min``: the mu-ladder's
canonicaliser, all 20 Whitehead automorphisms) after every AC move.  Unlike the
mu-probe, which searched raw states and only measured mu, this search EXPANDS
FROM THE ORBIT REPRESENTATIVE, so a move that lengthens the raw pair but lands
in a short orbit keeps the frontier short and lets chains of moves run at the
floor.  Priority: (mu, S20 score of the rep).  Children: the census kernel's
Definition 2.1 children of the rep; every child with raw total <= mu_root +
``slack`` is canonicalised (others are dropped: they cannot lower mu below the
floor in one step by more than they exceed it, and this keeps the cost at
~0.4 ms per canonicalisation).

Every path is a mixed sequence: substitution moves (replayed with
``words.replay_move``) alternating with orbit steps (``rep = aut_min(state)``,
checked by recomputing ``aut_min`` on replay).  A descent below the floor would
be a new floor for the class; a hit on the cap-14 table or on (x, y) would be
a solve of the class (a simultaneous automorphism of both relators preserves
AC-triviality: the Nielsen path from the image basis to (x, y) is AC).

Usage:
  PYTHONPATH=. python3 research/residual_20260909/u124/orbit_search.py \
      --panel data/ms_unsolved_reps/aca_124_best.csv --budget 2000 --slack 6 \
      --workers 2 --out research/residual_20260909/u124/aca124_orbit_2000.jsonl
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

from experiments.equivalence_classes.lib.words import canon_pair, replay_move  # noqa: E402
from experiments.heuristic_search.core.hexpand import expand_and_score_h  # noqa: E402
from experiments.heuristic_search.core.hfast import _arrs, compile_config  # noqa: E402
from experiments.search.heuristic_1k import pack, score_key, unpack  # noqa: E402
import autcanon_fast  # noqa: E402

_TABLE = None


def _table(stem):
    global _TABLE
    if _TABLE is None and stem != 'none':
        from research.residual_20260909.policies import ball_table_any
        _TABLE = ball_table_any(stem)
    return _TABLE


def orbit_search(pair, budget, table, slack, s_weight=20.0, mk_weight=2.0):
    mu0, rep0 = autcanon_fast.aut_min(tuple(canon_pair(*pair)))
    root = pack(tuple(rep0))
    config = {'segments': [{'upto': None, 'w': {'L': 1.0, 'S': s_weight, 'MK': mk_weight}}]}
    upto, weights, _ = compile_config(config)
    # parent[rep_key] = (parent_rep_key, move, raw_child_key)
    parent = {root: None}
    heap = [((int(mu0), float(score_key(np.frombuffer(root, dtype=np.uint8), False, 0.0, s_weight, mk_weight))), 0, root)]
    best_mu, best_key = int(mu0), root
    nodes = canon_evals = 0
    solved_key = None
    while heap and nodes < budget and solved_key is None:
        _, depth, key = heapq.heappop(heap)
        nodes += 1
        state = unpack(key)
        if len(state[0]) == len(state[1]) == 1 and state[0].lower() != state[1].lower():
            solved_key = key
            break
        a, b = _arrs(key)
        blob, offsets, lengths, segs, scores, _, _, moves, count = expand_and_score_h(
            a, b, len(key) - 1, True, upto, weights, True, True)
        raw = blob.tobytes()
        for i in range(count):
            o = int(offsets[i])
            child = raw[o:o + int(lengths[i])]
            if len(child) - 1 > mu0 + slack:
                continue
            canon_evals += 1
            mu, rep = autcanon_fast.aut_min(unpack(child))
            rep_key = pack(tuple(rep))
            if rep_key in parent:
                continue
            parent[rep_key] = (key, tuple(int(v) for v in moves[i]), child)
            mu = int(mu)
            if (mu, rep_key) < (best_mu, best_key):
                best_mu, best_key = mu, rep_key
            if table is not None and rep_key in table:
                solved_key = rep_key
                break
            score = float(score_key(np.frombuffer(rep_key, dtype=np.uint8), False, 0.0, s_weight, mk_weight))
            heapq.heappush(heap, ((mu, score), depth + 1, rep_key))

    def path_to(key):
        steps, states = [], []
        cur = key
        while cur is not None:
            states.append(list(unpack(cur)))
            previous = parent[cur]
            if previous is None:
                break
            pkey, move, raw_child = previous
            steps.append({'move': list(move), 'raw_child': list(unpack(raw_child))})
            cur = pkey
        states.reverse()
        steps.reverse()
        return states, steps

    states, steps = path_to(best_key)
    return dict(mu0=int(mu0), rep0=list(rep0), nodes=nodes, canon_evals=canon_evals,
                solved=solved_key is not None, best_mu=best_mu, best_rep=list(unpack(best_key)),
                depth=len(steps), states=states, steps=steps,
                solved_path=path_to(solved_key) if solved_key is not None else None)


def replay(states, steps):
    """Replay: substitution on the rep, then canonicalise to the next rep."""
    cur = tuple(states[0])
    for state, step in zip(states[1:], steps):
        raw = tuple(replay_move(cur, tuple(step['move'])))
        if raw != tuple(step['raw_child']):
            return False
        cur = tuple(autcanon_fast.aut_min(raw)[1])
        if cur != tuple(state):
            return False
    return True


def run_row(args):
    row, budget, stem, slack = args
    table = _table(stem)
    autcanon_fast.warm()
    started = time.perf_counter()
    r = orbit_search((row['r1'], row['r2']), budget, table, slack)
    rec = dict(name=row['name'], r1=row['r1'], r2=row['r2'], budget=budget, slack=slack,
               floor_mu=r['mu0'], best_mu=r['best_mu'], mu_reduction=r['mu0'] - r['best_mu'],
               best_rep=r['best_rep'], depth=r['depth'], path_replayed=replay(r['states'], r['steps']),
               solved=r['solved'], nodes=r['nodes'], canon_evals=r['canon_evals'],
               wall=time.perf_counter() - started, states=r['states'], steps=r['steps'])
    if r['solved']:
        s_states, s_steps = r['solved_path']
        rec.update(solved_states=s_states, solved_steps=s_steps, solved_replayed=replay(s_states, s_steps))
    return rec


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--panel', required=True)
    parser.add_argument('--budget', type=int, default=2000)
    parser.add_argument('--slack', type=int, default=6)
    parser.add_argument('--table', default='ball_cap14_aut')
    parser.add_argument('--workers', type=int, default=2)
    parser.add_argument('--out', required=True)
    args = parser.parse_args(argv)
    rows = list(csv.DictReader(open(args.panel, newline='')))
    out = Path(args.out)
    partial = out.with_suffix(out.suffix + '.partial')
    started = time.perf_counter()
    records = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool, open(partial, 'w') as stream:
        for rec in pool.map(run_row, [(row, args.budget, args.table, args.slack) for row in rows]):
            stream.write(json.dumps(rec) + '\n')
            stream.flush()
            records.append(rec)
    partial.rename(out)
    summary = dict(rows=len(records), solved=sum(r['solved'] for r in records),
                   mu_reduced=sum(r['mu_reduction'] > 0 for r in records),
                   mu_letters_saved=sum(max(0, r['mu_reduction']) for r in records),
                   replay_failures=sum(not r['path_replayed'] for r in records),
                   nodes=sum(r['nodes'] for r in records), canon_evals=sum(r['canon_evals'] for r in records),
                   max_depth=max(r['depth'] for r in records), wall=sum(r['wall'] for r in records),
                   wall_total=time.perf_counter() - started, budget=args.budget, slack=args.slack)
    out.with_suffix('.summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
