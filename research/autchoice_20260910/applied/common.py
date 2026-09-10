"""Shared pieces of the applied campaign: paths, the targets, one verified search, one record.

The applied campaign asks whether B1's radius-2 trick (search from an Aut(F2)-image of the
row rather than the row itself) solves anything the record has never solved.  Everything
here is deterministic and uses B1's library read-only: ``orbit.ball`` for the images,
``engine.replay`` / ``engine.is_trivial`` / ``engine.verify_from_original`` for the
independent replays, ``features.features`` for the per-image features.

``search(pair, budget, cap)`` runs ``greedy_search_hcompact`` under ``S20_MK2`` with
``track_path=True`` and keeps three fields ``engine.cost`` drops: ``min_total_length_seen``
(the engine's ``min_relator_length``, the smallest total relator length of any state it
discovered), ``min_relator`` (that state) and the wall time.  A claimed solve is replayed
through ``words.replay_move`` from the image (pure Python, never the engine's replay); a
claim the replay rejects is recorded with ``rejected`` set and counted as unsolved.

``make_record(...)`` builds one JSON line in the shape of ``atlas.jsonl`` (``row, level,
form, source, orbit, pair_id, image_index, depth, seq, phi, r1, r2, rkey, is_identity,
features, budget, cap, s20, greedy``) plus ``orig_r1, orig_r2, start_len, phase, radius`` so a
verifier can work from the JSONL alone; ``s20.verified`` is the conjunction of the image
replay and ``engine.verify_from_original`` from the target's own pair through the elementary
automorphism sequence.

Set ``OMP_NUM_THREADS=1 NUMBA_NUM_THREADS=1`` (done here on import).
"""
import csv
import hashlib
import json
import os
import sys
import time
from collections import OrderedDict
from pathlib import Path

os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('NUMBA_NUM_THREADS', '1')
ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

HERE = Path(__file__).resolve().parent            # research/autchoice_20260910/applied
CAMPAIGN = HERE.parent                            # research/autchoice_20260910
LADDER_ALL = ROOT / 'benchmark' / 'ladder' / 'ladder_all.csv'
ATLAS = CAMPAIGN / 'atlas.jsonl'
TARGETS_CSV = HERE / 'targets.csv'
PHASE1 = HERE / 'phase1.jsonl'
PHASE2 = HERE / 'phase2.jsonl'
TARGET_COLS = ('name', 'r1', 'r2', 'source', 'form', 'note')
CAP = 48
FORM_ORDER = ('aca_initial', 'ac19_level9_leftover', 'aca_best')


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def git_head():
    import subprocess
    try:
        return subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception:  # noqa: BLE001
        return None


def load_targets(path=TARGETS_CSV):
    rows = list(csv.DictReader(open(path)))
    assert rows and tuple(rows[0].keys()) == TARGET_COLS, f'unexpected columns in {path}'
    return rows


def read_jsonl(path):
    path = Path(path)
    if not path.exists():
        return
    with open(path) as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def done_keys(path):
    """``{(row, image_index, budget)}`` already on disk -- the resume key."""
    return {(d['row'], d['image_index'], d['budget']) for d in read_jsonl(path)}


def search(pair, budget, cap=CAP):
    """One S20_MK2 search from ``pair``; a claimed solve is replayed independently."""
    from experiments.heuristic_search.core.hcompact import greedy_search_hcompact
    from research.autchoice_20260910.engine import S20_MK2, is_trivial, replay
    r1, r2 = pair
    t0 = time.perf_counter()
    res = greedy_search_hcompact(r1, r2, budget, max_relator_length=cap, config=S20_MK2,
                                 track_path=True)
    wall = time.perf_counter() - t0
    solved = bool(res['solved'])
    moves = [str(m) for m in res['path_moves']] if solved else []
    rejected = None
    if solved:
        end = replay(pair, moves)
        if not is_trivial(end):
            rejected = f'{pair}: engine claimed a solve, replay ends on {end}'
            solved = False
    out = OrderedDict(solved=solved, nodes=int(res['nodes_explored']),
                      max_expanded=int(res['max_relator_length_expanded']),
                      min_total_length_seen=int(res['min_relator_length']),
                      min_relator=[str(res['min_relator'][0]), str(res['min_relator'][1])],
                      path_len=len(moves) if solved else None, wall=round(wall, 3),
                      path_moves=moves if solved else None)
    if rejected:
        out['rejected'] = rejected
    return out


def make_record(target, idx, node, result, budget, cap, phase, radius, shared=False, extra=None):
    """One JSON-ready record for (target, image); ``result`` is ``search(...)``'s dict."""
    from research.autchoice_20260910.engine import verify_from_original
    from research.autchoice_20260910.features import features
    orig = (target['r1'], target['r2'])
    rec = OrderedDict(row=target['name'], level='10' if target['form'].startswith('aca') else '9',
                      form=target['form'], source=target['source'], orbit='', pair_id='',
                      image_index=idx, depth=node['depth'], seq=list(node['seq']), phi=node['phi'],
                      r1=node['r1'], r2=node['r2'], rkey=list(node['rkey']), is_identity=(idx == 0),
                      orig_r1=orig[0], orig_r2=orig[1], start_len=len(orig[0]) + len(orig[1]),
                      features=features(node['r1'], node['r2']), budget=budget, cap=cap,
                      phase=phase, radius=radius)
    if extra:
        rec.update(extra)
    s20 = OrderedDict(result)
    ok = bool(s20['solved']) and not s20.get('rejected') and \
        verify_from_original(orig, node['seq'], s20['path_moves'])
    s20['verified'] = ok
    s20['shared'] = bool(shared)      # True when this pair was searched once for several rows
    rec['s20'] = s20
    rec['greedy'] = None
    return rec


def group_by_pair(items):
    """``items`` = (target, idx, node); returns ``{(r1, r2): [items...]}`` in first-seen order."""
    groups = OrderedDict()
    for it in items:
        groups.setdefault((it[2]['r1'], it[2]['r2']), []).append(it)
    return groups


def write_json(path, obj):
    with open(path, 'w') as f:
        json.dump(obj, f, indent=1)
        f.write('\n')
