"""aut-start: change basis first, then descend.

For each class: enumerate the Aut(F2)-orbit members reachable from the stored
Aut-minimal representative by composing up to ``--depth`` of the 20 Whitehead
automorphisms (``autcanon.AUTOS``), keep those with raw total length at most
floor + ``--start-slack`` (at most ``--max-starts`` of them, shortest first),
and run the census search (S20_MK2, uncapped, cap-14 table terminal) for
``--budget`` pops FROM EACH START.  Per start we record how low the search got
(best raw total, its Whitehead-minimal mu), how fast (pops until the best state
was first generated), and whether it solved; per class the best over starts;
and across the panel the mean gain by FIRST automorphism, which is what
"does a particular initial automorphism make the descent smoother" asks.

Every solve is a mixed path: the start automorphisms (``apply_pair``), the
substitution moves (``words.replay_move``) and the table tail; it is replayed
here and reported with ``solved_replayed``.

Usage:
  PYTHONPATH=. python3 research/residual_20260909/u124/aut_start_search.py \
      --panel data/ms_unsolved_reps/aca_124_best.csv --budget 1000 --depth 2 \
      --start-slack 6 --max-starts 40 --workers 1 \
      --out research/residual_20260909/u124/aca124_autstart_1000.jsonl
"""
import argparse
import csv
import heapq
import json
import sys
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from experiments.equivalence_classes.lib.autcanon import AUTOS  # noqa: E402
from experiments.equivalence_classes.lib.words import apply_pair, canon_pair, replay_move  # noqa: E402
from experiments.heuristic_search.core.hexpand import expand_and_score_h  # noqa: E402
from experiments.heuristic_search.core.hfast import _arrs, compile_config  # noqa: E402
from experiments.search.heuristic_1k import pack, score_key, unpack  # noqa: E402
from research.residual_20260909.backward_table import tail as ball_tail  # noqa: E402
import autcanon_fast  # noqa: E402

_TABLE = None


def _table(stem):
    global _TABLE
    if _TABLE is None and stem != 'none':
        from research.residual_20260909.policies import ball_table_any
        _TABLE = ball_table_any(stem)
    return _TABLE


def starts_for(pair, depth, slack, max_starts):
    """Orbit members within ``slack`` letters of the floor, with the automorphism
    index sequence that produced each (shortest sequence wins)."""
    root = tuple(canon_pair(*pair))
    floor = sum(map(len, root))
    seen = {root: ()}
    frontier = [root]
    for _ in range(depth):
        nxt = []
        for p in frontier:
            for k, auto in enumerate(AUTOS):
                q = tuple(canon_pair(*apply_pair(p, auto)))
                if q in seen or sum(map(len, q)) > floor + slack:
                    continue
                seen[q] = seen[p] + (k,)
                nxt.append(q)
        frontier = nxt
    items = sorted(seen.items(), key=lambda kv: (sum(map(len, kv[0])), len(kv[1]), kv[0]))
    return items[:max_starts]


def search_from(start, budget, table, s_weight=20.0, mk_weight=2.0):
    root = pack(start)
    priority = float(score_key(np.frombuffer(root, dtype=np.uint8), False, 0.0, s_weight, mk_weight))
    heap = [(priority, 0, root)]
    parent = {root: None}
    best, best_total, best_at = root, len(root) - 1, 0
    config = {'segments': [{'upto': None, 'w': {'L': 1.0, 'S': s_weight, 'MK': mk_weight}}]}
    upto, weights, _ = compile_config(config)
    nodes = 0
    solved_key, ball_depth = None, None
    if table is not None and root in table:
        solved_key, ball_depth = root, table[root][0]
    while solved_key is None and heap and nodes < budget:
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
            if child in parent:
                continue
            parent[child] = (key, tuple(int(v) for v in moves[i]))
            if (len(child) - 1, child) < (best_total, best):
                best, best_total, best_at = child, len(child) - 1, nodes
            if table is not None and child in table:
                solved_key, ball_depth = child, table[child][0]
                break
            heapq.heappush(heap, (float(scores[i]), depth + 1, child))

    def path_to(key):
        states, steps = [], []
        cur = key
        while cur is not None:
            states.append(list(unpack(cur)))
            previous = parent[cur]
            if previous is None:
                break
            cur, move = previous
            steps.append(list(move))
        states.reverse()
        steps.reverse()
        return states, steps

    out = dict(nodes=nodes, best_total=best_total, best_state=list(unpack(best)), pops_to_best=best_at,
               solved=solved_key is not None)
    if solved_key is not None:
        states, steps = path_to(solved_key)
        if ball_depth is not None:
            tail_states, tail_steps = ball_tail(table, solved_key)
            out['tail_states'], out['tail_steps'] = [list(s) for s in tail_states], tail_steps
        out['states'], out['steps'] = states, steps
    return out


def run_row(args):
    row, budget, depth, slack, max_starts, stem = args
    table = _table(stem)
    autcanon_fast.warm()
    pair = (row['r1'], row['r2'])
    floor = int(autcanon_fast.aut_min(tuple(canon_pair(*pair)))[0])
    records = []
    for start, seq in starts_for(pair, depth, slack, max_starts):
        t0 = time.perf_counter()
        r = search_from(start, budget, table)
        mu = int(autcanon_fast.aut_min(tuple(r['best_state']))[0])
        rec = dict(name=row['name'], floor=floor, start=list(start), start_total=sum(map(len, start)),
                   aut_seq=list(seq), first_auto=(seq[0] if seq else None),
                   best_total=r['best_total'], best_mu=mu, gain=floor - r['best_total'], mu_gain=floor - mu,
                   pops_to_best=r['pops_to_best'], solved=r['solved'], nodes=r['nodes'],
                   wall=time.perf_counter() - t0)
        if r['solved']:
            # replay: start automorphisms, then substitutions, then the table tail
            cur = tuple(canon_pair(*pair))
            for k in seq:
                cur = tuple(canon_pair(*apply_pair(cur, AUTOS[k])))
            ok = cur == tuple(start)
            for state, move in zip(r['states'][1:], r['steps']):
                cur = tuple(replay_move(cur, tuple(move)))
                ok = ok and cur == tuple(state)
            for state, step in zip(r.get('tail_states', [])[1:], r.get('tail_steps', [])):
                if isinstance(step, dict) and step.get('kind') == 'automorphism':
                    cur = tuple(canon_pair(*apply_pair(cur, step['images'])))
                else:
                    move = step['move'] if isinstance(step, dict) else step
                    move = tuple(int(v) for v in (move.split('_') if isinstance(move, str) else move))
                    cur = tuple(replay_move(cur, move))
                ok = ok and cur == tuple(state)
            ok = ok and sorted(w.lower() for w in cur) == ['x', 'y']
            rec.update(solved_replayed=ok, states=r['states'], steps=r['steps'],
                       tail_states=r.get('tail_states'), tail_steps=r.get('tail_steps'))
        records.append(rec)
    return records


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--panel', required=True)
    parser.add_argument('--budget', type=int, default=1000)
    parser.add_argument('--depth', type=int, default=2)
    parser.add_argument('--start-slack', type=int, default=6)
    parser.add_argument('--max-starts', type=int, default=40)
    parser.add_argument('--table', default='ball_cap14_aut')
    parser.add_argument('--workers', type=int, default=1)
    parser.add_argument('--out', required=True)
    args = parser.parse_args(argv)
    rows = list(csv.DictReader(open(args.panel, newline='')))
    out = Path(args.out)
    partial = out.with_suffix(out.suffix + '.partial')
    started = time.perf_counter()
    records = []
    jobs = [(row, args.budget, args.depth, args.start_slack, args.max_starts, args.table) for row in rows]
    with ProcessPoolExecutor(max_workers=args.workers) as pool, open(partial, 'w') as stream:
        for batch in pool.map(run_row, jobs):
            for rec in batch:
                stream.write(json.dumps(rec) + '\n')
                records.append(rec)
            stream.flush()
    partial.rename(out)
    by_row = defaultdict(list)
    for r in records:
        by_row[r['name']].append(r)
    by_first = defaultdict(list)
    for r in records:
        by_first[str(r['first_auto'])].append(r)
    summary = dict(rows=len(by_row), starts=len(records), budget=args.budget,
                   solved_starts=sum(r['solved'] for r in records),
                   solved_rows=sum(any(r['solved'] for r in rs) for rs in by_row.values()),
                   rows_with_raw_gain=sum(any(r['gain'] > 0 for r in rs) for rs in by_row.values()),
                   rows_with_mu_gain=sum(any(r['mu_gain'] > 0 for r in rs) for rs in by_row.values()),
                   starts_reaching_floor=sum(r['best_total'] <= r['floor'] for r in records),
                   mean_starts_per_row=len(records) / max(1, len(by_row)),
                   by_first_auto={k: dict(starts=len(v), mean_best_minus_floor=sum(r['best_total'] - r['floor'] for r in v) / len(v),
                                          reached_floor=sum(r['best_total'] <= r['floor'] for r in v),
                                          mean_pops_to_best=sum(r['pops_to_best'] for r in v) / len(v),
                                          auto=(AUTOS[int(k)] if k != 'None' else 'identity'))
                                  for k, v in sorted(by_first.items(), key=lambda kv: (kv[0] == 'None', kv[0]))},
                   wall_total=time.perf_counter() - started)
    out.with_suffix('.summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({k: v for k, v in summary.items() if k != 'by_first_auto'}, indent=2))


if __name__ == '__main__':
    main()
