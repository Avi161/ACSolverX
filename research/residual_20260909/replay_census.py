"""Re-decode and re-replay every certificate of a census result directory in
fresh worker processes, independently of the census run that produced it.

Each solved row's stored mixed path (``states``, ``steps``) is decoded with
``certificate_decoder_compact_moves.decode_elementary`` and the returned
elementary moves are replayed with ``certificate_decoder.replay_elementary``
from the row's own ``pair``; the replayed pair must be exactly ``['x', 'y']``
up to letter case (the census's own contract, ``harness.run_row``).

Usage: PYTHONPATH=. python3 -m research.residual_20260909.replay_census \
           --result-dir results/heuristic_search/<dir> [--workers 4] [--out replay_check.json]
"""
import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _check_shard(path):
    from research.supermoves_20260908.certificate_decoder import replay_elementary
    from research.supermoves_20260908.certificate_decoder_compact_moves import decode_elementary
    started = time.perf_counter()
    rows = solved = replayed_ok = moves_total = 0
    failures = []
    with open(path) as stream:
        for line in stream:
            row = json.loads(line)
            rows += 1
            if not row.get('solved'):
                continue
            solved += 1
            pair = list(row['pair'])
            try:
                moves = decode_elementary(pair, row['states'], row['steps'], row.get('elementary_tail'))
                final = replay_elementary(pair, moves)
                ok = sorted(word.lower() for word in final) == ['x', 'y'] and len(moves) == row['elementary_count']
            except Exception as error:  # noqa: BLE001 - any failure is a finding
                ok, moves = False, []
                failures.append((row['name'], f'{type(error).__name__}: {error}'))
            if ok:
                replayed_ok += 1
                moves_total += len(moves)
            elif not failures or failures[-1][0] != row['name']:
                failures.append((row['name'], 'replay did not end at (x, y) or move count differs'))
    return dict(shard=Path(path).name, rows=rows, solved=solved, replayed_ok=replayed_ok,
                elementary_moves=moves_total, failures=failures, wall=time.perf_counter() - started)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--result-dir', required=True)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--out', default='replay_check.json')
    args = parser.parse_args(argv)
    out_dir = ROOT / args.result_dir
    shards = sorted(str(p) for p in out_dir.glob('rows_*.jsonl'))
    started = time.perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        reports = list(pool.map(_check_shard, shards))
    wall = time.perf_counter() - started
    totals = dict(shards=len(reports), rows=sum(r['rows'] for r in reports),
                  solved=sum(r['solved'] for r in reports),
                  replayed_ok=sum(r['replayed_ok'] for r in reports),
                  elementary_moves=sum(r['elementary_moves'] for r in reports),
                  failures=[f for r in reports for f in r['failures']],
                  replay_wall=wall, replay_cpu_sum=sum(r['wall'] for r in reports),
                  workers=args.workers, result_dir=args.result_dir)
    (out_dir / args.out).write_text(json.dumps(totals, indent=2) + '\n')
    print(json.dumps({k: v for k, v in totals.items() if k != 'failures'}, indent=2))
    print('failures:', len(totals['failures']), totals['failures'][:10])
    return 0 if totals['solved'] == totals['replayed_ok'] and not totals['failures'] else 1


if __name__ == '__main__':
    sys.exit(main())
