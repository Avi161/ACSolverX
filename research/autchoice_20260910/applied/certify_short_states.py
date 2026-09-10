"""Certify every state the campaign found that is shorter than a class's best-known form.

    OMP_NUM_THREADS=1 NUMBA_NUM_THREADS=1 PYTHONPATH=. \\
        python3 -m research.autchoice_20260910.applied.certify_short_states

``phase1.jsonl`` / ``phase2.jsonl`` record, per (row, image), the engine's
``min_total_length_seen`` and the state ``min_relator`` that attained it, but not the AC path
to it.  For every ``aca_*`` record whose minimum is strictly below the class's best-known
length (the ``acabest_N`` start length; ``data/ms_unsolved_reps/README_aca_124.md`` defines
"best" as strictly shorter total length), this script re-runs the identical search
(``HCompactSolver`` under ``S20_MK2``, same budget and cap, ``track_path=True``; the engine is
deterministic), walks the solver's ``parent`` / ``pmove`` arrays from ``min_id`` back to the
root -- the same walk ``HCompactSolver.path`` does from the solved node -- and replays the
moves with ``words.replay_move`` from the image, demanding that the replay lands exactly on
the recorded ``min_relator`` with the recorded length.  The automorphism sequence from the
row's own pair to the image is replayed with ``words.apply_pair`` first (``seq`` empty for the
identity: then the certified path is a pure AC path from the row itself).

Identical (image pair, budget) is certified once.  Output ``short_states.json``: one entry per
certified state with the class, the row, the image, ``seq``, the AC moves, the length profile
of the path (its hump), and the state; ``failed`` lists anything that did not replay.
"""
import json
import sys
from collections import OrderedDict

from research.autchoice_20260910.applied.common import (
    CAP, HERE, PHASE1, PHASE2, load_targets, read_jsonl, write_json,
)

sys.path.insert(0, str(HERE.parents[2]))
from experiments.equivalence_classes.lib.autcanon import AUTOS  # noqa: E402
from experiments.equivalence_classes.lib.words import apply_pair, canon_pair, replay_move  # noqa: E402


def path_to_min(pair, budget, cap):
    """Re-run the search; return (min_state, moves root->min_id) from the parent chain."""
    from experiments.heuristic_search.core.hcompact import HCompactSolver
    from experiments.search.heuristics import S20_MK2
    solver = HCompactSolver(pair[0], pair[1], max_nodes=budget, max_relator_length=cap,
                            cyclic_reduce=True, config=S20_MK2, track_path=True)
    solver.solve(None)
    sid, moves = int(solver.min_id), []
    for _ in range(int(solver.states_cap) + 1):
        p = int(solver.parent[sid])
        if p < 0:
            moves.reverse()
            return tuple(solver.relators(int(solver.min_id))), moves, int(solver.min_total)
        moves.append(tuple(int(v) for v in solver.pmove[sid]))
        sid = p
    raise RuntimeError('parent chain did not reach the root')


def main():
    targets = {t['name']: t for t in load_targets()}
    best_len = {t['name'][8:]: len(t['r1']) + len(t['r2']) for t in targets.values() if t['form'] == 'aca_best'}
    wanted = OrderedDict()
    for path in (PHASE1, PHASE2):
        for d in read_jsonl(path):
            if not d['form'].startswith('aca'):
                continue
            cls = d['row'].rsplit('_', 1)[1]
            m = d['s20']['min_total_length_seen']
            if cls in best_len and m < best_len[cls]:
                wanted.setdefault((d['r1'], d['r2'], d['budget'], d['cap']), []).append(d)
    out = OrderedDict(certified=[], failed=[])
    for (r1, r2, budget, cap), recs in wanted.items():
        state, moves, mtot = path_to_min((r1, r2), budget, cap)
        cur = canon_pair(r1, r2)
        profile = [len(cur[0]) + len(cur[1])]
        for mv in moves:
            cur = replay_move(cur, mv)
            profile.append(len(cur[0]) + len(cur[1]))
        d = recs[0]
        rec_state = tuple(d['s20']['min_relator'])
        ok = (cur == state == rec_state and len(cur[0]) + len(cur[1]) == d['s20']['min_total_length_seen'] == mtot)
        # the automorphism side: the image must be reachable from each carrying row's own pair
        rows = []
        for r in recs:
            st = canon_pair(r['orig_r1'], r['orig_r2'])
            for i in r['seq']:
                st = apply_pair(st, AUTOS[i])
            rows.append(OrderedDict(row=r['row'], image_index=r['image_index'], depth=r['depth'], seq=r['seq'],
                                    phi=r['phi'], aut_ok=(st == (r1, r2))))
        cls = d['row'].rsplit('_', 1)[1]
        entry = OrderedDict(cls=f'aca_{cls}', best_known_len=best_len[cls], best_known_pair=[targets[f'acabest_{cls}']['r1'], targets[f'acabest_{cls}']['r2']],
                            image=[r1, r2], image_len=len(r1) + len(r2), budget=budget, cap=cap,
                            state=list(cur), state_len=len(cur[0]) + len(cur[1]), n_moves=len(moves),
                            peak_len=max(profile), moves=['_'.join(str(v) for v in mv) for mv in moves],
                            length_profile=profile, carried_by=rows, replay_ok=ok)
        (out['certified'] if ok and all(r['aut_ok'] for r in rows) else out['failed']).append(entry)
        print(f"{entry['cls']}: best-known {entry['best_known_len']} -> state {entry['state']} length {entry['state_len']} "
              f"via {len(moves)} AC moves from image {r1} {r2} (peak {max(profile)}) "
              f"{'CERTIFIED' if ok else 'FAILED'}; rows {[r['row'] for r in rows]}", flush=True)
    write_json(HERE / 'short_states.json', out)
    print(f"short_states.json: {len(out['certified'])} certified, {len(out['failed'])} failed")


if __name__ == '__main__':
    main()
