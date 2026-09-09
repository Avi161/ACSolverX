"""All-gates supermove sweep on the 124 unsolved ACA classes.

Runs the table mid-search (``mid_search_ball.mixed_search``) with EVERY
recogniser and compiler switched on and probing at generation time: general
consecutive-BS collapse with Britton preflight, two-block unimodular reduction,
primitive-donor completion (one-occurrence and Christoffel gates), stable-power,
splice-power and stable-square collapses, BS escape feature, cap-14 table.
Records the per-row counters the search returns so we can see whether any
theory hypothesis fires on any visited state, and decodes + replays any solve.

Usage:
  PYTHONPATH=. python3 research/residual_20260909/u124/supermove_sweep.py \
      --panel data/ms_unsolved_reps/aca_124_best.csv --budget 10000 \
      --out research/residual_20260909/u124/aca124_supermoves_10000.jsonl
"""
import argparse
import csv
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))

from research.residual_20260909 import mid_search_ball  # noqa: E402
from research.residual_20260909.policies import ball_table_any  # noqa: E402
from research.supermoves_20260908.certificate_decoder import replay_elementary  # noqa: E402
from research.supermoves_20260908.certificate_decoder_compact_moves import decode_elementary  # noqa: E402

FLAGS = dict(use_bs=True, general_bs=True, use_two_block=True, probe_when='generated',
             use_primitive=True, use_stable_square=True, use_bs_preflight=True,
             use_stable_power=True, use_splice_power=True, use_christoffel=True,
             bs_escape_weight=4.0)
SKIP = {'states', 'steps', 'elementary_tail', 'best_state'}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--panel', required=True)
    parser.add_argument('--budget', type=int, default=10000)
    parser.add_argument('--arm', default='s20')
    parser.add_argument('--out', required=True)
    args = parser.parse_args(argv)
    table = ball_table_any('ball_cap14_aut')
    rows = list(csv.DictReader(open(args.panel, newline='')))
    out = Path(args.out)
    partial = out.with_suffix(out.suffix + '.partial')
    records = []
    with open(partial, 'w') as stream:
        for row in rows:
            pair = (row['r1'], row['r2'])
            started = time.perf_counter()
            try:
                result = mid_search_ball.mixed_search(pair, args.arm, budget=args.budget, cap=None,
                                                     table=table, **FLAGS)
                error = None
            except Exception as exc:  # noqa: BLE001
                result, error = {}, f'{type(exc).__name__}: {exc}'
            rec = dict(name=row['name'], r1=row['r1'], r2=row['r2'], budget=args.budget,
                       wall=time.perf_counter() - started, error=error)
            rec.update({k: v for k, v in result.items() if k not in SKIP and not k.startswith('_')})
            rec['min_total_length_seen'] = result.get('min_total_length_seen')
            if result.get('solved'):
                moves = decode_elementary(list(pair), result['states'], result['steps'], result.get('elementary_tail'))
                final = replay_elementary(list(pair), moves)
                rec.update(verified=sorted(w.lower() for w in final) == ['x', 'y'], elementary_count=len(moves),
                           states=result['states'], steps=result['steps'])
            stream.write(json.dumps(rec, default=str) + '\n')
            stream.flush()
            records.append(rec)
    partial.rename(out)
    counters = {}
    for rec in records:
        for k, v in rec.items():
            if isinstance(v, (int, float)) and not isinstance(v, bool) and k not in ('budget', 'wall'):
                counters[k] = counters.get(k, 0) + v
    summary = dict(rows=len(records), solved=sum(bool(r.get('solved')) for r in records),
                   verified=sum(bool(r.get('verified')) for r in records),
                   errors=sum(1 for r in records if r['error']),
                   shorter_total=sum(1 for r in records if r.get('min_total_length_seen') is not None
                                     and r['min_total_length_seen'] < len(r['r1']) + len(r['r2'])),
                   wall=sum(r['wall'] for r in records), counters=counters,
                   first_error=next((r['error'] for r in records if r['error']), None))
    out.with_suffix('.summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
