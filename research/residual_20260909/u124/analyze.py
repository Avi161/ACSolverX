"""Assemble the 10,000-unit probe on the 124 unsolved ACA classes.

Reads the harness screens (frozen policy, K3p_c14aut), the certified reduction
search (both arms) and the mu-ladder record, and prints per-row and summary
tables.  A reduction counts only when its path replayed."""
import csv
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def load_jsonl(path):
    return [json.loads(line) for line in open(path)] if Path(path).exists() else []


def main():
    reduced = {r['name']: r for r in csv.DictReader(open(ROOT / 'data/ms_unsolved_reps/aca_124_reduced.csv'))}
    best = {r['name']: r for r in csv.DictReader(open(ROOT / 'data/ms_unsolved_reps/aca_124_best.csv'))}
    frozen = {r['name']: r for r in load_jsonl(HERE / 'aca124_frozen_10000.jsonl')}
    cascade = {r['name']: r for r in load_jsonl(HERE / 'aca124_K3p_c14aut_10000.jsonl')}
    probe = load_jsonl(HERE / 'aca124_reduce_10000.jsonl')
    s20 = {r['name']: r for r in probe if r['arm'] == 's20'}
    aut = {r['name']: r for r in probe if r['arm'] == 'aut_edges'}
    print(f'rows: best {len(best)} frozen {len(frozen)} cascade {len(cascade)} s20 {len(s20)} aut {len(aut)}')
    rows = []
    for name, row in best.items():
        total = len(row['r1']) + len(row['r2'])
        f, c, s, a = frozen.get(name), cascade.get(name), s20.get(name), aut.get(name)
        rows.append(dict(name=name, total=total, mx=max(len(row['r1']), len(row['r2'])),
                         mu_ladder=reduced[name]['reduce_kind'],
                         frozen_solved=f and f['solved'], frozen_best=f and f.get('min_total_length_seen'),
                         cascade_solved=c and c['solved'], cascade_best=c and c.get('min_total_length_seen'),
                         cascade_route=c and c.get('policy_route'),
                         s20_best=s and s['best_total'], s20_ok=s and s['path_replayed'], s20_solved=s and s['solved'],
                         aut_best=a and a['best_total'], aut_ok=a and a['path_replayed'], aut_solved=a and a['solved'],
                         aut_max=a and a['best_max'], s20_max=s and s['best_max']))
    def count(key, pred):
        return sum(1 for r in rows if r[key] is not None and pred(r))
    print('solved: frozen', count('frozen_solved', lambda r: r['frozen_solved']),
          'cascade', count('cascade_solved', lambda r: r['cascade_solved']),
          's20+table', count('s20_solved', lambda r: r['s20_solved']),
          'aut_edges+table', count('aut_solved', lambda r: r['aut_solved']))
    print('rows whose search reached a strictly shorter total length than the best-known pair:')
    for key, ok in (('frozen_best', None), ('cascade_best', None), ('s20_best', 's20_ok'), ('aut_best', 'aut_ok')):
        n = count(key, lambda r: r[key] < r['total'] and (ok is None or r[ok]))
        gain = sum(r['total'] - r[key] for r in rows if r[key] is not None and r[key] < r['total'] and (ok is None or r[ok]))
        print(f'  {key:13s} {n:3d} rows, total letters saved {gain}')
    print('rows whose search reached a smaller MAX relator length (certified arms):')
    for key, ok in (('s20_max', 's20_ok'), ('aut_max', 'aut_ok')):
        print(f'  {key:9s}', count(key, lambda r: r[key] < r['mx'] and r[ok]))
    print()
    print('per-row (total -> best total seen: frozen | cascade | s20 certified | aut certified)')
    for r in sorted(rows, key=lambda r: (r['total'], r['name'])):
        marks = []
        for key, ok in (('frozen_best', None), ('cascade_best', None), ('s20_best', 's20_ok'), ('aut_best', 'aut_ok')):
            v = r[key]
            marks.append('  -' if v is None else f'{v:3d}' + ('*' if v < r['total'] and (ok is None or r[ok]) else ' '))
        print(f"{r['name']:8s} {r['total']:3d} (max {r['mx']:2d}) {r['mu_ladder']:8s} " + ' | '.join(marks))
    routes = Counter(r['cascade_route'] for r in rows if r['cascade_route'])
    print('cascade routes', dict(routes))


if __name__ == '__main__':
    main()
