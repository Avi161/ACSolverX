"""Replay every solved certificate in the given JSONL(.gz) records with the independent
verifiers (string certificates -> verify.replay, hybrid certificates -> hfhybrid.verify_hybrid,
dynamic-rank certificates -> research/ac_dynamic_rank_20260913/verify.replay)."""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.ac_dynamic_rank_20260913 import verify as DV  # noqa: E402
from research.ac_hashfree_cascade_20260914 import hfhybrid, verify  # noqa: E402


def records(path):
    opener = gzip.open if str(path).endswith('.gz') else open
    with opener(path, 'rt') as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def main(argv):
    grand_ok = grand_total = 0
    for path in argv:
        ok = total = skipped = 0
        for rec in records(path):
            if not rec.get('solved'):
                continue
            pair = (rec['r1'], rec['r2'])
            steps = rec.get('steps')
            if steps is None and rec.get('path') is None:
                skipped += 1
                continue
            total += 1
            try:
                if 'path' in rec and steps is None:          # dynamic-rank record
                    root = [list(w) for w in (DV.cyc_canon(tuple(x)) for x in
                            (tuple(__import__('research.ac_dynamic_rank_20260913.dynrank', fromlist=['parse']).parse(w))
                             for w in pair))]
                    DV.replay(root, rec['path'], rec['params'].get('min_uses', 2), rec.get('root_relabel'))
                elif any(s.get('kind') == 'dyn' for s in steps):
                    hfhybrid.verify_hybrid(pair, steps)
                elif rec.get('params', {}).get('engine') == 'hybrid':
                    hfhybrid.verify_hybrid(pair, steps)
                else:
                    verify.replay(pair, steps, rec.get('states'))
                ok += 1
            except (verify.Failure, DV.Failure) as exc:
                print('FAIL', path, rec.get('name', rec.get('pres_id')), exc)
        grand_ok += ok
        grand_total += total
        print('%s: %d/%d replayed%s' % (Path(path).name, ok, total, (' (%d without certificate)' % skipped) if skipped else ''))
    print('TOTAL %d/%d' % (grand_ok, grand_total))
    return 0 if grand_ok == grand_total else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
