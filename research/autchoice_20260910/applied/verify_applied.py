"""Independent re-check of every claimed solve in ``applied/*.jsonl``, in a fresh process.

    PYTHONPATH=. python3 -m research.autchoice_20260910.applied.verify_applied

Reads only the JSONL records (``phase1.jsonl``, ``phase2.jsonl``) -- each carries the
target's own pair ``orig_r1, orig_r2``, the automorphism sequence ``seq`` (``autcanon.AUTOS``
indices, applied in order) and the certificate ``s20.path_moves`` -- and for every record
with ``s20.solved`` true:

  1. ``canon_pair(orig)``, then ``words.apply_pair`` with ``AUTOS[i]`` one step at a time,
     must land on the recorded image ``(r1, r2)``;
  2. ``words.replay_move`` over ``path_moves`` from that image (the replay stops as soon as a
     relator passes 512 letters -- a wrong replay grows exponentially) must end on two
     distinct single letters;
  3. the record's ``orig_r1, orig_r2`` must equal the row's pair in ``targets.csv``.

Nothing from ``engine.py`` or ``hcompact`` is imported.  Writes ``verify_applied.json``
(``checked / ok / failed`` overall and per file, the failures listed) and exits non-zero if
anything failed.
"""
import csv
import json
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.equivalence_classes.lib.autcanon import AUTOS  # noqa: E402
from experiments.equivalence_classes.lib.words import apply_pair, canon_pair, replay_move  # noqa: E402

HERE = Path(__file__).resolve().parent
FILES = ('phase1.jsonl', 'phase2.jsonl')
MAX_LEN = 512


def is_trivial(state):
    a, b = state
    return len(a) == 1 and len(b) == 1 and a.lower() != b.lower()


def check(rec, targets):
    orig = (rec['orig_r1'], rec['orig_r2'])
    t = targets.get(rec['row'])
    if t is None or (t['r1'], t['r2']) != orig:
        return 'orig pair does not match targets.csv'
    state = canon_pair(*orig)
    for i in rec['seq']:
        state = apply_pair(state, AUTOS[i])
    if state != (rec['r1'], rec['r2']):
        return f'automorphism sequence lands on {state}, record says {(rec["r1"], rec["r2"])}'
    moves = rec['s20']['path_moves'] or []
    for m in moves:
        state = replay_move(state, tuple(int(v) for v in m.split('_')))
        if max(len(state[0]), len(state[1])) > MAX_LEN:
            break
    if not is_trivial(state):
        return f'replay ends on {state}'
    return None


def main():
    targets = {r['name']: r for r in csv.DictReader(open(HERE / 'targets.csv'))}
    out = OrderedDict(checked=0, ok=0, failed=0, records=0, per_file=OrderedDict(), failures=[])
    for name in FILES:
        path = HERE / name
        pf = OrderedDict(records=0, checked=0, ok=0, failed=0)
        if path.exists():
            for line in open(path):
                if not line.strip():
                    continue
                rec = json.loads(line)
                pf['records'] += 1
                if not rec['s20']['solved']:
                    continue
                pf['checked'] += 1
                err = check(rec, targets)
                if err is None:
                    pf['ok'] += 1
                else:
                    pf['failed'] += 1
                    out['failures'].append(OrderedDict(file=name, row=rec['row'], image_index=rec['image_index'],
                                                       budget=rec['budget'], error=err))
        out['per_file'][name] = pf
        for k in ('records', 'checked', 'ok', 'failed'):
            out[k] += pf[k]
    with open(HERE / 'verify_applied.json', 'w') as f:
        json.dump(out, f, indent=1)
        f.write('\n')
    print(f"verify_applied: {out['records']} records, {out['checked']} claimed solves checked, "
          f"{out['ok']} ok, {out['failed']} failed")
    sys.exit(1 if out['failed'] else 0)


if __name__ == '__main__':
    main()
