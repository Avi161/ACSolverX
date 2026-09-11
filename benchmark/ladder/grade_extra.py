"""Grade the rows the committed record leaves un-placeable, as small rung files.

Two gaps in the leftover-branch escalation record:

* ``ac19_orig_cascade/orig_of_cascade_open8.csv`` -- eight ORIGINALS of hard orbits
  that were only ever run through the cascade, so they have no greedy node count.
* ``ac19_autmin_screen/unescalated_10k_{baseline,s20_mk2}.csv`` -- 12 orbits greedy
  left unsolved at 10,000 nodes and 1 orbit s20_mk2 left unsolved, which the 100k
  rung never received.

This script runs the missing searches: plain length-ordered greedy (``config=None``,
pop-for-pop the baseline) or ``S20_MK2`` through the compact engine, 100,000 pops
first and 1,000,000 for any row still open, every solve replayed independently through
``words.replay_move``.  Cap 64 for the originals (their siblings' 10M run used 64) and
cap 48 for the orbits (the <= 1M rungs used 48).

Outputs under ``benchmark/ladder/sources/``, one record per row with the keys the
leftover-branch rungs use (``name, arm, r1, r2, budget, max_relator_length, solved,
nodes_explored, path_length, max_relator_length_expanded, path, path_moves, seconds``)
plus ``engine`` and ``git_head``:

    open8_greedy_mrl64.jsonl          unescalated_greedy_mrl48.jsonl
    unescalated_s20_mrl48.jsonl

``build_ladder.py`` reads them like any other rung.  Deterministic; a rerun rewrites
the same records (``seconds`` aside).  A 1,000,000-pop run reserves ~6 GB.

    PYTHONPATH=. python3 benchmark/ladder/grade_extra.py [--only open8|unescalated]
"""
import argparse
import csv
import io
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('NUMBA_NUM_THREADS', '1')

from experiments.equivalence_classes.lib.words import canon_pair, replay_move  # noqa: E402
from experiments.heuristic_search.core.hcompact import greedy_search_hcompact  # noqa: E402
from experiments.search.heuristics import S20_MK2  # noqa: E402

LEFTOVER = 'dab82a8412b007f23cffd35bee2727d977510de0'
SCREEN = 'results/heuristic_search/ac19_autmin_screen/'
JOBS = {
    # out file: (input csv on LEFTOVER, arm, config, cap)
    'open8_greedy_mrl64.jsonl': ('results/heuristic_search/ac19_orig_cascade/orig_of_cascade_open8.csv',
                                 'greedy', None, 64),
    'unescalated_greedy_mrl48.jsonl': (SCREEN + 'unescalated_10k_baseline.csv', 'greedy', None, 48),
    'unescalated_s20_mrl48.jsonl': (SCREEN + 'unescalated_10k_s20_mk2.csv', 's20_mk2', S20_MK2, 48),
}
OUT_DIR = ROOT / 'benchmark/ladder/sources'
BUDGETS = (100_000, 1_000_000)


def git_show(commit, path):
    return subprocess.run(['git', 'show', f'{commit}:{path}'], cwd=ROOT,
                          capture_output=True, check=True).stdout.decode()


def git_head():
    return subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                          capture_output=True, check=True, text=True).stdout.strip()


def replay(r1, r2, path, path_moves):
    """Independent replay: pure-Python words.replay_move, never the engine."""
    state = canon_pair(r1, r2)
    assert list(state) == list(path[0]), (state, path[0])
    for i, move in enumerate(path_moves):
        state = replay_move(state, tuple(int(v) for v in move.split('_')))
        assert list(state) == list(path[i + 1]), (i, state, path[i + 1])
    a, b = state
    assert len(a) == len(b) == 1 and a.lower() != b.lower(), state
    return True


def grade(row, arm, config, cap, head):
    r1, r2 = row['r1'], row['r2']
    for budget in BUDGETS:
        t0 = time.perf_counter()
        res = greedy_search_hcompact(r1, r2, budget, max_relator_length=cap,
                                     config=config, track_path=True)
        seconds = time.perf_counter() - t0
        if res['solved'] or budget == BUDGETS[-1]:
            break
    if res['solved']:
        replay(r1, r2, res['path'], res['path_moves'])
    rec = {
        'name': row['name'], 'arm': arm, 'r1': r1, 'r2': r2,
        'budget': budget, 'max_relator_length': cap,
        'solved': bool(res['solved']), 'nodes_explored': int(res['nodes_explored']),
        'path_length': int(res['path_length']) if res['solved'] else None,
        'max_relator_length_expanded': int(res['max_relator_length_expanded']),
        'path': res['path'] if res['solved'] else [],
        'path_moves': res['path_moves'] if res['solved'] else [],
        'seconds': round(seconds, 3), 'engine': 'hcompact', 'git_head': head,
    }
    if 'orbit' in row:
        rec['orbit'] = row['orbit']
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', choices=['open8', 'unescalated'], default=None)
    args = ap.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    head = git_head()
    for out_name, (path, arm, config, cap) in JOBS.items():
        if args.only and not out_name.startswith(args.only):
            continue
        rows = list(csv.DictReader(io.StringIO(git_show(LEFTOVER, path))))
        print(f'== {out_name}: {len(rows)} rows, arm {arm}, cap {cap}', flush=True)
        records = []
        for row in rows:
            rec = grade(row, arm, config, cap, head)
            records.append(rec)
            print(f"  {row['name']:14} solved={rec['solved']!s:5} nodes={rec['nodes_explored']:>9,} "
                  f"budget={rec['budget']:>9,} {rec['seconds']:7.1f}s", flush=True)
        with open(OUT_DIR / out_name, 'w') as fh:
            for rec in records:
                fh.write(json.dumps(rec) + '\n')
        print('  wrote', OUT_DIR / out_name, flush=True)


if __name__ == '__main__':
    main()
