"""Sweep of the rules proved in this campaign over the states a 10,000-pop
search visits on the unsolved ACA classes.

Rules: F1 (four-block primitive merge) and F3 (twin four-block row reduction)
from ``theory/FOURBLOCK_verify.py``; BS-DEMOTE from ``bs_demote_gate``.  At
the root and at every popped state of the census search (S20_MK2, uncapped,
cap-14 table terminal) the three recognisers run; every hit is compiled; every
compiled certificate is replayed (F1/F3 through ``replay_certificate``,
BS-DEMOTE through the census decoders), after replaying the prefix path from
the root to the state with ``words.replay_move``.

Usage:
  PYTHONPATH=. python3 research/residual_20260909/u124/newmoves_sweep.py \
      --panel data/ms_unsolved_reps/aca_124_best.csv --budget 10000 \
      --out research/residual_20260909/u124/aca124_newmoves_10000.jsonl
"""
import argparse
import csv
import heapq
import json
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'research/residual_20260909/theory'))

from experiments.equivalence_classes.lib.words import canon_pair, replay_move  # noqa: E402
from experiments.heuristic_search.core.hexpand import expand_and_score_h  # noqa: E402
from experiments.heuristic_search.core.hfast import _arrs, compile_config  # noqa: E402
from experiments.search.heuristic_1k import pack, score_key, unpack  # noqa: E402
from research.residual_20260909 import bs_demote_gate  # noqa: E402
from research.residual_20260909.policies import ball_table_any  # noqa: E402
from research.supermoves_20260908.certificate_decoder import replay_elementary  # noqa: E402
from research.supermoves_20260908.certificate_decoder_compact_moves import decode_elementary  # noqa: E402
import FOURBLOCK_verify as FB  # noqa: E402


def try_rules(state, counters, reasons, budget):
    """Run the three recognisers on ``state``; return a solved certificate dict or None."""
    hit = FB.recognize_F1(state)
    if hit is not None:
        counters['F1_hits'] += 1
        cert = FB.compile_F1(state, budget=budget)
        counters['F1_compiles'] += 1
        if cert.get('solved') and FB.replay_certificate(state, cert):
            counters['F1_solved'] += 1
            return dict(rule='F1', cert=cert)
        reasons['F1:' + str(cert.get('reason'))] += 1
    hit = FB.recognize_F3(state)
    if hit is not None:
        counters['F3_hits'] += 1
        counters['F3_branch_' + hit['branch']] += 1
        cert = FB.compile_F3(state, budget=budget)
        counters['F3_compiles'] += 1
        if cert.get('solved') and FB.replay_certificate(state, cert):
            counters['F3_solved'] += 1
            return dict(rule='F3', cert=cert)
        reasons['F3:' + str(cert.get('reason'))] += 1
    label = bs_demote_gate.recognize(state)
    if label is not None:
        counters['BSD_hits'] += 1
        if bs_demote_gate.demotable(label):
            counters['BSD_demotable'] += 1
            cert = bs_demote_gate.complete(state, budget=budget)
            counters['BSD_compiles'] += 1
            if cert.get('solved'):
                moves = decode_elementary(list(state), cert['states'], cert['steps'], cert.get('elementary_tail'))
                final = replay_elementary(list(state), moves)
                if sorted(w.lower() for w in final) == ['x', 'y']:
                    counters['BSD_solved'] += 1
                    return dict(rule='BS-DEMOTE', cert=cert)
            reasons['BSD:' + str(cert.get('reason'))] += 1
        else:
            reasons['BSD:label_' + '_'.join(map(str, label))] += 1
    return None


def sweep_row(pair, budget, table, macro_budget=10000):
    counters, reasons = Counter(), Counter()
    root = pack(canon_pair(*pair))
    upto, weights, _ = compile_config({'segments': [{'upto': None, 'w': {'L': 1.0, 'S': 20.0, 'MK': 2.0}}]})
    heap = [(float(score_key(np.frombuffer(root, dtype=np.uint8), False, 0.0, 20.0, 2.0)), 0, root)]
    parent = {root: None}
    nodes = 0
    solution = None
    while heap and nodes < budget and solution is None:
        _, depth, key = heapq.heappop(heap)
        nodes += 1
        state = unpack(key)
        counters['states_tested'] += 1
        found = try_rules(state, counters, reasons, macro_budget)
        if found is not None:
            # replay the prefix from the root
            cur, ok = tuple(canon_pair(*pair)), True
            chain, k = [], key
            while parent[k] is not None:
                pk, move = parent[k]
                chain.append((move, unpack(k)))
                k = pk
            for move, st in reversed(chain):
                cur = tuple(replay_move(cur, tuple(move)))
                ok = ok and cur == tuple(st)
            solution = dict(rule=found['rule'], state=list(state), prefix_moves=len(chain),
                            prefix_replayed=ok, certificate_work=found['cert'].get('work'))
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
            if table is not None and child in table:
                solution = dict(rule='table', state=list(unpack(child)))
                break
            heapq.heappush(heap, (float(scores[i]), depth + 1, child))
    return dict(nodes=nodes, counters=dict(counters), reasons=dict(reasons), solution=solution)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--panel', required=True)
    parser.add_argument('--budget', type=int, default=10000)
    parser.add_argument('--out', required=True)
    args = parser.parse_args(argv)
    table = ball_table_any('ball_cap14_aut')
    rows = list(csv.DictReader(open(args.panel, newline='')))
    out = Path(args.out)
    partial = out.with_suffix(out.suffix + '.partial')
    records = []
    with open(partial, 'w') as stream:
        for row in rows:
            t0 = time.perf_counter()
            r = sweep_row((row['r1'], row['r2']), args.budget, table)
            rec = dict(name=row['name'], r1=row['r1'], r2=row['r2'], budget=args.budget,
                       solved=r['solution'] is not None, wall=time.perf_counter() - t0, **r)
            stream.write(json.dumps(rec) + '\n')
            stream.flush()
            records.append(rec)
    partial.rename(out)
    total = Counter()
    reasons = Counter()
    for rec in records:
        total.update(rec['counters'])
        reasons.update(rec['reasons'])
    summary = dict(rows=len(records), solved=sum(r['solved'] for r in records),
                   rows_with_any_hit=sum(1 for r in records if any(k.endswith('_hits') and v for k, v in r['counters'].items())),
                   counters=dict(total), reasons=dict(reasons.most_common(12)),
                   wall=sum(r['wall'] for r in records))
    out.with_suffix('.summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
