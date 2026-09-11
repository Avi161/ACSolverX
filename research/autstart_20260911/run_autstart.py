"""Automorphic starts as reduction finders on the 36 reducible u124 classes.

Hypothesis: some automorphic image of a presentation is easier to *reduce* by plain AC
search than the presentation itself.  Test bed: the 36 unsolved Miller-Schupp classes
whose mu-reduced form (``acabest_N``) is shorter than the form first found (``aca_N``).

For each class: the initial form (k = 0) plus 50 automorphic images of it -- the first 50
relabel-distinct images under the compositions of the 12 length-changing Whitehead
automorphisms ordered by (depth, image length, lex), which reaches depth 4-5; applied
once, at the start.  From
each of the 51 starts: plain greedy (length order), 10,000 pops, relator cap 128 (never
binds), the queue pure AC moves, no Whitehead step in the search.  Recorded: the
smallest total length seen and the AC path to that state (parent chain from the
engine), replayed independently by ``words.replay_move``.

    PYTHONPATH=. python3 -m research.autstart_20260911.run_autstart build
    PYTHONPATH=. python3 -m research.autstart_20260911.run_autstart run [--workers 4]
    PYTHONPATH=. python3 -m research.autstart_20260911.run_autstart verify
    PYTHONPATH=. python3 -m research.autstart_20260911.run_autstart report
"""
import argparse
import csv
import hashlib
import json
import multiprocessing as mp
import os
import sys
import time
from collections import Counter, OrderedDict, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
for _v in ('OMP_NUM_THREADS', 'NUMBA_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

from experiments.equivalence_classes.lib.autcanon import DESCENT, ID, compose  # noqa: E402
from experiments.equivalence_classes.lib.words import (  # noqa: E402
    apply_pair, canon_pair, free_reduce, relabel_key, replay_move)

HERE = Path(__file__).resolve().parent
UNSOLVED = ROOT / 'benchmark' / 'ladder' / 'unsolved_all_forms.csv'
BUDGET = 10_000
CAP = 128
N_AUT = 50
START_FIELDS = ['cls', 'k', 'depth', 'phi_x', 'phi_y', 'r1', 'r2', 'start_len', 'initial_len', 'best_len']


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# --- targets -----------------------------------------------------------------------
def targets():
    """The 36 classes whose best known form is shorter than the form first found."""
    with open(UNSOLVED, newline='') as fh:
        rows = list(csv.DictReader(fh))
    init = {r['name']: r for r in rows if r['form'] == 'aca_initial'}
    best = {r['name'].replace('acabest_', 'aca_'): r for r in rows if r['form'] == 'aca_best'}
    out = []
    for name in sorted(init, key=lambda n: int(n.split('_')[1])):
        li, lb = int(init[name]['start_len']), int(best[name]['start_len'])
        if lb < li:
            out.append(dict(cls=name, r1=init[name]['r1'], r2=init[name]['r2'], initial_len=li, best_len=lb,
                            best_r1=best[name]['r1'], best_r2=best[name]['r2']))
    assert len(out) == 36, len(out)
    return out


# --- the automorphisms -------------------------------------------------------------
def automorphisms(max_depth=5):
    """Distinct compositions of the 12 length-changing Whitehead automorphisms, by
    (depth, image length, lex): 12 at depth 1, 88 more at depth 2, 510 at depth 3, ...
    Distinct as maps; as *images of a presentation* they collapse hard (the 12 moves are
    four outer classes plus conjugations, and conjugation does not change a cyclic
    word), so a class has only 12 relabel-distinct images within depth 2 and 28 within
    depth 3 -- the first 50 need depth 4-5."""
    seen, out, level = set(), [], [ID]
    for depth in range(1, max_depth + 1):
        nxt = []
        for g in level:
            for f in DESCENT:
                h = compose(f, g)
                h = {'x': free_reduce(h['x']), 'y': free_reduce(h['y'])}
                key = (h['x'], h['y'])
                if key == ('x', 'y') or key in seen:
                    continue
                seen.add(key)
                out.append((depth, len(h['x']) + len(h['y']), key, h))
                nxt.append(h)
        level = nxt
    out.sort(key=lambda t: (t[0], t[1], t[2]))
    return [(d, h) for d, _, _, h in out]


def build_starts():
    auts = automorphisms(5)
    rows = []
    for t in targets():
        pair = (t['r1'], t['r2'])
        assert canon_pair(*pair) == pair, t['cls']
        keys = {relabel_key(pair)}
        rows.append(dict(cls=t['cls'], k=0, depth=0, phi_x='x', phi_y='y', r1=pair[0], r2=pair[1],
                         start_len=t['initial_len'], initial_len=t['initial_len'], best_len=t['best_len']))
        k = 0
        for depth, phi in auts:
            img = apply_pair(pair, phi)
            rk = relabel_key(img)
            if rk in keys:
                continue
            keys.add(rk)
            k += 1
            rows.append(dict(cls=t['cls'], k=k, depth=depth, phi_x=phi['x'], phi_y=phi['y'], r1=img[0], r2=img[1],
                             start_len=len(img[0]) + len(img[1]), initial_len=t['initial_len'],
                             best_len=t['best_len']))
            if k == N_AUT:
                break
        assert k == N_AUT, (t['cls'], k)
    with open(HERE / 'starts.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=START_FIELDS, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)
    print(f'{len(rows)} starts ({len(rows) // 51} classes x 51) -> starts.csv; '
          f'{len(auts)} automorphisms enumerated, {N_AUT} kept per class')


# --- the search --------------------------------------------------------------------
def _search(row):
    from experiments.heuristic_search.core.hcompact import HCompactSolver
    r1, r2 = row['r1'], row['r2']
    t0 = time.perf_counter()
    solver = HCompactSolver(r1, r2, max_nodes=BUDGET, max_relator_length=CAP, cyclic_reduce=True,
                            config=None, track_path=True)
    solved, pops = solver.solve(None)
    wall = time.perf_counter() - t0
    # the AC path to the shortest state seen: walk the parent chain from min_id, as path()
    # does from solved_id
    sid, moves = int(solver.min_id), []
    for _ in range(int(solver.states_cap) + 1):
        p = int(solver.parent[sid])
        if p < 0:
            break
        moves.append('_'.join(str(int(v)) for v in solver.pmove[sid]))
        sid = p
    else:
        raise RuntimeError('parent chain did not reach the root')
    moves.reverse()
    min_pair = solver.relators(int(solver.min_id))
    rec = OrderedDict(cls=row['cls'], k=int(row['k']), depth=int(row['depth']), phi_x=row['phi_x'], phi_y=row['phi_y'],
                      r1=r1, r2=r2, start_len=int(row['start_len']), initial_len=int(row['initial_len']),
                      best_len=int(row['best_len']), budget=BUDGET, cap=CAP, engine='greedy',
                      solved=bool(solved), pops=int(pops), min_len=int(solver.min_total),
                      min_pair=[min_pair[0], min_pair[1]], min_depth=len(moves), path_moves_to_min=moves,
                      max_len_expanded=int(solver.max_expanded_total), wall=round(wall, 3))
    if solved:
        states, smoves = solver.path()
        rec['solved_path_moves'] = ['_'.join(str(int(v)) for v in m) for m in smoves]
    return rec


def _work(row):
    try:
        return _search(row)
    except Exception as exc:  # noqa: BLE001
        return OrderedDict(cls=row['cls'], k=int(row['k']), error=f'{type(exc).__name__}: {exc}')


def run(workers):
    with open(HERE / 'starts.csv', newline='') as fh:
        starts = list(csv.DictReader(fh))
    out = HERE / 'results.jsonl'
    done = set()
    if out.exists():
        for line in open(out):
            if line.strip():
                r = json.loads(line)
                if 'error' not in r:
                    done.add((r['cls'], r['k']))
    todo = [s for s in starts if (s['cls'], int(s['k'])) not in done]
    print(f'{len(starts)} starts, {len(done)} done, {len(todo)} to run, {workers} workers')
    t0 = time.time()
    n = 0
    with open(out, 'a') as fh:
        ctx = mp.get_context('spawn')
        with ctx.Pool(workers) as pool:
            for rec in pool.imap_unordered(_work, todo, chunksize=4):
                fh.write(json.dumps(rec) + '\n')
                fh.flush()
                n += 1
                if n % 100 == 0 or n == len(todo):
                    print(f'  [{n}/{len(todo)}] {time.time() - t0:.0f}s', flush=True)
    print(f'done in {time.time() - t0:.0f}s -> {out}')


# --- verification --------------------------------------------------------------------
def load_results():
    recs = {}
    for line in open(HERE / 'results.jsonl'):
        if line.strip():
            r = json.loads(line)
            if 'error' not in r:
                recs[(r['cls'], r['k'])] = r     # last complete record wins
    return recs


def verify():
    recs = load_results()
    init = {t['cls']: t for t in targets()}
    checked = ok = 0
    failures = []
    for (cls, k), r in sorted(recs.items()):
        checked += 1
        problems = []
        phi = {'x': r['phi_x'], 'y': r['phi_y']}
        start = apply_pair((init[cls]['r1'], init[cls]['r2']), phi)
        if list(start) != [r['r1'], r['r2']]:
            problems.append('start is not the automorphic image of the initial form')
        state = canon_pair(r['r1'], r['r2'])
        for m in r['path_moves_to_min']:
            state = replay_move(state, tuple(int(v) for v in m.split('_')))
        if list(state) != r['min_pair']:
            problems.append('replay does not reach min_pair')
        if len(state[0]) + len(state[1]) != r['min_len']:
            problems.append('min_len disagrees with the replayed state')
        if r['min_len'] > r['start_len']:
            problems.append('min_len above the start length')
        if r['solved']:
            s = canon_pair(r['r1'], r['r2'])
            for m in r.get('solved_path_moves', []):
                s = replay_move(s, tuple(int(v) for v in m.split('_')))
            if not (len(s[0]) == len(s[1]) == 1 and s[0].lower() != s[1].lower()):
                problems.append('claimed solve does not replay to (x, y)')
        if problems:
            failures.append(dict(cls=cls, k=k, problems=problems))
        else:
            ok += 1
    out = OrderedDict(records=checked, ok=ok, failures=failures,
                      starts_sha256=sha256(HERE / 'starts.csv'), results_sha256=sha256(HERE / 'results.jsonl'))
    (HERE / 'verify.json').write_text(json.dumps(out, indent=1) + '\n')
    print(f'verify: {checked} records, {ok} ok, {len(failures)} failures')
    return not failures


# --- report --------------------------------------------------------------------------
def report():
    recs = load_results()
    by_cls = defaultdict(dict)
    for (cls, k), r in recs.items():
        by_cls[cls][k] = r
    tg = {t['cls']: t for t in targets()}
    lines = ['# Automorphic starts as reduction finders: the 36 reducible u124 classes', '']
    lines.append(f'Plain greedy, {BUDGET:,} pops, cap {CAP}, from the initial form (k = 0) and {N_AUT} '
                 'relabel-distinct automorphic images of it (compositions of the 12 length-changing Whitehead '
                 'automorphisms, depth 1 then 2, applied once at the start). `min` = smallest total length of '
                 'any state the search discovered; every `min` state is replayed from its start '
                 '(`verify.json`).', '')
    lines.append('| class | initial | best known | identity start min | best aut start min | k | depth | phi | '
                 'start len | at depth | < initial | <= best | < best |')
    lines.append('|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|---|---|')
    n_id_below = n_aut_below = n_any_below = n_match = n_beat = n_aut_better_than_id = 0
    wins = Counter()
    for cls in sorted(by_cls, key=lambda c: int(c.split('_')[1])):
        rs = by_cls[cls]
        li, lb = tg[cls]['initial_len'], tg[cls]['best_len']
        ident = rs.get(0)
        auts = [r for k, r in rs.items() if k > 0]
        best_aut = min(auts, key=lambda r: (r['min_len'], r['k'])) if auts else None
        id_min = ident['min_len'] if ident else None
        a_min = best_aut['min_len'] if best_aut else None
        any_min = min(v for v in (id_min, a_min) if v is not None)
        if id_min is not None and id_min < li:
            n_id_below += 1
        if a_min is not None and a_min < li:
            n_aut_below += 1
        if any_min < li:
            n_any_below += 1
        if any_min <= lb:
            n_match += 1
        if any_min < lb:
            n_beat += 1
        if a_min is not None and id_min is not None and a_min < id_min:
            n_aut_better_than_id += 1
            wins[(best_aut['phi_x'], best_aut['phi_y'])] += 1
        flag = lambda b: 'yes' if b else '-'
        lines.append(f"| {cls} | {li} | {lb} | {id_min} | {a_min} | {best_aut['k']} | {best_aut['depth']} | "
                     f"x->{best_aut['phi_x']}, y->{best_aut['phi_y']} | {best_aut['start_len']} | {best_aut['min_depth']} | "
                     f"{flag(any_min < li)} | {flag(any_min <= lb)} | {flag(any_min < lb)} |")
    n = len(by_cls)
    lines += ['', '## Totals', '',
              f'- classes: {n}; records: {len(recs)} (of {n * (N_AUT + 1)}); solves: '
              f'{sum(1 for r in recs.values() if r["solved"])}',
              f'- identity start reaches a state shorter than the initial form: **{n_id_below} / {n}**',
              f'- some automorphic start reaches a state shorter than the initial form: **{n_aut_below} / {n}**',
              f'- either: **{n_any_below} / {n}**; matching the known best length: **{n_match} / {n}**; '
              f'beating it: **{n_beat} / {n}**',
              f'- automorphic start strictly better than the identity start (smaller min): '
              f'**{n_aut_better_than_id} / {n}**']
    if wins:
        lines += ['', 'Automorphisms of the best start where it beat the identity start:', '']
        for (px, py), c in wins.most_common():
            lines.append(f'- x->{px}, y->{py}: {c}')
    # how the min depends on the start length
    lines += ['', '## Min length over all 51 starts per class (distribution)', '']
    for cls in sorted(by_cls, key=lambda c: int(c.split('_')[1])):
        rs = by_cls[cls]
        li = tg[cls]['initial_len']
        c = Counter(r['min_len'] for r in rs.values())
        lines.append(f"- {cls} (initial {li}, best {tg[cls]['best_len']}): " +
                     ', '.join(f'{m}:{c[m]}' for m in sorted(c)))
    (HERE / 'SUMMARY.md').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines[-(n + 12):]))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('cmd', choices=['build', 'run', 'verify', 'report'])
    ap.add_argument('--workers', type=int, default=4)
    a = ap.parse_args()
    if a.cmd == 'build':
        build_starts()
    elif a.cmd == 'run':
        run(a.workers)
    elif a.cmd == 'verify':
        sys.exit(0 if verify() else 1)
    else:
        report()


if __name__ == '__main__':
    main()
